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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages
from PyQt5.QtWidgets import QListView
from PyQt5.QtCore import QMutex
import pyqtgraph as pg

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import measure_ui


class MeasureWindow(toolsQtWidget.MWidget):
    """
    the measure window class handles

    """

    __all__ = ['MeasureWindow']

    NUMBER_POINTS = 250
    NUMBER_XTICKS = 5

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = measure_ui.Ui_MeasureDialog()
        self.ui.setupUi(self)
        self.drawLock = QMutex()
        self.mSetUI = [self.ui.set0,
                       self.ui.set1,
                       self.ui.set2,
                       self.ui.set3,
                       self.ui.set4]
        self.oldTitle = [None] * len(self.mSetUI)

        self.dataPlots = {
            'No chart': {},
            'Axis Stability': {
                'gen': {'leg': None,
                        'label': 'Delta angle [arcsec]'},
                'deltaRaJNow': {'pd': None,
                                'name': 'RA',
                                'pen': self.M_GREEN},
                'deltaDecJNow': {'pd': None,
                                 'name': 'DEC',
                                 'pen': self.M_RED},
            },
            'Angular Tracking': {
                'gen': {'leg': None,
                        'label': 'Angle error [arcsec]'},
                'errorAngularPosRA': {'pd': None,
                                      'name': 'RA counter',
                                      'pen': self.M_GREEN},
                'errorAngularPosDEC': {'pd': None,
                                       'name': 'DEC counter',
                                       'pen': self.M_RED},
            },
            'Temperature': {
                'gen': {'range': (-20, 40, False),
                        'leg': None,
                        'label': 'Temperature [°C]'},
                'sensorWeatherTemp': {'pd': None,
                                      'name': 'Sensor',
                                      'pen': self.M_GREEN},
                'directWeatherTemp': {'pd': None,
                                      'name': 'Direct',
                                      'pen': self.M_RED},
                'onlineWeatherTemp': {'pd': None,
                                      'name': 'Online',
                                      'pen': self.M_YELLOW},
                'skyTemp': {'pd': None,
                            'name': 'SQR sensor',
                            'pen': self.M_BLUE},
                'powTemp': {'pd': None,
                            'name': 'Power sensor',
                            'pen': self.M_PINK},
            },
            'Camera Temperature': {
                'gen': {'range': (-20, 20, False),
                        'leg': None,
                        'label': 'Camera Temperature [°C]'},
                'cameraTemp': {'pd': None,
                               'name': 'Camera',
                               'pen': self.M_PINK},
            },
            'Camera Cooler Power': {
                'gen': {'range': (-5, 105, True),
                        'leg': None,
                        'label': 'Camera Cooler Power [%]'},
                'cameraPower': {'pd': None,
                                'name': 'CoolerPower',
                                'pen': self.M_PINK},
            },
            'Dew Temperature': {
                'gen': {'range': (-20, 40, False),
                        'leg': None,
                        'label': 'Dew Temperature [°C]'},
                'sensorWeatherDew': {'pd': None,
                                     'name': 'Sensor',
                                     'pen': self.M_GREEN},
                'directWeatherDew': {'pd': None,
                                     'name': 'Direct',
                                     'pen': self.M_RED},
                'onlineWeatherDew': {'pd': None,
                                     'name': 'Online',
                                     'pen': self.M_YELLOW},
                'powDew': {'pd': None,
                           'name': 'Power sensor',
                           'pen': self.M_PINK},
            },
            'Pressure': {
                'gen': {'range': (900, 1050, False),
                        'leg': None,
                        'label': 'Pressure [hPa]'},
                'sensorWeatherPress': {'pd': None,
                                       'name': 'Sensor',
                                       'pen': self.M_GREEN},
                'directWeatherPress': {'pd': None,
                                       'name': 'Direct',
                                       'pen': self.M_RED},
                'onlineWeatherPress': {'pd': None,
                                       'name': 'Online',
                                       'pen': self.M_YELLOW},
            },
            'Humidity': {
                'gen': {'range': (-5, 105, True),
                        'leg': None,
                        'label': 'Humidity [%]'},
                'sensorWeatherHum': {'pd': None,
                                     'name': 'Sensor',
                                     'pen': self.M_GREEN},
                'directWeatherHum': {'pd': None,
                                     'name': 'Direct',
                                     'pen': self.M_RED},
                'onlineWeatherHum': {'pd': None,
                                     'name': 'Online',
                                     'pen': self.M_YELLOW},
                'powHum': {'pd': None,
                           'name': 'Power sensor',
                           'pen': self.M_PINK},
            },
            'Sky Quality': {
                'gen': {'range': (10, 22.5, False),
                        'leg': None,
                        'label': 'Sky Quality [mpas]'},
                'skySQR': {'pd': None,
                           'name': 'SQR',
                           'pen': self.M_YELLOW},
            },
            'Voltage': {
                'gen': {'range': (8, 15, False),
                        'leg': None,
                        'label': 'Supply Voltage [V]'},
                'powVolt': {'pd': None,
                            'name': 'Main Sensor',
                            'pen': self.M_YELLOW},
            },
            'Current': {
                'gen': {'range': (0, 5, False),
                        'leg': None,
                        'label': 'Current [A]'},
                'powCurr': {'pd': None,
                            'name': 'Sum',
                            'pen': self.M_CYAN1},
                'powCurr1': {'pd': None,
                             'name': 'Current 1',
                             'pen': self.M_GREEN},
                'powCurr2': {'pd': None,
                             'name': 'Current 2',
                             'pen': self.M_PINK},
                'powCurr3': {'pd': None,
                             'name': 'Current 3',
                             'pen': self.M_RED},
                'powCurr4': {'pd': None,
                             'name': 'Current 4',
                             'pen': self.M_YELLOW},
            },
            'Time Diff Comp-Mount': {
                'gen': {'leg': None,
                        'label': 'Time Difference [ms]'},
                'timeDiff': {'pd': None,
                             'name': 'MountControl',
                             'pen': self.M_YELLOW},
            },
            'Focus Position': {
                'gen': {'leg': None,
                        'label': 'Focus Position [units]'},
                'focusPosition': {'pd': None,
                                  'name': 'MountControl',
                                  'pen': self.M_YELLOW},
            },
        }

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'measureW' not in self.app.config:
            self.app.config['measureW'] = {}
        config = self.app.config['measureW']

        self.positionWindow(config)
        self.setupButtons()
        for i, ui in enumerate(self.mSetUI):
            ui.setCurrentIndex(config.get(f'set{i}', 0))
        self.drawMeasure()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config
        if 'measureW' not in config:
            config['measureW'] = {}
        else:
            config['measureW'].clear()
        config = config['measureW']

        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        for i, ui in enumerate(self.mSetUI):
            config[f'set{i}'] = ui.currentIndex()
        return True

    def showWindow(self):
        """
        :return:
        """
        self.show()
        for ui in self.mSetUI:
            ui.currentIndexChanged.connect(self.changeChart)
        self.app.colorChange.connect(self.colorChange)
        self.app.update1s.connect(self.drawMeasure)
        self.app.update1s.connect(self.setTitle)
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def colorChange(self):
        """
        :return:
        """
        self.setStyleSheet(self.mw4Style)
        self.ui.measure.colorChange()
        for ui, plotItem in zip(self.mSetUI, self.ui.measure.p):
            values = self.dataPlots.get(ui.currentText(), 0)
            self.resetPlotItem(plotItem, values)
        self.drawMeasure()
        return True

    def setTitle(self):
        """
        :return:
        """
        if self.app.measure.framework == 'csv':
            imagePath = self.app.measure.run['csv'].csvFilename
            title = f'Measuring:   {os.path.basename(imagePath)}'
        else:
            title = 'Measuring'
        self.setWindowTitle(title)
        return True

    def setupButtons(self):
        """
        setupButtons prepares the dynamic content od the buttons in measurement
        window. it writes the bottom texts and number as well as the coloring for
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

    def constructPlotItem(self, plotItem, values, x):
        """
        :param plotItem:
        :param values:
        :param x:
        :return:
        """
        yMin, yMax, fixed = values['gen'].get('range', (None, None, False))
        if yMin is not None and yMax is not None:
            minYRange = (yMax - yMin) if fixed else (yMax - yMin) / 4
            maxYRange = (yMax - yMin)
            plotItem.setLimits(yMin=yMin, yMax=yMax,
                               minYRange=minYRange,
                               maxYRange=maxYRange)
        label = values['gen'].get('label', '-')
        plotItem.setLabel('left', label)
        legend = pg.LegendItem(pen=self.ui.measure.pen,
                               offset=(65, 5),
                               verSpacing=-5,
                               labelTextColor=self.M_BLUE,
                               labelTextSize='10pt',
                               brush=pg.mkBrush(color=self.M_BACK))
        legend.setParentItem(plotItem)
        values['gen']['leg'] = legend
        plotItem.setLimits(xMin=x[0])
        return True

    def plotting(self, plotItem, values, x):
        """
        :param plotItem:
        :param values:
        :param x:
        :return:
        """
        newPlot = values['gen']['label'] != plotItem.getAxis('left').labelText
        newPlot = newPlot or values['gen']['leg'] is None
        if newPlot:
            self.constructPlotItem(plotItem, values, x)

        data = self.app.measure.data
        for value in values:
            if value == 'gen':
                continue
            pen = pg.mkPen(values[value].get('pen'), width=2)
            name = values[value].get('name', value)
            pd = values[value]['pd']
            if pd is None:
                pd = plotItem.plot()
                values[value]['pd'] = pd
                if values['gen']['leg'] is not None:
                    values['gen']['leg'].addItem(pd, name)
            pd.setData(x=x[5:], y=data[value][5:], pen=pen, name=name)
        return True

    @staticmethod
    def resetPlotItem(plotItem, values):
        """
        :param plotItem:
        :param values:
        :return:
        """
        plotItem.clear()
        for value in values:
            if value == 'gen':
                values['gen']['leg'] = None
            else:
                values[value]['pd'] = None
        return True

    def triggerUpdate(self):
        """
        :return:
        """
        self.resize(self.width() - 1, self.height())
        self.resize(self.width() + 1, self.height())
        return True

    def inUseMessage(self):
        """
        :return:
        """
        self.messageDialog(self, 'Chart selection',
                           'Chart already in use\n\n     Cannot be selected!',
                           ['Ok'], iconType=1)
        return True

    def changeChart(self, index):
        """
        :param index:
        :return:
        """
        sender = self.sender()
        for ui in self.mSetUI:
            if ui == sender:
                continue
            if ui.currentIndex() == 0:
                continue
            if index == ui.currentIndex():
                sender.setCurrentIndex(0)
                self.inUseMessage()
                break
        else:
            self.drawMeasure()
        return True

    def drawMeasure(self):
        """
        :return: success
        """
        data = self.app.measure.data
        if len(data.get('time', [])) < 5:
            return False
        if not self.drawLock.tryLock():
            return False

        ui = self.ui.measure
        x = data['time'].astype('datetime64[s]').astype('int')

        noChart = all([x in ['No chart', None] for x in self.oldTitle])

        for i, v in enumerate(zip(self.mSetUI, ui.p)):
            ui, plotItem = v
            title = ui.currentText()
            if title != self.oldTitle[i] and self.oldTitle[i] is not None:
                self.resetPlotItem(
                    plotItem, self.dataPlots[self.oldTitle[i]])

            self.oldTitle[i] = title
            isVisible = title != 'No chart'
            plotItem.setVisible(isVisible)
            if not isVisible:
                continue

            self.plotting(plotItem, self.dataPlots[title], x)
            if noChart:
                self.triggerUpdate()
                plotItem.autoRange()
                plotItem.enableAutoRange(x=True, y=True)

        self.drawLock.unlock()
        return True
