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

# local imports
from gui.utilities.gPlotBase import PlotBase
from gui.utilities.gTimeMeasure import TimeMeasure
from gui.utilities.gCustomViewBox import CustomViewBox


class Measure(PlotBase):
    """ """

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
            plotItem.setAxisItems({"bottom": TimeMeasure(orientation="bottom")})
            plotItem.getAxis("bottom").setPen(self.pen)
            plotItem.getAxis("bottom").setTextPen(self.pen)
            plotItem.enableAutoRange(x=True, y=True)
            plotItem.getAxis("left").setWidth(60)
            plotItem.setVisible(False)
