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
        self.msg: Any = parent.app.msg
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.threadPool: QThreadPool = parent.app.threadPool
        self.loadConfig: bool = False
        self.propertyExceptions: list[str] = []
        self.device: Any = None
        self.deviceName: str = ""
        self.deviceConnected: bool = False
        self.serverConnected: bool = False
        self.commandQueue: queue.Queue = queue.Queue()
        self.stopEvent: threading.Event = threading.Event()

    def getDeviceProp(self, valueProp: str) -> Any:
        raise NotImplementedError

    def setDeviceProp(self, valueProp: str, value: Any) -> None:
        raise NotImplementedError

    def callDeviceMethod(self, valueProp: str, **kwargs: Any) -> Any:
        raise NotImplementedError

    def setDevicePropQueued(self, valueProp: str, value: Any) -> None:
        self.commandQueue.put(
            CommandItem(cmdType="set", valueProp=valueProp, value=value)
        )

    def callDeviceMethodQueued(self, valueProp: str, **kwargs: Any) -> None:
        self.commandQueue.put(
            CommandItem(cmdType="call", valueProp=valueProp, kwargs=kwargs)
        )

    def getAndStoreDeviceProp(self, valueProp: str, element: str) -> None:
        value = self.getDeviceProp(valueProp)
        # print(valueProp, value)
        self.storePropertyToData(value, element)

    def connectDevice(self) -> bool:
        for retry in range(0, 10):
            self.setDeviceProp("Connected", True)
            suc = self.getDeviceProp("Connected")
            if suc:
                self.log.debug(
                    f"[{self.deviceName}] connected, [{retry}] retries"
                )
                break
            self.log.info(
                f"[{self.deviceName}] connection retry: [{retry}]"
            )
            time.sleep(0.2)
        else:
            suc = False
        if not suc:
            self.msg.emit(
                2, self.PROTOCOL_NAME, "Connect error", self.deviceName
            )
        return suc

    def getInitialConfig(self) -> None:
        self.getAndStoreDeviceProp("Name", "DRIVER_INFO.DRIVER_NAME")
        self.getAndStoreDeviceProp(
            "DriverVersion", "DRIVER_INFO.DRIVER_VERSION"
        )
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
                    f"[{self.deviceName}] unknown cmdType: [{cmd.cmdType}]"
                )

    def handleDeviceConnect(self) -> None:
        if not self.connectDevice():
            return
        self.serverConnected = True
        self.deviceConnected = True
        self.signals.serverConnected.emit()
        self.signals.deviceConnected.emit(self.deviceName)
        self.msg.emit(
            0, self.PROTOCOL_NAME, "Device found", self.deviceName
        )
        self.getInitialConfig()

    def handleDeviceDisconnect(self) -> None:
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(self.deviceName)
        self.msg.emit(
            0, self.PROTOCOL_NAME, "Device remove", self.deviceName
        )

    def runnerCommunicationLoop(self) -> None:
        while not self.stopEvent.is_set():
            if not self.deviceConnected:
                self.handleDeviceConnect()
            if not self.getDeviceProp("Connected"):
                self.handleDeviceDisconnect()
            else:
                self.pollData()
                self.processCommandQueue()
            self.stopEvent.wait(timeout=self.UPDATE_RATE)

    def stopCommunication(self) -> None:
        self.stopEvent.set()
        self.setDevicePropQueued("Connected", False)
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(self.deviceName)
        self.signals.serverDisconnected.emit({self.deviceName: 0})
        self.msg.emit(
            0, self.PROTOCOL_NAME, "Device  remove", self.deviceName
        )

