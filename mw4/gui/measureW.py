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
import PyQt5
import numpy as np
import matplotlib.path as mpath
import matplotlib.patches as mpatches
# local import
from mw4.gui import widget
from mw4.gui.widgets import measure_ui


class MeasureWindow(widget.MWidget):
    """
    the hemisphere window class handles

    """

    __all__ = ['HemisphereWindow',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    BACK = 'background-color: transparent;'
    CYCLE_UPDATE_TASK = 1000

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.showStatus = False
        self.ui = measure_ui.Ui_MeasureDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.data = {
            'title': 'Title',
            'xlabel': 'x-axis',
            'ylabel': 'y-axis',
            'time': list(),
            'y': list(),
        }

        # doing the matplotlib embedding
        # for the alt az plane
        self.measureMat = self.embedMatplot(self.ui.measure)
        self.measureMat.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.measureMat, True)
        self.initConfig()

        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.drawMeasure)
        self.timerTask.start(self.CYCLE_UPDATE_TASK)

    def initConfig(self):
        if 'measureW' not in self.app.config:
            return False
        config = self.app.config['measureW']
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
        if config.get('showStatus'):
            self.showWindow()
        return True

    def storeConfig(self):
        if 'measureW' not in self.app.config:
            self.app.config['measureW'] = {}
        config = self.app.config['measureW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
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
        startY = 5
        self.ui.measure.setGeometry(space,
                                    startY - space,
                                    self.width() - 2 * space,
                                    self.height() - startY)

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)
        # self.changeStyleDynamic(self.app.mainW.ui.openHemisphereW, 'running', 'false')

    def toggleWindow(self):
        self.showStatus = not self.showStatus
        if self.showStatus:
            self.showWindow()
        else:
            self.close()

    def showWindow(self):
        self.showStatus = True
        self.drawMeasure()
        self.show()
        # self.changeStyleDynamic(self.app.mainW.ui.openHemisphereW, 'running', 'true')

    def updateGUI(self):
        """
        updateGUI update gui elements on regular bases (actually 10 second) for items,
        which are not events based.

        :return: success
        """
        self.appendData()
        return True

    @staticmethod
    def clearAxes(axes, visible=False, title=None, xlabel=None, ylabel=None):
        axes.cla()
        axes.set_facecolor((0, 0, 0, 0))
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
        '''
        axes.tick_params(axis='y',
                         colors='#2090C0',
                         which='both',
                         labelleft=True,
                         labelright=True,
                         labelsize=12)
        '''
        axes.set_xlabel(xlabel,
                        color='#2090C0',
                        fontweight='bold',
                        fontsize=12)
        axes.set_ylabel(ylabel,
                        color='#2090C0',
                        fontweight='bold',
                        fontsize=12)
        return True

    def drawMeasure(self):
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
        axes = self.measureMat.figure.axes[0]

        # clearing axes before drawing, only static visible, dynamic only when content
        # is available. visibility is handled with their update method
        title = self.data['title'],
        xlabel = self.data['xlabel'],
        ylabel = self.data['ylabel'],
        self.clearAxes(axes,
                       visible=True,
                       title=title,
                       xlabel=xlabel,
                       ylabel=ylabel,
                       )
        if self.data is None:
            return False
        if not self.data:
            return False
        axes.autoscale_view(scalex=True, scaley=True)
        data = self.app.measure.mData
        axes.plot(data['time'][-50:],
                  data['y'][-50:],
                  marker='o',
                  markersize=5,
                  fillstyle='none',
                  color='#E0E0E0',
                  )
        # drawing the canvas
        axes.figure.canvas.draw()

        # finally setting the mouse handler
        # self.measureMat.figure.canvas.mpl_connect('button_press_event',
        #                                           self.onMouse)
