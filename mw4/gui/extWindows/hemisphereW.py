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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

# local import
from gui.utilities import widget
from gui.widgets import hemisphere_ui
from gui.extWindows.hemisphereWext import HemisphereWindowExt


class HemisphereWindow(widget.MWidget, HemisphereWindowExt):
    """
    the hemisphere window class handles all interaction with model points show / edit etc.

    """

    __all__ = ['HemisphereWindow',
               ]

    RESIZE_FINISHED_TIMEOUT = 0.3

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.ui = hemisphere_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.mutexDraw = PyQt5.QtCore.QMutex()
        self.operationMode = 'normal'
        self.statusDAT = None

        self.MODE = dict(
            normal=dict(horMarker='None',
                        horColor=self.M_GREEN,
                        buildPColor=self.M_GREEN_H,
                        starSize=6,
                        starColor=self.M_YELLOW_L,
                        starAnnColor=self.M_WHITE_L),
            build=dict(horMarker='None',
                       horColor=self.M_GREEN,
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
                      horColor=self.M_GREEN_LL,
                      buildPColor=self.M_GREEN_L,
                      starSize=12,
                      starColor=self.M_YELLOW_H,
                      starAnnColor=self.M_WHITE_H)
        )

        self.startup = True
        self.resizeTimerValue = -1

        # attributes to be stored in class
        self.pointerAltAz = None
        self.pointerDome = None
        self.pointsBuild = None
        self.pointsBuildAnnotate = list()
        self.starsAlign = None
        self.starsAlignAnnotate = list()
        self.horizonFill = None
        self.horizonMarker = None
        self.meridianSlew = None
        self.meridianTrack = None
        self.horizonLimitHigh = None
        self.horizonLimitLow = None
        self.celestialPath = None

        # doing the matplotlib embedding
        self.hemisphereMat = self.embedMatplot(self.ui.hemisphere)
        self.hemisphereMat.parentWidget().setStyleSheet(self.BACK_BG)
        self.hemisphereBack = None
        self.hemisphereBackStars = None

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        if 'hemisphereW' not in self.app.config:
            self.app.config['hemisphereW'] = {}

        config = self.app.config['hemisphereW']
        x = config.get('winPosX', 60)
        y = config.get('winPosY', 60)

        if x > self.screenSizeX:
            x = 0

        if y > self.screenSizeY:
            y = 0

        self.move(x, y)
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        self.ui.checkShowSlewPath.setChecked(config.get('checkShowSlewPath', False))
        self.ui.checkShowMeridian.setChecked(config.get('checkShowMeridian', False))
        self.ui.checkShowCelestial.setChecked(config.get('checkShowCelestial', False))
        self.ui.checkShowAlignStar.setChecked(config.get('checkShowAlignStar', False))
        self.ui.checkUseHorizon.setChecked(config.get('checkUseHorizon', False))
        self.ui.showPolar.setChecked(config.get('showPolar', False))
        self.configOperationMode()

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

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

        return True

    def closeEvent(self, closeEvent):
        """

        :param closeEvent:
        :return:
        """
        self.app.update10s.disconnect(self.updateAlignStar)
        self.app.update0_1s.disconnect(self.resizeTimer)
        self.app.redrawHemisphere.disconnect(self.drawHemisphere)
        self.app.mount.signals.settingDone.disconnect(self.updateSettings)
        self.storeConfig()

        # restore DAT status
        self.ui.checkEditNone.setChecked(True)
        self.setOperationMode()

        # signals for gui
        self.ui.checkShowSlewPath.clicked.disconnect(self.drawHemisphere)
        self.ui.checkShowMeridian.clicked.disconnect(self.updateSettings)
        self.ui.checkShowCelestial.clicked.disconnect(self.updateSettings)
        self.ui.checkUseHorizon.clicked.disconnect(self.drawHemisphere)
        self.ui.checkEditNone.clicked.disconnect(self.setOperationMode)
        self.ui.checkEditHorizonMask.clicked.disconnect(self.setOperationMode)
        self.ui.checkEditBuildPoints.clicked.disconnect(self.setOperationMode)
        self.ui.checkPolarAlignment.clicked.disconnect(self.setOperationMode)
        self.ui.checkShowAlignStar.clicked.disconnect(self.drawHemisphere)
        self.ui.checkShowAlignStar.clicked.disconnect(self.configOperationMode)
        self.app.mount.signals.pointDone.disconnect(self.updatePointerAltAz)
        self.app.dome.signals.azimuth.disconnect(self.updateDome)
        self.app.dome.signals.deviceDisconnected.disconnect(self.updateDome)
        self.app.dome.signals.serverDisconnected.disconnect(self.updateDome)

        plt.close(self.hemisphereMat.figure)
        super().closeEvent(closeEvent)

    def resizeEvent(self, event):
        """
        we are using the resize event to reset the timer, which means waiting for
        RESIZE_FINISHED_TIMEOUT in total before redrawing the complete hemisphere.
        as we are using a 0.1s cyclic timer.

        :param event:
        :return:
        """

        super().resizeEvent(event)
        if self.startup:
            self.startup = False
        else:
            self.resizeTimerValue = int(self.RESIZE_FINISHED_TIMEOUT / 0.1)

    def resizeTimer(self):
        """
        the resize timer is a workaround because when resizing the window, the blit
        function needs a new scaled background picture to retrieve. otherwise you will get
        odd picture. unfortunately there is no resize finished event from qt
        framework itself. problem is you never know, when resizing is finished.
        it might be the best way to implement a event filter with mouse and resize
        events to build a resize finished event. so the only quick solution is to wait for
        some time after we got the last resize event and than draw the widgets
        from scratch on.

        :return: True for test purpose
        """

        self.resizeTimerValue -= 1
        if self.resizeTimerValue == 0:
            self.drawHemisphere()

        return True

    def showWindow(self):
        """

        :return:
        """

        self.app.update10s.connect(self.updateAlignStar)
        self.app.update0_1s.connect(self.resizeTimer)
        self.app.redrawHemisphere.connect(self.drawHemisphere)
        self.app.mount.signals.settingDone.connect(self.updateSettings)
        self.app.mount.signals.pointDone.connect(self.updatePointerAltAz)
        self.app.dome.signals.azimuth.connect(self.updateDome)
        self.app.dome.signals.deviceDisconnected.connect(self.updateDome)
        self.app.dome.signals.serverDisconnected.connect(self.updateDome)

        self.ui.checkShowSlewPath.clicked.connect(self.drawHemisphere)
        self.ui.checkUseHorizon.clicked.connect(self.drawHemisphere)
        self.ui.checkShowAlignStar.clicked.connect(self.drawHemisphere)
        self.ui.checkShowMeridian.clicked.connect(self.updateSettings)
        self.ui.checkShowCelestial.clicked.connect(self.updateSettings)
        self.ui.checkEditNone.clicked.connect(self.setOperationMode)
        self.ui.checkEditHorizonMask.clicked.connect(self.setOperationMode)
        self.ui.checkEditBuildPoints.clicked.connect(self.setOperationMode)
        self.ui.checkPolarAlignment.clicked.connect(self.setOperationMode)
        self.ui.checkShowAlignStar.clicked.connect(self.configOperationMode)

        self.hemisphereMat.figure.canvas.mpl_connect('button_press_event',
                                                     self.onMouseDispatcher)
        self.hemisphereMat.figure.canvas.mpl_connect('motion_notify_event',
                                                     self.showMouseCoordinates)
        self.show()
        self.drawHemisphere()

        return True

    def drawBlit(self):
        """
        There were some optimizations in with regard to drawing speed derived from:
        https://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
        so whenever a draw canvas is made, I store the background and painting the
        pointers is done via blit.

        :return: success
        """

        if not self.mutexDraw.tryLock():
            return False

        if self.hemisphereMat.figure.axes and self.hemisphereBackStars:
            axe = self.hemisphereMat.figure.axes[0]
            axe.figure.canvas.restore_region(self.hemisphereBackStars)
            self.pointerAltAz.set_visible(True)
            axe.draw_artist(self.pointerAltAz)
            axe.draw_artist(self.pointerDome)
            axe.figure.canvas.blit(axe.bbox)

        self.mutexDraw.unlock()

        return True

    def drawBlitStars(self):
        """
        The alignment stars were the second layer to be draw.

        There were some optimizations in with regard to drawing speed derived from:
        https://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
        so whenever a draw canvas is made, I store the background and painting the
        pointers is done via blit.

        :return: success
        """

        if not self.mutexDraw.tryLock():
            return False

        if self.hemisphereMat.figure.axes and self.hemisphereBack:
            axe = self.hemisphereMat.figure.axes[0]
            axe.figure.canvas.restore_region(self.hemisphereBack)
            axe.draw_artist(self.starsAlign)
            for annotation in self.starsAlignAnnotate:
                axe.draw_artist(annotation)
            axe.figure.canvas.blit(axe.bbox)
            self.hemisphereBackStars = axe.figure.canvas.copy_from_bbox(axe.bbox)

        self.mutexDraw.unlock()
        return True

    def updateCelestialPath(self):
        """
        updateCelestialPath is called whenever an update of settings from mount are given.
        it takes the actual values and corrects the point in window if window is in
        show status.
        If the object is not created, the routing returns false.

        :return: needs drawing
        """

        if self.celestialPath is None:
            return False

        isVisible = self.celestialPath.get_visible()
        newVisible = self.ui.checkShowCelestial.isChecked()
        needDraw = isVisible != newVisible
        self.celestialPath.set_visible(newVisible)

        return needDraw

    def updateMeridian(self, sett):
        """
        updateMeridian is called whenever an update of settings from mount are given. it
        takes the actual values and corrects the point in window if window is in
        show status.
        If the object is not created, the routing returns false.

        :param sett: settings reference from mount
        :return: needs drawing
        """

        slew = sett.meridianLimitSlew
        track = sett.meridianLimitTrack

        if slew is None or track is None:
            return False

        if self.meridianTrack is None:
            return False

        if self.meridianSlew is None:
            return False

        isVisible = self.meridianTrack.get_visible()
        newVisible = self.ui.checkShowMeridian.isChecked()
        needDraw = isVisible != newVisible

        self.meridianTrack.set_visible(newVisible)
        self.meridianSlew.set_visible(newVisible)

        self.meridianTrack.set_xy((180 - track, 0))
        self.meridianSlew.set_xy((180 - slew, 0))

        aktTrack = self.meridianTrack.get_width() / 2
        aktSlew = self.meridianSlew.get_width() / 2

        needDraw = needDraw or (track != aktTrack) or (slew != aktSlew)

        self.meridianTrack.set_width(2 * track)
        self.meridianSlew.set_width(2 * slew)

        return needDraw

    def updateHorizonLimits(self, sett):
        """
        updateHorizonLimits is called whenever an update of settings from mount are given. it
        takes updateHorizonLimits actual values and corrects the point in window if window
        is in show status.
        If the object is not created, the routing returns false.

        :param sett: settings reference from mount
        :return: success
        """

        high = sett.horizonLimitHigh
        low = sett.horizonLimitLow

        if high is None or low is None:
            return False

        if self.horizonLimitLow is None:
            return False

        if self.horizonLimitHigh is None:
            return False

        aktHigh = self.horizonLimitHigh.get_xy()[1]
        aktLow = self.horizonLimitLow.get_height()

        needDraw = aktHigh != high or aktLow != low

        self.horizonLimitHigh.set_xy((0, high))
        self.horizonLimitHigh.set_height(90 - high)
        self.horizonLimitLow.set_xy((0, 0))
        self.horizonLimitLow.set_height(low)

        return needDraw

    def updateSettings(self):
        """
        updateSettings renders all static settings upon signals received and aggregates the
        need of a drawing. the called methods have to detect if something changed to
        determine if a redraw has to be done. this is done to reduce runtime and preserve
        low CPU processing.

        :return: needs draw
        """

        sett = self.app.mount.setting

        suc = self.updateCelestialPath()
        suc = self.updateHorizonLimits(sett) or suc
        suc = self.updateMeridian(sett) or suc

        if suc:
            self.drawHemisphere()

        return suc

    def updatePointerAltAz(self):
        """
        updatePointerAltAz is called whenever an update of coordinates from mount are
        given. it takes the actual values and corrects the point in window if window is in
        show status.
        If the object is not created, the routing returns false.

        There were some optimizations in with regard to drawing speed derived from:
        https://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
        so whenever a draw canvas is made, I store the background and painting the
        pointers is done via blit.

        :return: success
        """

        obsSite = self.app.mount.obsSite

        if obsSite.Alt is None:
            return False

        if obsSite.Az is None:
            return False

        if self.pointerAltAz is None:
            return False

        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerAltAz.set_data((az, alt))

        self.drawBlit()

        return True

    def updateDome(self, azimuth):
        """
        updateDome is called whenever an update of coordinates from dome are given.
        it takes the actual values and corrects the point in window if window is in
        show status.
        If the object is not created, the routing returns false.

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

        self.drawBlit()

        return True

    def updateAlignStar(self):
        """
        updateAlignStar is called whenever an update of coordinates from mount are
        given. it takes the actual values and corrects the point in window if window is in
        show status.
        If the object is not created, the routing returns false.

        :return: success
        """

        if not self.ui.checkShowAlignStar.isChecked():
            return False

        if self.starsAlign is None:
            return False

        if self.starsAlignAnnotate is None:
            return False

        axes = self.hemisphereMat.figure.axes[0]
        hip = self.app.hipparcos
        hip.calculateAlignStarPositionsAltAz()
        self.starsAlign.set_data(hip.az, hip.alt)
        for i, starAnnotation in enumerate(self.starsAlignAnnotate):
            starAnnotation.remove()
        self.starsAlignAnnotate = list()

        # due to the fact that all annotation are only shown if in axes when coordinate
        # are in data, after some time, no annotation will be shown, because just moved.
        # therefore we add each time the annotation again.

        visible = self.ui.checkShowAlignStar.isChecked()
        for alt, az, name in zip(hip.alt, hip.az, hip.name):
            annotation = axes.annotate(name,
                                       xy=(az, alt),
                                       xytext=(2, 2),
                                       textcoords='offset points',
                                       xycoords='data',
                                       color=self.M_WHITE_L,
                                       fontsize=12,
                                       clip_on=True,
                                       visible=visible,
                                       )
            self.starsAlignAnnotate.append(annotation)
        self.drawBlitStars()
        return True

    def clearHemisphere(self):
        """
        clearHemisphere is called when after startup the location of the mount is changed
        to reconstruct correctly the hemisphere window

        :return: True for test Purpose
        """

        self.pointsBuild = None
        self.app.data.clearBuildP()
        self.drawHemisphere()

        return True

    def staticHorizon(self, axes=None):
        """
        staticHorizon draw the horizon line. in case of a polar plot it will be reversed,
        which mean the background will be green and to horizon polygon will be drawn in
        background color

        :param axes: matplotlib axes object
        :return:
        """

        showHorizon = self.ui.checkUseHorizon.isChecked()

        if not (self.app.data.horizonP and showHorizon):
            return False

        alt, az = zip(*self.app.data.horizonP)
        alt = np.array(alt)
        az = np.array(az)

        self.horizonFill, = axes.fill(az,
                                      alt,
                                      color=self.M_GREEN_LL,
                                      zorder=-20)
        self.horizonMarker, = axes.plot(az,
                                        alt,
                                        color=self.MODE[self.operationMode]['horColor'],
                                        marker=self.MODE[self.operationMode]['horMarker'],
                                        zorder=-20,
                                        lw=3)

        return True

    def staticModelData(self, axes=None):
        """
        staticModelData draw in the chart the build points and their index as annotations

        :param axes: matplotlib axes object
        :return: success
        """

        if not self.app.data.buildP:
            return False

        points = self.app.data.buildP
        alt = [x[0] for x in points]
        az = [x[1] for x in points]

        if self.ui.checkShowSlewPath.isChecked():
            ls = ':'
            lw = 1

        else:
            ls = ''
            lw = 0

        self.pointsBuild, = axes.plot(az, alt,
                                      marker=self.markerPoint(),
                                      markersize=9,
                                      linestyle=ls,
                                      lw=lw,
                                      fillstyle='none',
                                      color=self.MODE[self.operationMode]['buildPColor'],
                                      zorder=20,
                                      )

        for point in points:
            if point[2]:
                continue

            axes.plot(point[1], point[0],
                      marker='$\u2714$',
                      color=self.M_YELLOW,
                      zorder=25,
                      markersize=15,
                      alpha=0.6,
                      )

        self.pointsBuildAnnotate = list()

        for i, point in enumerate(points):
            if point[2]:
                annotationText = f'{i + 1:2d}'
                color = self.M_WHITE
            else:
                annotationText = f'{i + 1:2d}'
                color = self.M_YELLOW

            annotation = axes.annotate(annotationText,
                                       xy=(point[1], point[0]),
                                       xytext=(2, -10),
                                       textcoords='offset points',
                                       color=color,
                                       zorder=10,
                                       )
            self.pointsBuildAnnotate.append(annotation)

        return True

    def staticCelestialEquator(self, axes=None):
        """
        staticCelestialEquator draw ra / dec lines on the chart

        :param axes: matplotlib axes object
        :return: success
        """

        visible = self.ui.checkShowCelestial.isChecked()
        celestial = self.app.data.generateCelestialEquator()
        alt, az = zip(*celestial)

        self.celestialPath, = axes.plot(az,
                                        alt,
                                        '.',
                                        markersize=1,
                                        fillstyle='none',
                                        color=self.M_WHITE_L,
                                        visible=visible)
        return True

    def staticMeridianLimits(self, axes=None):
        """

        :param axes: matplotlib axes object
        :return: success
        """
        if self.app.mount.setting.meridianLimitSlew is not None:
            slew = self.app.mount.setting.meridianLimitSlew

        else:
            slew = 0

        visible = self.ui.checkShowMeridian.isChecked()
        self.meridianSlew = mpatches.Rectangle((180 - slew, 0),
                                               2 * slew,
                                               90,
                                               zorder=-5,
                                               color=self.M_BLUE_ALPHA,
                                               visible=visible)
        axes.add_patch(self.meridianSlew)

        if self.app.mount.setting.meridianLimitTrack is not None:
            track = self.app.mount.setting.meridianLimitTrack

        else:
            track = 0

        self.meridianTrack = mpatches.Rectangle((180 - track, 0),
                                                2 * track,
                                                90,
                                                zorder=-10,
                                                color=self.M_YELLOW_L_ALPHA,
                                                visible=visible)
        axes.add_patch(self.meridianTrack)

        return True

    def staticHorizonLimits(self, axes=None):
        """

        :param axes: matplotlib axes object
        :return: success
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
                                                   zorder=-30,
                                                   color=self.M_RED_ALPHA,
                                                   visible=True)
        self.horizonLimitLow = mpatches.Rectangle((0, 0),
                                                  360,
                                                  low,
                                                  zorder=-30,
                                                  color=self.M_RED_ALPHA,
                                                  visible=True)
        axes.add_patch(self.horizonLimitHigh)
        axes.add_patch(self.horizonLimitLow)

        return True

    def drawHemisphereStatic(self, axes=None):
        """
         drawHemisphereStatic renders the static part of the hemisphere window and puts
         all drawing on the static plane. the content consist of:
            - modeldata points
            - horizon mask
            - celestial paths
            - meridian limits
        with all their styles an coloring

        :param axes: matplotlib axes object
        :return: success
        """

        if not self.mutexDraw.tryLock():
            return False

        self.staticHorizon(axes=axes)
        self.staticCelestialEquator(axes=axes)
        self.staticMeridianLimits(axes=axes)
        self.staticHorizonLimits(axes=axes)
        self.staticModelData(axes=axes)

        axes.figure.canvas.draw()
        axes.figure.canvas.flush_events()
        self.hemisphereBack = axes.figure.canvas.copy_from_bbox(axes.bbox)

        self.mutexDraw.unlock()

        return True

    def drawHemisphereMoving(self, axes=None):
        """
        drawHemisphereMoving is rendering the moving part which consists of:
            - pointer: where the mount points to
            - dome widget: which shows the position of the dome opening
        the dynamic ones are located on a separate plane to improve rendering speed,
        because we update this part very often.

        :param axes: matplotlib axes object
        :return:
        """

        self.pointerAltAz, = axes.plot(180, 45,
                                       zorder=10,
                                       color=self.M_PINK,
                                       marker=self.markerAltAz(),
                                       markersize=25,
                                       linestyle='none',
                                       fillstyle='none',
                                       clip_on=True,
                                       visible=False,
                                       )

        self.pointerDome = mpatches.Rectangle((165, 1),
                                              30,
                                              88,
                                              zorder=-30,
                                              color=self.M_GREY_ALPHA,
                                              lw=3,
                                              clip_on=True,
                                              fill=True,
                                              visible=False)

        axes.add_patch(self.pointerDome)

        return True

    def drawAlignmentStars(self, axes=None):
        """
        drawAlignmentStars is rendering the alignment star map. this moves over time with
        the speed of earth turning. so we have to update the rendering, but on low speed
        without having any user interaction.

        :param axes: matplotlib axes object
        :return: true for test purpose
        """

        visible = self.ui.checkShowAlignStar.isChecked()
        self.starsAlignAnnotate = list()
        hip = self.app.hipparcos
        hip.calculateAlignStarPositionsAltAz()
        self.starsAlign, = axes.plot(hip.az,
                                     hip.alt,
                                     marker=self.markerStar(),
                                     markersize=7,
                                     linestyle='',
                                     color=self.MODE[self.operationMode]['starColor'],
                                     zorder=-20,
                                     visible=visible,
                                     )
        for alt, az, name in zip(hip.alt, hip.az, hip.name):
            annotation = axes.annotate(name,
                                       xy=(az, alt),
                                       xytext=(2, 2),
                                       textcoords='offset points',
                                       xycoords='data',
                                       color=self.M_WHITE_L,
                                       fontsize=12,
                                       clip_on=True,
                                       visible=visible,
                                       )
            self.starsAlignAnnotate.append(annotation)
        self.drawBlitStars()
        return True

    def drawHemisphere(self):
        """
        drawHemisphere is the basic renderer for all items and widgets in the hemisphere
        window. it takes care of drawing the grid, enables three layers of transparent
        widgets for static content, moving content and star maps. this is mainly done to
        get a reasonable performance when redrawing the canvas. in addition it initializes
        the objects for points markers, patches, lines etc. for making the window nice
        and user friendly.
        the user interaction on the hemisphere windows is done by the event handler of
        matplotlib itself implementing an on Mouse handler, which takes care of functions.

        :return: nothing
        """

        # clearing axes before drawing, only static visible, dynamic only when content
        # is available. visibility is handled with their update method
        self.hemisphereMat.figure.canvas.draw()
        axe, _ = self.generateFlat(widget=self.hemisphereMat, horizon=True)

        # calling renderer
        self.drawHemisphereStatic(axes=axe)
        self.drawHemisphereMoving(axes=axe)
        self.drawAlignmentStars(axes=axe)
