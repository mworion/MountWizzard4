# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from functools import partial
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.nativeQt.qtInputDialog import MWInputDialog
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, clickable, guiSetText
from mw4.mountcontrol.convert import valueToFloat, valueToInt
from PySide6.QtWidgets import QWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow


class Power(TabAddon):
    def __init__(self, mainW: "MainWindow") -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.version: int = 1
        self.powerOnOFF = {str(i): getattr(self.ui, f"powerPort{i}") for i in range(1, 5)}
        self.dewCycle = {str(i): getattr(self.ui, f"dewCycle{i}") for i in range(1, 4)}
        self.dewLabel = {str(i): getattr(self.ui, f"groupDew{i}") for i in range(1, 4)}
        self.current = {str(i): getattr(self.ui, f"powerCurrent{i}") for i in range(1, 5)}
        self.powerLabel = {str(i): getattr(self.ui, f"powerLabel{i}") for i in range(1, 5)}
        self.portUSB = {str(i): getattr(self.ui, f"portUSB{i}") for i in range(1, 7)}
        self.valueFields = [
            (self.ui.consumptionAvgAmps, "POWER_CONSUMPTION.CONSUMPTION_AVG_AMPS", "4.2f"),
            (self.ui.consumptionAmpHours, "POWER_CONSUMPTION.CONSUMPTION_AMP_HOURS", "4.2f"),
            (self.ui.consumptionWattHours, "POWER_CONSUMPTION.CONSUMPTION_WATT_HOURS", "4.2f"),
            (self.ui.sensorVoltage, "POWER_SENSORS.SENSOR_VOLTAGE", "4.1f"),
            (self.ui.sensorCurrent, "POWER_SENSORS.SENSOR_CURRENT", "4.2f"),
            (self.ui.sensorPower, "POWER_SENSORS.SENSOR_POWER", "4.2f"),
            (self.ui.dewCurrent1, "DEW_CURRENT.DEW_CHANNEL_1", "4.2f"),
            (self.ui.dewCurrent2, "DEW_CURRENT.DEW_CHANNEL_2", "4.2f"),
            (self.ui.dewCurrent3, "DEW_CURRENT.DEW_CHANNEL_3", "4.2f"),
        ]

        # gui tasks
        self.ui.hubUSB.clicked.connect(self.toggleHubUSB)
        self.ui.rebootUPB.clicked.connect(self.rebootUPB)
        clickable(self.ui.adjustableOutput).connect(self.setAdjustableOutput)

        # setting gui elements
        for name, button in self.dewCycle.items():
            clickable(button).connect(partial(self.setDewCycle, name))
        for name, button in self.powerOnOFF.items():
            button.clicked.connect(partial(self.togglePowerPort, name))
        for name, button in self.portUSB.items():
            button.clicked.connect(partial(self.togglePortUSB, name))

        # functional signals
        self.app.dReg["power"].signals.version.connect(self.setGuiVersion)

        # cyclic tasks
        self.app.timeMgr.update1s.connect(self.updatePowerGui)

    def setGuiVersion(self, version: int = 1) -> None:
        self.version = version
        if version == 1:
            self.ui.groupDew3.setVisible(False)
            self.ui.groupPortUSB.setVisible(False)
            self.ui.groupHubUSB.setVisible(True)
            self.ui.groupAdjustableOutput.setVisible(False)
        elif version == 2:
            self.ui.groupDew3.setVisible(True)
            self.ui.groupPortUSB.setVisible(True)
            self.ui.groupHubUSB.setVisible(False)
            self.ui.groupAdjustableOutput.setVisible(True)

    def updatePowerGui(self) -> None:
        data = self.app.dReg["power"].data
        for name, button in self.powerOnOFF.items():
            value = data.get(f"POWER_CHANNELS.POWER_CHANNEL_{name}", False)
            changeStyleDynamic(button, "run", value)

        for name, button in self.current.items():
            guiSetText(button, "4.2f", data.get(f"POWER_CURRENTS.POWER_CHANNEL_{name}"))

        for name, button in self.dewCycle.items():
            guiSetText(button, "3.0f", data.get(f"DEW_DUTY_CYCLES.DEW_CHANNEL_{name}"))

        for name, button in self.dewLabel.items():
            value = data.get(f"DEW_LABELS.DEW_CHANNEL_{name}", "")
            button.setTitle(str(value))

        for name, button in self.powerLabel.items():
            value = data.get(f"POWER_LABELS.POWER_CHANNEL_{name}", f"Power {name}")
            button.setText(value)

        for widget, key, fmt in self.valueFields:
            guiSetText(widget, fmt, data.get(key))

        if self.version == 2:
            value = data.get("VARIABLE_VOLTAGES.VAR_CHANNEL_1")
            guiSetText(self.ui.adjustableOutput, "4.1f", value)
            for name, button in self.portUSB.items():
                value = data.get(f"USB_PORTS.USB_PORT_{name}", False)
                changeStyleDynamic(button, "run", value)
        else:
            value = data.get("USB_HUB_CONTROL.INDI_ENABLED", False)
            changeStyleDynamic(self.ui.hubUSB, "run", value)

    def setDewCycle(self, name: str, widget: QWidget) -> bool:
        actValue = valueToInt(self.dewCycle[name].text())
        value, ok = MWInputDialog.getInt(
            self.mainW,
            f"Set dew PWM {name}",
            "Value (0-100):",
            actValue,
            0,
            100,
            10,
        )
        if not ok:
            return False
        self.app.dReg["power"].instance.sendDew(name, value)
        return True

    def togglePowerPort(self, name: str) -> None:
        self.app.dReg["power"].instance.togglePowerPort(name)

    def toggleHubUSB(self) -> None:
        self.app.dReg["power"].instance.toggleHubUSB()

    def togglePortUSB(self, name: str) -> None:
        self.app.dReg["power"].instance.togglePortUSB(name)

    def setAdjustableOutput(self) -> bool:
        actValue = valueToFloat(self.ui.adjustableOutput.text())
        value, ok = MWInputDialog.getDouble(
            self.mainW, "Set Voltage Output", "Value (3-12):", actValue, 3, 12, 1
        )
        if not ok:
            return False
        self.app.dReg["power"].instance.sendAdjustableOutput(value=value)
        return True

    def rebootUPB(self) -> None:
        self.app.dReg["power"].instance.reboot()
