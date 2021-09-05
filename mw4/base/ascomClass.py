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
    import pythoncom
    from win32com import client

# external packages
from PyQt5.QtCore import QTimer
from PyQt5.QtTest import QTest

# local imports
from base.tpool import Worker
from base.driverDataClass import DriverData, Signals


class AscomClass(DriverData, Signals):
    """
    the class AscomClass inherits all information and handling of ascom devices
    this class will be only referenced from other classes and not directly used

        >>> a = AscomClass(app=None, data=None, threadPool=None)
    """

    log = logging.getLogger(__name__)
    CYCLE_POLL_STATUS = 3000
    CYCLE_POLL_DATA = 3000

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()

        self.app = app
        self.threadPool = threadPool
        self.ascomSignals = Signals()

        self.client = None
        self.data = data
        self.propertyExceptions = []
        self.deviceName = ''
        self.deviceConnected = False
        self.serverConnected = False

        self.defaultConfig = {
            'ascom': {
                'deviceName': '',
            }
        }

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
        self.propertyExceptions = []
        self.client.connected = True
        return True

    def disconnectClient(self):
        """
        :return:
        """
        self.propertyExceptions = []
        self.client.connected = False
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

    def getAscomProperty(self, valueProp):
        """
        :param valueProp:
        :return: value
        """
        value = None
        if valueProp in self.propertyExceptions:
            return value

        try:
            cmd = 'self.client.' + valueProp
            value = eval(cmd)
        except Exception as e:
            t = f'[{self.deviceName}]:[{cmd}], property [{valueProp}] not implemented: {e}'
            self.log.debug(t)
            self.propertyExceptions.append(valueProp)
        else:
            t = f'[{self.deviceName}]: property [{valueProp}] set to [{value}]'
            self.log.trace(t)
        finally:
            return value

    def setAscomProperty(self, valueProp, value):
        """
        :param valueProp:
        :param value:
        """
        if valueProp in self.propertyExceptions:
            return False

        try:
            cmd = 'self.client.' + valueProp + ' = value'
            exec(cmd)
        except Exception as e:
            t = f'[{self.deviceName}]:[{cmd}], property [{valueProp}] not implemented: {e}'
            self.log.debug(t)
            if valueProp != 'Connect':
                self.propertyExceptions.append(valueProp)
            return False
        else:
            t = f'[{self.deviceName}]: property [{valueProp}] set to [{value}]'
            self.log.trace(t)
            return True

    def callAscomMethod(self, method, param):
        """
        :param method:
        :param param:
        """
        if method in self.propertyExceptions:
            return False

        paramStr = f'{param}'.rstrip(')').lstrip('(')
        try:
            cmd = 'self.client.' + method + f'({paramStr})'
            exec(cmd)
        except Exception as e:
            t = f'[{self.deviceName}]:[{cmd}], method [{method}] not implemented: {e}'
            self.log.debug(t)
            self.propertyExceptions.append(method)
            return False
        else:
            t = f'[{self.deviceName}]: method [{method}] called [{param}]'
            self.log.trace(t)
            return True

    def getAndStoreAscomProperty(self, valueProp, element, elementInv=None):
        """
        :param valueProp:
        :param element:
        :param elementInv:
        :return: reset entry
        """
        value = self.getAscomProperty(valueProp)
        self.storePropertyToData(value, element, elementInv)
        return True

    def workerConnectDevice(self):
        """
        As some ASCOM devices need some time to be able to connect, we try to
        connect multiply (10) times with an waiting period 0f 250ms, so 2,5
        seconds in total.

        :return: true for test purpose
        """
        for retry in range(0, 10):
            try:
                self.connectClient()
                self.log.debug(f'Connect to [{self.deviceName}]')
            except Exception as e:
                suc = False
                t = f'Connection retry [{retry}]: [{self.deviceName}]: [{e}]'
                self.log.warning(t)
            else:
                suc = self.getAscomProperty('connected')
                if suc:
                    t = f'[{self.deviceName}] connected, [{retry}] retries'
                    self.log.debug(t)
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
        return True

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        self.getAndStoreAscomProperty('Name', 'DRIVER_INFO.DRIVER_NAME')
        self.getAndStoreAscomProperty('DriverVersion', 'DRIVER_INFO.DRIVER_VERSION')
        self.getAndStoreAscomProperty('DriverInfo', 'DRIVER_INFO.DRIVER_EXEC')
        return True

    def workerPollStatus(self):
        """
        :return: success
        """
        suc = self.getAscomProperty('connected')

        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.ascomSignals.deviceDisconnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ASCOM device remove: [{self.deviceName}]', 0)

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.ascomSignals.deviceConnected.emit(f'{self.deviceName}')
            self.app.message.emit(f'ASCOM device found:  [{self.deviceName}]', 0)

        return suc

    @staticmethod
    def callerInitUnInit(fn, *args, **kwargs):
        """
        :return: success
        """
        pythoncom.CoInitialize()
        result = fn(*args, **kwargs)
        pythoncom.CoUninitialize()
        return result

    def callMethodThreaded(self, fn, *args, cb_res=None, cb_fin=None, **kwargs):
        """
        callMethodThreaded is done mainly for ASCOM ctypes interfaces which take
        longer to end and should not slow down the gui thread itself. All called
        functions run in PyQt5 threadPool and could have callback after result is
        processed or the thread task is finished. It does not call directly the
        defined function, but the callerInitUnInit method, which does the necessary
        pythoncom.Initialize() before running win32 functions in another thread
        than the dispatch was done (in our case the main gui thread) and call
        pythoncom.CoUninitialize() after the functions finished.

        :param fn: function
        :param args:
        :param cb_res: callback
        :param cb_fin: callback
        :param kwargs:
        :return:
        """
        if not self.deviceConnected:
            return False

        worker = Worker(self.callerInitUnInit, fn, *args, **kwargs)
        if cb_res:
            worker.signals.result.connect(cb_res)
        if cb_fin:
            worker.signals.finished.connect(cb_fin)
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
        self.callMethodThreaded(self.workerPollData,
                                cb_res=self.processPolledData)
        return True

    def pollStatus(self):
        """
        :return: success
        """
        self.callMethodThreaded(self.workerPollStatus)
        return True

    def getInitialConfig(self):
        """
        :return: success
        """
        self.callMethodThreaded(self.workerGetInitialConfig)
        return True

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return: True for test purpose
        """
        if not self.deviceName:
            return False

        try:
            self.client = client.dynamic.Dispatch(self.deviceName)
            self.log.debug(f'Dispatch [{self.deviceName}]')

        except Exception as e:
            self.log.error(f'Dispatch for [{self.deviceName}] error: {e}')
            return False

        else:
            worker = Worker(self.callerInitUnInit, self.workerConnectDevice)
            worker.signals.result.connect(self.getInitialConfig)
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
                t = f'Connection to [{self.deviceName}] could not be closed, {e}'
                self.log.debug(t)

            else:
                t = f'Connection to [{self.deviceName}] closed'
                self.log.debug(t)

        self.deviceConnected = False
        self.serverConnected = False
        self.client = None
        self.propertyExceptions = []
        self.ascomSignals.deviceDisconnected.emit(f'{self.deviceName}')
        self.ascomSignals.serverDisconnected.emit({f'{self.deviceName}': 0})
        self.app.message.emit(f'ASCOM device remove: [{self.deviceName}]', 0)
        return True
