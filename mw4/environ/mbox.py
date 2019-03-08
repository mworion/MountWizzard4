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
from indibase import qtIndiBase
# local imports


class MBox(object):
    """
    the class Environ inherits all information and handling of environment devices

        >>> fw = MBox(
        >>>                  host=host
        >>>                  name='MBox'
        >>>                 )
    """

    __all__ = ['MBox',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 1 seconds for setting indi server
    UPDATE_RATE = 1

    def __init__(self,
                 host=None,
                 name='',
                 ):
        super().__init__()

        self.indiServerUp = False
        self.client = qtIndiBase.Client(host=host)
        self.name = name
        self.data = {}
        self.device = None

        # link signals
        self.client.signals.newDevice.connect(self.newDevice)
        self.client.signals.removeDevice.connect(self.removeDevice)
        self.client.signals.newProperty.connect(self.connectDevice)
        self.client.signals.newNumber.connect(self.updateData)
        self.client.signals.deviceConnected.connect(self._setUpdateRate)
        self.client.signals.serverConnected.connect(self.serverConnected)
        self.client.signals.serverDisconnected.connect(self.serverDisconnected)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def serverConnected(self):
        self.indiServerUp = True

    def serverDisconnected(self):
        self.indiServerUp = False

    def newDevice(self, deviceName):
        """
        newDevice is called whenever a new device entry is received in indi client. it
        adds the device if the name fits to the given name in configuration.

        :param deviceName:
        :return: true for test purpose
        """

        if deviceName == self.name:
            self.device = self.client.getDevice(deviceName)
        return True

    def removeDevice(self, deviceName):
        """
        removeDevice is called whenever a device is removed from indi client. it sets
        the device entry to None

        :param deviceName:
        :return: true for test purpose
        """

        if deviceName == self.name:
            self.device = None
            self.data = {}
        return True

    def startCommunication(self):
        """
        startCommunication adds a device on the watch list of the server.

        :return: success of reconnecting to server
        """

        suc = self.client.connectServer()
        if not suc:
            return False

        suc = self.client.watchDevice(self.name)
        return suc

    def reconnectIndiServer(self):
        """
        as it says.

        :return: success of reconnecting to server
        """

        if self.client.isServerConnected():
            self.client.disconnectServer()
        suc = self.startCommunication()
        return suc

    def connectDevice(self, deviceName, propertyName):
        """
        connectDevice is called when a new property is received and checks it against
        property CONNECTION. if this is there, we could check the connection state of
        a given device

        :param deviceName:
        :param propertyName:
        :return: success if device could connect
        """
        if propertyName != 'CONNECTION':
            return False

        if deviceName == self.name:
            suc = self.client.connectDevice(deviceName=deviceName)
        return suc

    def _setUpdateRate(self, deviceName):
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
        if update.get('PERIOD', 0) != self.UPDATE_RATE:
            update['PERIOD'] = self.UPDATE_RATE
            suc = self.client.sendNewNumber(deviceName=deviceName,
                                            propertyName='WEATHER_UPDATE',
                                            elements=update)
        return suc

    @staticmethod
    def _getDewPoint(t_air_c, rel_humidity):
        """
        Compute the dew point in degrees Celsius

        :param t_air_c: current ambient temperature in degrees Celsius
        :type t_air_c: float
        :param rel_humidity: relative humidity in %
        :type rel_humidity: float
        :return: the dew point in degrees Celsius
        :rtype: float
        """

        A = 17.27
        B = 237.7
        alpha = ((A * t_air_c) / (B + t_air_c)) + np.log(rel_humidity / 100.0)
        return (B * alpha) / (A - alpha)

    def updateData(self, deviceName, propertyName):
        """
        updateData is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.
        for global weather data as there is no dew point value available, it calculates
        it and stores it as value as well.

        in addition it does a first setup and config for the device. basically the update
        rates are set to 10 seconds if they are not on this level.

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
            elArray = element + '_ARRAY'
            elTime = element + '_TIME'
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

        # calculate is manually

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
        isPressure = 'WEATHER_BAROMETER_ARRAY' in self.data
        if isTemperature and isPressure:
            temp = np.mean(self.data['WEATHER_TEMPERATURE_ARRAY'][:10])
            press = np.mean(self.data['WEATHER_BAROMETER_ARRAY'][:10])
            return temp, press
        else:
            return None, None
