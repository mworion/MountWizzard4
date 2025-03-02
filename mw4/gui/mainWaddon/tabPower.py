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

# external packages
from functools import partial
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import QObject
from mountcontrol.convert import valueToInt

# local import
from gui.utilities.toolsQtWidget import changeStyleDynamic, guiSetText, clickable


class Power(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
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
        self.powerBoot = {
            "1": self.ui.powerBootPort1,
            "2": self.ui.powerBootPort2,
            "3": self.ui.powerBootPort3,
            "4": self.ui.powerBootPort4,
        }
        self.dew = {
            "A": self.ui.dewA,
            "B": self.ui.dewB,
            "C": self.ui.dewC,
        }
        self.dewLabel = {
            1: self.ui.groupDewA,
            2: self.ui.groupDewB,
            3: self.ui.groupDewC,
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
        self.ui.autoDew.clicked.connect(self.toggleAutoDew)
        self.ui.rebootUPB.clicked.connect(self.rebootUPB)
        clickable(self.ui.adjustableOutput).connect(self.setAdjustableOutput)

        # setting gui elements
        for name, button in self.dew.items():
            clickable(button).connect(partial(self.setDew, name))
        for name, button in self.powerOnOFF.items():
            button.clicked.connect(partial(self.togglePowerPort, name))
        for name, button in self.powerBoot.items():
            button.clicked.connect(partial(self.togglePowerBootPort, name))
        for name, button in self.portUSB.items():
            button.clicked.connect(partial(self.togglePortUSB, name))

        # functional signals
        self.app.power.signals.version.connect(self.setGuiVersion)

        # cyclic tasks
        self.app.update1s.connect(self.updatePowerGui)

    def setGuiVersion(self, version=1) -> None:
        """ """
        if version == 1:
            self.ui.groupDewC.setVisible(False)
            self.ui.groupPortUSB.setVisible(False)
            self.ui.groupHubUSB.setVisible(True)
            self.ui.groupAdjustableOutput.setVisible(False)
        elif version == 2:
            self.ui.groupDewC.setVisible(True)
            self.ui.groupPortUSB.setVisible(True)
            self.ui.groupHubUSB.setVisible(False)
            self.ui.groupAdjustableOutput.setVisible(True)

    def updatePowerGui(self) -> None:
        """ """
        for name, button in self.powerOnOFF.items():
            value = self.app.power.data.get(f"POWER_CONTROL.POWER_CONTROL_{name}", False)
            changeStyleDynamic(button, "running", value)

        for name, button in self.powerBoot.items():
            value = self.app.power.data.get(f"POWER_ON_BOOT.POWER_PORT_{name}", False)
            button.setChecked(value)

        for name, button in self.current.items():
            value = self.app.power.data.get(f"POWER_CURRENT.POWER_CURRENT_{name}")
            guiSetText(button, "4.2f", value)

        for name, button in self.dew.items():
            value = self.app.power.data.get(f"DEW_PWM.DEW_{name}")
            guiSetText(button, "3.0f", value)

        for name, button in self.dewLabel.items():
            value = self.app.power.data.get(f"DEW_CONTROL_LABEL.DEW_LABEL_{name}", "")
            button.setTitle(f"{value:1s}")

        for name, button in self.powerLabel.items():
            value = self.app.power.data.get(
                f"POWER_CONTROL_LABEL.POWER_LABEL_{name}", f"Power {name}"
            )
            button.setText(value)

        value = self.app.power.data.get("POWER_CONSUMPTION.CONSUMPTION_AVG_AMPS")
        guiSetText(self.ui.consumptionAvgAmps, "4.2f", value)
        value = self.app.power.data.get("POWER_CONSUMPTION.CONSUMPTION_AMP_HOURS")
        guiSetText(self.ui.consumptionAmpHours, "4.2f", value)
        value = self.app.power.data.get("POWER_CONSUMPTION.CONSUMPTION_WATT_HOURS")
        guiSetText(self.ui.consumptionWattHours, "4.2f", value)

        value = self.app.power.data.get("POWER_SENSORS.SENSOR_VOLTAGE")
        guiSetText(self.ui.sensorVoltage, "4.1f", value)
        value = self.app.power.data.get("POWER_SENSORS.SENSOR_CURRENT")
        guiSetText(self.ui.sensorCurrent, "4.2f", value)
        value = self.app.power.data.get("POWER_SENSORS.SENSOR_POWER")
        guiSetText(self.ui.sensorPower, "4.2f", value)

        value = self.app.power.data.get("DEW_CURRENT.DEW_CURRENT_A")
        guiSetText(self.ui.dewCurrentA, "4.2f", value)
        value = self.app.power.data.get("DEW_CURRENT.DEW_CURRENT_B")
        guiSetText(self.ui.dewCurrentB, "4.2f", value)
        value = self.app.power.data.get("DEW_CURRENT.DEW_CURRENT_C")
        guiSetText(self.ui.dewCurrentC, "4.2f", value)

        value1 = self.app.power.data.get("AUTO_DEW.INDI_ENABLED", False)
        value2 = self.app.power.data.get("AUTO_DEW.DEW_A", False)
        value3 = self.app.power.data.get("AUTO_DEW.DEW_B", False)
        value4 = self.app.power.data.get("AUTO_DEW.DEW_C", False)
        value = value1 or value2 or value3 or value4
        changeStyleDynamic(self.ui.autoDew, "running", value)

        if self.app.power.data.get("FIRMWARE_INFO.VERSION", "1.4") > "1.4":
            value = self.app.power.data.get("ADJUSTABLE_VOLTAGE.ADJUSTABLE_VOLTAGE_VALUE")
            guiSetText(self.ui.adjustableOutput, "4.1f", value)

            for name, button in self.portUSB.items():
                value = self.app.power.data.get(f"USB_PORT_CONTROL.PORT_{name}", False)
                changeStyleDynamic(button, "running", value)

        else:
            value = self.app.power.data.get("USB_HUB_CONTROL.INDI_ENABLED", False)
            changeStyleDynamic(self.ui.hubUSB, "running", value)

    def setDew(self, name: str) -> bool:
        """ """
        actValue = valueToInt(self.dew[name].text())
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self,
            f"Set dew PWM {name}",
            "Value (0-100):",
            actValue,
            0,
            100,
            10,
        )
        if not ok:
            return False
        return self.app.power.sendDew(name, value)

    def togglePowerPort(self, name: str) -> bool:
        """ """
        return self.app.power.togglePowerPort(name)

    def togglePowerBootPort(self, name: str) -> bool:
        """ """
        return self.app.power.togglePowerPortBoot(name)

    def toggleHubUSB(self) -> bool:
        """ """
        return self.app.power.toggleHubUSB()

    def togglePortUSB(self, name: str) -> bool:
        """ """
        return self.app.power.togglePortUSB(name)

    def toggleAutoDew(self) -> bool:
        """ """
        return self.app.power.toggleAutoDew()

    def setAdjustableOutput(self) -> bool:
        """ """
        actValue = float(self.ui.adjustableOutput.text())
        dlg = QInputDialog()
        value, ok = dlg.getDouble(
            self, "Set Voltage Output", "Value (3-12):", actValue, 3, 12, 1
        )

        if not ok:
            return False

        return self.app.power.sendAdjustableOutput(value=value)

    def rebootUPB(self) -> bool:
        """ """
        return self.app.power.reboot()
