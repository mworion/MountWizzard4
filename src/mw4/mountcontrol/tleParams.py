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
from skyfield.units import Angle


@dataclass
class TLEParams:
    """ """

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
    _jdStart: object = None
    _jdEnd: object = None

    @property
    def jdStart(self):
        if self._jdStart is None:
            return self.obsSite.ts.now()
        return self._jdStart

    @jdStart.setter
    def jdStart(self, value):
        self._jdStart = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)

    @property
    def jdEnd(self):
        if self._jdEnd is None:
            return self.obsSite.ts.now()
        return self._jdEnd

    @jdEnd.setter
    def jdEnd(self, value):
        self._jdEnd = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
