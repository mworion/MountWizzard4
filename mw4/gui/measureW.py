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
    the measure window class handles

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
            'ui': [self.ui.ms0,
                   self.ui.ms1,
                   self.ui.ms2,
                   ]
        }
        self.measureIndex = 0
        self.timeIndex = 0

        # doing the matplotlib embedding
        self.measureMat = self.embedMatplot(self.ui.measure)
        self.measureMat.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.measureMat, True)
        # adding two axes (getting 3 in total)
        self.measureMat.figure.axes[0].twinx()
        self.measureMat.figure.axes[0].twinx()

        self.ui.tp0.clicked.connect(lambda: self.setTimeWindow(0))
        self.ui.tp1.clicked.connect(lambda: self.setTimeWindow(1))
        self.ui.tp2.clicked.connect(lambda: self.setTimeWindow(2))
        self.ui.tp3.clicked.connect(lambda: self.setTimeWindow(3))
        self.ui.tp4.clicked.connect(lambda: self.setTimeWindow(4))
        self.ui.tp5.clicked.connect(lambda: self.setTimeWindow(5))
        self.ui.tp6.clicked.connect(lambda: self.setTimeWindow(6))

        self.ui.ms0.clicked.connect(lambda: self.setMeasureSet(0))
        self.ui.ms1.clicked.connect(lambda: self.setMeasureSet(1))
        self.ui.ms2.clicked.connect(lambda: self.setMeasureSet(2))

        mainW = self.app.mainW.ui
        self.clickable(mainW.RA).connect(lambda: self.openShowMeasureSet(0))
        self.clickable(mainW.DEC).connect(lambda: self.openShowMeasureSet(0))
        self.clickable(mainW.localTemp).connect(lambda: self.openShowMeasureSet(1))
        self.clickable(mainW.localPress).connect(lambda: self.openShowMeasureSet(1))
        self.clickable(mainW.localDewPoint).connect(lambda: self.openShowMeasureSet(1))
        self.clickable(mainW.SQR).connect(lambda: self.openShowMeasureSet(2))

        self.timerTask = PyQt5.QtCore.QTimer()
        self.timerTask.setSingleShot(False)
        self.timerTask.timeout.connect(self.drawMeasure)
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
        self.setupButtons()
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
        if not self.app.mainW.ui.checkMeasurement.isChecked():
            return False
        self.showStatus = True
        self.drawMeasure()
        self.show()
        return True

    def setupButtons(self):
        """
        setupButtons prepares the dynamic content od the buttons in measurement window. it
        write the bottom texts and number as well as the coloring for the actual setting

        :return: success for test purpose
        """

        for i, ui in enumerate(self.diagram['ui']):
            value = self.diagram['cycle'][i] * self.NUMBER_POINTS
            if value < 3000:
                text = '{0:2d} min'.format(int(value / 60))
            else:
                text = '{0:2d} hrs'.format(int(value / 3600))
            ui.setText(text)

        for i, button in enumerate(self.diagram['ui']):
            if i == 0:
                self.changeStyleDynamic(button, 'running', 'true')
            else:
                self.changeStyleDynamic(button, 'running', 'false')

        for i, button in enumerate(self.measureSet['ui']):
            if i == 0:
                self.changeStyleDynamic(button, 'running', 'true')
            else:
                self.changeStyleDynamic(button, 'running', 'false')

        return True

    def setTimeWindow(self, index):
        """

        :param index: index of time window set
        :return: success
        """

        if index < 0:
            return False
        if index > len(self.diagram['ui']):
            return False

        self.timeIndex = index
        for i, button in enumerate(self.diagram['ui']):
            if i == index:
                self.changeStyleDynamic(button, 'running', 'true')
            else:
                self.changeStyleDynamic(button, 'running', 'false')
        self.drawMeasure()
        return True

    def setMeasureSet(self, index):
        """

        :param index: index of time window set
        :return: success
        """

        if index < 0:
            return False
        if index > len(self.measureSet['ui']):
            return False

        self.measureIndex = index
        for i, button in enumerate(self.measureSet['ui']):
            if i == index:
                self.changeStyleDynamic(button, 'running', 'true')
            else:
                self.changeStyleDynamic(button, 'running', 'false')
        self.drawMeasure()
        return True

    def openShowMeasureSet(self, index):
        """

        :param index: index of time window set
        :return: success
        """

        suc = self.setMeasureSet(index)
        if suc:
            self.showWindow()
            return True
        else:
            return False

    def clearPlot(self, numbAxes=None):

        if numbAxes < 1:
            return False
        if numbAxes > 3:
            return False

        color = '#2090C0'

        fig = self.measureMat.figure

        if 0 < numbAxes < 3:
            fig.subplots_adjust(left=0.1,
                                right=0.9,
                                bottom=0.1,
                                top=0.95,
                                )
        elif numbAxes == 3:
            fig.subplots_adjust(left=0.1,
                                right=0.8,
                                bottom=0.1,
                                top=0.95,
                                )

        for i, axe in enumerate(fig.axes):
            axe.cla()
            if i < numbAxes:
                axe.set_visible(True)
            else:
                axe.set_visible(False)
            axe.set_facecolor((0, 0, 0, 0))
            axe.tick_params(axis='both',
                            colors=color,
                            labelsize=12)
            axe.set_facecolor((0, 0, 0, 0))
            axe.spines['bottom'].set_color(color)
            axe.spines['top'].set_color(color)
            axe.spines['left'].set_color(color)
            axe.spines['right'].set_color(color)
        return True

    def drawRaDecStability(self):
        if not self.clearPlot(numbAxes=2):
            return False

        axe0 = self.measureMat.figure.axes[0]
        axe1 = self.measureMat.figure.axes[1]

        colorTitle = '#2090C0'
        colorLeft = '#A0A0A0'
        colorRight = '#30B030'
        colorGrid = '#404040'
        title = 'RaDec Stability'
        ylabelLeft = 'delta RA [arcsec]'
        ylabelRight = 'delta DEC [arcsec]'

        data = self.app.measure.data
        cycle = self.diagram['cycle'][self.timeIndex]
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        yLeft = data['raJNow'][start:-1:cycle]
        yRight = data['decJNow'][start:-1:cycle]

        axe0.set_title(title,
                       color=colorTitle,
                       fontweight='bold',
                       fontsize=16)
        axe0.set_xlabel('Time [HH:MM:SS - UTC]',
                        color=colorTitle,
                        fontweight='bold',
                        fontsize=12)
        axe0.set_ylabel(ylabelLeft,
                        color=colorLeft,
                        fontweight='bold',
                        fontsize=12)
        axe1.set_ylabel(ylabelRight,
                        color=colorRight,
                        fontweight='bold',
                        fontsize=12)
        l0, = axe0.plot(time,
                        yLeft,
                        marker='o',
                        markersize=1,
                        color=colorLeft,
                        )
        l1, = axe1.plot(time,
                        yRight,
                        marker='o',
                        markersize=1,
                        color=colorRight,
                        )
        axe0.set_ylim(-0.4, 0.4)
        axe1.set_ylim(-4, 4)
        axe0.grid(True, color=colorGrid, alpha=0.5)
        legend = axe0.legend([l0, l1],
                             [ylabelLeft, ylabelRight],
                             facecolor='#000000',
                             edgecolor='#2090C0',
                             fontsize='large',
                             )
        for text in legend.get_texts():
            text.set_color('#2090C0')

        return True

    def drawMeasureEnvironment(self):

        if not self.clearPlot(numbAxes=2):
            return False

        axe0 = self.measureMat.figure.axes[0]
        axe1 = self.measureMat.figure.axes[1]

        colorLeft = '#A0A0A0'
        colorRight = '#30B030'
        colorLeft2 = '#B030B0'
        colorTitle = '#2090C0'
        colorGrid = '#404040'
        title = 'Environment'
        ylabelLeft = 'Temperature [°C]'
        ylabelLeft2 = 'Dew Temperature [°C]'
        ylabelRight = 'Pressure [hPas]'

        data = self.app.measure.data
        cycle = self.diagram['cycle'][self.timeIndex]
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        yLeft = data['temp'][start:-1:cycle]
        yLeft2 = data['dewTemp'][start:-1:cycle]
        yRight = data['press'][start:-1:cycle]

        axe0.set_title(title,
                       color=colorTitle,
                       fontweight='bold',
                       fontsize=16)
        axe0.set_xlabel('Time [HH:MM:SS - UTC]',
                        color=colorTitle,
                        fontweight='bold',
                        fontsize=12)
        axe0.set_ylabel(ylabelLeft,
                        color=colorLeft,
                        fontweight='bold',
                        fontsize=12)
        axe1.set_ylabel(ylabelRight,
                        color=colorRight,
                        fontweight='bold',
                        fontsize=12)
        l0, = axe0.plot(time,
                        yLeft,
                        marker='o',
                        markersize=1,
                        color=colorLeft,
                        )
        l1, = axe0.plot(time,
                        yLeft2,
                        marker='o',
                        markersize=1,
                        color=colorLeft2,
                        )
        l2, = axe1.plot(time,
                        yRight,
                        marker='o',
                        markersize=1,
                        color=colorRight,
                        )
        axe0.set_ylim(-10, 25)
        axe1.set_ylim(800, 1050)
        axe0.grid(True, color=colorGrid, alpha=0.5)
        legend = axe0.legend([l0, l1, l2],
                             [ylabelLeft, ylabelLeft2, ylabelRight],
                             facecolor='#000000',
                             edgecolor='#2090C0',
                             )
        for text in legend.get_texts():
            text.set_color('#2090C0')
        return True

    def drawSQR(self):
        if not self.clearPlot(numbAxes=1):
            return False

        axe0 = self.measureMat.figure.axes[0]

        colorLeft = '#A0A0A0'
        colorTitle = '#2090C0'
        colorGrid = '#404040'
        title = 'Sky Quality'
        ylabelLeft = 'Sky Quality [mpas]'

        data = self.app.measure.data
        cycle = self.diagram['cycle'][self.timeIndex]
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        yLeft = data['sqr'][start:-1:cycle]

        axe0.set_title(title,
                       color=colorTitle,
                       fontweight='bold',
                       fontsize=16)
        axe0.set_xlabel('Time [HH:MM:SS - UTC]',
                        color=colorTitle,
                        fontweight='bold',
                        fontsize=12)
        axe0.set_ylabel(ylabelLeft,
                        color=colorLeft,
                        fontweight='bold',
                        fontsize=12)

        l0, = axe0.plot(time,
                        yLeft,
                        marker='o',
                        markersize=1,
                        color=colorLeft,
                        )

        axe0.set_ylim(10, 21)
        axe0.grid(True, color=colorGrid, alpha=0.5)
        legend = axe0.legend([l0],
                             [ylabelLeft],
                             facecolor='#000000',
                             edgecolor='#2090C0',
                             )
        for text in legend.get_texts():
            text.set_color('#2090C0')
        return True

    def drawMeasure(self):
        """

        :return: nothing
        """

        if not self.showStatus:
            return False

        data = self.app.measure.data

        if len(data['time']) == 0:
            for axe in self.measureMat.figure.axes:
                axe.set_visible(False)
            return False

        if not self.mutexDraw.tryLock():
            return False

        cycle = self.diagram['cycle'][self.timeIndex]
        self.timerTask.stop()
        self.timerTask.start(cycle * 1000)

        grid = int(self.NUMBER_POINTS / self.NUMBER_XTICKS)
        ratio = cycle * grid
        time_end = data['time'][-1]

        time_ticks = np.arange(-self.NUMBER_XTICKS, 1, 1)
        time_ticks = time_ticks * ratio * 1000000
        time_ticks = time_ticks + time_end
        time_labels = [x.astype(dt).strftime('%H:%M:%S') for x in time_ticks]

        if self.measureIndex == 0:
            self.drawRaDecStability()
        elif self.measureIndex == 1:
            self.drawMeasureEnvironment()
        elif self.measureIndex == 2:
            self.drawSQR()
        else:
            pass

        for axe in self.measureMat.figure.axes:
            axe.set_xticks(time_ticks)
            axe.set_xticklabels(time_labels)
            axe.set_xlim(time_ticks[0], time_ticks[-1])
            axe.figure.canvas.draw()

        self.mutexDraw.unlock()
