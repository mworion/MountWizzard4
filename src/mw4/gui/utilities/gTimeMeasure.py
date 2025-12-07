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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

from datetime import datetime as dt
import pyqtgraph as pg


class TimeMeasure(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values: [], scale: float, spacing: []) -> []:
        """ """
        ticks = []
        for x in values:
            if x < 0:
                continue
            lStr = dt.fromtimestamp(x).strftime("%H:%M:%S")
            ticks.append(lStr)
        return ticks
