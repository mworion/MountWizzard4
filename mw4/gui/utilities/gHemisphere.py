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
from gui.utilities.gCustomViewBox import CustomViewBox


class Hemisphere(PlotBase):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.setupItems()
        self.p[1].getViewBox().setAspectLocked(True)
        self.p[1].setVisible(False)
