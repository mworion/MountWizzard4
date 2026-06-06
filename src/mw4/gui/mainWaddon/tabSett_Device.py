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
from mw4.logic.driverHandling.driverHandling import DriverHandling
from PySide6.QtWidgets import QListView
from typing import Any


class SettDevice:
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.driversData = {}
        self.dHandling = DriverHandling(mainW.app.dReg, self.driversData)
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

        for driver in self.setupUiDriver:
            self.setupUiDriver[driver]["uiDropDown"].activated.connect(
                partial(self.dispatchDriverDropdown, driver)
            )
            if self.setupUiDriver[driver]["uiSetup"] is not None:
                ui = self.setupUiDriver[driver]["uiSetup"]
                ui.clicked.connect(partial(self.callPopup, driver))

            if hasattr(self.app.dReg[driver].instance, "signals"):
                signals = self.app.dReg[driver].signals
                signals.serverDisconnected.connect(partial(self.serverDisconnected, driver))
                signals.deviceConnected.connect(partial(self.deviceConnected, driver))
                signals.deviceDisconnected.connect(partial(self.deviceDisconnected, driver))

        self.ui.ascomConnect.clicked.connect(self.dHandling.manualStartAllAscomDrivers)
        self.ui.ascomDisconnect.clicked.connect(self.dHandling.manualStopAllAscomDrivers)

    def initConfig(self) -> None:
        config = self.app.config["WindowSetting"]
        self.dHandling.loadDriversDataFromConfig(self.app.config)
        self.ui.autoConnectASCOM.setChecked(config.get("autoConnectASCOM", False))
        self.setupDeviceGui()
        self.startDrivers()

    def storeConfig(self) -> None:
        config = self.app.config["WindowSetting"]
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

    def dispatchDriverDropdown(self, driver: str, position: int) -> None:
        dropDownEntry = self.setupUiDriver[driver]["uiDropDown"].currentText()
        isDisabled = position == 0
        framework = "" if isDisabled else dropDownEntry.split("-")[0].rstrip()

        self.driversData[driver]["framework"] = framework
        changeStyleDynamic(self.setupUiDriver[driver]["uiDropDown"], "active", False)
        self.stopDriver(driver)
        if framework:
            self.startDriver(driver, True)

    def startDrivers(self) -> None:
        autoConnect = self.ui.autoConnectASCOM.isChecked()
        self.dHandling.startDrivers(autoConnect)

    def stopDrivers(self) -> None:
        self.dHandling.stopDrivers()

    def startDriver(self, driver: str, auto: bool) -> None:
        self.dHandling.startDriver(driver)
        framework = self.app.dReg[driver].instance.framework
        self.msg.emit(0, "Driver", f"{framework} enabled", f"{driver}")

    def stopDriver(self, driver: str) -> None:
        self.dHandling.stopDriver(driver)
        framework = self.app.dReg[driver].instance.framework
        self.msg.emit(0, "Driver", f"{framework} disabled", f"{driver}")

    def serverDisconnected(self, driver: str, deviceList: list) -> None:
        self.msg.emit(0, "Driver", "Server disconnected", f"{driver}")

    def deviceConnected(self, driver: str, deviceName: str) -> None:
        changeStyleDynamic(self.setupUiDriver[driver]["uiDropDown"], "active", True)
        self.app.dReg.setStat(driver, True)
        self.msg.emit(0, "Driver", "Device connected", f"{deviceName}::{driver}")

        data = self.driversData[driver]
        framework = data["framework"]
        if data["frameworks"][framework].get("loadConfig", False):
            self.msg.emit(0, "Driver", "Config loaded", f"{deviceName}::{driver}")

    def deviceDisconnected(self, driver: str, deviceName: str) -> None:
        changeStyleDynamic(self.setupUiDriver[driver]["uiDropDown"], "active", False)
        self.app.dReg.setStat(driver, False)
        self.msg.emit(0, "Driver", "Device disconnected", f"{deviceName}::{driver}")
