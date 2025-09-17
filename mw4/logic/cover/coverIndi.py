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


class CoverIndi(IndiClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def updateText(self, deviceName: str, propertyName: str) -> None:
        """ """
        for element, value in self.device.getText(propertyName).items():
            if element == "Cover":
                value = value.strip().upper()
                if value == "OPEN":
                    self.data["CAP_PARK.UNPARK"] = True
                    self.data["CAP_PARK.PARK"] = False

                elif value == "CLOSED":
                    self.data["CAP_PARK.UNPARK"] = False
                    self.data["CAP_PARK.PARK"] = True

                else:
                    self.data["CAP_PARK.UNPARK"] = None
                    self.data["CAP_PARK.PARK"] = None

    def closeCover(self) -> None:
        """ """
        if self.device is None:
            return
        cover = self.device.getSwitch("CAP_PARK")
        if "PARK" not in cover:
            return
        cover["UNPARK"] = "Off"
        cover["PARK"] = "On"

        self.client.sendNewSwitch(
            deviceName=self.deviceName,
            propertyName="CAP_PARK",
            elements=cover,
        )

    def openCover(self) -> None:
        """ """
        if self.device is None:
            return
        cover = self.device.getSwitch("CAP_PARK")
        if "UNPARK" not in cover:
            return
        cover["UNPARK"] = "On"
        cover["PARK"] = "Off"

        self.client.sendNewSwitch(
            deviceName=self.deviceName,
            propertyName="CAP_PARK",
            elements=cover,
        )

    @staticmethod
    def haltCover() -> None:
        """ """
        pass

    def lightOn(self) -> None:
        """ """
        if self.device is None:
            return
        light = self.device.getSwitch("FLAT_LIGHT_CONTROL")
        if "FLAT_LIGHT_ON" not in light:
            return
        light["FLAT_LIGHT_ON"] = "On"
        light["FLAT_LIGHT_OFF"] = "Off"

        self.client.sendNewSwitch(
            deviceName=self.deviceName,
            propertyName="FLAT_LIGHT_CONTROL",
            elements=light,
        )

    def lightOff(self) -> None:
        """ """
        if self.device is None:
            return
        light = self.device.getSwitch("FLAT_LIGHT_CONTROL")
        if "FLAT_LIGHT_OFF" not in light:
            return
        light["FLAT_LIGHT_ON"] = "Off"
        light["FLAT_LIGHT_OFF"] = "On"

        self.client.sendNewSwitch(
            deviceName=self.deviceName,
            propertyName="FLAT_LIGHT_CONTROL",
            elements=light,
        )

    def lightIntensity(self, value: float) -> None:
        """ """
        if self.device is None:
            return
        light = self.device.getNumber("FLAT_LIGHT_INTENSITY")
        if "FLAT_LIGHT_INTENSITY_VALUE" not in light:
            return
        light["FLAT_LIGHT_INTENSITY_VALUE"] = value

        self.client.sendNewNumber(
            deviceName=self.deviceName,
            propertyName="FLAT_LIGHT_INTENSITY",
            elements=light,
        )
