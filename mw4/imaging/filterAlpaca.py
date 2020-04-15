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
# GUI with PyQT5 for python
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5

# local imports
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.alpacaBase import FilterWheel


class FilterAlpaca(AlpacaClass):
    """
    the class Telescope inherits all information and handling of the Telescope device.
    """

    __all__ = ['FilterAlpaca',
               ]

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = FilterWheel()
        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """

        super().getInitialConfig()

        return True
