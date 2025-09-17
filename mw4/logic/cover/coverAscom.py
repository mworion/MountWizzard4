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
from base.ascomClass import AscomClass


class CoverAscom(AscomClass):
    """ """

    coverStates = ["NotPresent", "Closed", "Moving", "Open", "Unknown", "Error"]

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)

        self.signals = parent.signals
        self.data = parent.data

    def workerPollData(self) -> None:
        """ """
        state = self.getAscomProperty("CoverState")
        stateText = self.coverStates[state]
        self.storePropertyToData(stateText, "Status.Cover")

        brightness = self.getAscomProperty("Brightness")
        self.storePropertyToData(brightness, "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE")

        maxBrightness = self.getAscomProperty("MaxBrightness")
        self.storePropertyToData(
            maxBrightness, "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX"
        )

    def closeCover(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.CloseCover)

    def openCover(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.OpenCover)

    def haltCover(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.HaltCover)

    def lightOn(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        maxBrightness = self.app.cover.data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX", 255
        )
        brightness = int(maxBrightness / 2)
        self.callMethodThreaded(self.client.CalibratorOn, brightness)

    def lightOff(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.CalibratorOff)

    def lightIntensity(self, value: float) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.CalibratorOn, value)
