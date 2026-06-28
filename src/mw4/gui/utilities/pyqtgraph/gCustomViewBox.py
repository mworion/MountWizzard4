############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QEvent, Qt


class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwargs):
        self._previousGeometry = None
        super().__init__(*args, **kwargs)
        self.plotDataItem = None
        self.dragOffset = None
        self.dragPoint = None
        self.enableLimitX = None
        self.epsilonCurve = 2
        self.epsilonFree = 360
        self.setOpts(*args, **kwargs)

    def setPlotDataItem(self, plotDataItem: pg.PlotDataItem) -> None:
        self.plotDataItem = plotDataItem

    def setOpts(self, *args, **kwargs):
        self.enableLimitX = kwargs.get("enableLimitX", False)

    def updateData(self, x: np.ndarray, y: np.ndarray) -> None:
        self.plotDataItem.setData(x=x, y=y)

    @staticmethod
    def callbackMDC(event: QEvent, posView: pg.Point) -> None:
        pass

    @staticmethod
    def distance(a: tuple[int, int], b: tuple[int, int]) -> float:
        return np.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def isBetween(self, a: tuple[int, int], b: tuple[int, int], c: tuple[int, int]) -> float:
        d = self.distance(a, c) + self.distance(c, b) - self.distance(a, b)
        return np.abs(d)

    def getCurveIndex(self, pos: pg.Point) -> int | None:
        data = self.plotDataItem.curve.getData()
        curve = [(x, y) for x, y in zip(data[0], data[1])]
        for index in range(0, len(curve) - 1):
            d = self.isBetween(curve[index], curve[index + 1], (int(pos.x()), int(pos.y())))
            if d < self.epsilonCurve:
                break
        else:
            return None
        return index + 1

    def getNearestPointIndex(self, pos: pg.Point) -> int | None:
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
        data = self.plotDataItem.getData()
        x = data[0]
        y = data[1]
        if x is None and y is None:
            return False
        x = np.delete(x, index)
        y = np.delete(y, index)
        self.updateData(x=x, y=y)
        return True

    @staticmethod
    def clampToRange(value: float, limits: list) -> float:
        if None not in limits:
            return float(np.clip(value, limits[0], limits[1]))
        return value

    @staticmethod
    def clampXToNeighbors(x: np.ndarray, index: int, px: float) -> float:
        if index == 0:
            return float(np.minimum(px, x[index + 1]))
        if index == len(x) - 1:
            return float(np.maximum(x[index - 1], px))
        return float(np.clip(px, x[index - 1], x[index + 1]))

    def checkLimits(
        self, data: tuple[np.ndarray, np.ndarray], index: int, pos: pg.Point
    ) -> tuple[np.ndarray, np.ndarray]:
        xRange = self.state["limits"]["xLimits"]
        yRange = self.state["limits"]["yLimits"]
        px = self.clampToRange(pos.x(), xRange)
        py = self.clampToRange(pos.y(), yRange)
        x = data[0]
        y = data[1]
        x[index] = px
        y[index] = py
        if not self.enableLimitX:
            return x, y
        x[index] = self.clampXToNeighbors(x, index, px)
        return x, y

    def posInViewRange(self, pos: pg.Point) -> bool:
        mousePoint = self.mapSceneToView(pos)
        x, y = mousePoint.x(), mousePoint.y()
        vr = self.viewRange()
        return bool(vr[0][0] < x < vr[0][1] and vr[1][0] < y < vr[1][1])

    def rightMouseRange(self) -> None:
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

    def mouseDragEvent(self, event: QEvent, axis=None) -> None:
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

    def mouseClickEvent(self, event) -> None:
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

    def mouseDoubleClickEvent(self, event, QGraphicsSceneMouseEvent=None) -> None:
        if self.plotDataItem is not None:
            return
        posScene = event.scenePos()
        posView = self.mapSceneToView(posScene)
        self.callbackMDC(event, posView)
