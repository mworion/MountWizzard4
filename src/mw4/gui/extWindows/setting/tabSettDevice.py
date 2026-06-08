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
from dataclasses import fields
from functools import partial
from mw4.gui.extWindows.devicePopupW import DevicePopup
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, findIndexValue
from PySide6.QtWidgets import QListView
from typing import Any


class SettDevice:
    def __init__(self, parentW: Any) -> None:
        self.mainW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
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
                signals.deviceConnected.connect(self.deviceConnected)
                signals.deviceDisconnected.connect(self.deviceDisconnected)
        self.setupDeviceGui()

    def setupIcons(self) -> None:
        for driver in self.setupUiDriver:
            if self.setupUiDriver[driver]["uiSetup"] is not None:
                ui = self.setupUiDriver[driver]["uiSetup"]
                self.mainW.wIcon(ui, "cogs")

    def closeEvent(self) -> None:
        for driver in self.setupUiDriver:
            signals = self.app.dReg[driver].signals
            signals.deviceConnected.disconnect(self.deviceConnected)
            signals.deviceDisconnected.disconnect(self.deviceDisconnected)

    def setupDeviceGui(self) -> None:
        dropDowns = [self.setupUiDriver[driver]["uiDropDown"] for driver in self.setupUiDriver]
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(QListView())
            dropDown.addItem("device disabled")

        for entry in self.app.dReg.configurable():
            for framework in entry.run:
                if not hasattr(self.app.dReg.d[entry.name].run[framework], "config"):
                    continue
                deviceName = entry.run[framework].config.deviceName
                itemText = f"{framework} - {deviceName}"
                self.setupUiDriver[entry.name]["uiDropDown"].addItem(itemText)
            selectedFramework = entry.framework
            index = findIndexValue(self.setupUiDriver[entry.name]["uiDropDown"], selectedFramework)
            self.setupUiDriver[entry.name]["uiDropDown"].setCurrentIndex(index)

    def copyConfig(self, driverOrig: str, framework: str) -> None:
        return
        for entry in self.app.dReg.configurable():
            if entry.name == driverOrig:
                continue
            if entry.instance.framework == framework:
                self.stopDevice(driver=driverOrig)
            if entry.name not in self.driversData:
                continue
            if framework not in self.driversData[entry.name]["frameworks"]:
                continue
            for param in self.driversData[entry.name]["frameworks"][framework]:
                if param in ["deviceList", "deviceName"]:
                    continue
                source = self.driversData[driverOrig]["frameworks"][framework][param]
                self.driversData[entry.name]["frameworks"][framework][param] = source

    def processPopupResults(self) -> None:
        self.devicePopup.ui.ok.clicked.disconnect(self.processPopupResults)
        driver = self.devicePopup.returnValues.get("driver")
        if self.devicePopup.returnValues.get("indiCopyConfig", False):
            self.copyConfig(driverOrig=driver, framework="indi")
        if self.devicePopup.returnValues.get("alpacaCopyConfig", False):
            self.copyConfig(driverOrig=driver, framework="alpaca")

        name = "test"
        selectedFramework = self.driversData[driver]["framework"]
        index = findIndexValue(self.setupUiDriver[driver]["uiDropDown"], selectedFramework)
        itemText = f"{selectedFramework} - {name}"
        self.setupUiDriver[driver]["uiDropDown"].setCurrentIndex(index)
        self.setupUiDriver[driver]["uiDropDown"].setItemText(index, itemText)
        self.app.dReg.startDevice(driver)

    def callPopup(self, device: str) -> None:
        self.app.dReg.stopDevice(device)
        data = self.app.dReg.collectConfigFromSingleDevice(device)
        deviceType = self.app.dReg[device].instance.DEVICE_TYPE
        deviceClass = self.app.dReg[device].instance
        self.devicePopup = DevicePopup(
            self.mainW, parent=deviceClass, driver=device, deviceType=deviceType, data=data
        )
        self.devicePopup.initConfig()
        self.devicePopup.ui.ok.clicked.connect(self.processPopupResults)

    def dispatchDriverDropdown(self, device: str, position: int) -> None:
        dropDownEntry = self.setupUiDriver[device]["uiDropDown"].currentText()
        isDisabled = position == 0
        framework = "" if isDisabled else dropDownEntry.split("-")[0].rstrip()
        self.app.dReg[device].instance.framework = framework
        changeStyleDynamic(self.setupUiDriver[device]["uiDropDown"], "active", False)
        self.app.dReg.stopDevice(device)
        if framework:
            self.app.dReg.startDevice(device)

    def startDevice(self, device: str, auto: bool) -> None:
        self.app.dReg.startDevice(device)
        framework = self.app.dReg[device].framework
        self.msg.emit(0, "Driver", f"{framework} enabled", f"{device}")

    def stopDevice(self, device: str) -> None:
        self.app.dReg.stopDevice(device)
        framework = self.app.dReg[device].framework
        self.msg.emit(0, "Driver", f"{framework} disabled", f"{device}")

    def deviceConnected(self, device: str, deviceName: str) -> None:
        changeStyleDynamic(self.setupUiDriver[device]["uiDropDown"], "active", True)
        self.app.dReg.setStat(device, True)
        self.msg.emit(0, "Driver", "Device connected", f"{deviceName}::{device}")

    def deviceDisconnected(self, driver: str, deviceName: str) -> None:
        changeStyleDynamic(self.setupUiDriver[driver]["uiDropDown"], "active", False)
        self.app.dReg.setStat(driver, False)
        self.msg.emit(0, "Driver", "Device disconnected", f"{deviceName}::{driver}")
