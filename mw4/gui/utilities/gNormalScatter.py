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

# external packages
import numpy as np
import pyqtgraph as pg
from PySide6.QtGui import QColor

# local imports
from gui.utilities.gPlotBase import PlotBase


class NormalScatter(PlotBase):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupItems()
        self.colorInx = None
        self.col = None
        self.p[0].setVisible(True)

    def plot(self, x, y, **kwargs):
        """
        :param x:
        :param y:
        :param kwargs:
        :return:
        """
        self.p[0].clear()
        self.p[0].showAxes(True, showValues=True)
        self.scatterItem = pg.ScatterPlotItem(hoverable=True, hoverSize=10, hoverPen=self.pen)
        self.p[0].addItem(self.scatterItem)
        self.defRange = kwargs.get("range", {})

        xMin = self.defRange.get("xMin", np.min(x))
        yMin = self.defRange.get("yMin", np.min(y))
        xMax = self.defRange.get("xMax", np.max(x))
        yMax = self.defRange.get("yMax", np.max(y))

        if kwargs.get("limits", True):
            if xMin is not None and xMax is not None:
                self.p[0].setLimits(
                    xMin=xMin,
                    xMax=xMax,
                    minXRange=(xMax - xMin) / 4,
                    maxXRange=(xMax - xMin),
                )
                self.p[0].setXRange(xMin, xMax - xMin)
            if yMin is not None and yMax is not None:
                self.p[0].setLimits(
                    yMin=yMin,
                    yMax=yMax,
                    minYRange=(yMax - yMin) / 4,
                    maxYRange=(yMax - yMin),
                )
                self.p[0].setYRange(yMin, yMax - yMin)
        self.p[0].getViewBox().rightMouseRange()

        dataVal = kwargs.get("data", y)
        self.col = kwargs.get("color", self.M_PRIM)
        if isinstance(self.col, (str, QColor)):
            self.col = [self.col] * len(x)

        if "z" in kwargs:
            z = kwargs.get("z")
            err = np.abs(z)
            minE = np.min(err)
            maxE = np.max(err)
            divisor = max((maxE - minE), 0.1)
            self.colorInx = (err - minE) / divisor

        hasBar = kwargs.get("bar", False)
        if hasBar and "z" in kwargs:
            self.barItem.setVisible(True)
            self.barItem.setLevels(values=(minE, maxE))
            self.barItem.setColorMap(self.cMapGYR)

        spots = []
        for i in range(len(x)):
            if "z" in kwargs:
                colorVal = self.cMapGYR.mapToQColor(self.colorInx[i])
            else:
                colorVal = self.col[i]
            spots.append(
                {
                    "pos": (x[i], y[i]),
                    "data": dataVal[i],
                    "brush": colorVal,
                    "pen": colorVal,
                    "size": 6,
                }
            )
        tip = kwargs.get("tip")
        if tip is None:
            self.scatterItem.addPoints(spots)
        else:
            self.scatterItem.addPoints(spots, tip=tip)

        isoLevels = kwargs.get("isoLevels", 0)
        if isoLevels != 0 and "z" in kwargs:
            self.addIsoItemHorizon(x, y, z, levels=isoLevels)
        return True
