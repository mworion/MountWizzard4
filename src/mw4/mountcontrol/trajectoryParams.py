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
from dataclasses import dataclass
from mw4.mountcontrol.obsSite import ObsSite
from skyfield.timelib import Time


@dataclass
class TrajectoryParams:
    """ """

    obsSite: ObsSite
    flip: bool = False
    message: str = ""
    offsetRA: float = 0
    offsetDEC: float = 0
    offsetDECcorr: float = 0
    offsetTime: float = 0
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
