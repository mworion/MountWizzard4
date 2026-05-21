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
from mw4.base.driverDataClass import DriverData
from mw4.base.tpool import Worker
from PySide6.QtCore import QThreadPool
from typing import Any


class SgproNinaCommon(DriverData):
    TIMEOUT: int = 1
    HOST_ADDR: str = "localhost"
    PORT: int = 59590
    PROTOCOL: str = "http"
    BASE_URL: str = f"{PROTOCOL}://{HOST_ADDR}:{PORT}"
    DEVICE_TYPE: str = "Camera"
    UPDATE_RATE: float = 0.5
    PROTOCOL_NAME: str = ""

    def __init__(self, parent: Any) -> None:
        super().__init__(parent.data)
        self.parent: Any = parent
        self.app: Any = parent.app
        self.data: dict = parent.data
        self.msg: Any = parent.app.msg
        self.signals: Any = parent.signals
        self.threadPool: QThreadPool = parent.app.threadPool
        self.loadConfig: bool = False
        self._deviceName: str = ""
        self.defaultConfig: dict[str, Any] = {
            "deviceList": [self.PROTOCOL_NAME],
            "deviceName": self.PROTOCOL_NAME,
        }
        self.deviceConnected: bool = False
        self.serverConnected: bool = False
        self.commandQueue: queue.Queue = queue.Queue()
        self.stopEvent: threading.Event = threading.Event()

    @property
    def deviceName(self) -> str:
        return self._deviceName

    @deviceName.setter
    def deviceName(self, value: str) -> None:
        self._deviceName = value

    def requestProperty(self, valueProp: str, params: dict | None = None) -> dict:
        try:
            if params:
                response = requests.post(
                    f"{self.BASE_URL}/{valueProp}?format=json",
                    json=params,
                    timeout=self.TIMEOUT,
                )
            else:
                response = requests.get(
                    f"{self.BASE_URL}/{valueProp}?format=json",
                    timeout=self.TIMEOUT,
                )
        except Exception as e:
            self.log.error(f"Request error: [{e}]")
            return {}

        if response.status_code != 200:
            t = f"Request response invalid: [{response.status_code}]"
            self.log.warning(t)
            return {}

        self.log.trace(f"Request response: [{response.json()}]")
        response = response.json()
        return response

    def requestPropertyQueued(self, valueProp: str, params: dict | None = None) -> None:
        self.commandQueue.put((valueProp, params))

    def connectDevice(self) -> bool:
        devName = self.deviceName.replace(" ", "%20")
        prop = f"connectdevice/{self.DEVICE_TYPE}/{devName}"
        response = self.requestProperty(prop)
        print(devName, self.deviceName, response)
        return response.get("Success", False)

    def disconnectDevice(self) -> bool:
        prop = f"disconnectdevice/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Success", False)

    def enumerateDevice(self) -> list:
        prop = f"enumdevices/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Devices", [])

    def getInitialConfig(self) -> None:
        pass

    def pollData(self) -> None:
        pass

    def isConnectedState(self, response: dict) -> bool:
        pass

    def isConnected(self) -> bool:
        prop = f"devicestatus/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        if not response:
            return False
        return self.isConnectedState(response)

    def processCommandQueue(self) -> None:
        while not self.commandQueue.empty():
            try:
                valueProp, params = self.commandQueue.get_nowait()
            except queue.Empty:
                break
            self.requestProperty(valueProp, params)

    def handleDeviceConnect(self) -> None:
        if not self.connectDevice():
            return
        self.serverConnected = True
        self.deviceConnected = True
        self.signals.serverConnected.emit()
        self.signals.deviceConnected.emit(self.deviceName)
        self.msg.emit(0, self.PROTOCOL_NAME, "Device found", self.deviceName)
        self.getInitialConfig()

    def handleDeviceDisconnect(self) -> None:
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit(self.deviceName)
        self.msg.emit(0, self.PROTOCOL_NAME, "Device remove", self.deviceName)

    def runnerCommunicationLoop(self) -> None:
        while not self.stopEvent.is_set():
            if not self.deviceConnected:
                self.handleDeviceConnect()
            if not self.isConnected():
                self.handleDeviceDisconnect()
            else:
                self.pollData()
                self.processCommandQueue()
            self.stopEvent.wait(timeout=self.UPDATE_RATE)

    def startCommunication(self) -> None:
        self.data.clear()
        self.stopEvent.clear()
        self.discoverDevices(self.DEVICE_TYPE)
        workerCommunicationLoop = Worker(self.runnerCommunicationLoop)
        self.threadPool.start(workerCommunicationLoop)

    def stopCommunication(self) -> None:
        self.stopEvent.set()
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(self.deviceName)
        self.signals.serverDisconnected.emit(self.deviceName)
        self.msg.emit(0, self.PROTOCOL_NAME, "Device remove", self.deviceName)

    def discoverDevices(self, deviceType: str) -> list:
        discoverList = self.enumerateDevice()
        self.log.debug(f"[Type: {deviceType}: {discoverList}]")
        return discoverList
