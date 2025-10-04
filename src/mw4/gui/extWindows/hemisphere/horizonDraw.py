############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from pathlib import Path

import cv2
import numpy as np
import pyqtgraph as pg

# external packages
from PySide6.QtCore import QPointF

# local import
from mw4.gui.utilities.toolsQtWidget import MWidget


class HorizonDraw(MWidget):
    """ """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = parent.ui
        self.app = parent.app
        self.msg = parent.msg
        self.horizonPlot = None
        self.imageTerrain = None
        self.pointerHor = None

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("hemisphereW", {})
        fileName = Path(config.get("horizonMaskFileName", ""))
        self.ui.horizonMaskFileName.setText(fileName.stem)
        self.app.data.loadHorizonP(fileName=fileName.stem)
        fileName = config.get("terrainFileName", "")
        self.ui.terrainFileName.setText(fileName)
        terrainFile = self.app.mwGlob["configDir"] / self.ui.terrainFileName.text()
        self.loadTerrainImage(terrainFile)

        self.ui.saveHorizonMask.clicked.connect(self.saveHorizonMask)
        self.ui.saveHorizonMaskAs.clicked.connect(self.saveHorizonMaskAs)
        self.ui.loadHorizonMask.clicked.connect(self.loadHorizonMask)
        self.ui.loadTerrainFile.clicked.connect(self.selectTerrainFile)
        self.ui.clearTerrainFile.clicked.connect(self.clearTerrainFile)
        self.ui.clearHorizonMask.clicked.connect(self.clearHorizonMask)
        self.ui.addPositionToHorizon.clicked.connect(self.addActualPosition)
        self.ui.showTerrain.clicked.connect(self.drawTab)
        self.ui.azimuthShift.valueChanged.connect(self.drawTab)
        self.ui.altitudeShift.valueChanged.connect(self.drawTab)
        self.ui.terrainAlpha.valueChanged.connect(self.drawTab)
        self.ui.normalModeHor.clicked.connect(self.setOperationMode)
        self.ui.editModeHor.clicked.connect(self.setOperationMode)
        self.app.mount.signals.pointDone.connect(self.drawPointer)
        self.ui.horizon.p[0].scene().sigMouseMoved.connect(self.mouseMovedHorizon)

    def mouseMovedHorizon(self, pos: QPointF) -> None:
        """ """
        self.parent.mouseMoved(pos)

    def drawTerrainImage(self, plotItem: pg.PlotItem) -> None:
        """ """
        if self.imageTerrain is None:
            return

        shiftAz = (self.ui.azimuthShift.value() + 360) % 360
        shiftAlt = self.ui.altitudeShift.value()
        alpha = self.ui.terrainAlpha.value()
        x1 = int(4 * shiftAz)
        x2 = int(1440 + 4 * shiftAz)
        y1 = int(60 + shiftAlt * 2)
        y2 = int(420 + shiftAlt * 2)
        img = self.imageTerrain[y1:y2, x1:x2]
        img = cv2.resize(img, (360, 90))
        imgItem = pg.ImageItem(img)
        cMap = pg.colormap.get("CET-L2")
        imgItem.setColorMap(cMap)
        imgItem.setOpts(opacity=alpha)
        imgItem.setZValue(-10)
        plotItem.addItem(imgItem)

    def loadTerrainImage(self, terrainFile: Path) -> None:
        """ """
        if not terrainFile.is_file():
            self.imageTerrain = None
            return

        img = cv2.imread(terrainFile, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        h2 = int(h / 2)
        img = img[0:h2, 0:w]
        img = cv2.resize(img, (1440, 360))
        img = cv2.flip(img, 0)
        self.imageTerrain = np.ones((480, 2880)) * 128
        self.imageTerrain[60:420, 0:1440] = img
        self.imageTerrain[60:420, 1440:2880] = img

    def selectTerrainFile(self) -> None:
        """ """
        folder = self.app.mwGlob["configDir"]
        fileTypes = "Terrain images (*.jpg)"
        loadFilePath = self.openFile(self.parent, "Open terrain image", folder, fileTypes)
        if not loadFilePath.is_file():
            return

        self.ui.terrainFileName.setText(loadFilePath.name)
        self.ui.showTerrain.setChecked(True)
        self.loadTerrainImage(loadFilePath)
        self.msg.emit(0, "Hemisphere", "Terrain", f"Mask [{loadFilePath.name}] loaded")
        self.parent.redrawAll()

    def clearTerrainFile(self) -> None:
        """ """
        self.ui.terrainFileName.setText("")
        self.ui.showTerrain.setChecked(False)
        self.parent.redrawAll()

    def loadHorizonMask(self) -> None:
        """ """
        folder = self.app.mwGlob["configDir"]
        fileTypes = "Horizon mask files (*.hpts);; CSV Files (*.csv);; MW3 Files (*.txt)"
        loadFilePath = self.openFile(self.parent, "Open horizon mask file", folder, fileTypes)
        if not loadFilePath.is_file():
            return

        self.app.data.loadHorizonP(fileName=loadFilePath.stem, ext=loadFilePath.suffix)
        self.ui.horizonMaskFileName.setText(loadFilePath.stem)
        self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{loadFilePath.stem}] loaded")
        self.parent.redrawAll()

    def saveHorizonMask(self) -> None:
        """ """
        fileName = self.ui.horizonMaskFileName.text()
        if not fileName:
            self.msg.emit(2, "Hemisphere", "Horizon", "Mask file name not given")
            return

        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{fileName}] saved")
        else:
            self.msg.emit(2, "Hemisphere", "Horizon", f"Mask [{fileName}] cannot no be saved")

    def saveHorizonMaskAs(self) -> None:
        """ """
        folder = self.app.mwGlob["configDir"]
        saveFilePath, fileName, ext = self.saveFile(
            self, "Save horizon mask file", folder, "Horizon mask files (*.hpts)"
        )
        if not saveFilePath:
            return

        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.ui.horizonMaskFileName.setText(fileName)
            self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{fileName}] saved")
        else:
            self.msg.emit(2, "Hemisphere", "Horizon", f"Mask [{fileName}] cannot no be saved")

    def setOperationMode(self) -> None:
        """ """
        self.ui.addPositionToHorizon.setEnabled(self.ui.editModeHor.isChecked())
        self.drawTab()

    def updateDataHorizon(self, x: list, y: list) -> None:
        """ """
        hp = [(y, x) for y, x in zip(y, x)]
        hp.sort(key=lambda x: x[1])
        x = [x[1] for x in hp]
        y = [x[0] for x in hp]
        self.horizonPlot.setData(x=x, y=y)
        self.app.data.horizonP = hp
        self.drawTab()

    def clearHorizonMask(self) -> None:
        """ """
        self.app.data.horizonP = []
        self.ui.horizonMaskFileName.setText("")
        self.parent.redrawAll()

    def addActualPosition(self) -> None:
        """ """
        vb = self.ui.horizon.p[0].getViewBox()
        az = self.app.mount.obsSite.Az
        alt = self.app.mount.obsSite.Alt
        if alt is None and az is None:
            return
        az = az.degrees
        alt = alt.degrees
        index = vb.getNearestPointIndex(QPointF(az, alt))
        if index is not None:
            vb.addUpdate(index, QPointF(az, alt))

    def prepareView(self) -> None:
        """ """
        plotItem = self.ui.horizon.p[0]
        self.parent.preparePlotItem(plotItem)
        self.pointerHor = None

    def drawView(self) -> None:
        """ """
        hp = self.app.data.horizonP
        if len(hp) == 0:
            return
        alt, az = zip(*hp)
        alt = np.array(alt)
        az = np.array(az)
        self.horizonPlot.setData(x=az, y=alt)

    def setupPointer(self) -> None:
        """ """
        plotItem = self.ui.horizon.p[0]
        symbol = self.makePointer()
        self.pointerHor = pg.ScatterPlotItem(symbol=symbol, size=40)
        self.pointerHor.setData(x=[0], y=[45])
        self.pointerHor.setPen(pg.mkPen(color=self.M_PINK))
        self.pointerHor.setBrush(pg.mkBrush(color=self.M_PINK + "20"))
        self.pointerHor.setZValue(10)
        plotItem.addItem(self.pointerHor)

    def drawPointer(self) -> None:
        """ """
        if self.pointerHor is None:
            return

        obsSite = self.app.mount.obsSite
        if obsSite.Alt is None or obsSite.Az is None:
            self.pointerHor.setVisible(False)
            return

        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerHor.setData(x=[az], y=[alt])
        self.pointerHor.setVisible(True)

    def setupView(self) -> None:
        """ """
        plotItem = self.ui.horizon.p[0]
        if self.ui.editModeHor.isChecked():
            self.horizonPlot = pg.PlotDataItem(
                symbolBrush=pg.mkBrush(color=self.M_PINK + "40"),
                symbolPen=pg.mkPen(color=self.M_PINK1, width=2),
                brush=pg.mkBrush(color=self.M_PINK + "40"),
                pen=pg.mkPen(color=self.M_PINK1, width=2),
                symbolSize=10,
                symbol="o",
                connect="all",
            )
            plotItem.addItem(self.horizonPlot)
            vb = plotItem.getViewBox()
            vb.setPlotDataItem(self.horizonPlot)
            vb.updateData = self.updateDataHorizon
            vb.setOpts(enableLimitX=True)
        else:
            self.horizonPlot = pg.PlotDataItem(
                symbolBrush=pg.mkBrush(color=self.M_PRIM + "40"),
                symbolPen=pg.mkPen(color=self.M_PRIM1, width=2),
                brush=pg.mkBrush(color=self.M_PRIM + "40"),
                pen=pg.mkPen(color=self.M_PRIM1, width=2),
                symbolSize=5,
                symbol="o",
                connect="all",
            )
            plotItem.addItem(self.horizonPlot)

    def drawTab(self) -> None:
        """ """
        self.prepareView()
        if self.ui.showTerrain.isChecked():
            self.drawTerrainImage(self.ui.horizon.p[0])
        self.setupView()
        self.drawView()
        if self.ui.editModeHor.isChecked():
            self.setupPointer()
            self.drawPointer()
