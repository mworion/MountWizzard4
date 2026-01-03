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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
import logging
from skyfield.timelib import Time
from skyfield.units import Angle


class TLEParams:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, obsSite):
        self.obsSite = obsSite
        self.azimuth: Angle = Angle(degrees=0)
        self.altitude: Angle = Angle(degrees=0)
        self.ra: Angle = Angle(hours=0)
        self.dec: Angle = Angle(degrees=0)
        self._jdStart: Time = self.obsSite.ts.tt_jd(0)
        self._jdEnd: Time = self.obsSite.ts.tt_jd(0)
        self._flip: bool = False

        self.message: str = ""
        self.l0: str = ""
        self.l1: str = ""
        self.l2: str = ""
        self.name: str = ""

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
