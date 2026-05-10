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
from mw4.base.ascomClass import AscomClass
from typing import Any


class DomeAscom(AscomClass):
    shutterStates = ["Open", "Closed", "Opening", "Closing", "Error"]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        self.getAndStoreAscomProperty("CanSetAltitude", "CanSetAltitude")
        self.getAndStoreAscomProperty("CanSetAzimuth", "CanSetAzimuth")
        self.getAndStoreAscomProperty("CanSetShutter", "CanSetShutter")
        self.log.debug(f"Initial data: {self.data}")

    def pollData(self) -> None:
        azimuth = self.getAscomProperty("Azimuth")
        self.storePropertyToData(azimuth, "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION")
        self.signals.azimuth.emit(azimuth)
        self.getAndStoreAscomProperty("Slewing", "Slewing")

        state = self.getAscomProperty("ShutterStatus")
        if state == 0:
            stateText = self.shutterStates[state]
            self.storePropertyToData(stateText, "Status.Shutter")
            self.storePropertyToData(True, "DOME_SHUTTER.SHUTTER_OPEN")
            self.storePropertyToData(False, "DOME_SHUTTER.SHUTTER_CLOSED")
        elif state == 1:
            stateText = self.shutterStates[state]
            self.storePropertyToData(stateText, "Status.Shutter")
            self.storePropertyToData(False, "DOME_SHUTTER.SHUTTER_OPEN")
            self.storePropertyToData(True, "DOME_SHUTTER.SHUTTER_CLOSED")
        else:
            self.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
            self.data["DOME_SHUTTER.SHUTTER_CLOSED"] = None

    def slewToAltAz(self, altitude: float, azimuth: float) -> None:
        self.callAscomMethodQueued("SlewToAzimuth", azimuth)
        self.callAscomMethodQueued("SlewToAltitude", altitude)

    def openShutter(self) -> None:
        self.callAscomMethodQueued("OpenShutter", ())

    def closeShutter(self) -> None:
        self.callAscomMethodQueued("CloseShutter", ())

    def slewCW(self) -> None:
        self.callAscomMethodQueued("OpenShutter", ())

    def slewCCW(self) -> None:
        pass

    def abortSlew(self) -> None:
        pass
