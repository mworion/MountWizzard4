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
    CLIENT_ID = uuid.uuid4().int % 2 ** 16

    def __init__(self, app, data):
        super().__init__()

        self.app = app
        self.msg = app.msg
        self.data = data
        self.threadPool = app.threadPool
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
        """
        """
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
        """
        """
        url = "{0}://{1}:{2}/management/apiversions".format(
            self.protocol, self.host[0], self.host[1]
        )

        uid = uuid.uuid4().int % 2 ** 32
        data = {"ClientTransactionID": uid, "ClientID": self.CLIENT_ID}

        try:
            response = requests.get(url, params=data, timeout=self.ALPACA_TIMEOUT)
        except requests.exceptions.Timeout:
            t = "Discover API version has timeout"
            self.log.debug(t)
            return 0
        except requests.exceptions.ConnectionError:
            t = "Discover API version has connection error"
            self.log.warning(t)
            return 0
        except Exception as e:
            t = f"Discover API version has exception: [{e}]"
            self.log.error(t)
            return 0

        if response.status_code == 400 or response.status_code == 500:
            t = f"Discover API version stat 400/500, [{response.text}]"
            self.log.warning(t)
            return 0

        response = response.json()
        if response["ErrorNumber"] != 0:
            t = f"Discover API version response: [{response}]"
            self.log.warning(t)
            return 0

        t = f"Discover API version response: [{response}]"
        self.log.trace(t)
        return response["Value"]

    def discoverAlpacaDevices(self) -> str:
        """
        """
        url = "{0}://{1}:{2}/management/v{3}/configureddevices".format(
            self.protocol, self.host[0], self.host[1], self.apiVersion
        )

        uid = uuid.uuid4().int % 2 ** 32
        data = {"ClientTransactionID": uid, "ClientID": self.CLIENT_ID}

        try:
            response = requests.get(url, params=data, timeout=self.ALPACA_TIMEOUT)
        except requests.exceptions.Timeout:
            t = "Search devices has timeout"
            self.log.debug(t)
            return ""
        except requests.exceptions.ConnectionError:
            t = "Search devices has connection error"
            self.log.warning(t)
            return ""
        except Exception as e:
            t = f"Search devices has exception: [{e}]"
            self.log.error(t)
            return ""

        if response.status_code == 400 or response.status_code == 500:
            t = f"Search devices stat 400/500, [{response.text}]"
            self.log.warning(t)
            return ""

        response = response.json()
        if response["ErrorNumber"] != 0:
            t = f"Search devices response: [{response}]"
            self.log.warning(t)
            return ""

        t = f"Search devices response: [{response}]"
        self.log.trace(t)
        return response["Value"]

    def getAlpacaProperty(self, valueProp, **data):
        """
        :param valueProp:
        :param data:
        :return:
        """
        if not self.deviceName:
            return None
        if valueProp in self.propertyExceptions:
            return None

        uid = uuid.uuid4().int % 2 ** 32
        data["ClientTransactionID"] = uid
        data["ClientID"] = self.CLIENT_ID

        t = f"[{self.deviceName}] [{uid:10d}], get [{valueProp}], data:[{data}]"
        self.log.trace(t)

        try:
            response = requests.get(
                f"{self.baseUrl}/{valueProp}", params=data, timeout=self.ALPACA_TIMEOUT
            )
        except requests.exceptions.Timeout:
            t = f"[{self.deviceName}] [{uid:10d}] has timeout"
            self.log.debug(t)
            return None
        except requests.exceptions.ConnectionError:
            t = f"[{self.deviceName}] [{uid:10d}] has connection error"
            self.log.warning(t)
            return None
        except Exception as e:
            t = f"[{self.deviceName}] [{uid:10d}] has exception: [{e}]"
            self.log.error(t)
            return None

        if response.status_code == 400 or response.status_code == 500:
            t = f"[{self.deviceName}] [{uid:10d}], stat 400/500, [{response.text}]"
            self.log.warning(t)
            return None

        response = response.json()
        if response["ErrorNumber"] != 0:
            t = f"[{self.deviceName}] [{uid:10d}], response: [{response}]"
            self.log.warning(t)
            self.propertyExceptions.append(valueProp)
            return None

        if valueProp != "imagearray":
            t = f"[{self.deviceName}] [{uid:10d}], response: [{response}]"
            self.log.trace(t)
        else:
            self.log.trace(f"[{self.deviceName}] [{uid:10d}]")

        return response["Value"]

    def setAlpacaProperty(self, valueProp, **data):
        """
        :param valueProp:
        :param data:
        :return:
        """
        if not self.deviceName:
            return None
        if valueProp in self.propertyExceptions:
            return None

        uid = uuid.uuid4().int % 2 ** 32
        t = f"[{self.deviceName}] [{uid:10d}], set [{valueProp}] to: [{data}]"
        self.log.trace(t)

        try:
            response = requests.put(
                f"{self.baseUrl}/{valueProp}", data=data, timeout=self.ALPACA_TIMEOUT
            )
        except requests.exceptions.Timeout:
            t = f"[{self.deviceName}] [{uid:10d}] has timeout"
            self.log.debug(t)
            return None
        except requests.exceptions.ConnectionError:
            t = f"[{self.deviceName}] [{uid:10d}] has connection error"
            self.log.warning(t)
            return None
        except Exception as e:
            t = f"[{self.deviceName}] [{uid:10d}] has exception: [{e}]"
            self.log.error(t)
            return None

        if response.status_code == 400 or response.status_code == 500:
            t = f"[{self.deviceName}] [{uid:10d}], stat 400/500, [{response.text}]"
            self.log.warning(t)
            return None

        response = response.json()
        if response["ErrorNumber"] != 0:
            t = f"[{self.deviceName}] [{uid:10d}], response: [{response}]"
            self.log.warning(t)
            self.propertyExceptions.append(valueProp)
            return None

        t = f"[{self.deviceName}] [{uid:10d}], response: [{response}]"
        self.log.trace(t)
        return response

    def getAndStoreAlpacaProperty(self, valueProp, element, elementInv=None):
        """
        :param valueProp:
        :param element:
        :param elementInv:
        :return: reset entry
        """
        value = self.getAlpacaProperty(valueProp)
        self.storePropertyToData(value, element, elementInv)
        return True

    def workerConnectDevice(self):
        """
        :return: success of reconnecting to server
        """
        self.propertyExceptions = []
        self.deviceConnected = False
        self.serverConnected = False
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
            self.startTimer()
            self.getInitialConfig()
        return True

    def startTimer(self):
        """
        :return: true for test purpose
        """
        self.cycleData.start(self.updateRate)
        self.cycleDevice.start(self.updateRate)
        return True

    def stopTimer(self):
        """
        :return: true for test purpose
        """
        self.cycleData.stop()
        self.cycleDevice.stop()
        return True

    def workerGetInitialConfig(self):
        """
        :return:
        """
        self.data["DRIVER_INFO.DRIVER_NAME"] = self.getAlpacaProperty("name")
        self.data["DRIVER_INFO.DRIVER_VERSION"] = self.getAlpacaProperty(
            "driverversion"
        )
        self.data["DRIVER_INFO.DRIVER_EXEC"] = self.getAlpacaProperty("driverinfo")
        return True

    def workerPollStatus(self):
        """
        :return: success
        """
        suc = self.getAlpacaProperty("connected")
        if self.deviceConnected and not suc:
            self.deviceConnected = False
            self.signals.deviceDisconnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ALPACA", "Device remove", f"{self.deviceName}")

        elif not self.deviceConnected and suc:
            self.deviceConnected = True
            self.signals.deviceConnected.emit(f"{self.deviceName}")
            self.msg.emit(0, "ALPACA", "Device found", f"{self.deviceName}")

        return suc

    def processPolledData(self):
        pass

    def workerPollData(self):
        pass

    def pollData(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False
        worker = Worker(self.workerPollData)
        worker.signals.result.connect(self.processPolledData)
        self.threadPool.start(worker)
        return True

    def pollStatus(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False
        worker = Worker(self.workerPollStatus)
        self.threadPool.start(worker)
        return True

    def getInitialConfig(self):
        """
        :return: success
        """
        if not self.deviceConnected:
            return False
        worker = Worker(self.workerGetInitialConfig)
        self.threadPool.start(worker)
        return True

    def startCommunication(self):
        """
        :return: True for test purpose
        """
        self.data.clear()
        worker = Worker(self.workerConnectDevice)
        self.threadPool.start(worker)
        return True

    def stopCommunication(self):
        """
        :return: true for test purpose
        """
        self.stopTimer()
        self.setAlpacaProperty("connected", Connected=False)
        self.deviceConnected = False
        self.serverConnected = False
        self.propertyExceptions = []
        self.signals.deviceDisconnected.emit(f"{self.deviceName}")
        self.signals.serverDisconnected.emit({f"{self.deviceName}": 0})
        self.msg.emit(0, "ALPACA", "Device  remove", f"{self.deviceName}")
        return True

    def discoverDevices(self, deviceType=""):
        """ """
        devices = self.discoverAlpacaDevices()
        if not devices:
            return []

        temp = [x for x in devices if x["DeviceType"].lower() == deviceType]
        discoverList = [
            f'{x["DeviceName"]}:{deviceType}:{x["DeviceNumber"]}' for x in temp
        ]
        return discoverList
