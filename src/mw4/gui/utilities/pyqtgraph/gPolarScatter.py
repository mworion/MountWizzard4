# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
import pyqtgraph as pg
from mw4.gui.utilities.pyqtgraph.gNormalScatter import NormalScatter
from numpy.typing import ArrayLike
from PySide6.QtGui import QColor
from typing import Any


class PolarScatter(NormalScatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.p[0].setAspectLocked(True)
        self.addBarItem()

    def plot(self, x: ArrayLike, y: ArrayLike, **kwargs: Any) -> bool | None:
        x = np.radians(90 - np.asarray(x))
        y = np.asarray(y)
        if kwargs.get("reverse", False):
            posX = (90 - y) * np.cos(x)
            posY = (90 - y) * np.sin(x)
        else:
            posX = y * np.cos(x)
            posY = y * np.sin(x)
        super().plot(posX, posY, limits=False, **kwargs)
        self.p[0].showAxes(False, showValues=False)
        self.setGrid(y, **kwargs)

        ang = kwargs.get("ang")
        if ang is None:
            return False
        ang = np.degrees(ang)

        for i in range(len(x)):
            arrow = pg.ArrowItem()
            if "z" in kwargs:
                colorVal = self.colorMapStyle[0].mapToQColor(self.colorInx[i])
            else:
                colorVal = QColor(*self.col[i])
            arrow.setStyle(
                angle=ang[i] - 90,
                tipAngle=0,
                headLen=0,
                tailWidth=1,
                tailLen=12,
                pen=pg.mkPen(color=colorVal),
                brush=pg.mkBrush(color=colorVal),
            )
            arrow.setPos(posX[i], posY[i])
            self.p[0].addItem(arrow)
        return True
