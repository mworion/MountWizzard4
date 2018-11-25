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
from datetime import datetime
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
        >>>                  globalWeatherName='OpenWeatherMap'
        >>>                 )
    """

    __all__ = ['Environment',
               ]

    version = '0.1'
    logger = logging.getLogger(__name__)

    # update rate to 10 seconds for setting indi server
    UPDATE_RATE = 10

    # data from open weather map (id, [text, day icon, night icon]
    WEATHER_ID = {
        200: ['thunderstorm with light rain', '11d', '11n'],
        201: ['thunderstorm with rain', '11d', '11n'],
        202: ['thunderstorm with heavy rain', '11d', '11n'],
        210: ['light thunderstorm', '11d', '11n'],
        211: ['thunderstorm', '11d', '11n'],
        212: ['heavy thunderstorm', '11d', '11n'],
        221: ['ragged thunderstorm', '11d', '11n'],
        230: ['thunderstorm with light drizzle', '11d', '11n'],
        231: ['thunderstorm with drizzle', '11d', '11n'],
        232: ['thunderstorm with heavy drizzle', '11d', '11n'],
        300: ['light intensity drizzle', '09d', '09n'],
        301: ['drizzle', '09d', '09n'],
        302: ['heavy intensity drizzle', '09d', '09n'],
        310: ['light intensity drizzle rain', '09d', '09n'],
        311: ['drizzle rain', '09d', '09n'],
        312: ['heavy intensity drizzle rain', '09d', '09n'],
        313: ['shower rain and drizzle', '09d', '09n'],
        314: ['heavy shower rain and drizzle', '09d', '09n'],
        321: ['shower drizzle', '09d', '09n'],
        500: ['light rain', '10d', '10n'],
        501: ['moderate rain', '10d', '10n'],
        502: ['heavy intensity rain', '10d', '10n'],
        503: ['very heavy rain', '10d', '10n'],
        504: ['extreme rain', '10d', '10n'],
        511: ['freezing rain', '13d', '13n'],
        520: ['light intensity shower rain', '09d', '09n'],
        521: ['shower rain', '09d', '09n'],
        522: ['heavy intensity shower rain', '09d', '09n'],
        531: ['ragged shower rain', '09d', '09n'],
        600: ['light snow', '13d', '13n'],
        601: ['snow', '13d', '13n'],
        602: ['heavy snow', '13d', '13n'],
        611: ['sleet', '13d', '13n'],
        612: ['shower sleet', '13d', '13n'],
        615: ['light rain and snow', '13d', '13n'],
        616: ['rain and snow', '13d', '13n'],
        620: ['light shower snow', '13d', '13n'],
        621: ['shower snow', '13d', '13n'],
        622: ['heavy shower snow', '13d', '13n'],
        701: ['mist', '50d', '50n'],
        711: ['smoke', '50d', '50n'],
        721: ['haze', '50d', '50n'],
        731: ['sand, dust whirls', '50d', '50n'],
        741: ['fog', '50d', '50n'],
        751: ['sand', '50d', '50n'],
        761: ['dust', '50d', '50n'],
        762: ['volcanic ash', '50d', '50n'],
        771: ['squalls', '50d', '50n'],
        781: ['tornado', '50d', '50n'],
        800: ['clear sky', '01d', '01n'],
        801: ['few clouds', '02d', '02n'],
        802: ['scattered clouds', '03d', '03n'],
        803: ['broken clouds', '04d', '04n'],
        804: ['overcast clouds', '04d', '04n'],
    }

    def __init__(self,
                 host=None,
                 localWeatherName='',
                 sqmName='',
                 globalWeatherName='',
                 ):
        super().__init__()

        self.client = indiBase.Client(host=host)

        self.wDevice = {'local': {'name': localWeatherName,
                                  'data': {},
                                  'device': None,
                                  },
                        'global': {'name': globalWeatherName,
                                   'data': {},
                                   'device': None,
                                   },
                        'sqm': {'name': sqmName,
                                'data': {},
                                'device': None,
                                },
                        }

        # link signals
        self.client.signals.newDevice.connect(self.newDevice)
        self.client.signals.removeDevice.connect(self.removeDevice)
        self.client.signals.newProperty.connect(self.connectDevice)
        self.client.signals.newNumber.connect(self.updateData)
        self.client.signals.newNumber.connect(self._setUpdateRate)

    @property
    def localWeatherName(self):
        return self.wDevice['local']['name']

    @localWeatherName.setter
    def localWeatherName(self, value):
        self.wDevice['local']['name'] = value

    @property
    def sqmName(self):
        return self.wDevice['sqm']['name']

    @sqmName.setter
    def sqmName(self, value):
        self.wDevice['sqm']['name'] = value

    @property
    def globalWeatherName(self):
        return self.wDevice['global']['name']

    @globalWeatherName.setter
    def globalWeatherName(self, value):
        self.wDevice['global']['name'] = value

    def newDevice(self, deviceName):
        """
        newDevice is called whenever a new device entry is received in indi client. it
        adds the device if the name fits to the given name in configuration.

        :param deviceName:
        :return:
        """

        if not self.client.isServerConnected():
            return False

        for wType in self.wDevice:
            if deviceName != self.wDevice[wType]['name']:
                continue
            self.wDevice[wType]['device'] = self.client.getDevice(deviceName)

    def removeDevice(self, deviceName):
        """
        removeDevice is called whenever a device is removed from indi client. it sets
        the device entry to None

        :param deviceName:
        :return:
        """

        if not self.client.isServerConnected():
            return False

        for wType in self.wDevice:
            if deviceName != self.wDevice[wType]['name']:
                continue
            self.wDevice[wType]['device'] = None
            self.wDevice[wType]['data'] = {}

    def startCommunication(self):
        """
        startCommunication adds a device on the watch list of the server.

        :return: success of reconnecting to server
        """

        suc = self.client.connectServer()
        for wType in self.wDevice:
            if not self.wDevice[wType]['name']:
                continue
            self.client.watchDevice(self.wDevice[wType]['name'])
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

        for wType in self.wDevice:
            if deviceName != self.wDevice[wType]['name']:
                continue
            self.client.connectDevice(deviceName=deviceName)
        return True

    def getDeviceStatus(self):
        """
        getDeviceStatus is a generator for the connection state of the devices. it reads
        the device status ot of the client and returns the deviceKey and the status value

        :return: yields the device key and status
        """

        for wType in self.wDevice:
            device = self.wDevice[wType]['device']
            if device is None:
                yield wType, ''
                continue
            status = device.getSwitch('CONNECTION')['CONNECT']
            if status:
                yield wType, 'green'
            else:
                yield wType, 'red'

    def _setUpdateRate(self, deviceName):
        """
        _setUpdateRate corrects the update rate of weather devices to get an defined
        setting regardless, what is setup in server side.

        :param deviceName:
        :return:    success for test purpose
        """

        for wType in self.wDevice:
            if deviceName != self.wDevice[wType]['name']:
                continue
            device = self.wDevice[wType]['device']
            if device is None:
                return False
            if deviceName not in ['local', 'global']:
                continue
            update = device.getNumber('WEATHER_UPDATE')
            if update['PERIOD'] != 10:
                update['PERIOD'] = 10
                self.client.sendNewNumber(deviceName=deviceName,
                                          propertyName='WEATHER_UPDATE',
                                          elements=update)
        return True

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

        for wType in self.wDevice:
            device = self.client.getDevice(deviceName)
            if device is None:
                return False
            if deviceName != self.wDevice[wType]['name']:
                continue
            for element, value in device.getNumber(propertyName).items():
                data = self.wDevice[wType]['data']
                data[element] = value
                elArray = element + '_ARRAY'
                elTime = element + '_TIME'
                if elArray not in data:
                    data[elArray] = np.full(100, value)
                    data[elTime] = np.full(100, datetime.now())
                else:
                    data[elArray] = np.roll(data[elArray], 1)
                    data[elArray][0] = value
                    data[elTime] = np.roll(data[elTime], 1)
                    data[elTime][0] = datetime.now()

            # in case of global weather we calculate the dew point manually
            if wType == 'global':
                temp = self.wDevice[wType]['data']['WEATHER_TEMPERATURE']
                humidity = self.wDevice[wType]['data']['WEATHER_HUMIDITY']
                dewPoint = self._getDewPoint(temp, humidity)
                self.wDevice['global']['data']['WEATHER_DEWPOINT'] = dewPoint

        return True

    def getFilteredRefracParams(self):
        """
        getFilteredRefracParams filters local temperature and pressure with and moving
        average filter over 5 minutes and returns the filtered values.

        :return:  temperature and pressure
        """

        isTemperature = 'WEATHER_TEMPERATURE_ARRAY' in self.wDevice['local']['data']
        isPressure = 'WEATHER_BAROMETER_ARRAY' in self.wDevice['local']['data']
        if isTemperature and isPressure:
            temp = np.mean(self.wDevice['local']['data']['WEATHER_TEMPERATURE_ARRAY'][:10])
            press = np.mean(self.wDevice['local']['data']['WEATHER_BAROMETER_ARRAY'][:10])
            return temp, press
        else:
            return None, None
