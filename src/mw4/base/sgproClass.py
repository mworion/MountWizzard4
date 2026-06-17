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
import requests
import threading
import time
from dataclasses import dataclass, field
from mw4.base.driverDataClass import DriverData
from mw4.base.tpool import Worker
from PySide6.QtCore import QThreadPool
from typing import Any


@dataclass
class CommandItem:
    cmdType: str
    valueProp: str
    kwargs: dict = field(default_factory=dict)
    value: Any = None


@dataclass
class DeviceConfigSGPro:
    deviceName: str = field(default="")
    hostAddress: str = field(default="127.0.0.1")
    port: int = field(default=59590)
    UPDATE_RATE: float = 0.25
    PROTOCOL_NAME: str = "SGPro"


class SGProClass(DriverData):
    SGPRO_TIMEOUT: int = 3
    DEVICE_TYPE: str = "Camera"

    def __init__(self, parent: Any) -> None:
        super().__init__(parent.data)
        self.app: Any = parent.app
        self.data: dict = parent.data
        self.msg: Any = parent.app.msg
        self.signals: Any = parent.signals
        self.threadPool: QThreadPool = parent.app.threadPool
        self.deviceConnected: bool = False
        self.commandQueue: queue.Queue = queue.Queue()
        self.stopEvent: threading.Event = threading.Event()
        self.loggingTrace: bool = False
        self.config = DeviceConfigSGPro()
        self.workerCommunicationLoop: Worker | None = None

    def requestProperty(self, valueProp: str, params: dict | None = None) -> dict:
        try:
            url = f"http://{self.config.hostAddress}:{self.config.port}"
            if params:
                response = requests.post(
                    f"{url}/{valueProp}?format=json",
                    json=params,
                    timeout=self.SGPRO_TIMEOUT,
                )
            else:
                response = requests.get(
                    f"{url}/{valueProp}?format=json",
                    timeout=self.SGPRO_TIMEOUT,
                )
        except Exception as e:
            self.log.debug(
                f"[{self.config.deviceName}] method [{valueProp}] not implemented: {e}"
            )
            return {}

        if response.status_code != 200:
            t = f"Response invalid: [{response.status_code}]"
            self.log.warning(t)
            return {}

        self.log.debug(f"[Trace] Response: [{response.json()}]")
        response = response.json()
        return response

    def sgConnectDevice(self) -> bool:
        devName = self.config.deviceName.replace(" ", "%20")
        prop = f"connectdevice/{self.DEVICE_TYPE}/{devName}"
        response = self.requestProperty(prop)
        return response.get("Success", False)

    def sgEnumerateDevice(self) -> list:
        prop = f"enumdevices/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Devices", [])

    def workerPollStatus(self) -> None:
        prop = f"devicestatus/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)

        if response is None:
            return

        self.storePropertyToData(response["State"], "Device.Status")
        self.storePropertyToData(response["Message"], "Device.Message")

        if response.get("State", "") == "DISCONNECTED":
            if self.deviceConnected:
                self.deviceConnected = False
                self.signals.deviceDisconnected.emit(f"{self.config.deviceName}")
                self.msg.emit(0, "SGPRO", "Device remove", f"{self.config.deviceName}")

        else:
            if not self.deviceConnected:
                self.deviceConnected = True
                self.getInitialConfig()
                self.signals.deviceConnected.emit(f"{self.config.deviceName}")
                self.msg.emit(0, "SGPRO", "Device found", f"{self.config.deviceName}")

    def callDeviceMethodQueued(self, valueProp: str, **kwargs: Any) -> None:
        self.commandQueue.put(CommandItem(cmdType="call", valueProp=valueProp, kwargs=kwargs))

    def connectDevice(self) -> bool:
        for retry in range(25):
            suc = self.sgConnectDevice()
            if suc:
                self.log.debug(f"[{self.config.deviceName}] connected, [{retry}] retries")
                break
            time.sleep(0.2)
        else:
            self.log.debug(f"[{self.config.deviceName}] not connected, [{retry}] retries")
            suc = False
        if not suc:
            self.msg.emit(
                2, self.config.PROTOCOL_NAME, "Connect error", self.config.deviceName
            )
        return suc

    def getInitialConfig(self) -> None:
        pass

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
            else:
                self.log.warning(
                    f"[{self.config.deviceName}] unknown cmdType: [{cmd.cmdType}]"
                )

    def handleDeviceConnect(self) -> None:
        if not self.connectDevice():
            return
        self.deviceConnected = True
        self.signals.deviceConnected.emit(self.config.deviceName)
        self.msg.emit(0, self.PROTOCOL_NAME, "Device found", self.config.deviceName)
        self.getInitialConfig()

    def handleDeviceDisconnect(self) -> None:
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.config.deviceName)
        self.msg.emit(0, self.PROTOCOL_NAME, "Device remove", self.config.deviceName)

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

    def startCommunication(self) -> None:
        self.data.clear()
        self.deviceConnected = False
        self.stopEvent.clear()
        self.workerCommunicationLoop = Worker(self.runnerCommunicationLoop)
        self.threadPool.start(self.workerCommunicationLoop)

    def stopCommunication(self) -> None:
        self.stopEvent.set()
        self.deviceConnected = False
        self.msg.emit(0, self.PROTOCOL_NAME, "Device remove", f"{self.config.deviceName}")

    def discoverDevices(self, deviceType: str) -> list:
        discoverList = self.sgEnumerateDevice()
        self.log.debug(f"[Type: {deviceType}: {discoverList}]")
        return discoverList
