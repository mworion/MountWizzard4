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
from functools import partial
from mw4.gui.extWindows.devicePopupW import DevicePopup
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, findIndexValue
from PySide6.QtWidgets import QListView
from typing import Any


class SettDevice:
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.drivers = mainW.app.dReg.drivers
        self.devicePopup = None

        self.setupUiDriver: dict[str, Any] = {
            "camera": {
                "uiDropDown": self.ui.cameraDevice,
                "uiSetup": self.ui.cameraSetup,
            },
            "cover": {
                "uiDropDown": self.ui.coverDevice,
                "uiSetup": self.ui.coverSetup,
            },
            "directWeather": {
                "uiDropDown": self.ui.directWeatherDevice,
                "uiSetup": None,
            },
            "dome": {
                "uiDropDown": self.ui.domeDevice,
                "uiSetup": self.ui.domeSetup,
            },
            "filter": {
                "uiDropDown": self.ui.filterDevice,
                "uiSetup": self.ui.filterSetup,
            },
            "focuser": {
                "uiDropDown": self.ui.focuserDevice,
                "uiSetup": self.ui.focuserSetup,
            },
            "lightPanel": {
                "uiDropDown": self.ui.lightPanelDevice,
                "uiSetup": self.ui.lightPanelSetup,
            },
            "measure": {
                "uiDropDown": self.ui.measureDevice,
                "uiSetup": None,
            },
            "plateSolve": {
                "uiDropDown": self.ui.plateSolveDevice,
                "uiSetup": self.ui.plateSolveSetup,
            },
            "power": {
                "uiDropDown": self.ui.powerDevice,
                "uiSetup": self.ui.powerSetup,
            },
            "relay": {
                "uiDropDown": self.ui.relayDevice,
                "uiSetup": self.ui.relaySetup,
            },
            "remote": {
                "uiDropDown": self.ui.remoteDevice,
                "uiSetup": None,
            },
            "seeingWeather": {
                "uiDropDown": self.ui.seeingWeatherDevice,
                "uiSetup": self.ui.seeingWeatherSetup,
            },
            "sensor1Weather": {
                "uiDropDown": self.ui.sensor1WeatherDevice,
                "uiSetup": self.ui.sensor1WeatherSetup,
            },
            "sensor2Weather": {
                "uiDropDown": self.ui.sensor2WeatherDevice,
                "uiSetup": self.ui.sensor2WeatherSetup,
            },
            "sensor3Weather": {
                "uiDropDown": self.ui.sensor3WeatherDevice,
                "uiSetup": self.ui.sensor3WeatherSetup,
            },
            "sensor4Weather": {
                "uiDropDown": self.ui.sensor4WeatherDevice,
                "uiSetup": self.ui.sensor4WeatherSetup,
            },
            "telescope": {
                "uiDropDown": self.ui.telescopeDevice,
                "uiSetup": self.ui.telescopeSetup,
            },
        }

        self.driversData = {}
        for driver in self.setupUiDriver:
            self.setupUiDriver[driver]["uiDropDown"].activated.connect(
                partial(self.dispatchDriverDropdown, driver)
            )
            if self.setupUiDriver[driver]["uiSetup"] is not None:
                ui = self.setupUiDriver[driver]["uiSetup"]
                ui.clicked.connect(partial(self.callPopup, driver))

            if hasattr(self.app.dReg[driver].instance, "signals"):
                signals = self.app.dReg[driver].instance.signals
                signals.serverDisconnected.connect(partial(self.serverDisconnected, driver))
                signals.deviceConnected.connect(partial(self.deviceConnected, driver))
                signals.deviceDisconnected.connect(partial(self.deviceDisconnected, driver))

        self.ui.ascomConnect.clicked.connect(self.manualStartAllAscomDrivers)
        self.ui.ascomDisconnect.clicked.connect(self.manualStopAllAscomDrivers)

    def addMissingFrameworksData(self, driver: str, config: dict) -> dict:
        for framework in self.app.dReg[driver].instance.run:
            if framework not in config[driver]["frameworks"]:
                entry = self.app.dReg[driver].instance.defaultConfig["frameworks"][framework]
                config[driver]["frameworks"][framework] = entry
        return config

    def addMissingDefaultData(self, config: dict) -> dict:
        for entry in self.app.dReg.configurable():
            if entry.name not in config:
                config[entry.name] = {}
                config[entry.name].update(entry.instance.defaultConfig)
                continue
            config = self.addMissingFrameworksData(entry.name, config)
        return config

    def removeUnknownDriversData(self, config: dict) -> dict:
        for driver in list(config):
            if driver not in self.app.dReg.drivers:
                del config[driver]
        return config

    def loadDriversDataFromConfig(self, config: dict) -> None:
        config = config.get("driversData", {})
        self.driversData.clear()
        config = self.addMissingDefaultData(config)
        config = self.removeUnknownDriversData(config)
        self.driversData.update(config)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.loadDriversDataFromConfig(self.app.config)
        self.ui.autoConnectASCOM.setChecked(config.get("autoConnectASCOM", False))
        self.setupDeviceGui()
        self.startDrivers()

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.app.config["driversData"] = self.driversData
        config["autoConnectASCOM"] = self.ui.autoConnectASCOM.isChecked()

    def setupIcons(self) -> None:
        for driver in self.setupUiDriver:
            if self.setupUiDriver[driver]["uiSetup"] is not None:
                ui = self.setupUiDriver[driver]["uiSetup"]
                self.mainW.wIcon(ui, "cogs")

        self.mainW.wIcon(self.ui.ascomConnect, "link")
        self.mainW.wIcon(self.ui.ascomDisconnect, "unlink")

    def setupDeviceGui(self) -> None:
        dropDowns = [self.setupUiDriver[driver]["uiDropDown"] for driver in self.setupUiDriver]
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(QListView())
            dropDown.addItem("device disabled")

        for driver in self.driversData:
            frameworks = self.driversData[driver].get("frameworks")

            if driver not in self.app.dReg.drivers:
                self.msg.emit(2, "SYSTEM", "Driver setup", f"Missing driver: [{driver}]")
                continue

            for fw in frameworks:
                name = frameworks[fw]["deviceName"]
                itemText = f"{fw} - {name}"
                self.setupUiDriver[driver]["uiDropDown"].addItem(itemText)

            framework = self.driversData[driver]["framework"]
            index = findIndexValue(self.setupUiDriver[driver]["uiDropDown"], framework)
            self.setupUiDriver[driver]["uiDropDown"].setCurrentIndex(index)

    def processPopupResults(self) -> None:
        self.devicePopup.ui.ok.clicked.disconnect(self.processPopupResults)
        driver = self.devicePopup.returnValues.get("driver")
        if self.devicePopup.returnValues.get("indiCopyConfig", False):
            self.copyConfig(driverOrig=driver, framework="indi")
        if self.devicePopup.returnValues.get("alpacaCopyConfig", False):
            self.copyConfig(driverOrig=driver, framework="alpaca")

        selectedFramework = self.driversData[driver]["framework"]
        index = findIndexValue(self.setupUiDriver[driver]["uiDropDown"], selectedFramework)
        name = self.driversData[driver]["frameworks"][selectedFramework]["deviceName"]

        if not name:
            return

        itemText = f"{selectedFramework} - {name}"
        self.setupUiDriver[driver]["uiDropDown"].setCurrentIndex(index)
        self.setupUiDriver[driver]["uiDropDown"].setItemText(index, itemText)
        self.startDriver(driver, True)

    def copyConfig(self, driverOrig: str, framework: str) -> None:
        for entry in self.app.dReg.configurable():
            if entry.name == driverOrig:
                continue
            if entry.instance.framework == framework:
                self.stopDriver(driver=driverOrig)
            if entry.name not in self.driversData:
                continue
            if framework not in self.driversData[entry.name]["frameworks"]:
                continue
            for param in self.driversData[entry.name]["frameworks"][framework]:
                if param in ["deviceList", "deviceName"]:
                    continue
                source = self.driversData[driverOrig]["frameworks"][framework][param]
                self.driversData[entry.name]["frameworks"][framework][param] = source

    def callPopup(self, driver: str) -> None:
        self.stopDriver(driver)
        data = self.driversData[driver]
        deviceType = self.app.dReg[driver].deviceType
        deviceClass = self.app.dReg[driver].instance
        self.devicePopup = DevicePopup(
            self.mainW, parent=deviceClass, driver=driver, deviceType=deviceType, data=data
        )
        self.devicePopup.initConfig()
        self.devicePopup.ui.ok.clicked.connect(self.processPopupResults)

    def stopDriver(self, driver: str) -> None:
        self.app.dReg[driver].stat = None
        framework = self.app.dReg[driver].instance.framework
        if framework not in self.app.dReg[driver].instance.run:
            return

        driverClass = self.app.dReg[driver].instance
        if driverClass.run[framework].deviceName != "":
            driverClass.stopCommunication()
            driverClass.data.clear()
            driverClass.run[framework].deviceName = ""
            self.msg.emit(0, "Driver", f"{framework.upper()} disabled", f"{driver}")

        changeStyleDynamic(self.setupUiDriver[driver]["uiDropDown"], "active", False)
        self.app.dReg[driver].stat = None

    def stopDrivers(self) -> None:
        for entry in self.app.dReg.configurable():
            self.stopDriver(driver=entry.name)

    def configDriver(self, driver: str) -> None:
        self.app.dReg[driver].stat = False
        framework = self.driversData[driver]["framework"]
        if framework not in self.app.dReg[driver].instance.run:
            return

        frameworkConfig = self.driversData[driver]["frameworks"][framework]
        driverClass = self.app.dReg[driver].instance.run[framework]
        for attribute in frameworkConfig:
            setattr(driverClass, attribute, frameworkConfig[attribute])

    def startDriver(self, driver: str, autoStart: bool = False) -> None:
        data = self.driversData[driver]
        framework = data["framework"]
        if framework not in self.app.dReg[driver].instance.run:
            return

        driverClass = self.app.dReg[driver].instance
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
        for entry in self.app.dReg.configurable():
            if entry.name not in self.driversData:
                continue
            if self.driversData[entry.name]["framework"] == "":
                continue
            isAscomAutoConnect = self.ui.autoConnectASCOM.isChecked()
            isAscom = self.driversData[entry.name]["framework"] in ["ascom", "alpaca"]
            autostart = isAscomAutoConnect and isAscom or not isAscom
            self.startDriver(entry.name, autostart)

    def manualStopAllAscomDrivers(self) -> None:
        for entry in self.app.dReg.configurable():
            if entry.name not in self.driversData:
                continue
            if self.driversData[entry.name]["framework"] in ["ascom", "alpaca"]:
                self.stopDriver(entry.name)

    def manualStartAllAscomDrivers(self) -> None:
        for entry in self.app.dReg.configurable():
            if entry.name not in self.driversData:
                continue
            if self.driversData[entry.name]["framework"] in ["ascom", "alpaca"]:
                self.startDriver(entry.name, True)

    def dispatchDriverDropdown(self, driver: str, position: int) -> None:
        dropDownEntry = self.setupUiDriver[driver]["uiDropDown"].currentText()
        isDisabled = position == 0
        framework = "" if isDisabled else dropDownEntry.split("-")[0].rstrip()

        self.driversData[driver]["framework"] = framework
        self.stopDriver(driver)
        if framework:
            self.startDriver(driver, True)

    def serverDisconnected(self, driver: str, deviceList: list) -> None:
        self.msg.emit(0, "Driver", "Server disconnected", f"{driver}")

    def deviceConnected(self, driver: str, deviceName: str) -> None:
        changeStyleDynamic(self.setupUiDriver[driver]["uiDropDown"], "active", True)
        self.app.dReg[driver].stat = True
        self.msg.emit(0, "Driver", "Device connected", f"{deviceName}::{driver}")

        data = self.driversData[driver]
        framework = data["framework"]
        if data["frameworks"][framework].get("loadConfig", False):
            self.msg.emit(0, "Driver", "Config loaded", f"{deviceName}::{driver}")

    def deviceDisconnected(self, driver: str, deviceName: str) -> None:
        changeStyleDynamic(self.setupUiDriver[driver]["uiDropDown"], "active", False)
        self.app.dReg[driver].stat = False
        self.msg.emit(0, "Driver", "Device disconnected", f"{deviceName}::{driver}")
