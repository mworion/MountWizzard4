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
from datetime import datetime as dt
# external packages
import PyQt5
import numpy as np
# local import
from mw4.gui import widget
from mw4.gui.widgets import measure_ui


class MeasureWindow(widget.MWidget):
    """
    the hemisphere window class handles

    """

    __all__ = ['MeasureWindow',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    BACK = 'background-color: transparent;'
    CYCLE_UPDATE_TASK = 1000
    NUMBER_POINTS = 500
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
            'ui': [self.ui.tp0,
                   self.ui.tp1,
                   self.ui.tp2,
                   self.ui.tp3,
                   self.ui.tp4,
                   self.ui.tp5,
                   self.ui.tp6,
                   ],
            'cycle': [1,
                      2,
                      4,
                      8,
                      16,
                      32,
                      64,
                      ],
        }
        self.measureSet = {
            'title': ['Environment',
                      'RaDec Stability',
                      'Sky Quality',
                      ],
            'ylabel1': ['Temperature',
                        'arcsec',
                        'mpas',
                        ],
            'ylabel2': ['Pressure',
                        'arcsec',
                        '',
                        ],
        }
        self.measureSetCheck = 0
        self.timeWindowCheck = 0

        # doing the matplotlib embedding
        self.measureMat = self.embedMatplot(self.ui.measure)
        self.measureMat.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.measureMat, True)
        self.measureMat.figure.axes[0].twinx()

        for i, ui in enumerate(self.diagram['ui']):
            value = self.diagram['cycle'][i] * self.NUMBER_POINTS
            if value < 3000:
                text = '{0:2d} min'.format(int(value/60))
            else:
                text = '{0:2d} hrs'.format(int(value / 3600))
            ui.setText(text)
        self.ui.tp0.clicked.connect(lambda: self.drawMeasure(0))
        self.ui.tp1.clicked.connect(lambda: self.drawMeasure(1))
        self.ui.tp2.clicked.connect(lambda: self.drawMeasure(2))
        self.ui.tp3.clicked.connect(lambda: self.drawMeasure(3))
        self.ui.tp4.clicked.connect(lambda: self.drawMeasure(4))
        self.ui.tp5.clicked.connect(lambda: self.drawMeasure(5))
        self.ui.tp6.clicked.connect(lambda: self.drawMeasure(6))

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

    def clearPlot(self, title='default', ylabel=('', '')):
        # shortening the references
        fig = self.measureMat.figure
        axe0 = fig.axes[0]
        axe1 = fig.axes[1]

        color1 = '#2090C0'
        color2 = '#209020'
        color1grid = '#104860'
        color2grid = '#104810'
        fig.subplots_adjust(left=0.1,
                            right=0.9,
                            bottom=0.1,
                            top=0.95,
                            )

        axe0.cla()
        axe0.set_facecolor((0, 0, 0, 0))
        axe0.grid(True, color=color1grid)
        axe0.set_facecolor((0, 0, 0, 0))
        axe0.tick_params(axis='x',
                         colors=color1,
                         labelsize=12)
        axe0.set_title(title,
                       color=color1,
                       fontweight='bold',
                       fontsize=12)
        axe0.set_xlabel('time',
                        color=color1,
                        fontweight='bold',
                        fontsize=12)
        axe0.set_ylabel(ylabel[0],
                        color=color1,
                        fontweight='bold',
                        fontsize=12)
        if not ylabel[1]:
            return
        axe1.cla()
        axe1.set_facecolor((0, 0, 0, 0))
        axe1.spines['bottom'].set_color(color1)
        axe1.spines['top'].set_color(color1)
        axe1.spines['left'].set_color(color1)
        axe1.spines['right'].set_color(color1)
        axe1.grid(True, color=color2grid)
        axe1.set_facecolor((0, 0, 0, 0))
        axe1.tick_params(axis='y',
                         colors=color2,
                         labelsize=12)
        axe1.set_ylabel(ylabel[1],
                        color=color2,
                        fontweight='bold',
                        fontsize=12)

    def drawMeasure(self, timeWindow=0):
        """

        :return: nothing
        """

        color1 = '#2090C0'
        color2 = '#209020'
        title = self.measureSet['title'][self.measureSetCheck]
        ylabel1 = self.measureSet['ylabel1'][self.measureSetCheck]
        ylabel2 = self.measureSet['ylabel2'][self.measureSetCheck]
        self.clearPlot(title=title,
                       ylabel=(ylabel1, ylabel2)
                       )
        if not self.showStatus:
            return False
        data = self.app.measure.mData
        if len(data['time']) == 0:
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

        axe0 = self.measureMat.figure.axes[0]
        axe1 = self.measureMat.figure.axes[1]

        start = -self.NUMBER_POINTS * cycle
        grid = int(self.NUMBER_POINTS / self.NUMBER_XTICKS)
        ratio = cycle * grid
        time = data['time'][start:-1:cycle]
        time_end = data['time'][-1]
        y1 = data['temp'][start:-1:cycle]
        y2 = data['press'][start:-1:cycle]

        time_ticks = np.arange(-self.NUMBER_XTICKS, 1, 1)
        time_ticks = time_ticks * ratio * 1000000
        time_ticks = time_ticks + time_end
        time_labels = [x.astype(dt).strftime('%H:%M:%S') for x in time_ticks]

        axe0.set_xticks(time_ticks)
        axe0.set_xticklabels(time_labels)
        axe0.set_xlim(time_ticks[0], time_ticks[-1])

        axe0.plot(time,
                  y1,
                  marker='o',
                  markersize=2,
                  fillstyle='none',
                  color=color1,
                  )
        if ylabel2:
            axe1.plot(time,
                      y2,
                      marker='o',
                      markersize=2,
                      fillstyle='none',
                      color=color2,
                      )
            axe1.set_xticks(time_ticks)
            axe1.set_xticklabels(time_labels)
            axe1.set_xlim(time_ticks[0], time_ticks[-1])
        axe0.figure.canvas.draw()
        axe1.figure.canvas.draw()
        self.mutexDraw.unlock()
