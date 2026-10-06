# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
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

    @staticmethod
    def parseVersion(version: str) -> tuple[int, ...]:
        try:
            return tuple(int(x) for x in str(version).split("."))
        except ValueError:
            return (0,)

    def checkFirmwareInfo(self, vectors: dict) -> None:
        firmwareInfo = vectors.get("FIRMWARE_INFO", {})
        if not firmwareInfo:
            return
        version = firmwareInfo["members"].get("VERSION", {"value": "1.4"})["value"]
        if self.parseVersion(version) < (1, 5):
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
            value = "Off" if self.data[f"POWER_CHANNELS.POWER_CHANNEL_{port}"] else "On"
            self.txQ.put(
                (self.config.deviceName, "POWER_CHANNELS", {f"POWER_CHANNEL_{port}": value})
            )

    def toggleHubUSB(self) -> None:
        if self.isINDIGO:
            return
        value = "Off" if self.data["USB_HUB_CONTROL.INDI_ENABLED"] else "On"
        self.txQ.put((self.config.deviceName, "USB_HUB_CONTROL", {"INDI_ENABLED": value}))

    def togglePortUSB(self, port: str) -> None:
        if self.isINDIGO:
            value = "Off" if self.data[f"AUX_USB_PORT.PORT_{port}"] else "On"
            self.txQ.put((self.config.deviceName, "AUX_USB_PORT", {f"PORT_{port}": value}))
        else:
            value = "Off" if self.data[f"USB_PORTS.USB_PORT_{port}"] else "On"
            self.txQ.put((self.config.deviceName, "USB_PORTS", {f"USB_PORT_{port}": value}))

    def sendDew(self, port: str, value: float) -> None:
        if self.isINDIGO:
            self.txQ.put(
                (self.config.deviceName, "AUX_HEATER_OUTLET", {f"OUTLET_{port}": value})
            )
        else:
            self.txQ.put(
                (self.config.deviceName, "DEW_DUTY_CYCLES", {f"DEW_CHANNEL_{port}": value})
            )

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
