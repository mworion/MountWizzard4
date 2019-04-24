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
    version = '0.3'
    logger = logging.getLogger(__name__)

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
        self.ui.timeSet.currentIndexChanged.disconnect(self.drawMeasure)
        self.ui.measureSet1.currentIndexChanged.disconnect(self.drawMeasure)
        self.ui.measureSet2.currentIndexChanged.disconnect(self.drawMeasure)
        self.ui.measureSet3.currentIndexChanged.disconnect(self.drawMeasure)
        self.app.update1s.disconnect(self.drawMeasure)

        super().closeEvent(closeEvent)

    def showWindow(self):
        """

        :return:
        """
        self.drawMeasure()
        self.show()

        # signals for gui
        self.ui.timeSet.currentIndexChanged.connect(self.drawMeasure)
        self.ui.measureSet1.currentIndexChanged.connect(self.drawMeasure)
        self.ui.measureSet2.currentIndexChanged.connect(self.drawMeasure)
        self.ui.measureSet3.currentIndexChanged.connect(self.drawMeasure)
        self.app.update1s.connect(self.drawMeasure)
        return True

    def setupButtons(self):
        """
        setupButtons prepares the dynamic content od the buttons in measurement window. it
        write the bottom texts and number as well as the coloring for the actual setting

        :return: success for test purpose
        """

        mSetUI = [self.ui.measureSet1,
                  self.ui.measureSet2,
                  self.ui.measureSet3,
                  ]

        for mSet in mSetUI:
            mSet.clear()
            mSet.setView(PyQt5.QtWidgets.QListView())
            mSet.addItem('None')
            mSet.addItem('RA Stability')
            mSet.addItem('DEC Stability')
            mSet.addItem('Temperature')
            mSet.addItem('Pressure')
            mSet.addItem('Humidity')
            mSet.addItem('Sky Quality')
            mSet.addItem('Voltage')
            mSet.addItem('Current')
            mSet.addItem('Memory Hemisphere')
            mSet.addItem('Memory Image')
            mSet.addItem('Memory Measure')

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

    def clearPlot(self, numberPlots=None):
        """
        clearPlot deletes the content of the axes and renews the basic setting for grid,
        color, spines etc.

        :param numberPlots: number of subplots to be defined and cleared. actual 1 to 3.
        :return: success
        """

        suc = self.clearRect(self.measureMat,
                             numberPlots=numberPlots)
        if not suc:
            return False

        fig = self.measureMat.figure

        fig.subplots_adjust(left=0.1,
                            right=0.95,
                            bottom=0.05,
                            top=0.95,
                            )

        for i, axe in enumerate(fig.axes):
            axe.cla()
            axe.set_facecolor((0, 0, 0, 0))
            axe.tick_params(colors=self.M_BLUE,
                            labelsize=12)
            axe.spines['bottom'].set_color(self.M_BLUE)
            axe.spines['top'].set_color(self.M_BLUE)
            axe.spines['left'].set_color(self.M_BLUE)
            axe.spines['right'].set_color(self.M_BLUE)

        return True

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

    def drawPlots(self, axe=None, index=0, title='', data=None, cycle=0):
        """

        :param axe:
        :param index:
        :param title:
        :param data:
        :param cycle:
        :return: success
        """
        plotFunc = [None,
                    self.plotRa,
                    self.plotDec,
                    self.plotTemperature,
                    self.plotPressure,
                    self.plotHumidity,
                    self.plotSQR,
                    self.plotVoltage,
                    self.plotCurrent,
                    ]

        if plotFunc[index] is None:
            return False

        plotFunc[index](axe=axe, title=title, data=data, cycle=cycle)

        return True

    def drawMeasure(self):
        """
        drawMeasure does the basic preparation for making the plot. it checks for borders
        and does finally the content dispatcher. currently there is no chance to implement
        a basic pattern as the graphs differ heavily.

        :return: success
        """

        data = self.app.measure.data
        cycle = int(np.exp2(self.ui.timeSet.currentIndex()))

        if len(data['time']) < 4:
            return False

        if not self.clearPlot(numberPlots=3):
            return False

        grid = int(self.NUMBER_POINTS / self.NUMBER_XTICKS)
        ratio = cycle * grid
        time_end = data['time'][-1]

        time_ticks = np.arange(-self.NUMBER_XTICKS, 1, 1)
        time_ticks = time_ticks * ratio * 1000000
        time_ticks = time_ticks + time_end
        time_labels = [x.astype(dt).strftime('%H:%M:%S') for x in time_ticks]

        mIndex = [self.ui.measureSet1.currentIndex(),
                  self.ui.measureSet2.currentIndex(),
                  self.ui.measureSet3.currentIndex(),
                  ]
        mTitle = [self.ui.measureSet1.currentText(),
                  self.ui.measureSet2.currentText(),
                  self.ui.measureSet3.currentText(),
                  ]

        for axe, index, title in zip(self.measureMat.figure.axes, mIndex, mTitle):
            self.drawPlots(axe=axe, index=index, title=title, data=data, cycle=cycle)

        for i, axe in enumerate(self.measureMat.figure.axes):
            axe.set_xticks(time_ticks)
            axe.set_xlim(time_ticks[0], time_ticks[-1])
            if i == 2:
                axe.set_xticklabels(time_labels)
            else:
                axe.set_xticklabels([])
            axe.figure.canvas.draw()

        return True
