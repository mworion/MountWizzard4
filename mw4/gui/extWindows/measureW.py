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
import PyQt5
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
        self.plot = None

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
        self.ui.measureSet1.setCurrentIndex(config.get('measureSet1', 0))
        self.ui.measureSet2.setCurrentIndex(config.get('measureSet2', 0))
        self.ui.measureSet3.setCurrentIndex(config.get('measureSet3', 0))
        self.ui.timeSet.setCurrentIndex(config.get('timeSet', 0))
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
        self.ui.timeSet.currentIndexChanged.connect(self.cycleRefresh)
        self.ui.measureSet1.currentIndexChanged.connect(self.cycleRefresh)
        self.ui.measureSet2.currentIndexChanged.connect(self.cycleRefresh)
        self.ui.measureSet3.currentIndexChanged.connect(self.cycleRefresh)
        self.app.colorChange.connect(self.colorChange)
        self.app.update1s.connect(self.cycleRefresh)
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.app.update1s.disconnect(self.cycleRefresh)
        self.storeConfig()
        self.ui.timeSet.currentIndexChanged.disconnect(self.cycleRefresh)
        self.ui.measureSet1.currentIndexChanged.disconnect(self.cycleRefresh)
        self.ui.measureSet2.currentIndexChanged.disconnect(self.cycleRefresh)
        self.ui.measureSet3.currentIndexChanged.disconnect(self.cycleRefresh)
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

    def cycleRefresh(self):
        """
        :return: True for test purpose
        """
        data = self.app.measure.data
        if len(data['time']) < 1:
            return False
        self.plotRa()
        return True

    def plotRa(self):
        """
        :return: success
        """
        data = self.app.measure.data
        if len(data['time']) < 1:
            return False
        x = data['time'].astype('datetime64[s]').astype('int')
        y = data['test']
        self.ui.measure.plotDataItem.setData(x=x, y=y)
        return True

    def drawMeasure(self):
        """
        :return: success
        """
        data = self.app.measure.data
        if 'time' not in data:
            return False

        self.plotRa()

        return True
