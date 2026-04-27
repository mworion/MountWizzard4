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
from mw4.base.indiClass import IndiClass
from indipyclient.queclient import EventItem
from typing import Any


class DomeIndi(IndiClass):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent=parent)
        self.signals = parent.signals
        self.lastAzimuth: float | None = None

    def sendDomePosition(self, vectors: dict) -> None:
        position = vectors.get("ABS_DOME_POSITION", {})
        if not position:
            return
        member = position.get("members", {}).get("DOME_ABSOLUTE_POSITION")
        if member is None:
            return
        azimuth = member["floatvalue"]
        slewing = position["state"] == "Busy"
        self.data["Slewing"] = slewing
        self.signals.azimuth.emit(azimuth)

    def addShutterStatus(self, vectors: dict) -> None:
        shutterState = vectors.get("DOME_SHUTTER", {})
        if not shutterState:
            return
        if shutterState["state"] == "Busy":
            self.data["Shutter.Status"] = "Moving"
        else:
            self.data["Shutter.Status"] = "-"

    def writeVectorsToData(self, item: EventItem, vectors: dict) -> None:
        super().writeVectorsToData(item, vectors)
        self.sendDomePosition(vectors)
        self.addShutterStatus(vectors)

    def slewToAltAz(self, altitude: float, azimuth: float) -> None:
        self.txQ.put((self.deviceName, "ABS_DOME_POSITION", {"DOME_ABSOLUTE_POSITION": azimuth}))

    def openShutter(self) -> None:
        self.txQ.put((self.deviceName, "DOME_SHUTTER", {"SHUTTER_OPEN": "On"}))

    def closeShutter(self) -> None:
        self.txQ.put((self.deviceName, "DOME_SHUTTER", {"SHUTTER_CLOSE": "On"}))

    def slewCW(self) -> None:
        self.txQ.put((self.deviceName, "DOME_MOTION", {"DOME_CW": "On"}))

    def slewCCW(self) -> None:
        self.txQ.put((self.deviceName, "DOME_MOTION", {"DOME_CCW": "On"}))

    def abortSlew(self) -> None:
        self.txQ.put((self.deviceName, "DOME_ABORT_MOTION", {"ABORT": "On"}))
