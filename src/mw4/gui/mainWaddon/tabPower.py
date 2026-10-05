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
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.nativeQt.qtInputDialog import MWInputDialog
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, clickable, guiSetText
from mw4.mountcontrol.convert import valueToInt
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow


class Power(TabAddon):
    def __init__(self, mainW: "MainWindow") -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.powerOnOFF = {
            "1": self.ui.powerPort1,
            "2": self.ui.powerPort2,
            "3": self.ui.powerPort3,
            "4": self.ui.powerPort4,
        }
        self.dewCycle = {
            "1": self.ui.dewCycle1,
            "2": self.ui.dewCycle2,
            "3": self.ui.dewCycle3,
        }
        self.dewLabel = {
            "1": self.ui.groupDew1,
            "2": self.ui.groupDew2,
            "3": self.ui.groupDew3,
        }
        self.current = {
            "1": self.ui.powerCurrent1,
            "2": self.ui.powerCurrent2,
            "3": self.ui.powerCurrent3,
            "4": self.ui.powerCurrent4,
        }
        self.powerLabel = {
            "1": self.ui.powerLabel1,
            "2": self.ui.powerLabel2,
            "3": self.ui.powerLabel3,
            "4": self.ui.powerLabel4,
        }
        self.portUSB = {
            "1": self.ui.portUSB1,
            "2": self.ui.portUSB2,
            "3": self.ui.portUSB3,
            "4": self.ui.portUSB4,
            "5": self.ui.portUSB5,
            "6": self.ui.portUSB6,
        }

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

    def setGuiVersion(self, version=1) -> None:
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
        for name, button in self.powerOnOFF.items():
            value = self.app.dReg["power"].data.get(
                f"POWER_CHANNELS.POWER_CHANNEL_{name}", False
            )
            changeStyleDynamic(button, "run", value)

        for name, button in self.current.items():
            value = self.app.dReg["power"].data.get(f"POWER_CURRENTS.POWER_CHANNEL_{name}")
            guiSetText(button, "4.2f", value)

        for name, button in self.dewCycle.items():
            value = self.app.dReg["power"].data.get(f"DEW_DUTY_CYCLES.DEW_CHANNEL_{name}")
            guiSetText(button, "3.0f", value)

        for name, button in self.dewLabel.items():
            value = self.app.dReg["power"].data.get(f"DEW_LABELS.DEW_CHANNEL_{name}", "")
            button.setTitle(f"{value:1s}")

        for name, button in self.powerLabel.items():
            value = self.app.dReg["power"].data.get(
                f"POWER_LABELS.POWER_CHANNEL_{name}", f"Power {name}"
            )
            button.setText(value)

        value = self.app.dReg["power"].data.get("POWER_CONSUMPTION.CONSUMPTION_AVG_AMPS")
        guiSetText(self.ui.consumptionAvgAmps, "4.2f", value)
        value = self.app.dReg["power"].data.get("POWER_CONSUMPTION.CONSUMPTION_AMP_HOURS")
        guiSetText(self.ui.consumptionAmpHours, "4.2f", value)
        value = self.app.dReg["power"].data.get("POWER_CONSUMPTION.CONSUMPTION_WATT_HOURS")
        guiSetText(self.ui.consumptionWattHours, "4.2f", value)

        value = self.app.dReg["power"].data.get("POWER_SENSORS.SENSOR_VOLTAGE")
        guiSetText(self.ui.sensorVoltage, "4.1f", value)
        value = self.app.dReg["power"].data.get("POWER_SENSORS.SENSOR_CURRENT")
        guiSetText(self.ui.sensorCurrent, "4.2f", value)
        value = self.app.dReg["power"].data.get("POWER_SENSORS.SENSOR_POWER")
        guiSetText(self.ui.sensorPower, "4.2f", value)

        value = self.app.dReg["power"].data.get("DEW_CURRENT.DEW_CHANNEL_1")
        guiSetText(self.ui.dewCurrent1, "4.2f", value)
        value = self.app.dReg["power"].data.get("DEW_CURRENT.DEW_CHANNEL_2")
        guiSetText(self.ui.dewCurrent2, "4.2f", value)
        value = self.app.dReg["power"].data.get("DEW_CURRENT.DEW_CHANNEL_3")
        guiSetText(self.ui.dewCurrent3, "4.2f", value)

        if self.app.dReg["power"].data.get("FIRMWARE_INFO.VERSION", "1.4") > "1.4":
            value = self.app.dReg["power"].data.get(
                "VARIABLE_VOLTAGES.VAR_CHANNEL_1"
            )
            guiSetText(self.ui.adjustableOutput, "4.1f", value)

            for name, button in self.portUSB.items():
                value = self.app.dReg["power"].data.get(f"USB_PORTS.USB_PORT_{name}", False)
                changeStyleDynamic(button, "run", value)

        else:
            value = self.app.dReg["power"].data.get("USB_HUB_CONTROL.INDI_ENABLED", False)
            changeStyleDynamic(self.ui.hubUSB, "run", value)

    def setDewCycle(self, name: str, widget) -> bool:
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
        return self.app.dReg["power"].instance.sendDew(name, value)

    def togglePowerPort(self, name: str) -> bool:
        return self.app.dReg["power"].instance.togglePowerPort(name)

    def toggleHubUSB(self) -> bool:
        return self.app.dReg["power"].instance.toggleHubUSB()

    def togglePortUSB(self, name: str) -> bool:
        return self.app.dReg["power"].instance.togglePortUSB(name)

    def setAdjustableOutput(self) -> bool:
        actValue = float(self.ui.adjustableOutput.text())
        value, ok = MWInputDialog.getDouble(
            self.mainW, "Set Voltage Output", "Value (3-12):", actValue, 3, 12, 1
        )

        if not ok:
            return False

        return self.app.dReg["power"].instance.sendAdjustableOutput(value=value)

    def rebootUPB(self) -> bool:
        return self.app.dReg["power"].instance.reboot()
