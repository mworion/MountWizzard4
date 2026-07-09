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
# License APL2.0
#
###########################################################
import numpy as np
import pyqtgraph as pg
from mw4.gui.utilities.pyqtgraph.gPlotBase import PlotBase
from PySide6.QtGui import QColor


class NormalScatter(PlotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupItems()
        self.colorInx = None
        self.col = None
        self.p[0].setVisible(True)

    def setupRangeLimits(self, x: np.ndarray, y: np.ndarray, kwargs: dict) -> None:
        self.defRange = kwargs.get("range", {})
        xMin = self.defRange.get("xMin", np.min(x))
        yMin = self.defRange.get("yMin", np.min(y))
        xMax = self.defRange.get("xMax", np.max(x))
        yMax = self.defRange.get("yMax", np.max(y))
        if not kwargs.get("limits", True):
            return
        if xMin is not None and xMax is not None:
            self.p[0].setLimits(
                xMin=xMin,
                xMax=xMax,
                minXRange=(xMax - xMin) / 4,
                maxXRange=(xMax - xMin),
            )
            self.p[0].setXRange(xMin, xMax)
        if yMin is not None and yMax is not None:
            self.p[0].setLimits(
                yMin=yMin,
                yMax=yMax,
                minYRange=(yMax - yMin) / 4,
                maxYRange=(yMax - yMin),
            )
            self.p[0].setYRange(yMin, yMax)

    @staticmethod
    def computeZColorMap(z: np.ndarray) -> tuple[np.ndarray, float, float]:
        err = np.abs(z)
        minE = float(np.min(err))
        maxE = float(np.max(err))
        divisor = max((maxE - minE), 0.1)
        colorInx = (err - minE) / divisor
        return colorInx, minE, maxE

    def setupColorData(self, x: np.ndarray, kwargs: dict) -> tuple[float, float]:
        self.col = kwargs.get("color", self.M_PRIM)
        if isinstance(self.col[0], int):
            self.col = [self.col] * len(x)
        minE, maxE = 0.0, 0.0
        if "z" in kwargs:
            self.colorInx, minE, maxE = self.computeZColorMap(kwargs["z"])
        return minE, maxE

    def setupBarItem(self, kwargs: dict, minE: float, maxE: float) -> None:
        if not (kwargs.get("bar", False) and "z" in kwargs):
            return
        self.barItem.setVisible(True)
        self.barItem.setLevels(values=(minE, maxE))
        self.barItem.setColorMap(self.colorMapStyle[0])

    def buildSpots(self, x: np.ndarray, y: np.ndarray, kwargs: dict) -> list:
        dataVal = kwargs.get("data", y)
        spots = []
        for i in range(len(x)):
            if "z" in kwargs:
                colorVal = self.colorMapStyle[0].mapToQColor(self.colorInx[i])
            else:
                colorVal = QColor(*self.col[i])
            spots.append(
                {
                    "pos": (x[i], y[i]),
                    "data": dataVal[i],
                    "brush": colorVal,
                    "pen": colorVal,
                    "size": 6,
                }
            )
        return spots

    def addScatterPoints(self, spots: list, kwargs: dict) -> None:
        tip = kwargs.get("tip")
        if tip is None:
            self.scatterItem.addPoints(spots)
        else:
            self.scatterItem.addPoints(spots, tip=tip)

    def plot(self, x: np.ndarray, y: np.ndarray, **kwargs) -> None:
        self.p[0].clear()
        self.p[0].showAxes(True, showValues=True)
        self.scatterItem = pg.ScatterPlotItem(hoverable=True, hoverSize=10, hoverPen=self.pen)
        self.p[0].addItem(self.scatterItem)
        self.setupRangeLimits(x, y, kwargs)
        self.p[0].getViewBox().rightMouseRange()
        minE, maxE = self.setupColorData(x, kwargs)
        self.setupBarItem(kwargs, minE, maxE)
        spots = self.buildSpots(x, y, kwargs)
        self.addScatterPoints(spots, kwargs)
        isoLevels = kwargs.get("isoLevels", 0)
        if isoLevels != 0 and "z" in kwargs:
            self.addIsoItemHorizon(x, y, kwargs["z"], levels=isoLevels)
