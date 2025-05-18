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
from PySide6.QtCore import QTimer, QObject
import requests

# local imports
from base.driverDataClass import DriverData
from base.driverDataClass import RemoteDeviceShutdown
from base.tpool import Worker


class SGProClass(DriverData, QObject):
    """ """

    SGPRO_TIMEOUT = 3
    HOST_ADDR = "localhost"
    PORT = 59590
    PROTOCOL = "http"
    BASE_URL = f"{PROTOCOL}://{HOST_ADDR}:{PORT}"
    DEVICE_TYPE = "Camera"

    def __init__(self, app=None, data=None):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool
        self.msg = app.msg
        self.data = data
        self.updateRate = 1000
        self.loadConfig = False
        self._deviceName = ""
        self.defaultConfig = {
            "deviceList": ["SGPro"],
            "deviceName": "SGPro",
        }
        self.signalRS = RemoteDeviceShutdown()

        self.deviceConnected = False
        self.serverConnected = False
        self.workerPollData = None
        self.workerGetConfig = None
        self.workerPollStatus = None

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

    def requestProperty(self, valueProp, params: dict = {}) -> dict:
        """ """
        try:
            t = f"SGPro: [{self.BASE_URL}/{valueProp}?format=json]"
            if params:
                t += f" data: [{bytes(json.dumps(params).encode('utf-8'))}]"
                self.log.trace("POST " + t)
                response = requests.post(
                    f"{self.BASE_URL}/{valueProp}?format=json",
                    json=params,
                    timeout=self.SGPRO_TIMEOUT,
                )
            else:
                self.log.trace("GET " + t)
                response = requests.get(
                    f"{self.BASE_URL}/{valueProp}?format=json",
                    timeout=self.SGPRO_TIMEOUT,
                )
        except Exception as e:
            self.log.error(f"Request SGPro error: [{e}]")
            return {}

        if response.status_code != 200:
            t = f"Request SGPro response invalid: [{response.status_code}]"
            self.log.warning(t)
            return {}

        self.log.trace(f"Request SGpro response: [{response.json()}]")
        response = response.json()
        return response

    def sgConnectDevice(self) -> bool:
        """ """
        devName = self.deviceName.replace(" ", "%20")
        prop = f"connectdevice/{self.DEVICE_TYPE}/{devName}"
        response = self.requestProperty(prop)
        return response.get("Success", False)

    def sgDisconnectDevice(self) -> bool:
        """ """
        prop = f"disconnectdevice/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Success", False)

    def sgEnumerateDevice(self) -> list:
        """ """
        prop = f"enumdevices/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)
        return response.get("Devices", [])

    def startTimer(self) -> None:
        """ """
        self.cycleData.start(self.updateRate)
        self.cycleDevice.start(self.updateRate)

    def stopTimer(self) -> None:
        """ """
        self.cycleData.stop()
        self.cycleDevice.stop()

    def processPolledData(self) -> None:
        pass

    def workerPollData(self) -> None:
        pass

    def pollData(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.workerPollData = Worker(self.workerPollData)
        self.workerPollData.signals.result.connect(self.processPolledData)
        self.threadPool.start(self.workerPollData)

    def workerGetInitialConfig(self) -> None:
        pass

    def getInitialConfig(self) -> None:
        """ """
        self.workerGetConfig = Worker(self.workerGetInitialConfig)
        self.threadPool.start(self.workerGetConfig)

    def workerPollStatus(self) -> None:
        """ """
        prop = f"devicestatus/{self.DEVICE_TYPE}"
        response = self.requestProperty(prop)

        if response is None:
            return

        self.storePropertyToData(response["State"], "Device.Status")
        self.storePropertyToData(response["Message"], "Device.Message")

        if response.get("State", "") == "DISCONNECTED":
            if self.deviceConnected:
                self.deviceConnected = False
                self.signals.deviceDisconnected.emit(f"{self.deviceName}")
                self.msg.emit(0, "SGPRO", "Device remove", f"{self.deviceName}")

        else:
            if not self.deviceConnected:
                self.deviceConnected = True
                self.getInitialConfig()
                self.signals.deviceConnected.emit(f"{self.deviceName}")
                self.msg.emit(0, "SGPRO", "Device found", f"{self.deviceName}")

    def pollStatus(self) -> None:
        """ """
        self.workerPollStatus = Worker(self.workerPollStatus)
        self.threadPool.start(self.workerPollStatus)

    def startCommunication(self) -> None:
        """ """
        self.data.clear()
        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()
        self.startTimer()

    def stopCommunication(self) -> None:
        """ """
        self.stopTimer()
        if self.deviceName != "SGPro controlled":
            self.sgDisconnectDevice()
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, "SGPRO", "Device remove", f"{self.deviceName}")

    def discoverDevices(self, deviceType: str) -> list:
        """ """
        discoverList = self.sgEnumerateDevice()
        return discoverList
