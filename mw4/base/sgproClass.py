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
import logging
import json

# external packages
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest
import requests

# local imports
from base.driverDataClass import DriverData
from base.tpool import Worker


class SGProClass(DriverData):
    """
    """
    log = logging.getLogger(__name__)

    CYCLE_POLL_STATUS = 1000
    CYCLE_POLL_DATA = 1000
    SGPRO_TIMEOUT = 10
    HOST_ADDR = '127.0.0.1'
    PORT = 59590
    PROTOCOL = 'http'
    BASE_URL = f'{PROTOCOL}://{HOST_ADDR}:{PORT}/json/reply'

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()
        self.app = app
        self.threadPool = threadPool
        self.data = data
        self._deviceName = ''
        self.defaultConfig = {
            'sgpro': {
                'deviceName': '',
                'deviceList': [],
            }
        }

        self.deviceConnected = False
        self.serverConnected = False

        self.cycleDevice = QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.pollStatus)

        self.cycleData = QTimer()
        self.cycleData.setSingleShot(False)
        self.cycleData.timeout.connect(self.pollData)

    @property
    def deviceName(self):
        return self._deviceName

    @deviceName.setter
    def deviceName(self, value):
        self._deviceName = value

    def requestProperty(self, valueProp, params=None):
        """
        :param valueProp:
        :param params:
        :return:
        """
        try:
            response = requests.post(f'{self.BASE_URL}/{valueProp}',
                                     data=bytes(json.dumps(params).encode('utf-8')),
                                     timeout=self.SGPRO_TIMEOUT)
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.ConnectionError:
            return None
        except Exception as e:
            return None

        if response.status_code != 200:
            return None

        response = response.json()
        return response

    def sgConnectDevice(self):
        params = {'Device': self.DEVICE_TYPE,
                  'DeviceName': self.deviceName}
        response = self.requestProperty('SgConnectDevice', params=params)
        if response is None:
            return False
        return response['Success']

    def sgDisconnectDevice(self):
        params = {'Device': self.DEVICE_TYPE}
        response = self.requestProperty('SgDisconnectDevice', params=params)
        if response is None:
            return False
        return response['Success']

    def sgEnumerateDevice(self):
        params = {'Device': self.DEVICE_TYPE}
        response = self.requestProperty('SgEnumerateDevices', params=params)
        if response is None:
            return False
        return response['Devices']

    def getAndStoreSGProProperty(self, valueProp, element, elementInv=None):
        """
        :param valueProp:
        :param element:
        :param elementInv:
        :return: reset entry
        """
        self.storePropertyToData(value, element, elementInv)
        return True

    def workerConnectDevice(self):
        """
        :return: success of reconnecting to server
        """
        suc = self.sgConnectDevice()

        if suc:
            t = f'[{self.deviceName}] connected'
            self.log.debug(t)

        if not suc:
            self.app.message.emit(f'SGPro connect error: [{self.deviceName}]', 2)
            self.deviceConnected = False
            self.serverConnected = False
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'SGPro device found:  [{self.deviceName}]', 0)

        return True

    def startTimer(self):
        """
        :return: true for test purpose
        """
        self.cycleData.start(self.CYCLE_POLL_DATA)
        self.cycleDevice.start(self.CYCLE_POLL_STATUS)
        return True

    def stopTimer(self):
        """
        :return: true for test purpose
        """
        self.cycleData.stop()
        self.cycleDevice.stop()
        return True

    def workerPollStatus(self):
        """
        :return: success
        """
        return True

    def processPolledData(self):
        pass

    def workerPollData(self):
        pass

    def pollData(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False
        worker = Worker(self.workerPollData)
        worker.signals.result.connect(self.processPolledData)
        self.threadPool.start(worker)
        return True

    def pollStatus(self):
        """
        :return: success
        """
        worker = Worker(self.workerPollStatus)
        self.threadPool.start(worker)
        return True

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return: True for test purpose
        """
        worker = Worker(self.workerConnectDevice)
        # worker.signals.finished.connect(self.startTimer)
        self.threadPool.start(worker)
        return True

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        # self.stopTimer()
        self.sgDisconnectDevice()
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(f'{self.deviceName}')
        self.signals.serverDisconnected.emit({f'{self.deviceName}': 0})
        self.app.message.emit(f'SGPro device remove: [{self.deviceName}]', 0)
        return True

    def discoverDevices(self):
        """
        :return: device list
        """
        discoverList = self.sgEnumerateDevice()
        return discoverList
