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
    version = '0.2'
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

        # signals for gui
        self.ui.timeSet.currentIndexChanged.connect(self.drawMeasure)
        self.ui.measureSet.currentIndexChanged.connect(self.drawMeasure)
        self.clickable(self.app.mainW.ui.RA).connect(self.showWindow)
        self.clickable(self.app.mainW.ui.DEC).connect(self.showWindow)
        self.clickable(self.app.mainW.ui.environTemp).connect(self.showWindow)
        self.clickable(self.app.mainW.ui.environPress).connect(self.showWindow)
        self.clickable(self.app.mainW.ui.environDewPoint).connect(self.showWindow)
        self.clickable(self.app.mainW.ui.skymeterSQR).connect(self.showWindow)

        self.app.update1s.connect(self.drawMeasure)

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
        if self.app.mainW.ui.measureDevice.currentIndex() == 0:
            self.showStatus = False
            return False
        self.showStatus = True
        suc = self.drawMeasure()
        self.show()
        return suc

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

    def clearPlot(self, numberPlots=None):
        """
        clearPlot deletes the content of the axes and renews the basic setting for grid,
        color, spines etc.

        :param numberPlots: number of subplots to be defined and cleared. actual 1 to 2.
        :return: success
        """

        suc = self.clearRect(self.measureMat,
                             numberPlots=numberPlots)
        if not suc:
            return False

        fig = self.measureMat.figure

        fig.subplots_adjust(left=0.11,
                            right=0.95,
                            bottom=0.1,
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

    def drawRaDec(self, data=None, cycle=None):
        """
        drawRaDec show the specific graph for plotting the ra dec deviations. this
        is done with two color and axes to distinguish the values for ra and dec.
        ideally the values are around zero, but the scales of ra and dec axis have to be
        different.

        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """

        if not self.clearPlot(numberPlots=2):
            return False

        axe0 = self.measureMat.figure.axes[0]
        axe1 = self.measureMat.figure.axes[1]

        title = 'RaDec Stability'
        ylabelLeft = 'delta RA [arcsec]'
        ylabelRight = 'delta DEC [arcsec]'

        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        mLeft = data['raJNow'][start:-1:cycle]
        mRight = data['decJNow'][start:-1:cycle]

        axe0.set_title(title,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=16)
        axe1.set_xlabel('Time [HH:MM:SS - UTC]',
                        color=self.M_BLUE,
                        fontweight='bold',
                        fontsize=12)

        axe0.set_ylabel(ylabelLeft,
                        color=self.M_WHITE,
                        fontweight='bold',
                        fontsize=12)
        axe1.set_ylabel(ylabelRight,
                        color=self.M_GREEN,
                        fontweight='bold',
                        fontsize=12)

        axe0.plot(time,
                  mLeft,
                  marker='o',
                  markersize=1,
                  color=self.M_WHITE,
                  )
        axe1.plot(time,
                  mRight,
                  marker='o',
                  markersize=1,
                  color=self.M_GREEN,
                  )

        axe0.grid(True, color=self.M_GREY, alpha=1)
        axe1.grid(True, color=self.M_GREY, alpha=1)
        axe0.set_xticklabels([])
        axe0.set_ylim(-0.4, 0.4)
        axe1.set_ylim(-4, 4)

        axe0.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                              integer=True,
                                                              min_n_ticks=4,
                                                              prune='both',
                                                              ))
        axe0.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                       ))

        axe1.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                              integer=True,
                                                              min_n_ticks=4,
                                                              prune='both',
                                                              ))
        axe1.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                       ))

        return True

    def drawEnvironment(self, data=None, cycle=None):
        """
        drawEnvironment show the specific graph for plotting the temps, pressure
        and humidity deviations. this is done with two color and axes to distinguish the
        ranges.

        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """

        if not self.clearPlot(numberPlots=2):
            return False

        axe0 = self.measureMat.figure.axes[0]
        axe1 = self.measureMat.figure.axes[1]

        title = 'Environment'
        ylabelLeft = 'Pressure [hPas]'
        ylabelRight = 'Temperature / DewTemp [°C]'

        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        mLeft = data['press'][start:-1:cycle]
        mRight1 = data['temp'][start:-1:cycle]
        mRight2 = data['dewTemp'][start:-1:cycle]

        axe0.set_title(title,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=16)
        axe1.set_xlabel('Time [HH:MM:SS - UTC]',
                        color=self.M_BLUE,
                        fontweight='bold',
                        fontsize=12)

        axe0.set_ylabel(ylabelLeft,
                        color=self.M_GREEN,
                        fontweight='bold',
                        fontsize=12)
        axe1.set_ylabel(ylabelRight,
                        color=self.M_WHITE,
                        fontweight='bold',
                        fontsize=12)

        axe0.plot(time,
                  mLeft,
                  marker='o',
                  markersize=1,
                  color=self.M_GREEN,
                  )
        axe1.plot(time,
                  mRight1,
                  marker='o',
                  markersize=1,
                  color=self.M_WHITE,
                  )
        axe1.plot(time,
                  mRight2,
                  marker='o',
                  markersize=1,
                  color=self.M_PINK,
                  )

        axe0.grid(True, color=self.M_GREY, linestyle='dotted', alpha=1)
        axe1.grid(True, color=self.M_GREY, linestyle='dotted', alpha=1)
        axe0.set_xticklabels([])
        axe0.margins(y=0.2)
        axe1.margins(y=0.2)

        axe0.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                              integer=True,
                                                              min_n_ticks=4,
                                                              prune='both',
                                                              ))
        axe0.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.1f',
                                                                       ))

        axe1.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                              integer=True,
                                                              min_n_ticks=4,
                                                              prune='both',
                                                              ))
        axe1.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.0f',
                                                                       ))

        return True

    def drawSQR(self, data=None, cycle=None):
        """
        drawSQR show the measured sqr values over time

        :param data: data location
        :param cycle: cycle time for measurement
        :return: success
        """

        if not self.clearPlot(numberPlots=1):
            return False

        axe0 = self.measureMat.figure.axes[0]

        title = 'Sky Quality'
        ylabelLeft = 'Sky Quality [mpas]'

        start = -self.NUMBER_POINTS * cycle
        time = data['time'][start:-1:cycle]
        mLeft = data['sqr'][start:-1:cycle]

        axe0.set_title(title,
                       color=self.M_BLUE,
                       fontweight='bold',
                       fontsize=16)
        axe0.set_xlabel('Time [HH:MM:SS - UTC]',
                        color=self.M_BLUE,
                        fontweight='bold',
                        fontsize=12)
        axe0.set_ylabel(ylabelLeft,
                        color=self.M_WHITE,
                        fontweight='bold',
                        fontsize=12)

        axe0.plot(time,
                  mLeft,
                  marker='o',
                  markersize=1,
                  color=self.M_WHITE,
                  )

        axe0.grid(True, color=self.M_GREY, alpha=1)
        axe0.margins(y=0.2)

        axe0.get_yaxis().set_major_locator(ticker.MaxNLocator(nbins=8,
                                                              integer=True,
                                                              min_n_ticks=4,
                                                              prune='both',
                                                              ))
        axe0.get_yaxis().set_major_formatter(ticker.FormatStrFormatter('%.2f',
                                                                       ))

        return True

    def drawMeasure(self):
        """
        drawMeasure does the basic preparation for making the plot. it checks for borders
        and does finally the content dispatcher. currently there is no chance to implement
        a basic pattern as the graphs differ heavily.

        :return: success
        """

        if not self.showStatus:
            return False

        data = self.app.measure.data
        mIndex = self.ui.measureSet.currentIndex()
        tIndex = self.ui.timeSet.currentIndex()

        if len(data['time']) < 4:
            return False

        if not self.mutexDraw.tryLock():
            return False

        cycle = int(np.exp2(tIndex))
        grid = int(self.NUMBER_POINTS / self.NUMBER_XTICKS)
        ratio = cycle * grid
        time_end = data['time'][-1]

        time_ticks = np.arange(-self.NUMBER_XTICKS, 1, 1)
        time_ticks = time_ticks * ratio * 1000000
        time_ticks = time_ticks + time_end
        time_labels = [x.astype(dt).strftime('%H:%M:%S') for x in time_ticks]

        if mIndex == 0:
            self.drawRaDec(data=data, cycle=cycle)
        elif mIndex == 1:
            self.drawEnvironment(data=data, cycle=cycle)
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
