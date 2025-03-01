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
# written in python3, (c) 2019-2024 by mworion
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


class NINAClass(DriverData, QObject):
    """ """

    NINA_TIMEOUT = 3
    HOST_ADDR = "localhost"
    PORT = 59590
    PROTOCOL = "http"
    BASE_URL = f"{PROTOCOL}://{HOST_ADDR}:{PORT}"

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
            "deviceList": ["N.I.N.A."],
            "deviceName": "N.I.N.A.",
        }
        self.signalRS = RemoteDeviceShutdown()

        self.deviceConnected = False
        self.serverConnected = False

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

    def requestProperty(self, valueProp: str, params: dict = {}) -> dict:
        """ """
        try:
            t = f"N.I.N.A.: [{self.BASE_URL}/{valueProp}?format=json]"
            if params:
                t += f' data: [{bytes(json.dumps(params).encode("utf-8"))}]'
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
        worker = Worker(self.workerPollData)
        worker.signals.result.connect(self.processPolledData)
        self.threadPool.start(worker)

    def workerGetInitialConfig(self) -> None:
        pass

    def getInitialConfig(self) -> None:
        """ """
        worker = Worker(self.workerGetInitialConfig)
        self.threadPool.start(worker)

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

    def pollStatus(self) -> None:
        """ """
        worker = Worker(self.workerPollStatus)
        self.threadPool.start(worker)

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
        if self.deviceName != "N.I.N.A. controlled":
            self.disconnectDevice()
        self.deviceConnected = False
        self.serverConnected = False
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, "N.I.N.A.", "Device remove", f"{self.deviceName}")

    def discoverDevices(self) -> list:
        """ """
        discoverList = self.enumerateDevice()
        return discoverList
