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

# external packages
import os.path

import PyQt5
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QGuiApplication, QCursor, QFont
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
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
    there are two planes static / moving where the moving is behind the static
    one. the static on has to be transparent.

    on the static plane we have (and set to the z order)
        - horizon               0
        - horizon limits        0
        - meridian limit track  10
        - meridian limit slew   15
        - celestial path        20
        - alignment stars       30
        - build points          40
        - checked build points  50

    on the moving plane we have (and set to the z order)
        - dome                  0
        - pointing marker       10

    """

    __all__ = ['HemisphereWindow',
               ]

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.ui = hemisphere_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.mwSuper('__init__')
        self.mutexDraw = PyQt5.QtCore.QMutex()
        self.operationMode = 'normal'
        self.MODE = None
        self.setModeColors()
        self.pointerAltAz = None
        self.pointerDome = None
        self.pointsBuild = None
        self.starsAlign = None
        self.starsAlignAnnotate = None
        self.meridianSlew = None
        self.meridianTrack = None
        self.horizonLimitHigh = None
        self.horizonLimitLow = None
        self.celestialPath = None
        self.celestialPolarPath = None
        self.meridianSlewParam = None
        self.meridianTrackParam = None
        self.horizonLimitHighParam = None
        self.horizonLimitLowParam = None
        self.pointerPolarAltAz = None
        self.pointsBuildAnnotate = None
        self.pointsPolarBuild = None
        self.pointsPolarBuildAnnotate = None
        self.imageTerrain = None
        self.closingWindow = False
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
        self.ui.checkEditNone.setChecked(True)
        self.setOperationMode()
        self.storeConfig()
        self.closingWindow = True
        QGuiApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return:
        """
        self.app.update10s.connect(self.updateAlignStar)
        self.app.redrawHemisphere.connect(self.drawHemisphere)
        self.app.updatePointMarker.connect(self.updatePointMarker)
        self.app.updatePointMarker.connect(self.updatePolarPointMarker)
        self.app.mount.signals.settingDone.connect(self.updateOnChangedParams)
        self.app.mount.signals.pointDone.connect(self.updatePointerAltAz)
        self.app.mount.signals.pointDone.connect(self.updatePointerPolarAltAz)
        self.app.dome.signals.azimuth.connect(self.updateDome)
        self.app.dome.signals.deviceDisconnected.connect(self.updateDome)
        self.app.dome.signals.serverDisconnected.connect(self.updateDome)
        self.app.enableEditPoints.connect(self.enableEditPoints)
        self.ui.showSlewPath.clicked.connect(self.drawHemisphere)
        self.ui.showHorizon.clicked.connect(self.drawHemisphere)
        self.ui.showAlignStar.clicked.connect(self.drawHemisphere)
        self.ui.showMountLimits.clicked.connect(self.drawHemisphere)
        self.ui.showCelestial.clicked.connect(self.drawHemisphere)
        self.ui.showTerrain.clicked.connect(self.drawHemisphere)
        self.ui.checkEditNone.clicked.connect(self.setOperationMode)
        self.ui.checkEditBuildPoints.clicked.connect(self.setOperationMode)
        self.ui.checkPolarAlignment.clicked.connect(self.setOperationMode)
        self.ui.azimuthShift.valueChanged.connect(self.drawHemisphere)
        self.ui.altitudeShift.valueChanged.connect(self.drawHemisphere)
        self.ui.terrainAlpha.valueChanged.connect(self.drawHemisphere)
        self.app.colorChange.connect(self.colorChange)

        self.ui.showPolar.clicked.connect(self.togglePolar)
        self.ui.addPositionToHorizon.clicked.connect(self.addHorizonPointManual)
        self.togglePolar()
        self.show()
        return True

    def setModeColors(self):
        """
        :return:
        """
        self.MODE = dict(
            normal=dict(horMarker='None',
                        horColor=self.M_BLUE,
                        buildPColor=self.M_GREEN,
                        starSize=6,
                        starColor=self.M_YELLOW1,
                        starAnnColor=self.M_WHITE1),

            build=dict(horMarker='None',
                       horColor=self.M_BLUE,
                       buildPColor=self.M_PINK,
                       starSize=6,
                       starColor=self.M_YELLOW1,
                       starAnnColor=self.M_WHITE1),

            horizon=dict(horMarker='o',
                         horColor=self.M_PINK,
                         buildPColor=self.M_GREEN1,
                         starSize=6,
                         starColor=self.M_YELLOW1,
                         starAnnColor=self.M_WHITE1),

            star=dict(horMarker='None',
                      horColor=self.M_BLUE1,
                      buildPColor=self.M_GREEN1,
                      starSize=12,
                      starColor=self.M_YELLOW,
                      starAnnColor=self.M_WHITE)
        )
        return True

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.setModeColors()
        self.ui.hemisphere.colorChange()
        self.drawHemisphere()
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
        color = cMap[relevance]
        size = 8 + int(relevance * 5)
        return color, size

    def togglePolar(self):
        """
        :return: success
        """
        return
        if self.ui.showPolar.isChecked():
            self.ui.polar.setVisible(True)

        else:
            self.ui.polar.setVisible(False)

        self.drawHemisphere()
        return True

    def updateOnChangedParams(self, sett):
        """
        :param sett:
        :return: status redraw
        """
        needRedraw = False
        if self.meridianSlewParam != sett.meridianLimitSlew:
            self.meridianSlewParam = sett.meridianLimitSlew
            needRedraw = True

        if self.meridianTrackParam != sett.meridianLimitTrack:
            self.meridianTrackParam = sett.meridianLimitTrack
            needRedraw = True

        if self.horizonLimitHighParam != sett.horizonLimitHigh:
            self.horizonLimitHighParam = sett.horizonLimitHigh
            needRedraw = True

        if self.horizonLimitLowParam != sett.horizonLimitLow:
            self.horizonLimitLowParam = sett.horizonLimitLow
            needRedraw = True

        if needRedraw:
            self.drawHemisphere()

        return needRedraw

    def updatePointerAltAz(self):
        """
        :return: success
        """
        return
        if self.pointerAltAz is None:
            return False

        obsSite = self.app.mount.obsSite
        if obsSite.Alt is None or obsSite.Az is None:
            self.pointerAltAz.set_visible(False)
            return False
        else:
            self.pointerAltAz.set_visible(True)

        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerAltAz.set_data((az, alt))
        return True

    def updatePointerPolarAltAz(self):
        """
        :return: success
        """
        return
        if self.pointerPolarAltAz is None:
            return False

        obsSite = self.app.mount.obsSite
        if obsSite.Alt is None or obsSite.Az is None:
            self.pointerPolarAltAz.set_visible(False)
            return False
        else:
            self.pointerPolarAltAz.set_visible(True)

        alt = 90 - obsSite.Alt.degrees
        az = obsSite.Az.radians
        self.pointerPolarAltAz.set_data((az, alt))
        return True

    def updateDome(self, azimuth):
        """
        updateDome is called whenever an update of coordinates from dome are
        given. it takes the actual values and corrects the point in window if
        window is in show status.

        :param azimuth:
        :return: success
        """
        return
        if self.pointerDome is None:
            return False
        if not isinstance(azimuth, (int, float)):
            self.pointerDome.set_visible(False)
            return False

        visible = self.app.deviceStat['dome']
        self.pointerDome.set_xy((azimuth - 15, 1))
        self.pointerDome.set_visible(visible)
        return True

    def getMarkerStatusParams(self, active, index):
        """
        :param active:
        :param index:
        :return: values
        """
        if active:
            marker = self.markerPoint()
            color = self.MODE[self.operationMode]['buildPColor']
            mSize = 9
            annotationText = f'{index + 1:2d}'
        else:
            marker = '$\u2714$'
            color = self.M_YELLOW
            mSize = 11
            annotationText = f'{index + 1:2d}'

        return marker, mSize, color, annotationText

    def updatePointMarker(self):
        """
        :return: success
        """
        return
        for index, point in enumerate(self.app.data.buildP):
            active = point[2]
            marker, mSize, color, _ = self.getMarkerStatusParams(active, index)
            self.pointsBuild[index].set_marker(marker)
            self.pointsBuild[index].set_markersize(mSize)
            self.pointsBuild[index].set_color(color)
            self.pointsBuildAnnotate[index].set_color(color)

        self.hemisphereMat.figure.canvas.draw()
        return True

    def updatePolarPointMarker(self):
        """
        :return: success
        """
        return
        if not self.pointsPolarBuild:
            return False

        for index, point in enumerate(self.app.data.buildP):
            active = point[2]
            marker, mSize, color, _ = self.getMarkerStatusParams(active, index)
            self.pointsPolarBuild[index].set_marker(marker)
            self.pointsPolarBuild[index].set_markersize(mSize)
            self.pointsPolarBuild[index].set_color(color)
            self.pointsPolarBuildAnnotate[index].set_color(color)

        self.polarMat.figure.canvas.draw()
        return True

    def updateAlignStar(self):
        """
        updateAlignStar is called whenever an update of coordinates from mount
        are given. it takes the actual values and corrects the point in window if
        window is in show status. If the object is not created, the routing
        returns false. Due to the fact that all annotation are only shown if in
        axes when coordinate are in data, after some time, no annotation will be
        shown, because just moved. Therefore we add each time the annotation again.

        :return: success
        """
        return
        if self.starsAlign is None:
            return False
        if self.starsAlignAnnotate is None:
            return False
        if not self.mutexDraw.tryLock():
            return False

        axes = self.hemisphereMat.figure.axes[0]
        hip = self.app.hipparcos
        hip.calculateAlignStarPositionsAltAz()
        self.starsAlign.set_data(hip.az, hip.alt)

        for i, starAnnotation in enumerate(self.starsAlignAnnotate):
            starAnnotation.remove()
        self.starsAlignAnnotate = list()

        for alt, az, name in zip(hip.alt, hip.az, hip.name):
            if self.operationMode == 'star':
                rel = self.calculateRelevance(alt=alt, az=az)
                fontColor, fontSize = self.selectFontParam(rel)
            else:
                fontSize = 12
                fontColor = self.M_WHITE1
            annotation = axes.annotate(name,
                                       xy=(az, alt),
                                       xytext=(2, 2),
                                       textcoords='offset points',
                                       xycoords='data',
                                       color=fontColor,
                                       fontsize=fontSize,
                                       zorder=30,
                                       clip_on=True,
                                       )
            self.starsAlignAnnotate.append(annotation)

        self.hemisphereMat.figure.canvas.draw()
        self.mutexDraw.unlock()
        return True

    def clearHemisphere(self):
        """
        clearHemisphere is called when after startup the location of the mount
        is changed to reconstruct correctly the hemisphere window

        :return: True for test Purpose
        """
        self.pointsBuild = None
        self.app.data.clearBuildP()
        self.drawHemisphere()
        return True

    def staticModelData(self, axes=None, polar=False):
        """
        :param axes:
        :param polar:
        :return:
        """
        points = self.app.data.buildP
        if not points:
            return False

        if polar:
            self.pointsPolarBuild = list()
            self.pointsPolarBuildAnnotate = list()
        else:
            self.pointsBuild = list()
            self.pointsBuildAnnotate = list()

        for index, point in enumerate(points):
            az = point[1]
            alt = point[0]
            active = point[2]

            marker, mSize, color, text = self.getMarkerStatusParams(active, index)

            if self.ui.checkShowSlewPath.isChecked() and index > 0:
                if polar:
                    axes.plot(np.radians((points[index - 1][1], points[index][1])),
                              (90 - points[index - 1][0], 90 - points[index][0]),
                              ls=':', lw=1, color=self.M_WHITE, zorder=40)
                else:
                    axes.plot((points[index - 1][1], points[index][1]),
                              (points[index - 1][0], points[index][0]),
                              ls=':', lw=1, color=self.M_WHITE, zorder=40)

            if polar:
                p, = axes.plot(np.radians(az), 90 - alt,
                               marker=marker,
                               markersize=mSize,
                               fillstyle='none',
                               color=self.MODE['normal']['buildPColor'],
                               zorder=40,
                               )
                self.pointsPolarBuild.append(p)
            else:
                p, = axes.plot(az, alt,
                               marker=marker,
                               markersize=mSize,
                               fillstyle='none',
                               color=self.MODE[self.operationMode]['buildPColor'],
                               zorder=40,
                               )
                self.pointsBuild.append(p)

            if polar:
                annotation = axes.annotate(text,
                                           xy=(np.radians(az), 90 - alt),
                                           xytext=(2, -10),
                                           textcoords='offset points',
                                           color=color,
                                           zorder=40,
                                           )
                self.pointsPolarBuildAnnotate.append(annotation)
            else:
                annotation = axes.annotate(text,
                                           xy=(az, alt),
                                           xytext=(2, -10),
                                           textcoords='offset points',
                                           color=color,
                                           zorder=40,
                                           )
                self.pointsBuildAnnotate.append(annotation)

        return True

    def drawHemisphereMoving(self, axes=None, polar=False):
        """
        drawHemisphereMoving is rendering the moving part which consists of:
            - pointer: where the mount points to
            - dome widget: which shows the position of the dome opening
        the dynamic ones are located on a separate plane to improve rendering
        speed, because we update this part very often.

        :param axes: matplotlib axes object
        :param polar: flag if polar should be drawn
        :return:
        """
        if polar:
            self.pointerPolarAltAz, = axes.plot(np.radians(180), 45,
                                                zorder=10,
                                                color=self.M_PINK,
                                                marker=self.markerAltAz(),
                                                markersize=25,
                                                linestyle='none',
                                                fillstyle='none',
                                                clip_on=False,
                                                visible=False,
                                                )
        else:
            self.pointerAltAz, = axes.plot(180, 45,
                                           zorder=10,
                                           color=self.M_PINK,
                                           marker=self.markerAltAz(),
                                           markersize=25,
                                           linestyle='none',
                                           fillstyle='none',
                                           clip_on=False,
                                           visible=False,
                                           )
            self.pointerDome = mpatches.Rectangle((165, 1),
                                                  30,
                                                  88,
                                                  zorder=0,
                                                  color=self.M_GREY,
                                                  lw=3,
                                                  clip_on=True,
                                                  fill=True,
                                                  visible=False)
            axes.add_patch(self.pointerDome)
        return True

    def prepareHemisphere(self):
        """
        :return:
        """
        plotItem = self.ui.hemisphere.p[0]
        plotItem.showAxes(True, showValues=True)
        plotItem.getViewBox().setMouseMode(pg.ViewBox().RectMode)
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
        plotItem.setMouseEnabled(x=True, y=True)
        plotItem.clear()

    def staticCelestialEquator(self):
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
        self.celestialPath = pg.ScatterPlotItem()
        self.celestialPath.setData(
            x=az, y=alt, symbol='o', pen=pg.mkPen(color=self.M_WHITE1), size=1)
        plotItem.addItem(self.celestialPath)
        return True

    def staticHorizon(self):
        """
        :return:
        """
        if not self.app.data.horizonP:
            return False

        self.ui.hemisphere.staticHorizon(self.app.data.horizonP)
        return True

    def staticTerrainMask(self):
        """
        :return:
        """
        if not self.imageTerrain:
            return False

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
        self.ui.hemisphere.p[0].addItem(imgItem)
        return True

    def staticMeridianLimits(self):
        """

        :return:
        """
        slew = self.app.mount.setting.meridianLimitSlew
        track = self.app.mount.setting.meridianLimitTrack
        if slew is None or track is None:
            return False

        mSlew = pg.QtWidgets.QGraphicsRectItem(180 - slew, 0, 2 * slew, 90)
        mSlew.setPen(pg.mkPen(color=self.M_YELLOW + '80'))
        mSlew.setBrush(pg.mkBrush(color=self.M_YELLOW + '80'))
        mSlew.setZValue(-15)
        self.ui.hemisphere.p[0].addItem(mSlew)

        mTrack = pg.QtWidgets.QGraphicsRectItem(180 - track, 0, 2 * track, 90)
        mTrack.setPen(pg.mkPen(color=self.M_YELLOW1 + '80'))
        mTrack.setBrush(pg.mkBrush(color=self.M_YELLOW1 + '80'))
        mTrack.setZValue(-15)
        self.ui.hemisphere.p[0].addItem(mTrack)
        return True

    def staticHorizonLimits(self):
        """
        :return:
        """
        if self.app.mount.setting.horizonLimitHigh is not None:
            high = self.app.mount.setting.horizonLimitHigh
        else:
            high = 90

        if self.app.mount.setting.horizonLimitLow is not None:
            low = self.app.mount.setting.horizonLimitLow
        else:
            low = 0

        hLow = pg.QtWidgets.QGraphicsRectItem(0, high, 360, 90 - high)
        hLow.setPen(pg.mkPen(color=self.M_RED + '80'))
        hLow.setBrush(pg.mkBrush(color=self.M_RED + '80'))
        hLow.setZValue(-20)
        self.ui.hemisphere.p[0].addItem(hLow)

        hHigh = pg.QtWidgets.QGraphicsRectItem(0, 0, 360, low)
        hHigh.setPen(pg.mkPen(color=self.M_RED + '80'))
        hHigh.setBrush(pg.mkBrush(color=self.M_RED + '80'))
        hHigh.setZValue(-20)
        self.ui.hemisphere.p[0].addItem(hHigh)
        return True

    def drawAlignmentStars(self):
        """
        :return: true for test purpose
        """
        self.starsAlignAnnotate = list()
        hip = self.app.hipparcos
        hip.calculateAlignStarPositionsAltAz()

        self.starsAlign = pg.ScatterPlotItem()
        self.starsAlign.setData(
            x=hip.az, y=hip.alt, symbol='star',
            size=self.MODE[self.operationMode]['starSize'],
            pen=pg.mkPen(color=self.MODE[self.operationMode]['starColor']),
            brush=pg.mkBrush(color=self.MODE[self.operationMode]['starColor']))
        self.starsAlign.setZValue(30)
        self.ui.hemisphere.p[0].addItem(self.starsAlign)

        for alt, az, name in zip(hip.alt, hip.az, hip.name):
            if self.operationMode == 'star':
                rel = self.calculateRelevance(alt=alt, az=az)
                fontColor, fontSize = self.selectFontParam(rel)
            else:
                fontSize = 7
                fontColor = self.M_WHITE1

            textItem = pg.TextItem(text=name, color=fontColor, anchor=(0.5, 1.1))
            font = QFont(self.window().font().family(),
                         int(self.window().font().pointSize() * fontSize / 8))
            textItem.setFont(font)
            textItem.setPos(az, alt)
            textItem.setZValue(30)
            self.ui.hemisphere.p[0].addItem(textItem)
        return True

    def drawHemisphere(self):
        """
        :return: True for test purpose
        """
        if self.closingWindow:
            return False

        self.prepareHemisphere()
        if self.ui.showCelestial.isChecked():
            self.staticCelestialEquator()
        if self.ui.showHorizon.isChecked():
            self.staticHorizon()
        if self.ui.showTerrain.isChecked():
            self.staticTerrainMask()
        if self.ui.showAlignStar.isChecked():
            self.drawAlignmentStars()
        if self.ui.showMountLimits.isChecked():
            self.staticMeridianLimits()
            self.staticHorizonLimits()

        return True
