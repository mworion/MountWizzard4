############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import cv2
import numpy as np
import pyqtgraph as pg
from mw4.gui.utilities.generateSprites import makePointer
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtCore import QPointF


class HorizonDraw(MWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = parent.ui
        self.app = parent.app
        self.msg = parent.msg
        self.horizonPlot: pg.PlotDataItem = pg.PlotDataItem()
        self.imageTerrain: np.ndarray = np.zeros((0, 0))
        self.pointerHor: pg.ScatterPlotItem = pg.ScatterPlotItem()

    def initConfig(self) -> None:
        config = self.app.config.get("hemisphereW", {})
        fileName = config.get("horizonMaskFileName", "")
        self.ui.horizonMaskFileName.setText(fileName)
        horizonFile = self.app.mwGlob["configDir"] / (
            self.ui.horizonMaskFileName.text() + ".hpts"
        )
        self.app.data.loadHorizonP(horizonFile)
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
        self.app.mount.signals.settingDone.connect(self.drawTab)
        self.ui.showMountLimits.clicked.connect(self.drawTab)
        self.ui.horizon.p[0].scene().sigMouseMoved.connect(self.mouseMovedHorizon)
        self.app.mount.signals.mountIsUp.connect(self.setPointerVisibility)

    def closeTab(self):
        self.app.mount.signals.pointDone.disconnect(self.drawPointer)
        self.app.mount.signals.settingDone.disconnect(self.drawTab)
        self.app.mount.signals.mountIsUp.disconnect(self.setPointerVisibility)

    def setPointerVisibility(self, status) -> None:
        self.pointerHor.setVisible(status)

    def mouseMovedHorizon(self, pos: QPointF) -> None:
        self.parent.mouseMoved(pos)

    def loadTerrainImage(self, terrainFile: Path) -> None:
        if not terrainFile.is_file():
            self.imageTerrain = np.ones((240, 720)) * 128
            return

        imgLoad = np.array(cv2.imread(terrainFile, cv2.IMREAD_GRAYSCALE))
        height, width = imgLoad.shape
        if 2 * height != width:
            self.msg.emit(
                0, "Hemisphere", "Terrain", "Wrong aspect ration of image, should be 2:1"
            )
            return

        imgLoad = cv2.resize(imgLoad, (360, 180))
        imgLoad = imgLoad[0:90, 0:360]
        imgLoad = cv2.flip(imgLoad, 0)
        self.imageTerrain = np.ones((240, 720)) * 128
        self.imageTerrain[30:120, 0:360] = imgLoad
        self.imageTerrain[30:120, 360:720] = imgLoad

    def selectTerrainFile(self) -> None:
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
        self.ui.terrainFileName.setText("")
        self.ui.showTerrain.setChecked(False)
        self.parent.redrawAll()

    def loadHorizonMask(self) -> None:
        folder = self.app.mwGlob["configDir"]
        fileTypes = "Horizon mask files (*.hpts);; CSV Files (*.csv);; MW3 Files (*.txt)"
        loadFilePath = self.openFile(self.parent, "Open horizon mask file", folder, fileTypes)
        if not loadFilePath.is_file():
            return

        self.app.data.loadHorizonP(loadFilePath)
        self.ui.horizonMaskFileName.setText(loadFilePath.stem)
        self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{loadFilePath.stem}] loaded")
        self.app.redrawHorizon.emit()

    def saveHorizonMask(self) -> None:
        fileName = self.ui.horizonMaskFileName.text()
        if not fileName:
            self.msg.emit(2, "Hemisphere", "Horizon", "Mask file name not given")
            return

        suc = self.app.data.saveHorizonP(fileName)
        if suc:
            self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{fileName}] saved")
        else:
            self.msg.emit(2, "Hemisphere", "Horizon", f"Mask [{fileName}] cannot no be saved")
        self.app.redrawHorizon.emit()

    def saveHorizonMaskAs(self) -> None:
        folder = self.app.mwGlob["configDir"]
        saveFilePath = self.saveFile(
            self.parent, "Save horizon mask file", folder, "Horizon mask files (*.hpts)"
        )
        if not saveFilePath.stem:
            return
        if self.app.data.saveHorizonP(saveFilePath.stem):
            self.ui.horizonMaskFileName.setText(saveFilePath.stem)
            self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{saveFilePath.stem}] saved")
        else:
            self.msg.emit(
                2, "Hemisphere", "Horizon", f"Mask [{saveFilePath.stem}] cannot no be saved"
            )
        self.app.redrawHorizon.emit()

    def setOperationMode(self) -> None:
        self.ui.addPositionToHorizon.setEnabled(self.ui.editModeHor.isChecked())
        self.app.redrawHorizon.emit()

    def updateDataHorizon(self, x: list, y: list) -> None:
        hp = [[y, x] for y, x in zip(y, x)]
        hp.sort(key=lambda s: x[1]) if len(x) > 1 else x
        y, x = zip(*hp)
        self.horizonPlot.setData(x=x, y=y)
        self.app.data.horizonP = hp
        self.drawTab()

    def clearHorizonMask(self) -> None:
        self.app.data.horizonP = []
        self.ui.horizonMaskFileName.setText("")
        self.app.redrawHorizon.emit()

    def addActualPosition(self) -> None:
        vb = self.ui.horizon.p[0].getViewBox()
        az = self.app.mount.obsSite.Az
        alt = self.app.mount.obsSite.Alt
        az = az.degrees
        alt = alt.degrees
        index = vb.getNearestPointIndex(QPointF(az, alt))
        if index is not None:
            vb.addUpdate(index, QPointF(az, alt))

    def prepareView(self) -> None:
        plotItem = self.ui.horizon.p[0]
        self.parent.preparePlotItem(plotItem)

    def drawView(self) -> None:
        hp = self.app.data.horizonP
        if len(hp) == 0:
            return
        alt, az = zip(*hp)
        alt = np.array(alt)
        az = np.array(az)
        self.horizonPlot.setData(x=az, y=alt)

    def setupPointer(self) -> None:
        plotItem = self.ui.horizon.p[0]
        symbol = makePointer()
        self.pointerHor = pg.ScatterPlotItem(symbol=symbol, size=40)
        self.pointerHor.setData(x=[0], y=[45])
        self.pointerHor.setPen(pg.mkPen(color=self.M_PINK))
        self.pointerHor.setBrush(pg.mkBrush(color=self.M_PINK + "20"))
        self.pointerHor.setZValue(10)
        plotItem.addItem(self.pointerHor)

    def drawPointer(self) -> None:
        obsSite = self.app.mount.obsSite
        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerHor.setData(x=[az], y=[alt])
        self.pointerHor.setVisible(False)

    def setupView(self) -> None:
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
        self.prepareView()
        if self.ui.showTerrain.isChecked():
            self.parent.drawTerrainImage(self.ui.horizon.p[0])
        if self.ui.showMountLimits.isChecked():
            self.parent.drawMeridianLimits(self.ui.horizon.p[0])
            self.parent.drawHorizonLimits(self.ui.horizon.p[0])
        self.setupView()
        self.drawView()
        if self.ui.editModeHor.isChecked():
            self.setupPointer()
            self.drawPointer()
