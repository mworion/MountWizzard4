############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from skyfield.api import Angle, Star

# local imports


class ProgStar(object):
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, mCoord: Star, sCoord: Star, sidereal: Angle, pierside: str):
        self.mCoord = mCoord
        self.sCoord = sCoord
        self.sidereal = sidereal
        self.pierside = pierside

    @property
    def pierside(self):
        return self._pierside

    @pierside.setter
    def pierside(self, value):
        if value in ["E", "W", "e", "w"]:
            value = value.capitalize()
            self._pierside = value
        else:
            self._pierside = None
            self.log.warning(f"Malformed value: {value}")
