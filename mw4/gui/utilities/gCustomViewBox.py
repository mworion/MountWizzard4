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
from PySide6.QtCore import Qt, QEvent

# local imports

__all__ = ["CustomViewBox"]


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

    def setPlotDataItem(self, plotDataItem: pg.PlotDataItem) -> None:
        """ """
        self.plotDataItem = plotDataItem

    def setOpts(self, *args, **kwargs):
        """ """
        self.enableLimitX = kwargs.get("enableLimitX", False)

    def updateData(self, x: int, y: int) -> None:
        """ """
        self.plotDataItem.setData(x=x, y=y)

    @staticmethod
    def callbackMDC(event: QEvent, posView: pg.Point) -> None:
        pass

    @staticmethod
    def distance(a: (int, int), b: (int, int)) -> float:
        """ """
        return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def isBetween(self, a: int, b: int, c: int) -> float:
        """ """
        d = self.distance(a, c) + self.distance(c, b) - self.distance(a, b)
        return np.abs(d)

    def getCurveIndex(self, pos: pg.Point) -> int:
        """ """
        data = self.plotDataItem.curve.getData()
        curve = [(x, y) for x, y in zip(data[0], data[1])]
        for index in range(0, len(curve) - 1):
            d = self.isBetween(curve[index], curve[index + 1], (pos.x(), pos.y()))
            if d < self.epsilonCurve:
                break
        else:
            return None
        return index + 1

    def getNearestPointIndex(self, pos: pg.Point) -> int:
        """ """
        data = self.plotDataItem.getData()
        if data[0] is None or data[1] is None:
            return 0
        x = data[0]
        y = data[1]
        d = np.sqrt((x - pos.x()) ** 2 / 4 + (y - pos.y()) ** 2)
        index = int(d.argsort()[:1][0])
        if d[index] >= self.epsilonFree:
            return None
        return index + 1

    def addUpdate(self, index: int, pos: pg.Point) -> None:
        """ """
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

    def delUpdate(self, index: int) -> bool:
        """ """
        data = self.plotDataItem.getData()
        x = data[0]
        y = data[1]
        if x is None and y is None:
            return False
        x = np.delete(x, index)
        y = np.delete(y, index)
        self.updateData(x=x, y=y)
        return True

    def checkLimits(
        self, data: (float, float), index: int, pos: pg.Point
    ) -> (np.array, np.array):
        """ """
        xRange = self.state["limits"]["xLimits"]
        yRange = self.state["limits"]["yLimits"]
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

    def posInViewRange(self, pos: pg.Point) -> bool:
        mousePoint = self.mapSceneToView(pos)
        x, y = mousePoint.x(), mousePoint.y()
        vr = self.viewRange()
        if vr[0][0] < x < vr[0][1] and vr[1][0] < y < vr[1][1]:
            return True
        return False

    def rightMouseRange(self) -> None:
        """ """
        xRange = self.state["limits"]["xLimits"]
        yRange = self.state["limits"]["yLimits"]
        if None in xRange or any(np.abs(xRange) > 1e300):
            self.enableAutoRange(x=True)
        else:
            self.setXRange(xRange[0], xRange[1], update=True)
        if None in yRange or any(np.abs(xRange) > 1e300):
            self.enableAutoRange(y=True)
        else:
            self.setYRange(yRange[0], yRange[1], update=True)

    def mouseDragEvent(self, event: QEvent(QEvent.Type.DragEnter), axis=None) -> None:
        """ """
        if self.plotDataItem is None:
            super().mouseDragEvent(event)
            return

        if event.button() != Qt.MouseButton.LeftButton:
            event.ignore()
            return

        if event.isStart():
            posScene = event.buttonDownScenePos()
            pos = self.mapSceneToView(posScene)
            spot = self.plotDataItem.scatter.pointsAt(pos)
            if len(spot) == 0:
                event.ignore()
                return
            spot = spot[0]
            self.dragPoint = spot
            self.dragOffset = spot.pos() - pos

        elif event.isFinish():
            self.dragPoint = None
            event.accept()
            return
        else:
            if self.dragPoint is None:
                event.ignore()
                return

        posScene = event.scenePos()
        pos = self.mapSceneToView(posScene)
        posNew = pos + self.dragOffset
        index = self.dragPoint.index()
        data = self.plotDataItem.getData()
        x, y = self.checkLimits(data, index, posNew)
        self.updateData(x=x, y=y)
        event.accept()

    def mouseClickEvent(self, event):
        """ """
        if self.plotDataItem is None and event.button() == Qt.MouseButton.RightButton:
            self.rightMouseRange()
            event.accept()
            return
        elif self.plotDataItem is None:
            super().mouseClickEvent(event)
            return

        posScene = event.scenePos()
        pos = self.mapSceneToView(posScene)
        spot = self.plotDataItem.scatter.pointsAt(pos)

        if event.button() == Qt.MouseButton.RightButton:
            if len(spot) == 0:
                self.rightMouseRange()
            else:
                spot = spot[0]
                ind = spot.index()
                self.delUpdate(ind)
            event.accept()
            return

        if event.button() == Qt.MouseButton.LeftButton:
            posScene = event.scenePos()
            pos = self.mapSceneToView(posScene)
            index = self.getCurveIndex(pos)
            if index is not None:
                self.addUpdate(index, pos)
            else:
                index = self.getNearestPointIndex(pos)
                if index is not None:
                    self.addUpdate(index, pos)
            event.accept()
            return

        event.ignore()
        return

    def mouseDoubleClickEvent(self, event, QGraphicsSceneMouseEvent=None):
        """ """
        if self.plotDataItem is not None:
            return
        posScene = event.scenePos()
        posView = self.mapSceneToView(posScene)
        self.callbackMDC(event, posView)
