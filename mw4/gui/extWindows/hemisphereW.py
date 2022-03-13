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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os.path

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QCursor, QFont, QPainterPath
import numpy as np
from PIL import Image
import pyqtgraph as pg

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets import hemisphere_ui
from gui.extWindows.hemisphere.hemisphereWext import HemisphereWindowExt
from gui.extWindows.hemisphere.editHorizon import EditHorizon
from base.transform import diffModulusAbs


class HemisphereWindow(MWidget, HemisphereWindowExt, EditHorizon):
    """
    the hemisphere window class handles all interaction with model points
    show / edit etc. the z orders is aligned as follows:

    on the static plane we have (and set to the z order)
        - horizon               0
        - horizon limits        0
        - meridian limit track  10
        - meridian limit slew   15
        - celestial path        20
        - alignment stars       30
        - build points          40
        - checked build points  50
    """

    __all__ = ['HemisphereWindow']

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.ui = hemisphere_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.mwSuper('__init__')
        self.operationMode = 'normal'
        self.pointerAltAz = None
        self.pointerDome = None
        self.modelPoints = None
        self.modelPointsText = None
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
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)
        self.ui.showSlewPath.setChecked(config.get('showSlewPath', False))
        self.ui.showMountLimits.setChecked(config.get('showMountLimits', False))
        self.ui.showCelestial.setChecked(config.get('showCelestial', False))
        self.ui.showAlignStar.setChecked(config.get('showAlignStar', False))
        self.ui.showHorizon.setChecked(config.get('showHorizon', True))
        self.ui.showPolar.setChecked(config.get('showPolar', False))
        self.ui.showTerrain.setChecked(config.get('showTerrain', False))
        self.ui.terrainAlpha.setValue(config.get('terrainAlpha', 0.35))
        self.ui.azimuthShift.setValue(config.get('azimuthShift', 0))
        self.ui.altitudeShift.setValue(config.get('altitudeShift', 0))
        self.ui.tabWidget.setCurrentIndex(config.get('tabWidget', 0))

        terrainFile = self.app.mwGlob['configDir'] + '/terrain.jpg'
        if not os.path.isfile(terrainFile):
            self.imageTerrain = None
            return False

        img = Image.open(terrainFile).convert('LA')
        (w, h) = img.size
        img = img.crop((0, 0, w, h / 2))
        img = img.resize((1440, 360))
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        self.imageTerrain = Image.new('L', (2880, 480), 128)
        self.imageTerrain.paste(img, (0, 60))
        self.imageTerrain.paste(img, (1440, 60))
        self.mwSuper('initConfig')
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'hemisphereW' not in self.app.config:
            self.app.config['hemisphereW'] = {}

        config = self.app.config['hemisphereW']
        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        config['showSlewPath'] = self.ui.showSlewPath.isChecked()
        config['showMountLimits'] = self.ui.showMountLimits.isChecked()
        config['showCelestial'] = self.ui.showCelestial.isChecked()
        config['showAlignStar'] = self.ui.showAlignStar.isChecked()
        config['showHorizon'] = self.ui.showHorizon.isChecked()
        config['showPolar'] = self.ui.showPolar.isChecked()
        config['showTerrain'] = self.ui.showTerrain.isChecked()
        config['terrainAlpha'] = self.ui.terrainAlpha.value()
        config['azimuthShift'] = self.ui.azimuthShift.value()
        config['altitudeShift'] = self.ui.altitudeShift.value()
        config['tabWidget'] = self.ui.tabWidget.currentIndex()

        self.mwSuper('storeConfig')
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.ui.normalMode.setChecked(True)
        self.setOperationMode()
        self.storeConfig()
        QGuiApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return:
        """
        self.app.update3s.connect(self.drawAlignmentStars)
        self.app.updatePointMarker.connect(self.drawModelPoints)
        self.app.redrawHemisphere.connect(self.drawHemisphere)
        self.app.colorChange.connect(self.colorChange)

        self.app.mount.signals.settingDone.connect(self.updateOnChangedParams)
        self.app.mount.signals.pointDone.connect(self.drawPointerAltAz)
        self.app.dome.signals.azimuth.connect(self.drawDome)
        self.app.dome.signals.deviceDisconnected.connect(self.drawDome)
        self.app.dome.signals.serverDisconnected.connect(self.drawDome)

        self.ui.normalMode.clicked.connect(self.setOperationMode)
        self.ui.editMode.clicked.connect(self.setOperationMode)
        self.ui.alignmentMode.clicked.connect(self.setOperationMode)

        self.ui.azimuthShift.valueChanged.connect(self.drawHemisphere)
        self.ui.altitudeShift.valueChanged.connect(self.drawHemisphere)
        self.ui.terrainAlpha.valueChanged.connect(self.drawHemisphere)
        self.ui.showSlewPath.clicked.connect(self.drawHemisphere)
        self.ui.showHorizon.clicked.connect(self.drawHemisphere)
        self.ui.showAlignStar.clicked.connect(self.drawHemisphere)
        self.ui.showMountLimits.clicked.connect(self.drawHemisphere)
        self.ui.showCelestial.clicked.connect(self.drawHemisphere)
        self.ui.showTerrain.clicked.connect(self.drawHemisphere)

        self.ui.addPositionToHorizon.clicked.connect(self.addHorizonPointManual)
        self.drawHemisphere()
        self.show()
        return True

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.ui.hemisphere.colorChange()
        self.ui.horizon.colorChange()
        self.drawHemisphere()
        self.mwSuper('colorChange')
        return True

    def setOperationMode(self):
        """
        :return: success
        """
        if self.ui.normalMode.isChecked():
            self.operationMode = 'normal'
        elif self.ui.editMode.isChecked():
            self.operationMode = 'edit'
            self.drawModelPoints()
        elif self.ui.alignmentMode.isChecked():
            self.ui.showAlignStar.setChecked(True)
            self.operationMode = 'star'
            self.app.data.clearBuildP()

        self.drawHemisphere()
        return True

    @staticmethod
    def makePointer():
        path = QPainterPath()
        path.moveTo(0, -1)
        path.lineTo(0, 1)
        path.moveTo(-1, 0)
        path.lineTo(1, 0)
        path.addEllipse(-0.1, -0.1, 0.2, 0.2)
        path.addEllipse(-0.3, -0.3, 0.6, 0.6)
        return path

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
        color = cMap[relevance]
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
            self.drawHemisphere()
        return needRedraw

    def prepareHemisphere(self):
        """
        :return:
        """
        plotItem = self.ui.hemisphere.p[0]
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
                           minXRange=360 / 4, minYRange=180 / 4)
        plotItem.setXRange(0, 360)
        plotItem.setYRange(0, 90)
        plotItem.disableAutoRange()
        plotItem.setMouseEnabled(x=False, y=False)
        plotItem.clear()
        self.pointerAltAz = None
        self.pointerDome = None
        self.modelPoints = None
        self.modelPointsText = None
        self.alignmentStars = None
        self.alignmentStarsText = None

    def drawCelestialEquator(self):
        """
        :return:
        """
        celestial = self.app.data.generateCelestialEquator()
        if not celestial:
            return False

        plotItem = self.ui.hemisphere.p[0]
        alt, az = zip(*celestial)
        alt = np.array(alt)
        az = np.array(az)
        pd = pg.ScatterPlotItem()
        pd.setData(
            x=az, y=alt, symbol='o', pen=pg.mkPen(color=self.M_WHITE1),
            brush=pg.mkBrush(color=self.M_WHITE + '80'), size=1)
        pd.setZValue(5)
        plotItem.addItem(pd)
        return True

    def drawHorizon(self):
        """
        :return:
        """
        if not self.app.data.horizonP:
            return False
        self.ui.hemisphere.drawHorizon(self.app.data.horizonP)
        return True

    def drawTerrainMask(self):
        """
        :return:
        """
        if not self.imageTerrain:
            return False

        plotItem = self.ui.hemisphere.p[0]
        shiftAz = self.ui.azimuthShift.value()
        shiftAlt = self.ui.altitudeShift.value()
        alpha = self.ui.terrainAlpha.value()
        imgF = self.imageTerrain.crop((4 * shiftAz, 60 + shiftAlt * 2,
                                       1440 + 4 * shiftAz, 420 + shiftAlt * 2))
        imgF = imgF.resize((360, 90), Image.ANTIALIAS)
        (w, h) = imgF.size
        img = list(imgF.getdata())
        img = np.array(img).reshape((h, w))

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
        mTrack.setZValue(15)
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

    def drawAlignmentStars(self):
        """
        :return: true for test purpose
        """
        if not self.ui.showAlignStar.isChecked():
            return False

        plotItem = self.ui.hemisphere.p[0]
        hip = self.app.hipparcos
        hip.calculateAlignStarPositionsAltAz()

        if self.alignmentStars is None:
            self.alignmentStars = []
            self.alignmentStarsText = []
            for i in range(len(hip.name)):
                pd = pg.ScatterPlotItem(symbol='star', size=6)
                self.alignmentStars.append(pd)
                plotItem.addItem(pd)
                textItem = pg.TextItem(anchor=(0.5, 1.1))
                self.alignmentStarsText.append(textItem)
                plotItem.addItem(textItem)

        for i, val in enumerate(zip(hip.alt, hip.az, hip.name)):
            alt, az, name = val
            color = self.M_YELLOW if self.operationMode == 'star' else self.M_YELLOW1

            size = 10 if self.operationMode == 'star' else 6
            if self.operationMode == 'star':
                rel = self.calculateRelevance(alt=alt, az=az)
                fontColor, fontSize = self.selectFontParam(rel)
            else:
                fontSize = 7
                fontColor = self.M_WHITE1

            self.alignmentStars[i].setData(
                x=hip.az, y=hip.alt,  size=size,
                pen=pg.mkPen(color=color), brush=pg.mkBrush(color=color))
            self.alignmentStars[i].setZValue(30)

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
        plotItem = self.ui.hemisphere.p[0]
        points = self.app.data.buildP
        if not points:
            return False

        if self.modelPoints is None:
            self.modelPoints = []
            self.modelPointsText = []
            for i in range(len(points)):
                pd = pg.ScatterPlotItem(symbol='o', size=10)
                self.modelPoints.append(pd)
                plotItem.addItem(pd)
                textItem = pg.TextItem(anchor=(0.5, 1.1))
                self.modelPointsText.append(textItem)
                plotItem.addItem(textItem)

        for i, point in enumerate(points):
            az = point[1]
            alt = point[0]
            active = point[2]

            colActive = self.M_GREEN if active else self.M_YELLOW
            color = self.M_PINK if self.operationMode == 'edit' else colActive

            self.modelPoints[i].setPen(pg.mkPen(color=color, width=1.5))
            self.modelPoints[i].setBrush(pg.mkBrush(color=color + '40'))
            self.modelPoints[i].setData(x=[az], y=[alt])
            self.modelPoints[i].setZValue(40)

            text = f'{i + 1}'
            self.modelPointsText[i].setText(text)
            self.modelPointsText[i].setColor(color)
            self.modelPointsText[i].setPos(az, alt)
            self.modelPointsText[i].setZValue(40)

    def drawModelSlewPath(self):
        """
        :return:
        """
        points = self.app.data.buildP
        if not points:
            return False

        plotItem = self.ui.hemisphere.p[0]
        for index, point in enumerate(points):
            if self.ui.showSlewPath.isChecked() and index > 0:
                pd = pg.PlotDataItem()
                pd.setData(
                    x=[points[index - 1][1], points[index][1]],
                    y=[points[index - 1][0], points[index][0]],
                    pen=pg.mkPen(color=self.M_WHITE + '80', style=Qt.DashLine))
                pd.setZValue(40)
                plotItem.addItem(pd)
        return True

    def drawPointerAltAz(self):
        """
        :return:
        """
        if not self.pointerAltAz:
            plotItem = self.ui.hemisphere.p[0]
            symbol = self.makePointer()
            self.pointerAltAz = pg.ScatterPlotItem(symbol=symbol, size=40)
            self.pointerAltAz.setData(x=[0], y=[45])
            self.pointerAltAz.setPen(pg.mkPen(color=self.M_PINK1))
            self.pointerAltAz.setBrush(pg.mkBrush(color=self.M_PINK + '20'))
            self.pointerAltAz.setZValue(10)
            plotItem.addItem(self.pointerAltAz)

        obsSite = self.app.mount.obsSite
        if obsSite.Alt is None or obsSite.Az is None:
            self.pointerAltAz.setVisible(False)
            return False
        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerAltAz.setData(x=[az], y=[alt])
        self.pointerAltAz.setVisible(True)
        return True

    def drawDome(self, azimuth=None):
        """
        :param azimuth:
        :return:
        """
        if not self.pointerDome:
            plotItem = self.ui.hemisphere.p[0]
            self.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
            self.pointerDome.setPen(pg.mkPen(color=self.M_GREY))
            self.pointerDome.setBrush(pg.mkBrush(color=self.M_GREY + '80'))
            self.pointerDome.setVisible(False)
            plotItem.addItem(self.pointerDome)

        if not isinstance(azimuth, (int, float)):
            self.pointerDome.setVisible(False)
            return False

        visible = self.app.deviceStat['dome']
        self.pointerDome.setRect(azimuth - 15, 1, 30, 88)
        self.pointerDome.setVisible(visible)
        return True

    def drawHemisphere(self):
        """
        :return: True for test purpose
        """
        self.prepareHemisphere()
        if self.ui.showCelestial.isChecked():
            self.drawCelestialEquator()
        if self.ui.showHorizon.isChecked():
            self.drawHorizon()
        if self.ui.showTerrain.isChecked():
            self.drawTerrainMask()
        if self.ui.showMountLimits.isChecked():
            self.drawMeridianLimits()
            self.drawHorizonLimits()
        self.drawAlignmentStars()
        self.drawModelPoints()
        self.drawModelSlewPath()
        self.drawPointerAltAz()
        self.drawDome()
        return True
