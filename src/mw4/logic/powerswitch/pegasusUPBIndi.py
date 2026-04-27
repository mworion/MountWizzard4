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
from indipyclient.queclient import EventItem
from typing import Any


class PegasusUPBIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.modelVersion: int = 0

    def setUpdateConfig(self, deviceName: str) -> None:
        self.txQ.put((self.deviceName, "POLLING_PERIOD", {"PERIOD_MS": self.updateRate}))

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

    def writeVectorsToData(self, item: EventItem, vectors: dict) -> None:
        super().writeVectorsToData(item, vectors)
        self.checkDriverInfo(vectors)
        self.checkFirmwareInfo(vectors)

    def togglePowerPort(self, port: str) -> None:
        if self.isINDIGO:
            value = "On" if self.data[f"AUX_POWER_OUTLET.OUTLET_{port}"] == "Off" else "Off"
            self.txQ.put((self.deviceName, "AUX_POWER_OUTLET", {f"OUTLET_{port}": value}))
        else:
            value = "On" if self.data[f"POWER_CONTROL.POWER_CONTROL_{port}"] == "Off" else "Off"
            self.txQ.put((self.deviceName, "POWER_CONTROL", {f"POWER_CONTROL_{port}": value}))

    def togglePowerPortBoot(self, port: str) -> None:
        if self.isINDIGO:
            return
        value = "On" if self.data[f"POWER_ON_BOOT.POWER_PORT_{port}"] == "Off" else "Off"
        self.txQ.put((self.deviceName, "POWER_ON_BOOT", {f"POWER_PORT_{port}": value}))

    def toggleHubUSB(self) -> None:
        if self.isINDIGO:
            return
        value = "On" if self.data[f"USB_HUB_CONTROL.INDI_ENABLED"] == "Off" else "Off"
        self.txQ.put((self.deviceName, "USB_HUB_CONTROL", {f"INDI_ENABLED": value}))

    def togglePortUSB(self, port: str) -> None:
        if self.isINDIGO:
            value = "On" if self.data[f"AUX_USB_PORT.PORT_{port}"] == "Off" else "Off"
            self.txQ.put((self.deviceName, "AUX_USB_PORT", {f"PORT_{port}": value}))
        else:
            value = "On" if self.data[f"USB_PORT_CONTROL.PORT_{port}"] == "Off" else "Off"
            self.txQ.put((self.deviceName, "USB_PORT_CONTROL", {f"PORT_{port}": value}))

    def toggleAutoDew(self) -> None:
        if self.device is None:
            return
        if self.isINDIGO:
            value = "On" if self.data[f"AUX_DEW_CONTROL.MANUAL"] == "Off" else "Off"
            self.txQ.put((self.deviceName, "AUX_DEW_CONTROL", {"MANUAL": value}))
            value = "On" if self.data[f"AUX_DEW_CONTROL.MANUAL"] == "On" else "Off"
            self.txQ.put((self.deviceName, "AUX_DEW_CONTROL", {"AUTOMATIC": value}))
        else:
            if self.modelVersion == 1:
                if "AUTO_DEW.INDI_ENABLED" not in self.data:
                    return
                value = "On" if self.data[f"AUTO_DEW.INDI_ENABLED"] == "Off" else "Off"
                self.txQ.put((self.deviceName, "AUTO_DEW", {"INDI_ENABLED": value}))
            else:
                if "AUTO_DEW.DEW_A" not in self.data:
                    return
                value = "On" if self.data[f"AUTO_DEW.DEW_A"] == "Off" else "Off"
                self.txQ.put((self.deviceName, "AUTO_DEW", {"DEW_A": value}))
                self.txQ.put((self.deviceName, "AUTO_DEW", {"DEW_B": value}))
                self.txQ.put((self.deviceName, "AUTO_DEW", {"DEW_C": value}))

    def sendDew(self, port: str, value: float) -> None:
        if self.isINDIGO:
            conv = {"A": "1", "B": "2", "C": "3"}
            self.txQ.put((self.deviceName, "AUX_HEATER_OUTLET", {f"OUTLET_{conv[port]}": value}))
        else:
            self.txQ.put((self.deviceName, "DEW_PWM", {f"DEW_{port}": value}))

    def sendAdjustableOutput(self, value: float) -> None:
        if self.isINDIGO:
            self.txQ.put((self.deviceName, "X_AUX_VARIABLE_POWER_OUTLET", {"OUTLET_1": value}))
        else:
            self.txQ.put((self.deviceName, "ADJUSTABLE_VOLTAGE", {"ADJUSTABLE_VOLTAGE_VALUE": value}))

    def reboot(self) -> None:
        if self.device is None:
            return
        if self.isINDIGO:
            self.txQ.put((self.deviceName, "X_AUX_REBOOT", {"REBOOT": "On"}))
        else:
            self.txQ.put((self.deviceName, "REBOOT_DEVICE", {"REBOOT": "On"}))
