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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
from functools import partial

# external packages
from PySide6.QtWidgets import QListView
from PySide6.QtCore import QMutex
from PySide6.QtGui import QCloseEvent
import pyqtgraph as pg

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import measure_ui


class MeasureWindow(toolsQtWidget.MWidget):
    """ """

    NUMBER_POINTS = 250
    NUMBER_XTICKS = 5

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = measure_ui.Ui_MeasureDialog()
        self.ui.setupUi(self)
        self.drawLock = QMutex()

        self.mSetUI = {
            "set0": self.ui.set0,
            "set1": self.ui.set1,
            "set2": self.ui.set2,
            "set3": self.ui.set3,
            "set4": self.ui.set4,
        }

        self.oldTitle = [None] * len(self.mSetUI)

        self.dataPlots = {
            "No chart": {},
            "Axis Stability": {
                "gen": {"leg": None, "label": "Delta angle [arcsec]"},
                "deltaRaJNow": {"pd": None, "name": "RA", "pen": self.M_GREEN},
                "deltaDecJNow": {"pd": None, "name": "DEC", "pen": self.M_RED},
            },
            "Angular Tracking": {
                "gen": {"leg": None, "label": "Angle error [arcsec]"},
                "errorAngularPosRA": {
                    "pd": None,
                    "name": "RA counter",
                    "pen": self.M_GREEN,
                },
                "errorAngularPosDEC": {
                    "pd": None,
                    "name": "DEC counter",
                    "pen": self.M_RED,
                },
            },
            "Temperature": {
                "gen": {
                    "range": (-20, 40, False),
                    "leg": None,
                    "label": "Temperature [°C]",
                },
                "sensor1WeatherTemp": {
                    "pd": None,
                    "name": "Sensor 1",
                    "pen": self.M_GREEN,
                },
                "sensor2WeatherTemp": {
                    "pd": None,
                    "name": "Sensor 2",
                    "pen": self.M_RED,
                },
                "sensor3WeatherTemp": {
                    "pd": None,
                    "name": "Sensor 3",
                    "pen": self.M_PINK,
                },
                "onlineWeatherTemp": {
                    "pd": None,
                    "name": "Online",
                    "pen": self.M_YELLOW,
                },
                "directWeatherTemp": {"pd": None, "name": "Direct", "pen": self.M_PRIM},
            },
            "Camera Temperature": {
                "gen": {
                    "range": (-20, 20, False),
                    "leg": None,
                    "label": "Camera Temperature [°C]",
                },
                "cameraTemp": {"pd": None, "name": "Camera", "pen": self.M_PINK},
            },
            "Camera Cooler Power": {
                "gen": {
                    "range": (-5, 105, True),
                    "leg": None,
                    "label": "Camera Cooler Power [%]",
                },
                "cameraPower": {"pd": None, "name": "CoolerPower", "pen": self.M_PINK},
            },
            "Dew Temperature": {
                "gen": {
                    "range": (-20, 40, False),
                    "leg": None,
                    "label": "Dew Temperature [°C]",
                },
                "sensor1WeatherDew": {
                    "pd": None,
                    "name": "Sensor 1",
                    "pen": self.M_GREEN,
                },
                "sensor2WeatherDew": {
                    "pd": None,
                    "name": "Sensor 2",
                    "pen": self.M_RED,
                },
                "sensor3WeatherDew": {
                    "pd": None,
                    "name": "Sensor 3",
                    "pen": self.M_PINK,
                },
                "onlineWeatherDew": {
                    "pd": None,
                    "name": "Online",
                    "pen": self.M_YELLOW,
                },
                "directWeatherDew": {"pd": None, "name": "Direct", "pen": self.M_PRIM},
            },
            "Pressure": {
                "gen": {
                    "range": (900, 1050, False),
                    "leg": None,
                    "label": "Pressure [hPa]",
                },
                "sensor1WeatherPress": {
                    "pd": None,
                    "name": "Sensor 1",
                    "pen": self.M_GREEN,
                },
                "sensor2WeatherPress": {
                    "pd": None,
                    "name": "Sensor 2",
                    "pen": self.M_RED,
                },
                "sensor3WeatherPress": {
                    "pd": None,
                    "name": "Sensor 3",
                    "pen": self.M_PINK,
                },
                "onlineWeatherPress": {
                    "pd": None,
                    "name": "Online",
                    "pen": self.M_YELLOW,
                },
                "directWeatherPress": {
                    "pd": None,
                    "name": "Direct",
                    "pen": self.M_PRIM,
                },
            },
            "Humidity": {
                "gen": {"range": (-5, 105, True), "leg": None, "label": "Humidity [%]"},
                "sensor1WeatherHum": {
                    "pd": None,
                    "name": "Sensor 1",
                    "pen": self.M_GREEN,
                },
                "sensor2WeatherHum": {
                    "pd": None,
                    "name": "Sensor 2",
                    "pen": self.M_RED,
                },
                "sensor3WeatherHum": {
                    "pd": None,
                    "name": "Sensor 3",
                    "pen": self.M_PINK,
                },
                "onlineWeatherHum": {
                    "pd": None,
                    "name": "Online",
                    "pen": self.M_YELLOW,
                },
                "directWeatherHum": {"pd": None, "name": "Direct", "pen": self.M_PRIM},
            },
            "Sky Quality": {
                "gen": {
                    "range": (10, 22.5, False),
                    "leg": None,
                    "label": "Sky Quality [mpas]",
                },
                "sensor1WeatherSky": {
                    "pd": None,
                    "name": "Sensor 1",
                    "pen": self.M_GREEN,
                },
                "sensor2WeatherSky": {
                    "pd": None,
                    "name": "Sensor 2",
                    "pen": self.M_RED,
                },
                "sensor3WeatherSky": {
                    "pd": None,
                    "name": "Sensor 3",
                    "pen": self.M_PINK,
                },
                "onlineWeatherHum": {
                    "pd": None,
                    "name": "Online",
                    "pen": self.M_YELLOW,
                },
            },
            "Voltage": {
                "gen": {
                    "range": (8, 15, False),
                    "leg": None,
                    "label": "Supply Voltage [V]",
                },
                "powVolt": {"pd": None, "name": "Main Sensor", "pen": self.M_YELLOW},
            },
            "Current": {
                "gen": {"range": (0, 5, False), "leg": None, "label": "Current [A]"},
                "powCurr": {"pd": None, "name": "Sum", "pen": self.M_CYAN1},
                "powCurr1": {"pd": None, "name": "Current 1", "pen": self.M_GREEN},
                "powCurr2": {"pd": None, "name": "Current 2", "pen": self.M_PINK},
                "powCurr3": {"pd": None, "name": "Current 3", "pen": self.M_RED},
                "powCurr4": {"pd": None, "name": "Current 4", "pen": self.M_YELLOW},
            },
            "Time Diff Comp-Mount": {
                "gen": {"leg": None, "label": "Time Difference [ms]"},
                "timeDiff": {"pd": None, "name": "MountControl", "pen": self.M_YELLOW},
            },
            "Focus Position": {
                "gen": {"leg": None, "label": "Focus Position [units]"},
                "focusPosition": {
                    "pd": None,
                    "name": "MountControl",
                    "pen": self.M_YELLOW,
                },
            },
        }

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("measureW", {})

        self.positionWindow(config)
        self.setupButtons()
        self.drawMeasure()
        for setName in self.mSetUI:
            self.mSetUI[setName].setCurrentIndex(config.get(setName, 0))

    def storeConfig(self) -> None:
        """ """
        configMain = self.app.config
        configMain["measureW"] = {}
        config = configMain["measureW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()
        for setName in self.mSetUI:
            config[setName] = self.mSetUI[setName].currentIndex()

    def showWindow(self) -> None:
        """ """
        for setName in self.mSetUI:
            self.mSetUI[setName].currentIndexChanged.connect(
                partial(self.changeChart, setName)
            )
        self.app.colorChange.connect(self.colorChange)
        self.app.update1s.connect(self.drawMeasure)
        self.app.update1s.connect(self.setTitle)
        self.show()

    def closeEvent(self, closeEvent: QCloseEvent) -> None:
        """ """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)
        self.ui.measure.colorChange()
        for setName, plotItem in zip(self.mSetUI.keys(), self.ui.measure.p):
            values = self.dataPlots.get(self.mSetUI[setName].currentText(), 0)
            self.resetPlotItem(plotItem, values)
        self.drawMeasure()

    def setTitle(self) -> None:
        """ """
        if self.app.measure.framework == "csv":
            imagePath = self.app.measure.run["csv"].csvFilename
            title = f"Measuring:   {os.path.basename(imagePath)}"
        else:
            title = "Measuring"
        self.setWindowTitle(title)

    def setupButtons(self) -> None:
        """ """
        for setName in self.mSetUI:
            ui = self.mSetUI[setName]
            ui.clear()
            ui.setView(QListView())
            for text in self.dataPlots:
                ui.addItem(text)

    def constructPlotItem(self, plotItem, values: dict, x: list[float]) -> None:
        """ """
        yMin, yMax, fixed = values["gen"].get("range", (None, None, False))
        if yMin is not None and yMax is not None:
            minYRange = (yMax - yMin) if fixed else (yMax - yMin) / 4
            maxYRange = yMax - yMin
            plotItem.setLimits(yMin=yMin, yMax=yMax, minYRange=minYRange, maxYRange=maxYRange)
        label = values["gen"].get("label", "-")
        plotItem.setLabel("left", label)
        legend = pg.LegendItem(
            pen=self.ui.measure.pen,
            offset=(65, 5),
            verSpacing=-5,
            labelTextColor=self.M_PRIM,
            labelTextSize="10pt",
            brush=pg.mkBrush(color=self.M_BACK),
        )
        legend.setParentItem(plotItem)
        values["gen"]["leg"] = legend
        plotItem.setLimits(xMin=x[0])

    def plotting(self, plotItem, values: dict, x: list[float]) -> bool:
        """ """
        newPlot = values["gen"]["label"] != plotItem.getAxis("left").labelText
        newPlot = newPlot or values["gen"]["leg"] is None
        if newPlot:
            self.constructPlotItem(plotItem, values, x)

        data = self.app.measure.data
        for value in values:
            if value == "gen":
                continue
            pen = pg.mkPen(values[value].get("pen"), width=2)
            name = values[value].get("name", value)
            pd = values[value]["pd"]
            if pd is None:
                pd = plotItem.plot()
                values[value]["pd"] = pd
                if values["gen"]["leg"] is not None:
                    values["gen"]["leg"].addItem(pd, name)
            pd.setData(x=x[5:], y=data[value][5:], pen=pen, name=name)

    @staticmethod
    def resetPlotItem(plotItem, values: dict) -> None:
        """ """
        plotItem.clear()
        for value in values:
            if value == "gen":
                values["gen"]["leg"] = None
            else:
                values[value]["pd"] = None

    def triggerUpdate(self) -> None:
        """ """
        self.resize(self.width() - 1, self.height())
        self.resize(self.width() + 1, self.height())

    def inUseMessage(self) -> None:
        """ """
        self.messageDialog(
            self,
            "Chart selection",
            "Chart already in use\n\n     Cannot be selected!",
            ["Ok"],
            iconType=1,
        )

    def checkInUse(self, setName: str, index: int) -> bool:
        """ """
        for name in self.mSetUI:
            if name == setName:
                continue
            if self.mSetUI[name].currentIndex() == index:
                return True
        return False

    def changeChart(self, setName: str, index: int) -> None:
        """ """
        if self.checkInUse(setName, index) and index != 0:
            self.mSetUI[setName].setCurrentIndex(0)
            self.inUseMessage()
        self.drawMeasure()

    def drawMeasure(self) -> None:
        """ """
        data = self.app.measure.data
        if len(data.get("time", [])) < 5:
            return
        if not self.drawLock.tryLock():
            return

        x = data["time"].astype("datetime64[s]").astype("int")

        noChart = all([x in ["No chart", None] for x in self.oldTitle])

        for i, v in enumerate(zip(self.mSetUI.keys(), self.ui.measure.p)):
            setName, plotItem = v
            title = self.mSetUI[setName].currentText()
            if title != self.oldTitle[i] and self.oldTitle[i] is not None:
                self.resetPlotItem(plotItem, self.dataPlots[self.oldTitle[i]])

            self.oldTitle[i] = title
            isVisible = title != "No chart"
            plotItem.setVisible(isVisible)
            if not isVisible:
                continue

            self.plotting(plotItem, self.dataPlots[title], x)
            if noChart:
                self.triggerUpdate()
                plotItem.autoRange()
                plotItem.enableAutoRange(x=True, y=True)

        self.drawLock.unlock()
