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
