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
import logging
import json
import os

# external packages
import numpy as np
import requests

# local imports
from base.tpool import Worker
from base.driverDataClass import Signals


class OnlineWeather():
    """
    """

    __all__ = ['OnlineWeather']
    log = logging.getLogger(__name__)

    def __init__(self, app=None):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool
        self.signals = Signals()
        self.location = app.mount.obsSite.location

        # minimum set for driver package built in
        self.framework = ''
        self.run = {
            'onlineWeather': self
        }
        self.deviceName = ''

        self.data = {}
        self.defaultConfig = {
            'framework': '',
            'frameworks': {
                'onlineWeather': {
                    'deviceName': 'OnlineWeather',
                    'apiKey': '',
                    'hostaddress': 'api.openweathermap.org',
                }
            }
        }
        self.running = False
        self.enabled = False
        self.hostaddress = ''
        self.apiKey = ''
        self._online = False
        self.app.update10s.connect(self.pollOpenWeatherMapData)

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, value):
        self._online = value
        self.pollOpenWeatherMapData()

    def startCommunication(self):
        """
        :return: success of reconnecting to server
        """
        self.enabled = True
        self.pollOpenWeatherMapData()
        return True

    def stopCommunication(self):
        """
        :return: success of reconnecting to server
        """
        self.enabled = False
        self.running = False
        self.data.clear()
        self.signals.deviceDisconnected.emit('OnlineWeather')
        return True

    @staticmethod
    def getDewPoint(tempAir, relativeHumidity):
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

    def processOpenWeatherMapData(self):
        """
        :return: success
        """
        dataFile = self.app.mwGlob['dataDir'] + '/openweathermap.data'
        if not os.path.isfile(dataFile):
            self.log.info(f'{dataFile} not available')
            return False

        try:
            with open(self.app.mwGlob['dataDir'] + '/openweathermap.data', 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.log.warning(f'Cannot load data file, error: {e}')
            return False

        if 'list' not in data:
            self.data.clear()
            return False

        if len(data['list']) == 0:
            self.data.clear()
            return False

        val = data['list'][0]
        self.log.trace(f'onlineWeatherData:[{val}]')

        if 'main' in val:
            self.data['temperature'] = val['main']['temp'] - 273.15
            self.data['pressure'] = val['main']['grnd_level']
            self.data['humidity'] = val['main']['humidity']
            self.data['dewPoint'] = self.getDewPoint(self.data['temperature'],
                                                     self.data['humidity'])
            self.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = self.data['temperature']
            self.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = self.data['pressure']

        if 'clouds' in val:
            self.data['cloudCover'] = val['clouds']['all']

        if 'wind' in val:
            self.data['windSpeed'] = val['wind']['speed']
            self.data['windDir'] = val['wind']['deg']

        if 'rain' in val:
            self.data['rain'] = val['rain']['3h']
        else:
            self.data['rain'] = 0
        return True

    def workerGetOpenWeatherMapData(self, url):
        """
        :param url:
        :return: data
        """
        try:
            data = requests.get(url, timeout=30)
        except TimeoutError:
            self.log.warning(f'[{url}] not reachable')
            return False
        except Exception as e:
            self.log.critical(f'[{url}] general exception: [{e}]')
            return False
        if data.status_code != 200:
            self.log.warning(f'[{url}] status is not 200')
            return False

        with open(self.app.mwGlob['dataDir'] + '/openweathermap.data', 'w+') as f:
            json.dump(data.json(), f, indent=4)
            self.log.trace(data.json())
        return True

    def sendStatus(self, status):
        """
        :return:
        """
        if not status and self.running:
            self.signals.deviceDisconnected.emit('OnlineWeather')
        elif status and not self.running:
            self.signals.deviceConnected.emit('OnlineWeather')
        return True

    def getOpenWeatherMapData(self, url=''):
        """
        :param url:
        :return: true for test purpose
        """
        worker = Worker(self.workerGetOpenWeatherMapData, url)
        worker.signals.finished.connect(self.processOpenWeatherMapData)
        worker.signals.result.connect(self.sendStatus)
        self.threadPool.start(worker)
        return True

    def loadingFileNeeded(self, fileName, hours):
        """
        :param fileName:
        :param hours:
        :return:
        """
        filePath = self.app.mwGlob['dataDir'] + '/' + fileName
        if not os.path.isfile(filePath):
            return True

        ageData = self.app.mount.obsSite.loader.days_old(fileName)
        if ageData < hours / 24:
            return False
        else:
            return True

    def pollOpenWeatherMapData(self):
        """
        updateOpenWeatherMap downloads the actual OpenWeatherMap image and
        displays it in environment tab. it checks first if online is set,
        otherwise not download will take place. it will be updated every 10 minutes.

        :return: success
        """
        if not self.enabled:
            return False
        if not self.apiKey:
            return False

        if not self.online and self.running:
            self.signals.deviceDisconnected.emit('OnlineWeather')
            self.running = False
            return False
        elif self.online and not self.running:
            self.signals.deviceConnected.emit('OnlineWeather')
            self.running = True

        if not self.loadingFileNeeded('openweathermap.data', 1):
            self.processOpenWeatherMapData()
            return True

        lat = self.location.latitude.degrees
        lon = self.location.longitude.degrees

        webSite = f'http://{self.hostaddress}/data/2.5/forecast'
        url = f'{webSite}?lat={lat:1.2f}&lon={lon:1.2f}&APPID={self.apiKey}'
        self.getOpenWeatherMapData(url=url)
        self.log.debug(f'{url}')
        return True
