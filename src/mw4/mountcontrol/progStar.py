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
from skyfield.api import Angle, Star


class ProgStar:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, mCoord: Star, sCoord: Star, sidereal: Angle, pierside: str):
        self.mCoord: Star = mCoord
        self.sCoord: Star = sCoord
        self.sidereal: Angle = sidereal
        self.pierside: str = pierside

    @property
    def pierside(self):
        return self._pierside

    @pierside.setter
    def pierside(self, value):
        if value in ["E", "W", "e", "w"]:
            value = value.capitalize()
            self._pierside = value
        else:
            self._pierside = "E"
            self.log.warning(f"Malformed value: {value}")
