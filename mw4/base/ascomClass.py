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
import platform
import time
if platform.system() == 'Windows':
    import win32com.client
    import pythoncom

# external packages
import PyQt5.QtCore

# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.base.tpool import Worker


class AscomSignals(PyQt5.QtCore.QObject):

    """
    The AscomSignals class offers a list of signals to be used and instantiated by
    the Ascom class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['AscomSignals']

    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal(object)
    deviceConnected = PyQt5.QtCore.pyqtSignal(str)
    deviceDisconnected = PyQt5.QtCore.pyqtSignal(str)


class AscomClass(object):
    """
    the class AscomClass inherits all information and handling of ascom devices
    this class will be only referenced from other classes and not directly used

        >>> a = AscomClass(app=None, data=None, threadPool=None)
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
        self.ascomSignals = AscomSignals()

        self.client = None
        self.data = data
        self.name = ''
        self.host = None

        self.deviceConnected = False
        self.serverConnected = False

        self.cycleDevice = PyQt5.QtCore.QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.startPollStatus)

        self.cycleData = PyQt5.QtCore.QTimer()
        self.cycleData.setSingleShot(False)
        self.cycleData.timeout.connect(self.pollData)

    def getInitialConfig(self):
        """
        getInitialConfig starts connecting the ascom device with retry and send the
        corresponding signals. basis information will be collected, too.

        :return: success of reconnecting to server
        """

        retry = 3
        while retry > 0:
            try:
                self.client.connected = True
            except Exception as e:
                self.log.warning(f'Connection error [{self.name}]: [{e}]')
            else:
                suc = self.client.connected
            finally:
                if suc:
                    break
                time.sleep(0.3)

        if not suc:
            self.app.message.emit(f'ASCOM connect error: [{self.name}]', 2)
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.ascomSignals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.ascomSignals.deviceConnected.emit(f'{self.name}')
            self.app.message.emit(f'ASCOM device found:  [{self.name}]', 0)

        self.data['DRIVER_INFO.DRIVER_NAME'] = self.client.Name
        self.data['DRIVER_INFO.DRIVER_VERSION'] = self.client.DriverVersion
        self.data['DRIVER_INFO.DRIVER_EXEC'] = self.client.DriverInfo

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

        suc = self.client.connected

        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.ascomSignals.deviceDisconnected.emit(f'{self.name}')
            self.app.message.emit(f'ASCOM device remove: [{self.name}]', 0)

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.ascomSignals.deviceConnected.emit(f'{self.name}')
            self.app.message.emit(f'ASCOM device found:  [{self.name}]', 0)

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

        pythoncom.CoInitialize()
        try:
            self.client = win32com.client.Dispatch(self.name)
        except Exception as e:
            self.log.critical(f'Error: [{e}]')
            return False
        else:
            worker = Worker(self.getInitialConfig)
            worker.signals.finished.connect(self.startTimer)
            self.threadPool.start(worker)
        finally:
            pass

        return True

    def stopCommunication(self):
        """
        stopCommunication stops cycling of the server.

        :return: true for test purpose
        """

        self.stopTimer()
        if self.client:
            self.client.connected = False
        self.deviceConnected = False
        self.serverConnected = False
        self.client = None
        pythoncom.CoUninitialize()

        self.ascomSignals.deviceDisconnected.emit(f'{self.name}')
        self.ascomSignals.serverDisconnected.emit({f'{self.name}': 0})
        self.app.message.emit(f'ASCOM device remove: [{self.name}]', 0)

        return True
