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
import logging
import numpy
from dataclasses import dataclass
from skyfield.api import Angle, Star

@dataclass
class ModelStar:
    """
    The class ModelStar inherits all information and handling of one star in
    the alignment model used by the mount and the data in the mount and provides
    the abstracted interface to a 10-micron mount.
    The coordinates are in JNow topocentric
    point could be from type skyfield.api.Star or just a tuple of (ha, dec) where
    the format should be in float or the 10-micron string format.

    Command protocol (from2.8.15 onwards):
    "HH:MM:SS.SS,+dd*mm:ss.s,eeee.e,ppp#" where HH:MM:SS.SS is the hour angle
    of the alignment star in hours, minutes, seconds and hundredths of second
    (from 0h to 23h59m59.99s), +dd*mm:ss.s is the declination of the alignment
    star in degrees, arcminutes, arcseconds and tenths of arcsecond, eeee.e is
    the error between the star and the alignment model in arcseconds, ppp is the
    polar angle of the measured star with respect to the modeled star in the
    equatorial system in degrees from 0 to 359 (0 towards the North Pole,
    90 towards east).
    """

    log = logging.getLogger("MW4")

    def __init__(
        self,
        coord: Star = Star(ra_hours=0, dec_degrees=0),
        errorRMS: float = 0,
        errorAngle: Angle = Angle(degrees=0),
        number: int = 0,
        alt: Angle = Angle(degrees=0),
        az: Angle = Angle(degrees=0),
    ):
        self.coord = coord
        self.errorRMS = errorRMS
        self.errorAngle = errorAngle
        self.number = number
        self.alt = alt
        self.az = az

    def errorRA(self):
        return Angle(degrees=self.errorRMS * numpy.sin(self.errorAngle.radians))

    def errorDEC(self):
        return Angle(degrees=self.errorRMS * numpy.cos(self.errorAngle.radians))
