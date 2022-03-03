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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from datetime import datetime as dt

# external packages
from PyQt5.QtWidgets import QListView
import numpy as np
import pyqtgraph as pg

# local import
from gui.utilities import toolsQtWidget
from gui.utilities.tools4pyqtgraph import TimeAxis
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

        self.mSetUI = [self.ui.set1,
                       self.ui.set2,
                       self.ui.set3]

        self.oldTitle = [None, None, None]

        self.dataPlots = {
            'No chart': {},
            'RA Stability': {},
            'DEC Stability': {},
            'RA Angular Error': {},
            'DEC Angular Error': {},
            'Temperature': {
                'general': {'range': (-20, 20),
                            'label': 'Temperature [°C]'},
                'sensorWeatherTemp': {'pd': None,
                                      'name': 'direct',
                                      'pen': self.M_GREEN},
                'onlineWeatherTemp': {'pd': None,
                                      'name': 'direct',
                                      'pen': self.M_YELLOW}
            },
            'Pressure': {
                'general': {'range': (900, 1100),
                            'label': 'Pressure [hPa]'},
                'sensorWeatherPress': {'pd': None,
                                       'name': 'direct',
                                       'pen': self.M_GREEN},
                'onlineWeatherPress': {'pd': None,
                                       'name': 'direct',
                                       'pen': self.M_YELLOW}
            },
            'Humidity': {},
            'Sky Quality': {},
            'Voltage': {},
            'Current': {},
        }

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
        self.ui.set1.setCurrentIndex(config.get('set1', 0))
        self.ui.set2.setCurrentIndex(config.get('set2', 0))
        self.ui.set3.setCurrentIndex(config.get('set3', 0))
        self.drawMeasure()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        if 'measureW' not in self.app.config:
            self.app.config['measureW'] = {}
        config = self.app.config['measureW']
        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        config['set1'] = self.ui.set1.currentIndex()
        config['set2'] = self.ui.set2.currentIndex()
        config['set3'] = self.ui.set3.currentIndex()
        return True

    def showWindow(self):
        """
        :return:
        """
        self.show()
        self.ui.set1.currentIndexChanged.connect(self.drawMeasure)
        self.ui.set2.currentIndexChanged.connect(self.drawMeasure)
        self.ui.set3.currentIndexChanged.connect(self.drawMeasure)
        self.app.colorChange.connect(self.colorChange)
        self.app.update1s.connect(self.drawMeasure)
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.app.update1s.disconnect(self.drawMeasure)
        self.storeConfig()
        self.ui.set1.currentIndexChanged.disconnect(self.drawMeasure)
        self.ui.set2.currentIndexChanged.disconnect(self.drawMeasure)
        self.ui.set3.currentIndexChanged.disconnect(self.drawMeasure)
        self.app.colorChange.disconnect(self.colorChange)
        super().closeEvent(closeEvent)

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.measureMat.parentWidget().setStyleSheet(self.mw4Style)
        self.drawMeasure()
        return True

    def setupButtons(self):
        """
        setupButtons prepares the dynamic content od the buttons in measurement
        window. it write the bottom texts and number as well as the coloring for
        the actual setting

        :return: success for test purpose
        """
        for mSet in self.mSetUI:
            mSet.clear()
            mSet.setView(QListView())
            for text in self.dataPlots:
                if text == 'No chart':
                    mSet.addItem(text)
                    continue
                if self.dataPlots[text]:
                    mSet.addItem(text)
        return True

    @staticmethod
    def setPlotItem(plotItem, general):
        """
        :param plotItem:
        :param general:
        :return:
        """
        yMin, yMax = general.get('range', (None, None))
        if yMin and yMax:
            plotItem.setLimits(yMin=yMin, yMax=yMax,
                               minYRange=(yMax - yMin) / 2,
                               maxYRange=(yMax - yMin))
            plotItem.setYRange(yMin, yMax)
        label = general.get('label', '')
        plotItem.setLabel('left', label)
        return True

    def plotY(self, plotItem, x, values):
        """
        :param plotItem:
        :param x:
        :param values:
        :return:
        """
        data = self.app.measure.data
        for value in values:
            if value == 'general':
                continue

            pen = values[value].get('pen', self.M_BLUE)
            name = values[value].get('name', value)
            pd = values[value]['pd']

            if pd is None:
                pd = pg.PlotDataItem()
                plotItem.addItem(pd)
                newPlot = True

            pd.setData(x=x, y=data[value], pen=pen,
                       autoDownsample=True, name=name)
        if newPlot:
            self.setPlotItem(plotItem, values['general'])
        return True

    def drawMeasure(self):
        """
        :return: success
        """
        data = self.app.measure.data
        if len(data.get('time', [])) < 1:
            return False

        ui = self.ui.measure
        plotItems = [ui.p1, ui.p2, ui.p3]
        uis = [self.ui.set1, self.ui.set2, self.ui.set3]

        x = data['time'].astype('datetime64[s]').astype('int')
        for i, val in enumerate(zip(uis, plotItems)):
            ui, plotItem = val
            title = ui.currentText()
            self.oldTitle[i] = title
            if title == 'No chart':
                plotItem.setVisible(False)
                plotItem.clear()
                continue
            plotItem.setVisible(True)
            self.plotY(plotItem, x, self.dataPlots[title])
        return True
