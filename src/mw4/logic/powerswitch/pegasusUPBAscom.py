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
from mw4.base.ascomClass import AscomClass
from typing import Any


class PegasusUPBAscom(AscomClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def pollData(self) -> None:
        self.getAndStoreDeviceProp("MaxSwitch", "MaxSwitch")
        maxSwitch = self.data.get("MaxSwitch", 0)
        model = "UPB" if maxSwitch == 15 else "UPBv2"

        self.data["FIRMWARE_INFO.VERSION"] = "1.4" if model == "UPB" else "2.1"
        if model == "UPB":
            self.getAndStoreDeviceProp("getswitch(0)", "POWER_CONTROL.POWER_CONTROL_1")
            self.getAndStoreDeviceProp("getswitch(1)", "POWER_CONTROL.POWER_CONTROL_2")
            self.getAndStoreDeviceProp("getswitch(2)", "POWER_CONTROL.POWER_CONTROL_3")
            self.getAndStoreDeviceProp("getswitch(3)", "POWER_CONTROL.POWER_CONTROL_4")
            self.getAndStoreDeviceProp("getswitchvalue(4)", "DEW_CURRENT.DEW_CURRENT_A")
            self.getAndStoreDeviceProp("getswitchvalue(5)", "DEW_CURRENT.DEW_CURRENT_B")
            self.getAndStoreDeviceProp("getswitch(6)", "USB_HUB_CONTROL.INDI_ENABLED")
            self.getAndStoreDeviceProp("getswitch(7)", "AUTO_DEW.INDI_ENABLED")
            self.getAndStoreDeviceProp("getswitchvalue(11)", "POWER_SENSORS.SENSOR_VOLTAGE")
            self.getAndStoreDeviceProp("getswitchvalue(12)", "POWER_SENSORS.SENSOR_CURRENT")
            self.getAndStoreDeviceProp("getswitchvalue(13)", "POWER_SENSORS.SENSOR_POWER")

        if model == "UPBv2":
            self.getAndStoreDeviceProp("getswitch(0)", "POWER_CONTROL.POWER_CONTROL_1")
            self.getAndStoreDeviceProp("getswitch(1)", "POWER_CONTROL.POWER_CONTROL_2")
            self.getAndStoreDeviceProp("getswitch(2)", "POWER_CONTROL.POWER_CONTROL_3")
            self.getAndStoreDeviceProp("getswitch(3)", "POWER_CONTROL.POWER_CONTROL_4")
            self.getAndStoreDeviceProp("getswitchvalue(4) / 2.55", "DEW_PWM.DEW_A")
            self.getAndStoreDeviceProp("getswitchvalue(5) / 2.55", "DEW_PWM.DEW_B")
            self.getAndStoreDeviceProp("getswitchvalue(6) / 2.55", "DEW_PWM.DEW_C")
            self.getAndStoreDeviceProp("getswitch(7)", "USB_PORT_CONTROL.PORT_1")
            self.getAndStoreDeviceProp("getswitch(8)", "USB_PORT_CONTROL.PORT_2")
            self.getAndStoreDeviceProp("getswitch(9)", "USB_PORT_CONTROL.PORT_3")
            self.getAndStoreDeviceProp("getswitch(10)", "USB_PORT_CONTROL.PORT_4")
            self.getAndStoreDeviceProp("getswitch(11)", "USB_PORT_CONTROL.PORT_5")
            self.getAndStoreDeviceProp("getswitch(12)", "USB_PORT_CONTROL.PORT_6")
            self.getAndStoreDeviceProp("getswitch(13)", "AUTO_DEW.DEW_A")
            self.getAndStoreDeviceProp("getswitch(13)", "AUTO_DEW.DEW_B")
            self.getAndStoreDeviceProp("getswitch(13)", "AUTO_DEW.DEW_C")
            self.getAndStoreDeviceProp(
                "getswitchvalue(17) / 10", "POWER_SENSORS.SENSOR_VOLTAGE"
            )
            self.getAndStoreDeviceProp(
                "getswitchvalue(18) / 10", "POWER_SENSORS.SENSOR_CURRENT"
            )
            self.getAndStoreDeviceProp("getswitchvalue(19)", "POWER_SENSORS.SENSOR_POWER")

    def togglePowerPort(self, port: str) -> None:
        switchNumber = int(port) - 1
        val = self.data.get(f"POWER_CONTROL.POWER_CONTROL_{port}", True)
        self.callDeviceMethodQueued("SetSwitch", Id=switchNumber, State=not val)

    def togglePowerPortBoot(self, port: str) -> None:
        pass

    def toggleHubUSB(self) -> None:
        pass

    def togglePortUSB(self, port: str) -> None:
        maxSwitch = self.data.get("MaxSwitch", 0)
        model = "UPB" if maxSwitch == 15 else "UPBv2"
        if model == "UPBv2":
            switchNumber = int(port) + 6
            val = self.data.get(f"USB_PORT_CONTROL.PORT_{port}", True)
            self.callDeviceMethodQueued("SetSwitch", Id=switchNumber, State=not val)

    def toggleAutoDew(self) -> None:
        maxSwitch = self.data.get("MaxSwitch", 0)
        model = "UPB" if maxSwitch == 15 else "UPBv2"

        if model == "UPB":
            val = self.data.get("AUTO_DEW.INDI_ENABLED", False)
            self.callDeviceMethodQueued("SetSwitch", Id=7, State=not val)
        else:
            val = self.data.get("AUTO_DEW.DEW_A", False)
            self.callDeviceMethodQueued("SetSwitch", Id=13, State=not val)

    def sendDew(self, port: str, value: float) -> None:
        maxSwitch = self.data.get("MaxSwitch", 0)
        model = "UPB" if maxSwitch == 15 else "UPBv2"

        switchNumber = ord(port) - ord("A") + 4
        val = int(value * 2.55)
        if model == "UPBv2":
            self.callDeviceMethodQueued("SetSwitchValue", Id=switchNumber, Value=val)

    def sendAdjustableOutput(self, value: float) -> None:
        pass

    def reboot(self) -> None:
        pass
