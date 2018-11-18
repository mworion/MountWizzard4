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
# local import
from mw4.gui import widget
from mw4.gui import hemisphere_ui


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
        self.resize(800, height)
        if config.get('showStatus'):
            self.showWindow()

    def storeConfig(self):
        if 'hemisphereW' not in self.app.config:
            self.app.config['hemisphereW'] = {}
        config = self.app.config['hemisphereW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['showStatus'] = self.showStatus

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

    def drawHemisphere(self):
        # shortening the references
        axes = self.hemisphereMat.figure.axes[0]
        axesM = self.hemisphereMatM.figure.axes[0]
        axesS = self.hemisphereMatS.figure.axes[0]

        # the static part (model points, horizon, celestial paths, meridian limits)
        self.clearAxes(axes, visible=True)
        y, x = zip(*list(self.app.data.genGrid(numbRows=8,
                                               numbCols=10)))
        axes.plot(x, y,
                  'o',
                  markersize=9,
                  fillstyle='none',
                  color='#00A000')
        for i, xy in enumerate(zip(x, y)):
            axes.annotate('{0:2d}'.format(i+1),
                          xy=xy,
                          color='#E0E0E0')
        # now the moving part (pointing of mount, dome position)
        self.clearAxes(axesM, visible=False)

        # and the the star part (alignment stars)
        self.clearAxes(axesS, visible=False)

