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
from base.indiClass import IndiClass


class FilterIndi(IndiClass):
    """
    the class FilterIndi inherits all information and handling of the FilterWheel device

        >>> f = FilterIndi(app=None)
    """

    __all__ = ['FilterIndi',
               ]

    UPDATE_RATE = 1

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of weather devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """
        if deviceName != self.deviceName:
            return False

        if self.device is None:
            return False

        update = self.device.getNumber('PERIOD_MS')

        if 'PERIOD' not in update:
            return False

        if update.get('PERIOD', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='PERIOD_MS',
                                        elements=update)
        return suc

    def sendFilterNumber(self, filterNumber=1):
        """
        :param filterNumber:
        :return: success
        """
        if self.device is None:
            return False

        filterNo = self.device.getNumber('FILTER_SLOT')
        filterNo['FILTER_SLOT_VALUE'] = filterNumber
        suc = self.client.sendNewNumber(deviceName=self.deviceName,
                                        propertyName='FILTER_SLOT',
                                        elements=filterNo,
                                        )
        return suc
