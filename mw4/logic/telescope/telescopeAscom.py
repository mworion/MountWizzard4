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
from base.ascomClass import AscomClass


class TelescopeAscom(AscomClass):
    """
    the class Telescope inherits all information and handling of the Telescope device.
    """

    __all__ = ['TelescopeAscom',
               ]

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """

        super().getInitialConfig()

        if not self.deviceConnected:
            return False

        value = self.client.ApertureDiameter
        if isinstance(value, float):
            value = value * 1000

        self.dataEntry(value, 'TELESCOPE_INFO.TELESCOPE_APERTURE')

        value = self.client.FocalLength
        if isinstance(value, float):
            value = value * 1000

        self.dataEntry(value, 'TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH')

        return True
