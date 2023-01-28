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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QGuiApplication, QCursor
import numpy as np
import cv2
import pyqtgraph as pg

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.slewInterface import SlewInterface
from gui.widgets import hemisphere_ui
from gui.extWindows.hemisphere.editHorizon import EditHorizon
from base.transform import diffModulusAbs


class HemisphereWindow(MWidget, EditHorizon, SlewInterface):
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

    __all__ = ['HemisphereWindow']

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.msg = app.msg
        self.ui = hemisphere_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.mwSuper('__init__')
        self.operationMode = 'normal'
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

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'hemisphereW' not in self.app.config:
            self.app.config['hemisphereW'] = {}
        config = self.app.config['hemisphereW']

        self.positionWindow(config)
        self.setTabAndIndex(self.ui.tabWidget, config, 'orderMain')
        self.ui.showSlewPath.setChecked(config.get('showSlewPath', False))
        self.ui.showMountLimits.setChecked(config.get('showMountLimits', False))
        self.ui.showCelestial.setChecked(config.get('showCelestial', False))
        self.ui.showAlignStar.setChecked(config.get('showAlignStar', False))
        self.ui.showHorizon.setChecked(config.get('showHorizon', True))
        self.ui.showPolar.setChecked(config.get('showPolar', False))
        self.ui.showTerrain.setChecked(config.get('showTerrain', False))
        self.ui.showIsoModel.setChecked(config.get('showIsoModel', False))
        self.ui.tabWidget.setCurrentIndex(config.get('tabWidget', 0))
        isMovable = self.app.config['mainW'].get('tabsMovable', False)
        self.enableTabsMovable(isMovable)

        self.mwSuper('initConfig')
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        if 'hemisphereW' not in config:
            config['hemisphereW'] = {}
        else:
            config['hemisphereW'].clear()
        config = config['hemisphereW']

        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        self.getTabAndIndex(self.ui.tabWidget, config, 'orderMain')
        config['showSlewPath'] = self.ui.showSlewPath.isChecked()
        config['showMountLimits'] = self.ui.showMountLimits.isChecked()
        config['showCelestial'] = self.ui.showCelestial.isChecked()
        config['showAlignStar'] = self.ui.showAlignStar.isChecked()
        config['showHorizon'] = self.ui.showHorizon.isChecked()
        config['showPolar'] = self.ui.showPolar.isChecked()
        config['showTerrain'] = self.ui.showTerrain.isChecked()
        config['showIsoModel'] = self.ui.showIsoModel.isChecked()
        config['tabWidget'] = self.ui.tabWidget.currentIndex()
        self.mwSuper('storeConfig')
        return True

    def enableTabsMovable(self, isMovable):
        """
        :param isMovable:
        :return:
        """
        self.ui.tabWidget.setMovable(isMovable)
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
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

        self.app.mount.signals.alignDone.connect(self.drawHemisphereTab)
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
        self.ui.hemisphere.p[0].scene().sigMouseMoved.connect(
            self.mouseMovedHemisphere)

        sett = self.app.mount.setting
        self.meridianSlew = sett.meridianLimitSlew
        self.meridianTrack = sett.meridianLimitTrack
        self.horizonLimitHigh = sett.horizonLimitHigh
        self.horizonLimitLow = sett.horizonLimitLow
        self.drawHemisphereTab()
        self.drawHorizonTab()
        self.show()
        return True

    def mouseMoved(self, plotItem, pos):
        """
        :param plotItem:
        :param pos:
        :return:
        """
        mousePoint = plotItem.getViewBox().mapSceneToView(pos)
        vr = plotItem.getViewBox().viewRange()
        x = mousePoint.x()
        y = mousePoint.y()
        if vr[0][0] < x < vr[0][1] and vr[1][0] < y < vr[1][1]:
            self.ui.azimuth.setText(f'{x:3.1f}')
            self.ui.altitude.setText(f'{y:3.1f}')
            QGuiApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        else:
            self.ui.azimuth.setText('')
            self.ui.altitude.setText('')
            QGuiApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        return True

    def mouseMovedHemisphere(self, pos):
        """
        :param pos:
        :return:
        """
        plotItem = self.ui.hemisphere.p[0]
        self.mouseMoved(plotItem, pos)
        return True

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.ui.hemisphere.colorChange()
        self.ui.horizon.colorChange()
        self.drawHemisphereTab()
        self.colorChangeHorizon()
        return True

    def enableOperationModeChange(self, status):
        """
        :param status:
        :return:
        """
        isRunning = status != 0
        if isRunning:
            self.ui.normalModeHem.setChecked(True)
        self.ui.operationModeGroup.setEnabled(not isRunning)
        return True

    def setOperationModeHem(self):
        """
        :return: success
        """
        if self.ui.editModeHem.isChecked():
            self.drawModelPoints()
        elif self.ui.alignmentModeHem.isChecked():
            self.ui.showAlignStar.setChecked(True)
            self.app.data.clearBuildP()

        self.drawHemisphereTab()
        return True

    def calculateRelevance(self, alt=None, az=None):
        """
        :param alt:
        :param az:
        :return:
        """
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
        :param relevance:
        :return: calculated color
        """
        cMap = pg.ColorMap([0, 0.6, 1.0], [self.M_RED, self.M_YELLOW, self.M_GREEN])
        color = cMap[float(relevance)]
        size = 8 + int(relevance * 5)
        return color, size

    def updateOnChangedParams(self, sett):
        """
        :param sett:
        :return: status redraw
        """
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
        """
        :param plotItem:
        :return:
        """
        plotItem.clear()
        plotItem.showAxes(True, showValues=True)
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        xTicks = [(x, f'{x:0.0f}') for x in np.arange(30, 331, 30)]
        plotItem.getAxis('bottom').setTicks([xTicks])
        plotItem.getAxis('top').setTicks([xTicks])
        yTicks = [(x, f'{x:0.0f}') for x in np.arange(10, 90, 10)]
        plotItem.getAxis('left').setTicks([yTicks])
        plotItem.getAxis('right').setTicks([yTicks])
        plotItem.setLabel('bottom', 'Azimuth [deg]')
        plotItem.setLabel('left', 'Altitude [deg]')
        plotItem.setLimits(xMin=0, xMax=360, yMin=0, yMax=90,
                           minXRange=120, maxXRange=360,
                           minYRange=30, maxYRange=90)
        plotItem.setXRange(0, 360)
        plotItem.setYRange(0, 90)
        plotItem.disableAutoRange()
        return True

    def preparePolarItem(self, plotItem):
        """
        :param plotItem:
        :return:
        """
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
        """
        :return:
        """
        plotItem = self.ui.hemisphere.p[0]
        self.preparePlotItem(plotItem)
        polarItem = self.ui.hemisphere.p[1]
        self.preparePolarItem(polarItem)
        self.pointerDome = None
        self.modelPointsText = []
        self.alignmentStars = None
        self.alignmentStarsText = None
        plotItem.getViewBox().callbackMDC = self.mouseDoubleClick
        return True

    def drawCelestialEquator(self):
        """
        :return:
        """
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
                x=az, y=alt, symbol='o', pen=pg.mkPen(color=self.M_WHITE1, size=0.9),
                brush=pg.mkBrush(color=self.M_WHITE), size=0.9)
            plotItem.addItem(pd)
        return True

    def drawHorizonOnHem(self):
        """
        :return:
        """
        p0 = self.ui.hemisphere.p[0]
        p1 = self.ui.hemisphere.p[1]
        self.ui.hemisphere.drawHorizon(self.app.data.horizonP, plotItem=p0)
        self.ui.hemisphere.drawHorizon(self.app.data.horizonP, plotItem=p1,
                                       polar=True)
        return True

    def drawTerrainMask(self, plotItem):
        """
        :return:
        """
        if self.imageTerrain is None:
            return False

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
        cMap = pg.colormap.get('CET-L2')
        imgItem.setColorMap(cMap)
        imgItem.setOpts(opacity=alpha)
        imgItem.setZValue(-10)
        plotItem.addItem(imgItem)
        return True

    def drawMeridianLimits(self):
        """
        :return:
        """
        slew = self.app.mount.setting.meridianLimitSlew
        track = self.app.mount.setting.meridianLimitTrack
        if slew is None or track is None:
            return False

        plotItem = self.ui.hemisphere.p[0]

        mSlew = pg.QtWidgets.QGraphicsRectItem(180 - slew, 0, 2 * slew, 90)
        mSlew.setPen(pg.mkPen(color=self.M_YELLOW1 + '40'))
        mSlew.setBrush(pg.mkBrush(color=self.M_YELLOW + '40'))
        mSlew.setZValue(10)
        plotItem.addItem(mSlew)

        mTrack = pg.QtWidgets.QGraphicsRectItem(180 - track, 0, 2 * track, 90)
        mTrack.setPen(pg.mkPen(color=self.M_YELLOW1 + '40'))
        mTrack.setBrush(pg.mkBrush(color=self.M_YELLOW + '40'))
        mTrack.setZValue(20)
        plotItem.addItem(mTrack)
        return True

    def drawHorizonLimits(self):
        """
        :return:
        """
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
        hLow.setPen(pg.mkPen(color=self.M_RED1 + '40'))
        hLow.setBrush(pg.mkBrush(color=self.M_RED + '40'))
        hLow.setZValue(0)
        plotItem.addItem(hLow)

        hHigh = pg.QtWidgets.QGraphicsRectItem(0, 0, 360, low)
        hHigh.setPen(pg.mkPen(color=self.M_RED1 + '40'))
        hHigh.setBrush(pg.mkBrush(color=self.M_RED + '40'))
        hHigh.setZValue(0)
        plotItem.addItem(hHigh)
        return True

    def setupAlignmentStars(self):
        """
        :return:
        """
        plotItem = self.ui.hemisphere.p[0]
        hip = self.app.hipparcos
        self.alignmentStarsText = []
        pd = pg.ScatterPlotItem(
            symbol='star', size=6, pen=pg.mkPen(color=self.M_YELLOW1))
        pd.setZValue(30)
        self.alignmentStars = pd
        plotItem.addItem(pd)
        for i in range(len(hip.name)):
            textItem = pg.TextItem(anchor=(0.5, 1.1))
            self.alignmentStarsText.append(textItem)
            plotItem.addItem(textItem)
        return True

    def drawAlignmentStars(self):
        """
        :return: true for test purpose
        """
        if not self.ui.showAlignStar.isChecked():
            return False
        if self.alignmentStars is None:
            return False

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
                fontColor = self.M_WHITE1

            item = self.alignmentStars.points()[i]
            item.setPen(pg.mkPen(color=color))
            item.setBrush(pg.mkBrush(color=color))
            item.setSize(size)
            font = QFont(self.window().font().family(),
                         int(self.window().font().pointSize() * fontSize / 9))
            self.alignmentStarsText[i].setText(name)
            self.alignmentStarsText[i].setFont(font)
            self.alignmentStarsText[i].setColor(fontColor)
            self.alignmentStarsText[i].setPos(az, alt)
            self.alignmentStarsText[i].setZValue(30)
        return True

    def drawModelPoints(self):
        """
        :return:
        """
        points = self.app.data.buildP
        if not points:
            return False

        x = [x[1] for x in points]
        y = [x[0] for x in points]
        act = [x[2] for x in points]

        for index, plotItem in enumerate(self.ui.hemisphere.p):
            item = self.ui.hemisphere.findItemByName(plotItem, 'model')
            if not item:
                continue
            if index == 1:
                x, y = self.ui.hemisphere.toPolar(x, y)
            item.setData(x=x, y=y)

            isEdit = self.ui.editModeHem.isChecked()
            for i in range(len(x)):
                active = act[i]
                col = [self.M_WHITE, self.M_GREEN, self.M_RED]
                colActive = col[active]
                color = self.M_PINK if isEdit else colActive
                sym = ['d', 'o', 'x']
                symbol = sym[active]

                spot = item.scatter.points()[i]
                spot.setPen(pg.mkPen(color=color, width=1.5))
                spot.setBrush(pg.mkBrush(color=color + '40'))
                spot.setSymbol(symbol)
        return True

    def drawModelText(self):
        """
        :return:
        """
        plotItem = self.ui.hemisphere.p[0]
        points = self.app.data.buildP
        if not points:
            return False
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
        font = QFont(self.window().font().family(),
                     int(self.window().font().pointSize() * facFont))
        for i in range(len(x)):
            az = x[i]
            alt = y[i]
            active = act[i]
            col = [self.M_WHITE, self.M_GREEN, self.M_RED]
            colActive = col[active]
            color = self.M_PINK if isEdit else colActive

            text = f'{i + 1}'
            textItem = pg.TextItem(anchor=(0.5, 1.1))
            textItem.setText(text)
            textItem.setFont(font)
            textItem.setColor(color)
            textItem.setPos(az, alt)
            textItem.setZValue(40)
            self.modelPointsText.append(textItem)
            plotItem.addItem(textItem)
        return True

    def updateDataModel(self, x, y):
        """
        :return:
        """
        bp = [(y, x, True) for x, y in zip(x, y)]
        self.app.data.buildP = bp
        self.drawModelPoints()
        self.drawModelText()
        self.app.buildPointsChanged.emit()
        return True

    def setupModel(self):
        """
        :return:
        """
        for i, plotItem in enumerate(self.ui.hemisphere.p):
            if self.ui.showSlewPath.isChecked():
                pen = pg.mkPen(color=self.M_GREEN, style=Qt.DashLine)
            else:
                pen = None

            if self.ui.editModeHem.isChecked():
                pd = pg.PlotDataItem(
                    symbolBrush=pg.mkBrush(color=self.M_PINK + '40'),
                    symbolPen=pg.mkPen(color=self.M_PINK1, width=2),
                    symbolSize=10, symbol='o', connect='all', pen=pen)
                pd.nameStr = 'model'
                vb = plotItem.getViewBox()
                vb.setPlotDataItem(pd)
                if i == 0:
                    vb.updateData = self.updateDataModel
            else:
                pd = pg.PlotDataItem(
                    symbolBrush=pg.mkBrush(color=self.M_GREEN + '40'),
                    symbolPen=pg.mkPen(color=self.M_GREEN1, width=2),
                    symbolSize=8, symbol='o', connect='all', pen=pen)
                pd.nameStr = 'model'
                vb = plotItem.getViewBox()
                if i == 0:
                    vb.setPlotDataItem(None)
            pd.setZValue(40)
            plotItem.addItem(pd)

        self.drawModelPoints()
        self.drawModelText()
        return True

    def setupPointerHem(self):
        """
        :return:
        """
        for plotItem in self.ui.hemisphere.p:
            symbol = self.makePointer()
            pd = pg.ScatterPlotItem(symbol=symbol, size=40)
            pd.setData(x=[0], y=[0])
            pd.setPen(pg.mkPen(color=self.M_PINK))
            pd.setBrush(pg.mkBrush(color=self.M_PINK + '20'))
            pd.setZValue(60)
            pd.nameStr = 'pointer'
            plotItem.addItem(pd)
        return True

    def drawPointerHem(self):
        """
        :return:
        """
        items = []
        for plotItem in self.ui.hemisphere.p:
            item = self.ui.hemisphere.findItemByName(plotItem, 'pointer')
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
        """
        :return:
        """
        plotItem = self.ui.hemisphere.p[0]
        self.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
        self.pointerDome.setPen(pg.mkPen(color=self.M_GREY))
        self.pointerDome.setBrush(pg.mkBrush(color=self.M_GREY + '80'))
        self.pointerDome.setVisible(False)
        plotItem.addItem(self.pointerDome)
        return True

    def drawDome(self, azimuth=None):
        """
        :param azimuth:
        :return:
        """
        if not isinstance(azimuth, (int, float)):
            self.pointerDome.setVisible(False)
            return False

        visible = self.app.deviceStat.get('dome', False)
        self.pointerDome.setRect(azimuth - 15, 1, 30, 88)
        self.pointerDome.setVisible(visible)
        return True

    def getMountModelData(self):
        """
        :return:
        """
        model = self.app.mount.model
        if len(model.starList) == 0:
            return None, None, None
        alt = np.array([x.alt.degrees for x in model.starList])
        az = np.array([x.az.degrees for x in model.starList])
        err = np.array([x.errorRMS for x in model.starList])
        return az, alt, err

    def drawModelIsoCurve(self):
        """
        :return:
        """
        az, alt, err = self.getMountModelData()
        if az is None or alt is None or err is None:
            return False

        suc = self.ui.hemisphere.addIsoItemHorizon(az, alt, err)
        return suc

    def drawHemisphereTab(self):
        """
        :return: True for test purpose
        """
        hasModel = bool(self.app.mount.model.numberStars)
        self.ui.alignmentModeHem.setEnabled(hasModel)
        self.ui.showIsoModel.setEnabled(hasModel)
        isMount = bool(self.app.deviceStat['mount'])
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
        return True

    def slewDirect(self, posView):
        """
        :param posView:
        :return:
        """
        azimuth = int(posView.x() + 0.5)
        altitude = int(posView.y() + 0.5)

        question = '<b>Manual slewing to coordinate</b>'
        question += '<br><br>Selected coordinates are:<br>'
        question += f'<font color={self.M_BLUE}> Altitude: {altitude:3.1f}°'
        question += f'   Azimuth: {azimuth:3.1f}°</font>'
        question += '<br><br>Would you like to start slewing?<br>'

        suc = self.messageDialog(self, 'Slewing mount', question)
        if not suc:
            return False

        suc = self.slewTargetAltAz(altitude, azimuth)
        return suc

    def slewStar(self, posView):
        """
        :param posView:
        :return:
        """
        spot = self.alignmentStars.pointsAt(posView)
        if len(spot) == 0:
            return False

        index = spot[0].index()
        hip = self.app.hipparcos
        name = hip.name[index]
        ra, dec = hip.getAlignStarRaDecFromName(hip.name[index])

        question = '<b>Polar / Ortho Alignment procedure</b>'
        question += '<br>Selected alignment star: '
        question += f'<font color={self.M_BLUE}>{name}.</font>'
        question += '<br>Would you like to start alignment?<br>'

        isDAT = self.app.mount.setting.statusDualAxisTracking
        warning = f'<br><i><font color={self.M_YELLOW}>'
        warning += 'Dual Axis Tracking is actually enabled!<br>'
        warning += 'It should be off during alignment process.</font></i>'

        buttons = ['Cancel', 'Ortho Align', 'Polar Align']
        question = question + warning if isDAT else question
        reply = self.messageDialog(self, 'Slewing mount', question, buttons)
        if reply == 0:
            return False
        elif reply == 1:
            alignType = 'ortho'
        else:
            alignType = 'polar'

        t = f'Align [{alignType}] to [{name}]'
        self.msg.emit(1, 'Hemisphere', 'Align', t)
        suc = self.slewTargetRaDec(ra, dec, slewType=alignType, epoch='JNow')
        return suc

    def mouseDoubleClick(self, ev, posView):
        """
        :param ev:
        :param posView:
        :return:
        """
        if self.ui.alignmentModeHem.isChecked():
            self.slewStar(posView)
        elif self.ui.normalModeHem.isChecked():
            self.slewDirect(posView)
        return True
