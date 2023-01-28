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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.alpacaClass import AlpacaClass


class FilterAlpaca(AlpacaClass):
    """
    the class filter inherits all information and handling of the filter device.
    """

    __all__ = ['FilterAlpaca',
               ]

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)

        self.signals = signals
        self.data = data

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        names = self.getAlpacaProperty('names')
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

        position = self.getAlpacaProperty('position')
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

        self.setAlpacaProperty('position', Position=filterNumber)
        return True
