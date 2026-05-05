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


class DomeAlpaca(AlpacaClass):
    SHUTTER_STATES: list[str] = ["Open", "Closed", "Opening", "Closing", "Error"]

    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals

    def getInitialConfig(self) -> None:
        super().getInitialConfig()
        self.getAndStoreDeviceProp("CanSetAltitude", "CanSetAltitude")
        self.getAndStoreDeviceProp("CanSetAzimuth", "CanSetAzimuth")
        self.getAndStoreDeviceProp("CanSetShutter", "CanSetShutter")
        self.log.debug(f"Initial data: {self.data}")

    def pollData(self) -> None:
        self.getAndStoreDeviceProp("Azimuth", "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION")
        self.signals.azimuth.emit(self.data.get("ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION"))
        self.getAndStoreDeviceProp("Slewing", "Slewing")

        state = self.getDeviceProp("ShutterStatus")
        if state is None:
            self.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
            self.data["DOME_SHUTTER.SHUTTER_CLOSED"] = None
            return

        stateIndex = int(state)
        if stateIndex == 0:
            stateText = self.SHUTTER_STATES[stateIndex]
            self.storePropertyToData(stateText, "Status.Shutter")
            self.storePropertyToData(True, "DOME_SHUTTER.SHUTTER_OPEN")
            self.storePropertyToData(False, "DOME_SHUTTER.SHUTTER_CLOSED")
        elif stateIndex == 1:
            stateText = self.SHUTTER_STATES[stateIndex]
            self.storePropertyToData(stateText, "Status.Shutter")
            self.storePropertyToData(False, "DOME_SHUTTER.SHUTTER_OPEN")
            self.storePropertyToData(True, "DOME_SHUTTER.SHUTTER_CLOSED")
        else:
            self.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
            self.data["DOME_SHUTTER.SHUTTER_CLOSED"] = None

    def slewToAltAz(self, altitude: float, azimuth: float) -> None:
        if self.data.get("CanSetAzimuth"):
            self.callDeviceMethodQueued("SlewToAzimuth", Azimuth=azimuth)
        if self.data.get("CanSetAltitude"):
            self.callDeviceMethodQueued("SlewToAltitude", Altitude=altitude)

    def openShutter(self) -> None:
        if self.data.get("CanSetShutter"):
            self.callDeviceMethodQueued("OpenShutter")

    def closeShutter(self) -> None:
        if self.data.get("CanSetShutter"):
            self.callDeviceMethodQueued("CloseShutter")

    def slewCW(self) -> None:
        pass

    def slewCCW(self) -> None:
        pass

    def abortSlew(self) -> None:
        self.callDeviceMethodQueued("AbortSlew")
