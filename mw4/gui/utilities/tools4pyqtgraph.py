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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QTransform, QPainterPath
from PyQt5.QtWidgets import QApplication
from scipy.interpolate import griddata
from scipy.ndimage import uniform_filter

# local imports
from gui.utilities.stylesQtCss import Styles

__all__ = [
    'ImageBar',
    'PlotBase',
    'NormalScatter',
    'PolarScatter',
    'Measure',
    'CustomViewBox',
    'TimeMeasure'
]


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plotDataItem = None
        self.dragOffset = None
        self.dragPoint = None
        self.enableLimitX = None
        self.epsilonCurve = 2
        self.epsilonFree = 360
        self.setOpts(*args, **kwargs)

    def setPlotDataItem(self, plotDataItem):
        """
        :param plotDataItem:
        :return:
        """
        self.plotDataItem = plotDataItem
        return True

    def setOpts(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        self.enableLimitX = kwargs.get('enableLimitX', False)
        return True

    def updateData(self, x, y):
        """
        :param x:
        :param y:
        :return:
        """
        self.plotDataItem.setData(x=x, y=y)
        return True

    @staticmethod
    def callbackMDC(ev, posView):
        return True

    @staticmethod
    def distance(a, b):
        """
        :param a:
        :param b:
        :return:
        """
        return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def isBetween(self, a, b, c):
        """
        :param a:
        :param b:
        :param c:
        :return:
        """
        d = self.distance(a, c) + self.distance(c, b) - self.distance(a, b)
        return np.abs(d)

    def getCurveIndex(self, pos):
        """
        :param pos:
        :return:
        """
        data = self.plotDataItem.curve.getData()
        curve = [(x, y) for x, y in zip(data[0], data[1])]
        for index in range(0, len(curve) - 1):
            d = self.isBetween(curve[index], curve[index + 1], (pos.x(), pos.y()))
            if d < self.epsilonCurve:
                break
        else:
            return None
        return index + 1

    def getNearestPointIndex(self, pos):
        """
        :param pos:
        :return: index or none
        """
        data = self.plotDataItem.curve.getData()
        if len(data[0]) == 0:
            return 0
        x = data[0]
        y = data[1]
        d = np.sqrt((x - pos.x()) ** 2 / 4 + (y - pos.y()) ** 2)
        index = int(d.argsort()[:1][0])
        if d[index] >= self.epsilonFree:
            return None
        return index + 1

    def addUpdate(self, index, pos):
        """
        :param index:
        :param pos:
        :return:
        """
        data = self.plotDataItem.getData()
        x = data[0]
        y = data[1]
        if x is not None and y is not None:
            x = np.concatenate((x[0:index], [pos.x()], x[index:]))
            y = np.concatenate((y[0:index], [pos.y()], y[index:]))
        else:
            x = np.array([pos.x()])
            y = np.array([pos.y()])
        self.updateData(x=x, y=y)
        return True

    def delUpdate(self, index):
        """
        :param index:
        :return:
        """
        data = self.plotDataItem.getData()
        x = data[0]
        y = data[1]
        if x is None and y is None:
            return False
        x = np.delete(x, index)
        y = np.delete(y, index)
        self.updateData(x=x, y=y)
        return True

    def checkLimits(self, data, index, pos):
        """
        :param data:
        :param index:
        :param pos:
        :return:
        """
        xRange = self.state['limits']['xLimits']
        yRange = self.state['limits']['yLimits']
        px = pos.x()
        py = pos.y()
        if None not in xRange:
            if pos.x() > xRange[1]:
                px = xRange[1]
            elif pos.x() < xRange[0]:
                px = xRange[0]
        if None not in yRange:
            if pos.y() > yRange[1]:
                py = yRange[1]
            elif pos.y() < yRange[0]:
                py = yRange[0]

        x = data[0]
        y = data[1]
        x[index] = px
        y[index] = py
        if not self.enableLimitX:
            return x, y

        if index == 0:
            x[index] = np.minimum(px, x[index + 1])
        elif index == len(x) - 1:
            x[index] = np.maximum(x[index - 1], px)
        else:
            if px < x[index - 1]:
                x[index] = x[index - 1]
            elif px > x[index + 1]:
                x[index] = x[index + 1]
        return x, y

    def rightMouseRange(self):
        """
        :return:
        """
        xRange = self.state['limits']['xLimits']
        yRange = self.state['limits']['yLimits']
        if None in xRange or any(np.abs(xRange) > 1e300):
            self.enableAutoRange(x=True)
        else:
            self.setXRange(xRange[0], xRange[1], update=True)
        if None in yRange or any(np.abs(xRange) > 1e300):
            self.enableAutoRange(y=True)
        else:
            self.setYRange(yRange[0], yRange[1], update=True)
        return True

    def mouseDragEvent(self, ev):
        """
        :param ev:
        :return:
        """
        if self.plotDataItem is None:
            super().mouseDragEvent(ev)
            return

        if ev.button() != Qt.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            posScene = ev.buttonDownScenePos()
            pos = self.mapSceneToView(posScene)
            spot = self.plotDataItem.scatter.pointsAt(pos)
            if len(spot) == 0:
                ev.ignore()
                return
            spot = spot[0]
            self.dragPoint = spot
            self.dragOffset = spot.pos() - pos

        elif ev.isFinish():
            self.dragPoint = None
            ev.accept()
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        posScene = ev.scenePos()
        pos = self.mapSceneToView(posScene)
        posNew = pos + self.dragOffset
        index = self.dragPoint.index()
        data = self.plotDataItem.getData()
        x, y = self.checkLimits(data, index, posNew)
        self.updateData(x=x, y=y)
        ev.accept()

    def mouseClickEvent(self, ev):
        """
        :param ev:
        :return:
        """
        if self.plotDataItem is None and ev.button() == Qt.RightButton:
            self.rightMouseRange()
            ev.accept()
            return
        elif self.plotDataItem is None:
            super().mouseClickEvent(ev)
            return

        posScene = ev.scenePos()
        pos = self.mapSceneToView(posScene)
        spot = self.plotDataItem.scatter.pointsAt(pos)

        if ev.button() == Qt.RightButton:
            if len(spot) == 0:
                self.rightMouseRange()
            else:
                spot = spot[0]
                ind = spot.index()
                self.delUpdate(ind)
            ev.accept()
            return

        if ev.button() == Qt.LeftButton:
            posScene = ev.scenePos()
            pos = self.mapSceneToView(posScene)
            index = self.getCurveIndex(pos)
            if index is not None:
                self.addUpdate(index, pos)
            else:
                index = self.getNearestPointIndex(pos)
                if index is not None:
                    self.addUpdate(index, pos)
            ev.accept()
            return

        ev.ignore()
        return

    def mouseDoubleClickEvent(self, ev):
        """
        :param ev:
        :return:
        """
        if self.plotDataItem is not None:
            return
        posScene = ev.scenePos()
        posView = self.mapSceneToView(posScene)
        self.callbackMDC(ev, posView)


class PlotBase(pg.GraphicsLayoutWidget, Styles):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, show=True)
        pg.setConfigOptions(antialias=True, imageAxisOrder='row-major')

        self.pen = pg.mkPen(color=self.M_BLUE, width=1)
        self.penPink = pg.mkPen(color=self.M_PINK, width=1)
        self.brush = pg.mkBrush(color=self.M_BLUE + '80')
        self.penGrid = pg.mkPen(color=self.M_GREY)
        self.brushGrid = pg.mkBrush(color=self.M_GREY + '80')
        self.penHorizon = pg.mkPen(color=self.M_BLUE + '80', width=1)
        self.brushHorizon = pg.mkBrush(color=self.M_BLUE2 + '40')
        self.setBackground(self.M_BACK)
        self.cMapGYR = pg.ColorMap([0, 0.6, 1.0],
                                   [self.M_GREEN, self.M_YELLOW, self.M_RED])
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
        self.pen = pg.mkPen(color=self.M_BLUE, width=1)
        self.brush = pg.mkBrush(color=self.M_BLUE + '80')
        self.penGrid = pg.mkPen(color=self.M_GREY)
        self.brushGrid = pg.mkBrush(color=self.M_GREY + '80')
        self.penHorizon = pg.mkPen(color=self.M_BLUE + '80', width=1)
        self.brushHorizon = pg.mkBrush(color=self.M_BLUE2 + '40')
        self.setBackground(self.M_BACK)
        for side in ('left', 'top', 'right', 'bottom'):
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
            for side in ('left', 'top', 'right', 'bottom'):
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
        self.barItem = pg.ColorBarItem(width=15, interactive=interactive,
                                       rounding=0.025)
        self.barItem.setVisible(False)
        for side in ('left', 'top', 'right', 'bottom'):
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
            if hasattr(item, 'nameStr'):
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

        plotItem.removeItem(self.findItemByName(plotItem, 'horizon'))
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
        horItem.nameStr = 'horizon'
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
            pg.nameStr = 'iso'
            pd.setPen(pg.mkPen(color=colorVal))
            plotItem.addItem(pd)
            QApplication.processEvents()
        return True

    def addIsoItem(self, x, y, z, plotItem=None, rangeX=None,
                   rangeY=None, levels=20):
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
        zm = griddata((x, y), z, (xm, ym), method='linear',
                      fill_value=np.min(z))
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
        if kwargs.get('reverse', False):
            maxR = 90
            stepLines = 10
            gridLines = range(10, maxR, stepLines)
            circle = pg.QtWidgets.QGraphicsEllipseItem(-maxR, -maxR, maxR * 2,
                                                       maxR * 2)
            circle.setPen(self.pen)
            plotItem.addItem(circle)
        else:
            maxR = int(np.max(y))
            steps = 7
            gridLines = np.round(np.linspace(0, maxR, steps), 1)

        plotItem.addLine(x=0, pen=self.penGrid)
        plotItem.addLine(y=0, pen=self.penGrid)

        font = QFont(self.window().font().family(),
                     int(self.window().font().pointSize() * 1.1))
        for r in gridLines:
            circle = pg.QtWidgets.QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            circle.setPen(self.penGrid)
            plotItem.addItem(circle)
            if kwargs.get('reverse', False):
                text = f'{90 - r}'
            else:
                text = f'{r}'
            textItem = pg.TextItem(text=text, color=self.M_BLUE, anchor=(0.5, 0.5))
            textItem.setFont(font)
            textItem.setPos(r * np.cos(textAngle), r * np.sin(textAngle))
            plotItem.addItem(textItem)

        maxL = maxR * 1.1
        for text, x, y in zip(
                ['N', 'E', 'S', 'W', 'NE', 'SE', 'SW', 'NW'],
                [0, maxL, 0, -maxL, maxL * 0.75,
                 maxL * 0.75, -maxL * 0.75, - maxL * 0.75],
                [maxL, 0, -maxL, 0, maxL * 0.75,
                 - maxL * 0.75, - maxL * 0.75, maxL * 0.75]):
            textItem = pg.TextItem(color=self.M_BLUE, anchor=(0.5, 0.5))
            textItem.setHtml(f'<b>{text}</b>')
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


class NormalScatter(PlotBase):
    """
    """
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
        self.scatterItem = pg.ScatterPlotItem(hoverable=True,
                                              hoverSize=10, hoverPen=self.pen)
        self.p[0].addItem(self.scatterItem)
        self.defRange = kwargs.get('range', {})

        xMin = self.defRange.get('xMin', np.min(x))
        yMin = self.defRange.get('yMin', np.min(y))
        xMax = self.defRange.get('xMax', np.max(x))
        yMax = self.defRange.get('yMax', np.max(y))

        if kwargs.get('limits', True):
            if xMin is not None and xMax is not None:
                self.p[0].setLimits(xMin=xMin, xMax=xMax,
                                    minXRange=(xMax - xMin) / 4,
                                    maxXRange=(xMax - xMin))
                self.p[0].setXRange(xMin, xMax - xMin)
            if yMin is not None and yMax is not None:
                self.p[0].setLimits(yMin=yMin, yMax=yMax,
                                    minYRange=(yMax - yMin) / 4,
                                    maxYRange=(yMax - yMin))
                self.p[0].setYRange(yMin, yMax - yMin)
        self.p[0].getViewBox().rightMouseRange()

        dataVal = kwargs.get('data', y)
        self.col = kwargs.get('color', self.M_BLUE)
        if isinstance(self.col, (str, QColor)):
            self.col = [self.col] * len(x)

        if 'z' in kwargs:
            z = kwargs.get('z')
            err = np.abs(z)
            minE = np.min(err)
            maxE = np.max(err)
            divisor = max((maxE - minE), 0.1)
            self.colorInx = (err - minE) / divisor

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

        isoLevels = kwargs.get('isoLevels', 0)
        if isoLevels != 0 and 'z' in kwargs:
            self.addIsoItemHorizon(x, y, z, levels=isoLevels)
        return True


class PolarScatter(NormalScatter):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.p[0].setAspectLocked(True)
        self.addBarItem()

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
        self.p[0].showAxes(False, showValues=False)
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
                           brush=pg.mkBrush(color=colorVal),)
            arrow.setPos(posX[i], posY[i])
            self.p[0].addItem(arrow)
        return True


class ImageBar(PlotBase):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lx = None
        self.ly = None
        self.setupItems()
        self.addBarItem(interactive=True)
        self.barItem.setVisible(True)
        for side in ('left', 'top', 'right', 'bottom'):
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

    def setImage(self, imageDisp):
        """
        :param imageDisp:
        :return:
        """
        self.constructPlot()
        self.imageItem.setImage(imageDisp)
        if imageDisp is None:
            return False
        yMax, xMax = imageDisp.shape
        xMinR = max(xMax / 100, 100)
        yMinR = max(yMax / 100, 100)
        self.p[0].setLimits(xMin=0, xMax=xMax, yMin=0, yMax=yMax,
                            minXRange=xMinR, minYRange=yMinR)
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
        text = pg.TextItem(text=f'{value:2.2f}',
                           color=self.M_BLUE)
        text.setPos(posX, posY)
        self.p[0].addItem(text)
        return True


class TimeMeasure(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """
        :param values:
        :param scale:
        :param spacing:
        :return:
        """
        ticks = []
        for x in values:
            if x < 0:
                continue
            lStr = dt.fromtimestamp(x).strftime('%H:%M:%S')
            ticks.append(lStr)
        return ticks


class Measure(PlotBase):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nextRow()
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.nextRow()
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.nextRow()
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.nextRow()
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.p[1].setXLink(self.p[0])
        self.p[2].setXLink(self.p[0])
        self.p[3].setXLink(self.p[0])
        self.p[4].setXLink(self.p[0])

        self.setupItems()
        for plotItem in self.p:
            plotItem.showAxes(True, showValues=True)
            plotItem.setAxisItems({'bottom': TimeMeasure(orientation='bottom')})
            plotItem.getAxis('bottom').setPen(self.pen)
            plotItem.getAxis('bottom').setTextPen(self.pen)
            plotItem.enableAutoRange(x=True, y=True)
            plotItem.getAxis('left').setWidth(60)
            plotItem.setVisible(False)


class Hemisphere(PlotBase):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.setupItems()
        self.p[1].getViewBox().setAspectLocked(True)
        self.p[1].setVisible(False)
