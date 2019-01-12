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
    NUMBER_POINTS = 50
    NUMBER_XTICKS = 8

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.showStatus = False
        self.ui = measure_ui.Ui_MeasureDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.mutexDraw = PyQt5.QtCore.QMutex()
        self.diagram = {
            'ui': [self.ui.tp03m,
                   self.ui.tp10m,
                   self.ui.tp30m,
                   self.ui.tp01h,
                   self.ui.tp03h,
                   self.ui.tp10h,
                   ],
            'cycle': [1,
                      2,
                      5,
                      10,
                      20,
                      50,
                      100,
                      ],
        }
        self.measureSet = {
            'title': ['Environment',
                      'RaDec Stability',
                      'Sky Quality',
                      ],
            'ylabel': ['Temperature',
                       'arcsec',
                       'mpas',
                       ],
        }
        self.measureSetCheck = 0
        self.timeWindowCheck = 0

        # doing the matplotlib embedding
        self.measureMat = self.embedMatplot(self.ui.measure)
        self.measureMat.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.measureMat, True)

        self.ui.tp03m.clicked.connect(lambda: self.drawMeasure(0))
        self.ui.tp10m.clicked.connect(lambda: self.drawMeasure(1))
        self.ui.tp30m.clicked.connect(lambda: self.drawMeasure(2))
        self.ui.tp01h.clicked.connect(lambda: self.drawMeasure(3))
        self.ui.tp03h.clicked.connect(lambda: self.drawMeasure(4))
        self.ui.tp10h.clicked.connect(lambda: self.drawMeasure(5))

        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(lambda: self.drawMeasure(self.timeWindowCheck))
        self.timerTask.start(self.CYCLE_UPDATE_TASK)
        self.initConfig()

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

        # todo: initialize the old setup

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

        # todo: save actual status

        return True

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
        startY = 95
        self.ui.measure.setGeometry(space,
                                    startY - space,
                                    self.width() - 2 * space,
                                    self.height() - startY)

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)

    def showWindow(self):
        self.showStatus = True
        self.drawMeasure(0)
        self.show()

    def clearPlot(self):
        # shortening the references
        axes = self.measureMat.figure.axes[0]
        axes.cla()
        axes.set_facecolor((0, 0, 0, 0))
        axes.spines['bottom'].set_color('#2090C0')
        axes.spines['top'].set_color('#2090C0')
        axes.spines['left'].set_color('#2090C0')
        axes.spines['right'].set_color('#2090C0')
        axes.grid(True, color='#404040')
        axes.set_facecolor((0, 0, 0, 0))

    def drawMeasure(self, timeWindow=0):
        """

        :return: nothing
        """

        if not self.showStatus:
            return False
        if not self.mutexDraw.tryLock():
            return False

        self.timeWindowCheck = timeWindow
        for i, button in enumerate(self.diagram['ui']):
            if i == timeWindow:
                self.changeStyleDynamic(button, 'running', 'true')
            else:
                self.changeStyleDynamic(button, 'running', 'false')

        cycle = self.diagram['cycle'][timeWindow]
        self.timerTask.stop()
        self.timerTask.start(cycle * 1000)
        self.clearPlot()

        axes = self.measureMat.figure.axes[0]
        axes.tick_params(axis='x',
                         colors='#2090C0',
                         labelsize=12)
        axes.set_xlabel(self.measureSet['title'][0],
                        color='#2090C0',
                        fontweight='bold',
                        fontsize=12)
        axes.set_ylabel(self.measureSet['ylabel'][0],
                        color='#2090C0',
                        fontweight='bold',
                        fontsize=12)

        data = self.app.measure.mData

        start = -self.NUMBER_POINTS * cycle
        ratio = cycle * int(self.NUMBER_POINTS / self.NUMBER_XTICKS)

        time = data['time'][start:-1:cycle]
        time_ticks = data['time'][start:-1:ratio]
        y = data['temp'][start:-1:cycle]

        axes.plot(time,
                  y,
                  marker='o',
                  markersize=3,
                  fillstyle='none',
                  color='#E0E0E0',
                  )
        axes.set_xticks(time_ticks)

        axes.figure.canvas.draw()
        self.mutexDraw.unlock()
