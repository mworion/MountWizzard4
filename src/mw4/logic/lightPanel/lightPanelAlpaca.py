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
from mw4.base.alpacaClass import AlpacaClass
from typing import Any


class LightPanelAlpaca(AlpacaClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.signals = parent.signals
        self.data = parent.data

    def pollData(self) -> None:
        self.getAndStoreDeviceProp(
            "Brightness",
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE",
        )
        self.getAndStoreDeviceProp(
            "MaxBrightness",
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX",
        )

    def lightOn(self) -> None:
        maxBrightness = self.app.cover.data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX", 255
        )
        brightness = int(maxBrightness / 2)
        self.callDeviceMethodQueued("CalibratorOn", Brightness=brightness)

    def lightOff(self) -> None:
        self.callDeviceMethodQueued("CalibratorOff")

    def lightIntensity(self, value: float) -> None:
        self.callDeviceMethodQueued("CalibratorOn", Brightness=int(value))
