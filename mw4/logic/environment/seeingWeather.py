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
from PyQt5.QtCore import pyqtSignal
import requests

# local imports
from base.tpool import Worker
from base.driverDataClass import Signals


class SeeingWeatherSignals(Signals):
    """
    """
    update = pyqtSignal()


class SeeingWeather():
    """
    """

    __all__ = ['SeeingWeather']
    log = logging.getLogger(__name__)

    def __init__(self, app=None):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool
        self.signals = SeeingWeatherSignals()
        self.location = app.mount.obsSite.location
        self.b = ''

        # minimum set for driver package built in
        self.framework = ''
        self.run = {
            'seeing': self
        }
        self.deviceName = ''
        self.data = {}
        self.defaultConfig = {
            'framework': '',
            'frameworks': {
                'seeing': {
                    'deviceName': 'meteoblue',
                    'apiKey': 'free',
                    'hostaddress': 'my.meteoblue.com',
                }
            }
        }
        self.running = False
        self.enabled = False
        self.hostaddress = ''
        self.apiKey = ''
        self._online = False
        self.app.update10m.connect(self.pollSeeingData)

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, value):
        self._online = value
        self.pollSeeingData()

    def startCommunication(self):
        """
        :return: success of reconnecting to server
        """
        self.enabled = True
        self.pollSeeingData()
        return True

    def stopCommunication(self):
        """
        :return: success of reconnecting to server
        """
        self.enabled = False
        self.running = False
        self.data.clear()
        self.signals.deviceDisconnected.emit('SeeingWeather')
        return True

    def processSeeingData(self):
        """
        :return: success
        """
        dataFile = self.app.mwGlob['dataDir'] + '/meteoblue.data'
        if not os.path.isfile(dataFile):
            self.log.info(f'{dataFile} not available')
            return False

        try:
            with open(dataFile, 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            self.log.warning(f'Cannot load data file, error: {e}')
            return False

        self.signals.update.emit()
        return True

    def workerGetSeeingData(self, url):
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
            self.log.warning(f'[{url}] status is {data.status_code}')
            return False

        data = data.json()
        self.log.trace(data)

        with open(self.app.mwGlob['dataDir'] + '/meteoblue.data', 'w+') as f:
            json.dump(data, f, indent=4)
        return True

    def sendStatus(self, status):
        """
        :return:
        """
        if not status and self.running:
            self.signals.deviceDisconnected.emit('SeeingWeather')
        elif status and not self.running:
            self.signals.deviceConnected.emit('SeeingWeather')
        return True

    def getSeeingData(self, url=''):
        """
        :param url:
        :return: true for test purpose
        """
        worker = Worker(self.workerGetSeeingData, url)
        worker.signals.finished.connect(self.processSeeingData)
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

    def pollSeeingData(self):
        """
        updateOpenWeatherMap downloads the actual OpenWeatherMap image and
        displays it in environment tab. it checks first if online is set,
        otherwise not download will take place. it will be updated every 10 minutes.

        :return: success
        """
        if not self.enabled:
            return False
        if not self.apiKey or not self.b:
            return False

        if not self.online and self.running:
            self.signals.deviceDisconnected.emit('SeeingWeather')
            self.running = False
            return False
        elif self.online and not self.running:
            self.signals.deviceConnected.emit('SeeingWeather')
            self.running = True

        if not self.loadingFileNeeded('meteoblue.data', 0.5):
            self.processSeeingData()
            return True

        lat = self.location.latitude.degrees
        lon = self.location.longitude.degrees

        webSite = f'http://{self.hostaddress}/feed/seeing_json'
        url = f'{webSite}?lat={lat:1.2f}&lon={lon:1.2f}&apikey={self.b}&tz=utc'
        self.getSeeingData(url=url)
        self.log.debug(f'{url}')
        return True
