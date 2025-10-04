############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from mw4.gui.utilities.gCustomViewBox import CustomViewBox
from mw4.gui.utilities.gPlotBase import PlotBase


class Hemisphere(PlotBase):
    """ """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.p.append(self.addPlot(viewBox=CustomViewBox()))
        self.setupItems()
        self.p[1].getViewBox().setAspectLocked(True)
        self.p[1].setVisible(False)
