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


class SensorWeatherIndi(IndiClass):
    """
    the class SensorWeatherIndi inherits all information and handling of the SensorWeather device

        >>> SensorWeatherIndi(host=None,
        >>>         name=''
        >>>         )
    """

    __all__ = ['SensorWeatherIndi',
               ]
    UPDATE_RATE = 1

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data, threadPool=app.threadPool)

        self.signals = signals
        self.data = data

    def setUpdateConfig(self, deviceName):
        """
        setUpdateRate corrects the update rate of weather devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """
        if deviceName != self.deviceName:
            return False
        if self.device is None:
            return False

        update = self.device.getNumber('WEATHER_UPDATE')
        if 'PERIOD' not in update:
            return False

        if update.get('PERIOD', 0) == self.UPDATE_RATE:
            return True

        update['PERIOD'] = self.UPDATE_RATE
        suc = self.client.sendNewNumber(deviceName=deviceName,
                                        propertyName='WEATHER_UPDATE',
                                        elements=update)
        return suc
