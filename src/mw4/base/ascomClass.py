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

if platform.system() == "Windows":
    from pythoncom import CoInitialize, CoUninitialize
    from win32com import client
from mw4.base.driverDataClass import DriverData
from mw4.base.tpool import Worker
from PySide6.QtCore import QThreadPool


@dataclass
class CommandItem:
    cmdType: str
    name: str
    args: tuple = field(default_factory=tuple)
    value: Any = None


class AscomClass(DriverData):
    """ASCOM driver adapter.

    Wraps a win32com dispatch object and exposes a uniform
    startCommunication / stopCommunication / poll lifecycle that is
    compatible with AlpacaClass and NINAClass. All COM calls run
    inside a single worker loop that calls CoInitialize once at start
    and CoUninitialize in a finally block. GUI-thread callers enqueue
    commands via the Queued-suffix methods; the loop drains the queue
    on every iteration via processCommandQueue.
    """

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
        self.client: Any = None
        self.deviceName: str = ""
        self.deviceConnected: bool = False
        self.serverConnected: bool = False

        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
        }

        self.commandQueue: queue.Queue = queue.Queue()
        self.stopEvent: threading.Event = threading.Event()
        self.workerCommunicationLoop: Worker | None = None

    def getAscomProperty(self, valueProp: str) -> str | float | bool | None:
        try:
            value = getattr(self.client, valueProp)
        except Exception as e:
            self.log.debug(f"[{self.deviceName}] property [{valueProp}] not implemented: {e}")
            return None
        if valueProp != "ImageArray":
            self.log.trace(f"[{self.deviceName}] property [{valueProp}] has value: [{value}]")
        else:
            self.log.trace(f"[{self.deviceName}] property [{valueProp}]")
        return value

    def setAscomProperty(self, valueProp: str, value: Any) -> None:
        try:
            setattr(self.client, valueProp, value)
        except Exception as e:
            self.log.debug(f"[{self.deviceName}] property [{valueProp}] not implemented: {e}")
            return
        self.log.trace(f"[{self.deviceName}] property [{valueProp}] set to: [{value}]")

    def callAscomMethod(self, methodString: str, param: Any = ()) -> Any:
        args = param if isinstance(param, tuple) else (param,)
        try:
            result = getattr(self.client, methodString)(*args)
        except Exception as e:
            self.log.debug(f"[{self.deviceName}] method [{methodString}] not implemented: {e}")
            return None
        self.log.trace(f"[{self.deviceName}] method [{methodString}] called [{param}]")
        return result

    def getAndStoreAscomProperty(self, valueProp: str, element: str) -> None:
        value = self.getAscomProperty(valueProp)
        self.storePropertyToData(value, element)

    def setAscomPropertyQueued(self, valueProp: str, value: Any) -> None:
        self.commandQueue.put(CommandItem(cmdType="set", name=valueProp, value=value))

    def callAscomMethodQueued(self, methodString: str, param: Any = ()) -> None:
        args = param if isinstance(param, tuple) else (param,)
        self.commandQueue.put(CommandItem(cmdType="call", name=methodString, args=args))
        self.log.trace(f"[{self.deviceName}] method [{methodString}] queued")

    def processCommandQueue(self) -> None:
        while not self.commandQueue.empty():
            try:
                cmd = self.commandQueue.get_nowait()
            except queue.Empty:
                break
            if cmd.cmdType == "call":
                self.callAscomMethod(cmd.name, cmd.args)
            elif cmd.cmdType == "set":
                self.setAscomProperty(cmd.name, cmd.value)
            else:
                self.log.warning(f"[{self.deviceName}] unknown cmdType: [{cmd.cmdType}]")

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
        return bool(suc)

    def getInitialConfig(self) -> None:
        self.getAndStoreAscomProperty("Name", "DRIVER_INFO.DRIVER_NAME")
        self.getAndStoreAscomProperty("DriverVersion", "DRIVER_INFO.DRIVER_VERSION")
        self.getAndStoreAscomProperty("DriverInfo", "DRIVER_INFO.DRIVER_EXEC")

    def pollData(self) -> None:
        pass

    def handleDeviceConnect(self) -> None:
        suc = self.connectDevice()
        if not suc:
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
        CoInitialize()
        try:
            try:
                self.client = client.dynamic.Dispatch(self.deviceName)
                self.log.debug(f"[{self.deviceName}] Dispatching")
            except Exception as e:
                self.log.error(f"[{self.deviceName}] Dispatch error: [{e}]")
                return
            while not self.stopEvent.is_set():
                if not self.deviceConnected:
                    self.handleDeviceConnect()
                elif not self.getAscomProperty("Connected"):
                    self.handleDeviceDisconnect()
                else:
                    try:
                        self.pollData()
                    except Exception as e:
                        self.log.error(f"[{self.deviceName}] pollData error: [{e}]")
                    self.processCommandQueue()
                self.stopEvent.wait(timeout=self.updateRate / 1000)
        finally:
            if self.client:
                self.setAscomProperty("Connected", False)
                self.client = None
            CoUninitialize()

    def startCommunication(self) -> None:
        self.data.clear()
        if not self.deviceName:
            return
        self.stopEvent.clear()
        self.workerCommunicationLoop = Worker(self.runnerCommunicationLoop)
        self.threadPool.start(self.workerCommunicationLoop)

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
