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
from PySide6.QtGui import QTransform

# local imports
from gui.utilities.gPlotBase import PlotBase


class ImageBar(PlotBase):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lx = None
        self.ly = None
        self.setupItems()
        self.addBarItem(interactive=True)
        self.barItem.setVisible(True)
        for side in ("left", "top", "right", "bottom"):
            self.p[0].getAxis(side).setGrid(0)
        self.defRange = {}

    def constructPlot(self):
        """
        :return:
        """
        self.p[0].clear()
        self.p[0].showAxes(True, showValues=True)
        self.imageItem = pg.ImageItem()
        self.p[0].addItem(self.imageItem)
        self.barItem.setImageItem(self.imageItem, insert_in=self.p[0])
        self.lx = self.p[0].addLine(x=0, pen=pg.mkPen(color=self.M_YELLOW))
        self.ly = self.p[0].addLine(y=0, pen=pg.mkPen(color=self.M_YELLOW))
        self.lx.setVisible(False)
        self.ly.setVisible(False)
        return True

    def setColorMap(self, colorMap):
        """
        :param colorMap:
        :return:
        """
        cMap = pg.colormap.get(colorMap)
        self.barItem.setColorMap(cMap)
        return True

    def setImage(self, imageDisp, updateGeometry=True):
        """
        :param imageDisp:
        :param updateGeometry:
        :return:
        """
        self.constructPlot()
        self.imageItem.setImage(imageDisp)
        if imageDisp is None:
            return False
        yMax, xMax = imageDisp.shape
        xMinR = max(xMax / 100, 100)
        yMinR = max(yMax / 100, 100)
        self.p[0].setLimits(
            xMin=0, xMax=xMax, yMin=0, yMax=yMax, minXRange=xMinR, minYRange=yMinR
        )
        if updateGeometry:
            self.p[0].getViewBox().rightMouseRange()

        med = np.median(imageDisp)
        minB = 1.5 * med
        maxB = 5 * med
        if (maxB - minB) > 1:
            self.barItem.setLevels(values=(minB, maxB))
        self.lx.setPos((xMax / 2, 0))
        self.ly.setPos((0, yMax / 2))
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
        ellipse = pg.QtWidgets.QGraphicsEllipseItem(-a, -b, 2 * a + 1, 2 * b + 1)
        ellipse.setPos(x, y)
        tr = QTransform()
        tr.rotate(np.degrees(theta))
        ellipse.setTransform(tr)
        ellipse.setPen(self.penPink)
        self.p[0].addItem(ellipse)
        return ellipse

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
        text = pg.TextItem(text=f"{value:2.2f}", color=self.M_PRIM)
        text.setPos(posX, posY)
        self.p[0].addItem(text)
        return True
