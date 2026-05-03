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
from mw4.base.alpacaClass import AlpacaClass
from typing import Any


class LightPanelAlpaca(AlpacaClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.alpacaSignals = parent.signals
        self.data = parent.data

    def workerPollData(self) -> None:

        brightness = self.getDeviceProp("Brightness")
        self.storePropertyToData(
            brightness, "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"
        )
        maxBrightness = self.getDeviceProp("MaxBrightness")
        self.storePropertyToData(
            maxBrightness, "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX"
        )

    def lightOn(self) -> None:
        maxBrightness = self.app.cover.data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX", 255
        )
        brightness = int(maxBrightness / 2)
        self.callDeviceMethod("CalibratorOn", Brightness=brightness)

    def lightOff(self) -> None:
        self.callDeviceMethod("CalibratorOff")

    def lightIntensity(self, value: float) -> None:
        self.callDeviceMethod("CalibratorOn", Brightness=int(value))
