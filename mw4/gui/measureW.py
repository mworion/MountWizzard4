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
from matplotlib import ticker
# local import
from mw4.gui import widget
from mw4.gui.widgets import measure_ui


class MeasureWindow(widget.MWidget):
    """
    the measure window class handles

    """

    __all__ = ['MeasureWindow',
               ]
    version = '0.5'
    logger = logging.getLogger(__name__)

    NUMBER_POINTS = 500
    NUMBER_XTICKS = 8

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = measure_ui.Ui_MeasureDialog()
        self.ui.setupUi(self)
        self.initUI()
        self.refreshCounter = 1

        self.mSetUI = [self.ui.measureSet1,
                       self.ui.measureSet2,
                       self.ui.measureSet3,
                       ]

        self.plotFunc = {'None': None,
                         'RA Stability': self.plotRa,
                         'DEC Stability': self.plotDec,
                         'Temperature': self.plotTemperature,
                         'Pressure': self.plotPressure,
                         'Humidity': self.plotHumidity,
                         'Sky Quality': self.plotSQR,
                         'Voltage': self.plotVoltage,
                         'Current': self.plotCurrent,
                         }

        self.timeScale = {'  8 min': 1,
                          ' 16 min': 2,
                          ' 32 min': 4,
                          '  1 hour': 8,
                          '  2 hours': 16,
                          '  4 hours': 32,
                          '  8 hours': 64,
                          }

        self.mutexDraw = PyQt5.QtCore.QMutex()
        self.measureIndex = 0
        self.timeIndex = 0

        # doing the matplotlib embedding
        self.measureMat = self.embedMatplot(self.ui.measure)
        self.measureMat.parentWidget().setStyleSheet(self.BACK_BG)

        self.initConfig()
        self.showWindow()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

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
        self.ui.measureSet1.setCurrentIndex(config.get('measureSet1', 0))
        self.ui.measureSet2.setCurrentIndex(config.get('measureSet2', 0))
        self.ui.measureSet3.setCurrentIndex(config.get('measureSet3', 0))
        self.ui.timeSet.setCurrentIndex(config.get('timeSet', 0))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        if 'measureW' not in self.app.config:
            self.app.config['measureW'] = {}
        config = self.app.config['measureW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()
        config['measureSet1'] = self.ui.measureSet1.currentIndex()
        config['measureSet2'] = self.ui.measureSet2.currentIndex()
        config['measureSet3'] = self.ui.measureSet3.currentIndex()
        config['timeSet'] = self.ui.timeSet.currentIndex()

        return True

    def closeEvent(self, closeEvent):
        """

        :param closeEvent:
        :return:
        """

        self.storeConfig()
        # signals for gui
        self.ui.timeSet.currentIndexChanged.disconnect(self.setCycleRefresh)
        self.ui.measureSet1.currentIndexChanged.disconnect(self.setCycleRefresh)
        self.ui.measureSet2.currentIndexChanged.disconnect(self.setCycleRefresh)
        self.ui.measureSet3.currentIndexChanged.disconnect(self.setCycleRefresh)
        self.app.update1s.disconnect(self.setCycleRefresh)

        self.measureMat.figure = None

        super().closeEvent(closeEvent)

    def showWindow(self):
        """

        :return:
        """
        self.drawMeasure()
        self.show()

        # signals for gui
        self.ui.timeSet.currentIndexChanged.connect(self.setCycleRefresh)
        self.ui.measureSet1.currentIndexChanged.connect(self.setCycleRefresh)
        self.ui.measureSet2.currentIndexChanged.connect(self.setCycleRefresh)
        self.ui.measureSet3.currentIndexChanged.connect(self.setCycleRefresh)
        self.app.update1s.connect(self.setCycleRefresh)
        return True

    def setupButtons(self):
        """
        setupButtons prepares the dynamic content od the buttons in measurement window. it
        write the bottom texts and number as well as the coloring for the actual setting

        :return: success for test purpose
        """

        for mSet in self.mSetUI:
            mSet.clear()
            mSet.setView(PyQt5.QtWidgets.QListView())
            for text in self.plotFunc.keys():
                mSet.addItem(text)

        tSet = self.ui.timeSet
        tSet.clear()
        tSet.setView(PyQt5.QtWidgets.QListView())
        for text in self.timeScale.keys():
            tSet.addItem(text)

        return True

    def setCycleRefresh(self):
        """

        :return: True for test purpose
        """

        cycle = self.timeScale[self.ui.timeSet.currentText()]
        if not self.refreshCounter % cycle:
            self.drawMeasure(cycle)
        self.refreshCounter += 1

    def setupAxes(self, figure=None, numberPlots=3):
        """
        setupAxes cleans up the axes object in figure an setup a new plotting. it draws
        grid, ticks etc.

        :param numberPlots:
        :param figure: axes object of figure
        :return:
        """

        if figure is None:
            return False
        if numberPlots > 3:
            return False
        if numberPlots < 0:
            return False

        figure.clf()
        figure.subplots_adjust(left=0.1, right=0.95, bottom=0.05, top=0.95)
        for i in range(numberPlots):
            self.measureMat.figure.add_subplot(numberPlots, 1, i + 1, facecolor=None)

        for axe in figure.axes:
            axe.set_facecolor((0, 0, 0, 0))
            axe.tick_params(colors=self.M_BLUE,
                            labelsize=12)
            axe.spines['bottom'].set_color(self.M_BLUE)
            axe.spines['top'].set_color(self.M_BLUE)
            axe.spines['left'].set_color(self.M_BLUE)
            axe.spines['right'].set_color(self.M_BLUE)

        return figure.axes

    def plotRa(self, axe=None, title='', data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'delta RA [arcsec]'
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        m = data['raJNow'][start:-1:cycle]
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(time,
                 m,
                 marker='o',
                 markersize=1,
                 color=self.M_WHITE,
                 )
        axe.grid(True, color=self.M_GREY, alpha=1)
        axe.set_ylim(-0.4, 0.4)
        axe.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                             integer=True,
                                                             min_n_ticks=4,
                                                             prune='both',
                                                             ))
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                      ))
        return True

    def plotDec(self, axe=None, title='', data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'delta DEC [arcsec]'
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        m = data['decJNow'][start:-1:cycle]
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(time,
                 m,
                 marker='o',
                 markersize=1,
                 color=self.M_WHITE,
                 )
        axe.grid(True, color=self.M_GREY, alpha=1)
        axe.set_ylim(-4, 4)
        axe.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                             integer=True,
                                                             min_n_ticks=4,
                                                             prune='both',
                                                             ))
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                      ))
        return True

    def plotTemperature(self, axe=None, title='', data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Temperature [°C]'
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        m1 = data['envTemp'][start:-1:cycle]
        m2 = data['powTemp'][start:-1:cycle]
        m3 = data['skyTemp'][start:-1:cycle]
        m4 = data['envDew'][start:-1:cycle]
        m5 = data['powDew'][start:-1:cycle]

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        r1, = axe.plot(time,
                       m1,
                       marker='o',
                       markersize=1,
                       color=self.M_WHITE,
                       )
        r2, = axe.plot(time,
                       m2,
                       marker='o',
                       markersize=1,
                       color=self.M_PINK,
                       )
        r3, = axe.plot(time,
                       m3,
                       marker='o',
                       markersize=1,
                       color=self.M_YELLOW,
                       )
        r4, = axe.plot(time,
                       m4,
                       marker='o',
                       markersize=1,
                       color=self.M_GREEN,
                       )
        r5, = axe.plot(time,
                       m5,
                       marker='o',
                       markersize=1,
                       color=self.M_RED,
                       )
        legend = axe.legend([r1, r2, r3, r4, r5],
                            ['Env Temp', 'Pow Temp', 'Sky Temp', 'Env Dew', 'Pow Dew'],
                            facecolor=self.M_BLACK,
                            edgecolor=self.M_BLUE,
                            )
        for text in legend.get_texts():
            text.set_color(self.M_BLUE)
        axe.grid(True, color=self.M_GREY, alpha=1)
        axe.margins(y=0.2)
        axe.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                             integer=True,
                                                             min_n_ticks=4,
                                                             prune='both',
                                                             ))
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                      ))
        return True

    def plotPressure(self, axe=None, title='', data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Pressure [hPas]'
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        m = data['envPress'][start:-1:cycle]
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(time,
                 m,
                 marker='o',
                 markersize=1,
                 color=self.M_WHITE,
                 )
        axe.grid(True, color=self.M_GREY, alpha=1)
        axe.margins(y=0.2)
        axe.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                             integer=True,
                                                             min_n_ticks=4,
                                                             prune='both',
                                                             ))
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.0f',
                                                                      ))
        return True

    def plotHumidity(self, axe=None, title='', data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Humidity [%]'
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        m1 = data['envHum'][start:-1:cycle]
        m2 = data['powHum'][start:-1:cycle]

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        r1, = axe.plot(time,
                       m1,
                       marker='o',
                       markersize=1,
                       color=self.M_WHITE,
                       )
        r2, = axe.plot(time,
                       m2,
                       marker='o',
                       markersize=1,
                       color=self.M_PINK,
                       )
        legend = axe.legend([r1, r2],
                            ['Env Hum', 'Pow Hum'],
                            facecolor=self.M_BLACK,
                            edgecolor=self.M_BLUE,
                            )
        for text in legend.get_texts():
            text.set_color(self.M_BLUE)
        axe.grid(True, color=self.M_GREY, alpha=1)
        axe.set_ylim(-0, 100)
        axe.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                             integer=True,
                                                             min_n_ticks=4,
                                                             prune='both',
                                                             ))
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.0f',
                                                                      ))
        return True

    def plotSQR(self, axe=None, title='', data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Sky Quality [mpas]'
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        m = data['skySQR'][start:-1:cycle]
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(time,
                 m,
                 marker='o',
                 markersize=1,
                 color=self.M_WHITE,
                 )
        axe.grid(True, color=self.M_GREY, alpha=1)
        axe.margins(y=0.2)
        axe.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                             integer=True,
                                                             min_n_ticks=4,
                                                             prune='both',
                                                             ))
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                      ))
        return True

    def plotVoltage(self, axe=None, title='', data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Power Voltage on Rack [V]'
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        m = data['powVolt'][start:-1:cycle]
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(time,
                 m,
                 marker='o',
                 markersize=1,
                 color=self.M_WHITE,
                 )
        axe.grid(True, color=self.M_GREY, alpha=1)
        axe.margins(y=0.2)
        axe.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                             integer=True,
                                                             min_n_ticks=4,
                                                             prune='both',
                                                             ))
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                      ))
        return True

    def plotCurrent(self, axe=None, title='', data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Power Current [A]'
        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        m1 = data['powCurr'][start:-1:cycle]
        m2 = data['powCurr1'][start:-1:cycle]
        m3 = data['powCurr2'][start:-1:cycle]
        m4 = data['powCurr3'][start:-1:cycle]
        m5 = data['powCurr4'][start:-1:cycle]

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        r1, = axe.plot(time,
                       m1,
                       marker='o',
                       markersize=1,
                       color=self.M_WHITE,
                       )
        r2, = axe.plot(time,
                       m2,
                       marker='o',
                       markersize=1,
                       color=self.M_PINK,
                       )
        r3, = axe.plot(time,
                       m3,
                       marker='o',
                       markersize=1,
                       color=self.M_YELLOW,
                       )
        r4, = axe.plot(time,
                       m4,
                       marker='o',
                       markersize=1,
                       color=self.M_GREEN,
                       )
        r5, = axe.plot(time,
                       m5,
                       marker='o',
                       markersize=1,
                       color=self.M_RED,
                       )
        legend = axe.legend([r1, r2, r3, r4, r5],
                            ['Curr Sum', 'Curr P1', 'Curr P2', 'Curr P3', 'Curr P4'],
                            facecolor=self.M_BLACK,
                            edgecolor=self.M_BLUE,
                            )
        for text in legend.get_texts():
            text.set_color(self.M_BLUE)
        axe.grid(True, color=self.M_GREY, alpha=1)
        axe.margins(y=0.2)
        axe.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                             integer=True,
                                                             min_n_ticks=4,
                                                             prune='both',
                                                             ))
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                      ))
        return True

    def drawMeasure(self, cycle=1):
        """
        drawMeasure does the basic preparation for making the plot. it checks for borders
        and does finally the content dispatcher. currently there is no chance to implement
        a basic pattern as the graphs differ heavily.

        :param cycle:
        :return: success
        """

        data = self.app.measure.data

        if len(data['time']) < 4:
            return False

        numberPlots = 0
        for mSet in self.mSetUI:
            if mSet.currentText() == 'None':
                continue
            numberPlots += 1

        axes = self.setupAxes(figure=self.measureMat.figure, numberPlots=numberPlots)
        if not numberPlots:
            self.measureMat.figure.canvas.draw()
            return False

        grid = int(self.NUMBER_POINTS / self.NUMBER_XTICKS)
        ratio = cycle * grid
        time_end = data['time'][-1]

        time_ticks = np.arange(-self.NUMBER_XTICKS, 1, 1)
        time_ticks = time_ticks * ratio * 1000000
        time_ticks = time_ticks + time_end
        time_labels = [x.astype(dt).strftime('%H:%M:%S') for x in time_ticks]

        for axe, mSet in zip(axes, self.mSetUI):
            key = mSet.currentText()
            if self.plotFunc[key] is None:
                continue
            self.plotFunc[key](axe=axe,
                               title=mSet.currentText(),
                               data=data,
                               cycle=cycle)

        for i, axe in enumerate(axes):
            axe.set_xticks(time_ticks)
            axe.set_xlim(time_ticks[0], time_ticks[-1])
            if i == len(axes) - 1:
                axe.set_xticklabels(time_labels)
            else:
                axe.set_xticklabels([])
            axe.figure.canvas.draw()

        return True
