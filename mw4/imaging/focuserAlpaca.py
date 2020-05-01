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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from mw4.base.alpacaClass import AlpacaClass
from mw4.base.alpacaBase import Focuser


class FocuserAlpaca(AlpacaClass):
    """
    the class Telescope inherits all information and handling of the Telescope device.
    """

    __all__ = ['FocuserAlpaca',
               ]

    # specific timing for device
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = Focuser()
        self.signals = signals
        self.data = data

        self.client.signals.deviceConnected.connect(self.startCommunication)

    def getInitialConfig(self):
        """

        :return: true for test purpose
        """

        super().getInitialConfig()

        return True

    def workerPollData(self):
        """

        :return: true for test purpose
        """

        self.data['ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION'] = self.client.position()

        return True
