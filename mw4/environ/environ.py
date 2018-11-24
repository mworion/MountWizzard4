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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
import PyQt5
import numpy as np
from indibase import indiBase
# local imports


class Environment(PyQt5.QtWidgets.QWidget):
    """
    the class Environ inherits all information and handling of environment devices

        >>> fw = Environment(
        >>>                  host=host
        >>>                  localWeatherName='MBox'
        >>>                  sqmName='SQM'
        >>>                  globalWeatherName='OpenWeather'
        >>>                 )
    """

    __all__ = ['Environment',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 10 seconds for setting indi server
    UPDATE_RATE = 10

    def __init__(self,
                 host=None,
                 localWeatherName='',
                 sqmName='',
                 globalWeatherName='',
                 ):
        super().__init__()

        self.client = indiBase.Client(host=host)

        self.localWeatherName = localWeatherName
        self.sqmName = sqmName
        self.globalWeatherName = globalWeatherName

        self.localWeatherDevice = None
        self.sqmDevice = None
        self.globalWeatherDevice = None

        self.localWeatherData = {}
        self.globalWeatherData = {}
        self.sqmData = {}

        # link signals
        self.client.signals.newDevice.connect(self.newDevice)
        self.client.signals.removeDevice.connect(self.removeDevice)
        self.client.signals.newProperty.connect(self.connectDevice)
        self.client.signals.newNumber.connect(self.updateData)

    @property
    def localWeatherName(self):
        return self._localWeatherName

    @localWeatherName.setter
    def localWeatherName(self, value):
        self._localWeatherName = value

    @property
    def sqmName(self):
        return self._sqmName

    @sqmName.setter
    def sqmName(self, value):
        self._sqmName = value

    @property
    def globalWeatherName(self):
        return self._globalWeatherName

    @globalWeatherName.setter
    def globalWeatherName(self, value):
        self._globalWeatherName = value

    def newDevice(self, deviceName):
        """
        newDevice is called whenever a new device entry is received in indi client. it
        adds the device if the name fits to the given name in configuration.

        :param deviceName:
        :return:
        """

        if not self.client.isServerConnected():
            return False
        if deviceName == self.localWeatherName:
            self.localWeatherDevice = self.client.getDevice(deviceName)
        elif deviceName == self.sqmName:
            self.sqmDevice = self.client.getDevice(self.sqmName)
        elif deviceName == self.globalWeatherName:
            self.globalWeatherDevice = self.client.getDevice(deviceName)

    def removeDevice(self, deviceName):
        """

        :param deviceName:
        :return:
        """

        if not self.client.isServerConnected():
            return False
        if deviceName == self.localWeatherName:
            self.localWeatherDevice = None
        elif deviceName == self.sqmName:
            self.sqmDevice = None
        elif deviceName == self.globalWeatherName:
            self.globalWeatherDevice = None

    def startCommunication(self):
        """
        startCommunication adds a device on the watch list of the server and does a first
        setup and config for the device. basically the update rates are set to 10 seconds.

        :return: success of reconnecting to server
        """
        suc = self.client.connectServer()
        if self.localWeatherName:
            self.client.watchDevice(self.localWeatherName)
        if self.globalWeatherName:
            self.client.watchDevice(self.globalWeatherName)
        if self.sqmName:
            self.client.watchDevice(self.sqmName)
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
        deviceList = [self.localWeatherName,
                      self.globalWeatherName,
                      self.sqmName
                      ]
        if deviceName in deviceList:
            self.client.connectDevice(deviceName=deviceName)
        return True

    def getDeviceStatus(self):
        """
        getDeviceStatus is a generator for the connection state of the devices. it reads
        the device status ot of the client and returns the deviceKey and the status value

        :return: yields the device key and status
        """

        deviceNameList = {'localWeather': self.localWeatherName,
                          'globalWeather': self.globalWeatherName,
                          'sqm': self.sqmName,
                          }

        for deviceKey, deviceName in deviceNameList.items():
            if deviceName not in self.client.devices:
                yield deviceKey, ''
                continue
            device = self.client.getDevice(deviceName)
            status = device.getSwitch('CONNECTION')['CONNECT']
            if status:
                yield deviceKey, 'green'
            else:
                yield deviceKey, 'red'

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

        :param deviceName:
        :param propertyName:
        :return:
        """

        deviceNameList = {self.localWeatherName: self.localWeatherData,
                          self.globalWeatherName: self.globalWeatherData,
                          self.sqmName: self.sqmData,
                          }
        if deviceName not in deviceNameList.keys():
            return False
        if deviceName not in self.client.devices:
            return False

        device = self.client.getDevice(deviceName)
        # calculate dew point globally
        if deviceName == self.globalWeatherName:
            temp = device.getNumber(propertyName).get('WEATHER_TEMPERATURE', 0)
            humidity = device.getNumber(propertyName).get('WEATHER_HUMIDITY', 0)
            dewPoint = self._getDewPoint(temp, humidity)
            self.globalWeatherData['WEATHER_DEWPOINT'] = dewPoint

        for element, value in device.getNumber(propertyName).items():
            data = deviceNameList[deviceName]
            data[element] = value
        return True
