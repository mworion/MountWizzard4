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
from mw4.base.alpacaAscomCommon import AlpacaAscomCommon
from typing import Any


class LightPanelAlpacaAscomBase(AlpacaAscomCommon):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)

    def pollData(self) -> None:
        self.getAndStoreDeviceProp(
            "Brightness",
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE",
        )
        self.getAndStoreDeviceProp(
            "MaxBrightness",
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX",
        )
        if self.data.get("FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"):
            self.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] = 1
        else:
            self.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] = 0

    def lightOn(self) -> None:
        maxBrightness = self.app.lightPanel.data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX", 255
        )
        brightness = int(maxBrightness / 2)
        self.callDeviceMethodQueued("CalibratorOn", BrightnessVal=brightness)

    def lightOff(self) -> None:
        self.callDeviceMethodQueued("CalibratorOff")

    def lightIntensity(self, value: int) -> None:
        self.callDeviceMethodQueued("CalibratorOn", BrightnessVal=value)
