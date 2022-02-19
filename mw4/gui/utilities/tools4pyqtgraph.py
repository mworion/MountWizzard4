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
    'MW_PlotWidget',
]


class PlotImageBar(pg.PlotWidget, Styles):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        pg.setConfigOptions(antialias=True,
                            imageAxisOrder='row-major')
        self.setBackground(self.M_BACK)
        self.plotItem = self.getPlotItem()
        self.imageItem = pg.ImageItem()
        self.barItem = pg.ColorBarItem()
        self.pen = pg.mkPen(color=self.M_BLUE)
        self.lx = None
        self.ly = None

        self.plotItem.addItem(self.imageItem)
        self.barItem.setImageItem(self.imageItem, insert_in=self.plotItem)
        self.lx = self.plotItem.addLine(x=0, pen=self.pen)
        self.ly = self.plotItem.addLine(y=0, pen=self.pen)

        self.plotItem.getViewBox().setMenuEnabled(False)
        self.plotItem.showAxes((True, True, True, True))
        for side in ('left', 'top', 'right', 'bottom'):
            self.plotItem.getAxis(side).setPen(self.pen)
            self.plotItem.getAxis(side).setTextPen(self.pen)
            self.barItem.getAxis(side).setPen(self.pen)
            self.barItem.getAxis(side).setTextPen(self.pen)

        self.plotItem.hideButtons()
        self.plotItem.setLabel('left', text='[Pixel]')
        self.plotItem.setLabel('bottom', text='[Pixel]')
        self.barItem.setLabel('right', text='ADU')

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

    def clearItems(self, itemType):
        delList = [x for x in self.plotItem.items if isinstance(x, itemType)]
        for item in delList:
            self.plotItem.removeItem(item)

