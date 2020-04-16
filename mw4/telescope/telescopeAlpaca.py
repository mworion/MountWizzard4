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

# local imports
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.alpacaBase import Telescope


class TelescopeAlpaca(AlpacaClass):
    """
    the class Telescope inherits all information and handling of the Telescope device.
    """

    __all__ = ['TelescopeAlpaca',
               ]

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = Telescope()
        self.signals = signals
        self.data = data

        self.client.signals.deviceConnected.connect(self.startCommunication)

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """

        super().getInitialConfig()

        self.dataEntry(self.client.aperturediameter() * 1000,
                       'TELESCOPE_INFO.TELESCOPE_APERTURE')
        self.dataEntry(self.client.focallength() * 1000,
                       'TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH')

        return True
