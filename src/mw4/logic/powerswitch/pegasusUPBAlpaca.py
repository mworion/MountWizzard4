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

from mw4.base.alpacaClass import AlpacaClass
from typing import Any


class PegasusUPBAlpaca(AlpacaClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.data = parent.data

    def pollData(self) -> None:
        model = (
            "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
        )
        self.data["FIRMWARE_INFO.VERSION"] = (
            "1.4" if model == "UPB" else "2.1"
        )
        if model == "UPB":
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=0),
                "POWER_CONTROL.POWER_CONTROL_1",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=1),
                "POWER_CONTROL.POWER_CONTROL_2",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=2),
                "POWER_CONTROL.POWER_CONTROL_3",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=3),
                "POWER_CONTROL.POWER_CONTROL_4",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=4),
                "DEW_CURRENT.DEW_CURRENT_A",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=5),
                "DEW_CURRENT.DEW_CURRENT_B",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=6),
                "USB_HUB_CONTROL.INDI_ENABLED",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=7),
                "AUTO_DEW.INDI_ENABLED",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=11),
                "POWER_SENSORS.SENSOR_VOLTAGE",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=12),
                "POWER_SENSORS.SENSOR_CURRENT",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=13),
                "POWER_SENSORS.SENSOR_POWER",
            )

        if model == "UPBv2":
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=0),
                "POWER_CONTROL.POWER_CONTROL_1",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=1),
                "POWER_CONTROL.POWER_CONTROL_2",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=2),
                "POWER_CONTROL.POWER_CONTROL_3",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=3),
                "POWER_CONTROL.POWER_CONTROL_4",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=4) / 2.55,
                "DEW_PWM.DEW_A",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=5) / 2.55,
                "DEW_PWM.DEW_B",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=6) / 2.55,
                "DEW_PWM.DEW_C",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=7),
                "USB_PORT_CONTROL.PORT_1",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=8),
                "USB_PORT_CONTROL.PORT_2",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=9),
                "USB_PORT_CONTROL.PORT_3",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=10),
                "USB_PORT_CONTROL.PORT_4",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=11),
                "USB_PORT_CONTROL.PORT_5",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=12),
                "USB_PORT_CONTROL.PORT_6",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=13),
                "AUTO_DEW.DEW_A",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=13),
                "AUTO_DEW.DEW_B",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitch", Id=13),
                "AUTO_DEW.DEW_C",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=17),
                "POWER_SENSORS.SENSOR_VOLTAGE",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=18),
                "POWER_SENSORS.SENSOR_CURRENT",
            )
            self.storePropertyToData(
                self.callDeviceMethodSync("GetSwitchValue", Id=19),
                "POWER_SENSORS.SENSOR_POWER",
            )

    def togglePowerPort(self, port: str) -> None:
        switchNumber = int(port) - 1
        val = self.data.get(f"POWER_CONTROL.POWER_CONTROL_{port}", True)
        self.callDeviceMethod("SetSwitchValue", Id=switchNumber, Value=not val)

    def togglePowerPortBoot(self, port: str) -> None:
        pass

    def toggleHubUSB(self) -> None:
        pass

    def togglePortUSB(self, port: str) -> None:
        model = (
            "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
        )
        if model == "UPBv2":
            switchNumber = int(port) + 6
            val = self.data.get(f"USB_PORT_CONTROL.PORT_{port}", True)
            self.callDeviceMethod(
                "SetSwitchValue", Id=switchNumber, Value=val
            )

    def toggleAutoDew(self) -> None:
        model = (
            "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
        )
        if model == "UPB":
            val = self.data.get("AUTO_DEW.INDI_ENABLED", False)
            self.callDeviceMethod("SetSwitchValue", Id=7, Value=val)
        else:
            val = self.data.get("AUTO_DEW.DEW_A", False)
            self.callDeviceMethod("SetSwitchValue", Id=13, Value=val)

    def sendDew(self, port: str, value: float) -> None:
        model = (
            "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
        )
        switchNumber = ord(port) - ord("A") + 4
        val = int(value * 2.55)
        if model == "UPBv2":
            self.callDeviceMethod(
                "SetSwitchValue", Id=switchNumber, Value=val
            )

    def sendAdjustableOutput(self, value: float) -> None:
        pass

    def reboot(self) -> None:
        pass
