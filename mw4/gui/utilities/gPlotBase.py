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
from PySide6.QtGui import QPainterPath, QFont
from PySide6.QtWidgets import QApplication
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter

# local imports
from gui.styles.styles import Styles
from gui.utilities.gCustomViewBox import CustomViewBox


class PlotBase(pg.GraphicsLayoutWidget, Styles):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, show=True)
        pg.setConfigOptions(antialias=True, imageAxisOrder="row-major")

        self.pen = pg.mkPen(color=self.M_PRIM, width=1)
        self.penPink = pg.mkPen(color=self.M_PINK, width=1)
        self.brush = pg.mkBrush(color=self.M_PRIM + "80")
        self.penGrid = pg.mkPen(color=self.M_SEC)
        self.brushGrid = pg.mkBrush(color=self.M_SEC + "80")
        self.penHorizon = pg.mkPen(color=self.M_PRIM + "80", width=1)
        self.brushHorizon = pg.mkBrush(color=self.M_PRIM2 + "40")
        self.setBackground(self.M_BACK)
        self.cMapGYR = pg.ColorMap([0, 0.6, 1.0], [self.M_GREEN, self.M_YELLOW, self.M_RED])
        self.defRange = {}
        self.scatterItem = None
        self.imageItem = None
        self.barItem = None
        self.horizon = None
        self.p = []
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.setupItems()
        self.colorChange()

    def colorChange(self):
        """
        :return:
        """
        self.pen = pg.mkPen(color=self.M_PRIM, width=1)
        self.brush = pg.mkBrush(color=self.M_PRIM + "80")
        self.penGrid = pg.mkPen(color=self.M_SEC)
        self.brushGrid = pg.mkBrush(color=self.M_SEC + "80")
        self.penHorizon = pg.mkPen(color=self.M_PRIM + "80", width=1)
        self.brushHorizon = pg.mkBrush(color=self.M_PRIM2 + "40")
        self.setBackground(self.M_BACK)
        for side in ("left", "top", "right", "bottom"):
            for plotItem in self.p:
                plotItem.getAxis(side).setPen(self.pen)
                plotItem.getAxis(side).setTextPen(self.pen)
            if self.barItem:
                self.barItem.getAxis(side).setPen(self.pen)
                self.barItem.getAxis(side).setTextPen(self.pen)
        return True

    def setupItems(self):
        """
        :return:
        """
        for plotItem in self.p:
            plotItem.getViewBox().setMouseMode(pg.ViewBox().RectMode)
            plotItem.getViewBox().rbScaleBox.setPen(self.pen)
            plotItem.getViewBox().rbScaleBox.setBrush(self.brushGrid)
            plotItem.getViewBox().setMenuEnabled(False)
            plotItem.hideButtons()
            plotItem.disableAutoRange()
            plotItem.setOwnedByLayout(True)
            plotItem.showAxes(False, showValues=False)
            for side in ("left", "top", "right", "bottom"):
                plotItem.getAxis(side).setPen(self.pen)
                plotItem.getAxis(side).setTextPen(self.pen)
                plotItem.getAxis(side).setGrid(32)

    def addBarItem(self, interactive=False, plotItem=None):
        """
        :param interactive:
        :param plotItem:
        :return:
        """
        if plotItem is None:
            plotItem = self.p[0]
        self.barItem = pg.ColorBarItem(width=15, interactive=interactive, rounding=0.025)
        self.barItem.setVisible(False)
        for side in ("left", "top", "right", "bottom"):
            self.barItem.getAxis(side).setPen(self.pen)
            self.barItem.getAxis(side).setTextPen(self.pen)
        plotItem.layout.addItem(self.barItem, 2, 5)
        plotItem.layout.setColumnFixedWidth(4, 5)
        return True

    @staticmethod
    def toPolar(az, alt):
        az = np.array(az)
        alt = np.array(alt)
        theta = np.radians(90 - az)
        x = (90 - alt) * np.cos(theta)
        y = (90 - alt) * np.sin(theta)
        return x, y

    @staticmethod
    def findItemByName(plotItem, name):
        for item in plotItem.items:
            if hasattr(item, "nameStr"):
                if item.nameStr == name:
                    return item
        return None

    def drawHorizon(self, horizonP, plotItem=None, polar=False):
        """
        :param horizonP:
        :param plotItem:
        :param polar:
        :return:
        """
        if plotItem is None:
            plotItem = self.p[0]

        plotItem.removeItem(self.findItemByName(plotItem, "horizon"))
        if len(horizonP) == 0:
            return False
        if not self.p[0].items:
            return False

        alt, az = zip(*horizonP)
        alt = np.array(alt)
        az = np.array(az)
        path = QPainterPath()
        if not polar:
            altF = np.concatenate([[0], [alt[0]], alt, [alt[-1]], [0]])
            azF = np.concatenate([[0], [0], az, [360], [360]])
        else:
            azF, altF = self.toPolar(az, alt)
            path.addEllipse(-90, -90, 180, 180)

        horPath = pg.arrayToQPath(azF, altF)
        path.addPath(horPath)
        horItem = pg.QtWidgets.QGraphicsPathItem(path)
        horItem.setPen(self.penHorizon)
        horItem.setBrush(self.brushHorizon)
        horItem.setZValue(-5)
        horItem.nameStr = "horizon"
        plotItem.addItem(horItem)
        return True

    def addIsoBasic(self, plotItem, zm, levels=10):
        """
        :param plotItem:
        :param zm:
        :param levels:
        :return:
        """
        minE = np.min(zm)
        maxE = np.max(zm)

        for level in np.linspace(minE, maxE, levels):
            colorInx = (level - minE) / (maxE - minE)
            colorVal = self.cMapGYR.mapToQColor(colorInx)
            colorVal.setAlpha(128)

            pd = pg.IsocurveItem()
            pd.setData(zm, level)
            pd.setZValue(10)
            pg.nameStr = "iso"
            pd.setPen(pg.mkPen(color=colorVal))
            plotItem.addItem(pd)
            QApplication.processEvents()
        return True

    def addIsoItem(self, x, y, z, plotItem=None, rangeX=None, rangeY=None, levels=20):
        """
        :param x:
        :param y:
        :param z:
        :param plotItem:
        :param rangeX:
        :param rangeY:
        :param levels:
        :return:
        """
        if plotItem is None:
            plotItem = self.p[0]
        if rangeX is None:
            rangeX = np.linspace(0, 360, 360)
        if rangeY is None:
            rangeY = np.linspace(0, 90, 90)

        xm, ym = np.meshgrid(rangeX, rangeY)
        zm = griddata((x, y), z, (xm, ym), method="linear", fill_value=np.min(z))
        zm = uniform_filter(zm, size=10)
        self.addIsoBasic(plotItem, zm, levels)
        return True

    def addIsoItemHorizon(self, x, y, z, plotItem=None, levels=20):
        """
        :param x:
        :param y:
        :param z:
        :param plotItem:
        :param levels:
        :return:
        """
        z = np.abs(z)
        az = np.concatenate([x - 360, x, x + 360])
        alt = np.concatenate([y, y, y])
        err = np.concatenate([z, z, z])
        self.addIsoItem(az, alt, err, plotItem=plotItem, levels=levels)
        return True

    def setGrid(self, y=0, plotItem=None, **kwargs):
        """
        :param y:
        :param plotItem:
        :param kwargs:
        :return:
        """
        if plotItem is None:
            plotItem = self.p[0]
        textAngle = np.radians(150)
        if kwargs.get("reverse", False):
            maxR = 90
            stepLines = 10
            gridLines = range(10, maxR, stepLines)
            circle = pg.QtWidgets.QGraphicsEllipseItem(-maxR, -maxR, maxR * 2, maxR * 2)
            circle.setPen(self.pen)
            plotItem.addItem(circle)
        else:
            maxR = int(np.max(y))
            steps = 7
            gridLines = np.round(np.linspace(0, maxR, steps), 1)

        plotItem.addLine(x=0, pen=self.penGrid)
        plotItem.addLine(y=0, pen=self.penGrid)

        font = QFont(
            self.window().font().family(), int(self.window().font().pointSize() * 1.1)
        )
        for r in gridLines:
            circle = pg.QtWidgets.QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            circle.setPen(self.penGrid)
            plotItem.addItem(circle)
            if kwargs.get("reverse", False):
                text = f"{90 - r}"
            else:
                text = f"{r}"
            textItem = pg.TextItem(text=text, color=self.M_PRIM, anchor=(0.5, 0.5))
            textItem.setFont(font)
            textItem.setPos(r * np.cos(textAngle), r * np.sin(textAngle))
            plotItem.addItem(textItem)

        maxL = maxR * 1.1
        for text, x, y in zip(
            ["N", "E", "S", "W", "NE", "SE", "SW", "NW"],
            [0, maxL, 0, -maxL, maxL * 0.75, maxL * 0.75, -maxL * 0.75, -maxL * 0.75],
            [maxL, 0, -maxL, 0, maxL * 0.75, -maxL * 0.75, -maxL * 0.75, maxL * 0.75],
        ):
            textItem = pg.TextItem(color=self.M_PRIM, anchor=(0.5, 0.5))
            textItem.setHtml(f"<b>{text}</b>")
            textItem.setFont(font)
            textItem.setPos(x, y)
            plotItem.addItem(textItem)
        return True

    def plotLoc(self, lat, plotItem=None):
        """
        :param lat:
        :param plotItem:
        :return:
        """
        if plotItem is None:
            plotItem = self.p[0]
        circle = pg.QtWidgets.QGraphicsEllipseItem(-2, -2, 4, 4)
        circle.setPen(self.pen)
        circle.setBrush(self.brush)
        circle.setPos(0, 90 - lat)
        plotItem.addItem(circle)
        circle = pg.QtWidgets.QGraphicsEllipseItem(-4, -4, 8, 8)
        circle.setPen(self.pen)
        circle.setPos(0, 90 - lat)
        plotItem.addItem(circle)
        circle = pg.QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
        circle.setPen(self.pen)
        circle.setPos(0, 90 - lat)
        plotItem.addItem(circle)
        return True
