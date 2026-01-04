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
# Licence APL2.0
#
###########################################################
import pyqtgraph as pg
from datetime import datetime as dt


class TimeMeasure(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values: list, scale: float, spacing: list) -> list:
        """ """
        ticks = []
        for x in values:
            if x < 0:
                continue
            lStr = dt.fromtimestamp(x).strftime("%H:%M:%S")
            ticks.append(lStr)
        return ticks
