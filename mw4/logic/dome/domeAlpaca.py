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


class DomeAlpaca(AlpacaClass):
    """ """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def workerGetInitialConfig(self) -> None:
        """ """
        super().workerGetInitialConfig()
        self.getAndStoreAlpacaProperty("cansetaltitude", "CanSetAltitude")
        self.getAndStoreAlpacaProperty("cansetazimuth", "CanSetAzimuth")
        self.getAndStoreAlpacaProperty("cansetshutter", "CanSetShutter")
        self.log.debug(f"Initial data: {self.data}")

    def processPolledData(self) -> None:
        """ """
        azimuth = self.data.get("ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION", 0)
        self.signals.azimuth.emit(azimuth)

    def workerPollData(self) -> None:
        """ """
        if not self.deviceConnected:
            return

        shutterStates = ["Open", "Closed", "Opening", "Closing", "Error"]
        azimuth = self.getAlpacaProperty("azimuth")
        self.storePropertyToData(azimuth, "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION")
        self.signals.azimuth.emit(azimuth)
        self.getAndStoreAlpacaProperty("slewing", "Slewing")

        state = self.getAlpacaProperty("shutterstatus")
        if state == 0:
            stateText = shutterStates[state]
            self.storePropertyToData(stateText, "Status.Shutter")
            self.storePropertyToData(True, "DOME_SHUTTER.SHUTTER_OPEN")
            self.storePropertyToData(False, "DOME_SHUTTER.SHUTTER_CLOSED")
        elif state == 1:
            stateText = shutterStates[state]
            self.storePropertyToData(stateText, "Status.Shutter")
            self.storePropertyToData(False, "DOME_SHUTTER.SHUTTER_OPEN")
            self.storePropertyToData(True, "DOME_SHUTTER.SHUTTER_CLOSED")
        else:
            self.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
            self.data["DOME_SHUTTER.SHUTTER_CLOSED"] = None

    def slewToAltAz(self, altitude: float, azimuth: float) -> None:
        """ """
        if not self.deviceConnected:
            return
        if self.data.get("CanSetAzimuth"):
            self.setAlpacaProperty("slewtoazimuth", Azimuth=azimuth)
        if self.data.get("CanSetAltitude"):
            self.setAlpacaProperty("slewtoaltitude", Altitude=altitude)

    def openShutter(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        if self.data.get("CanSetShutter"):
            self.getAlpacaProperty("openshutter")

    def closeShutter(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        if self.data.get("CanSetShutter"):
            self.getAlpacaProperty("closeshutter")

    def slewCW(self) -> None:
        """ """
        pass

    def slewCCW(self) -> None:
        """ """
        pass

    def abortSlew(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.getAlpacaProperty("abortslew")
