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
# written in python 3, (c) 2019, 2020 by mworion
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
from base.loggerMW import CustomLogger
from base.tpool import Worker


class AlpacaClass:
    """
    the class AlpacaClass inherits all information and handling of alpaca devices
    this class will be only referenced from other classes and not directly used

        >>> a = AlpacaClass(app=None, data=None, threadPool=None)
    """

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    # relaxed generic timing
    CYCLE_DEVICE = 3000
    CYCLE_DATA = 3000

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()

        self.app = app
        self.threadPool = threadPool

        self.client = AlpacaBase()
        self.data = data
        self.defaultConfig = {
            'alpaca': {
                'deviceName': '',
                'deviceList': [],
                'host': 'localhost',
                'port': 11111,
                'apiVersion': 1,
                'protocol': '',
                'protocolList': ['https', 'http'],
                'user': '',
                'password': '',
            }
        }

        self.deviceConnected = False
        self.serverConnected = False

        self.cycleDevice = QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.startPollStatus)

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

    def getInitialConfig(self):
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

        self.data['DRIVER_INFO.DRIVER_NAME'] = self.client.nameDevice()
        self.data['DRIVER_INFO.DRIVER_VERSION'] = self.client.driverVersion()
        self.data['DRIVER_INFO.DRIVER_EXEC'] = self.client.driverInfo()

        return True

    def startTimer(self):
        """
        startTimer enables the cyclic timer for polling information

        :return: true for test purpose
        """
        self.cycleData.start(self.CYCLE_DATA)
        self.cycleDevice.start(self.CYCLE_DEVICE)
        return True

    def stopTimer(self):
        """
        stopTimer disables the cyclic timer for polling information

        :return: true for test purpose
        """
        self.cycleData.stop()
        self.cycleDevice.stop()
        return True

    def dataEntry(self, value, element, elementInv=None):
        """

        :param value:
        :param element:
        :param elementInv:
        :return: reset entry
        """

        resetValue = value is None and element in self.data
        if resetValue:
            del self.data[element]
        else:
            self.data[element] = value

        if elementInv is None:
            return resetValue

        resetValue = value is None and elementInv in self.data
        if resetValue:
            del self.data[elementInv]
        else:
            self.data[elementInv] = value

        return resetValue

    def pollStatus(self):
        """
        pollStatus is the thread method to be called for collecting data

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

        else:
            pass

        return suc

    def emitData(self):
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
        worker.signals.result.connect(self.emitData)
        self.threadPool.start(worker)
        return True

    def startPollStatus(self):
        """
        startPollStatus starts a thread every 1 second for polling.

        :return: success
        """
        worker = Worker(self.pollStatus)
        self.threadPool.start(worker)

        return True

    def startCommunication(self, loadConfig=False):
        """
        startCommunication starts cycling of the polling.

        :param loadConfig:
        :return: True for test purpose
        """

        worker = Worker(self.getInitialConfig)
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
        discoverList = [f'{deviceType}:{x["DeviceNumber"]}:{x["DeviceName"]}' for x in temp]

        return discoverList
