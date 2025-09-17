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
import logging

# external packages
from PySide6.QtCore import QTimer

# local imports
from gui.utilities.toolsQtWidget import sleepAndEvents
from indibase.indiClient import Client
from base.signalsDevices import Signals


class IndiClass:
    """ """

    log = logging.getLogger("MW4")

    RETRY_DELAY = 1500
    NUMBER_RETRY = 5
    INDIGO = {
        # numbers
        "WEATHER_PARAMETERS.WEATHER_BAROMETER": "WEATHER_PARAMETERS.WEATHER_PRESSURE",
        # SQM device
        "AUX_INFO.X_AUX_SKY_BRIGHTNESS": "SKY_QUALITY.SKY_BRIGHTNESS",
        "AUX_INFO.X_AUX_SKY_TEMPERATURE": "SKY_QUALITY.SKY_TEMPERATURE",
        # UPB device
        "AUX_INFO.X_AUX_AVERAGE": "POWER_CONSUMPTION.CONSUMPTION_AVG_AMPS",
        "AUX_INFO.X_AUX_AMP_HOUR": "POWER_CONSUMPTION.CONSUMPTION_AMP_HOURS",
        "AUX_INFO.X_AUX_WATT_HOUR": "POWER_CONSUMPTION.CONSUMPTION_WATT_HOURS",
        "AUX_INFO.X_AUX_VOLTAGE": "POWER_SENSORS.SENSOR_VOLTAGE",
        "AUX_INFO.X_AUX_CURRENT": "POWER_SENSORS.SENSOR_CURRENT",
        "AUX_INFO.X_AUX_POWER_OUTLET": "POWER_SENSORS.SENSOR_POWER",
        "AUX_POWER_OUTLET_CURRENT.OUTLET_1": "POWER_CURRENT.POWER_CURRENT_1",
        "AUX_POWER_OUTLET_CURRENT.OUTLET_2": "POWER_CURRENT.POWER_CURRENT_2",
        "AUX_POWER_OUTLET_CURRENT.OUTLET_3": "POWER_CURRENT.POWER_CURRENT_3",
        "AUX_POWER_OUTLET_CURRENT.OUTLET_4": "POWER_CURRENT.POWER_CURRENT_4",
        "AUX_HEATER_OUTLET_CURRENT.OUTLET_1": "DEW_CURRENT.DEW_CURRENT_A",
        "AUX_HEATER_OUTLET_CURRENT.OUTLET_2": "DEW_CURRENT.DEW_CURRENT_B",
        "AUX_HEATER_OUTLET_CURRENT.OUTLET_3": "DEW_CURRENT.DEW_CURRENT_C",
        "AUX_HEATER_OUTLET.OUTLET_1": "DEW_PWM.DEW_A",
        "AUX_HEATER_OUTLET.OUTLET_2": "DEW_PWM.DEW_B",
        "AUX_HEATER_OUTLET.OUTLET_3": "DEW_PWM.DEW_C",
        "X_AUX_VARIABLE_POWER_OUTLET.OUTLET_1": "ADJUSTABLE_VOLTAGE.ADJUSTABLE_VOLTAGE_VALUE",
        # switches
        # UPB device
        "AUX_POWER_OUTLET.OUTLET_1": "POWER_CONTROL.POWER_CONTROL_1",
        "AUX_POWER_OUTLET.OUTLET_2": "POWER_CONTROL.POWER_CONTROL_2",
        "AUX_POWER_OUTLET.OUTLET_3": "POWER_CONTROL.POWER_CONTROL_3",
        "AUX_POWER_OUTLET.OUTLET_4": "POWER_CONTROL.POWER_CONTROL_4",
        "AUX_USB_PORT.PORT_1": "USB_PORT_CONTROL.PORT_1",
        "AUX_USB_PORT.PORT_2": "USB_PORT_CONTROL.PORT_2",
        "AUX_USB_PORT.PORT_3": "USB_PORT_CONTROL.PORT_3",
        "AUX_USB_PORT.PORT_4": "USB_PORT_CONTROL.PORT_4",
        "AUX_USB_PORT.PORT_5": "USB_PORT_CONTROL.PORT_5",
        "AUX_USB_PORT.PORT_6": "USB_PORT_CONTROL.PORT_6",
        "AUX_DEW_CONTROL.MANUAL": "AUTO_DEW.INDI_DISABLED",
        "AUX_DEW_CONTROL.AUTOMATIC": "AUTO_DEW.INDI_ENABLED",
        "X_AUX_REBOOT.REBOOT": "REBOOT_DEVICE.REBOOT",
        # text
        # UPB device
        "X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_1": "POWER_CONTROL_LABEL.POWER_LABEL_1",
        "X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_2": "POWER_CONTROL_LABEL.POWER_LABEL_2",
        "X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_3": "POWER_CONTROL_LABEL.POWER_LABEL_3",
        "X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_4": "POWER_CONTROL_LABEL.POWER_LABEL_4",
        # Uranus Meteo device
        "SENSORS.AbsolutePressure": "WEATHER_PARAMETERS.WEATHER_PRESSURE",
        "SENSORS.DewPoint": "WEATHER_PARAMETERS.WEATHER_DEWPOINT",
        "CLOUDS.CloudSkyTemperature": "SKY_QUALITY.SKY_TEMPERATURE",
        "SKYQUALITY.MPAS": "SKY_QUALITY.SKY_BRIGHTNESS",
    }
    INDI = {y: x for x, y in INDIGO.items()}
    INDI_TYPES = {
        "telescope": (1 << 0),
        "camera": (1 << 1),
        "guider": (1 << 2),
        "focuser": (1 << 3),
        "filterwheel": (1 << 4),
        "dome": (1 << 5),
        "observingconditions": (1 << 7) | (1 << 15),
        "skymeter": (1 << 15) | (1 << 19),
        "covercalibrator": (1 << 9) | (1 << 10),
        "switch": (1 << 7) | (1 << 3) | (1 << 15) | (1 << 18),
    }
    signals = Signals()

    def __init__(self, parent):
        self.parent = parent
        self.app = parent.app
        self.msg = parent.app.msg
        self.data = parent.data
        self.loadConfig = parent.loadConfig
        self.updateRate = parent.updateRate
        self.threadPool = parent.app.threadPool
        self.client = Client(host=None)

        clientSig = self.client.signals
        selfSig = self.signals
        clientSig.deviceConnected.connect(selfSig.deviceConnected)
        clientSig.deviceDisconnected.connect(selfSig.deviceDisconnected)
        clientSig.serverConnected.connect(selfSig.serverConnected)
        clientSig.serverDisconnected.connect(selfSig.serverDisconnected)

        self.deviceName = ""
        self.device = None
        self.deviceConnected = False
        self._hostaddress = None
        self._host = None
        self._port = None
        self.discoverType = None
        self.discoverList = None
        self.isINDIGO = False
        self.messages = False

        self.defaultConfig = {
            "deviceName": "",
            "deviceList": [],
            "hostaddress": "localhost",
            "port": 7624,
            "loadConfig": False,
            "messages": False,
            "updateRate": 1000,
        }

        self.timerRetry = QTimer()
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
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self.client.host = value

    @property
    def hostaddress(self):
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value):
        self._hostaddress = value
        self.client.host = (self._hostaddress, self._port)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = int(value)
        self.client.host = (self._hostaddress, self._port)

    def serverConnected(self) -> None:
        """ """
        suc = self.client.watchDevice(self.deviceName)
        self.log.info(f"INDI watch: [{self.deviceName}], result: [{suc}]")

    def serverDisconnected(self, devices: str) -> None:
        """ """
        t = f"INDI server for [{self.deviceName}:{devices}] disconnected"
        self.log.info(t)

    def newDevice(self, deviceName: str) -> None:
        """ """
        if deviceName == self.deviceName:
            self.device = self.client.getDevice(deviceName)
            self.msg.emit(0, "INDI", "Device found", f"{deviceName}")
        else:
            self.log.info(f"INDI device snoop: [{deviceName}]")

    def removeDevice(self, deviceName: str) -> None:
        """ """
        if deviceName == self.deviceName:
            self.msg.emit(0, "INDI", "Device removed", f"{deviceName}")
            self.device = None
            self.data.clear()

    def startRetry(self) -> None:
        """ """
        self.timerRetry.start(self.RETRY_DELAY)
        if not self.deviceName:
            return
        if self.client.connected:
            return

        self.client.connectServer()

    def startCommunication(self) -> None:
        """ """
        self.data.clear()
        self.timerRetry.start(self.RETRY_DELAY)

    def stopCommunication(self) -> None:
        """ """
        self.client.disconnectServer(self.deviceName)
        self.deviceName = ""
        self.deviceConnected = False

    def connectDevice(self, deviceName: str, propertyName: str) -> None:
        """ """
        if propertyName != "CONNECTION":
            return

        if deviceName == self.deviceName:
            self.client.connectDevice(deviceName=deviceName)

    def loadIndiConfig(self, deviceName: str) -> None:
        """ """
        loadObject = self.device.getSwitch("CONFIG_PROCESS")
        loadObject["CONFIG_LOAD"] = True
        suc = self.client.sendNewSwitch(
            deviceName=deviceName, propertyName="CONFIG_PROCESS", elements=loadObject
        )
        t = f"Config load [{deviceName}] success: [{suc}], value: [True]"
        self.log.info(t)

    def setUpdateConfig(self, deviceName: str) -> None:
        """ """
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

    def convertIndigoProperty(self, key: str) -> str:
        """ """
        if key in self.INDIGO:
            key = self.INDIGO.get(key)
        return key

    def updateNumber(self, deviceName: str, propertyName: str) -> None:
        """ """
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

        for element, value in self.device.getNumber(propertyName).items():
            key = self.convertIndigoProperty(propertyName + "." + element)
            self.data[key] = float(value)

    def updateSwitch(self, deviceName: str, propertyName: str) -> None:
        """ """
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
        """ """
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

        for element, value in self.device.getText(propertyName).items():
            key = self.convertIndigoProperty(propertyName + "." + element)
            self.data[key] = value

    def updateLight(self, deviceName: str, propertyName: str) -> None:
        """ """
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

        for element, value in self.device.getLight(propertyName).items():
            key = self.convertIndigoProperty(propertyName + "." + element)
            self.data[key] = value

    def updateBLOB(self, deviceName: str, propertyName: str) -> None:
        """ """
        if self.device is None:
            return
        if deviceName != self.deviceName:
            return

    @staticmethod
    def removePrefix(text: str, prefix: str) -> str:
        """ """
        value = text[text.startswith(prefix) and len(prefix) :]
        value = value.strip()
        return value

    def updateMessage(self, device: str, text: str) -> None:
        """ """
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
        """ """
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

    def discoverDevices(self, deviceType: str) -> list:
        """ """
        self.discoverList = list()
        self.discoverType = self.INDI_TYPES.get(deviceType, 0)
        self.client.signals.defText.connect(self.addDiscoveredDevice)
        self.client.connectServer()
        sleepAndEvents(2000)
        self.client.signals.defText.disconnect(self.addDiscoveredDevice)
        self.client.disconnectServer()
        return self.discoverList
