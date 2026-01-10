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
from mw4.gui.extWindows.measure.measureAddons import dataPlots


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
        self.dataPlots = dataPlots()

        self.mSetUI = {
            "set0": self.ui.set0,
            "set1": self.ui.set1,
            "set2": self.ui.set2,
            "set3": self.ui.set3,
            "set4": self.ui.set4,
        }
        self.oldTitle = ["No chart"] * len(self.mSetUI)

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
        for i, setName in enumerate(self.mSetUI):
            self.mSetUI[setName].currentIndexChanged.connect(
                partial(self.changeChart, setName)
            )
        self.app.colorChange.connect(self.colorChange)
        self.app.update1s.connect(self.drawMeasure)
        self.app.update1s.connect(self.setTitle)
        self.show()

    def closeEvent(self, closeEvent: QCloseEvent) -> None:
        """ """
        self.app.update1s.disconnect(self.drawMeasure)
        self.app.update1s.disconnect(self.setTitle)
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

    def constructPlotItem(self, plotItem, chart: dict, x: list[float]) -> None:
        """ """
        yMin, yMax, fixed = chart["template"].get("range", (None, None, False))
        if yMin is not None and yMax is not None:
            minYRange = (yMax - yMin) if fixed else (yMax - yMin) / 4
            maxYRange = yMax - yMin
            plotItem.setLimits(yMin=yMin, yMax=yMax, minYRange=minYRange, maxYRange=maxYRange)
        label = chart["template"].get("label", "-")
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
        chart["template"]["legendRef"] = legend
        plotItem.setLimits(xMin=x[0])

    def plotting(self, plotItem, chart: dict, x: list[float]) -> None:
        """ """
        newPlot = chart["template"]["label"] != plotItem.getAxis("left").labelText
        newPlot = newPlot or chart["template"]["legendRef"] is None
        if newPlot:
            self.constructPlotItem(plotItem, chart, x)

        data = self.app.measure.data
        for plot in chart["lineItems"]:
            print(plot)
            if plot not in data:
                continue
            pen = pg.mkPen(chart["lineItems"][plot].get("pen"), width=2)
            name = chart["lineItems"][plot].get("name", "")
            pd = chart["lineItems"][plot]["plotItemRef"]
            if pd is None:
                pd = plotItem.plot()
                chart["lineItems"][plot]["plotItemRef"] = pd
                if chart["template"]["legendRef"] is not None:
                    chart["template"]["legendRef"].addItem(pd, name)
            pd.setData(x=x[5:], y=data[plot][5:], pen=pen, name=name)

    @staticmethod
    def resetPlotItem(plotItem, chart: dict) -> None:
        """
        Reset legend based on https://github.com/pyqtgraph/pyqtgraph/discussions/1930
        """
        if not chart:
            return
        plotItem.scene().removeItem(chart["template"]["legendRef"])
        chart["template"]["legendRef"] = None
        plotItem.clear()
        for plot in chart["lineItems"]:
            chart["lineItems"][plot]["plotItemRef"] = None

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

            if title != self.oldTitle[i]:
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
