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
from dataclasses import dataclass
from mw4.mountcontrol.obsSite import ObsSite
from skyfield.timelib import Time
from skyfield.units import Angle


@dataclass
class TLEParams:
    obsSite: ObsSite
    azimuth: Angle = Angle(degrees=0)
    altitude: Angle = Angle(degrees=0)
    ra: Angle = Angle(hours=0)
    dec: Angle = Angle(degrees=0)
    flip: bool = False
    message: str = ""
    l0: str = ""
    l1: str = ""
    l2: str = ""
    name: str = ""
    _jdStart: Time | None = None
    _jdEnd: Time | None = None

    @property
    def jdStart(self) -> Time:
        if self._jdStart is None:
            return self.obsSite.ts.now()
        return self._jdStart

    @jdStart.setter
    def jdStart(self, value: float) -> None:
        self._jdStart = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)

    @property
    def jdEnd(self) -> Time:
        if self._jdEnd is None:
            return self.obsSite.ts.now()
        return self._jdEnd

    @jdEnd.setter
    def jdEnd(self, value: float) -> None:
        self._jdEnd = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
