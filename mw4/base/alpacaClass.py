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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import dateutil
import datetime
# external packages
import PyQt5.QtCore
import requests
# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.base.tpool import Worker
from mw4.base.alpacaBase import AlpacaBase


class AlpacaClass(object):
    """
    the class AlpacaClass inherits all information and handling of alpaca devices
    this class will be only referenced from other classes and not directly used

        >>> a = AlpacaClass(app=None, data={})
    """

    __all__ = ['AlpacaClass']

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    CYCLE_DEVICE = 2000
    CYCLE_DATA = 1000

    def __init__(self, app=None, data={}):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool

        self.client = AlpacaBase()
        self.name = ':0'
        self.number = 0
        self.deviceType = ''
        self.protocol = 'http'
        self.host = ('localhost', 11111)
        self.apiVersion = 1
        self.data = data

        self.deviceConnected = False
        self.serverConnected = False

        self.cycleDevice = PyQt5.QtCore.QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.startPollStatus)

        self.cycleData = PyQt5.QtCore.QTimer()
        self.cycleData.setSingleShot(False)
        self.cycleData.timeout.connect(self.pollData)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self.client.host = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.client.name = value

    @property
    def apiVersion(self):
        return self._apiVersion

    @apiVersion.setter
    def apiVersion(self, value):
        self._apiVersion = value
        self.client.apiVersion = value

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value
        self.client.protocol = value

    def getInitialConfig(self):
        """

        :return: success of reconnecting to server
        """
        self.client.connected(Connected=True)
        suc = self.client.connected()
        if not suc:
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.client.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.client.signals.deviceConnected.emit(f'{self.name}')
            self.app.message.emit(f'Alpaca device found: [{self.name}]', 0)

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
            self.client.signals.deviceDisconnected.emit(f'{self.name}')
            self.app.message.emit(f'Alpaca device remove:[{self.name}]', 0)

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.client.signals.deviceConnected.emit(f'{self.name}')
            self.app.message.emit(f'Alpaca device found: [{self.name}]', 0)

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

    def startCommunication(self):
        """
        startCommunication starts cycling of the polling.

        :return: True for connecting to server
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
        self.timeCycle.stop()
        self.deviceConnected = False
        self.serverConnected = False
        self.client.signals.deviceDisconnected.emit(f'{self.name}')
        self.client.signals.serverDisconnected.emit({f'{self.name}': 0})
        self.app.message.emit(f'Alpaca device remove:[{self.name}]', 0)

        worker = Worker(self.client.connected, Connected=False)
        worker.signals.result.connect(self.stopTimer)
        self.threadPool.start(worker)

        return True


if __name__ == '__main__':
    import time

    a = AlpacaClass()

    a.host = ('mw-develop.fritz.box', 11111)
    a.deviceType = 'dome'
    start = time.time()

    print('start', a.startCommunication())
    print(a.data)
    print('stop', a.stopCommunication())

    print(time.time() - start)
