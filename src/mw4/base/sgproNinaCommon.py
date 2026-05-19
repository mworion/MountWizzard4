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
import requests
from mw4.base.driverDataClass import DriverData, RemoteDeviceShutdown
from mw4.base.tpool import Worker
from PySide6.QtCore import QMutex, QThreadPool, QTimer
from typing import Any


class SgproNinaCommon(DriverData):
    TIMEOUT: int = 1
    HOST_ADDR: str = "localhost"
    PORT: int = 59590
    PROTOCOL: str = "http"
    BASE_URL: str = f"{PROTOCOL}://{HOST_ADDR}:{PORT}"
    DEVICE_TYPE: str = "Camera"
    UPDATE_RATE: int = 1000
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
        self.signalRS: RemoteDeviceShutdown = RemoteDeviceShutdown()
        self.deviceConnected: bool = False
        self.serverConnected: bool = False
        self.workerGetConfig: Worker | None = None
        self.workerStatus: Worker | None = None
        self.mutexPollStatus: QMutex = QMutex()
        self.cycleDevice: QTimer = QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.pollStatus)
        self.signalRS.signalRemoteShutdown.connect(self.stopCommunication)

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

    def isConnectedState(self, state: Any) -> bool:
        return state != "DISCONNECTED"

    def connectDevice(self) -> bool:
        devName = self.deviceName.replace(" ", "%20")
        prop = f"connectdevice/{self.DEVICE_TYPE}/{devName}"
        response = self.requestProperty(prop)
        return response.get("Success", False)

    def disconnectDevice(self) -> bool:
        prop = f"disconnectdevice/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Success", False)

    def enumerateDevice(self) -> list:
        prop = f"enumdevices/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Devices", [])

    def startTimer(self) -> None:
        self.cycleDevice.start(self.UPDATE_RATE)

    def stopTimer(self) -> None:
        self.cycleDevice.stop()

    def workerGetInitialConfig(self) -> None:
        pass

    def getInitialConfig(self) -> None:
        self.workerGetConfig = Worker(self.workerGetInitialConfig)
        self.threadPool.start(self.workerGetConfig)

    def workerPollStatus(self) -> None:
        prop = f"devicestatus/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        if not response:
            return

        self.storePropertyToData(response["State"], "Device.Status")
        self.storePropertyToData(response["Message"], "Device.Message")

        state = response.get("State")
        if not self.isConnectedState(state):
            if self.deviceConnected:
                self.deviceConnected = False
                self.signals.deviceDisconnected.emit(self.deviceName)
                self.msg.emit(0, self.PROTOCOL_NAME, "Device remove", self.deviceName)
        else:
            if not self.deviceConnected:
                self.deviceConnected = True
                self.getInitialConfig()
                self.signals.deviceConnected.emit(self.deviceName)
                self.msg.emit(0, self.PROTOCOL_NAME, "Device found", self.deviceName)

    def clearPollStatus(self) -> None:
        self.mutexPollStatus.unlock()

    def pollStatus(self) -> None:
        if not self.mutexPollStatus.tryLock():
            return

        self.workerStatus = Worker(self.workerPollStatus)
        self.workerStatus.signals.finished.connect(self.clearPollStatus)
        self.threadPool.start(self.workerStatus)

    def startCommunication(self) -> None:
        self.data.clear()
        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()
        self.startTimer()

    def stopCommunication(self) -> None:
        self.stopTimer()
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, self.PROTOCOL_NAME, "Device remove", f"{self.deviceName}")

    def discoverDevices(self, deviceType: str) -> list:
        discoverList = self.enumerateDevice()
        self.log.debug(f"[Type: {deviceType}: {discoverList}]")
        return discoverList
