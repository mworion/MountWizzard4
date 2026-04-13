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
# Licence APL2.0
#
###########################################################
import logging
from mw4.base.indiClassAddOns import INDI_TYPES, INDIGO
from mw4.base.threadUtils import mainThreadSleep
from mw4.indibase.indiClient import Client
from PySide6.QtCore import Qt, QThreadPool, QTimer, QMutex
from typing import Any


class IndiClass:
    log = logging.getLogger("MW4")
    RETRY_DELAY: int = 1500
    NUMBER_RETRY: int = 5

    def __init__(self, parent: Any) -> None:
        self.parent: Any = parent
        self.app: Any = parent.app
        self.msg: Any = parent.app.msg
        self.data: dict = parent.data
        self.signals: Any = parent.signals
        self.loadConfig: bool = parent.loadConfig
        self.updateRate: int = parent.updateRate
        self.threadPool: QThreadPool = parent.app.threadPool
        self.discoverMutex: QMutex = QMutex()
        self.client: Client = Client(host=None)
        self.client.signals.deviceConnected.connect(self.chainDeviceConnected)
        self.client.signals.deviceDisconnected.connect(self.chainDeviceDisconnected)
        self.client.signals.serverConnected.connect(self.chainServerConnected)
        self.client.signals.serverDisconnected.connect(self.chainServerDisconnected)

        self.deviceName: str = ""
        self.device: Any = None
        self.deviceConnected: bool = False
        self._hostaddress: str | None = None
        self._host: tuple[str, int] | None = None
        self._port: int | None = None
        self.discoverType: int | None = None
        self.discoverList: list[str] = []
        self.isINDIGO: bool = False
        self.messages: bool = False

        self.defaultConfig: dict[str, Any] = {
            "deviceName": "",
            "deviceList": [],
            "hostaddress": "localhost",
            "port": 7624,
            "loadConfig": False,
            "messages": False,
            "updateRate": 1000,
        }

        self.timerRetry: QTimer = QTimer()
        self.timerRetry.setSingleShot(True)
        self.timerRetry.timeout.connect(self.startRetry)
        self.client.signals.newDevice.connect(self.newDevice)
        self.client.signals.removeDevice.connect(self.removeDevice)
        self.client.signals.newProperty.connect(self.connectDevice)
        self.client.signals.newNumber.connect(self.updateNumber)
        self.client.signals.defNumber.connect(self.updateNumber)
        self.client.signals.newSwitch.connect(self.updateSwitch)
        self.client.signals.defSwitch.connect(self.updateSwitch)
        self.client.signals.newText.connect(self.updateText)
        self.client.signals.defText.connect(self.updateText)
        self.client.signals.newLight.connect(self.updateLight)
        self.client.signals.defLight.connect(self.updateLight)
        self.client.signals.newBLOB.connect(self.updateBLOB)
        self.client.signals.defBLOB.connect(self.updateBLOB)
        self.client.signals.deviceConnected.connect(self.setUpdateConfig)
        self.client.signals.serverConnected.connect(self.serverConnected)
        self.client.signals.serverDisconnected.connect(self.serverDisconnected)
        self.client.signals.newMessage.connect(self.updateMessage)

    @property
    def host(self) -> tuple[str, int] | None:
        return self._host

    @host.setter
    def host(self, value: tuple[str, int] | None) -> None:
        self._host = value
        self.client.host = value

    @property
    def hostaddress(self) -> str | None:
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value: str | None) -> None:
        self._hostaddress = value
        self.client.host = (self._hostaddress, self._port)

    @property
    def port(self) -> int | None:
        return self._port

    @port.setter
    def port(self, value: int | str) -> None:
        self._port = int(value)
        self.client.host = (self._hostaddress, self._port)

    def chainServerConnected(self) -> None:
        self.signals.serverConnected.emit()

    def chainServerDisconnected(self, deviceName: str) -> None:
        self.signals.serverDisconnected.emit(deviceName)

    def chainDeviceConnected(self, deviceName: str) -> None:
        self.signals.deviceConnected.emit(deviceName)

    def chainDeviceDisconnected(self, deviceName: str) -> None:
        self.signals.deviceDisconnected.emit(deviceName)

    def serverConnected(self) -> None:
        suc = self.client.watchDevice(self.deviceName)
        self.log.info(f"INDI watch: [{self.deviceName}], result: [{suc}]")

    def serverDisconnected(self, devices: str) -> None:
        t = f"INDI server for [{self.deviceName}:{devices}] disconnected"
        self.log.info(t)

    def newDevice(self, deviceName: str) -> None:
        if deviceName == self.deviceName:
            self.device = self.client.getDevice(deviceName)
            self.msg.emit(0, "INDI", "Device found", f"{deviceName}")
        else:
            self.log.info(f"INDI device snoop: [{deviceName}]")

    def removeDevice(self, deviceName: str) -> None:
        if deviceName == self.deviceName:
            self.msg.emit(0, "INDI", "Device removed", f"{deviceName}")
            self.device = None
            self.data.clear()

    def startRetry(self) -> None:
        self.timerRetry.start(self.RETRY_DELAY)
        if not self.deviceName:
            return
        if self.client.connected:
            return

        self.client.connectServer()
        self.signals.serverConnected.emit()

    def startCommunication(self) -> None:
        self.data.clear()
        self.timerRetry.start(self.RETRY_DELAY)

    def stopCommunication(self) -> None:
        self.client.disconnectServer(self.deviceName)
        self.deviceName = ""
        self.deviceConnected = False

    def connectDevice(self, deviceName: str, propertyName: str) -> None:
        if propertyName != "CONNECTION":
            return

        if deviceName == self.deviceName:
            self.client.connectDevice(deviceName=deviceName)

    def loadIndiConfig(self, deviceName: str) -> None:
        loadObject = self.device.getSwitch("CONFIG_PROCESS")
        loadObject["CONFIG_LOAD"] = True
        suc = self.client.sendNewSwitch(
            deviceName=deviceName, propertyName="CONFIG_PROCESS", elements=loadObject
        )
        t = f"Config load [{deviceName}] success: [{suc}], value: [True]"
        self.log.info(t)

    def setUpdateConfig(self, deviceName: str) -> None:
        if deviceName != self.deviceName:
            return
        if self.device is None:
            return

        if self.loadConfig:
            self.loadIndiConfig(deviceName=deviceName)

        update = self.device.getNumber("POLLING_PERIOD")
        update["PERIOD_MS"] = int(self.updateRate)
        suc = self.client.sendNewNumber(
            deviceName=deviceName, propertyName="POLLING_PERIOD", elements=update
        )
        t = f"Polling [{deviceName}] success: [{suc}], value:[{update['PERIOD_MS']}]"
        self.log.info(t)

    @staticmethod
    def convertIndigoProperty(key: str) -> str:
        if key in INDIGO:
            key = INDIGO.get(key)
        return key

    def updateNumber(self, deviceName: str, propertyName: str) -> None:
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

        for element, value in self.device.getNumber(propertyName).items():
            key = self.convertIndigoProperty(propertyName + "." + element)
            self.data[key] = float(value)

    def updateSwitch(self, deviceName: str, propertyName: str) -> None:
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

        for element, value in self.device.getSwitch(propertyName).items():
            if propertyName == "PROFILE":
                self.isINDIGO = True
            key = self.convertIndigoProperty(propertyName + "." + element)
            self.data[key] = value == "On"

    def updateText(self, deviceName: str, propertyName: str) -> None:
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

        for element, value in self.device.getText(propertyName).items():
            key = self.convertIndigoProperty(propertyName + "." + element)
            self.data[key] = value

    def updateLight(self, deviceName: str, propertyName: str) -> None:
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

        for element, value in self.device.getLight(propertyName).items():
            key = self.convertIndigoProperty(propertyName + "." + element)
            self.data[key] = value

    def updateBLOB(self, deviceName: str, propertyName: str) -> None:
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

    @staticmethod
    def removePrefix(text: str, prefix: str) -> str:
        value = text[text.startswith(prefix) and len(prefix) :]
        value = value.strip()
        return value

    def updateMessage(self, device: str, text: str) -> None:
        if self.messages:
            if text.startswith("[WARNING]"):
                text = self.removePrefix(text, "[WARNING]")
                self.msg.emit(0, "INDI", "Device warning", f"{device:15s} {text}")
            elif text.startswith("[INFO]"):
                text = self.removePrefix(text, "[INFO]")
                self.msg.emit(0, "INDI", "Device info", f"{device:15s} {text}")
            elif text.startswith("[ERROR]"):
                text = self.removePrefix(text, "[ERROR]")
                self.msg.emit(2, "INDI", "Device error", f"{device:15s} {text}")
            else:
                self.msg.emit(0, "INDI", "Device message", f"{device:15s} {text}")

    def addDiscoveredDevice(self, deviceName: str, propertyName: str) -> None:
        if propertyName != "DRIVER_INFO":
            return

        device = self.client.devices.get(deviceName)
        if not device:
            return

        interface = device.getText(propertyName).get("DRIVER_INTERFACE", None)
        if interface is None:
            return
        if interface == "0":
            interface = 0xFFFF
        if self.discoverType is None:
            return

        self.log.debug(f"Found: [{deviceName}], interface: [{interface}]")
        interface = int(interface)
        if interface & self.discoverType:
            self.discoverList.append(deviceName)

    def discoverDevices(self, deviceType: str) -> list[str]:
        self.discoverList = []
        if not self.discoverMutex.tryLock():
            return self.discoverList
        self.discoverType = INDI_TYPES.get(deviceType, 0)
        self.client.signals.defText.connect(self.addDiscoveredDevice)
        self.client.connectServer()
        mainThreadSleep(2000)
        self.client.signals.defText.disconnect(self.addDiscoveredDevice)
        self.client.disconnectServer()
        return self.discoverList
