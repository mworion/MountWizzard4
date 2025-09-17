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
from base.alpacaClass import AlpacaClass


class CoverAlpaca(AlpacaClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.parent = parent
        self.alpacaSignals = parent.signals
        self.data = parent.data

    def workerPollData(self) -> None:
        """ """
        states = ["NotPresent", "Closed", "Moving", "Open", "Unknown", "Error"]
        if not self.deviceConnected:
            return

        state = self.getAlpacaProperty("coverstate")
        stateText = states[state]
        self.storePropertyToData(stateText, "Status.Cover")

        brightness = self.getAlpacaProperty("Brightness")
        self.storePropertyToData(brightness, "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE")

        maxBrightness = self.getAlpacaProperty("MaxBrightness")
        self.storePropertyToData(
            maxBrightness, "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX"
        )

    def closeCover(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.getAlpacaProperty("closecover")

    def openCover(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.getAlpacaProperty("opencover")

    def haltCover(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.getAlpacaProperty("haltcover")

    def lightOn(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        maxBrightness = self.app.cover.data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX", 255
        )
        brightness = int(maxBrightness / 2)
        self.setAlpacaProperty("calibratoron", Brightness=brightness)

    def lightOff(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.getAlpacaProperty("calibratoroff")

    def lightIntensity(self, value: float) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.setAlpacaProperty("calibratoron", Brightness=value)
