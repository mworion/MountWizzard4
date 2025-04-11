############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from pathlib import Path

# external packages
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QFont, QGuiApplication, QCursor

import numpy as np
import cv2
import pyqtgraph as pg

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.slewInterface import SlewInterface
from gui.widgets import hemisphere_ui
from base.transform import diffModulusAbs


class HemisphereWindow(MWidget, SlewInterface):
    """
    the hemisphere window class handles all interaction with model points
    show / edit etc. the z orders is aligned as follows:

    on the static plane we have (and set to the z order)
        - terrain image         -10
        - horizon               0
        - horizon limits        0
        - celestial path        0
        - meridian limit track  10
        - meridian limit slew   20
        - alignment stars       30
        - build points          40
        - checked build points  50
    """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.ui = hemisphere_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.operationMode = "normal"
        self.pointerDome = None
        self.modelPointsText = []
        self.alignmentStars = None
        self.alignmentStarsText = None
        self.horizonLimitHigh = None
        self.horizonLimitLow = None
        self.meridianSlew = None
        self.meridianTrack = None
        self.imageTerrain = None
        self.hemMouse = None
        self.horizonPlot = None
        self.imageTerrain = None
        self.pointerHor = None

    def initConfig(self):
        """ """
        config = self.app.config.get("hemisphereW", {})
        fileName = Path(config.get("horizonMaskFileName", ""))
        self.ui.horizonMaskFileName.setText(fileName.stem)
        self.app.data.loadHorizonP(fileName=fileName.stem)
        fileName = config.get("terrainFileName", "")
        self.setTerrainFile(fileName)
        self.positionWindow(config)

        self.setTabAndIndex(self.ui.tabWidget, config, "orderMain")
        self.ui.showSlewPath.setChecked(config.get("showSlewPath", False))
        self.ui.showMountLimits.setChecked(config.get("showMountLimits", False))
        self.ui.showCelestial.setChecked(config.get("showCelestial", False))
        self.ui.showAlignStar.setChecked(config.get("showAlignStar", False))
        self.ui.showHorizon.setChecked(config.get("showHorizon", True))
        self.ui.showPolar.setChecked(config.get("showPolar", False))
        self.ui.showTerrain.setChecked(config.get("showTerrain", False))
        self.ui.showIsoModel.setChecked(config.get("showIsoModel", False))
        self.ui.tabWidget.setCurrentIndex(config.get("tabWidget", 0))
        self.ui.terrainAlpha.setValue(config.get("terrainAlpha", 0.35))
        self.ui.azimuthShift.setValue(config.get("azimuthShift", 0))
        self.ui.altitudeShift.setValue(config.get("altitudeShift", 0))
        self.ui.azimuthShift.valueChanged.connect(self.drawHorizonTab)
        self.ui.altitudeShift.valueChanged.connect(self.drawHorizonTab)
        self.ui.terrainAlpha.valueChanged.connect(self.drawHorizonTab)
        self.ui.normalModeHor.clicked.connect(self.setOperationModeHor)
        self.ui.editModeHor.clicked.connect(self.setOperationModeHor)
        self.ui.saveHorizonMask.clicked.connect(self.saveHorizonMask)
        self.ui.saveHorizonMaskAs.clicked.connect(self.saveHorizonMaskAs)
        self.ui.loadHorizonMask.clicked.connect(self.loadHorizonMask)
        self.ui.loadTerrainFile.clicked.connect(self.loadTerrainFile)
        self.ui.clearTerrainFile.clicked.connect(self.clearTerrainFile)
        self.ui.clearHorizonMask.clicked.connect(self.clearHorizonMask)
        self.ui.horizon.p[0].scene().sigMouseMoved.connect(self.mouseMovedHorizon)
        self.ui.addPositionToHorizon.clicked.connect(self.addActualPosition)
        self.app.mount.signals.pointDone.connect(self.drawPointerHor)
        self.ui.showTerrain.clicked.connect(self.drawHorizonTab)

        isMovable = self.app.config["mainW"].get("tabsMovable", False)
        self.enableTabsMovable(isMovable)

    def storeConfig(self):
        """ """
        configMain = self.app.config
        configMain["hemisphereW"] = {}
        config = configMain["hemisphereW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()
        self.getTabAndIndex(self.ui.tabWidget, config, "orderMain")
        config["showSlewPath"] = self.ui.showSlewPath.isChecked()
        config["showMountLimits"] = self.ui.showMountLimits.isChecked()
        config["showCelestial"] = self.ui.showCelestial.isChecked()
        config["showAlignStar"] = self.ui.showAlignStar.isChecked()
        config["showHorizon"] = self.ui.showHorizon.isChecked()
        config["showPolar"] = self.ui.showPolar.isChecked()
        config["showTerrain"] = self.ui.showTerrain.isChecked()
        config["showIsoModel"] = self.ui.showIsoModel.isChecked()
        config["tabWidget"] = self.ui.tabWidget.currentIndex()
        config["horizonMaskFileName"] = self.ui.horizonMaskFileName.text()
        config["terrainFileName"] = self.ui.terrainFileName.text()
        config["terrainAlpha"] = self.ui.terrainAlpha.value()
        config["azimuthShift"] = self.ui.azimuthShift.value()
        config["altitudeShift"] = self.ui.altitudeShift.value()

    def enableTabsMovable(self, isMovable):
        """ """
        self.ui.tabWidget.setMovable(isMovable)

    def closeEvent(self, closeEvent):
        """ """
        self.ui.normalModeHem.setChecked(True)
        self.ui.normalModeHor.setChecked(True)
        self.storeConfig()
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return:
        """
        self.app.update3s.connect(self.drawAlignmentStars)
        self.app.colorChange.connect(self.colorChange)
        self.app.updatePointMarker.connect(self.setupModel)
        self.app.redrawHemisphere.connect(self.drawHemisphereTab)
        self.app.redrawHorizon.connect(self.drawHorizonOnHem)
        self.app.operationRunning.connect(self.enableOperationModeChange)
        self.app.mount.signals.pointDone.connect(self.drawPointerHem)
        self.app.dome.signals.azimuth.connect(self.drawDome)
        self.app.dome.signals.deviceDisconnected.connect(self.drawDome)
        self.app.dome.signals.serverDisconnected.connect(self.drawDome)
        self.ui.normalModeHem.clicked.connect(self.setOperationModeHem)
        self.ui.editModeHem.clicked.connect(self.setOperationModeHem)
        self.ui.alignmentModeHem.clicked.connect(self.setOperationModeHem)

        self.app.mount.signals.getModelDone.connect(self.drawHemisphereTab)
        self.app.mount.signals.settingDone.connect(self.updateOnChangedParams)
        self.app.tabsMovable.connect(self.enableTabsMovable)
        self.ui.showSlewPath.clicked.connect(self.drawHemisphereTab)
        self.ui.showHorizon.clicked.connect(self.drawHemisphereTab)
        self.ui.showAlignStar.clicked.connect(self.drawHemisphereTab)
        self.ui.showMountLimits.clicked.connect(self.drawHemisphereTab)
        self.ui.showCelestial.clicked.connect(self.drawHemisphereTab)
        self.ui.showPolar.clicked.connect(self.drawHemisphereTab)
        self.ui.showTerrain.clicked.connect(self.drawHemisphereTab)
        self.ui.showIsoModel.clicked.connect(self.drawHemisphereTab)
        self.ui.hemisphere.p[0].scene().sigMouseMoved.connect(self.mouseMoved)

        sett = self.app.mount.setting
        self.meridianSlew = sett.meridianLimitSlew
        self.meridianTrack = sett.meridianLimitTrack
        self.horizonLimitHigh = sett.horizonLimitHigh
        self.horizonLimitLow = sett.horizonLimitLow
        self.drawHemisphereTab()
        self.drawHorizonTab()
        self.setIcons()
        self.show()

    def setIcons(self):
        """ """
        self.wIcon(self.ui.loadTerrainFile, "load")
        self.wIcon(self.ui.clearTerrainFile, "trash")
        self.wIcon(self.ui.loadHorizonMask, "load")
        self.wIcon(self.ui.saveHorizonMask, "save")
        self.wIcon(self.ui.saveHorizonMaskAs, "save")
        self.wIcon(self.ui.clearHorizonMask, "trash")

    def mouseMoved(self, pos):
        """ """
        viewBox = self.ui.hemisphere.p[0].getViewBox()
        mousePoint = viewBox.mapSceneToView(pos)

        if viewBox.posInViewRange(pos):
            self.ui.azimuth.setText(f"{mousePoint.x():3.1f}")
            self.ui.altitude.setText(f"{mousePoint.y():3.1f}")
            QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.ui.azimuth.setText("")
            self.ui.altitude.setText("")
            QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def colorChange(self):
        """ """
        self.setStyleSheet(self.mw4Style)
        self.ui.hemisphere.colorChange()
        self.ui.horizon.colorChange()
        self.drawHemisphereTab()
        self.setIcons()

    def enableOperationModeChange(self, status):
        """ """
        isRunning = status != 0
        if isRunning:
            self.ui.normalModeHem.setChecked(True)
        self.ui.operationModeGroup.setEnabled(not isRunning)

    def setOperationModeHem(self):
        """ """
        if self.ui.editModeHem.isChecked():
            self.drawModelPoints()
        elif self.ui.alignmentModeHem.isChecked():
            self.ui.showAlignStar.setChecked(True)
            self.app.data.clearBuildP()

        self.drawHemisphereTab()

    def calculateRelevance(self, alt=None, az=None):
        """ """
        if self.app.mount.obsSite.location is None:
            isNorth = True
        else:
            isNorth = self.app.mount.obsSite.location.latitude.degrees > 0
        altFak = 1 - np.minimum(np.abs(alt - 30), 35) / 35
        if isNorth:
            azFak = 1 - np.minimum(diffModulusAbs(0, az - 180, 360), 75) / 75
        else:
            azFak = 1 - np.minimum(diffModulusAbs(0, az, 360), 75) / 75
        sumFak = np.sqrt(altFak * azFak)
        return sumFak

    def selectFontParam(self, relevance):
        """
        :return: calculated color
        """
        cMap = pg.ColorMap([0, 0.6, 1.0], [self.M_RED, self.M_YELLOW, self.M_GREEN])
        color = cMap[float(relevance)]
        size = 8 + int(relevance * 5)
        return color, size

    def updateOnChangedParams(self, sett):
        """ """
        needRedraw = False
        if self.meridianSlew != sett.meridianLimitSlew:
            self.meridianSlew = sett.meridianLimitSlew
            needRedraw = True
        if self.meridianTrack != sett.meridianLimitTrack:
            self.meridianTrack = sett.meridianLimitTrack
            needRedraw = True
        if self.horizonLimitHigh != sett.horizonLimitHigh:
            self.horizonLimitHigh = sett.horizonLimitHigh
            needRedraw = True
        if self.horizonLimitLow != sett.horizonLimitLow:
            self.horizonLimitLow = sett.horizonLimitLow
            needRedraw = True
        if needRedraw:
            self.drawHemisphereTab()
        return needRedraw

    @staticmethod
    def preparePlotItem(plotItem):
        """ """
        plotItem.clear()
        plotItem.showAxes(True, showValues=True)
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        xTicks = [(x, f"{x:0.0f}") for x in np.arange(30, 331, 30)]
        plotItem.getAxis("bottom").setTicks([xTicks])
        plotItem.getAxis("top").setTicks([xTicks])
        yTicks = [(x, f"{x:0.0f}") for x in np.arange(10, 90, 10)]
        plotItem.getAxis("left").setTicks([yTicks])
        plotItem.getAxis("right").setTicks([yTicks])
        plotItem.setLabel("bottom", "Azimuth [deg]")
        plotItem.setLabel("left", "Altitude [deg]")
        plotItem.setLimits(
            xMin=0,
            xMax=360,
            yMin=0,
            yMax=90,
            minXRange=120,
            maxXRange=360,
            minYRange=30,
            maxYRange=90,
        )
        plotItem.setXRange(0, 360)
        plotItem.setYRange(0, 90)
        plotItem.disableAutoRange()

    def preparePolarItem(self, plotItem):
        """ """
        plotItem.clear()
        showPolar = self.ui.showPolar.isChecked()
        if not showPolar:
            self.ui.hemisphere.ci.layout.setColumnStretchFactor(0, 17)
            self.ui.hemisphere.ci.layout.setColumnStretchFactor(1, 0)
            plotItem.setVisible(False)
            return False

        plotItem.setVisible(True)
        self.ui.hemisphere.ci.layout.setColumnStretchFactor(0, 17)
        self.ui.hemisphere.ci.layout.setColumnStretchFactor(1, 10)
        plotItem.showAxes(False, showValues=False)
        plotItem.setMouseEnabled(x=False, y=False)
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        plotItem.setXRange(-90, 90)
        plotItem.setYRange(-90, 90)
        plotItem.disableAutoRange()
        self.ui.hemisphere.setGrid(plotItem=plotItem, reverse=True)
        lat = self.app.mount.obsSite.location.latitude.degrees
        self.ui.hemisphere.plotLoc(lat, plotItem=plotItem)
        return True

    def prepareHemisphere(self):
        """ """
        plotItem = self.ui.hemisphere.p[0]
        self.preparePlotItem(plotItem)
        polarItem = self.ui.hemisphere.p[1]
        self.preparePolarItem(polarItem)
        self.pointerDome = None
        self.modelPointsText = []
        self.alignmentStars = None
        self.alignmentStarsText = None
        plotItem.getViewBox().callbackMDC = self.mouseDoubleClick

    def drawCelestialEquator(self):
        """ """
        celestial = self.app.data.generateCelestialEquator()
        if not celestial:
            return False

        for i, plotItem in enumerate(self.ui.hemisphere.p):
            alt, az = zip(*celestial)
            alt = np.array(alt)
            az = np.array(az)
            pd = pg.ScatterPlotItem()
            if i == 1:
                az, alt = self.ui.hemisphere.toPolar(az, alt)
            pd.setData(
                x=az,
                y=alt,
                symbol="o",
                pen=pg.mkPen(color=self.M_TER1, size=0.9),
                brush=pg.mkBrush(color=self.M_TER),
                size=0.9,
            )
            plotItem.addItem(pd)
        return True

    def drawHorizonOnHem(self):
        """ """
        p0 = self.ui.hemisphere.p[0]
        p1 = self.ui.hemisphere.p[1]
        self.ui.hemisphere.drawHorizon(self.app.data.horizonP, plotItem=p0)
        self.ui.hemisphere.drawHorizon(self.app.data.horizonP, plotItem=p1, polar=True)

    def drawTerrainMask(self, plotItem):
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

    def drawMeridianLimits(self):
        """ """
        slew = self.app.mount.setting.meridianLimitSlew
        track = self.app.mount.setting.meridianLimitTrack
        if slew is None or track is None:
            return

        plotItem = self.ui.hemisphere.p[0]

        mSlew = pg.QtWidgets.QGraphicsRectItem(180 - slew, 0, 2 * slew, 90)
        mSlew.setPen(pg.mkPen(color=self.M_YELLOW1 + "40"))
        mSlew.setBrush(pg.mkBrush(color=self.M_YELLOW + "40"))
        mSlew.setZValue(10)
        plotItem.addItem(mSlew)

        mTrack = pg.QtWidgets.QGraphicsRectItem(180 - track, 0, 2 * track, 90)
        mTrack.setPen(pg.mkPen(color=self.M_YELLOW1 + "40"))
        mTrack.setBrush(pg.mkBrush(color=self.M_YELLOW + "40"))
        mTrack.setZValue(20)
        plotItem.addItem(mTrack)

    def drawHorizonLimits(self):
        """ """
        plotItem = self.ui.hemisphere.p[0]
        if self.app.mount.setting.horizonLimitHigh is not None:
            high = self.app.mount.setting.horizonLimitHigh
        else:
            high = 90

        if self.app.mount.setting.horizonLimitLow is not None:
            low = self.app.mount.setting.horizonLimitLow
        else:
            low = 0

        hLow = pg.QtWidgets.QGraphicsRectItem(0, high, 360, 90 - high)
        hLow.setPen(pg.mkPen(color=self.M_RED1 + "40"))
        hLow.setBrush(pg.mkBrush(color=self.M_RED + "40"))
        hLow.setZValue(0)
        plotItem.addItem(hLow)

        hHigh = pg.QtWidgets.QGraphicsRectItem(0, 0, 360, low)
        hHigh.setPen(pg.mkPen(color=self.M_RED1 + "40"))
        hHigh.setBrush(pg.mkBrush(color=self.M_RED + "40"))
        hHigh.setZValue(0)
        plotItem.addItem(hHigh)

    def setupAlignmentStars(self):
        """ """
        plotItem = self.ui.hemisphere.p[0]
        hip = self.app.hipparcos
        self.alignmentStarsText = []
        pd = pg.ScatterPlotItem(symbol="star", size=6, pen=pg.mkPen(color=self.M_YELLOW1))
        pd.setZValue(30)
        self.alignmentStars = pd
        plotItem.addItem(pd)
        for i in range(len(hip.name)):
            textItem = pg.TextItem(anchor=(0.5, 1.1))
            self.alignmentStarsText.append(textItem)
            plotItem.addItem(textItem)

    def drawAlignmentStars(self):
        """ """
        if not self.ui.showAlignStar.isChecked():
            return
        if self.alignmentStars is None:
            return

        hip = self.app.hipparcos
        hip.calculateAlignStarPositionsAltAz()
        isAlignMode = self.ui.alignmentModeHem.isChecked()
        self.alignmentStars.setData(x=hip.az, y=hip.alt)
        for i, val in enumerate(zip(hip.alt, hip.az, hip.name)):
            alt, az, name = val
            color = self.M_YELLOW if isAlignMode else self.M_YELLOW1

            size = 10 if isAlignMode else 6
            if isAlignMode:
                rel = self.calculateRelevance(alt=alt, az=az)
                fontColor, fontSize = self.selectFontParam(rel)
            else:
                fontSize = 8
                fontColor = self.M_TER1

            item = self.alignmentStars.points()[i]
            item.setPen(pg.mkPen(color=color))
            item.setBrush(pg.mkBrush(color=color))
            item.setSize(size)
            font = QFont(
                self.window().font().family(),
                int(self.window().font().pointSize() * fontSize / 9),
            )
            self.alignmentStarsText[i].setText(name)
            self.alignmentStarsText[i].setFont(font)
            self.alignmentStarsText[i].setColor(fontColor)
            self.alignmentStarsText[i].setPos(az, alt)
            self.alignmentStarsText[i].setZValue(30)

    def drawModelPoints(self):
        """ """
        points = self.app.data.buildP
        if not points:
            return

        x = [x[1] for x in points]
        y = [x[0] for x in points]
        act = [x[2] for x in points]

        for index, plotItem in enumerate(self.ui.hemisphere.p):
            item = self.ui.hemisphere.findItemByName(plotItem, "model")
            if not item:
                continue
            if index == 1:
                x, y = self.ui.hemisphere.toPolar(x, y)
            item.setData(x=x, y=y)

            isEdit = self.ui.editModeHem.isChecked()
            for i in range(len(x)):
                active = act[i]
                col = [self.M_TER, self.M_GREEN, self.M_RED]
                colActive = col[active]
                color = self.M_PINK if isEdit else colActive
                sym = ["d", "o", "x"]
                symbol = sym[active]

                spot = item.scatter.points()[i]
                spot.setPen(pg.mkPen(color=color, width=1.5))
                spot.setBrush(pg.mkBrush(color=color + "40"))
                spot.setSymbol(symbol)

    def drawModelText(self):
        """ """
        plotItem = self.ui.hemisphere.p[0]
        points = self.app.data.buildP
        if not points:
            return
        x = [x[1] for x in points]
        y = [x[0] for x in points]
        act = [x[2] for x in points]

        for textItem in self.modelPointsText:
            self.ui.hemisphere.p[0].removeItem(textItem)
        self.modelPointsText = []
        isEdit = self.ui.editModeHem.isChecked()
        if isEdit:
            facFont = 1
        else:
            facFont = 0.85
        font = QFont(
            self.window().font().family(),
            int(self.window().font().pointSize() * facFont),
        )
        for i in range(len(x)):
            az = x[i]
            alt = y[i]
            active = act[i]
            col = [self.M_TER, self.M_GREEN, self.M_RED]
            colActive = col[active]
            color = self.M_PINK if isEdit else colActive

            text = f"{i + 1}"
            textItem = pg.TextItem(anchor=(0.5, 1.1))
            textItem.setText(text)
            textItem.setFont(font)
            textItem.setColor(color)
            textItem.setPos(az, alt)
            textItem.setZValue(40)
            self.modelPointsText.append(textItem)
            plotItem.addItem(textItem)

    def updateDataModel(self, x, y):
        """ """
        bp = [(y, x, True) for y, x in zip(y, x)]
        self.app.data.buildP = bp
        self.drawModelPoints()
        self.drawModelText()
        self.app.buildPointsChanged.emit()

    def setupModel(self):
        """ """
        for i, plotItem in enumerate(self.ui.hemisphere.p):
            if self.ui.showSlewPath.isChecked():
                pen = pg.mkPen(color=self.M_GREEN, style=Qt.PenStyle.DashLine)
            else:
                pen = None

            if self.ui.editModeHem.isChecked():
                pd = pg.PlotDataItem(
                    symbolBrush=pg.mkBrush(color=self.M_PINK + "40"),
                    symbolPen=pg.mkPen(color=self.M_PINK1, width=2),
                    symbolSize=10,
                    symbol="o",
                    connect="all",
                    pen=pen,
                )
                pd.nameStr = "model"
                vb = plotItem.getViewBox()
                vb.setPlotDataItem(pd)
                if i == 0:
                    vb.updateData = self.updateDataModel
            else:
                pd = pg.PlotDataItem(
                    symbolBrush=pg.mkBrush(color=self.M_GREEN + "40"),
                    symbolPen=pg.mkPen(color=self.M_GREEN1, width=2),
                    symbolSize=8,
                    symbol="o",
                    connect="all",
                    pen=pen,
                )
                pd.nameStr = "model"
                vb = plotItem.getViewBox()
                if i == 0:
                    vb.setPlotDataItem(None)
            pd.setZValue(40)
            plotItem.addItem(pd)

        self.drawModelPoints()
        self.drawModelText()

    def setupPointerHem(self):
        """ """
        for plotItem in self.ui.hemisphere.p:
            symbol = self.makePointer()
            pd = pg.ScatterPlotItem(symbol=symbol, size=40)
            pd.setData(x=[0], y=[0])
            pd.setPen(pg.mkPen(color=self.M_PINK))
            pd.setBrush(pg.mkBrush(color=self.M_PINK + "20"))
            pd.setZValue(60)
            pd.nameStr = "pointer"
            plotItem.addItem(pd)

    def drawPointerHem(self):
        """ """
        items = []
        for plotItem in self.ui.hemisphere.p:
            item = self.ui.hemisphere.findItemByName(plotItem, "pointer")
            if item:
                items.append(item)

        obsSite = self.app.mount.obsSite
        isVisible = not (obsSite.Alt is None or obsSite.Az is None)
        for item in items:
            item.setVisible(isVisible)

        if not isVisible or not items:
            return False

        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        items[0].setData(x=[az], y=[alt])
        x, y = self.ui.hemisphere.toPolar([az], [alt])
        items[1].setData(x=x, y=y)
        return True

    def setupDome(self):
        """ """
        plotItem = self.ui.hemisphere.p[0]
        self.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
        self.pointerDome.setPen(pg.mkPen(color=self.M_SEC))
        self.pointerDome.setBrush(pg.mkBrush(color=self.M_SEC + "80"))
        self.pointerDome.setVisible(False)
        plotItem.addItem(self.pointerDome)

    def drawDome(self, azimuth=None):
        """ """
        if not isinstance(azimuth, (int, float)):
            self.pointerDome.setVisible(False)
            return False

        visible = self.app.deviceStat.get("dome", False)
        self.pointerDome.setRect(azimuth - 15, 1, 30, 88)
        self.pointerDome.setVisible(visible)
        return True

    def getMountModelData(self):
        """ """
        model = self.app.mount.model
        if len(model.starList) == 0:
            return None, None, None
        alt = np.array([x.alt.degrees for x in model.starList])
        az = np.array([x.az.degrees for x in model.starList])
        err = np.array([x.errorRMS for x in model.starList])
        return az, alt, err

    def drawModelIsoCurve(self):
        """ """
        az, alt, err = self.getMountModelData()
        if az is None or alt is None or err is None:
            return

        self.ui.hemisphere.addIsoItemHorizon(az, alt, err)

    def drawHemisphereTab(self):
        """ """
        hasModel = bool(self.app.mount.model.numberStars)
        self.ui.alignmentModeHem.setEnabled(hasModel)
        self.ui.showIsoModel.setEnabled(hasModel)
        isMount = bool(self.app.deviceStat["mount"])
        self.ui.showMountLimits.setEnabled(isMount)

        self.prepareHemisphere()
        if self.ui.showCelestial.isChecked():
            self.drawCelestialEquator()
        if self.ui.showTerrain.isChecked():
            self.drawTerrainMask(self.ui.hemisphere.p[0])
        if self.ui.showMountLimits.isChecked():
            self.drawMeridianLimits()
            self.drawHorizonLimits()
        if self.ui.showIsoModel.isChecked():
            self.drawModelIsoCurve()
        self.setupAlignmentStars()
        self.drawAlignmentStars()
        self.setupModel()
        self.setupPointerHem()
        self.drawPointerHem()
        self.setupDome()
        self.drawDome()
        self.ui.hemisphere.p[1].getViewBox().rightMouseRange()
        if self.ui.showHorizon.isChecked():
            self.drawHorizonOnHem()

    def slewDirect(self, posView):
        """ """
        azimuth = int(posView.x() + 0.5)
        altitude = int(posView.y() + 0.5)

        question = "<b>Manual slewing to coordinate</b>"
        question += "<br><br>Selected coordinates are:<br>"
        question += f"<font color={self.M_PRIM}> Altitude: {altitude:3.1f}°"
        question += f"   Azimuth: {azimuth:3.1f}°</font>"
        question += "<br><br>Would you like to start slewing?<br>"

        suc = self.messageDialog(self, "Slewing mount", question)
        if not suc:
            return
        self.slewTargetAltAz(altitude, azimuth)

    def slewStar(self, posView):
        """ """
        spot = self.alignmentStars.pointsAt(posView)
        if len(spot) == 0:
            return

        index = spot[0].index()
        hip = self.app.hipparcos
        name = hip.name[index]
        ra, dec = hip.getAlignStarRaDecFromName(hip.name[index])

        question = "<b>Polar / Ortho Alignment procedure</b>"
        question += "<br>Selected alignment star: "
        question += f"<font color={self.M_PRIM}>{name}.</font>"
        question += "<br>Would you like to start alignment?<br>"

        isDAT = self.app.mount.setting.statusDualAxisTracking
        warning = f"<br><i><font color={self.M_YELLOW}>"
        warning += "Dual Axis Tracking is actually enabled!<br>"
        warning += "It should be off during alignment process.</font></i>"

        buttons = ["Cancel", "Ortho Align", "Polar Align"]
        question = question + warning if isDAT else question
        reply = self.messageDialog(self, "Slewing mount", question, buttons)
        if reply == 0:
            return
        elif reply == 1:
            alignType = "ortho"
        else:
            alignType = "polar"

        t = f"Align [{alignType}] to [{name}]"
        self.msg.emit(1, "Hemisphere", "Align", t)
        self.slewTargetRaDec(ra, dec, slewType=alignType, epoch="JNow")

    def mouseDoubleClick(self, ev, posView):
        """ """
        if self.ui.alignmentModeHem.isChecked():
            self.slewStar(posView)
        elif self.ui.normalModeHem.isChecked():
            self.slewDirect(posView)

    def mouseMovedHorizon(self, pos):
        """ """
        self.mouseMoved(pos)

    def setTerrainFile(self, fileName):
        """ """
        self.ui.terrainFileName.setText(str(fileName))
        terrainFile = self.app.mwGlob["configDir"] / fileName
        if not terrainFile.is_file():
            self.imageTerrain = None
            return False

        img = cv2.imread(terrainFile, cv2.IMREAD_GRAYSCALE)
        h, w = img.shape
        h2 = int(h / 2)
        img = img[0:h2, 0:w]
        img = cv2.resize(img, (1440, 360))
        img = cv2.flip(img, 0)
        self.imageTerrain = np.ones((480, 2880)) * 128
        self.imageTerrain[60:420, 0:1440] = img
        self.imageTerrain[60:420, 1440:2880] = img
        return True

    def loadTerrainFile(self):
        """ """
        folder = self.app.mwGlob["configDir"]
        fileTypes = "Terrain images (*.jpg)"
        loadFilePath = self.openFile(self, "Open terrain image", folder, fileTypes)
        if not loadFilePath.is_file():
            return False

        if self.setTerrainFile(loadFilePath):
            self.ui.terrainFileName.setText(loadFilePath.stem)
            self.ui.showTerrain.setChecked(True)
            self.msg.emit(0, "Hemisphere", "Terrain", f"Mask [{loadFilePath.stem}] loaded")
        else:
            self.msg.emit(
                2,
                "Hemisphere",
                "Terrain",
                f"Image [{loadFilePath.stem}] cannot be loaded",
            )
        self.drawHorizonTab()
        return True

    def clearTerrainFile(self):
        """ """
        self.ui.terrainFileName.setText("")
        self.ui.showTerrain.setChecked(False)
        self.setTerrainFile("")
        self.drawHorizonTab()

    def loadHorizonMask(self):
        """ """
        folder = self.app.mwGlob["configDir"]
        fileTypes = "Horizon mask files (*.hpts);; CSV Files (*.csv);; MW3 Files (*.txt)"
        loadFilePath = self.openFile(self, "Open horizon mask file", folder, fileTypes)
        if not loadFilePath.is_file():
            return False

        suc = self.app.data.loadHorizonP(fileName=loadFilePath.stem, ext=loadFilePath.suffix)
        if suc:
            self.ui.horizonMaskFileName.setText(loadFilePath.stem)
            self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{loadFilePath.stem}] loaded")
        else:
            self.msg.emit(
                2,
                "Hemisphere",
                "Horizon",
                f"Mask [{loadFilePath.stem}] cannot no be loaded",
            )

        self.app.redrawHemisphere.emit()
        self.app.redrawHorizon.emit()
        self.drawHorizonTab()
        return True

    def saveHorizonMask(self):
        """ """
        fileName = self.ui.horizonMaskFileName.text()
        if not fileName:
            self.msg.emit(2, "Hemisphere", "Horizon", "Mask file name not given")
            return False

        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{fileName}] saved")
        else:
            self.msg.emit(2, "Hemisphere", "Horizon", f"Mask [{fileName}] cannot no be saved")
        return True

    def saveHorizonMaskAs(self):
        """ """
        folder = self.app.mwGlob["configDir"]
        saveFilePath, fileName, ext = self.saveFile(
            self, "Save horizon mask file", folder, "Horizon mask files (*.hpts)"
        )
        if not saveFilePath:
            return False

        suc = self.app.data.saveHorizonP(fileName=fileName)
        if suc:
            self.ui.horizonMaskFileName.setText(fileName)
            self.msg.emit(0, "Hemisphere", "Horizon", f"Mask [{fileName}] saved")
        else:
            self.msg.emit(2, "Hemisphere", "Horizon", f"Mask [{fileName}] cannot no be saved")
        return True

    def setOperationModeHor(self):
        """ """
        if self.ui.editModeHor.isChecked():
            self.ui.addPositionToHorizon.setEnabled(True)
        else:
            self.ui.addPositionToHorizon.setEnabled(False)

        self.drawHorizonTab()

    def updateDataHorizon(self, x, y):
        """ """
        hp = [(y, x) for y, x in zip(y, x)]
        hp.sort(key=lambda x: x[1])
        x = [x[1] for x in hp]
        y = [x[0] for x in hp]
        self.horizonPlot.setData(x=x, y=y)
        self.app.data.horizonP = hp
        self.app.redrawHorizon.emit()

    def clearHorizonMask(self):
        """ """
        self.app.data.horizonP = []
        self.ui.horizonMaskFileName.setText("")
        self.app.redrawHorizon.emit()
        self.drawHorizonTab()

    def addActualPosition(self):
        """ """
        vb = self.ui.horizon.p[0].getViewBox()
        az = self.app.mount.obsSite.Az
        alt = self.app.mount.obsSite.Alt
        if alt is None and az is None:
            return False
        az = az.degrees
        alt = alt.degrees
        index = vb.getNearestPointIndex(QPointF(az, alt))
        if index is not None:
            vb.addUpdate(index, QPointF(az, alt))
        return True

    def prepareHorizonView(self):
        """ """
        plotItem = self.ui.horizon.p[0]
        self.preparePlotItem(plotItem)
        self.pointerHor = None

    def drawHorizonView(self):
        """ """
        hp = self.app.data.horizonP
        if len(hp) == 0:
            return False
        alt, az = zip(*hp)
        alt = np.array(alt)
        az = np.array(az)
        self.horizonPlot.setData(x=az, y=alt)
        return True

    def setupPointerHor(self):
        """ """
        plotItem = self.ui.horizon.p[0]
        symbol = self.makePointer()
        self.pointerHor = pg.ScatterPlotItem(symbol=symbol, size=40)
        self.pointerHor.setData(x=[0], y=[45])
        self.pointerHor.setPen(pg.mkPen(color=self.M_PINK))
        self.pointerHor.setBrush(pg.mkBrush(color=self.M_PINK + "20"))
        self.pointerHor.setZValue(10)
        plotItem.addItem(self.pointerHor)

    def drawPointerHor(self):
        """ """
        if self.pointerHor is None:
            return False

        obsSite = self.app.mount.obsSite
        if obsSite.Alt is None or obsSite.Az is None:
            self.pointerHor.setVisible(False)
            return False

        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerHor.setData(x=[az], y=[alt])
        self.pointerHor.setVisible(True)
        return True

    def setupHorizonView(self):
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

    def drawHorizonTab(self):
        """ """
        self.prepareHorizonView()
        if self.ui.showTerrain.isChecked():
            self.drawTerrainMask(self.ui.horizon.p[0])
        self.setupHorizonView()
        self.drawHorizonView()
        if self.ui.editModeHor.isChecked():
            self.setupPointerHor()
            self.drawPointerHor()
