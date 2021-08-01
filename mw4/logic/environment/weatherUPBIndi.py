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


class WeatherUPBIndi(IndiClass):
    """
    the class PegasusUPBIndi inherits all information and handling of the PegasusUPB device

        >>> power = WeatherUPBIndi(app=None)
    """

    __all__ = ['WeatherUPBIndi',
               ]

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

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

        update = self.device.getNumber('POLLING')
        if 'PERIOD' not in update:
            return False
        if update.get('PERIOD', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='POLLING',
                                        elements=update,
                                        )
        return suc
