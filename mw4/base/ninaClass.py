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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import json

# external packages
from PyQt5.QtCore import QTimer, QObject
import requests

# local imports
from base.driverDataClass import DriverData
from base.driverDataClass import RemoteDeviceShutdown
from base.tpool import Worker


class NINAClass(DriverData, QObject):
    """
    """
    log = logging.getLogger(__name__)

    NINA_TIMEOUT = 1
    HOST_ADDR = '127.0.0.1'
    PORT = 59590
    PROTOCOL = 'http'
    BASE_URL = f'{PROTOCOL}://{HOST_ADDR}:{PORT}'

    def __init__(self, app=None, data=None):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool
        self.msg = app.msg
        self.data = data
        self.updateRate = 1000
        self.loadConfig = False
        self._deviceName = ''
        self.defaultConfig = {
            'deviceList': ['N.I.N.A. controlled'],
            'deviceName': 'N.I.N.A. controlled',
        }
        self.signalRS = RemoteDeviceShutdown()

        self.deviceConnected = False
        self.serverConnected = False

        self.cycleDevice = QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.pollStatus)

        self.cycleData = QTimer()
        self.cycleData.setSingleShot(False)
        self.cycleData.timeout.connect(self.pollData)
        self.signalRS.signalRemoteShutdown.connect(self.stopCommunication)

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
            t = f'N.I.N.A: [{self.BASE_URL}/{valueProp}?format=json]'
            if params is not None:
                t += f' data: [{bytes(json.dumps(params).encode("utf-8"))}]'
                self.log.trace('POST ' + t)
                response = requests.post(f'{self.BASE_URL}/{valueProp}?format=json',
                                         json=params,
                                         timeout=self.NINA_TIMEOUT)
            else:
                self.log.trace('GET ' + t)
                response = requests.get(f'{self.BASE_URL}/{valueProp}?format=json',
                                        timeout=self.NINA_TIMEOUT)
        except requests.exceptions.Timeout:
            self.log.debug('Request N.I.N.A. timeout error')
            return None
        except requests.exceptions.ConnectionError:
            self.log.error('Request N.I.N.A. connection error')
            return None
        except Exception as e:
            self.log.error(f'Request N.I.N.A. error: [{e}]')
            return None

        if response.status_code != 200:
            t = f'Request N.I.N.A. response invalid: [{response.status_code}]'
            self.log.warning(t)
            return None

        self.log.trace(f'Request N.I.N.A. response: [{response.json()}]')
        response = response.json()
        return response

    def connectDevice(self):
        """
        :return:
        """
        devName = self.deviceName.replace(' ', '%20')
        prop = f'connectdevice/{self.DEVICE_TYPE}/{devName}'
        response = self.requestProperty(prop)
        if response is None:
            return False

        return response['Success']

    def disconnectDevice(self):
        """
        :return:
        """
        prop = f'disconnectdevice/{self.DEVICE_TYPE}'
        response = self.requestProperty(prop)
        if response is None:
            return False

        return response['Success']

    def enumerateDevice(self):
        """
        :return:
        """
        prop = f'enumdevices/{self.DEVICE_TYPE}'
        response = self.requestProperty(prop)
        if response is None:
            return []

        return response['Devices']

    def workerConnectDevice(self):
        """
        :return: success of reconnecting to server
        """
        if self.deviceName == 'N.I.N.A. controlled':
            return True

        for retry in range(0, 20):
            suc = self.connectDevice()
            if suc:
                t = f'[{self.deviceName}] connected, [{retry}] retries'
                self.log.debug(t)
                break
            else:
                t = f' [{self.deviceName}] Connection retry: [{retry}]'
                self.log.info(t)

        if suc:
            t = f'[{self.deviceName}] connected'
            self.log.debug(t)
        else:
            self.msg.emit(2, 'N.I.N.A.', 'Connect error',
                          f'{self.deviceName}')
            self.deviceConnected = False
            self.serverConnected = False
        return suc

    def startTimer(self):
        """
        :return: true for test purpose
        """
        self.cycleData.start(self.updateRate)
        self.cycleDevice.start(self.updateRate)
        return True

    def stopTimer(self):
        """
        :return: true for test purpose
        """
        self.cycleData.stop()
        self.cycleDevice.stop()
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

    def workerGetInitialConfig(self):
        pass

    def getInitialConfig(self):
        """
        :return: success
        """
        worker = Worker(self.workerGetInitialConfig)
        self.threadPool.start(worker)
        return True

    def workerPollStatus(self):
        """
        :return: success
        """
        prop = f'devicestatus/{self.DEVICE_TYPE}'
        response = self.requestProperty(prop)

        if response is None:
            return False

        state = response['State']
        self.storePropertyToData(state, 'Device.Status')
        if state == 3:
            self.storePropertyToData('integrating downloading image is ready',
                                     'Device.Message')
        elif state == 0:
            self.storePropertyToData('IDLE', 'Device.Message')

        if state == 5:
            if self.deviceConnected:
                self.deviceConnected = False
                self.signals.deviceDisconnected.emit(f'{self.deviceName}')
                self.msg.emit(0, 'N.I.N.A.', 'Device remove',
                              f'{self.deviceName}')
        else:
            if not self.deviceConnected:
                self.deviceConnected = True
                self.getInitialConfig()
                self.signals.deviceConnected.emit(f'{self.deviceName}')
                self.msg.emit(0, 'N.I.N.A.', 'Device found',
                              f'{self.deviceName}')
        return True

    def pollStatus(self):
        """
        :return: success
        """
        worker = Worker(self.workerPollStatus)
        self.threadPool.start(worker)
        return True

    def startCommunication(self):
        """
        :return: True for test purpose
        """
        self.data.clear()
        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()

        worker = Worker(self.workerConnectDevice)
        worker.signals.result.connect(self.startTimer)
        self.threadPool.start(worker)
        return True

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        self.stopTimer()
        if self.deviceName != 'N.I.N.A. controlled':
            self.disconnectDevice()
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(f'{self.deviceName}')
        self.signals.serverDisconnected.emit({f'{self.deviceName}': 0})
        self.msg.emit(0, 'N.I.N.A.', 'Device remove',
                      f'{self.deviceName}')
        return True

    def discoverDevices(self):
        """
        :return: device list
        """
        discoverList = self.enumerateDevice()
        return discoverList
