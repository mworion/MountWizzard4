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
from typing import Any


class PegasusUPBAlpacaAscomBase:
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None:
        model = "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
        self.data["FIRMWARE_INFO.VERSION"] = "1.4" if model == "UPB" else "2.1"
        if model == "UPB":
            self.getAndStoreDeviceProp("GetSwitch(0)", "POWER_CONTROL.POWER_CONTROL_1")
            self.getAndStoreDeviceProp("GetSwitch(1)", "POWER_CONTROL.POWER_CONTROL_2")
            self.getAndStoreDeviceProp("GetSwitch(2)", "POWER_CONTROL.POWER_CONTROL_3")
            self.getAndStoreDeviceProp("GetSwitch(3)", "POWER_CONTROL.POWER_CONTROL_4")
            self.getAndStoreDeviceProp("GetSwitchValue(4)", "DEW_CURRENT.DEW_CURRENT_A")
            self.getAndStoreDeviceProp("GetSwitchValue(5)", "DEW_CURRENT.DEW_CURRENT_B")
            self.getAndStoreDeviceProp("GetSwitch(6)", "USB_HUB_CONTROL.INDI_ENABLED")
            self.getAndStoreDeviceProp("GetSwitch(7)", "AUTO_DEW.INDI_ENABLED")
            self.getAndStoreDeviceProp("GetSwitchValue(11)", "POWER_SENSORS.SENSOR_VOLTAGE")
            self.getAndStoreDeviceProp("GetSwitchValue(12)", "POWER_SENSORS.SENSOR_CURRENT")
            self.getAndStoreDeviceProp("GetSwitchValue(13)", "POWER_SENSORS.SENSOR_POWER")
        if model == "UPBv2":
            self.getAndStoreDeviceProp("GetSwitch(0)", "POWER_CONTROL.POWER_CONTROL_1")
            self.getAndStoreDeviceProp("GetSwitch(1)", "POWER_CONTROL.POWER_CONTROL_2")
            self.getAndStoreDeviceProp("GetSwitch(2)", "POWER_CONTROL.POWER_CONTROL_3")
            self.getAndStoreDeviceProp("GetSwitch(3)", "POWER_CONTROL.POWER_CONTROL_4")
            self.getAndStoreDeviceProp("GetSwitchValue(4) / 2.55", "DEW_PWM.DEW_A")
            self.getAndStoreDeviceProp("GetSwitchValue(5) / 2.55", "DEW_PWM.DEW_B")
            self.getAndStoreDeviceProp("GetSwitchValue(6) / 2.55", "DEW_PWM.DEW_C")
            self.getAndStoreDeviceProp("GetSwitch(7)", "USB_PORT_CONTROL.PORT_1")
            self.getAndStoreDeviceProp("GetSwitch(8)", "USB_PORT_CONTROL.PORT_2")
            self.getAndStoreDeviceProp("GetSwitch(9)", "USB_PORT_CONTROL.PORT_3")
            self.getAndStoreDeviceProp("GetSwitch(10)", "USB_PORT_CONTROL.PORT_4")
            self.getAndStoreDeviceProp("GetSwitch(11)", "USB_PORT_CONTROL.PORT_5")
            self.getAndStoreDeviceProp("GetSwitch(12)", "USB_PORT_CONTROL.PORT_6")
            self.getAndStoreDeviceProp("GetSwitch(13)", "AUTO_DEW.DEW_A")
            self.getAndStoreDeviceProp("GetSwitch(13)", "AUTO_DEW.DEW_B")
            self.getAndStoreDeviceProp("GetSwitch(13)", "AUTO_DEW.DEW_C")
            self.getAndStoreDeviceProp(
                "GetSwitchValue(17) / 10", "POWER_SENSORS.SENSOR_VOLTAGE"
            )
            self.getAndStoreDeviceProp(
                "GetSwitchValue(18) / 10", "POWER_SENSORS.SENSOR_CURRENT"
            )
            self.getAndStoreDeviceProp("GetSwitchValue(19)", "POWER_SENSORS.SENSOR_POWER")

    def togglePowerPort(self, port: str) -> None:
        switchNumber = int(port) - 1
        val = self.data.get(f"POWER_CONTROL.POWER_CONTROL_{port}", True)
        self.callDeviceMethodQueued("SetSwitchValue", Id=switchNumber, Value=not val)

    def togglePowerPortBoot(self, port: str) -> None:
        pass

    def toggleHubUSB(self) -> None:
        pass

    def togglePortUSB(self, port: str) -> None:
        model = "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
        if model == "UPBv2":
            switchNumber = int(port) + 6
            val = self.data.get(f"USB_PORT_CONTROL.PORT_{port}", True)
            self.callDeviceMethodQueued("SetSwitchValue", Id=switchNumber, Value=val)

    def toggleAutoDew(self) -> None:
        model = "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
        if model == "UPB":
            val = self.data.get("AUTO_DEW.INDI_ENABLED", False)
            self.callDeviceMethodQueued("SetSwitch", Id=7, State=val)
        else:
            val = self.data.get("AUTO_DEW.DEW_A", False)
            self.callDeviceMethodQueued("SetSwitch", Id=13, State=val)

    def sendDew(self, port: str, value: float) -> None:
        model = "UPB" if self.getDeviceProp("MaxSwitch") == 15 else "UPBv2"
        switchNumber = ord(port) - ord("A") + 4
        val = int(value * 2.55)
        if model == "UPBv2":
            self.callDeviceMethodQueued("SetSwitch", Id=switchNumber, State=val)

    def sendAdjustableOutput(self, value: float) -> None:
        pass

    def reboot(self) -> None:
        pass
