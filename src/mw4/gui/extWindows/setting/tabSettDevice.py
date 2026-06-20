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
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QListView
from typing import Any


class SettDevice(QObject):
    def __init__(self, parentW: Any) -> None:
        super().__init__()
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.devicePopup: DevicePopup | None = None
        self.signalsToName: dict[int, str] = {}

        self.deviceUi: dict[str, Any] = {
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

        for entry in self.app.dReg.configurable():
            self.deviceUi[entry.name]["uiDropDown"].activated.connect(
                partial(self.dispatchDriverDropdown, entry.name)
            )

            if self.deviceUi[entry.name]["uiSetup"] is not None:
                ui = self.deviceUi[entry.name]["uiSetup"]
                ui.clicked.connect(partial(self.callPopup, entry.name))

            if hasattr(self.app.dReg[entry.name].instance, "signals"):
                sig = self.app.dReg[entry.name].signals
                self.signalsToName[id(sig)] = entry.name
                sig.deviceConnected.connect(self.deviceConnected)
                sig.deviceDisconnected.connect(self.deviceDisconnected)

        self.setupDeviceGui()

    def setupIcons(self) -> None:
        for driver in self.deviceUi:
            if self.deviceUi[driver]["uiSetup"] is not None:
                ui = self.deviceUi[driver]["uiSetup"]
                self.parentW.wIcon(ui, "cogs")

    def closeEvent(self) -> None:
        for entry in self.app.dReg.configurable():
            if not hasattr(self.app.dReg[entry.name].instance, "signals"):
                continue
            signals = self.app.dReg[entry.name].signals
            if id(signals) not in self.signalsToName:
                continue
            signals.deviceConnected.disconnect(self.deviceConnected)
            signals.deviceDisconnected.disconnect(self.deviceDisconnected)

    def setupDeviceGui(self) -> None:
        dropDowns = [self.deviceUi[driver]["uiDropDown"] for driver in self.deviceUi]
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(QListView())
            dropDown.addItem("device disabled")

        for entry in self.app.dReg.configurable():
            for framework in entry.run:
                deviceName = entry.run[framework].config.deviceName
                itemText = f"{framework} - {deviceName}"
                self.deviceUi[entry.name]["uiDropDown"].addItem(itemText)
            index = findIndexValue(self.deviceUi[entry.name]["uiDropDown"], entry.framework)
            self.deviceUi[entry.name]["uiDropDown"].setCurrentIndex(index)
            if entry.stat:
                self.applyConnected(entry.name)
            else:
                self.applyDisconnected(entry.name)

    def copyConfig(self, device: str, framework: str) -> None:
        return
        for entry in self.app.dReg.configurable():
            if entry.name == device:
                continue
            if entry.instance.framework == framework:
                self.app.dReg.stopDevice(device)
            if entry.name not in self.driversData:
                continue
            if framework not in self.driversData[entry.name]["frameworks"]:
                continue
            for param in self.driversData[entry.name]["frameworks"][framework]:
                if param in ["deviceList", "deviceName"]:
                    continue
                source = self.driversData[device]["frameworks"][framework][param]
                self.driversData[entry.name]["frameworks"][framework][param] = source

    def processPopupResults(self) -> None:
        device = self.devicePopup.returnValues["device"]
        framework = self.devicePopup.returnValues["data"]["framework"]
        deviceName = self.devicePopup.returnValues["data"][framework]["deviceName"]
        for framework in self.devicePopup.returnValues.get("copyConfig", []):
            self.copyConfig(device, framework)
        index = findIndexValue(self.deviceUi[device]["uiDropDown"], framework)
        itemText = f"{framework} - {deviceName}"
        self.app.dReg.writeConfigToSingleDevice(device, self.devicePopup.returnValues["data"])
        self.deviceUi[device]["uiDropDown"].setCurrentIndex(index)
        self.deviceUi[device]["uiDropDown"].setItemText(index, itemText)
        self.app.startDevice.emit(device)

    def callPopup(self, device: str) -> None:
        self.app.dReg.stopDevice(device)
        data = self.app.dReg.collectConfigFromSingleDevice(device)
        self.devicePopup = DevicePopup(self.parentW, device, data)
        suc = self.devicePopup.exec()
        if suc:
            self.processPopupResults()

    def dispatchDriverDropdown(self, device: str, position: int) -> None:
        dropDownEntry = self.deviceUi[device]["uiDropDown"].currentText()
        isDisabled = position == 0
        framework = "" if isDisabled else dropDownEntry.split("-")[0].rstrip()
        if self.app.dReg[device].instance.framework != framework:
            self.app.stopDevice.emit(device)
        self.app.dReg[device].instance.framework = framework
        changeStyleDynamic(self.deviceUi[device]["uiDropDown"], "active", False)
        if not framework:
            return
        deviceName = self.app.dReg[device].run[framework].config.deviceName
        if not deviceName:
            return
        self.app.startDevice.emit(device)

    def applyConnected(self, deviceSlot: str) -> None:
        changeStyleDynamic(self.deviceUi[deviceSlot]["uiDropDown"], "active", True)

    def applyDisconnected(self, deviceSlot: str) -> None:
        changeStyleDynamic(self.deviceUi[deviceSlot]["uiDropDown"], "active", False)

    def deviceConnected(self, *_args: Any) -> None:
        name = self.signalsToName.get(id(self.sender()))
        if name is None:
            return
        self.applyConnected(name)

    def deviceDisconnected(self, *_args: Any) -> None:
        name = self.signalsToName.get(id(self.sender()))
        if name is None:
            return
        self.applyDisconnected(name)
