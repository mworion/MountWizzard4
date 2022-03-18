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
from PyQt5.QtGui import QColor, QFont, QTransform

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
        self.xRange = None
        self.yRange = None
        self.dragOffset = None
        self.dragPoint = None
        self.enableDrag = kwargs.get('enableDrag', False)
        self.enableEdit = kwargs.get('enableEdit', False)
        self.enableRange = kwargs.get('enableRange', False)
        self.enableLimitX = kwargs.get('enableLimitX', False)

    def setEnableDrag(self, status):
        """
        :param status:
        :return:
        """
        self.enableDrag = status
        return True

    def setEnableEdit(self, status):
        """
        :param status:
        :return:
        """
        self.enableEdit = status
        return True

    def setEnableRange(self, status):
        """
        :param status:
        :return:
        """
        self.enableRange = status
        return True

    def setEnableLimitX(self, status):
        """
        :param status:
        :return:
        """
        self.enableLimitX = status
        return True

    def setPlotDataItem(self, plotDataItem):
        """
        :param plotDataItem:
        :return:
        """
        self.plotDataItem = plotDataItem
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

    def getCurveIndex(self, pos, epsilon=1):
        """
        :param pos:
        :param epsilon:
        :return:
        """
        data = self.plotDataItem.curve.getData()
        curve = [(x, y) for x, y in zip(data[0], data[1])]
        for index in range(0, len(curve) - 1):
            d = self.isBetween(curve[index], curve[index + 1], (pos.x(), pos.y()))
            if d < epsilon:
                break
        else:
            return 0
        return index + 1

    def getNearestPointIndex(self, pos):
        """
        :param pos:
        :return: index or none
        """
        data = self.plotDataItem.curve.getData()
        x = data[0]
        y = data[1]
        d = np.sqrt((x - pos.x()) ** 2 / 4 + (y - pos.y()) ** 2)
        index = int(d.argsort()[:1][0])
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
        x = np.concatenate((x[0:index], [pos.x()], x[index:]))
        y = np.concatenate((y[0:index], [pos.y()], y[index:]))
        self.plotDataItem.setData(x=x, y=y)
        return True

    def delUpdate(self, index):
        """
        :param index:
        :return:
        """
        data = self.plotDataItem.getData()
        x = data[0]
        y = data[1]
        x = np.delete(x, index)
        y = np.delete(y, index)
        self.plotDataItem.setData(x=x, y=y)
        return True

    def checkLimits(self, data, index, pos):
        """
        :param data:
        :param index:
        :param pos:
        :return:
        """
        if self.xRange:
            if pos.x() > self.xRange[1]:
                px = self.xRange[1]
            elif pos.x() < self.xRange[0]:
                px = self.xRange[0]
            else:
                px = pos.x()
        if self.yRange:
            if pos.y() > self.yRange[1]:
                py = self.yRange[1]
            elif pos.y() < self.yRange[0]:
                py = self.yRange[0]
            else:
                py = pos.y()

        x = data[0]
        y = data[1]
        x[index] = px
        y[index] = py
        if not self.enableLimitX:
            return x, y

        if index == 0:
            x[index] = np.minimum(px, x[index + 1])
        elif index == len(x):
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
        if self.xRange:
            self.setXRange(self.xRange[0], self.xRange[1])
        if self.yRange:
            self.setYRange(self.yRange[0], self.yRange[1])
        if self.xRange is None and self.yRange is None:
            self.enableAutoRange(x=True, y=True)
        return True

    def mouseDragEvent(self, ev):
        """
        :param ev:
        :return:
        """
        if not self.enableDrag:
            ev.ignore()
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
        self.plotDataItem.setData(x=x, y=y)
        ev.accept()

    def mouseClickEvent(self, ev):
        """
        :param ev:
        :return:
        """
        posScene = ev.scenePos()
        pos = self.mapSceneToView(posScene)
        spot = self.plotDataItem.scatter.pointsAt(pos)

        if ev.button() == Qt.RightButton:
            if len(spot) == 0:
                if not self.enableRange:
                    ev.ignore()
                    return
                self.rightMouseRange()
            else:
                if not self.enableEdit:
                    ev.ignore()
                    return
                spot = spot[0]
                ind = spot.index()
                self.delUpdate(ind)
            ev.accept()
            return

        if ev.button() == Qt.LeftButton:
            if not self.enableEdit:
                ev.ignore()
                return
            posScene = ev.scenePos()
            pos = self.mapSceneToView(posScene)
            inCurve = self.plotDataItem.curve.contains(pos)
            if inCurve:
                index = self.getCurveIndex(pos)
                self.addUpdate(index, pos)
            else:
                index = self.getNearestPointIndex(pos)
                self.addUpdate(index, pos)
            ev.accept()
            return

        ev.ignore()
        return


class PlotBase(pg.GraphicsLayoutWidget, Styles):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, show=True)

        pg.setConfigOptions(antialias=True, imageAxisOrder='row-major')

        self.pen = pg.mkPen(color=self.M_BLUE, width=1)
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
            plotItem.setClipToView(True)
            plotItem.setOwnedByLayout(True)
            plotItem.showAxes(False, showValues=False)
            for side in ('left', 'top', 'right', 'bottom'):
                plotItem.getAxis(side).setPen(self.pen)
                plotItem.getAxis(side).setTextPen(self.pen)
                plotItem.getAxis(side).setGrid(32)

    def addBarItem(self, interactive=False):
        """
        :return:
        """
        self.barItem = pg.ColorBarItem(width=15, interactive=interactive)
        self.barItem.setVisible(False)
        for side in ('left', 'top', 'right', 'bottom'):
            self.barItem.getAxis(side).setPen(self.pen)
            self.barItem.getAxis(side).setTextPen(self.pen)
        self.p[0].layout.addItem(self.barItem, 2, 5)
        self.p[0].layout.setColumnFixedWidth(4, 5)
        return True

    def drawHorizon(self, horizonP):
        """
        :param horizonP:
        :return:
        """
        if len(horizonP) == 0:
            return False
        alt, az = zip(*horizonP)
        alt = np.array(alt)
        az = np.array(az)
        altF = np.concatenate([[0], [alt[0]], alt, [alt[-1]], [0]])
        azF = np.concatenate([[0], [0], az, [360], [360]])
        path = pg.arrayToQPath(azF, altF)
        poly = pg.QtGui.QGraphicsPathItem(path)
        poly.setPen(self.penHorizon)
        poly.setBrush(self.brushHorizon)
        poly.setZValue(-5)
        self.p[0].addItem(poly)
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
        xMin = self.defRange['xMin'] = self.defRange.get('xMin', np.min(x) * 1.2)
        yMin = self.defRange['yMin'] = self.defRange.get('yMin', np.min(y) * 1.2)
        xMax = self.defRange['xMax'] = self.defRange.get('xMax', np.max(x) * 1.2)
        yMax = self.defRange['yMax'] = self.defRange.get('yMax', np.max(y) * 1.2)

        if kwargs.get('limits', True):
            self.p[0].setLimits(xMin=xMin, xMax=xMax,
                                yMin=yMin, yMax=yMax,
                                minXRange=(xMax - xMin) / 4,
                                maxXRange=(xMax - xMin),
                                minYRange=(yMax - yMin) / 4,
                                maxYRange=(yMax - yMin))
        self.p[0].setRange(QRectF(xMin, yMin, xMax - xMin, yMax - yMin))
        self.p[0].getViewBox().xRange = (xMin, xMax)
        self.p[0].getViewBox().yRange = (yMin, yMax)
        self.p[0].autoRange()

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
        self.p[0].setAspectLocked(True)
        self.addBarItem()

    def setGrid(self, y, **kwargs):
        """
        :param y:
        :param kwargs:
        :return:
        """
        textAngle = np.radians(30)
        if kwargs.get('reverse', False):
            maxR = 90
            stepLines = 10
            gridLines = range(10, maxR, stepLines)
            circle = pg.QtWidgets.QGraphicsEllipseItem(-maxR, -maxR, maxR * 2,
                                                       maxR * 2)
            circle.setPen(self.pen)
            self.p[0].addItem(circle)
        else:
            maxR = int(np.max(y))
            steps = 7
            gridLines = np.round(np.linspace(0, maxR, steps), 1)

        self.p[0].addLine(x=0, pen=self.penGrid)
        self.p[0].addLine(y=0, pen=self.penGrid)

        font = QFont(self.window().font().family(),
                     int(self.window().font().pointSize() * 1.1))
        for r in gridLines:
            circle = pg.QtWidgets.QGraphicsEllipseItem(-r, -r, r * 2, r * 2)
            circle.setPen(self.penGrid)
            self.p[0].addItem(circle)
            if kwargs.get('reverse', False):
                text = f'{90 - r}'
            else:
                text = f'{r}'
            textItem = pg.TextItem(text=text, color=self.M_GREY, anchor=(0.5, 0.5))
            textItem.setFont(font)
            textItem.setPos(r * np.cos(textAngle), r * np.sin(textAngle))
            self.p[0].addItem(textItem)

        for text, x, y in zip(
                ['N', 'E', 'S', 'W', 'NE', 'SE', 'SW', 'NW'],
                [0, maxR, 0, -maxR, maxR * 0.7, maxR * 0.7, -maxR * 0.7, - maxR * 0.7],
                [maxR, 0, -maxR, 0, maxR * 0.7, - maxR * 0.7, - maxR * 0.7, maxR * 0.7]):
            textItem = pg.TextItem(color=self.M_BLUE, anchor=(0.5, 0.5))
            textItem.setHtml(f'<b>{text}</b>')
            textItem.setFont(font)
            textItem.setPos(x, y)
            self.p[0].addItem(textItem)
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

    def plotLoc(self, lat):
        """
        :param lat:
        :return:
        """
        circle = pg.QtWidgets.QGraphicsEllipseItem(-2.5, -2.5, 5, 5)
        circle.setPen(self.pen)
        circle.setBrush(self.brush)
        circle.setPos(0, lat)
        self.p[0].addItem(circle)
        circle = pg.QtWidgets.QGraphicsEllipseItem(-5, -5, 10, 10)
        circle.setPen(self.pen)
        circle.setPos(0, lat)
        self.p[0].addItem(circle)
        circle = pg.QtWidgets.QGraphicsEllipseItem(-7.5, -7.5, 15, 15)
        circle.setPen(self.pen)
        circle.setPos(0, lat)
        self.p[0].addItem(circle)
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
        yMax, xMax = imageDisp.shape
        xMinR = max(xMax / 100, 100)
        yMinR = max(yMax / 100, 100)
        self.p[0].setLimits(xMin=0, xMax=xMax, yMin=0, yMax=yMax,
                            minXRange=xMinR, minYRange=yMinR)
        self.p[0].autoRange()

        minB = np.min(imageDisp)
        maxB = 2 * np.mean(imageDisp)
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
        ellipse = pg.QtWidgets.QGraphicsEllipseItem(-a, -b, 2 * a, 2 * b)
        ellipse.setPos(x, y)
        tr = QTransform()
        tr.rotate(np.degrees(theta))
        ellipse.setTransform(tr)
        ellipse.setPen(self.pen)
        self.p[0].addItem(ellipse)
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


