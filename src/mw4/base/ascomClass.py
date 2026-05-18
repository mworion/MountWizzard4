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
# License APL2.0
#
###########################################################
import platform
import queue
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Any
from mw4.base.driverDataClass import DriverData
from mw4.base.tpool import Worker
from PySide6.QtCore import QThreadPool
if platform.system() == "Windows":
    from pythoncom import CoInitialize, CoUninitialize
    from win32com import client


@dataclass
class CommandItem:
    cmdType: str
    valueProp: str
    kwargs: dict = field(default_factory=dict)
    value: Any = None


class AscomClass(DriverData):
    UPDATE_RATE: float = 0.5
    def __init__(self, parent: Any) -> None:
        super().__init__(parent.data)
        self.app: Any = parent.app
        self.msg: Any = parent.app.msg
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.threadPool: QThreadPool = parent.app.threadPool
        self.loadConfig: bool = False
        self.propertyExceptions: list[str] = []
        self.device: Any = None
        self.deviceName: str = ""
        self.deviceType: str = parent.deviceType
        self.deviceConnected: bool = False
        self.serverConnected: bool = False
        self.commandQueue: queue.Queue = queue.Queue()
        self.stopEvent: threading.Event = threading.Event()
        self.workerRunnerCoreLoop: Worker | None = None

        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
        }

    def getAscomProperty(self, valueProp: str) -> Any:
        if valueProp in self.propertyExceptions:
            return
        try:
            return getattr(self.device, valueProp)
        except Exception as e:
            self.log.debug(f"[{self.deviceName}] property [{valueProp}] not implemented: {e}")
            self.propertyExceptions.append(valueProp)

    def setAscomProperty(self, valueProp: str, value: Any) -> None:
        if valueProp in self.propertyExceptions:
            return
        try:
            setattr(self.device, valueProp, value)
        except Exception as e:
            self.log.debug(f"[{self.deviceName}] property [{valueProp}] not implemented: {e}")
            self.propertyExceptions.append(valueProp)

    def callAscomMethod(self, valueProp: str, **kwargs: Any) -> Any:
        if valueProp in self.propertyExceptions:
            return
        try:
            return getattr(self.device, valueProp)(**kwargs)
        except Exception as e:
            self.log.debug(f"[{self.deviceName}] method [{valueProp}] not implemented: {e}")
            self.propertyExceptions.append(valueProp)

    def setAscomPropertyQueued(self, valueProp: str, value: Any) -> None:
        self.commandQueue.put(CommandItem(cmdType="set", valueProp=valueProp, value=value))

    def callAscomMethodQueued(self, valueProp: str, **kwargs: Any) -> None:
        self.commandQueue.put(CommandItem(cmdType="call", valueProp=valueProp, kwargs=kwargs))

    def getAndStoreAscomProperty(self, valueProp: str, element: str) -> None:
        value = self.getAscomProperty(valueProp)
        self.storePropertyToData(value, element)

    def connectDevice(self) -> bool:
        self.deviceConnected = False
        self.serverConnected = False
        for retry in range(0, 10):
            self.setAscomProperty("Connected", True)
            suc = self.getAscomProperty("Connected")
            if suc:
                self.log.debug(f"[{self.deviceName}] connected, retries: [{retry}]")
                break
            self.log.info(f"[{self.deviceName}] connection retry: [{retry}]")
            time.sleep(0.2)
        else:
            suc = False
        if not suc:
            self.msg.emit(2, "ASCOM ", "Connect error", f"{self.deviceName}")
        return suc

    def getInitialConfig(self) -> None:
        self.getAndStoreAscomProperty("Name", "DRIVER_INFO.DRIVER_NAME")
        self.getAndStoreAscomProperty("DriverVersion", "DRIVER_INFO.DRIVER_VERSION")
        self.getAndStoreAscomProperty("DriverInfo", "DRIVER_INFO.DRIVER_EXEC")

    def pollData(self) -> None:
        pass

    def processCommandQueue(self) -> None:
        while not self.commandQueue.empty():
            try:
                cmd = self.commandQueue.get_nowait()
            except queue.Empty:
                break
            if cmd.cmdType == "call":
                self.callAscomMethod(cmd.valueProp, **cmd.kwargs)
            elif cmd.cmdType == "set":
                self.setAscomProperty(cmd.valueProp, cmd.value)
            else:
                self.log.warning(f"[{self.deviceName}] unknown cmdType: [{cmd.cmdType}]")

    def handleDeviceConnect(self) -> None:
        if not self.connectDevice():
            return
        self.serverConnected = True
        self.deviceConnected = True
        self.signals.serverConnected.emit()
        self.signals.deviceConnected.emit(f"{self.deviceName}")
        self.msg.emit(0, "ASCOM ", "Device found", f"{self.deviceName}")
        self.getInitialConfig()

    def handleDeviceDisconnect(self) -> None:
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.msg.emit(0, "ASCOM ", "Device remove", f"{self.deviceName}")

    def runnerCommunicationLoop(self) -> None:
        while not self.stopEvent.is_set():
            if not self.deviceConnected:
                self.handleDeviceConnect()
            if not self.getAscomProperty("Connected"):
                self.handleDeviceDisconnect()
            else:
                self.pollData()
                self.processCommandQueue()
            self.stopEvent.wait(timeout=self.UPDATE_RATE)

    def runnerCoreLoop(self) -> None:
        CoInitialize()
        try:
            self.device = client.dynamic.Dispatch(self.deviceName)
            self.log.debug(f"[{self.deviceName}] Dispatching")
        except Exception as e:
            self.log.error(f"[{self.deviceName}] Dispatch error: [{e}]")
            return
        else:
            self.runnerCoreLoop()
        finally:
            if self.device:
                self.setAscomProperty("Connected", False)
                self.device = None
            CoUninitialize()

    def startCommunication(self) -> None:
        self.data.clear()
        self.propertyExceptions.clear()
        if not self.deviceName:
            return
        self.stopEvent.clear()
        self.workerRunnerCoreLoop = Worker(self.runnerCoreLoop)
        self.threadPool.start(self.workerRunnerCoreLoop)

    def stopCommunication(self) -> None:
        self.stopEvent.set()
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, "ASCOM", "Device  remove", f"{self.deviceName}")

    def selectAscomDriver(self, deviceName: str) -> str:
        script = (
            "import sys; import win32com.client; "
            f"chooser = win32com.client.Dispatch('ASCOM.Utilities.Chooser'); "
            f"chooser.DeviceType = '{self.deviceType}'; "
            f"result = chooser.Choose('{deviceName}'); "
            "print(result if result else '', end='')"
        )
        try:
            result = subprocess.check_output(
                [sys.executable, "-c", script],
                text=True,
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            ).strip()
        except subprocess.CalledProcessError as e:
            self.log.critical(f"ASCOM Chooser subprocess error: {e}")
            return deviceName

        return result if result else deviceName
