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
import logging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.convert import valueToFloat, valueToInt
from skyfield.api import Angle
from collections.abc import Any


class Dome:
    log = logging.getLogger("MW4")

    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self._shutterState: int = 0
        self._flapState: int = 0
        self._slew: bool = False
        self._azimuth: float = 0

    @property
    def shutterState(self) -> int:
        return self._shutterState

    @shutterState.setter
    def shutterState(self, value: Any) -> None:
        value = valueToInt(value)
        self._shutterState = value if value in {0, 1, 2, 3} else 0

    @property
    def flapState(self) -> int:
        return self._flapState

    @flapState.setter
    def flapState(self, value: Any) -> None:
        value = valueToInt(value)
        self._flapState = value if value in {0, 1, 2, 3} else 0

    @property
    def slew(self) -> bool:
        return self._slew

    @slew.setter
    def slew(self, value: Any) -> None:
        value = valueToInt(value)
        self._slew = bool(value)

    @property
    def azimuth(self) -> float:
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value: Any) -> None:
        value = valueToFloat(value)
        self._azimuth = (value / 10) % 360.0

    def parse(self, response: list, numberOfChunks: int) -> bool:
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        self.shutterState = response[0]
        self.flapState = response[1]
        self.slew = response[2]
        self.azimuth = response[3]
        return True

    def poll(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":GDS#:GDF#:GDW#:GDA#"
        suc, response, chunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parse(response, chunks)

    def openShutter(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":SDS2#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def closeShutter(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":SDS1#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def openFlap(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":SDF2#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def closeFlap(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":SDF1#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def slewDome(self, azimuth: Angle) -> bool:
        azimuth = azimuth.degrees % 360
        conn = Connection(self.parent)
        commandString = f":SDA{azimuth:04.0f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def enableInternalDomeControl(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":SDAr#"
        suc, _, _ = conn.communicate(commandString)
        return suc
