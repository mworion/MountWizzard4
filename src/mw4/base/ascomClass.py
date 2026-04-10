############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import platform
import time
from typing import Any, Callable

if platform.system() == "Windows":
    from pythoncom import CoInitialize, CoUninitialize
    from win32com import client
from mw4.base.driverDataClass import DriverData
from mw4.base.tpool import Worker
from PySide6.QtCore import QMutex, QThreadPool, QTimer


class AscomClass(DriverData):
    """ """

    def __init__(self, parent: Any) -> None:
        super().__init__(parent.data)
        self.parent: Any = parent
        self.app: Any = parent.app
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.msg: Any = parent.app.msg
        self.deviceType: str = parent.deviceType
        self.threadPool: QThreadPool = parent.app.threadPool
        self.updateRate: int = 3000
        self.loadConfig: bool = False
        self.tM: QMutex = QMutex()
        self.worker: Worker | None = None
        self.workerData: Worker | None = None
        self.workerGetConfig: Worker | None = None
        self.workerStatus: Worker | None = None
        self.workerConnect: Worker | None = None
        self.client: Any = None
        self.propertyExceptions: list[str] = []
        self.deviceName: str = ""
        self.deviceConnected: bool = False
        self.serverConnected: bool = False

        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
        }

        self.cyclePollStatus: QTimer = QTimer()
        self.cyclePollStatus.setSingleShot(False)
        self.cyclePollStatus.timeout.connect(self.pollStatus)

        self.cyclePollData: QTimer = QTimer()
        self.cyclePollData.setSingleShot(False)
        self.cyclePollData.timeout.connect(self.pollData)

    def startAscomTimer(self) -> None:
        self.cyclePollData.start(self.updateRate)
        self.cyclePollStatus.start(self.updateRate)

    def stopAscomTimer(self) -> None:
        self.cyclePollData.stop()
        self.cyclePollStatus.stop()

    def getAscomProperty(self, valueProp: str) -> str | float | bool | None:
        value = None
        if valueProp in self.propertyExceptions:
            return value

        cmd = "self.client." + valueProp
        try:
            value = eval(cmd)
        except Exception as e:
            t = f"[{self.deviceName}] [{cmd}], property [{valueProp}] not implemented: {e}"
            self.log.debug(t)
            self.propertyExceptions.append(valueProp)
        else:
            if valueProp != "ImageArray":
                t = f"[{self.deviceName}] property [{valueProp}] has value: [{value}]"
                self.log.trace(t)
            else:
                self.log.trace(f"{self.deviceName}] property [{valueProp}]")
        return value

    def setAscomProperty(self, valueProp: str, value: str | float) -> None:
        if valueProp in self.propertyExceptions:
            return

        cmd = "self.client." + valueProp + " = value"
        try:
            exec(cmd)
        except Exception as e:
            t = f"[{self.deviceName}] [{cmd}], property [{valueProp}] not implemented: {e}"
            self.log.debug(t)
            if valueProp != "Connected":
                self.propertyExceptions.append(valueProp)
            return
        t = f"[{self.deviceName}] property [{valueProp}] set to: [{value}]"
        self.log.trace(t)

    def callAscomMethod(self, methodString: str, param: Any) -> None:
        if methodString in self.propertyExceptions:
            return

        paramStr = f"{param}".rstrip(")").lstrip("(")
        cmd = "self.client." + methodString + f"({paramStr})"
        try:
            exec(cmd)
        except Exception as e:
            t = f"[{self.deviceName}] [{cmd}], method [{methodString}] not implemented: {e}"
            self.log.debug(t)
            self.propertyExceptions.append(methodString)
            return

        t = f"[{self.deviceName}] method [{methodString}] called [{param}]"
        self.log.trace(t)

    def getAndStoreAscomProperty(self, valueProp: str, element: str) -> None:
        value = self.getAscomProperty(valueProp)
        self.storePropertyToData(value, element)

    def workerConnectDevice(self) -> None:
        self.propertyExceptions = []
        self.deviceConnected = False
        self.serverConnected = False
        for retry in range(0, 10):
            self.setAscomProperty("Connected", True)
            suc = self.getAscomProperty("Connected")

            if suc:
                t = f"[{self.deviceName}] connected, retries: [{retry}]"
                self.log.debug(t)
                break
            else:
                t = f"[{self.deviceName}] connection retry: [{retry}]"
                self.log.info(t)
                time.sleep(0.2)
        else:
            suc = False

        if not suc:
            self.msg.emit(2, "ASCOM ", "Connect error", f"{self.deviceName}")
            return

        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ASCOM ", "Device found", f"{self.deviceName}")
            self.startAscomTimer()
            self.getInitialConfig()

    def workerGetInitialConfig(self) -> None:
        self.getAndStoreAscomProperty("Name", "DRIVER_INFO.DRIVER_NAME")
        self.getAndStoreAscomProperty("DriverVersion", "DRIVER_INFO.DRIVER_VERSION")
        self.getAndStoreAscomProperty("DriverInfo", "DRIVER_INFO.DRIVER_EXEC")

    def workerPollStatus(self) -> None:
        suc = self.getAscomProperty("Connected")

        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.signals.deviceDisconnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ASCOM ", "Device remove", f"{self.deviceName}")

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ASCOM ", "Device found", f"{self.deviceName}")

    @staticmethod
    def callerInitUnInit(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        CoInitialize()
        fn(*args, **kwargs)
        CoUninitialize()

    def callMethodThreaded(self, fn: Callable[..., Any], *args: Any, cb_res: Callable | None = None, cb_fin: Callable | None = None, **kwargs: Any) -> None:
        """
        callMethodThreaded is done mainly for ASCOM ctypes interfaces which take
        longer to end and should not slow down the gui thread itself. All called
        functions run in PySide6 threadPool and could have callback after result is
        processed or the thread task is finished. It does not call directly the
        defined function, but the callerInitUnInit method, which does the necessary
        pythoncom.Initialize() before running win32 functions in another thread
        than the dispatch was done (in our case the main gui thread) and call
        pythoncom.CoUninitialize() after the functions finished.

        :param fn: function
        :param args:
        :param cb_res: callback result
        :param cb_fin: callback finished
        :param kwargs:
        :return:
        """
        if not self.deviceConnected:
            return

        self.worker = Worker(self.callerInitUnInit, fn, *args, **kwargs)
        t = f"ASCOM threaded: [{fn}], args:[{args}], kwargs:[{kwargs}]"
        self.log.trace(t)
        if cb_res:
            self.worker.signals.result.connect(cb_res)
        if cb_fin:
            self.worker.signals.finished.connect(cb_fin)
        self.threadPool.start(self.worker)

    def processPolledData(self) -> None:
        pass

    def workerPollData(self) -> None:
        pass

    def pollData(self) -> None:
        self.workerData = Worker(self.workerPollData)
        self.workerData.signals.result.connect(self.processPolledData)
        self.threadPool.start(self.workerData)

    def pollStatus(self) -> None:
        self.workerStatus = Worker(self.workerPollStatus)
        self.threadPool.start(self.workerStatus)

    def getInitialConfig(self) -> None:
        self.workerGetConfig = Worker(self.workerGetInitialConfig)
        self.threadPool.start(self.workerGetConfig)

    def startCommunication(self) -> None:
        self.data.clear()
        if not self.deviceName:
            return

        try:
            self.client = client.dynamic.Dispatch(self.deviceName)
            self.log.debug(f"[{self.deviceName}] Dispatching")

        except Exception as e:
            self.log.error(f"[{self.deviceName}] Dispatch error: [{e}]")
            return

        self.workerConnect = Worker(self.callerInitUnInit, self.workerConnectDevice)
        self.threadPool.start(self.workerConnect)

    def stopCommunication(self) -> None:
        self.stopAscomTimer()
        if self.client:
            self.setAscomProperty("Connected", False)
            self.deviceConnected = False
            self.serverConnected = False
            self.client = None
            self.propertyExceptions = []
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, "ALPACA", "Device  remove", f"{self.deviceName}")

    def selectAscomDriver(self, deviceName: str) -> str:
        try:
            chooser = client.Dispatch("ASCOM.Utilities.Chooser")
            chooser.DeviceType = self.deviceType
            deviceName = chooser.Choose(deviceName)

        except Exception as e:
            self.log.critical(f"Error: {e}")
            deviceName = ""

        return deviceName
