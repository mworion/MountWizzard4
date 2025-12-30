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


class TrajectoryParams:
    """
    The class TrajectoryParams inherits all information and handling of TLE tracking
    and managing attributes of the connected mount and provides the abstracted
    interface to a 10 micron mount.

        >>> trajectoryParams = TrajectoryParams(host='')
    """

    __all__ = ["TrajectoryParams"]

    log = logging.getLogger("MW4")

    def __init__(self, obsSite=None):
        self.obsSite = obsSite
        self._jdStart: Time = self.obsSite.ts.tt_jd(0)
        self._jdEnd: Time = self.obsSite.ts.tt_jd(0)
        self.flip: bool = False
        self.message: str = ""
        self.offsetRA: float = 0
        self.offsetDEC: float = 0
        self.offsetDECcorr: float = 0
        self.offsetTime: float = 0

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
