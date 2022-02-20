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
import logging

# external packages
import numpy as np
import pyqtgraph as pg

# local imports
from gui.utilities.stylesQtCss import Styles

__all__ = [
    'PlotImageBar',
]


class PlotNormal(pg.PlotWidget, Styles):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pg.setConfigOptions(antialias=True,
                            imageAxisOrder='row-major')
        self.setBackground(self.M_BACK)
        self.plotItem = self.getPlotItem()
        self.pen = pg.mkPen(color=self.M_BLUE)
        self.plotItem.getViewBox().setMenuEnabled(False)
        self.plotItem.showAxes((True, True, True, True))
        self.plotItem.hideButtons()
        for side in ('left', 'top', 'right', 'bottom'):
            self.plotItem.getAxis(side).setPen(self.pen)
            self.plotItem.getAxis(side).setTextPen(self.pen)


class PlotNormalScatterPier(PlotNormal):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatterItem = None
        self.plotItem.setMouseEnabled(x=False, y=False)

    def constructPlot(self, dec=False):
        """
        :return:
        """
        self.plotItem.clear()
        self.scatterItem = pg.ScatterPlotItem(pen=pg.mkPen(None),
                                              hoverable=True,
                                              hoverSymbol='s',
                                              hoverSize=15,
                                              hoverPen=self.pen,
                                              )
        self.plotItem.addItem(self.scatterItem)
        if dec:
            ticksX = [
                [(x, f'{x}') for x in range(-60, 90, 30)],
                [(x, '') for x in range(-75, 90, 15)],
            ]
            self.plotItem.setLimits(xMin=-90, xMax=90)
            self.plotItem.setRange(xRange=(-90, 90), padding=0)
        else:
            ticksX = [
                [(x, f'{x}') for x in range(30, 180, 30)],
                [(x, '') for x in range(15, 180, 15)],
            ]
            self.plotItem.setLimits(xMin=0, xMax=180)
            self.plotItem.setRange(xRange=(0, 180), padding=0)
        self.plotItem.getAxis('bottom').setTicks(ticksX)
        self.plotItem.getAxis('top').setTicks(ticksX)
        self.plotItem.getAxis('bottom').setGrid(64)
        self.plotItem.getAxis('left').setGrid(64)
        self.plotItem.getAxis('right').setGrid(64)

    def plot(self, x, y, pier, dec=False):
        self.constructPlot(dec)

        spots = [{'pos': (x[i], y[i]),
                  'data': f'{y[i]:4.1f}',
                  'brush': self.M_YELLOW if pier[i] == 'E' else self.M_GREEN,
                  } for i in range(len(x))]
        self.scatterItem.addPoints(spots)


class PlotNormalScatter(PlotNormal):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatterItem = None
        self.plotItem.setLimits(xMin=0, yMin=0, xMax=360, yMax=90)
        self.plotItem.setMouseEnabled(x=False, y=False)
        self.plotItem.setRange(xRange=(0, 360), yRange=(0, 90), padding=0)

    def constructPlot(self):
        """
        :return:
        """
        self.plotItem.clear()
        self.scatterItem = pg.ScatterPlotItem(pen=pg.mkPen(None),
                                              hoverable=True,
                                              hoverSymbol='s',
                                              hoverSize=15,
                                              hoverPen=self.pen,
                                              )
        self.plotItem.addItem(self.scatterItem)
        ticksX = [
            [(x, f'{x}') for x in range(30, 360, 30)],
            [(x, '') for x in range(15, 360, 15)],
        ]
        self.plotItem.getAxis('bottom').setTicks(ticksX)
        self.plotItem.getAxis('top').setTicks(ticksX)
        self.plotItem.getAxis('bottom').setGrid(64)
        ticksY = [
            [(x, f'{x}') for x in range(10, 90, 10)],
            [(x, '') for x in range(15, 90, 5)],
        ]
        self.plotItem.getAxis('left').setTicks(ticksY)
        self.plotItem.getAxis('right').setTicks(ticksY)
        self.plotItem.getAxis('left').setGrid(64)

    def plot(self, x, y, z):
        self.constructPlot()
        err = np.abs(z)
        minE = np.min(err)
        maxE = np.max(err)
        val = (err - minE) / (maxE - minE)
        cMap = pg.colormap.get('CET-D3')
        spots = [{'pos': (x[i], y[i]),
                  'data': f'{err[i]:4.1f}',
                  'brush': cMap.mapToQColor(val[i]),
                  } for i in range(len(x))]
        self.scatterItem.addPoints(spots)


class PlotImageBar(PlotNormal):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.imageItem = None
        self.barItem = pg.ColorBarItem()
        self.lx = None
        self.ly = None
        for side in ('left', 'top', 'right', 'bottom'):
            self.barItem.getAxis(side).setPen(self.pen)
            self.barItem.getAxis(side).setTextPen(self.pen)

    def constructPlot(self):
        """
        :return:
        """
        self.plotItem.clear()
        self.imageItem = pg.ImageItem()
        self.plotItem.addItem(self.imageItem)
        self.barItem.setImageItem(self.imageItem, insert_in=self.plotItem)
        self.lx = self.plotItem.addLine(x=0, pen=self.pen)
        self.ly = self.plotItem.addLine(y=0, pen=self.pen)
        self.lx.setVisible(False)
        self.ly.setVisible(False)

    def setColorMap(self, colorMap):
        """
        :param colorMap:
        :return:
        """
        cMap = pg.colormap.get(colorMap)
        self.barItem.setColorMap(cMap)
        return True

    def setImage(self, imageDisp):
        """
        :param imageDisp:
        :return:
        """
        self.constructPlot()
        self.imageItem.setImage(imageDisp)
        y, x = imageDisp.shape
        self.plotItem.setLimits(xMin=0, xMax=x, yMin=0, yMax=y)
        self.plotItem.setRange(xRange=(0, x), yRange=(0, y))
        minB = np.min(imageDisp)
        maxB = 2 * np.mean(imageDisp)
        self.barItem.setLevels(values=(minB, maxB))
        self.lx.setPos((x / 2, 0))
        self.ly.setPos((0, y / 2))
        return True

    def showCrosshair(self, value):
        """
        :param value:
        :return:
        """
        if self.lx:
            self.lx.setVisible(value)
        if self.ly:
            self.ly.setVisible(value)
        return True

    def addEllipse(self, x, y, a, b, theta):
        """
        :return:
        """
        d = 2
        w = (abs(np.cos(theta)) * a + abs(np.sin(theta)) * b) * d
        h = (abs(np.sin(theta)) * a + abs(np.cos(theta)) * b) * d
        ellipse = pg.QtGui.QGraphicsEllipseItem(x - w, y - h,
                                                2 * w, 2 * h)
        ellipse.setPen(self.pen)
        self.plotItem.addItem(ellipse)
        return True

    def addValueAnnotation(self, x, y, value):
        """
        :param x:
        :param y:
        :param value:
        :return:
        """
        d = 3
        posX = x + d
        posY = y + d
        text = pg.TextItem(text=f'{value:2.2f}',
                           anchor=(0, 0),
                           color=self.M_BLUE,
                           angle=0)
        text.setPos(posX, posY)
        self.plotItem.addItem(text)
        return True
