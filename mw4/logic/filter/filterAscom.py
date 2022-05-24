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
# written in python3, (c) 2019-2022 by mworion
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

    CYCLE_POLL_DATA = 1000

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)
        # as we have in the base class only the base client there, we will get more
        # specialized with Dome (which is derived from the base class)
        self.signals = signals

    def workerGetInitialConfig(self):
        """
        :return: success
        """
        super().workerGetInitialConfig()
        names = self.getAscomProperty('Names')
        if names is None:
            return False

        for i, name in enumerate(names):
            self.storePropertyToData(name, f'FILTER_NAME.FILTER_SLOT_NAME_{i:1.0f}')
        return True

    def workerPollData(self):
        """
        :return: true for test purpose
        """
        position = self.getAscomProperty('Position')
        if position == -1 or position is None:
            return False

        self.storePropertyToData(position, 'FILTER_SLOT.FILTER_SLOT_VALUE')
        return True

    def sendFilterNumber(self, filterNumber=0):
        """
        :return: true for test purpose
        """
        if not self.deviceConnected:
            return False

        self.setAscomProperty('Position', filterNumber)
        return True
