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


class DomeAscom(AscomClass):
    """ """

    shutterStates = ["Open", "Closed", "Opening", "Closing", "Error"]

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.signals = parent.signals

    def workerGetInitialConfig(self) -> None:
        """ """
        super().workerGetInitialConfig()
        self.getAndStoreAscomProperty("CanSetAltitude", "CanSetAltitude")
        self.getAndStoreAscomProperty("CanSetAzimuth", "CanSetAzimuth")
        self.getAndStoreAscomProperty("CanSetShutter", "CanSetShutter")
        self.log.debug(f"Initial data: {self.data}")

    def processPolledData(self) -> None:
        """ """
        azimuth = self.data.get("ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION", 0)
        self.signals.azimuth.emit(azimuth)

    def workerPollData(self) -> None:
        """ """
        azimuth = self.getAscomProperty("Azimuth")
        self.storePropertyToData(azimuth, "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION")
        self.signals.azimuth.emit(azimuth)
        self.getAndStoreAscomProperty("Slewing", "Slewing")

        state = self.getAscomProperty("ShutterStatus")
        if state == 0:
            stateText = self.shutterStates[state]
            self.storePropertyToData(stateText, "Status.Shutter")
            self.storePropertyToData(
                True,
                "DOME_SHUTTER.SHUTTER_OPEN",
                elementInv="DOME_SHUTTER.SHUTTER_CLOSED",
            )
        elif state == 1:
            stateText = self.shutterStates[state]
            self.storePropertyToData(stateText, "Status.Shutter")
            self.storePropertyToData(
                False,
                "DOME_SHUTTER.SHUTTER_OPEN",
                elementInv="DOME_SHUTTER.SHUTTER_CLOSED",
            )
        else:
            self.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
            self.data["DOME_SHUTTER.SHUTTER_CLOSED"] = None

    def slewToAltAz(self, altitude: float, azimuth: float) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.SlewToAzimuth, azimuth)
        self.callMethodThreaded(self.client.SlewToAltitude, altitude)

    def openShutter(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.OpenShutter)

    def closeShutter(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.CloseShutter)

    def slewCW(self) -> None:
        """ """
        if not self.deviceConnected:
            return
        self.callMethodThreaded(self.client.OpenShutter)

    def slewCCW(self) -> None:
        """ """
        pass

    def abortSlew(self) -> None:
        """ """
        pass
