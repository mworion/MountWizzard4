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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import json

# external packages
from PySide6.QtCore import QTimer, QMutex
import requests

# local imports
from base.driverDataClass import DriverData
from base.driverDataClass import RemoteDeviceShutdown
from base.tpool import Worker


class NINAClass(DriverData):
    """ """

    NINA_TIMEOUT = 3
    HOST_ADDR = "localhost"
    PORT = 59590
    PROTOCOL = "http"
    BASE_URL = f"{PROTOCOL}://{HOST_ADDR}:{PORT}"
    DEVICE_TYPE = "Camera"

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.app = parent.app
        self.data = parent.data
        self.msg = parent.app.msg
        self.signals = parent.signals
        self.threadPool = parent.app.threadPool
        self.updateRate = 1000
        self.loadConfig = False
        self._deviceName = ""
        self.defaultConfig = {
            "deviceList": ["N.I.N.A."],
            "deviceName": "N.I.N.A.",
        }
        self.signalRS = RemoteDeviceShutdown()

        self.deviceConnected = False
        self.serverConnected = False
        self.workerData: Worker = None
        self.workerGetConfig: Worker = None
        self.workerStatus: Worker = None
        self.mutexPollStatus = QMutex()

        self.cycleDevice = QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.pollStatus)

        self.cycleData = QTimer()
        self.cycleData.setSingleShot(False)
        self.cycleData.timeout.connect(self.pollData)
        self.signalRS.signalRemoteShutdown.connect(self.stopCommunication)

    @property
    def deviceName(self):
        return self._deviceName

    @deviceName.setter
    def deviceName(self, value):
        self._deviceName = value

    def requestProperty(self, valueProp: str, params: dict = None) -> dict:
        """ """
        try:
            t = f"N.I.N.A.: [{self.BASE_URL}/{valueProp}?format=json]"
            if params:
                t += f" data: [{bytes(json.dumps(params).encode('utf-8'))}]"
                self.log.trace("POST " + t)
                response = requests.post(
                    f"{self.BASE_URL}/{valueProp}?format=json",
                    json=params,
                    timeout=self.NINA_TIMEOUT,
                )
            else:
                self.log.trace("GET " + t)
                response = requests.get(
                    f"{self.BASE_URL}/{valueProp}?format=json",
                    timeout=self.NINA_TIMEOUT,
                )
        except Exception as e:
            self.log.error(f"Request N.I.N.A. error: [{e}]")
            return {}

        if response.status_code != 200:
            t = f"Request N.I.N.A. response invalid: [{response.status_code}]"
            self.log.warning(t)
            return {}

        self.log.trace(f"Request N.I.N.A. response: [{response.json()}]")
        response = response.json()
        return response

    def connectDevice(self) -> bool:
        """ """
        devName = self.deviceName.replace(" ", "%20")
        prop = f"connectdevice/{self.DEVICE_TYPE}/{devName}"
        response = self.requestProperty(prop)
        return response.get("Success", False)

    def disconnectDevice(self) -> bool:
        """ """
        prop = f"disconnectdevice/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Success", False)

    def enumerateDevice(self) -> list:
        """ """
        prop = f"enumdevices/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Devices", [])

    def startNINATimer(self) -> None:
        """ """
        self.cycleData.start(self.updateRate)
        self.cycleDevice.start(self.updateRate)

    def stopNINATimer(self) -> None:
        """ """
        self.cycleData.stop()
        self.cycleDevice.stop()

    def processPolledData(self) -> None:
        """ """
        pass

    def workerPollData(self) -> None:
        """ """
        pass

    def pollData(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.workerData = Worker(self.workerPollData)
        self.workerData.signals.result.connect(self.processPolledData)
        self.threadPool.start(self.workerData)

    def workerGetInitialConfig(self) -> None:
        """"""
        pass

    def getInitialConfig(self) -> None:
        """ """
        self.workerGetConfig = Worker(self.workerGetInitialConfig)
        self.threadPool.start(self.workerGetConfig)

    def workerPollStatus(self):
        """
        :return: success
        """
        prop = f"devicestatus/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)

        if not response:
            return

        state = response.get("State", -1)
        self.storePropertyToData(state, "Device.Status")
        if state == 3:
            self.storePropertyToData(
                "integrating downloading image is ready", "Device.Message"
            )
        elif state == 0:
            self.storePropertyToData("IDLE", "Device.Message")

        if state == 5:
            if self.deviceConnected:
                self.deviceConnected = False
                self.signals.deviceDisconnected.emit(f"{self.deviceName}")
                self.msg.emit(0, "N.I.N.A.", "Device remove", f"{self.deviceName}")
        else:
            if not self.deviceConnected:
                self.deviceConnected = True
                self.getInitialConfig()
                self.signals.deviceConnected.emit(f"{self.deviceName}")
                self.msg.emit(0, "N.I.N.A.", "Device found", f"{self.deviceName}")

    def clearPollStatus(self) -> None:
        """ """
        self.mutexPollStatus.unlock()

    def pollStatus(self) -> None:
        """ """
        if not self.mutexPollStatus.tryLock():
            return

        self.workerStatus = Worker(self.workerPollStatus)
        self.threadPool.start(self.workerStatus)

    def startCommunication(self) -> None:
        """ """
        self.data.clear()
        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()
        self.startNINATimer()

    def stopCommunication(self) -> None:
        """ """
        self.stopNINATimer()
        if self.deviceName != "N.I.N.A. controlled":
            self.disconnectDevice()
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, "N.I.N.A.", "Device remove", f"{self.deviceName}")

    def discoverDevices(self, deviceType: str) -> list:
        """ """
        discoverList = self.enumerateDevice()
        self.log.debug(f"[Type: {deviceType}: {discoverList}]")
        return discoverList
