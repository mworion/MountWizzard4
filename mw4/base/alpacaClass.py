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

# external packages
from PyQt5.QtCore import QTimer

# local imports
from base.driverDataClass import DriverData, Signals
from base.tpool import Worker


class AlpacaClass(DriverData, Signals):
    """
    the class AlpacaClass inherits all information and handling of alpaca devices
    this class will be only referenced from other classes and not directly used

        >>> a = AlpacaClass(app=None, data=None, threadPool=None)
    """

    log = logging.getLogger(__name__)

    CYCLE_POLL_STATUS = 3000
    CYCLE_POLL_DATA = 3000

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()

        self.app = app
        self.threadPool = threadPool
        self.alpacaSignals = Signals()

        self.client = None
        self.data = data
        self.propertyExceptions = []

        self.protocol = 'http'
        self.host = ('localhost', 11111)
        self.apiVersion = 1
        self._deviceName = ''
        self.deviceType = ''
        self.number = 0

        self.defaultConfig = {
            'alpaca': {
                'deviceName': '',
                'deviceList': [],
                'hostaddress': 'localhost',
                'port': 11111,
                'apiVersion': 1,
                'user': '',
                'password': '',
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
    def baseUrl(self):
        return self.generateBaseUrl()

    @property
    def deviceName(self):
        return self._deviceName

    @deviceName.setter
    def deviceName(self, value):
        self._deviceName = value
        valueSplit = value.split(':')
        if len(valueSplit) != 3:
            return
        self.deviceType = valueSplit[1].strip()
        self.number = valueSplit[2].strip()
        self.number = int(self.number)

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

    def discoverAPIVersion(self):
        """
        :return:
        """
        url = '{0}://{1}:{2}/management/apiversions'.format(
            self.protocol,
            self.host[0],
            self.host[1],
        )
        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.Timeout:
            self.log.info('timeout')
            return None
        except requests.exceptions.ConnectionError:
            self.log.debug('[connection error')
            return None
        except Exception as e:
            self.log.critical(f'[error in request: {e}')
            return None

        if response.status_code == 400 or response.status_code == 500:
            self.log.debug(f'{response.text}')
            return None

        response = response.json()
        if response['ErrorNumber'] != 0:
            self.log.warning(f'{response} err:{response["ErrorNumber"]}'
                             f',{response["ErrorMessage"]}')
            return None

        self.log.trace(f'[response:{response}')
        return response['Value']

    def discoverDevices(self):
        """
        :return:
        """
        url = '{0}://{1}:{2}/management/v{3}/configureddevices'.format(
            self.protocol,
            self.host[0],
            self.host[1],
            self.apiVersion,
        )
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.Timeout:
            self.log.info('timeout')
            return None
        except requests.exceptions.ConnectionError:
            self.log.debug('[connection error')
            return None
        except Exception as e:
            self.log.critical(f'[error in request: {e}')
            return None

        if response.status_code == 400 or response.status_code == 500:
            self.log.debug(f'{response.text}')
            return None

        response = response.json()
        if response['ErrorNumber'] != 0:
            self.log.warning(f'{response} err:{response["ErrorNumber"]}'
                             f',{response["ErrorMessage"]}')
            return None

        self.log.trace(f'[response:{response}')
        return response['Value']

    def getAlpacaProperty(self, valueProp, **data):
        """
        :param valueProp:
        :param data:
        :return:
        """
        if not self.deviceName:
            return None
        if not self.deviceConnected:
            return None
        if valueProp in self.propertyExceptions:
            return None

        uid = uuid.uuid4().int % 2**32
        data['ClientTransactionID'] = uid
        self.log.trace(f'[{uid:10d}] {self.baseUrl}/{attr}], data:[{data}]')

        try:
            response = requests.get(f'{self.baseUrl}/{attr}', params=data, timeout=10)
        except requests.exceptions.Timeout:
            self.log.info(f'[{uid:10d}] timeout')
            return None
        except requests.exceptions.ConnectionError:
            self.log.debug(f'[{uid:10d}] connection error')
            return None
        except Exception as e:
            self.log.critical(f'[{uid:10d}] error in request: {e}')
            return None

        if response.status_code == 400 or response.status_code == 500:
            self.log.debug(f'{response.text}')
            return None

        response = response.json()

        if response['ErrorNumber'] != 0:
            self.log.debug(f'{response} err:{response["ErrorNumber"]}'
                           f',{response["ErrorMessage"]}')
            return None

        if attr != 'imagearray':
            self.log.trace(f'[{uid:10d}] response:{response}')

        return response['Value']

    def setAlpacaProperty(self, valueProp, **data):
        """
        :param valueProp:
        :param data:
        :return:
        """
        if not self.deviceName:
            return None
        if not self.deviceConnected:
            return None
        if valueProp in self.propertyExceptions:
            return None

        uid = uuid.uuid4().int % 2**32
        data['ClientTransactionID'] = uid
        self.log.trace(f'[{uid:08d}] {self.baseUrl}, attr:[{attr}]')

        try:
            response = requests.put(f'{self.baseUrl}/{attr}', data=data, timeout=10)
        except requests.exceptions.Timeout:
            self.log.info(f'[{uid:10d}] timeout')
            return None
        except requests.exceptions.ConnectionError:
            self.log.debug(f'[{uid:10d}] connection error')
            return None
        except Exception as e:
            self.log.critical(f'[{uid:10d}] Error in request: {e}')
            return None

        if response.status_code == 400 or response.status_code == 500:
            self.log.debug(f'[{uid:10d}] {response.text}')
            return None

        response = response.json()

        if response['ErrorNumber'] != 0:
            self.log.warning(f'err:{response["ErrorNumber"]},{response["ErrorMessage"]}')
            return None

        self.log.trace(f'[{uid:10d}] response:{response}')
        return response

    def workerConnectDevice(self):
        """
        :return: success of reconnecting to server
        """
        self.setAlpacaProperty('connected', Connected=True)
        suc = getAlpacaProperty('connected')
        self.propertyExceptions = []
        if not suc:
            self.app.message.emit(f'ALPACA connect error:[{self.deviceName}]', 2)
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.alpacaSignals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.alpacaSignals.deviceConnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ALPACA device found: [{self.deviceName}]', 0)

        return True

    def startTimer(self):
        """
        startTimer enables the cyclic timer for polling information

        :return: true for test purpose
        """
        self.cycleData.start(self.CYCLE_POLL_DATA)
        self.cycleDevice.start(self.CYCLE_POLL_STATUS)
        return True

    def stopTimer(self):
        """
        stopTimer disables the cyclic timer for polling information

        :return: true for test purpose
        """
        self.cycleData.stop()
        self.cycleDevice.stop()
        return True

    def workerGetInitialConfig(self):
        """
        :return:
        """
        self.data['DRIVER_INFO.DRIVER_NAME'] = self.getAlpacaProperty('namedevice')
        self.data['DRIVER_INFO.DRIVER_VERSION'] = self.getAlpacaProperty('driverversion')
        self.data['DRIVER_INFO.DRIVER_EXEC'] = self.getAlpacaProperty('driverinfo')
        return True

    def workerPollStatus(self):
        """
        pollStatusWorker is the thread method to be called for collecting data

        :return: success
        """
        suc = self.client.connected()
        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.signals.deviceDisconnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ALPACA device remove:[{self.deviceName}]', 0)

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ALPACA device found: [{self.deviceName}]', 0)

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
        startCommunication starts cycling of the polling.

        :param loadConfig:
        :return: True for test purpose
        """
        worker = Worker(self.workerConnectDevice)
        worker.signals.result.connect(self.getInitialConfig)
        worker.signals.finished.connect(self.startTimer)
        self.threadPool.start(worker)
        return True

    def stopCommunication(self):
        """
        stopCommunication stops cycling of the server.

        :return: true for test purpose
        """
        self.stopTimer()
        self.client.connected(Connected=False)
        self.deviceConnected = False
        self.serverConnected = False
        self.propertyExceptions = []
        self.signals.deviceDisconnected.emit(f'{self.deviceName}')
        self.signals.serverDisconnected.emit({f'{self.deviceName}': 0})
        self.app.message.emit(f'ALPACA device remove:[{self.deviceName}]', 0)
        return True

    def discoverDevices(self, deviceType=''):
        """
        discoverDevices implements a discover for devices of a certain device type. it is
        called from a button press and checks which button it was. after that for the right
        device it collects all necessary data for host value, instantiates an INDI client and
        watches for all devices connected to this server. Than it connects a subroutine for
        collecting the right device names and waits a certain amount of time. the data
        collection takes place as long as the model dialog is open. when the user closes
        this dialog, the collected data is written to the drop down list.

        :param deviceType: device type of discovered indi devices
        :return: success
        """
        devices = self.client.discoverDevices()
        if not devices:
            return []

        temp = [x for x in devices if x['DeviceType'].lower() == deviceType]
        discoverList = [f'{x["DeviceName"]}:{deviceType}:{x["DeviceNumber"]}' for x in temp]

        return discoverList
