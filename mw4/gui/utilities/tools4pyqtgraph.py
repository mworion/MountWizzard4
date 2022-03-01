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
from datetime import datetime as dt

# external packages
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QFont

# local imports
from gui.utilities.stylesQtCss import Styles

__all__ = [
    'PlotImageBar',
]


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseMode(self.RectMode)

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.MouseButton.RightButton:
            self.autoRange()
            self.enableAutoRange(x=True, y=True)


class PlotBase(pg.PlotWidget, Styles):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(viewBox=CustomViewBox())
        pg.setConfigOptions(antialias=True,
                            imageAxisOrder='row-major')

        self.pen = pg.mkPen(color=self.M_BLUE, width=2)
        self.penGrid = pg.mkPen(color=self.M_GREY)
        self.brushGrid = pg.mkBrush(color=self.M_GREY + '80')
        self.setBackground(self.M_BACK)
        self.cMapGYR = pg.ColorMap([0, 0.6, 1.0],
                                   [self.M_GREEN, self.M_YELLOW, self.M_RED])
        self.defRange = {}
        self.plotItem = self.getPlotItem()
        self.scatterItem = None
        self.imageItem = None

        self.viewBox = self.plotItem.getViewBox()
        self.viewBox.rbScaleBox.setPen(self.pen)
        self.viewBox.rbScaleBox.setBrush(self.brushGrid)

        self.barItem = pg.ColorBarItem(width=15, interactive=False)
        self.barItem.setVisible(False)

        self.plotItem.layout.addItem(self.barItem, 2, 5)
        self.plotItem.layout.setColumnFixedWidth(4, 5)
        self.plotItem.getViewBox().setMenuEnabled(False)
        self.plotItem.hideButtons()
        for side in ('left', 'top', 'right', 'bottom'):
            self.plotItem.getAxis(side).setPen(self.pen)
            self.plotItem.getAxis(side).setTextPen(self.pen)
            self.plotItem.getAxis(side).setGrid(32)
            self.barItem.getAxis(side).setPen(self.pen)
            self.barItem.getAxis(side).setTextPen(self.pen)

    def colorChange(self):
        """
        :return:
        """
        self.pen = pg.mkPen(color=self.M_BLUE)
        self.penGrid = pg.mkPen(color=self.M_GREY)
        self.setBackground(self.M_BACK)
        for side in ('left', 'top', 'right', 'bottom'):
            self.plotItem.getAxis(side).setPen(self.pen)
            self.plotItem.getAxis(side).setTextPen(self.pen)
            self.barItem.getAxis(side).setPen(self.pen)
            self.barItem.getAxis(side).setTextPen(self.pen)
        return True


class NormalScatter(PlotBase):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plotItem.showAxes(True, showValues=True)
        self.colorInx = None
        self.col = None

    def plot(self, x, y, **kwargs):
        """
        :param x:
        :param y:
        :param kwargs:
        :return:
        """
        self.plotItem.clear()
        self.scatterItem = pg.ScatterPlotItem(hoverable=True,
                                              hoverSize=10, hoverPen=self.pen)
        self.plotItem.addItem(self.scatterItem)
        self.defRange = kwargs.get('range', {})
        xMin = self.defRange['xMin'] = self.defRange.get('xMin', np.min(x) * 1.1)
        yMin = self.defRange['yMin'] = self.defRange.get('yMin', np.min(y) * 1.1)
        xMax = self.defRange['xMax'] = self.defRange.get('xMax', np.max(x) * 1.1)
        yMax = self.defRange['yMax'] = self.defRange.get('yMax', np.max(y) * 1.1)

        if kwargs.get('limits', True):
            self.plotItem.setLimits(xMin=xMin, xMax=xMax,
                                    yMin=yMin, yMax=yMax,
                                    minXRange=(xMax - xMin) / 2,
                                    maxXRange=(xMax - xMin),
                                    minYRange=(yMax - yMin) / 2,
                                    maxYRange=(yMax - yMin))
        self.plotItem.setRange(QRectF(xMin, yMin, xMax - xMin, yMax - yMin))
        self.plotItem.autoRange()

        dataVal = kwargs.get('data', y)
        self.col = kwargs.get('color', self.M_BLUE)
        if isinstance(self.col, (str, QColor)):
            self.col = [self.col] * len(x)

        if 'z' in kwargs:
            z = kwargs.get('z')
            err = np.abs(z)
            minE = np.min(err)
            maxE = np.max(err)
            self.colorInx = (err - minE) / (maxE - minE)

        hasBar = kwargs.get('bar', False)
        if hasBar and 'z' in kwargs:
            self.barItem.setVisible(True)
            self.barItem.setLevels(values=(minE, maxE))
            self.barItem.setColorMap(self.cMapGYR)

        spots = []
        for i in range(len(x)):
            if 'z' in kwargs:
                colorVal = self.cMapGYR.mapToQColor(self.colorInx[i])
            else:
                colorVal = self.col[i]
            spots.append(
                {'pos': (x[i], y[i]),
                 'data': dataVal[i],
                 'brush': colorVal,
                 'pen': colorVal,
                 'size': 6,
                 })
        tip = kwargs.get('tip')
        if tip is None:
            self.scatterItem.addPoints(spots)
        else:
            self.scatterItem.addPoints(spots, tip=tip)
        return True


class PolarScatter(NormalScatter):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plotItem.showAxes(False, showValues=False)
        self.plotItem.setAspectLocked(True)

    def setGrid(self, y, **kwargs):
        """
        :param y:
        :param kwargs:
        :return:
        """
        if kwargs.get('reverse', False):
            maxR = 90
            stepLines = 10
            gridLines = range(10, maxR, stepLines)
            circle = pg.QtGui.QGraphicsEllipseItem(-maxR, -maxR, maxR * 2, maxR * 2)
            circle.setPen(self.pen)
            self.plotItem.addItem(circle)
        else:
            maxR = int(np.max(y))
            stepLines = 5
            gridLines = np.arange(0, maxR, stepLines)

        self.plotItem.addLine(x=0, pen=self.penGrid)
        self.plotItem.addLine(y=0, pen=self.penGrid)

        font = QFont(self.window().font().family(),
                     int(self.window().font().pointSize() * 1.1))
        for r in gridLines:
            circle = pg.QtGui.QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            circle.setPen(self.penGrid)
            self.plotItem.addItem(circle)
            if kwargs.get('reverse', False):
                text = f'{90 - r}'
            else:
                text = f'{r}'
            textItem = pg.TextItem(text=text, color=self.M_GREY, anchor=(0.5, 0.5))
            textItem.setFont(font)
            textItem.setPos(r * 0.7, r * 0.7)
            self.plotItem.addItem(textItem)

        for text, x, y in zip(
                ['N', 'E', 'S', 'W', 'NE', 'SE', 'SW', 'NW'],
                [0, maxR, 0, -maxR, maxR * 0.7, maxR * 0.7, -maxR * 0.7, - maxR * 0.7],
                [maxR, 0, -maxR, 0, maxR * 0.7, - maxR * 0.7, - maxR * 0.7, maxR * 0.7]):
            textItem = pg.TextItem(color=self.M_BLUE, anchor=(0.5, 0.5))
            textItem.setHtml(f'<b>{text}</b>')
            textItem.setFont(font)
            textItem.setPos(x, y)
            self.plotItem.addItem(textItem)
        return True

    def plot(self, x, y, **kwargs):
        """
        :param x: azimuth
        :param y: altitude
        :param kwargs:
        :return:
        """
        x = np.radians(90 - x)
        if kwargs.get('reverse', False):
            posX = (90 - y) * np.cos(x)
            posY = (90 - y) * np.sin(x)
        else:
            posX = y * np.cos(x)
            posY = y * np.sin(x)

        super().plot(posX, posY, limits=False, **kwargs)
        self.setGrid(y, **kwargs)

        ang = kwargs.get('ang')
        if ang is None:
            return False
        ang = np.degrees(ang)

        for i in range(len(x)):
            arrow = pg.ArrowItem()
            if 'z' in kwargs:
                colorVal = self.cMapGYR.mapToQColor(self.colorInx[i])
            else:
                colorVal = self.col[i]
            arrow.setStyle(angle=ang[i] - 90,
                           tipAngle=0,
                           headLen=0,
                           tailWidth=1,
                           tailLen=12,
                           pen=pg.mkPen(color=colorVal),
                           brush=pg.mkBrush(color=colorVal),
                           )
            arrow.setPos(posX[i], posY[i])
            self.plotItem.addItem(arrow)
        return True

    def plotLoc(self, lat):
        """
        :param lat:
        :return:
        """
        circle = pg.QtGui.QGraphicsEllipseItem(-3, -3, 6, 6)
        circle.setPen(pg.mkPen(color=self.M_BLUE))
        circle.setBrush(pg.mkBrush(color=self.M_BLUE))
        circle.setPos(0, lat)
        self.plotItem.addItem(circle)
        circle = pg.QtGui.QGraphicsEllipseItem(-10, -10, 20, 20)
        circle.setPen(pg.mkPen(color=self.M_BLUE, width=2))
        circle.setPos(0, lat)
        self.plotItem.addItem(circle)
        return True


class PlotImageBar(PlotBase):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lx = None
        self.ly = None
        for side in ('left', 'top', 'right', 'bottom'):
            self.plotItem.getAxis(side).setGrid(0)
        self.defRange = {}

    def constructPlot(self):
        """
        :return:
        """
        self.plotItem.clear()
        self.imageItem = pg.ImageItem()
        self.plotItem.addItem(self.imageItem)
        self.barItem.setVisible(True)
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

    def setImage(self, imageDisp, **kwargs):
        """
        :param imageDisp:
        :param kwargs:
        :return:
        """
        self.constructPlot()
        self.imageItem.setImage(imageDisp)
        y, x = imageDisp.shape

        self.defRange = kwargs.get('range', {})
        xMin = self.defRange['xMin'] = self.defRange.get('xMin', 0)
        yMin = self.defRange['yMin'] = self.defRange.get('yMin', 0)
        xMax = self.defRange['xMax'] = self.defRange.get('xMax', x)
        yMax = self.defRange['yMax'] = self.defRange.get('yMax', y)

        if kwargs.get('limits', True):
            self.plotItem.setLimits(xMin=xMin, xMax=xMax,
                                    yMin=yMin, yMax=yMax)
        self.plotItem.setRange(QRectF(xMin, yMin, xMax - xMin, yMax - yMin))
        self.plotItem.autoRange()

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
                           color=self.M_BLUE)
        text.setPos(posX, posY)
        self.plotItem.addItem(text)
        return True


class TimeAxis(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        ticks = []
        for x in values:
            lStr = dt.fromtimestamp(x).strftime('%H:%M:%S')
            ticks.append(lStr)
        return ticks


class PlotMeasure(PlotBase):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plotDataItem = pg.PlotDataItem()
        self.plotItem.addItem(self.plotDataItem)

        self.plotItem.showAxes(True, showValues=True)
        self.plotItem.setAxisItems({'bottom': TimeAxis(orientation='bottom')})
        self.plotItem.setClipToView(True)

        self.plotDataItem.setDownsampling(method='mean')
        self.plotDataItem.setPen(self.M_BLUE, width=2)

        for side in ('left', 'top', 'right', 'bottom'):
            self.plotItem.getAxis(side).setPen(self.pen)
            self.plotItem.getAxis(side).setTextPen(self.pen)
            self.plotItem.getAxis(side).setGrid(128)
