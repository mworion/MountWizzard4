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
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.indiClass import IndiClass


class SkymeterIndi(IndiClass):
    """
    """

    __all__ = ['SkymeterIndi']

    def __init__(self, app=None, signals=None, data=None):
        self.signals = signals
        super().__init__(app=app, data=data, threadPool=app.threadPool)
        self.data = data

    def setUpdateConfig(self, deviceName):
        """
        :param deviceName:
        :return: success
        """
        if deviceName != self.deviceName:
            return False
        if self.device is None:
            return False

        update = self.device.getNumber('WEATHER_UPDATE')
        if update.get('PERIOD', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='WEATHER_UPDATE',
                                        elements=update)
        return suc
