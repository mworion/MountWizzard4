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
from indipyclient.queclient import EventItem
from mw4.base.indiClass import IndiClass
from typing import Any


class PegasusUPBIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.modelVersion: int = 0

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
        if firmwareInfo["members"].get("VERSION", {"value": "1.4"})["value"] < "1.5":
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
            value = "Off" if self.data[f"AUX_POWER_OUTLET.OUTLET_{port}"] else "On"
            self.txQ.put(
                (self.config.deviceName, "AUX_POWER_OUTLET", {f"OUTLET_{port}": value})
            )
        else:
            value = (
                "Off" if self.data[f"POWER_CHANNELS.POWER_CHANNEL_{port}"] else "On"
            )
            self.txQ.put(
                (self.config.deviceName, "POWER_CHANNELS", {f"POWER_CHANNEL_{port}": value})
            )

    def toggleHubUSB(self) -> None:
        if self.isINDIGO:
            return
        value = "Off" if self.data["USB_HUB_CONTROL.INDI_ENABLED"]else "On"
        self.txQ.put((self.config.deviceName, "USB_HUB_CONTROL", {"INDI_ENABLED": value}))

    def togglePortUSB(self, port: str) -> None:
        if self.isINDIGO:
            value = "Off" if self.data[f"AUX_USB_PORT.PORT_{port}"] else "On"
            self.txQ.put((self.config.deviceName, "AUX_USB_PORT", {f"PORT_{port}": value}))
        else:
            value = "Off" if self.data[f"USB_PORTS.USB_PORT_{port}"] else "On"
            self.txQ.put((self.config.deviceName, "USB_PORTS", {f"USB_PORT_{port}": value}))

    def toggleAutoDew(self) -> None:
        if self.isINDIGO:
            value = "Off" if self.data["AUX_DEW_CONTROL.MANUAL"] else "On"
            self.txQ.put((self.config.deviceName, "AUX_DEW_CONTROL", {"MANUAL": value}))
            value = "Off" if self.data["AUX_DEW_CONTROL.MANUAL"] else "On"
            self.txQ.put((self.config.deviceName, "AUX_DEW_CONTROL", {"AUTOMATIC": value}))
        else:
            if self.modelVersion == 1:
                if "AUTO_DEW.INDI_ENABLED" not in self.data:
                    return
                value = "Off" if self.data["AUTO_DEW.INDI_ENABLED"] else "On"
                self.txQ.put((self.config.deviceName, "AUTO_DEW", {"INDI_ENABLED": value}))
            else:
                if "AUTO_DEW_CONTROL.DEW_CHANNEL_1" not in self.data:
                    return
                value = "Off" if self.data["AUTO_DEW_CONTROL.DEW_CHANNEL_1"] else "On"
                self.txQ.put((self.config.deviceName, "AUTO_DEW_CONTROL", {"DEW_CHANNEL_1": value}))
                self.txQ.put((self.config.deviceName, "AUTO_DEW_CONTROL", {"DEW_CHANNEL_2": value}))
                self.txQ.put((self.config.deviceName, "AUTO_DEW_CONTROL", {"DEW_CHANNEL_3": value}))

    def sendDew(self, port: str, value: float) -> None:
        if self.isINDIGO:
            self.txQ.put(
                (self.config.deviceName, "AUX_HEATER_OUTLET", {f"OUTLET_{port}": value})
            )
        else:
            self.txQ.put((self.config.deviceName, "DEW_DUTY_CYCLES", {f"DEW_CHANNEL_{port}": value}))

    def sendAdjustableOutput(self, value: float) -> None:
        if self.isINDIGO:
            self.txQ.put(
                (self.config.deviceName, "X_AUX_VARIABLE_POWER_OUTLET", {"OUTLET_1": value})
            )
        else:
            self.txQ.put(
                (
                    self.config.deviceName,
                    "VARIABLE_VOLTAGES",
                    {"VAR_CHANNEL_1": value},
                )
            )

    def reboot(self) -> None:
        if self.isINDIGO:
            self.txQ.put((self.config.deviceName, "X_AUX_REBOOT", {"REBOOT": "On"}))
        else:
            self.txQ.put((self.config.deviceName, "REBOOT_DEVICE", {"REBOOT": "On"}))
