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


class PegasusUPB(indiClass.IndiClass):
    """
    the class PegasusUPB inherits all information and handling of the PegasusUPB device

        >>> fw = PegasusUPB(
        >>>                  host=host
        >>>                  name=''
        >>>                 )
    """

    __all__ = ['Skymeter',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 1000 milli seconds for setting indi server
    UPDATE_RATE = 1000

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

        # calling some values, which weren't sent at the beginning

        dew = self.device.getNumber('DEW_PWM')
        self.client.sendNewNumber(deviceName=deviceName,
                                  propertyName='DEW_PWM',
                                  elements=dew,
                                  )
        powerControl = self.device.getSwitch('POWER_CONTROL')
        self.client.sendNewSwitch(deviceName=deviceName,
                                  propertyName='POWER_CONTROL',
                                  elements=powerControl,
                                  )
        powerBoot = self.device.getSwitch('POWER_ON_BOOT')
        self.client.sendNewSwitch(deviceName=deviceName,
                                  propertyName='POWER_ON_BOOT',
                                  elements=powerBoot,
                                  )
        sensor = self.device.getNumber('POWER_SENSORS')
        self.client.sendNewNumber(deviceName=deviceName,
                                  propertyName='POWER_SENSORS',
                                  elements=sensor,
                                  )
        consumption = self.device.getNumber('POWER_CONSUMPTION')
        self.client.sendNewNumber(deviceName=deviceName,
                                  propertyName='POWER_CONSUMPTION',
                                  elements=consumption,
                                  )
        weather = self.device.getNumber('WEATHER_PARAMETERS')
        self.client.sendNewNumber(deviceName=deviceName,
                                  propertyName='WEATHER_PARAMETERS',
                                  elements=weather,
                                  )

        # setting polling updates in driver

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

    def updateData(self, deviceName, propertyName):
        """
        updateData is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.
        for global weather data as there is no dew point value available, it calculates
        it and stores it as value as well.

        in addition it does a first setup and config for the device. basically the update
        rates are set to 10 seconds if they are not on this level.

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
            self.data[element] = value
            # print(propertyName, element, value)

        return True
