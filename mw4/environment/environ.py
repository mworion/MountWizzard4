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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
from datetime import datetime
# external packages
import numpy as np
# local imports
from mw4.base import indiClass


class Environ(indiClass.IndiClass):
    """
    the class Environ inherits all information and handling of the environment device

        >>> Environ(host=None,
        >>>         name=''
        >>>         )
    """

    __all__ = ['Environ',
               ]

    version = '0.100.0'
    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    UPDATE_RATE = 1

    def __init__(self,
                 app=None,
                 host=None,
                 name='',
                 ):
        super().__init__(host=host,
                         name=name
                         )
        self.app = app

    def setUpdateConfig(self, deviceName):
        """
        _setUpdateRate corrects the update rate of weather devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return: success
        """

        if deviceName != self.name:
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

    def updateNumber(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.
        for global weather data as there is no dew point value available, it calculates
        it and stores it as value as well.

        if no dew point is available in data, it will calculate this value from
        temperature and humidity.

        :param deviceName:
        :param propertyName:
        :return:
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getNumber(propertyName).items():

            # consolidate to WEATHER_PRESSURE
            if element == 'WEATHER_BAROMETER':
                key = 'WEATHER_PRESSURE'
            else:
                key = element

            self.data[key] = value

        return True
