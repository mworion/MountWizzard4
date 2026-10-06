# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import queue
import threading
from alpaca.exceptions import ActionNotImplementedException, NotImplementedException
from dataclasses import dataclass, field
from mw4.base.appProtocol import AppProtocol
from mw4.base.driverDataClass import DriverData
from PySide6.QtCore import QThreadPool
from typing import Any, ClassVar


@dataclass
class CommandItem:
    cmdType: str
    valueProp: str
    kwargs: dict = field(default_factory=dict)
    value: Any = None


class AlpacaAscomCommon(DriverData):
    PROTOCOL_NAME: str = ""
    UPDATE_RATE: float = 0.25
    # errors which mean the driver does not provide the property or method. only
    # these put an entry into propertyExceptions. communication errors (e.g.
    # OSError from a timeout) or invalid values / operations are retried.
    NOT_IMPLEMENTED_ERRORS: ClassVar[tuple[type[Exception], ...]] = (
        AttributeError,
        NotImplementedError,
        NotImplementedException,
        ActionNotImplementedException,
    )
    # scode of ASCOM (Property|Method)NotImplementedException in a COM error
    ASCOM_NOT_IMPLEMENTED: int = 0x80040400
    NEVER_BLOCKED: ClassVar[frozenset[str]] = frozenset({"Connected"})

    def __init__(self, parent: Any) -> None:
        super().__init__(parent.data)
        self.app: AppProtocol = parent.app
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.threadPool: QThreadPool = parent.app.threadPool
        self.propertyExceptions: set[str] = set()
        self.device: Any = None
        self.deviceConnected: bool = False
        self.commandQueue: queue.Queue = queue.Queue()
        self.stopEvent: threading.Event = threading.Event()
        self.connectEvent: threading.Event = threading.Event()
        self.loggingTrace: bool = False

    def isNotImplemented(self, e: Exception) -> bool:
        if isinstance(e, self.NOT_IMPLEMENTED_ERRORS):
            return True
        excepInfo = getattr(e, "excepinfo", None)
        if not excepInfo or len(excepInfo) < 6 or not isinstance(excepInfo[5], int):
            return False
        return excepInfo[5] & 0xFFFFFFFF == self.ASCOM_NOT_IMPLEMENTED

    def handleDeviceError(self, kind: str, valueProp: str, e: Exception) -> None:
        name = self.config.deviceName
        if self.isNotImplemented(e) and valueProp not in self.NEVER_BLOCKED:
            self.propertyExceptions.add(valueProp)
            self.log.debug(f"[{name}] {kind} [{valueProp}] not implemented: {e}")
            return
        self.log.debug(f"[{name}] {kind} [{valueProp}] error: [{type(e).__name__}] {e}")

    def getDeviceProp(self, valueProp: str) -> Any:
        if valueProp in self.propertyExceptions:
            return None
        try:
            returnVal = getattr(self.device, valueProp)
            if self.loggingTrace and "ImageArray" not in valueProp:
                self.log.debug(
                    f"[Trace][Get] [{self.config.deviceName}] [{valueProp}] [{returnVal}]"
                )
            return returnVal
        except Exception as e:
            self.handleDeviceError("property", valueProp, e)
            return None

    def setDeviceProp(self, valueProp: str, value: Any) -> None:
        if valueProp in self.propertyExceptions:
            return
        try:
            setattr(self.device, valueProp, value)
            if self.loggingTrace:
                self.log.debug(
                    f"[Trace][Set] [{self.config.deviceName}] [{valueProp}] [{value}]"
                )
        except Exception as e:
            self.handleDeviceError("property", valueProp, e)

    def callDeviceMethod(self, valueProp: str, **kwargs: Any) -> Any:
        if valueProp in self.propertyExceptions:
            return None
        try:
            returnVal = getattr(self.device, valueProp)(**kwargs)
            if self.loggingTrace:
                t = f"[Trace][Call] [{self.config.deviceName}] "
                t += f"[{valueProp}] [{kwargs}] [{returnVal}]"
                self.log.debug(t)
            return returnVal
        except Exception as e:
            self.handleDeviceError("method", valueProp, e)
            return None

    def setDevicePropQueued(self, valueProp: str, value: Any) -> None:
        self.commandQueue.put(CommandItem(cmdType="set", valueProp=valueProp, value=value))

    def callDeviceMethodQueued(self, valueProp: str, **kwargs: Any) -> None:
        self.commandQueue.put(CommandItem(cmdType="call", valueProp=valueProp, kwargs=kwargs))

    def getAndStoreDeviceProp(self, valueProp: str, element: str) -> None:
        value = self.getDeviceProp(valueProp)
        if value is None:
            return
        self.storePropertyToData(value, element)

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

    def connectDevice(self) -> bool:
        for retry in range(5):
            self.setDeviceProp("Connected", True)
            suc = self.getDeviceProp("Connected")
            if suc:
                self.log.debug(f"[{self.config.deviceName}] connected, [{retry}] retries")
                break
            self.connectEvent.wait(timeout=0.5)
        else:
            self.log.debug(f"[{self.config.deviceName}] not connected, [{retry}] retries")
            suc = False
        return suc

    def handleDeviceConnect(self) -> None:
        if not self.connectDevice():
            return
        self.deviceConnected = True
        self.signals.deviceConnected.emit(self.config.deviceName)
        self.getInitialConfig()

    def handleDeviceDisconnect(self) -> None:
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.config.deviceName)

    def clearCommandQueue(self) -> None:
        while True:
            try:
                self.commandQueue.get_nowait()
            except queue.Empty:
                break

    def runnerCommunicationLoop(self) -> None:
        # commands left over from a previous session (e.g. the disconnect queued
        # by stopCommunication while no loop was running) must not be replayed
        self.clearCommandQueue()
        while not self.stopEvent.is_set():
            if not self.deviceConnected:
                self.handleDeviceConnect()
            elif not self.getDeviceProp("Connected"):
                self.handleDeviceDisconnect()
            if self.deviceConnected:
                self.pollData()
                self.processCommandQueue()
            self.stopEvent.wait(timeout=self.UPDATE_RATE)
        # send the commands queued until the stop, including the disconnect
        self.processCommandQueue()

    def stopCommunication(self) -> None:
        # queue the disconnect before setting the stop event, so the loop always
        # finds it when it leaves
        self.setDevicePropQueued("Connected", False)
        self.stopEvent.set()
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.config.deviceName)
