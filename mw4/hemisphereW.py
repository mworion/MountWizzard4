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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
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
        self.app.mount.signals.settDone.connect(self.updateMeridian)
        self.app.mount.signals.settDone.connect(self.updateCelestialPath)
        self.app.mount.signals.mountUp.connect(self.updateMountDown)

        # initializing the plot
        self.initConfig()

    def initConfig(self):
        if 'hemisphereW' not in self.app.config:
            return
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
                                       self.width() - 2*space,
                                       self.height() - startY)
        self.ui.hemisphereS.setGeometry(space,
                                        startY - space,
                                        self.width() - 2*space,
                                        self.height() - startY)
        self.ui.hemisphereM.setGeometry(space,
                                        startY - space,
                                        self.width() - 2*space,
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
        axes = self.hemisphereMat.figure.axes[0]
        axes.figure.canvas.draw()

    def drawCanvasMoving(self):
        axesM = self.hemisphereMatM.figure.axes[0]
        axesM.figure.canvas.draw()

    def updateMountDown(self, status):
        if not status:
            self.drawHemisphere()

    def updateCelestialPath(self):
        self.celestialPath.set_visible(self.ui.checkShowCelestial.isChecked())
        self.drawCanvas()

    def updateMeridian(self):
        if self.showStatus:
            slew = self.app.mount.sett.meridianLimitSlew
            track = self.app.mount.sett.meridianLimitTrack
            self.meridianTrack.set_visible(self.ui.checkShowMeridian.isChecked())
            self.meridianSlew.set_visible(self.ui.checkShowMeridian.isChecked())
            self.meridianTrack.set_xy((180 - track, 0))
            self.meridianSlew.set_xy((180 - slew, 0))
            self.meridianTrack.set_width(2 * track)
            self.meridianSlew.set_width(2 * slew)
            self.drawCanvas()

    def updatePointerAltAz(self):
        if self.showStatus:
            alt = self.app.mount.obsSite.Alt.degrees
            az = self.app.mount.obsSite.Az.degrees
            self.pointerAltAz.set_data((az, alt))
            self.pointerAltAz.set_visible(True)
            self.drawCanvasMoving()

    @staticmethod
    def markerPoint():
        circleB = mpath.Path.unit_circle()
        circleS = mpath.Path.unit_circle()
        # concatenate the circle with an internal cutout of the star
        verts = np.concatenate([circleB.vertices, 0.5 * circleS.vertices])
        codes = np.concatenate([circleB.codes, circleS.codes])
        marker = mpath.Path(verts, codes)
        return marker

    @staticmethod
    def markerAltAz():
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

    def drawHemisphere(self):
        # shortening the references
        axes = self.hemisphereMat.figure.axes[0]
        axesM = self.hemisphereMatM.figure.axes[0]
        axesS = self.hemisphereMatS.figure.axes[0]

        self.clearAxes(axes, visible=True)
        self.clearAxes(axesM, visible=False)
        self.clearAxes(axesS, visible=False)

        # the static part (model points, horizon, celestial paths, meridian limits)
        # drawing horizon
        if self.app.data.horizonP:
            y, x = zip(*self.app.data.horizonP)

            self.horizonFill, = axes.fill(x, y, color='#002000', zorder=-20)
            self.horizonMarker, = axes.plot(x, y, color='#006000', zorder=-20, lw=3)
            # if self.ui.checkEditHorizonMask.isChecked():
            #    self.maskPlotMarker.set_marker('o')
            #    self.maskPlotMarker.set_color('#FF00FF')
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
            for i, xy in enumerate(zip(x, y)):
                self.pointsBuildAnnotate = axes.annotate('{0:2d}'.format(i+1),
                                                         xy=xy,
                                                         xytext=(2, -10),
                                                         textcoords='offset points',
                                                         color='#E0E0E0',
                                                         zorder=10,
                                                         )
        # draw celestial equator
        celestial = self.app.data.generateCelestialEquator()
        visible = self.ui.checkShowCelestial.isChecked()
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

        # and the the star part (alignment stars)

        # drawing the canvas
        axes.figure.canvas.draw()
        axesM.figure.canvas.draw()
        axesS.figure.canvas.draw()
