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
from mw4.base.indiClass import IndiClass
from typing import Any


class PegasusUPBIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.modelVersion: int = 0

    def setUpdateConfig(self, deviceName: str) -> None:
        self.sendQ.put((self.deviceName, "POLLING_PERIOD", {"PERIOD_MS": self.updateRate}))

    def checkDriverInfo(self, vectors: dict) -> None:
        driverInfo = vectors.get("DRIVER_INFO", {})
        if not driverInfo:
            return
        if driverInfo["members"].get("DEVICE_MODEL") == "UPB":
            if self.modelVersion != 1:
                self.signals.version.emit(1)
            self.modelVersion = 1
        else:
            if self.modelVersion != 2:
                self.signals.version.emit(2)
            self.modelVersion = 2

    def checkFirmwareInfo(self, vectors: dict) -> None:
        firmwareInfo = vectors.get("FIRMWARE_INFO", {})
        if not firmwareInfo:
            return
        if firmwareInfo["members"].get("VERSION", "1.4") < "1.5":
            if self.modelVersion != 1:
                self.signals.version.emit(1)
            self.modelVersion = 1
        else:
            if self.modelVersion != 2:
                self.signals.version.emit(2)
            self.modelVersion = 2

    def writeVectorsToData(self, vectors: dict) -> None:
        super().writeVectorsToData(vectors)
        self.checkDriverInfo(vectors)
        self.checkFirmwareInfo(vectors)

    def togglePowerPort(self, port: str) -> None:
        if self.isINDIGO:
            value = "On" if self.data[f"AUX_POWER_OUTLET.OUTLET_{port}"] == "Off" else "Off"
            self.sendQ.put((self.deviceName, "AUX_POWER_OUTLET", {f"OUTLET_{port}": value}))
        else:
            value = "On" if self.data[f"POWER_CONTROL.POWER_CONTROL_{port}"] == "Off" else "Off"
            self.sendQ.put((self.deviceName, "POWER_CONTROL", {f"POWER_CONTROL_{port}": value}))

    def togglePowerPortBoot(self, port: str) -> None:
        if self.isINDIGO:
            return
        value = "On" if self.data[f"POWER_ON_BOOT.POWER_PORT_{port}"] == "Off" else "Off"
        self.sendQ.put((self.deviceName, "POWER_ON_BOOT", {f"POWER_PORT_{port}": value}))

    def toggleHubUSB(self) -> None:
        if self.isINDIGO:
            return
        value = "On" if self.data[f"USB_HUB_CONTROL.INDI_ENABLED"] == "Off" else "Off"
        self.sendQ.put((self.deviceName, "USB_HUB_CONTROL", {f"INDI_ENABLED": value}))

    def togglePortUSB(self, port: str) -> None:
        if self.isINDIGO:
            value = "On" if self.data[f"AUX_USB_PORT.PORT_{port}"] == "Off" else "Off"
            self.sendQ.put((self.deviceName, "AUX_USB_PORT", {f"PORT_{port}": value}))
        else:
            value = "On" if self.data[f"USB_PORT_CONTROL.PORT_{port}"] == "Off" else "Off"
            self.sendQ.put((self.deviceName, "USB_PORT_CONTROL", {f"PORT_{port}": value}))

    def toggleAutoDew(self) -> None:
        if self.device is None:
            return
        if self.isINDIGO:
            propertyName = "AUX_DEW_CONTROL"
            autoDew = self.device.getSwitch(propertyName)

            if autoDew["MANUAL"] == "On":
                autoDew["MANUAL"] = "Off"
                autoDew["AUTOMATIC"] = "On"
            else:
                autoDew["MANUAL"] = "On"
                autoDew["AUTOMATIC"] = "Off"
        else:
            propertyName = "AUTO_DEW"
            autoDew = self.device.getSwitch(propertyName)

            if self.modelVersion == 1:
                if "INDI_ENABLED" not in autoDew:
                    return
                if autoDew["INDI_ENABLED"] == "On":
                    autoDew["INDI_ENABLED"] = "Off"
                    autoDew["INDI_DISABLED"] = "On"
                else:
                    autoDew["INDI_ENABLED"] = "Off"
                    autoDew["INDI_DISABLED"] = "On"
            else:
                if "DEW_A" not in autoDew:
                    return False
                if autoDew["DEW_A"] == "On":
                    autoDew["DEW_A"] = "Off"
                    autoDew["DEW_B"] = "Off"
                    autoDew["DEW_C"] = "Off"
                else:
                    autoDew["DEW_A"] = "On"
                    autoDew["DEW_B"] = "On"
                    autoDew["DEW_C"] = "On"

        self.client.sendNewSwitch(
            deviceName=self.deviceName,
            propertyName=propertyName,
            elements=autoDew,
        )

    def sendDew(self, port: str, value=float) -> None:
        if self.device is None:
            return
        if self.isINDIGO:
            conv = {"A": "1", "B": "2", "C": "3"}
            propertyName = "AUX_HEATER_OUTLET"
            dew = self.device.getNumber(propertyName)
            portName = f"OUTLET_{conv[port]}"
        else:
            propertyName = "DEW_PWM"
            dew = self.device.getNumber(propertyName)
            portName = f"DEW_{port}"

        if portName not in dew:
            return

        dew[portName] = value
        self.client.sendNewNumber(
            deviceName=self.deviceName,
            propertyName=propertyName,
            elements=dew,
        )

    def sendAdjustableOutput(self, value: float) -> None:
        if self.device is None:
            return
        if self.isINDIGO:
            propertyName = "X_AUX_VARIABLE_POWER_OUTLET"
            output = self.device.getNumber(propertyName)
            portName = "OUTLET_1"
        else:
            propertyName = "ADJUSTABLE_VOLTAGE"
            output = self.device.getNumber(propertyName)
            portName = "ADJUSTABLE_VOLTAGE_VALUE"

        output[portName] = value
        self.client.sendNewNumber(
            deviceName=self.deviceName,
            propertyName=propertyName,
            elements=output,
        )

    def reboot(self) -> None:
        if self.device is None:
            return
        if self.isINDIGO:
            propertyName = "X_AUX_REBOOT"
            output = self.device.getSwitch(propertyName)
            portName = "REBOOT"
        else:
            propertyName = "REBOOT_DEVICE"
            output = self.device.getSwitch(propertyName)
            portName = "REBOOT"

        if portName not in output:
            return

        output[portName] = "On"
        self.client.sendNewSwitch(
            deviceName=self.deviceName,
            propertyName=propertyName,
            elements=output,
        )
