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
from skyfield.api import Angle, Star


class ProgStar:
    log = logging.getLogger("MW4")

    def __init__(self, mCoord: Star, sCoord: Star, sidereal: Angle, pierside: str) -> None:
        self.mCoord: Star = mCoord
        self.sCoord: Star = sCoord
        self.sidereal: Angle = sidereal
        self._pierside: str = "E"
        self.pierside = pierside

    @property
    def pierside(self) -> str:
        return self._pierside

    @pierside.setter
    def pierside(self, value: str) -> None:
        if value in ["E", "W", "e", "w"]:
            self._pierside = value.capitalize()
        else:
            self._pierside = "E"
            self.log.warning(f"Malformed value: {value}")
