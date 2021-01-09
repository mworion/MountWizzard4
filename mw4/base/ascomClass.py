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
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform

if platform.system() == 'Windows':
    import win32com.client
    import pythoncom

# external packages
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtTest import QTest

# local imports
from base.tpool import Worker


class AscomSignals(QObject):

    """
    The AscomSignals class offers a list of signals to be used and instantiated
    by the Ascom class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed
    from QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['AscomSignals']

    serverConnected = pyqtSignal()
    serverDisconnected = pyqtSignal(object)
    deviceConnected = pyqtSignal(str)
    deviceDisconnected = pyqtSignal(str)


class AscomClass(object):
    """
    the class AscomClass inherits all information and handling of ascom devices
    this class will be only referenced from other classes and not directly used

        >>> a = AscomClass(app=None, data=None, threadPool=None)
    """

    log = logging.getLogger(__name__)

    # relaxed generic timing
    CYCLE_POLL_STATUS = 3000
    CYCLE_POLL_DATA = 3000

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()

        self.app = app
        self.threadPool = threadPool
        self.ascomSignals = AscomSignals()

        self.client = None
        self.data = data
        self.deviceName = ''
        self.defaultConfig = {
            'ascom': {
                'deviceName': '',
            }
        }

        self.deviceConnected = False
        self.serverConnected = False

        self.cyclePollStatus = QTimer()
        self.cyclePollStatus.setSingleShot(False)
        self.cyclePollStatus.timeout.connect(self.pollStatus)

        self.cyclePollData = QTimer()
        self.cyclePollData.setSingleShot(False)
        self.cyclePollData.timeout.connect(self.pollData)

    def connectClient(self):
        """
        :return:
        """
        self.client.connected = True
        return True

    def disconnectClient(self):
        """
        :return:
        """
        self.client.connected = False
        return True

    def isClientConnected(self):
        """
        :return:
        """
        return self.client.connected

    def getInitialConfig(self):
        """
        :return: success of reconnecting to server
        """
        for retry in range(0, 10):
            try:
                self.connectClient()

            except Exception as e:
                suc = False
                self.log.warning(f'Connection error [{self.deviceName}]: [{e}]')

            else:
                suc = self.isClientConnected()
                if suc:
                    text = f'[{self.deviceName}] connected, [{retry}] retries'
                    self.log.debug(text)
                    break

            finally:
                QTest.qWait(250)

        else:
            suc = False

        if not suc:
            self.app.message.emit(f'ASCOM connect error: [{self.deviceName}]', 2)
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.ascomSignals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.ascomSignals.deviceConnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ASCOM device found:  [{self.deviceName}]', 0)

        self.data['DRIVER_INFO.DRIVER_NAME'] = self.client.Name
        self.data['DRIVER_INFO.DRIVER_VERSION'] = self.client.DriverVersion
        self.data['DRIVER_INFO.DRIVER_EXEC'] = self.client.DriverInfo
        return True

    def startTimer(self):
        """
        :return: true for test purpose
        """
        self.cyclePollData.start(self.CYCLE_POLL_DATA)
        self.cyclePollStatus.start(self.CYCLE_POLL_STATUS)
        return True

    def stopTimer(self):
        """
        :return: true for test purpose
        """
        self.cyclePollData.stop()
        self.cyclePollStatus.stop()
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

    def pollStatusWorker(self):
        """
        :return: success
        """
        try:
            suc = self.isClientConnected()

        except Exception as e:
            self.log.info(f'Connection status error [{self.deviceName}]: [{e}]')
            suc = False

        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.ascomSignals.deviceDisconnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ASCOM device remove: [{self.deviceName}]', 0)

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.ascomSignals.deviceConnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ASCOM device found:  [{self.deviceName}]', 0)

        else:
            pass

        return suc

    def callMethodThreaded(self, fn, *args, **kwargs):
        """
        :param fn:
        :param args:
        :param kwargs:
        :return:
        """
        if not self.deviceConnected:
            return False

        worker = Worker(fn, *args, **kwargs)
        self.threadPool.start(worker)
        return True

    def processPolledData(self):
        """
        :return:
        """
        pass

    def workerPollData(self):
        """
        :return:
        """
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
        worker = Worker(self.pollStatusWorker)
        self.threadPool.start(worker)
        return True

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return: True for test purpose
        """
        if not self.deviceName:
            return False

        # clsctx = pythoncom.CLSCTX_LOCAL_SERVER
        pythoncom.CoInitialize()
        try:
            self.client = win32com.client.Dispatch(self.deviceName)

        except Exception as e:
            self.log.error(f'Dispatch for [{self.deviceName}] error: {e}')
            return False

        else:
            worker = Worker(self.getInitialConfig)
            worker.signals.finished.connect(self.startTimer)
            self.threadPool.start(worker)

        return True

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        self.stopTimer()
        if self.client:
            try:
                self.disconnectClient()

            except Exception as e:
                text = f'Connection to [{self.deviceName}] could not be closed, {e}'
                self.log.debug(text)

        self.deviceConnected = False
        self.serverConnected = False
        self.client = None
        pythoncom.CoUninitialize()
        self.ascomSignals.deviceDisconnected.emit(f'{self.deviceName}')
        self.ascomSignals.serverDisconnected.emit({f'{self.deviceName}': 0})
        self.app.message.emit(f'ASCOM device remove: [{self.deviceName}]', 0)
        return True
