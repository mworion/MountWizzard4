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
# written in python3, (c) 2019-2023 by mworion
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
from PyQt5.QtCore import QTimer, QMutex

# local imports
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.tpool import Worker
from base.driverDataClass import DriverData


class AscomClass(DriverData):
    """
    """

    log = logging.getLogger(__name__)

    def __init__(self, app=None, data=None):
        super().__init__()

        self.app = app
        self.data = data
        self.threadPool = app.threadPool
        self.msg = app.msg
        self.updateRate = 3000
        self.loadConfig = False
        self.tM = QMutex()

        self.client = None
        self.propertyExceptions = []
        self.deviceName = ''
        self.deviceConnected = False
        self.serverConnected = False

        self.defaultConfig = {
            'deviceName': '',
        }

        self.cyclePollStatus = QTimer()
        self.cyclePollStatus.setSingleShot(False)
        self.cyclePollStatus.timeout.connect(self.pollStatus)

        self.cyclePollData = QTimer()
        self.cyclePollData.setSingleShot(False)
        self.cyclePollData.timeout.connect(self.pollData)

    def startTimer(self):
        """
        :return: true for test purpose
        """
        self.cyclePollData.start(self.updateRate)
        self.cyclePollStatus.start(self.updateRate)
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
            t = f'[{self.deviceName}] [{cmd}], property [{valueProp}] not implemented: {e}'
            self.log.debug(t)
            self.propertyExceptions.append(valueProp)
        else:
            if valueProp != 'ImageArray':
                t = f'[{self.deviceName}] property [{valueProp}] has value: [{value}]'
                self.log.trace(t)
            else:
                self.log.trace(f'{self.deviceName}] property [{valueProp}]')
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
            t = f'[{self.deviceName}] [{cmd}], property [{valueProp}] not implemented: {e}'
            self.log.debug(t)
            if valueProp != 'Connected':
                self.propertyExceptions.append(valueProp)
            return False
        else:
            t = f'[{self.deviceName}] property [{valueProp}] set to: [{value}]'
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
            t = f'[{self.deviceName}] [{cmd}], method [{method}] not implemented: {e}'
            self.log.debug(t)
            self.propertyExceptions.append(method)
            return False
        else:
            t = f'[{self.deviceName}] method [{method}] called [{param}]'
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
        self.propertyExceptions = []
        for retry in range(0, 10):
            self.setAscomProperty('Connected', True)
            suc = self.getAscomProperty('Connected')

            if suc:
                t = f'[{self.deviceName}] connected, retries: [{retry}]'
                self.log.debug(t)
                break
            else:
                t = f'[{self.deviceName}] connection retry: [{retry}]'
                self.log.info(t)
                sleepAndEvents(250)
        else:
            suc = False

        if not suc:
            self.msg.emit(2, 'ASCOM ', 'Connect error', f'{self.deviceName}')
            self.deviceConnected = False
            self.serverConnected = False
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f'{self.deviceName}')
            self.msg.emit(0, 'ASCOM ', 'Device found', f'{self.deviceName}')
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
        suc = self.getAscomProperty('Connected')

        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.signals.deviceDisconnected.emit(f'{self.deviceName}')
            self.msg.emit(0, 'ASCOM ', 'Device remove', f'{self.deviceName}')

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f'{self.deviceName}')
            self.msg.emit(0, 'ASCOM ', 'Device found', f'{self.deviceName}')

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
        t = f'ASCOM threaded: [{fn}], args:[{args}], kwargs:[{kwargs}]'
        self.log.trace(t)
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

    def startCommunication(self):
        """
        :return: True for test purpose
        """
        self.data.clear()
        if not self.deviceName:
            return False

        try:
            self.client = client.dynamic.Dispatch(self.deviceName)
            self.log.debug(f'[{self.deviceName}] Dispatching')

        except Exception as e:
            self.log.error(f'[{self.deviceName}] Dispatch error: [{e}]')
            return False

        else:
            worker = Worker(self.callerInitUnInit, self.workerConnectDevice)
            worker.signals.finished.connect(self.getInitialConfig)
            worker.signals.finished.connect(self.startTimer)
            self.threadPool.start(worker)

        return True

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        self.stopTimer()
        if self.client:
            self.setAscomProperty('Connected', False)
            self.deviceConnected = False
            self.serverConnected = False
            self.client = None
            self.propertyExceptions = []
        self.signals.deviceDisconnected.emit(f'{self.deviceName}')
        self.signals.serverDisconnected.emit({f'{self.deviceName}': 0})
        self.msg.emit(0, 'ALPACA', 'Device  remove', f'{self.deviceName}')
        return True
