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
import queue
import threading
import time
from dataclasses import dataclass, field
from mw4.base.driverDataClass import DriverData
from PySide6.QtCore import QThreadPool
from typing import Any


@dataclass
class CommandItem:
    cmdType: str
    valueProp: str
    kwargs: dict = field(default_factory=dict)
    value: Any = None


class AlpacaAscomCommon(DriverData):
    PROTOCOL_NAME: str = ""
    UPDATE_RATE: float = 0.25

    def __init__(self, parent: Any) -> None:
        super().__init__(parent.data)
        self.app: Any = parent.app
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.threadPool: QThreadPool = parent.app.threadPool
        self.propertyExceptions: list[str] = []
        self.device: Any = None
        self.deviceConnected: bool = False
        self.commandQueue: queue.Queue = queue.Queue()
        self.stopEvent: threading.Event = threading.Event()
        self.loggingTrace: bool = False

    def getDeviceProp(self, valueProp: str) -> Any:
        if valueProp in self.propertyExceptions:
            return None
        try:
            returnVal = getattr(self.device, valueProp)
            if self.loggingTrace:
                self.log.debug(
                    f"[Trace] [{self.config.deviceName}] [{valueProp}] [{returnVal}]"
                )
            return returnVal
        except Exception as e:
            self.log.debug(
                f"[{self.config.deviceName}] property [{valueProp}] not implemented: {e}"
            )
            self.propertyExceptions.append(valueProp)

    def setDeviceProp(self, valueProp: str, value: Any) -> None:
        if valueProp in self.propertyExceptions:
            return
        try:
            setattr(self.device, valueProp, value)
            if self.loggingTrace:
                self.log.debug(f"[Trace] [{self.config.deviceName}] [{valueProp}] [{value}]")
        except Exception as e:
            self.log.debug(
                f"[{self.config.deviceName}] property [{valueProp}] not implemented: {e}"
            )
            self.propertyExceptions.append(valueProp)

    def callDeviceMethod(self, valueProp: str, **kwargs: Any) -> Any:
        if valueProp in self.propertyExceptions:
            return None
        try:
            returnVal = getattr(self.device, valueProp)(**kwargs)
            if self.loggingTrace:
                t = f"[Trace] [{self.config.deviceName}] "
                t += f"[{valueProp}] [{kwargs}] [{returnVal}]"
                self.log.debug(t)
            return returnVal
        except Exception as e:
            self.log.debug(
                f"[{self.config.deviceName}] method [{valueProp}] not implemented: {e}"
            )
            self.propertyExceptions.append(valueProp)

    def setDevicePropQueued(self, valueProp: str, value: Any) -> None:
        self.commandQueue.put(CommandItem(cmdType="set", valueProp=valueProp, value=value))

    def callDeviceMethodQueued(self, valueProp: str, **kwargs: Any) -> None:
        self.commandQueue.put(CommandItem(cmdType="call", valueProp=valueProp, kwargs=kwargs))

    def getAndStoreDeviceProp(self, valueProp: str, element: str) -> None:
        value = self.getDeviceProp(valueProp)
        self.storePropertyToData(value, element)

    def connectDevice(self) -> bool:
        for retry in range(25):
            self.setDeviceProp("Connected", True)
            suc = self.getDeviceProp("Connected")
            if suc:
                self.log.debug(f"[{self.config.deviceName}] connected, [{retry}] retries")
                break
            time.sleep(0.2)
        else:
            self.log.debug(f"[{self.config.deviceName}] not connected, [{retry}] retries")
            suc = False
        return suc

    def getInitialConfig(self) -> None:
        self.getAndStoreDeviceProp("Name", "DRIVER_INFO.DRIVER_NAME")
        self.getAndStoreDeviceProp("DriverVersion", "DRIVER_INFO.DRIVER_VERSION")
        self.getAndStoreDeviceProp("DriverInfo", "DRIVER_INFO.DRIVER_EXEC")

    def pollData(self) -> None:
        pass

    def processCommandQueue(self) -> None:
        while not self.commandQueue.empty():
            try:
                cmd = self.commandQueue.get_nowait()
            except queue.Empty:
                break
            if cmd.cmdType == "call":
                self.callDeviceMethod(cmd.valueProp, **cmd.kwargs)
            elif cmd.cmdType == "set":
                self.setDeviceProp(cmd.valueProp, cmd.value)
            else:
                self.log.warning(
                    f"[{self.config.deviceName}] unknown cmdType: [{cmd.cmdType}]"
                )

    def handleDeviceConnect(self) -> None:
        if not self.connectDevice():
            return
        self.deviceConnected = True
        self.signals.deviceConnected.emit(self.config.deviceName)
        self.getInitialConfig()

    def handleDeviceDisconnect(self) -> None:
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.config.deviceName)

    def runnerCommunicationLoop(self) -> None:
        while not self.stopEvent.is_set():
            if not self.deviceConnected:
                self.handleDeviceConnect()
            elif not self.getDeviceProp("Connected"):
                self.handleDeviceDisconnect()
            else:
                self.pollData()
                self.processCommandQueue()
            self.stopEvent.wait(timeout=self.UPDATE_RATE)

    def stopCommunication(self) -> None:
        self.stopEvent.set()
        self.setDevicePropQueued("Connected", False)
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.config.deviceName)
