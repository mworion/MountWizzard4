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
from functools import partial

# external packages
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QListView

# local import
from gui.extWindows.devicePopupW import DevicePopup
from gui.utilities.toolsQtWidget import changeStyleDynamic, findIndexValue


class SettDevice(QObject):
    """
    devices types in self.drivers are name related to ascom definitions

    architecture:
    - all properties are stored in the config dict as main source.
    - when starting, all gui elements will be populated based on the entries of config
    - all drivers were initialised with the content of config dict
    - if we setup a new device, data of device is gathered for the popup from config
    - when closing the popup, result data will be stored in config
    - if there is no default data for a driver in config dict, it will be retrieved from the
      driver

    sequence standard:
        loading config dict
        load driver default setup from driver if not present in config
        initialize gui
        initialize driver
        start drivers

    sequence popup:
        initialize popup data
        call popup modal
        popup close
        if cancel -> finished
        store data in config
        stop changed driver
        start new driver

    sequence dropdown:
        search driver
        if no driver -> finished
        stop changed driver
        if driver = "device disabled" -> finished
        start new driver
    """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.devicePopup = None

        self.drivers = {
            "dome": {
                "uiDropDown": self.ui.domeDevice,
                "uiSetup": self.ui.domeSetup,
                "class": self.app.dome,
                "deviceType": "dome",
            },
            "cover": {
                "uiDropDown": self.ui.coverDevice,
                "uiSetup": self.ui.coverSetup,
                "class": self.app.cover,
                "deviceType": "covercalibrator",
            },
            "camera": {
                "uiDropDown": self.ui.cameraDevice,
                "uiSetup": self.ui.cameraSetup,
                "class": self.app.camera,
                "deviceType": "camera",
            },
            "filter": {
                "uiDropDown": self.ui.filterDevice,
                "uiSetup": self.ui.filterSetup,
                "class": self.app.filter,
                "deviceType": "filterwheel",
            },
            "focuser": {
                "uiDropDown": self.ui.focuserDevice,
                "uiSetup": self.ui.focuserSetup,
                "class": self.app.focuser,
                "deviceType": "focuser",
            },
            "sensor1Weather": {
                "uiDropDown": self.ui.sensor1WeatherDevice,
                "uiSetup": self.ui.sensor1WeatherSetup,
                "class": self.app.sensor1Weather,
                "deviceType": "observingconditions",
            },
            "sensor2Weather": {
                "uiDropDown": self.ui.sensor2WeatherDevice,
                "uiSetup": self.ui.sensor2WeatherSetup,
                "class": self.app.sensor2Weather,
                "deviceType": "observingconditions",
            },
            "sensor3Weather": {
                "uiDropDown": self.ui.sensor3WeatherDevice,
                "uiSetup": self.ui.sensor3WeatherSetup,
                "class": self.app.sensor3Weather,
                "deviceType": "observingconditions",
            },
            "onlineWeather": {
                "uiDropDown": self.ui.onlineWeatherDevice,
                "uiSetup": self.ui.onlineWeatherSetup,
                "class": self.app.onlineWeather,
                "deviceType": "observingconditions",
            },
            "directWeather": {
                "uiDropDown": self.ui.directWeatherDevice,
                "uiSetup": None,
                "class": self.app.directWeather,
                "deviceType": None,
            },
            "seeingWeather": {
                "uiDropDown": self.ui.seeingWeatherDevice,
                "uiSetup": self.ui.seeingWeatherSetup,
                "class": self.app.seeingWeather,
                "deviceType": "observingconditions",
            },
            "telescope": {
                "uiDropDown": self.ui.telescopeDevice,
                "uiSetup": self.ui.telescopeSetup,
                "class": self.app.telescope,
                "deviceType": "telescope",
            },
            "power": {
                "uiDropDown": self.ui.powerDevice,
                "uiSetup": self.ui.powerSetup,
                "class": self.app.power,
                "deviceType": "switch",
            },
            "relay": {
                "uiDropDown": self.ui.relayDevice,
                "uiSetup": self.ui.relaySetup,
                "class": self.app.relay,
                "deviceType": None,
            },
            "plateSolve": {
                "uiDropDown": self.ui.plateSolveDevice,
                "uiSetup": self.ui.plateSolveSetup,
                "class": self.app.plateSolve,
                "deviceType": "plateSolve",
            },
            "remote": {
                "uiDropDown": self.ui.remoteDevice,
                "uiSetup": None,
                "class": self.app.remote,
                "deviceType": None,
            },
            "measure": {
                "uiDropDown": self.ui.measureDevice,
                "uiSetup": None,
                "class": self.app.measure,
                "deviceType": None,
            },
        }

        self.driversData = {}

        for driver in self.drivers:
            self.drivers[driver]["uiDropDown"].activated.connect(
                partial(self.dispatchDriverDropdown, driver)
            )
            if self.drivers[driver]["uiSetup"] is not None:
                ui = self.drivers[driver]["uiSetup"]
                ui.clicked.connect(partial(self.callPopup, driver))

            if hasattr(self.drivers[driver]["class"], "signals"):
                signals = self.drivers[driver]["class"].signals
                signals.serverDisconnected.connect(partial(self.serverDisconnected, driver))
                signals.deviceConnected.connect(partial(self.deviceConnected, driver))
                signals.deviceDisconnected.connect(partial(self.deviceDisconnected, driver))

        self.ui.ascomConnect.clicked.connect(self.manualStartAllAscomDrivers)
        self.ui.ascomDisconnect.clicked.connect(self.manualStopAllAscomDrivers)

    def setDefaultData(self, driver: str, config: dict) -> None:
        """ """
        config[driver] = {}
        defaultConfig = self.drivers[driver]["class"].defaultConfig
        config[driver].update(defaultConfig)

    def loadDriversDataFromConfig(self, config: dict) -> None:
        """ """
        config = config.get("driversData", {})
        self.driversData.clear()

        # adding default for missing drivers
        for driver in self.drivers:
            if driver not in config:
                self.setDefaultData(driver, config)

        # remove unknown drivers from data
        for driver in list(config):
            if driver not in self.drivers:
                del config[driver]

        self.driversData.update(config)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.loadDriversDataFromConfig(self.app.config)
        self.ui.autoConnectASCOM.setChecked(config.get("autoConnectASCOM", False))
        self.setupDeviceGui()
        self.startDrivers()

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.app.config["driversData"] = self.driversData
        config["autoConnectASCOM"] = self.ui.autoConnectASCOM.isChecked()

    def setupIcons(self) -> None:
        """ """
        for driver in self.drivers:
            if self.drivers[driver]["uiSetup"] is not None:
                ui = self.drivers[driver]["uiSetup"]
                self.mainW.wIcon(ui, "cogs")

        self.mainW.wIcon(self.ui.ascomConnect, "link")
        self.mainW.wIcon(self.ui.ascomDisconnect, "unlink")

    def setupDeviceGui(self) -> None:
        """ """
        dropDowns = [self.drivers[driver]["uiDropDown"] for driver in self.drivers]
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(QListView())
            dropDown.addItem("device disabled")

        for driver in self.driversData:
            frameworks = self.driversData[driver].get("frameworks")

            if driver not in self.drivers:
                self.msg.emit(2, "SYSTEM", "Driver setup", f"Missing driver: [{driver}]")
                continue

            for fw in frameworks:
                name = frameworks[fw]["deviceName"]
                itemText = f"{fw} - {name}"
                self.drivers[driver]["uiDropDown"].addItem(itemText)

            framework = self.driversData[driver]["framework"]
            index = findIndexValue(self.drivers[driver]["uiDropDown"], framework)
            self.drivers[driver]["uiDropDown"].setCurrentIndex(index)

    def processPopupResults(self) -> None:
        """ """
        self.devicePopup.ui.ok.clicked.disconnect(self.processPopupResults)
        driver = self.devicePopup.returnValues.get("driver")
        if self.devicePopup.returnValues.get("indiCopyConfig", False):
            self.copyConfig(driverOrig=driver, framework="indi")
        if self.devicePopup.returnValues.get("alpacaCopyConfig", False):
            self.copyConfig(driverOrig=driver, framework="alpaca")

        selectedFramework = self.driversData[driver]["framework"]
        index = findIndexValue(self.drivers[driver]["uiDropDown"], selectedFramework)
        name = self.driversData[driver]["frameworks"][selectedFramework]["deviceName"]

        if not name:
            return

        itemText = f"{selectedFramework} - {name}"
        self.drivers[driver]["uiDropDown"].setCurrentIndex(index)
        self.drivers[driver]["uiDropDown"].setItemText(index, itemText)

        self.stopDriver(driver)
        self.startDriver(driver, True)

    def copyConfig(self, driverOrig: str, framework: str) -> None:
        """ """
        for driverDest in self.drivers:
            if driverDest == driverOrig:
                continue

            driverClass = self.drivers[driverDest]["class"]

            if driverClass.framework == framework:
                self.stopDriver(driver=driverOrig)
            if driverDest not in self.driversData:
                continue
            if framework not in self.driversData[driverDest]["frameworks"]:
                continue
            for param in self.driversData[driverDest]["frameworks"][framework]:
                if param in ["deviceList", "deviceName"]:
                    continue

                source = self.driversData[driverOrig]["frameworks"][framework][param]
                self.driversData[driverDest]["frameworks"][framework][param] = source

    def callPopup(self, driver: str) -> None:
        """ """
        data = self.driversData[driver]
        deviceType = self.drivers[driver]["deviceType"]
        deviceClass = self.drivers[driver]["class"]
        self.devicePopup = DevicePopup(
            self.mainW, parent=deviceClass, driver=driver, deviceType=deviceType, data=data
        )
        self.devicePopup.ui.ok.clicked.connect(self.processPopupResults)

    def stopDriver(self, driver: str) -> None:
        """ """
        self.app.deviceStat[driver] = None
        framework = self.drivers[driver]["class"].framework
        if framework not in self.drivers[driver]["class"].run:
            return

        driverClass = self.drivers[driver]["class"]
        if driverClass.run[framework].deviceName != "":
            driverClass.stopCommunication()
            driverClass.data.clear()
            driverClass.run[framework].deviceName = ""
            self.msg.emit(0, "Driver", f"{framework.upper()} disabled", f"{driver}")

        changeStyleDynamic(self.drivers[driver]["uiDropDown"], "active", False)
        self.app.deviceStat[driver] = None

    def stopDrivers(self) -> None:
        """ """
        for driver in self.drivers:
            self.stopDriver(driver=driver)

    def configDriver(self, driver: str) -> None:
        """ """
        self.app.deviceStat[driver] = False
        framework = self.driversData[driver]["framework"]
        if framework not in self.drivers[driver]["class"].run:
            return

        frameworkConfig = self.driversData[driver]["frameworks"][framework]
        driverClass = self.drivers[driver]["class"].run[framework]
        for attribute in frameworkConfig:
            setattr(driverClass, attribute, frameworkConfig[attribute])

    def startDriver(self, driver: str, autoStart: bool = False) -> None:
        """ """
        data = self.driversData[driver]
        framework = data["framework"]
        if framework not in self.drivers[driver]["class"].run:
            return

        driverClass = self.drivers[driver]["class"]
        loadConfig = data["frameworks"][framework].get("loadConfig", False)
        updateRate = data["frameworks"][framework].get("updateRate", 1000)
        driverClass.updateRate = updateRate
        driverClass.loadConfig = loadConfig
        driverClass.framework = framework

        self.configDriver(driver)
        if autoStart:
            driverClass.startCommunication()

        self.msg.emit(0, "Driver", f"{framework.upper()} enabled", f"{driver}")

    def startDrivers(self) -> None:
        """ """
        for driver in self.drivers:
            if driver not in self.driversData:
                continue
            if self.driversData[driver]["framework"] == "":
                continue

            isAscomAutoConnect = self.ui.autoConnectASCOM.isChecked()
            isAscom = self.driversData[driver]["framework"] in ["ascom", "alpaca"]
            autostart = isAscomAutoConnect and isAscom or not isAscom
            self.startDriver(driver, autostart)

    def manualStopAllAscomDrivers(self) -> None:
        """ """
        for driver in self.drivers:
            if driver not in self.driversData:
                continue

            if self.driversData[driver]["framework"] in ["ascom", "alpaca"]:
                self.stopDriver(driver)

    def manualStartAllAscomDrivers(self) -> None:
        """ """
        for driver in self.drivers:
            if driver not in self.driversData:
                continue

            if self.driversData[driver]["framework"] in ["ascom", "alpaca"]:
                self.startDriver(driver, True)

    def dispatchDriverDropdown(self, driver: str, position: int) -> None:
        """ """
        dropDownEntry = self.drivers[driver]["uiDropDown"].currentText()
        isDisabled = position == 0
        framework = "" if isDisabled else dropDownEntry.split("-")[0].rstrip()

        self.driversData[driver]["framework"] = framework
        self.stopDriver(driver)
        if framework:
            self.startDriver(driver, True)

    def serverDisconnected(self, driver: str, deviceList: list) -> None:
        """ """
        self.msg.emit(0, "Driver", "Server disconnected", f"{driver}")

    def deviceConnected(self, driver: str, deviceName: str) -> None:
        """ """
        changeStyleDynamic(self.drivers[driver]["uiDropDown"], "active", True)
        self.app.deviceStat[driver] = True
        self.msg.emit(0, "Driver", "Device connected", f"{deviceName}::{driver}")

        data = self.driversData[driver]
        framework = data["framework"]
        if data["frameworks"][framework].get("loadConfig", False):
            self.msg.emit(0, "Driver", "Config loaded", f"{deviceName}::{driver}")

    def deviceDisconnected(self, driver: str, deviceName: str) -> None:
        """ """
        changeStyleDynamic(self.drivers[driver]["uiDropDown"], "active", False)
        self.app.deviceStat[driver] = False
        self.msg.emit(0, "Driver", "Device disconnected", f"{deviceName}::{driver}")
