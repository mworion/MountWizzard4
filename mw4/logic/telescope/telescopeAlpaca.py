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
#
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.alpacaClass import AlpacaClass
from base.alpacaBase import Telescope


class TelescopeAlpaca(AlpacaClass):
    """
    the class Telescope inherits all information and handling of the
    Telescope device.
    """

    __all__ = ['TelescopeAlpaca',
               ]

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = Telescope()
        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().getInitialConfig()

        self.storePropertyToData(self.client.aperturediameter(), 'TELESCOPE_INFO.TELESCOPE_APERTURE')
        self.storePropertyToData(self.client.focallength(), 'TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH')
        return True
