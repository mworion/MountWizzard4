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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import os.path

import PyQt5
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QGuiApplication, QCursor
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from PIL import Image

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import hemisphere_ui
from gui.extWindows.hemisphereWext import HemisphereWindowExt


class HemisphereWindow(toolsQtWidget.MWidget, HemisphereWindowExt):
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
        self.mutexDraw = PyQt5.QtCore.QMutex()
        self.operationMode = 'normal'
        self.statusDAT = None

        self.MODE = dict(
            normal=dict(horMarker='None',
                        horColor=self.M_BLUE,
                        buildPColor=self.M_GREEN_H,
                        starSize=6,
                        starColor=self.M_YELLOW_L,
                        starAnnColor=self.M_WHITE_L),

            build=dict(horMarker='None',
                       horColor=self.M_BLUE,
                       buildPColor=self.M_PINK_H,
                       starSize=6,
                       starColor=self.M_YELLOW_L,
                       starAnnColor=self.M_WHITE_L),

            horizon=dict(horMarker='o',
                         horColor=self.M_PINK_H,
                         buildPColor=self.M_GREEN_L,
                         starSize=6,
                         starColor=self.M_YELLOW_L,
                         starAnnColor=self.M_WHITE_L),

            star=dict(horMarker='None',
                      horColor=self.M_BLUE1,
                      buildPColor=self.M_GREEN_L,
                      starSize=12,
                      starColor=self.M_YELLOW_H,
                      starAnnColor=self.M_WHITE_H)
        )

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

        self.ui.hemisphereMove.stackUnder(self.ui.hemisphere)
        self.hemisphereMat = self.embedMatplot(self.ui.hemisphere)
        self.hemisphereMatMove = self.embedMatplot(self.ui.hemisphereMove)

        self.ui.polar.stackUnder(self.ui.polarMove)
        self.polarMat = self.embedMatplot(self.ui.polar)
        self.polarMatMove = self.embedMatplot(self.ui.polarMove)

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
        self.ui.checkShowSlewPath.setChecked(config.get('checkShowSlewPath', False))
        self.ui.checkShowMeridian.setChecked(config.get('checkShowMeridian', False))
        self.ui.checkShowCelestial.setChecked(config.get('checkShowCelestial', False))
        self.ui.checkShowAlignStar.setChecked(config.get('checkShowAlignStar', False))
        self.ui.checkUseHorizon.setChecked(config.get('checkUseHorizon', True))
        self.ui.showPolar.setChecked(config.get('showPolar', False))
        self.ui.checkUseTerrain.setChecked(config.get('useTerrain', False))
        self.ui.terrainAlpha.setValue(config.get('terrainAlpha', 0.35))
        self.ui.azimuthShift.setValue(config.get('azimuthShift', 0))

        terrainFile = self.app.mwGlob['configDir'] + '/terrain.jpg'
        if not os.path.isfile(terrainFile):
            self.imageTerrain = None
            return False

        img = Image.open(terrainFile).convert('LA')
        (w, h) = img.size
        img = img.crop((0, 0, w, h / 2))
        img = img.resize((1440, 360))
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        self.imageTerrain = Image.new('L', (2880, 360))
        self.imageTerrain.paste(img)
        self.imageTerrain.paste(img, (1440, 0))

        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'hemisphereW' not in self.app.config:
            self.app.config['hemisphereW'] = {}

        config = self.app.config['hemisphereW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['checkShowSlewPath'] = self.ui.checkShowSlewPath.isChecked()
        config['checkShowMeridian'] = self.ui.checkShowMeridian.isChecked()
        config['checkShowCelestial'] = self.ui.checkShowCelestial.isChecked()
        config['checkShowAlignStar'] = self.ui.checkShowAlignStar.isChecked()
        config['checkUseHorizon'] = self.ui.checkUseHorizon.isChecked()
        config['showPolar'] = self.ui.showPolar.isChecked()
        config['useTerrain'] = self.ui.checkUseTerrain.isChecked()
        config['terrainAlpha'] = self.ui.terrainAlpha.value()
        config['azimuthShift'] = self.ui.azimuthShift.value()
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
        self.app.update10s.disconnect(self.updateAlignStar)
        self.app.update1s.disconnect(self.hemisphereMatMove.figure.canvas.draw)
        self.app.update1s.disconnect(self.polarMatMove.figure.canvas.draw)
        self.app.redrawHemisphere.disconnect(self.drawHemisphere)
        self.app.updatePointMarker.disconnect(self.updatePointMarker)
        self.app.updatePointMarker.disconnect(self.updatePolarPointMarker)
        self.app.mount.signals.settingDone.disconnect(self.updateOnChangedParams)
        self.app.enableEditPoints.disconnect(self.enableEditPoints)
        self.ui.checkShowSlewPath.clicked.disconnect(self.drawHemisphere)
        self.ui.checkShowMeridian.clicked.disconnect(self.drawHemisphere)
        self.ui.checkShowCelestial.clicked.disconnect(self.drawHemisphere)
        self.ui.checkUseHorizon.clicked.disconnect(self.drawHemisphere)
        self.ui.checkEditNone.clicked.disconnect(self.setOperationMode)
        self.ui.checkEditHorizonMask.clicked.disconnect(self.setOperationMode)
        self.ui.checkEditBuildPoints.clicked.disconnect(self.setOperationMode)
        self.ui.checkPolarAlignment.clicked.disconnect(self.setOperationMode)
        self.ui.checkShowAlignStar.clicked.disconnect(self.drawHemisphere)
        self.ui.checkUseTerrain.clicked.disconnect(self.drawHemisphere)
        self.ui.azimuthShift.valueChanged.disconnect(self.drawHemisphere)
        self.ui.terrainAlpha.valueChanged.disconnect(self.drawHemisphere)

        self.ui.showPolar.clicked.disconnect(self.togglePolar)
        self.app.mount.signals.pointDone.disconnect(self.updatePointerAltAz)
        self.app.mount.signals.pointDone.disconnect(self.updatePointerPolarAltAz)
        self.app.dome.signals.azimuth.disconnect(self.updateDome)
        self.app.dome.signals.deviceDisconnected.disconnect(self.updateDome)
        self.app.dome.signals.serverDisconnected.disconnect(self.updateDome)

        plt.close(self.hemisphereMat.figure)
        plt.close(self.polarMat.figure)
        plt.close(self.hemisphereMatMove.figure)
        plt.close(self.polarMatMove.figure)
        QGuiApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))

        super().closeEvent(closeEvent)

    def resizeEvent(self, event):
        """
        :param event:
        :return:
        """

        geometry = self.ui.hemisphere.geometry()
        newGeometry = QRect(0, 0, geometry.width(), geometry.height())
        self.ui.hemisphereMove.setGeometry(newGeometry)

        if self.ui.showPolar.isChecked():
            geometry = self.ui.polar.geometry()
            newGeometry = QRect(0, 0, geometry.width(), geometry.height())
            self.ui.polarMove.setGeometry(newGeometry)

        super().resizeEvent(event)

    def showWindow(self):
        """
        :return:
        """
        self.app.update10s.connect(self.updateAlignStar)
        self.app.update1s.connect(self.hemisphereMatMove.figure.canvas.draw)
        self.app.update1s.connect(self.polarMatMove.figure.canvas.draw)
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
        self.ui.checkShowSlewPath.clicked.connect(self.drawHemisphere)
        self.ui.checkUseHorizon.clicked.connect(self.drawHemisphere)
        self.ui.checkShowAlignStar.clicked.connect(self.drawHemisphere)
        self.ui.checkShowMeridian.clicked.connect(self.drawHemisphere)
        self.ui.checkShowCelestial.clicked.connect(self.drawHemisphere)
        self.ui.checkEditNone.clicked.connect(self.setOperationMode)
        self.ui.checkEditHorizonMask.clicked.connect(self.setOperationMode)
        self.ui.checkEditBuildPoints.clicked.connect(self.setOperationMode)
        self.ui.checkPolarAlignment.clicked.connect(self.setOperationMode)
        self.ui.checkUseTerrain.clicked.connect(self.drawHemisphere)
        self.ui.azimuthShift.valueChanged.connect(self.drawHemisphere)
        self.ui.terrainAlpha.valueChanged.connect(self.drawHemisphere)

        self.ui.showPolar.clicked.connect(self.togglePolar)
        self.ui.addPositionToHorizon.clicked.connect(self.addHorizonPointManual)
        hem = self.hemisphereMat.figure.canvas
        self.hemMouse = hem.mpl_connect('button_press_event', self.onMouseDispatcher)
        hem.mpl_connect('motion_notify_event', self.showMouseCoordinates)
        self.togglePolar()
        self.show()
        return True

    def togglePolar(self):
        """
        :return: success
        """
        if self.ui.showPolar.isChecked():
            self.ui.polar.setMaximumSize(16777215, 16777215)
            self.ui.polar.setVisible(True)

        else:
            self.ui.polar.setFixedWidth(1)
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
            annotation = axes.annotate(name,
                                       xy=(az, alt),
                                       xytext=(2, 2),
                                       textcoords='offset points',
                                       xycoords='data',
                                       color=self.M_WHITE_L,
                                       fontsize=12,
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

    def staticHorizon(self, axes=None, polar=False):
        """
        :param axes:
        :param polar:
        :return:
        """
        if not self.app.data.horizonP:
            return False

        alt, az = zip(*self.app.data.horizonP)

        if polar:
            az = np.radians(az)
            alt = np.array(alt)
            azF = np.radians(range(0, 361, 5))
            altF = np.interp(azF, az, alt)

            axes.fill(azF,
                      90 - altF,
                      color=self.M_TRANS,
                      alpha=0.5,
                      zorder=0)

            axes.plot(az,
                      90 - alt,
                      color=self.MODE[self.operationMode]['horColor'],
                      marker=self.MODE['normal']['horMarker'],
                      alpha=0.5,
                      zorder=0,
                      ls='none')

            axes.plot(azF,
                      90 - altF,
                      color=self.MODE[self.operationMode]['horColor'],
                      marker='',
                      alpha=0.7,
                      zorder=0,
                      lw=2)

        else:
            alt = np.array(alt)
            az = np.array(az)
            altF = np.concatenate([[0], [alt[0]], alt, [alt[-1]], [0]])
            azF = np.concatenate([[0], [0], az, [360], [360]])
            axes.fill(azF,
                      altF,
                      color=self.M_GREY_LL,
                      alpha=0.5,
                      zorder=0)

            axes.plot(az,
                      alt,
                      color=self.MODE[self.operationMode]['horColor'],
                      marker=self.MODE[self.operationMode]['horMarker'],
                      alpha=0.5,
                      zorder=0,
                      ls='none')

            axes.plot(az,
                      alt,
                      color=self.MODE[self.operationMode]['horColor'],
                      marker='',
                      alpha=0.7,
                      zorder=0,
                      lw=2)

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

    def staticCelestialEquator(self, axes=None, polar=False):
        """
        :param axes:
        :param polar:
        :return:
        """
        celestial = self.app.data.generateCelestialEquator()
        if not celestial:
            return False

        alt, az = zip(*celestial)
        alt = np.array(alt)
        az = np.array(az)

        if polar:
            self.celestialPath, = axes.plot(np.radians(-az),
                                            90 - alt,
                                            '.',
                                            markersize=1,
                                            fillstyle='none',
                                            zorder=20,
                                            color=self.M_WHITE_L)
        else:
            self.celestialPath, = axes.plot(az,
                                            alt,
                                            '.',
                                            markersize=1,
                                            fillstyle='none',
                                            zorder=20,
                                            color=self.M_WHITE_L)
        return True

    def staticMeridianLimits(self, axes=None):
        """
        :param axes:
        :return:
        """
        slew = self.app.mount.setting.meridianLimitSlew
        track = self.app.mount.setting.meridianLimitTrack

        if slew is None or track is None:
            return False

        self.meridianSlew = mpatches.Rectangle((180 - slew, 0),
                                               2 * slew,
                                               90,
                                               zorder=15,
                                               color=self.M_YELLOW,
                                               alpha=0.5)
        axes.add_patch(self.meridianSlew)

        self.meridianTrack = mpatches.Rectangle((180 - track, 0),
                                                2 * track,
                                                90,
                                                zorder=10,
                                                color=self.M_YELLOW_L,
                                                alpha=0.5)
        axes.add_patch(self.meridianTrack)
        return True

    def staticHorizonLimits(self, axes=None, polar=False):
        """
        :param axes:
        :param polar:
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

        self.horizonLimitHigh = mpatches.Rectangle((0, high),
                                                   360,
                                                   90 - high,
                                                   zorder=0,
                                                   color=self.M_RED,
                                                   alpha=0.5,
                                                   visible=True)

        self.horizonLimitLow = mpatches.Rectangle((0, 0),
                                                  360,
                                                  low,
                                                  zorder=0,
                                                  color=self.M_RED,
                                                  alpha=0.5,
                                                  visible=True)
        axes.add_patch(self.horizonLimitHigh)
        axes.add_patch(self.horizonLimitLow)
        return True

    def staticTerrainMask(self, axes=None, polar=False):
        """
        :param axes:
        :param polar:
        :return:
        """
        if not self.imageTerrain:
            return False

        shift = self.ui.azimuthShift.value()
        alpha = self.ui.terrainAlpha.value()
        imgF = self.imageTerrain.crop((4 * shift, 0, 1440 + 4 * shift, 360))
        (w, h) = imgF.size
        img = list(imgF.getdata())
        img = np.array(img).reshape((h, w))

        if polar:
            phi = np.linspace(0, 2 * np.pi, img.shape[1] + 1)
            r = np.linspace(0, 90, img.shape[0] + 1)

            Phi, R = np.meshgrid(phi, r)
            axes.pcolormesh(Phi, 90 - R, img[:, :], linewidth=0, linestyle='None',
                            zorder=-10, cmap='gray', alpha=alpha * 0.1)

        else:
            axes.imshow(img, aspect='auto', extent=(0, 360, 90, 0),
                        zorder=-10, cmap='gray', alpha=alpha)
        return True

    def drawHemisphereStatic(self, axes=None, polar=False):
        """
         drawHemisphereStatic renders the static part of the hemisphere window
         and puts all drawing on the static plane. the content consist of:
            - modeldata points
            - horizon mask
            - celestial paths
            - meridian limits
        with all their styles an coloring

        :param axes: matplotlib axes object
        :param polar: flag if polar should be drawn
        :return: success
        """
        if polar:
            if self.ui.checkShowCelestial.isChecked():
                self.staticCelestialEquator(axes=axes, polar=polar)

            if self.ui.checkUseHorizon.isChecked():
                self.staticHorizon(axes=axes, polar=polar)

            self.staticModelData(axes=axes, polar=polar)

            if self.ui.checkUseTerrain.isChecked():
                self.staticTerrainMask(axes=axes, polar=polar)

        else:
            if self.ui.checkUseHorizon.isChecked():
                self.staticHorizon(axes=axes)
                self.staticHorizonLimits(axes=axes)

            if self.ui.checkShowCelestial.isChecked():
                self.staticCelestialEquator(axes=axes)

            if self.ui.checkShowMeridian.isChecked():
                self.staticMeridianLimits(axes=axes)

            self.staticModelData(axes=axes, polar=polar)

            if self.ui.checkUseTerrain.isChecked():
                self.staticTerrainMask(axes=axes)

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
                                                color=self.M_PINK_H,
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
                                           color=self.M_PINK_H,
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
                                                  color=self.M_GREY_MID,
                                                  lw=3,
                                                  clip_on=True,
                                                  fill=True,
                                                  visible=False)
            axes.add_patch(self.pointerDome)
        return True

    def drawAlignmentStars(self, axes=None):
        """
        drawAlignmentStars is rendering the alignment star map. this moves over
        time with the speed of earth turning. so we have to update the rendering,
        but on low speed without having any user interaction.

        :param axes: matplotlib axes object
        :return: true for test purpose
        """
        if not self.mutexDraw.tryLock():
            return False

        self.starsAlignAnnotate = list()
        hip = self.app.hipparcos
        hip.calculateAlignStarPositionsAltAz()

        self.starsAlign, = axes.plot(hip.az,
                                     hip.alt,
                                     marker=self.markerStar(),
                                     markersize=7,
                                     linestyle='None',
                                     color=self.MODE[self.operationMode]['starColor'],
                                     zorder=30,
                                     )

        for alt, az, name in zip(hip.alt, hip.az, hip.name):
            annotation = axes.annotate(name,
                                       xy=(az, alt),
                                       xytext=(2, 2),
                                       textcoords='offset points',
                                       xycoords='data',
                                       color=self.M_WHITE_L,
                                       zorder=30,
                                       fontsize=12,
                                       clip_on=True,
                                       )
            self.starsAlignAnnotate.append(annotation)
        self.mutexDraw.unlock()
        return True

    def drawHemisphere(self):
        """
        drawHemisphere is the basic renderer for all items and widgets in the
        hemisphere window. it takes care of drawing the grid, enables three
        layers of transparent widgets for static content, moving content and star
        maps. this is mainly done to get a reasonable performance when redrawing
        the canvas. in addition it initializes the objects for points markers,
        patches, lines etc. for making the window nice and user friendly. the
        user interaction on the hemisphere windows is done by the event handler
        of matplotlib itself implementing an on Mouse handler, which takes care
        of functions.

        :return: True for test purpose
        """
        if self.closingWindow:
            return False

        axe, _ = self.generateFlat(widget=self.hemisphereMat,
                                   horizon=True)
        axeMove, _ = self.generateFlat(widget=self.hemisphereMatMove,
                                       horizon=True,
                                       showAxes=False)
        hasPolar = self.ui.showPolar.isChecked()
        if hasPolar:
            axePolar, _ = self.generatePolar(widget=self.polarMat,
                                             horizon=True,
                                             reverse=True)
            axePolarMove, _ = self.generatePolar(widget=self.polarMatMove,
                                                 horizon=True,
                                                 showAxes=False,
                                                 reverse=True)
        else:
            self.pointerPolarAltAz = None
            self.pointsBuildAnnotate = None
            self.pointsPolarBuild = None
            self.pointsPolarBuildAnnotate = None
            self.polarMat.figure.clf()
            self.polarMatMove.figure.clf()

        axe.figure.canvas.flush_events()
        g = self.ui.hemisphere.geometry()
        self.ui.hemisphereMove.setGeometry(QRect(0, 0, g.width(), g.height()))

        if hasPolar:
            axePolar.figure.canvas.flush_events()
            g = self.ui.polar.geometry()
            self.ui.polarMove.setGeometry(QRect(0, 0, g.width(), g.height()))

        if self.ui.checkShowAlignStar.isChecked():
            self.drawAlignmentStars(axes=axe)

        else:
            self.starsAlign = None
            self.starsAlignAnnotate = None

        self.drawHemisphereStatic(axes=axe)
        self.drawHemisphereMoving(axes=axeMove)
        axe.figure.canvas.draw()

        if hasPolar:
            self.drawHemisphereStatic(axes=axePolar, polar=True)
            self.drawHemisphereMoving(axes=axePolarMove, polar=True)
            axePolar.figure.canvas.draw()

        return True
