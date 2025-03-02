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
from datetime import datetime as dt

# external packages
import pyqtgraph as pg

# local imports


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
            lStr = dt.fromtimestamp(x).strftime("%H:%M:%S")
            ticks.append(lStr)
        return ticks
