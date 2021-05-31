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
#
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from datetime import datetime as dt
import gc

# external packages
import PyQt5
import numpy as np
from matplotlib import ticker
import matplotlib.pyplot as plt

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import measure_ui


class MeasureWindow(toolsQtWidget.MWidget):
    """
    the measure window class handles

    """

    __all__ = ['MeasureWindow',
               ]

    NUMBER_POINTS = 250
    NUMBER_XTICKS = 5

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = measure_ui.Ui_MeasureDialog()
        self.ui.setupUi(self)
        self.refreshCounter = 1
        self.measureIndex = 0
        self.timeIndex = 0

        self.mSetUI = [self.ui.measureSet1,
                       self.ui.measureSet2,
                       self.ui.measureSet3,
                       ]

        self.plotFunc = {'No chart': None,
                         'RA Stability': self.plotRa,
                         'DEC Stability': self.plotDec,
                         'RA Angular Stability': self.plotAngularPosRa,
                         'DEC Angular Stability': self.plotAngularPosDec,
                         'Temperature': self.plotTemperature,
                         'Pressure': self.plotPressure,
                         'Humidity': self.plotHumidity,
                         'Sky Quality': self.plotSQR,
                         'Voltage': self.plotVoltage,
                         'Current': self.plotCurrent,
                         }

        self.timeScale = {'  1s Tick   -  4 min window': 1,
                          '  2s Ticks  -  8 min window': 2,
                          '  4s Ticks  - 16 min window': 4,
                          '  8s Ticks  - 32 min window': 8,
                          ' 16s Ticks  -  1 hour window': 16,
                          ' 32s Ticks  -  2 hours window': 32,
                          ' 64s Ticks  -  4 hours window': 64,
                          '128s Ticks  -  9 hours window': 128,
                          }

        self.measureMat = self.embedMatplot(self.ui.measure, constrainedLayout=False)
        self.measureMat.parentWidget().setStyleSheet(self.BACK_BG)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'measureW' not in self.app.config:
            self.app.config['measureW'] = {}
        config = self.app.config['measureW']
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)
        self.setupButtons()
        self.ui.measureSet1.setCurrentIndex(config.get('measureSet1', 0))
        self.ui.measureSet2.setCurrentIndex(config.get('measureSet2', 0))
        self.ui.measureSet3.setCurrentIndex(config.get('measureSet3', 0))
        self.ui.timeSet.setCurrentIndex(config.get('timeSet', 0))
        self.setCycleRefresh()
        return True

    def storeConfig(self):
        """
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

    def showWindow(self):
        """
        :return:
        """
        self.show()
        self.ui.timeSet.currentIndexChanged.connect(self.setCycleRefresh)
        self.ui.measureSet1.currentIndexChanged.connect(self.setCycleRefresh)
        self.ui.measureSet2.currentIndexChanged.connect(self.setCycleRefresh)
        self.ui.measureSet3.currentIndexChanged.connect(self.setCycleRefresh)
        self.app.update1s.connect(self.cycleRefresh)
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.app.update1s.disconnect(self.cycleRefresh)
        self.storeConfig()
        self.ui.timeSet.currentIndexChanged.disconnect(self.setCycleRefresh)
        self.ui.measureSet1.currentIndexChanged.disconnect(self.setCycleRefresh)
        self.ui.measureSet2.currentIndexChanged.disconnect(self.setCycleRefresh)
        self.ui.measureSet3.currentIndexChanged.disconnect(self.setCycleRefresh)
        plt.close(self.measureMat.figure)
        super().closeEvent(closeEvent)

    def setupButtons(self):
        """
        setupButtons prepares the dynamic content od the buttons in measurement
        window. it write the bottom texts and number as well as the coloring for
        the actual setting

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
        fallback = list(self.timeScale.keys())[0]
        self.refreshCounter = self.timeScale.get(self.ui.timeSet.currentText(),
                                                 fallback)
        self.cycleRefresh()
        return True

    def cycleRefresh(self):
        """
        :return: True for test purpose
        """
        cycle = self.timeScale.get(self.ui.timeSet.currentText(), 1)
        if not self.refreshCounter % cycle:
            self.drawMeasure(cycle=cycle)

        self.refreshCounter += 1
        return True

    def setupAxes(self, figure=None, numberPlots=3):
        """
        :param numberPlots:
        :param figure: axes object of figure
        :return:
        """
        if figure is None:
            return None
        if numberPlots > 3:
            return None
        if numberPlots < 0:
            return None

        for axe in figure.axes:
            axe.cla()
            gc.collect()

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
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Delta RA [arcsec]'
        start = -self.NUMBER_POINTS * cycle
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(data['time'][start:-1:cycle],
                 data['deltaRaJNow'][start:-1:cycle],
                 marker=None,
                 markersize=3,
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

    def plotDec(self, axe=None, title='', data=None, cycle=None):
        """
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Delta DEC [arcsec]'
        start = -self.NUMBER_POINTS * cycle
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(data['time'][start:-1:cycle],
                 data['deltaDecJNow'][start:-1:cycle],
                 marker=None,
                 markersize=3,
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

    def plotAngularPosRa(self, axe=None, title='', data=None, cycle=None):
        """
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Delta RA Angular [arcsec]'
        start = -self.NUMBER_POINTS * cycle
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(data['time'][start:-1:cycle],
                 data['deltaAngularPosRA'][start:-1:cycle],
                 marker=None,
                 markersize=3,
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

    def plotAngularPosDec(self, axe=None, title='', data=None, cycle=None):
        """
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Delta DEC Angular [arcsec]'
        start = -self.NUMBER_POINTS * cycle
        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        axe.plot(data['time'][start:-1:cycle],
                 data['deltaAngularPosDEC'][start:-1:cycle],
                 marker=None,
                 markersize=3,
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
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Temperature [deg C]'
        start = -self.NUMBER_POINTS * cycle

        plotList = []
        labelList = []

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        if 'sensorWeather' in self.app.measure.devices:
            r1, = axe.plot(data['time'][start:-1:cycle],
                           data['sensorWeatherTemp'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_WHITE,
                           )
            r2, = axe.plot(data['time'][start:-1:cycle],
                           data['sensorWeatherDew'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           linestyle=':',
                           color=self.M_WHITE,
                           )
            plotList.append(r1)
            plotList.append(r2)
            labelList.append('Sensor Temp')
            labelList.append('Sensor Dew')

        if 'onlineWeather' in self.app.measure.devices:
            r3, = axe.plot(data['time'][start:-1:cycle],
                           data['onlineWeatherTemp'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_GREEN,
                           )
            r4, = axe.plot(data['time'][start:-1:cycle],
                           data['onlineWeatherDew'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           linestyle=':',
                           color=self.M_GREEN,
                           )
            plotList.append(r3)
            plotList.append(r4)
            labelList.append('Online Temp')
            labelList.append('Online Dew')

        if 'directWeather' in self.app.measure.devices:
            r5, = axe.plot(data['time'][start:-1:cycle],
                           data['directWeatherTemp'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_RED,
                           )
            r6, = axe.plot(data['time'][start:-1:cycle],
                           data['directWeatherDew'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           linestyle=':',
                           color=self.M_RED,
                           )
            plotList.append(r5)
            plotList.append(r6)
            labelList.append('Direct Temp')
            labelList.append('Direct Dew')

        if 'power' in self.app.measure.devices:
            r7, = axe.plot(data['time'][start:-1:cycle],
                           data['powTemp'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_PINK,
                           )
            r8, = axe.plot(data['time'][start:-1:cycle],
                           data['powDew'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           linestyle=':',
                           color=self.M_PINK,
                           )
            plotList.append(r7)
            plotList.append(r8)
            labelList.append('Power Temp')
            labelList.append('Power Dew')

        if 'skymeter' in self.app.measure.devices:
            r9, = axe.plot(data['time'][start:-1:cycle],
                           data['skyTemp'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_YELLOW,
                           )
            plotList.append(r9)
            labelList.append('Skymeter Temp')

        if not labelList:
            return False

        legend = axe.legend(plotList, labelList,
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
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Pressure [hPas]'
        start = -self.NUMBER_POINTS * cycle

        plotList = []
        labelList = []

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        if 'sensorWeather' in self.app.measure.devices:
            r1, = axe.plot(data['time'][start:-1:cycle],
                           data['sensorWeatherPress'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_WHITE,
                           )
            plotList.append(r1)
            labelList.append('Sensor Temp')

        if 'onlineWeather' in self.app.measure.devices:
            r2, = axe.plot(data['time'][start:-1:cycle],
                           data['onlineWeatherPress'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_GREEN,
                           )
            plotList.append(r2)
            labelList.append('Online Press')

        if 'directWeather' in self.app.measure.devices:
            r3, = axe.plot(data['time'][start:-1:cycle],
                           data['directWeatherPress'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_RED,
                           )
            plotList.append(r3)
            labelList.append('Direct Press')

        if not labelList:
            return False

        legend = axe.legend(plotList, labelList,
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
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.0f',
                                                                      ))
        return True

    def plotHumidity(self, axe=None, title='', data=None, cycle=None):
        """
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Humidity [%]'
        start = -self.NUMBER_POINTS * cycle

        plotList = []
        labelList = []

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        if 'sensorWeather' in self.app.measure.devices:
            r1, = axe.plot(data['time'][start:-1:cycle],
                           data['sensorWeatherHum'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_WHITE,
                           )
            plotList.append(r1)
            labelList.append('Sensor Hum')

        if 'onlineWeather' in self.app.measure.devices:
            r2, = axe.plot(data['time'][start:-1:cycle],
                           data['onlineWeatherHum'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_GREEN,
                           )
            plotList.append(r2)
            labelList.append('Online Hum')

        if 'directWeather' in self.app.measure.devices:
            r3, = axe.plot(data['time'][start:-1:cycle],
                           data['directWeatherHum'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_RED,
                           )
            plotList.append(r3)
            labelList.append('Direct Hum')

        if 'power' in self.app.measure.devices:
            r4, = axe.plot(data['time'][start:-1:cycle],
                           data['powHum'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_PINK,
                           )
            plotList.append(r4)
            labelList.append('Power Hum')

        if not labelList:
            return False

        legend = axe.legend(plotList, labelList,
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
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Sky Quality [mpas]'
        start = -self.NUMBER_POINTS * cycle

        plotList = []
        labelList = []

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        if 'skymeter' in self.app.measure.devices:
            r1, = axe.plot(data['time'][start:-1:cycle],
                           data['skySQR'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_WHITE,
                           )
            plotList.append(r1)
            labelList.append('Skymeter SQR')

        if not labelList:
            return False

        legend = axe.legend(plotList, labelList,
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
        axe.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.2f',
                                                                      ))
        return True

    def plotVoltage(self, axe=None, title='', data=None, cycle=None):
        """
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Power Voltage [V]'
        start = -self.NUMBER_POINTS * cycle

        plotList = []
        labelList = []

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)
        if 'power' in self.app.measure.devices:
            r1, = axe.plot(data['time'][start:-1:cycle],
                           data['powVolt'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_WHITE,
                           )
            plotList.append(r1)
            labelList.append('Voltage')

        if not labelList:
            return False

        legend = axe.legend(plotList, labelList,
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

    def plotCurrent(self, axe=None, title='', data=None, cycle=None):
        """
        :param axe: axe for plotting
        :param title: title text
        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """
        ylabel = 'Power Current [A]'
        start = -self.NUMBER_POINTS * cycle

        plotList = []
        labelList = []

        axe.set_title(title,
                      color=self.M_BLUE,
                      fontweight='bold',
                      fontsize=16)
        axe.set_ylabel(ylabel,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=12)

        if 'power' in self.app.measure.devices:
            r1, = axe.plot(data['time'][start:-1:cycle],
                           data['powCurr'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_WHITE,
                           )
            r2, = axe.plot(data['time'][start:-1:cycle],
                           data['powCurr1'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_PINK,
                           )
            r3, = axe.plot(data['time'][start:-1:cycle],
                           data['powCurr2'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_YELLOW,
                           )
            r4, = axe.plot(data['time'][start:-1:cycle],
                           data['powCurr3'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_GREEN,
                           )
            r5, = axe.plot(data['time'][start:-1:cycle],
                           data['powCurr4'][start:-1:cycle],
                           marker=None,
                           markersize=3,
                           color=self.M_RED,
                           )
            plotList.append(r1)
            plotList.append(r2)
            plotList.append(r3)
            plotList.append(r4)
            plotList.append(r5)
            labelList.append('Curr Sum')
            labelList.append('Curr 1')
            labelList.append('Curr 2')
            labelList.append('Curr 3')
            labelList.append('Curr 4')

        if not labelList:
            return False

        legend = axe.legend(plotList, labelList,
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
        :param cycle:
        :return: success
        """
        data = self.app.measure.data

        if 'time' not in data:
            return False
        if len(data['time']) < 4:
            return False

        numberPlots = 0
        for mSet in self.mSetUI:
            if mSet.currentText() == 'No chart':
                continue
            numberPlots += 1

        axes = self.setupAxes(figure=self.measureMat.figure, numberPlots=numberPlots)

        if axes is None:
            return False
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

        for i, axe in enumerate(axes):
            axe.set_xticks(time_ticks)
            axe.set_xlim(time_ticks[0], time_ticks[-1])

            if i == len(axes) - 1:
                axe.set_xticklabels(time_labels)

            else:
                axe.set_xticklabels([])

        for axe, mSet in zip(axes, self.mSetUI):
            key = mSet.currentText()

            if self.plotFunc[key] is None:
                continue

            self.plotFunc[key](axe=axe,
                               title=mSet.currentText(),
                               data=data,
                               cycle=cycle)
            axe.figure.canvas.draw()
        return True
