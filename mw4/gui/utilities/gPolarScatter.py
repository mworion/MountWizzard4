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

# local imports
from gui.utilities.gNormalScatter import NormalScatter


class PolarScatter(NormalScatter):
    """ """

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
                colorVal = self.cMapGYR.mapToQColor(self.colorInx[i])
            else:
                colorVal = self.col[i]
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
