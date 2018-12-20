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
# external packages
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches
# local import
from mw4.gui import widget
from mw4.gui.widgets import hemisphere_ui


class HemisphereWindow(widget.MWidget):
    """
    the hemisphere window class handles

    """

    __all__ = ['HemisphereWindow',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    BACK = 'background-color: transparent;'

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.showStatus = False
        self.ui = hemisphere_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.initUI()

        # attributes to be stored in class
        self.pointerAltAz = None
        self.pointerDome = None
        self.pointsBuild = None
        self.pointsBuildAnnotate = None
        self.starsAlign = None
        self.starsAlignAnnotate = None
        self.horizonFill = None
        self.horizonMarker = None
        self.meridianSlew = None
        self.meridianTrack = None
        self.celestialPath = None

        # doing the matplotlib embedding
        # for the alt az plane
        self.hemisphereMat = self.embedMatplot(self.ui.hemisphere)
        self.hemisphereMat.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.hemisphereMat, True)
        # for the fast moving parts
        self.hemisphereMatM = self.embedMatplot(self.ui.hemisphereM)
        self.hemisphereMatM.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.hemisphereMatM, False)
        # for the stars in background
        self.hemisphereMatS = self.embedMatplot(self.ui.hemisphereS)
        self.hemisphereMatS.parentWidget().setStyleSheet(self.BACK)
        self.ui.hemisphereS.setVisible(False)
        self.clearRect(self.hemisphereMatS, False)

        # signals for gui
        self.ui.checkShowSlewPath.clicked.connect(self.drawHemisphere)
        self.ui.checkShowMeridian.clicked.connect(self.updateMeridian)
        self.ui.checkShowCelestial.clicked.connect(self.updateCelestialPath)
        self.app.mount.signals.pointDone.connect(self.updatePointerAltAz)
        self.app.mount.signals.pointDone.connect(self.updateDome)
        self.app.mount.signals.settDone.connect(self.updateMeridian)
        self.app.mount.signals.settDone.connect(self.updateCelestialPath)
        self.app.signalUpdateLocation.connect(self.clearHemisphere)
        self.ui.clearBuildP.clicked.connect(self.clearHemisphere)
        self.app.mainW.ui.checkUseHorizon.clicked.connect(self.drawHemisphere)
        self.ui.checkEditNone.clicked.connect(lambda: self.setOperationMode('normal'))
        self.ui.checkEditHorizonMask.clicked.connect(lambda: self.setOperationMode('horizon'))
        self.ui.checkEditModelPoints.clicked.connect(lambda: self.setOperationMode('model'))
        self.ui.checkPolarAlignment.clicked.connect(lambda: self.setOperationMode('polar'))

        if 'mainW' in self.app.config:
            self.app.data.horizonPFile = self.app.config['mainW'].get('horizonFileName')
            self.app.data.loadHorizonP()
        self.initConfig()

    def initConfig(self):
        if 'hemisphereW' not in self.app.config:
            return False
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
        if config.get('showStatus'):
            self.showWindow()
        return True

    def storeConfig(self):
        if 'hemisphereW' not in self.app.config:
            self.app.config['hemisphereW'] = {}
        config = self.app.config['hemisphereW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['showStatus'] = self.showStatus
        config['checkShowSlewPath'] = self.ui.checkShowSlewPath.isChecked()
        config['checkShowMeridian'] = self.ui.checkShowMeridian.isChecked()
        config['checkShowCelestial'] = self.ui.checkShowCelestial.isChecked()

    def resizeEvent(self, QResizeEvent):
        """
        resizeEvent changes the internal widget according to the resize of the window
        the formulae of the calculation is:
            spaces left right top button : 5 pixel
            widget start in height at y = 130

        :param QResizeEvent:
        :return: nothing
        """

        super().resizeEvent(QResizeEvent)
        space = 5
        startY = 130
        self.ui.hemisphere.setGeometry(space,
                                       startY - space,
                                       self.width() - 2 * space,
                                       self.height() - startY)
        self.ui.hemisphereS.setGeometry(space,
                                        startY - space,
                                        self.width() - 2 * space,
                                        self.height() - startY)
        self.ui.hemisphereM.setGeometry(space,
                                        startY - space,
                                        self.width() - 2 * space,
                                        self.height() - startY)

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)
        self.changeStyleDynamic(self.app.mainW.ui.openHemisphereW, 'running', 'false')

    def toggleWindow(self):
        self.showStatus = not self.showStatus
        if self.showStatus:
            self.showWindow()
        else:
            self.close()

    def showWindow(self):
        self.showStatus = True
        self.drawHemisphere()
        self.show()
        self.changeStyleDynamic(self.app.mainW.ui.openHemisphereW, 'running', 'true')

    @staticmethod
    def clearAxes(axes, visible=False):
        axes.cla()
        axes.set_facecolor((0, 0, 0, 0))
        axes.set_xlim(0, 360)
        axes.set_ylim(0, 90)
        if not visible:
            axes.set_axis_off()
            return False
        axes.spines['bottom'].set_color('#2090C0')
        axes.spines['top'].set_color('#2090C0')
        axes.spines['left'].set_color('#2090C0')
        axes.spines['right'].set_color('#2090C0')
        axes.grid(True, color='#404040')
        axes.set_facecolor((0, 0, 0, 0))
        axes.tick_params(axis='x',
                         colors='#2090C0',
                         labelsize=12)
        axes.set_xlim(0, 360)
        axes.set_xticks(np.arange(0, 361, 30))
        axes.set_ylim(0, 90)
        axes.tick_params(axis='y',
                         colors='#2090C0',
                         which='both',
                         labelleft=True,
                         labelright=True,
                         labelsize=12)
        axes.set_xlabel('Azimuth in degrees',
                        color='#2090C0',
                        fontweight='bold',
                        fontsize=12)
        axes.set_ylabel('Altitude in degrees',
                        color='#2090C0',
                        fontweight='bold',
                        fontsize=12)
        return True

    def drawCanvas(self):
        """
        drawCanvas retrieves the static content axes from widget and redraws the canvas

        :return: success for test
        """

        axes = self.hemisphereMat.figure.axes[0]
        axes.figure.canvas.draw()
        return True

    def drawCanvasMoving(self):
        """
        drawCanvasMoving retrieves the moving content axes from widget and redraws the
        canvas

        :return: success for test
        """

        axesM = self.hemisphereMatM.figure.axes[0]
        axesM.figure.canvas.draw()
        return True

    def drawCanvasStar(self):
        """
        drawCanvasStar retrieves the moving content axes from widget and redraws the canvas

        :return: success for test
        """

        axesS = self.hemisphereMatM.figure.axes[0]
        axesS.figure.canvas.draw()
        return True

    def updateCelestialPath(self):
        """
        updateCelestialPath is called whenever an update of settings from mount are given.
        it takes the actual values and corrects the point in window if window is in
        show status.

        :return: success for testing
        """

        if not self.showStatus:
            return False
        if self.celestialPath is None:
            return False
        self.celestialPath.set_visible(self.ui.checkShowCelestial.isChecked())
        self.drawCanvas()
        return True

    def updateMeridian(self):
        """
        updateMeridian is called whenever an update of settings from mount are given. it
        takes the actual values and corrects the point in window if window is in
        show status.

        :return: success
        """

        if not self.showStatus:
            return False
        slew = self.app.mount.sett.meridianLimitSlew
        track = self.app.mount.sett.meridianLimitTrack
        if slew is None or track is None:
            return False
        self.meridianTrack.set_visible(self.ui.checkShowMeridian.isChecked())
        self.meridianSlew.set_visible(self.ui.checkShowMeridian.isChecked())
        self.meridianTrack.set_xy((180 - track, 0))
        self.meridianSlew.set_xy((180 - slew, 0))
        self.meridianTrack.set_width(2 * track)
        self.meridianSlew.set_width(2 * slew)
        self.drawCanvas()
        return True

    def updatePointerAltAz(self):
        """
        updatePointerAltAz is called whenever an update of coordinates from mount are
        given. it takes the actual values and corrects the point in window if window is in
        show status.

        :return: success
        """

        if not self.showStatus:
            return False
        obsSite = self.app.mount.obsSite
        if obsSite.Alt is None:
            return False
        if obsSite.Az is None:
            return False
        alt = obsSite.Alt.degrees
        az = obsSite.Az.degrees
        self.pointerAltAz.set_data((az, alt))
        self.pointerAltAz.set_visible(True)
        self.drawCanvasMoving()
        return True

    def updateDome(self):
        """
        updateDome is called whenever an update of coordinates from dome are given.
        it takes the actual values and corrects the point in window if window is in
        show status.

        :return: success
        """

        if not self.showStatus:
            return False

        # using mount for test
        obsSite = self.app.mount.obsSite
        if obsSite.Az is None:
            return False
        az = obsSite.Az.degrees

        self.pointerDome.set_xy((az - 15, 0))
        self.pointerDome.set_visible(True)
        self.drawCanvasMoving()
        return True

    @staticmethod
    def markerPoint():
        """
        markerPoint constructs a custom marker for presentation of build points

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

    def clearHemisphere(self):
        """
        clearHemisphere is called when after startup the location of the mount is changed
        to reconstruct correctly the hemisphere window

        :return:
        """
        self.app.data.clearBuildP()
        self.drawHemisphere()

    def setOperationMode(self, mode):
        """
        setOperationMode changes the operation mode of the hemisphere window. depending
        on the choice, colors and styles will be changed.

        :param mode: operation mode as text
        :return: success
        """

        # reset the settings
        if self.horizonMarker is not None:
            self.horizonMarker.set_marker('None')
            self.horizonMarker.set_color('#006000')
        if self.pointsBuild is not None:
            self.pointsBuild.set_color('#00A000')
        # self.starsAlignment.set_color('#C0C000')
        # self.starsAlignment.set_markersize(6)
        # for i in range(0, len(self.starsAnnotate)):
        #    self.starsAnnotate[i].set_color('#808080')
        self.ui.hemisphere.stackUnder(self.ui.hemisphereM)

        # now choose the right styles
        if mode == 'normal':
            pass
        elif mode == 'model':
            if self.pointsBuild is not None:
                self.pointsBuild.set_color('#FF00FF')
            self.ui.hemisphereM.stackUnder(self.ui.hemisphere)
        elif mode == 'horizon':
            if self.horizonMarker is not None:
                self.horizonMarker.set_marker('o')
                self.horizonMarker.set_color('#FF00FF')
            self.ui.hemisphereM.stackUnder(self.ui.hemisphere)
        elif mode == 'polar':
            # self.starsAlignment.set_color('#FFFF00')
            # self.starsAlignment.set_markersize(12)
            # for i in range(0, len(self.starsAnnotate)):
            #    self.starsAnnotate[i].set_color('#F0F0F0')
            self.ui.hemisphere.stackUnder(self.ui.hemisphereM)
        self.drawCanvas()
        return True

    @staticmethod
    def getIndexUnderPoint(event, xy, epsilon):
        """

        :param event: data of the mouse clicked event
        :param xy: coordinates
        :param epsilon:
        :return: index or none
        """

        if len(xy) == 0:
            return None
        xt = np.asarray([i[0] for i in xy])
        yt = np.asarray([i[1] for i in xy])
        d = np.sqrt((xt - event.xdata)**2 / 16 + (yt - event.ydata)**2)
        ind = d.argsort()[:1][0]
        # position to far away
        if d[ind] >= epsilon:
            return None
        return ind

    @staticmethod
    def getTwoIndUnderPointX(event, xy):
        """

        :param event: data of the mouse clicked event
        :param xy: coordinates
        :return: index or none
        """

        if len(xy) < 2:
            return None
        xt = [i[0] for i in xy]
        return bisect.bisect_left(xt, event.xdata) - 1

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
        # shortening the references
        axes = self.hemisphereMat.figure.axes[0]
        axesM = self.hemisphereMatM.figure.axes[0]
        axesS = self.hemisphereMatS.figure.axes[0]

        self.clearAxes(axes, visible=True)
        self.clearAxes(axesM, visible=False)
        self.clearAxes(axesS, visible=False)

        # the static part (model points, horizon, celestial paths, meridian limits)
        # drawing horizon
        showHorizon = self.app.mainW.ui.checkUseHorizon.isChecked()
        if self.app.data.horizonP and showHorizon:
            y, x = zip(*self.app.data.horizonP)

            self.horizonFill, = axes.fill(x, y, color='#002000', zorder=-20)
            self.horizonMarker, = axes.plot(x, y, color='#006000', zorder=-20, lw=3)
            if self.ui.checkEditHorizonMask.isChecked():
                self.horizonMarker.set_marker('o')
                self.horizonMarker.set_color('#FF00FF')

        # drawing build points
        if self.app.data.buildP:
            y, x = zip(*self.app.data.buildP)
            # show line path pf slewing
            if self.ui.checkShowSlewPath.isChecked():
                ls = ':'
                lw = 1
            else:
                ls = ''
                lw = 0
            self.pointsBuild, = axes.plot(x, y,
                                          marker=self.markerPoint(),
                                          markersize=9,
                                          linestyle=ls,
                                          lw=lw,
                                          fillstyle='none',
                                          color='#00A000',
                                          zorder=20,
                                          )
            if self.ui.checkEditModelPoints.isChecked():
                self.pointsBuild.set_color('#FF00FF')
            for i, xy in enumerate(zip(x, y)):
                self.pointsBuildAnnotate = axes.annotate('{0:2d}'.format(i + 1),
                                                         xy=xy,
                                                         xytext=(2, -10),
                                                         textcoords='offset points',
                                                         color='#E0E0E0',
                                                         zorder=10,
                                                         )
        # draw celestial equator
        visible = self.ui.checkShowCelestial.isChecked()
        celestial = self.app.data.generateCelestialEquator()
        y, x = zip(*celestial)
        self.celestialPath, = axes.plot(x,
                                        y,
                                        '.',
                                        markersize=1,
                                        fillstyle='none',
                                        color='#808080',
                                        visible=visible)
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
                                               color='#FF000040',
                                               lw=1,
                                               fill=True,
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
                                                color='#FFFF0040',
                                                lw=1,
                                                fill=True,
                                                visible=visible)
        axes.add_patch(self.meridianTrack)

        # now the moving part (pointing of mount, dome position)
        self.pointerAltAz, = axesM.plot(180, 45,
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
        self.pointerDome = mpatches.Rectangle((165, 0),
                                              30,
                                              90,
                                              zorder=-30,
                                              color='#40404080',
                                              lw=3,
                                              fill=True,
                                              visible=False)
        axesM.add_patch(self.pointerDome)

        # and the the star part (alignment stars)

        # drawing the canvas
        axes.figure.canvas.draw()
        axesM.figure.canvas.draw()
        axesS.figure.canvas.draw()
