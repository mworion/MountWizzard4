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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import bisect
import gc
# external packages
import PyQt5
import numpy as np
import matplotlib.path as mpath
from matplotlib.artist import Artist
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
# local import
from mw4.gui import widget
from mw4.gui.widgets import hemisphere_ui


class HemisphereWindow(widget.MWidget):
    """
    the hemisphere window class handles

    """

    __all__ = ['HemisphereWindow',
               ]
    version = '0.8'
    logger = logging.getLogger(__name__)

    MODE = dict(
        normal=dict(horMarker='None',
                    horColor='#006000',
                    buildPColor='#00A000',
                    starSize=6,
                    starColor='#808000',
                    starAnnColor='#808080'),
        build=dict(horMarker='None',
                   horColor='#006000',
                   buildPColor='#FF00FF',
                   starSize=6,
                   starColor='#808000',
                   starAnnColor='#808080'),
        horizon=dict(horMarker='o',
                     horColor='#FF00FF',
                     buildPColor='#004000',
                     starSize=6,
                     starColor='#808000',
                     starAnnColor='#808080'),
        star=dict(horMarker='None',
                  horColor='#003000',
                  buildPColor='#004000',
                  starSize=12,
                  starColor='#FFFF00',
                  starAnnColor='#F0F0F0')
    )

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = hemisphere_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.mutexDraw = PyQt5.QtCore.QMutex()

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

        self.initConfig()
        self.configOperationMode()
        self.showWindow()

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
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
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
        # self.app.data.clearBuildP()

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
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

    def closeEvent(self, closeEvent):
        """

        :param closeEvent:
        :return:
        """
        self.storeConfig()

        # signals for gui
        self.ui.checkShowSlewPath.clicked.disconnect(self.drawHemisphere)
        self.ui.checkShowMeridian.clicked.disconnect(self.updateMeridian)
        self.ui.checkShowCelestial.clicked.disconnect(self.updateCelestialPath)
        self.ui.clearBuildP.clicked.disconnect(self.clearHemisphere)
        self.ui.checkUseHorizon.clicked.disconnect(self.drawHemisphere)
        self.ui.checkEditNone.clicked.disconnect(self.setOperationMode)
        self.ui.checkEditHorizonMask.clicked.disconnect(self.setOperationMode)
        self.ui.checkEditBuildPoints.clicked.disconnect(self.setOperationMode)
        self.ui.checkPolarAlignment.clicked.disconnect(self.setOperationMode)
        self.ui.checkShowAlignStar.clicked.disconnect(self.drawHemisphere)
        self.ui.checkShowAlignStar.clicked.disconnect(self.configOperationMode)
        self.app.redrawHemisphere.disconnect(self.drawHemisphere)
        self.app.mount.signals.pointDone.disconnect(self.updatePointerAltAz)
        self.app.mount.signals.settDone.disconnect(self.updateMeridian)
        self.app.mount.signals.settDone.disconnect(self.updateHorizonLimits)
        self.app.mount.signals.settDone.disconnect(self.updateCelestialPath)
        self.app.dome.signals.azimuth.disconnect(self.updateDome)
        self.app.dome.client.signals.deviceDisconnected.disconnect(self.updateDome)
        self.app.update1s.disconnect(self.drawCanvas)
        self.app.update10s.disconnect(self.updateAlignStar)

        plt.close(self.hemisphereMat.figure)

        super().closeEvent(closeEvent)

    def showWindow(self):
        """

        :return:
        """
        self.drawHemisphere()
        self.show()

        # signals for gui
        self.ui.checkShowSlewPath.clicked.connect(self.drawHemisphere)
        self.ui.checkShowMeridian.clicked.connect(self.updateMeridian)
        self.ui.checkShowCelestial.clicked.connect(self.updateCelestialPath)
        self.ui.clearBuildP.clicked.connect(self.clearHemisphere)
        self.ui.checkUseHorizon.clicked.connect(self.drawHemisphere)
        self.ui.checkEditNone.clicked.connect(self.setOperationMode)
        self.ui.checkEditHorizonMask.clicked.connect(self.setOperationMode)
        self.ui.checkEditBuildPoints.clicked.connect(self.setOperationMode)
        self.ui.checkPolarAlignment.clicked.connect(self.setOperationMode)
        self.ui.checkShowAlignStar.clicked.connect(self.drawHemisphere)
        self.ui.checkShowAlignStar.clicked.connect(self.configOperationMode)
        self.app.redrawHemisphere.connect(self.drawHemisphere)
        self.app.mount.signals.pointDone.connect(self.updatePointerAltAz)
        self.app.mount.signals.settDone.connect(self.updateMeridian)
        self.app.mount.signals.settDone.connect(self.updateHorizonLimits)
        self.app.mount.signals.settDone.connect(self.updateCelestialPath)
        self.app.dome.signals.azimuth.connect(self.updateDome)
        self.app.dome.client.signals.deviceDisconnected.connect(self.updateDome)
        self.app.update1s.connect(self.drawCanvas)
        self.app.update10s.connect(self.updateAlignStar)

        # finally setting the mouse handler
        self.hemisphereMat.figure.canvas.mpl_connect('button_press_event',
                                                     self.onMouseDispatcher)

        return True

    def setupAxes(self, figure=None):
        """
        setupAxes cleans up the axes object in figure an setup a new plotting. it draws
        grid, ticks etc.

        :param figure: axes object of figure
        :return:
        """

        if figure is None:
            return None

        for axe in figure.axes:
            axe.cla()
            del axe
            gc.collect()

        figure.clf()
        figure.subplots_adjust(left=0.075, right=0.95, bottom=0.1, top=0.975)
        axe = self.hemisphereMat.figure.add_subplot(1, 1, 1, facecolor=None)

        axe.set_facecolor((0, 0, 0, 0))
        axe.set_xlim(0, 360)
        axe.set_ylim(0, 90)
        axe.spines['bottom'].set_color('#2090C0')
        axe.spines['top'].set_color('#2090C0')
        axe.spines['left'].set_color('#2090C0')
        axe.spines['right'].set_color('#2090C0')
        axe.grid(True, color='#404040')
        axe.set_facecolor((0, 0, 0, 0))
        axe.tick_params(axis='x',
                        colors='#2090C0',
                        labelsize=12)
        axe.set_xlim(0, 360)
        axe.set_xticks(np.arange(0, 361, 30))
        axe.set_ylim(0, 90)
        axe.tick_params(axis='y',
                        colors='#2090C0',
                        which='both',
                        labelleft=True,
                        labelright=True,
                        labelsize=12)
        axe.set_xlabel('Azimuth in degrees',
                       color='#2090C0',
                       fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Altitude in degrees',
                       color='#2090C0',
                       fontweight='bold',
                       fontsize=12)
        return axe

    def drawCanvas(self):
        """
        drawCanvas retrieves the static content axe from widget and redraws the canvas

        :return: success for test
        """

        if not self.mutexDraw.tryLock():
            return False
        axe = self.hemisphereMat.figure.axes[0]
        axe.figure.canvas.draw()
        axe.figure.canvas.flush_events()
        self.mutexDraw.unlock()
        return True

    def updateCelestialPath(self):
        """
        updateCelestialPath is called whenever an update of settings from mount are given.
        it takes the actual values and corrects the point in window if window is in
        show status.
        If the object is not created, the routing returns false.

        :return: success for testing
        """

        if self.celestialPath is None:
            return False
        self.celestialPath.set_visible(self.ui.checkShowCelestial.isChecked())
        return True

    def updateMeridian(self):
        """
        updateMeridian is called whenever an update of settings from mount are given. it
        takes the actual values and corrects the point in window if window is in
        show status.
        If the object is not created, the routing returns false.

        :return: success
        """

        slew = self.app.mount.sett.meridianLimitSlew
        track = self.app.mount.sett.meridianLimitTrack
        if slew is None or track is None:
            return False
        if self.meridianTrack is None:
            return False
        if self.meridianSlew is None:
            return False
        self.meridianTrack.set_visible(self.ui.checkShowMeridian.isChecked())
        self.meridianSlew.set_visible(self.ui.checkShowMeridian.isChecked())
        self.meridianTrack.set_xy((180 - track, 0))
        self.meridianSlew.set_xy((180 - slew, 0))
        self.meridianTrack.set_width(2 * track)
        self.meridianSlew.set_width(2 * slew)
        return True

    def updateHorizonLimits(self):
        """
        updateMeridian is called whenever an update of settings from mount are given. it
        takes updateHorizonLimits actual values and corrects the point in window if window
        is in show status.
        If the object is not created, the routing returns false.

        :return: success
        """

        high = self.app.mount.sett.horizonLimitHigh
        low = self.app.mount.sett.horizonLimitLow
        if high is None or low is None:
            return False
        if self.horizonLimitLow is None:
            return False
        if self.horizonLimitHigh is None:
            return False
        self.horizonLimitHigh.set_xy((0, high))
        self.horizonLimitHigh.set_height(90 - high)
        self.horizonLimitLow.set_xy((0, 0))
        self.horizonLimitLow.set_height(low)
        return True

    def updatePointerAltAz(self):
        """
        updatePointerAltAz is called whenever an update of coordinates from mount are
        given. it takes the actual values and corrects the point in window if window is in
        show status.
        If the object is not created, the routing returns false.

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
        self.pointerAltAz.set_visible(True)
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

        visible = (azimuth != -1)

        self.pointerDome.set_xy((azimuth - 15, 0))
        self.pointerDome.set_visible(visible)

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
        # therefor we add each time the annotation again.

        visible = self.ui.checkShowAlignStar.isChecked()
        for alt, az, name in zip(hip.alt, hip.az, hip.name):
            annotation = axes.annotate(name,
                                       xy=(az, alt),
                                       xytext=(2, 2),
                                       textcoords='offset points',
                                       xycoords='data',
                                       color='#808080',
                                       fontsize=12,
                                       clip_on=True,
                                       visible=visible,
                                       )
            self.starsAlignAnnotate.append(annotation)
        return True

    @staticmethod
    def markerPoint():
        """
        markerPoint constructs a custom marker for presentation of modeldata points

        :return: marker
        """

        circleB = mpath.Path.unit_circle()
        circleS = mpath.Path.unit_circle()
        # concatenate the circle with an internal cutout of the star
        verts = np.concatenate([circleB.vertices, 0.5 * circleS.vertices])
        codes = np.concatenate([circleB.codes, circleS.codes])
        marker = mpath.Path(verts, codes)
        return marker

    @staticmethod
    def markerAltAz():
        """
        markerAltAz constructs a custom marker for AltAz pointer

        :return: marker
        """

        circleB = mpath.Path.unit_circle()
        circleM = mpath.Path.unit_circle()
        circleS = mpath.Path.unit_circle()
        # concatenate the circle with an internal cutout of the star
        verts = np.concatenate([circleB.vertices,
                                0.8 * circleM.vertices,
                                0.3 * circleS.vertices])
        codes = np.concatenate([circleB.codes,
                                circleM.codes,
                                circleS.codes])
        marker = mpath.Path(verts, codes)
        return marker

    @staticmethod
    def markerStar():
        """
        markerStar constructs a custom marker for presentation of modeldata points

        :return: marker
        """

        star = mpath.Path.unit_regular_star(8)
        # concatenate the circle with an internal cutout of the star
        verts = np.concatenate([star.vertices])
        codes = np.concatenate([star.codes])
        marker = mpath.Path(verts, codes)
        return marker

    def clearHemisphere(self):
        """
        clearHemisphere is called when after startup the location of the mount is changed
        to reconstruct correctly the hemisphere window

        :return:
        """

        self.pointsBuild = None
        self.app.data.clearBuildP()
        self.drawHemisphere()

    def configOperationMode(self):
        """
        configOperationMode enables and disables the select PolarAlign button according
        to the status of Show align stars. without showing align stars it does not make
        sense to enable this function.

        :return: nothing
        """

        if self.ui.checkShowAlignStar.isChecked():
            self.ui.checkPolarAlignment.setEnabled(True)
        else:
            self.ui.checkPolarAlignment.setEnabled(False)
            if self.ui.checkPolarAlignment.isChecked():
                self.ui.checkEditNone.setChecked(True)

    def setOperationMode(self):
        """
        setOperationMode changes the operation mode of the hemisphere window(s) depending
        on the choice, colors and styles will be changed.

        :return: success
        """

        mode = ''
        if self.ui.checkEditNone.isChecked():
            mode = 'normal'
        elif self.ui.checkEditBuildPoints.isChecked():
            mode = 'build'
        elif self.ui.checkEditHorizonMask.isChecked():
            mode = 'horizon'
        elif self.ui.checkPolarAlignment.isChecked():
            mode = 'star'

        # styles
        if self.horizonMarker is not None:
            self.horizonMarker.set_marker(self.MODE[mode]['horMarker'])
            self.horizonMarker.set_color(self.MODE[mode]['horColor'])
        if self.pointsBuild is not None:
            self.pointsBuild.set_color(self.MODE[mode]['buildPColor'])
        if self.starsAlign is not None:
            # self.starsAlignAnnotate.set_color(self.MODE[mode]['horMarker'])
            self.starsAlign.set_color(self.MODE[mode]['starColor'])

        self.drawCanvas()
        return True

    @staticmethod
    def getIndexPoint(event=None, plane=None, epsilon=2):
        """
        getIndexPoint returns the index of the point which is nearest to the coordinate
        of the mouse click when the click is in distance epsilon of the points. otherwise
        no index will be returned.

        :param event: data of the mouse clicked event
        :param plane: coordinates as tuples (alt, az)
        :param epsilon:
        :return: index or none
        """

        if event is None:
            return None
        if plane is None:
            return None
        if len(plane) == 0:
            return None

        xt = np.asarray([i[1] for i in plane])
        yt = np.asarray([i[0] for i in plane])
        d = np.sqrt((xt - event.xdata)**2 / 16 + (yt - event.ydata)**2)
        index = d.argsort()[:1][0]
        # position to far away
        if d[index] >= epsilon:
            return None
        index = int(index)
        return index

    @staticmethod
    def getIndexPointX(event=None, plane=None):
        """
        getIndexPointX returns the index of the point which has a x coordinate closest to
        the left of the x coordinate of the mouse click regardless which y coordinate it has

        :param event: data of the mouse clicked event
        :param plane: coordinates as tuples (x, y)
        :return: index or none
        """

        if event is None:
            return None
        if plane is None:
            return None
        if len(plane) < 2:
            return None

        xt = [i[1] for i in plane]
        index = int(bisect.bisect_left(xt, event.xdata) - 1)
        return index

    def onMouseNormal(self, event):
        """
        onMouseNormal handles the mouse event in normal mode. this means only a double
        click is possible and offers the opportunity to slew the telescope to a certain
        position in sky selected by the mouse.

        :param event: mouse events
        :return: success
        """

        if not event.inaxes:
            return False
        if event.button != 1 or not event.dblclick:
            return False

        textFormat = 'Do you want to slew the mount to:\n\nAzimuth:\t{0}°\nAltitude:\t{1}°'
        azimuth = int(event.xdata + 0.5)
        altitude = int(event.ydata + 0.5)
        question = textFormat.format(azimuth, altitude)
        msg = PyQt5.QtWidgets.QMessageBox
        reply = msg.question(self,
                             'Hemisphere direct slew',
                             question,
                             msg.Yes | msg.No,
                             msg.No,
                             )
        if reply != msg.Yes:
            return False
        suc = self.app.mount.obsSite.slewAltAz(alt_degrees=altitude,
                                               az_degrees=azimuth,
                                               slewType='normal')
        if not suc:
            self.app.message.emit('Cannot slew to: {0}, {1}'.format(azimuth, altitude), 2)
        else:
            self.app.message.emit('Slewing to: {0}, {1}'.format(azimuth, altitude), 0)
        return suc

    def addHorizonPoint(self, data=None, event=None):
        """
        addHorizonPoint calculates from the position of the left mouse click the position
        where the next horizon point should be added. the coordinates are given from mouse
        click itself.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return:
        """

        index = self.getIndexPointX(event=event, plane=data.horizonP) + 1
        suc = data.addHorizonP(value=(event.ydata, event.xdata),
                               position=index)
        return suc

    def deleteHorizonPoint(self, data=None, event=None):
        """
        deleteHorizonPoint selects the next horizon point in distance max and tries to
        delete it. there have to be at least 2 horizon point left.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return: success
        """

        index = self.getIndexPoint(event=event, plane=data.horizonP)
        suc = False
        if len(data.horizonP) > 2:
            suc = data.delHorizonP(position=index)
        return suc

    def editHorizonMask(self, data=None, event=None):
        """
        editHorizonMask does dispatching the different mouse clicks for adding or deleting
        horizon mask points and call the function accordingly.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return: success
        """

        if event.button == 1:
            suc = self.addHorizonPoint(data=data, event=event)
        elif event.button == 3:
            suc = self.deleteHorizonPoint(data=data, event=event)
        else:
            return False

        y, x = zip(*data.horizonP)
        self.horizonMarker.set_data(x, y)
        self.horizonFill.set_xy(np.column_stack((x, y)))

        self.drawCanvas()
        return suc

    def addBuildPoint(self, data=None, event=None, axes=None):
        """
        addBuildPoint calculates from the position of the left mouse click the position
        where the next modeldata point should be added. the coordinates are given from mouse
        click itself.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :param axes: link to drawing axes in matplotlib
        :return:
        """

        index = self.getIndexPoint(event=event, plane=data.buildP, epsilon=360)
        # if no point found, add at the end
        if index is None:
            index = len(data.buildP)
        # take the found point closer to the end of the list
        index += 1
        suc = data.addBuildP(value=(event.ydata, event.xdata),
                             position=index)
        if not suc:
            return False

        # if succeeded, than add the data to the matplotlib hemisphere widget
        # first the point
        x = event.xdata
        y = event.ydata
        if self.ui.checkShowSlewPath.isChecked():
            ls = ':'
            lw = 1
        else:
            ls = ''
            lw = 0
        color = '#FF00FF'
        if self.pointsBuild is None:
            newBuildP, = axes.plot(x,
                                   y,
                                   marker=self.markerPoint(),
                                   markersize=9,
                                   linestyle=ls,
                                   lw=lw,
                                   fillstyle='none',
                                   color=color,
                                   zorder=20,
                                   )
            self.pointsBuild = newBuildP

        # and than the annotation (number)
        xy = (x, y)
        newAnnotation = axes.annotate('4',
                                      xy=xy,
                                      xytext=(2, -10),
                                      textcoords='offset points',
                                      color='#E0E0E0',
                                      zorder=10,
                                      )
        if self.pointsBuildAnnotate is None:
            self.pointsBuildAnnotate = list()
        self.pointsBuildAnnotate.insert(index, newAnnotation)
        return True

    def deleteBuildPoint(self, data=None, event=None):
        """
        deleteBuildPoint selects the next modeldata point in distance max and tries to
        delete it. there have to be at least 2 horizon point left.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return: success
        """

        index = self.getIndexPoint(event=event, plane=data.buildP)
        suc = data.delBuildP(position=index)
        if suc:
            self.pointsBuildAnnotate[index].remove()
            del self.pointsBuildAnnotate[index]
        return suc

    def editBuildPoints(self, data=None, event=None, axes=None):
        """
        editBuildPoints does dispatching the different mouse clicks for adding or deleting
        model data points and call the function accordingly.

        :param data: points in tuples (alt, az)
        :param event: mouse event
        :param axes: link to drawing axes in matplotlib
        :return: success
        """

        if event.button == 1:
            suc = self.addBuildPoint(data=data, event=event, axes=axes)
        elif event.button == 3:
            suc = self.deleteBuildPoint(data=data, event=event)
        else:
            return False

        # redraw the corrected canvas (new positions ans new numbers)
        if len(data.buildP):
            y, x = zip(*data.buildP)
        else:
            y = x = []
        self.pointsBuild.set_data(x, y)
        for i, _ in enumerate(data.buildP):
            self.pointsBuildAnnotate[i].set_text('{0:2d}'.format(i))
        self.drawCanvas()
        return suc

    def onMouseEdit(self, event):
        """
        onMouseEdit handles the mouse event in normal mode. this means depending on the
        edit mode (horizon or model points) a left click adds a new point and right click
        deletes the selected point.

        :param event: mouse events
        :return: success
        """

        data = self.app.data
        axes = self.hemisphereMat.figure.axes[0].axes

        if not event.inaxes:
            return False
        if event.dblclick:
            return False

        if self.ui.checkEditHorizonMask.isChecked():
            suc = self.editHorizonMask(event=event, data=data)
        elif self.ui.checkEditBuildPoints.isChecked():
            suc = self.editBuildPoints(event=event, data=data, axes=axes)
        else:
            return False
        return suc

    def onMouseStar(self, event):
        """
        onMouseStar handles the mouse event in polar align mode. this means only a right
        click is possible and offers the opportunity to slew the telescope to the selected
        star and start manual polar alignment.

        :param event: mouse events
        :return: success
        """

        if not event.inaxes:
            return False
        if event.button == 1:
            alignType = 'polar'
        elif event.button == 3:
            alignType = 'ortho'
        else:
            return False
        if event.dblclick:
            return False

        hip = self.app.hipparcos
        plane = list(zip(hip.alt, hip.az))
        index = self.getIndexPoint(event=event, plane=plane, epsilon=2)
        if index is None:
            return False

        name = hip.name[index]
        ra, dec = hip.getAlignStarRaDecFromName(hip.name[index])

        textFormat = 'Align: {0}\nDo you want to slew the mount to:\n\n{1}'
        question = textFormat.format(alignType, name)
        msg = PyQt5.QtWidgets.QMessageBox
        reply = msg.question(self,
                             f'Hemisphere {alignType} align',
                             question,
                             msg.Yes | msg.No,
                             msg.No,
                             )
        if reply != msg.Yes:
            return False
        suc = self.app.mount.obsSite.slewRaDec(ra_hours=ra,
                                               dec_degrees=dec,
                                               slewType=f'{alignType}')
        if not suc:
            self.app.message.emit('Cannot slew to: {0}'.format(name), 2)
        else:
            self.app.message.emit('Slewing to: {0}'.format(name), 0)
        return suc

    def _staticHorizon(self, axes=None):
        """

        :param axes: matplotlib axes object
        :return:
        """

        showHorizon = self.ui.checkUseHorizon.isChecked()

        if not (self.app.data.horizonP and showHorizon):
            return False

        alt, az = zip(*self.app.data.horizonP)

        self.horizonFill, = axes.fill(az, alt, color='#002000', zorder=-20)
        self.horizonMarker, = axes.plot(az, alt, color='#006000', zorder=-20, lw=3)
        if self.ui.checkEditHorizonMask.isChecked():
            self.horizonMarker.set_marker('o')
            self.horizonMarker.set_color('#FF00FF')
        return True

    def _staticModelData(self, axes=None):
        """

        :param axes: matplotlib axes object
        :return: success
        """

        if not self.app.data.buildP:
            return False

        alt, az = zip(*self.app.data.buildP)
        # show line path pf slewing
        if self.ui.checkShowSlewPath.isChecked():
            ls = ':'
            lw = 1
        else:
            ls = ''
            lw = 0
        if self.ui.checkEditBuildPoints.isChecked():
            color = '#FF00FF'
        else:
            color = '#00A000'
        self.pointsBuild, = axes.plot(az, alt,
                                      marker=self.markerPoint(),
                                      markersize=9,
                                      linestyle=ls,
                                      lw=lw,
                                      fillstyle='none',
                                      color=color,
                                      zorder=20,
                                      )
        self.pointsBuildAnnotate = list()
        for i, AltAz in enumerate(zip(az, alt)):
            annotation = axes.annotate('{0:2d}'.format(i),
                                       xy=AltAz,
                                       xytext=(2, -10),
                                       textcoords='offset points',
                                       color='#E0E0E0',
                                       zorder=10,
                                       )
            self.pointsBuildAnnotate.append(annotation)
        return True

    def _staticCelestialEquator(self, axes=None):
        """

        :param axes: matplotlib axes object
        :return: success
        """

        # draw celestial equator
        visible = self.ui.checkShowCelestial.isChecked()
        celestial = self.app.data.generateCelestialEquator()
        alt, az = zip(*celestial)
        self.celestialPath, = axes.plot(az,
                                        alt,
                                        '.',
                                        markersize=1,
                                        fillstyle='none',
                                        color='#808080',
                                        visible=visible)
        return True

    def _staticMeridianLimits(self, axes=None):
        """

        :param axes: matplotlib axes object
        :return: success
        """

        # draw meridian limits
        if self.app.mount.sett.meridianLimitSlew is not None:
            slew = self.app.mount.sett.meridianLimitSlew
        else:
            slew = 0
        visible = self.ui.checkShowMeridian.isChecked()
        self.meridianSlew = mpatches.Rectangle((180 - slew, 0),
                                               2 * slew,
                                               90,
                                               zorder=-5,
                                               color='#00008080',
                                               visible=visible)
        axes.add_patch(self.meridianSlew)
        if self.app.mount.sett.meridianLimitTrack is not None:
            track = self.app.mount.sett.meridianLimitTrack
        else:
            track = 0
        self.meridianTrack = mpatches.Rectangle((180 - track, 0),
                                                2 * track,
                                                90,
                                                zorder=-10,
                                                color='#80800080',
                                                visible=visible)
        axes.add_patch(self.meridianTrack)
        return True

    def _staticAltitudeLimits(self, axes=None):
        """

        :param axes: matplotlib axes object
        :return: success
        """

        if self.app.mount.sett.horizonLimitHigh is not None:
            high = self.app.mount.sett.horizonLimitHigh
        else:
            high = 90
        if self.app.mount.sett.horizonLimitLow is not None:
            low = self.app.mount.sett.horizonLimitLow
        else:
            low = 0
        self.horizonLimitHigh = mpatches.Rectangle((0, high),
                                                   360,
                                                   90 - high,
                                                   zorder=-30,
                                                   color='#60383880',
                                                   visible=True)
        self.horizonLimitLow = mpatches.Rectangle((0, 0),
                                                  360,
                                                  low,
                                                  zorder=-30,
                                                  color='#60383880',
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
        :return:
        """

        self._staticHorizon(axes=axes)
        self._staticModelData(axes=axes)
        self._staticCelestialEquator(axes=axes)
        self._staticMeridianLimits(axes=axes)
        self._staticAltitudeLimits(axes=axes)

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

        # pointer
        self.pointerAltAz, = axes.plot(180, 45,
                                       zorder=10,
                                       color='#FF00FF',
                                       marker=self.markerAltAz(),
                                       markersize=25,
                                       linestyle='none',
                                       fillstyle='none',
                                       clip_on=False,
                                       visible=False,
                                       )
        # adding pointer of dome if dome is present
        az = self.app.dome.data.get('DOME_ABSOLUTE_POSITION', -1)
        visible = (az != -1)
        self.pointerDome = mpatches.Rectangle((165, 0),
                                              30,
                                              90,
                                              zorder=-30,
                                              color='#40404080',
                                              lw=3,
                                              fill=True,
                                              visible=visible)
        axes.add_patch(self.pointerDome)

    def drawHemisphereStars(self, axes=None):
        """
        drawHemisphereStars is rendering the alignment star map. this moves over time with
        the speed of earth turning. so we have to update the rendering, but on low speed
        without having any user interaction.

        :param axes: matplotlib axes object
        :return:
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
                                     color='#808000',
                                     zorder=-20,
                                     visible=visible,
                                     )
        for alt, az, name in zip(hip.alt, hip.az, hip.name):
            annotation = axes.annotate(name,
                                       xy=(az, alt),
                                       xytext=(2, 2),
                                       textcoords='offset points',
                                       xycoords='data',
                                       color='#808080',
                                       fontsize=12,
                                       clip_on=True,
                                       visible=visible,
                                       )
            self.starsAlignAnnotate.append(annotation)

    def onMouseDispatcher(self, event):
        """
        onMouseDispatcher dispatches the button events depending on the actual operation
        mode.

        :param event: button event for parsing
        :return:
        """

        if self.ui.checkEditNone.isChecked():
            self.onMouseNormal(event)
        elif self.ui.checkEditBuildPoints.isChecked():
            self.onMouseEdit(event)
        elif self.ui.checkEditHorizonMask.isChecked():
            self.onMouseEdit(event)
        elif self.ui.checkPolarAlignment.isChecked():
            self.onMouseStar(event)

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
        axes = self.setupAxes(figure=self.hemisphereMat.figure)

        # calling renderer
        self.drawHemisphereStatic(axes=axes)
        self.drawHemisphereMoving(axes=axes)
        self.drawHemisphereStars(axes=axes)

        self.setOperationMode()

        # drawing the canvas
        axes.figure.canvas.draw()
