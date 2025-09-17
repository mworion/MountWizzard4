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

# local imports
from base.indiClass import IndiClass


class DomeIndi(IndiClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.lastAzimuth = None
        self.app.update1s.connect(self.updateStatus)

    def updateStatus(self) -> None:
        """ """
        if not self.client.connected:
            return

        azimuth = self.data.get("ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION", 0)
        self.signals.azimuth.emit(azimuth)

    def updateNumber(self, deviceName: str, propertyName: str) -> None:
        """ """
        for element, value in self.device.getNumber(propertyName).items():
            if element == "DOME_ABSOLUTE_POSITION":
                azimuth = self.data.get("ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION", 0)
                self.signals.azimuth.emit(azimuth)
                slewing = self.device.ABS_DOME_POSITION["state"] == "Busy"
                self.data["Slewing"] = slewing

            if element == "SHUTTER_OPEN":
                moving = self.device.DOME_SHUTTER["state"] == "Busy"
                if moving:
                    self.data["Shutter.Status"] = "Moving"
                else:
                    self.data["Shutter.Status"] = "-"

    def slewToAltAz(self, altitude: float, azimuth: float) -> None:
        """ """
        if self.device is None:
            return
        if self.deviceName is None or not self.deviceName:
            return

        position = self.device.getNumber("ABS_DOME_POSITION")
        if "DOME_ABSOLUTE_POSITION" not in position:
            return

        position["DOME_ABSOLUTE_POSITION"] = azimuth
        self.client.sendNewNumber(
            deviceName=self.deviceName,
            propertyName="ABS_DOME_POSITION",
            elements=position,
        )

    def openShutter(self) -> None:
        """ """
        if self.device is None:
            return
        if self.deviceName is None or not self.deviceName:
            return

        position = self.device.getSwitch("DOME_SHUTTER")
        if "SHUTTER_OPEN" not in position:
            return

        position["SHUTTER_OPEN"] = "On"
        position["SHUTTER_CLOSE"] = "Off"
        self.client.sendNewSwitch(
            deviceName=self.deviceName, propertyName="DOME_SHUTTER", elements=position
        )

    def closeShutter(self) -> None:
        """ """
        if self.device is None:
            return
        if self.deviceName is None or not self.deviceName:
            return

        position = self.device.getSwitch("DOME_SHUTTER")
        if "SHUTTER_CLOSE" not in position:
            return

        position["SHUTTER_OPEN"] = "Off"
        position["SHUTTER_CLOSE"] = "On"
        self.client.sendNewSwitch(
            deviceName=self.deviceName, propertyName="DOME_SHUTTER", elements=position
        )

    def slewCW(self) -> None:
        """ """
        if self.device is None:
            return
        if self.deviceName is None or not self.deviceName:
            return

        position = self.device.getSwitch("DOME_MOTION")
        if "DOME_CW" not in position:
            return

        position["DOME_CW"] = "On"
        position["DOME_CCW"] = "Off"
        self.client.sendNewSwitch(
            deviceName=self.deviceName, propertyName="DOME_MOTION", elements=position
        )

    def slewCCW(self) -> None:
        """ """
        if self.device is None:
            return
        if self.deviceName is None or not self.deviceName:
            return

        position = self.device.getSwitch("DOME_MOTION")
        if "DOME_CW" not in position:
            return False

        position["DOME_CW"] = "Off"
        position["DOME_CCW"] = "On"
        self.client.sendNewSwitch(
            deviceName=self.deviceName, propertyName="DOME_MOTION", elements=position
        )

    def abortSlew(self) -> None:
        """ """
        if self.device is None:
            return
        if self.deviceName is None or not self.deviceName:
            return

        position = self.device.getSwitch("DOME_ABORT_MOTION")
        if "ABORT" not in position:
            return

        position["ABORT"] = "On"
        self.client.sendNewSwitch(
            deviceName=self.deviceName,
            propertyName="DOME_ABORT_MOTION",
            elements=position,
        )
