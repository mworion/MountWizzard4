############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import pyqtgraph as pg
from functools import partial
import numpy as np
from mw4.gui.utilities import toolsQtWidget
from mw4.gui.widgets import measure_ui
from PySide6.QtCore import QMutex
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QListView


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
                "template": {"legendRef": None, "label": "Delta angle [arcsec]"},
                "lineItems": {
                    "deltaRaJNow": {"plotItemRef": None, "name": "RA", "pen": self.M_GREEN},
                    "deltaDecJNow": {"plotItemRef": None, "name": "DEC", "pen": self.M_RED},
                }
            },
            "Angular Tracking": {
                "template": {"legendRef": None, "label": "Angle error [arcsec]"},
                "lineItems": {
                    "errorAngularPosRA": {
                        "plotItemRef": None,
                        "name": "RA counter",
                        "pen": self.M_GREEN,
                    },
                    "errorAngularPosDEC": {
                        "plotItemRef": None,
                        "name": "DEC counter",
                        "pen": self.M_RED,
                    },
                }
            },
            "Temperature": {
                "template": {
                    "range": (-20, 40, False),
                    "legendRef": None,
                    "label": "Temperature [°C]",
                },
                "lineItems": {
                    "sensor1WeatherTemp": {
                        "plotItemRef": None,
                        "name": "Sensor 1",
                        "pen": self.M_GREEN,
                    },
                    "sensor2WeatherTemp": {
                        "plotItemRef": None,
                        "name": "Sensor 2",
                        "pen": self.M_RED,
                    },
                    "sensor3WeatherTemp": {
                        "plotItemRef": None,
                        "name": "Sensor 3",
                        "pen": self.M_PINK,
                    },
                    "sensor4WeatherTemp": {
                        "plotItemRef": None,
                        "name": "Sensor 4",
                        "pen": self.M_YELLOW,
                    },
                    "directWeatherTemp": {"plotItemRef": None, "name": "Direct", "pen": self.M_PRIM},
                }
            },
            "Camera Temperature": {
                "template": {
                    "range": (-20, 20, False),
                    "legendRef": None,
                    "label": "Camera Temperature [°C]",
                },
                "lineItems": {
                    "cameraTemp": {"plotItemRef": None, "name": "Camera", "pen": self.M_PINK},
                }
            },
            "Camera Cooler Power": {
                "template": {
                    "range": (-5, 105, True),
                    "legendRef": None,
                    "label": "Camera Cooler Power [%]",
                },
                "lineItems": {
                    "cameraPower": {"plotItemRef": None, "name": "CoolerPower", "pen": self.M_PINK},
                }
            },
            "Dew Temperature": {
                "template": {
                    "range": (-20, 40, False),
                    "legendRef": None,
                    "label": "Dew Temperature [°C]",
                },
                "lineItems": {
                    "sensor1WeatherDew": {
                        "plotItemRef": None,
                        "name": "Sensor 1",
                        "pen": self.M_GREEN,
                    },
                    "sensor2WeatherDew": {
                        "plotItemRef": None,
                        "name": "Sensor 2",
                        "pen": self.M_RED,
                    },
                    "sensor3WeatherDew": {
                        "plotItemRef": None,
                        "name": "Sensor 3",
                        "pen": self.M_PINK,
                    },
                    "sensor4WeatherDew": {
                        "plotItemRef": None,
                        "name": "Sensor 4",
                        "pen": self.M_YELLOW,
                    },
                    "directWeatherDew": {"plotItemRef": None, "name": "Direct", "pen": self.M_PRIM},
                }
            },
            "Pressure": {
                "template": {
                    "range": (900, 1050, False),
                    "legendRef": None,
                    "label": "Pressure [hPa]",
                },
                "lineItems": {
                    "sensor1WeatherPress": {
                        "plotItemRef": None,
                        "name": "Sensor 1",
                        "pen": self.M_GREEN,
                    },
                    "sensor2WeatherPress": {
                        "plotItemRef": None,
                        "name": "Sensor 2",
                        "pen": self.M_RED,
                    },
                    "sensor3WeatherPress": {
                        "plotItemRef": None,
                        "name": "Sensor 3",
                        "pen": self.M_PINK,
                    },
                    "sensor4WeatherPress": {
                        "plotItemRef": None,
                        "name": "Sensor 4",
                        "pen": self.M_YELLOW,
                    },
                    "directWeatherPress": {
                        "plotItemRef": None,
                        "name": "Direct",
                        "pen": self.M_PRIM,
                    },
                }
            },
            "Humidity": {
                "template": {"range": (-5, 105, True), "legendRef": None, "label": "Humidity [%]"},
                "lineItems": {
                    "sensor1WeatherHum": {
                        "plotItemRef": None,
                        "name": "Sensor 1",
                        "pen": self.M_GREEN,
                    },
                    "sensor2WeatherHum": {
                        "plotItemRef": None,
                        "name": "Sensor 2",
                        "pen": self.M_RED,
                    },
                    "sensor3WeatherHum": {
                        "plotItemRef": None,
                        "name": "Sensor 3",
                        "pen": self.M_PINK,
                    },
                    "sensor4WeatherHum": {
                        "plotItemRef": None,
                        "name": "Sensor 4",
                        "pen": self.M_YELLOW,
                    },
                    "directWeatherHum": {"plotItemRef": None, "name": "Direct", "pen": self.M_PRIM},
                }
            },
            "Sky Quality": {
                "template": {
                    "range": (10, 22.5, False),
                    "legendRef": None,
                    "label": "Sky Quality [mpas]",
                },
                "lineItems": {
                    "sensor1WeatherSky": {
                        "plotItemRef": None,
                        "name": "Sensor 1",
                        "pen": self.M_GREEN,
                    },
                    "sensor2WeatherSky": {
                        "plotItemRef": None,
                        "name": "Sensor 2",
                        "pen": self.M_RED,
                    },
                    "sensor3WeatherSky": {
                        "plotItemRef": None,
                        "name": "Sensor 3",
                        "pen": self.M_PINK,
                    },
                    "sensor4WeatherSky": {
                        "plotItemRef": None,
                        "name": "Sensor 4",
                        "pen": self.M_YELLOW,
                    },
                }
            },
            "Voltage": {
                "template": {
                    "range": (8, 15, False),
                    "legendRef": None,
                    "label": "Supply Voltage [V]",
                },
                "lineItems": {
                    "powVolt": {"plotItemRef": None, "name": "Main Sensor", "pen": self.M_YELLOW},
                }
            },
            "Current": {
                "template": {"range": (0, 5, False), "legendRef": None, "label": "Current [A]"},
                "lineItems": {
                    "powCurr": {"plotItemRef": None, "name": "Sum", "pen": self.M_CYAN1},
                    "powCurr1": {"plotItemRef": None, "name": "Current 1", "pen": self.M_GREEN},
                    "powCurr2": {"plotItemRef": None, "name": "Current 2", "pen": self.M_PINK},
                    "powCurr3": {"plotItemRef": None, "name": "Current 3", "pen": self.M_RED},
                    "powCurr4": {"plotItemRef": None, "name": "Current 4", "pen": self.M_YELLOW},
                }
            },
            "Time Diff Comp-Mount": {
                "template": {"legendRef": None, "label": "Time Difference [ms]"},
                "lineItems": {
                    "timeDiff": {"plotItemRef": None, "name": "MountControl", "pen": self.M_YELLOW},
                }
            },
            "Focus Position": {
                "template": {"legendRef": None, "label": "Focus Position [units]"},
                "lineItems": {
                    "focusPosition": {
                        "plotItemRef": None,
                        "name": "MountControl",
                        "pen": self.M_YELLOW,
                    }
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
            title = f"Measuring:   {imagePath.stem}"
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
        yMin, yMax, fixed = values["template"].get("range", (None, None, False))
        if yMin is not None and yMax is not None:
            minYRange = (yMax - yMin) if fixed else (yMax - yMin) / 4
            maxYRange = yMax - yMin
            plotItem.setLimits(yMin=yMin, yMax=yMax, minYRange=minYRange, maxYRange=maxYRange)
        label = values["template"].get("label", "-")
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
        values["template"]["legendRef"] = legend
        plotItem.setLimits(xMin=x[0])

    def plotting(self, plotItem, values: dict, x: list[float]) -> None:
        """ """
        newPlot = values["template"]["label"] != plotItem.getAxis("left").labelText
        newPlot = newPlot or values["template"]["legendRef"] is None
        if newPlot:
            self.constructPlotItem(plotItem, values, x)

        data = self.app.measure.data
        for item in values["lineItems"]:
            pen = pg.mkPen(values["lineItems"][item].get("pen"), width=2)
            name = values["lineItems"][item].get("name", "")
            pd = values["lineItems"][item]["plotItemRef"]
            if pd is None:
                pd = plotItem.plot()
                values["lineItems"][item]["plotItemRef"] = pd
                if values["template"]["legendRef"] is not None:
                    values["template"]["legendRef"].addItem(pd, name)
            pd.setData(x=x[5:], y=data[item][5:], pen=pen, name=name)

    @staticmethod
    def resetPlotItem(plotItem, values: dict) -> None:
        """ """
        plotItem.clear()
        for value in values:
            if value == "template":
                values["template"]["legendRef"] = None
            else:
                values[value]["plotItemRef"] = None

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

    def processDrawMeasure(self, x: np.array, noChart: bool) -> None:
        """ """
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

    def drawMeasure(self) -> None:
        """ """
        data = self.app.measure.data
        if len(data.get("time", [])) < 5:
            return
        if not self.drawLock.tryLock():
            return
        x = data["time"].astype("datetime64[s]").astype("int")
        noChart = all(x in ["No chart", None] for x in self.oldTitle)
        self.processDrawMeasure(x, noChart)
        self.drawLock.unlock()
