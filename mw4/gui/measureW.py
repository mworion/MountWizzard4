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
        self.measureIndex = 0
        self.timeIndex = 0

        # doing the matplotlib embedding
        self.measureMat = self.embedMatplot(self.ui.measure)
        self.measureMat.parentWidget().setStyleSheet(self.BACK)
        self.clearRect(self.measureMat, True)
        # adding two axes (getting 3 in total)
        self.measureMat.figure.axes[0].twinx()
        self.measureMat.figure.axes[0].twinx()
        self.ui.timeSet.currentIndexChanged.connect(self.drawMeasure)
        self.ui.measureSet.currentIndexChanged.connect(self.drawMeasure)

        mainW = self.app.mainW.ui
        self.clickable(mainW.RA).connect(self.showWindow)
        self.clickable(mainW.DEC).connect(self.showWindow)
        self.clickable(mainW.localTemp).connect(self.showWindow)
        self.clickable(mainW.localPress).connect(self.showWindow)
        self.clickable(mainW.localDewPoint).connect(self.showWindow)
        self.clickable(mainW.SQR).connect(self.showWindow)

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
        self.resize(width, height)
        self.setupButtons()
        self.ui.measureSet.setCurrentIndex(config.get('measureSet', 0))
        self.ui.timeSet.setCurrentIndex(config.get('timeSet', 0))
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
        config['measureSet'] = self.ui.measureSet.currentIndex()
        config['timeSet'] = self.ui.timeSet.currentIndex()
        config['showStatus'] = self.showStatus

        return True

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

        mSet = self.ui.measureSet
        mSet.clear()
        mSet.setView(PyQt5.QtWidgets.QListView())
        mSet.addItem('RaDec Stability')
        mSet.addItem('Environment')
        mSet.addItem('Sky Quality')

        tSet = self.ui.timeSet
        tSet.clear()
        tSet.setView(PyQt5.QtWidgets.QListView())
        tSet.addItem('  8 min')
        tSet.addItem(' 16 min')
        tSet.addItem(' 32 min')
        tSet.addItem('  1 hour')
        tSet.addItem('  2 hours')
        tSet.addItem('  4 hours')
        tSet.addItem('  8 hours')

        return True

    def clearPlot(self, numbAxes=None):
        """

        :param numbAxes: number of axes to be defined and cleared. actual 1 or 2.
        :return: success
        """

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

    def drawRaDecStability(self, data=None, cycle=None):
        """

        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """

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

    def drawMeasureEnvironment(self, data=None, cycle=None):
        """

        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """

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

    def drawSQR(self, data=None, cycle=None):
        """

        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """

        if not self.clearPlot(numbAxes=1):
            return False

        axe0 = self.measureMat.figure.axes[0]

        colorLeft = '#A0A0A0'
        colorTitle = '#2090C0'
        colorGrid = '#404040'
        title = 'Sky Quality'
        ylabelLeft = 'Sky Quality [mpas]'

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

        :return: success
        """

        if not self.showStatus:
            return False

        data = self.app.measure.data
        mIndex = self.ui.measureSet.currentIndex()
        tIndex = self.ui.timeSet.currentIndex()

        if len(data['time']) == 0:
            for axe in self.measureMat.figure.axes:
                axe.set_visible(False)
            return False

        if not self.mutexDraw.tryLock():
            return False

        cycle = 2 ^ tIndex
        self.timerTask.stop()
        self.timerTask.start(cycle * 1000)

        grid = int(self.NUMBER_POINTS / self.NUMBER_XTICKS)
        ratio = cycle * grid
        time_end = data['time'][-1]

        time_ticks = np.arange(-self.NUMBER_XTICKS, 1, 1)
        time_ticks = time_ticks * ratio * 1000000
        time_ticks = time_ticks + time_end
        time_labels = [x.astype(dt).strftime('%H:%M:%S') for x in time_ticks]

        if mIndex == 0:
            self.drawRaDecStability(data=data, cycle=cycle)
        elif mIndex == 1:
            self.drawMeasureEnvironment(data=data, cycle=cycle)
        elif mIndex == 2:
            self.drawSQR(data=data, cycle=cycle)
        else:
            pass

        for axe in self.measureMat.figure.axes:
            axe.set_xticks(time_ticks)
            axe.set_xticklabels(time_labels)
            axe.set_xlim(time_ticks[0], time_ticks[-1])
            axe.figure.canvas.draw()

        self.mutexDraw.unlock()
        return True
