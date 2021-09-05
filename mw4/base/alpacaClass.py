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
from base.alpacaBase import AlpacaBase
from base.driverDataClass import DriverData
from base.tpool import Worker


class AlpacaClass(DriverData):
    """
    the class AlpacaClass inherits all information and handling of alpaca devices
    this class will be only referenced from other classes and not directly used

        >>> a = AlpacaClass(app=None, data=None, threadPool=None)
    """

    log = logging.getLogger(__name__)

    # relaxed generic timing
    CYCLE_POLL_STATUS = 3000
    CYCLE_POLL_DATA = 3000

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()

        self.app = app
        self.threadPool = threadPool
        self.data = data

        self.client = AlpacaBase()

        self._hostaddress = 'localhost'
        self._port = 11111

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
    def host(self):
        return self.client.host

    @host.setter
    def host(self, value):
        self.client.host = value

    @property
    def hostaddress(self):
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value):
        self._hostaddress = value
        self.client.host = (self._hostaddress, self._port)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = int(value)
        self.client.host = (self._hostaddress, self._port)

    @property
    def deviceName(self):
        return self.client.deviceName

    @deviceName.setter
    def deviceName(self, value):
        self.client.deviceName = value

    @property
    def apiVersion(self):
        return self.client.apiVersion

    @apiVersion.setter
    def apiVersion(self, value):
        self.client.apiVersion = value

    @property
    def protocol(self):
        return self.client.protocol

    @protocol.setter
    def protocol(self, value):
        self.client.protocol = value

    def workerConnectDevice(self):
        """
        :return: success of reconnecting to server
        """
        self.client.connected(Connected=True)
        suc = self.client.connected()
        if not suc:
            self.app.message.emit(f'ALPACA connect error:[{self.deviceName}]', 2)
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.client.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.client.signals.deviceConnected.emit(f'{self.deviceName}')
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
        self.data['DRIVER_INFO.DRIVER_NAME'] = self.client.nameDevice()
        self.data['DRIVER_INFO.DRIVER_VERSION'] = self.client.driverVersion()
        self.data['DRIVER_INFO.DRIVER_EXEC'] = self.client.driverInfo()
        return True

    def workerPollStatus(self):
        """
        pollStatusWorker is the thread method to be called for collecting data

        :return: success
        """
        suc = self.client.connected()
        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.client.signals.deviceDisconnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ALPACA device remove:[{self.deviceName}]', 0)

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.client.signals.deviceConnected.emit(f'{self.deviceName}')
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
        self.client.signals.deviceDisconnected.emit(f'{self.deviceName}')
        self.client.signals.serverDisconnected.emit({f'{self.deviceName}': 0})
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
