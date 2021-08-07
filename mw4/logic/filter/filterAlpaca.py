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
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.alpacaClass import AlpacaClass
from base.alpacaBase import FilterWheel


class FilterAlpaca(AlpacaClass):
    """
    the class filter inherits all information and handling of the filter device.
    """

    __all__ = ['FilterAlpaca',
               ]

    CYCLE_POLL_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.client = FilterWheel()
        self.signals = signals
        self.data = data

    def getInitialConfig(self):
        """
        :return: success
        """
        super().getInitialConfig()
        names = self.client.names()
        if names is None:
            return False

        for i, name in enumerate(names):
            if name is None:
                continue
            self.data[f'FILTER_NAME.FILTER_SLOT_NAME_{i:1.0f}'] = name

        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        position = self.client.position()
        if position == -1 or position is None:
            return False

        self.data['FILTER_SLOT.FILTER_SLOT_VALUE'] = position
        return True

    def sendFilterNumber(self, filterNumber=0):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.client.position(Position=filterNumber)
        return True
