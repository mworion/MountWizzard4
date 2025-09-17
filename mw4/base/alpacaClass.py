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
import uuid
import requests

# external packages
from PySide6.QtCore import QTimer

from base.driverDataClass import DriverData
from base.tpool import Worker

# local imports
from gui.utilities.toolsQtWidget import sleepAndEvents


class AlpacaClass(DriverData):
    """ """

    ALPACA_TIMEOUT = 3
    CLIENT_ID = uuid.uuid4().int % 2**16

    def __init__(self, parent):
        super().__init__()

        self.app = parent.app
        self.msg = parent.app.msg
        self.data = parent.data
        self.signals = parent.signals
        self.threadPool = parent.app.threadPool
        self.updateRate: int = 1000
        self.loadConfig: bool = False
        self.propertyExceptions: list = []

        self._host: tuple = ("localhost", 11111)
        self._port: int = 11111
        self._hostaddress: str = "localhost"
        self.protocol: str = "http"
        self.apiVersion: int = 1
        self._deviceName: str = ""
        self.deviceType: str = ""
        self.number: int = 0

        self.defaultConfig: dict = {
            "deviceName": "",
            "deviceList": [],
            "hostaddress": "localhost",
            "port": 11111,
            "apiVersion": 1,
            "user": "",
            "password": "",
            "updateRate": 1000,
        }

        self.deviceConnected: bool = False
        self.serverConnected: bool = False
        self.worker: Worker = None
        self.workerGetConfig: Worker = None
        self.workerStatus: Worker = None
        self.workerData: Worker = None
        self.workerConnect: Worker = None

        self.cycleDevice = QTimer()
        self.cycleDevice.setSingleShot(False)
        self.cycleDevice.timeout.connect(self.pollStatus)

        self.cycleData = QTimer()
        self.cycleData.setSingleShot(False)
        self.cycleData.timeout.connect(self.pollData)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def hostaddress(self):
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value):
        self._hostaddress = value
        self._host = (self._hostaddress, self._port)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = int(value)
        self._host = (self._hostaddress, self._port)

    @property
    def baseUrl(self):
        return self.generateBaseUrl()

    @property
    def deviceName(self):
        return self._deviceName

    @deviceName.setter
    def deviceName(self, value):
        self._deviceName = value
        valueSplit = value.split(":")
        if len(valueSplit) != 3:
            return
        self.deviceType = valueSplit[1].strip()
        self.number = valueSplit[2].strip()
        self.number = int(self.number)

    def generateBaseUrl(self) -> str:
        """ """
        val = "{0}://{1}:{2}/api/v{3}/{4}/{5}".format(
            self.protocol,
            self.host[0],
            self.host[1],
            self.apiVersion,
            self.deviceType,
            self.number,
        )
        return val

    def discoverAPIVersion(self) -> int:
        """ """
        url = "{0}://{1}:{2}/management/apiversions".format(
            self.protocol, self.host[0], self.host[1]
        )

        uid = uuid.uuid4().int % 2**32
        data = {"ClientTransactionID": uid, "ClientID": self.CLIENT_ID}

        try:
            response = requests.get(url, params=data, timeout=self.ALPACA_TIMEOUT)
        except Exception as e:
            self.log.error(f"Discover API exception: [{e}]")
            return 0

        if response.status_code == 400 or response.status_code == 500:
            t = f"Discover API version stat 400/500, [{response.text}]"
            self.log.warning(t)
            return 0

        response = response.json()
        if response["ErrorNumber"] != 0:
            self.log.warning(f"Discover API response: [{response}]")
            return 0

        self.log.trace(f"Discover API response: [{response}]")
        return response["Value"]

    def discoverAlpacaDevices(self) -> str:
        """ """
        url = "{0}://{1}:{2}/management/v{3}/configureddevices".format(
            self.protocol, self.host[0], self.host[1], self.apiVersion
        )

        uid = uuid.uuid4().int % 2**32
        data = {"ClientTransactionID": uid, "ClientID": self.CLIENT_ID}

        try:
            response = requests.get(url, params=data, timeout=self.ALPACA_TIMEOUT)

        except Exception as e:
            self.log.error(f"Search devices exception: [{e}]")
            return ""

        if response.status_code == 400 or response.status_code == 500:
            self.log.warning("Search devices stat 400/500]")
            return ""

        response = response.json()
        if response["ErrorNumber"] != 0:
            self.log.warning(f"Search devices response: [{response}]")
            return ""

        self.log.trace(f"Search devices response: [{response}]")
        return response["Value"]

    def getAlpacaProperty(self, valueProp: str, **data) -> dict:
        """ """
        if not self.deviceName:
            return {}
        if valueProp in self.propertyExceptions:
            return {}

        uid = uuid.uuid4().int % 2**32
        data["ClientTransactionID"] = uid
        data["ClientID"] = self.CLIENT_ID

        t = f"[{self.deviceName}] [{uid:10d}], get [{valueProp}], data:[{data}]"
        self.log.trace(t)

        try:
            response = requests.get(
                f"{self.baseUrl}/{valueProp}", params=data, timeout=self.ALPACA_TIMEOUT
            )
        except Exception as e:
            t = f"[{self.deviceName}] [{uid:10d}] has exception: [{e}]"
            self.log.error(t)
            return {}

        if response.status_code == 400 or response.status_code == 500:
            t = f"[{self.deviceName}] [{uid:10d}], stat 400/500"
            self.log.warning(t)
            return {}

        response = response.json()
        if response["ErrorNumber"] != 0:
            t = f"[{self.deviceName}] [{uid:10d}], response: [{response}]"
            self.log.warning(t)
            self.propertyExceptions.append(valueProp)
            return {}

        if valueProp != "imagearray":
            t = f"[{self.deviceName}] [{uid:10d}], response: [{response}]"
            self.log.trace(t)
        else:
            self.log.trace(f"[{self.deviceName}] [{uid:10d}]")

        return response["Value"]

    def setAlpacaProperty(self, valueProp: str, **data) -> dict:
        """ """
        if not self.deviceName:
            return {}
        if valueProp in self.propertyExceptions:
            return {}

        uid = uuid.uuid4().int % 2**32
        t = f"[{self.deviceName}] [{uid:10d}], set [{valueProp}] to: [{data}]"
        self.log.trace(t)

        try:
            response = requests.put(
                f"{self.baseUrl}/{valueProp}", data=data, timeout=self.ALPACA_TIMEOUT
            )
        except Exception as e:
            t = f"[{self.deviceName}] [{uid:10d}] has exception: [{e}]"
            self.log.error(t)
            return {}

        if response.status_code == 400 or response.status_code == 500:
            t = f"[{self.deviceName}] [{uid:10d}], stat 400/500, [{response.text}]"
            self.log.warning(t)
            return {}

        response = response.json()
        if response["ErrorNumber"] != 0:
            t = f"[{self.deviceName}] [{uid:10d}], response: [{response}]"
            self.log.warning(t)
            self.propertyExceptions.append(valueProp)
            return {}

        t = f"[{self.deviceName}] [{uid:10d}], response: [{response}]"
        self.log.trace(t)
        return response

    def getAndStoreAlpacaProperty(self, valueProp: str, element: str) -> None:
        """ """
        value = self.getAlpacaProperty(valueProp)
        self.storePropertyToData(value, element)

    def workerConnectDevice(self) -> None:
        """ """
        self.propertyExceptions = []
        self.deviceConnected = False
        self.serverConnected = False
        suc = False
        for retry in range(0, 10):
            self.setAlpacaProperty("connected", Connected=True)
            suc = self.getAlpacaProperty("connected")

            if suc:
                t = f"[{self.deviceName}] connected, [{retry}] retries"
                self.log.debug(t)
                break
            else:
                t = f" [{self.deviceName}] Connection retry: [{retry}]"
                self.log.info(t)
                sleepAndEvents(250)

        if not suc:
            self.msg.emit(2, "ALPACA", "Connect error", f"{self.deviceName}")
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ALPACA", "Device found", f"{self.deviceName}")
            self.startAlpacaTimer()
            self.getInitialConfig()
        return True

    def startAlpacaTimer(self) -> None:
        """ """
        self.cycleData.start(self.updateRate)
        self.cycleDevice.start(self.updateRate)

    def stopAlpacaTimer(self) -> None:
        """ """
        self.cycleData.stop()
        self.cycleDevice.stop()

    def workerGetInitialConfig(self) -> None:
        """ """
        self.data["DRIVER_INFO.DRIVER_NAME"] = self.getAlpacaProperty("name")
        self.data["DRIVER_INFO.DRIVER_VERSION"] = self.getAlpacaProperty("driverversion")
        self.data["DRIVER_INFO.DRIVER_EXEC"] = self.getAlpacaProperty("driverinfo")

    def workerPollStatus(self) -> None:
        """ """
        suc = self.getAlpacaProperty("connected")
        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.signals.deviceDisconnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ALPACA", "Device remove", f"{self.deviceName}")

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ALPACA", "Device found", f"{self.deviceName}")

    def processPolledData(self):
        pass

    def workerPollData(self):
        pass

    def pollData(self) -> None:
        """ """
        if not self.deviceConnected:
            return

        self.workerData = Worker(self.workerPollData)
        self.workerData.signals.result.connect(self.processPolledData)
        self.threadPool.start(self.workerData)

    def pollStatus(self) -> None:
        """ """
        if not self.deviceConnected:
            return

        self.workerStatus = Worker(self.workerPollStatus)
        self.threadPool.start(self.workerStatus)

    def getInitialConfig(self) -> None:
        """ """
        if not self.deviceConnected:
            return

        self.workerGetConfig = Worker(self.workerGetInitialConfig)
        self.threadPool.start(self.workerGetConfig)

    def startCommunication(self) -> None:
        """ """
        self.data.clear()
        self.workerConnect = Worker(self.workerConnectDevice)
        self.threadPool.start(self.workerConnect)

    def stopCommunication(self) -> None:
        """ """
        self.stopAlpacaTimer()
        self.setAlpacaProperty("connected", Connected=False)
        self.deviceConnected = False
        self.serverConnected = False
        self.propertyExceptions = []
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, "ALPACA", "Device  remove", f"{self.deviceName}")

    def discoverDevices(self, deviceType: str) -> list:
        """ """
        devices = self.discoverAlpacaDevices()
        if not devices:
            return []

        temp = [x for x in devices if x["DeviceType"].lower() == deviceType]
        discoverList = [f"{x['DeviceName']}:{deviceType}:{x['DeviceNumber']}" for x in temp]
        return discoverList
