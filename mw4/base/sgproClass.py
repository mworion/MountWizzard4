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
import uuid

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
    SGPRO_TIMEOUT = 3

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()
        self.app = app
        self.threadPool = threadPool
        self.data = data

        self._host = ('localhost', 11111)
        self._hostaddress = 'localhost'
        self._deviceName = ''
        self.deviceType = ''

        self.defaultConfig = {
            'sgpro': {
                'deviceName': '',
                'deviceList': [],
                'hostaddress': 'localhost',
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
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def hostaddress(self):
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value):
        self._hostaddress = value
        self._host = (self._hostaddress, self._port)

    @property
    def deviceName(self):
        return self._deviceName

    @deviceName.setter
    def deviceName(self, value):
        self._deviceName = value

    def generateBaseUrl(self):
        """
        :return: value for base url
        """
        val = '{0}://{1}:{2}/api/v{3}/{4}/{5}'.format(
            self.protocol,
            self.host[0],
            self.host[1],
            self.apiVersion,
            self.deviceType,
            self.number,
        )
        return val

    def getSGProProperty(self, valueProp, **data):
        """
        :param valueProp:
        :param data:
        :return:
        """
        if not self.deviceName:
            return None
        if valueProp in self.propertyExceptions:
            return None

        uid = uuid.uuid4().int % 2**32
        data['ClientTransactionID'] = uid

        t = f'[{self.deviceName}] [{uid:10d}], get [{valueProp}], data:[{data}]'
        self.log.trace(t)

        try:
            response = requests.get(f'{self.baseUrl}/{valueProp}',
                                    params=data, timeout=self.SGPRO_TIMEOUT)
        except requests.exceptions.Timeout:
            t = f'[{self.deviceName}] [{uid:10d}] has timeout'
            self.log.debug(t)
            return None
        except requests.exceptions.ConnectionError:
            t = f'[{self.deviceName}] [{uid:10d}] has connection error'
            self.log.warning(t)
            return None
        except Exception as e:
            t = f'[{self.deviceName}] [{uid:10d}] has exception: [{e}]'
            self.log.error(t)
            return None

        if response.status_code == 400 or response.status_code == 500:
            t = f'[{self.deviceName}] [{uid:10d}], stat 400/500, [{response.text}]'
            self.log.warning(t)
            return None

        response = response.json()
        if response['ErrorNumber'] != 0:
            t = f'[{self.deviceName}] [{uid:10d}], response: [{response}]'
            self.log.warning(t)
            self.propertyExceptions.append(valueProp)
            return None

        if valueProp != 'imagearray':
            t = f'[{self.deviceName}] [{uid:10d}], response: [{response}]'
            self.log.trace(t)

        return response['Value']

    def setSGProProperty(self, valueProp, **data):
        """
        :param valueProp:
        :param data:
        :return:
        """
        if not self.deviceName:
            return None
        if valueProp in self.propertyExceptions:
            return None

        uid = uuid.uuid4().int % 2**32
        t = f'[{self.deviceName}] [{uid:10d}], set [{valueProp}] to: [{data}]'
        self.log.trace(t)

        try:
            response = requests.put(f'{self.baseUrl}/{valueProp}',
                                    data=data, timeout=self.SGPRO_TIMEOUT)
        except requests.exceptions.Timeout:
            t = f'[{self.deviceName}] [{uid:10d}] has timeout'
            self.log.debug(t)
            return None
        except requests.exceptions.ConnectionError:
            t = f'[{self.deviceName}] [{uid:10d}] has connection error'
            self.log.warning(t)
            return None
        except Exception as e:
            t = f'[{self.deviceName}] [{uid:10d}] has exception: [{e}]'
            self.log.error(t)
            return None

        if response.status_code == 400 or response.status_code == 500:
            t = f'[{self.deviceName}] [{uid:10d}], stat 400/500, [{response.text}]'
            self.log.warning(t)
            return None

        response = response.json()
        if response['ErrorNumber'] != 0:
            t = f'[{self.deviceName}] [{uid:10d}], response: [{response}]'
            self.log.warning(t)
            self.propertyExceptions.append(valueProp)
            return None

        t = f'[{self.deviceName}] [{uid:10d}], response: [{response}]'
        self.log.trace(t)
        return response

    def getAndStoreSGProProperty(self, valueProp, element, elementInv=None):
        """
        :param valueProp:
        :param element:
        :param elementInv:
        :return: reset entry
        """
        value = self.getSGProProperty(valueProp)
        self.storePropertyToData(value, element, elementInv)
        return True

    def workerConnectDevice(self):
        """
        :return: success of reconnecting to server
        """
        self.propertyExceptions = []
        for retry in range(0, 10):
            self.setSGProProperty('connected', Connected=True)
            suc = self.getSGProProperty('connected')

            if suc:
                t = f'[{self.deviceName}] connected, [{retry}] retries'
                self.log.debug(t)
                break
            else:
                t = f' [{self.deviceName}] Connection retry: [{retry}]'
                self.log.info(t)
                QTest.qWait(250)

        if not suc:
            self.app.message.emit(f'SGPRO connect error:[{self.deviceName}]', 2)
            self.deviceConnected = False
            self.serverConnected = False
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'SGPRO device found: [{self.deviceName}]', 0)

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

    def workerGetInitialConfig(self):
        """
        :return:
        """
        self.data['DRIVER_INFO.DRIVER_NAME'] = self.getSGProProperty('name')
        self.data['DRIVER_INFO.DRIVER_VERSION'] = self.getSGProProperty('driverversion')
        self.data['DRIVER_INFO.DRIVER_EXEC'] = self.getSGProProperty('driverinfo')
        return True

    def workerPollStatus(self):
        """
        :return: success
        """
        suc = self.getSGProProperty('connected')
        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.signals.deviceDisconnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'SGPRO device remove:[{self.deviceName}]', 0)

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'SGPRO device found: [{self.deviceName}]', 0)

        return suc

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
        if not self.deviceConnected:
            return False
        worker = Worker(self.workerPollStatus)
        self.threadPool.start(worker)
        return True

    def getInitialConfig(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False
        worker = Worker(self.workerGetInitialConfig)
        self.threadPool.start(worker)
        return True

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return: True for test purpose
        """
        worker = Worker(self.workerConnectDevice)
        worker.signals.finished.connect(self.getInitialConfig)
        worker.signals.finished.connect(self.startTimer)
        self.threadPool.start(worker)
        return True

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        self.stopTimer()
        self.setSGProProperty('connected', Connected=False)
        self.deviceConnected = False
        self.serverConnected = False
        self.propertyExceptions = []
        self.signals.deviceDisconnected.emit(f'{self.deviceName}')
        self.signals.serverDisconnected.emit({f'{self.deviceName}': 0})
        self.app.message.emit(f'SGPRO device remove:[{self.deviceName}]', 0)
        return True
