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
    _jdStart: Time = 0
    _jdEnd: Time = 0
    flip: bool = False
    message: str = ""
    offsetRA: float = 0
    offsetDEC: float = 0
    offsetDECcorr: float = 0
    offsetTime: float = 0

    @property
    def jdStart(self):
        return self._jdStart

    @jdStart.setter
    def jdStart(self, value):
        self._jdStart = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)

    @property
    def jdEnd(self):
        return self._jdEnd

    @jdEnd.setter
    def jdEnd(self, value):
        self._jdEnd = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
