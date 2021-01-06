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
from base.ascomClass import AscomClass


class FilterAscom(AscomClass):
    """
    the class filter inherits all information and handling of the filter device.
    """

    __all__ = ['FilterAscom',
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
        :return: success
        """
        super().getInitialConfig()
        if not self.deviceConnected:
            return False

        names = self.client.Names
        if names is None:
            return False

        for i, name in enumerate(names):
            if name is None:
                continue
            self.dataEntry(name, f'FILTER_NAME.FILTER_SLOT_NAME_{i:1.0f}')
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        position = self.client.Position
        if position == -1 or position is None:
            return False

        self.dataEntry(position, 'FILTER_SLOT.FILTER_SLOT_VALUE')
        return True

    def sendFilterNumber(self, filterNumber=0):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.client.Position = filterNumber
        return True
