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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
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

        >>> fw = Environ(
        >>>                  host=host
        >>>                  name=''
        >>>                 )
    """

    __all__ = ['Environ',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    UPDATE_RATE = 1

    def __init__(self,
                 host=None,
                 name='',
                 ):
        super().__init__(host=host,
                         name=name
                         )

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

    @staticmethod
    def _getDewPoint(tempAir, relativeHumidity):
        """
        Compute the dew point in degrees Celsius

        :param tempAir: current ambient temperature in degrees Celsius
        :param relativeHumidity: relative humidity in %
        :return: the dew point in degrees Celsius
        """

        if tempAir < -40 or tempAir > 80:
            return 0
        if relativeHumidity < 0 or relativeHumidity > 100:
            return 0

        A = 17.27
        B = 237.7
        alpha = ((A * tempAir) / (B + tempAir)) + np.log(relativeHumidity / 100.0)
        dewPoint = (B * alpha) / (A - alpha)
        return dewPoint

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
            elArray = key + '_ARRAY'
            elTime = key + '_TIME'
            if elArray not in self.data:
                self.data[elArray] = np.full(100, value)
                self.data[elTime] = np.full(100, datetime.now())
            else:
                self.data[elArray] = np.roll(self.data[elArray], 1)
                self.data[elArray][0] = value
                self.data[elTime] = np.roll(self.data[elTime], 1)
                self.data[elTime][0] = datetime.now()

        if 'WEATHER_DEWPOINT' in self.data:
            return True
        if 'WEATHER_TEMPERATURE' not in self.data:
            return False
        if 'WEATHER_HUMIDITY' not in self.data:
            return False

        temp = self.data['WEATHER_TEMPERATURE']
        humidity = self.data['WEATHER_HUMIDITY']
        dewPoint = self._getDewPoint(temp, humidity)
        self.data['WEATHER_DEWPOINT'] = dewPoint

        return True

    def getFilteredRefracParams(self):
        """
        getFilteredRefracParams filters local temperature and pressure with and moving
        average filter over 5 minutes and returns the filtered values.

        :return:  temperature and pressure
        """

        isTemperature = 'WEATHER_TEMPERATURE_ARRAY' in self.data
        isPressure = 'WEATHER_PRESSURE_ARRAY' in self.data
        if isTemperature and isPressure:
            temp = np.mean(self.data['WEATHER_TEMPERATURE_ARRAY'][:10])
            press = np.mean(self.data['WEATHER_PRESSURE_ARRAY'][:10])
            return temp, press
        else:
            return None, None
