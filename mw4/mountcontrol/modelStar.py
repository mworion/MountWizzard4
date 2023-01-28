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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from skyfield.api import Star, Angle
import numpy

# local imports
from mountcontrol.convert import stringToDegree
from mountcontrol.convert import valueToAngle
from mountcontrol.convert import valueToFloat
from mountcontrol.convert import valueToInt
from mountcontrol.convert import topoToAltAz


class ModelStar(object):
    """
    The class ModelStar inherits all information and handling of one star in
    the alignment model used by the mount and the data in the mount and provides
    the abstracted interface to a 10 micron mount.
    The coordinates are in JNow topocentric

        >>> settings = ModelStar(
        >>>                     coord=None,
        >>>                     errorRMS=0,
        >>>                     errorAngle=0,
        >>>                     number=0,
        >>>                     obsSite=None,
        >>>                     )

    point could be from type skyfield.api.Star or just a tuple of (ha, dec) where
    the format should be float or the 10micron string format.

    Command protocol (from2.8.15 onwards):
    "HH:MM:SS.SS,+dd*mm:ss.s,eeee.e,ppp#" where HH:MM:SS.SS is the hour angle
    of the alignment star in hours, minutes, seconds and hundredths of second
    (from 0h to 23h59m59.99s), +dd*mm:ss.s is the declination of the alignment
    star in degrees, arcminutes, arcseconds and tenths of arcsecond, eeee.e is
    the error between the star and the alignment model in arcseconds, ppp is the
    polar angle of the measured star with respect to the modeled star in the
    equatorial system in degrees from 0 to 359 (0 towards the north pole,
    90 towards east).
    """

    __all__ = ['ModelStar',
               ]

    log = logging.getLogger(__name__)

    def __init__(self,
                 coord=None,
                 errorRMS=None,
                 errorAngle=None,
                 number=None,
                 obsSite=None,
                 ):

        self.obsSite = obsSite
        self.coord = coord
        self.errorRMS = errorRMS
        self.errorAngle = errorAngle
        self.number = number

    @property
    def coord(self):
        return self._coord

    @coord.setter
    def coord(self, value):
        self._coord = None
        self._az = None
        self._alt = None

        if not isinstance(value, (tuple, list, Star)):
            return
        if not self.obsSite:
            return

        loc = self.obsSite.location
        if not loc:
            return

        if isinstance(value, Star):
            self._coord = value
            ha = self._coord.ra.hours
            dec = self._coord.dec.degrees

        else:
            if len(value) != 2:
                return

            ha, dec = value
            ha = stringToDegree(ha)
            dec = stringToDegree(dec)

            if not ha or not dec:
                self.log.warning('Malformed value: {0}'.format(value))
                return
            self._coord = Star(ra_hours=ha, dec_degrees=dec)

        lat = loc.latitude.degrees
        alt, az = topoToAltAz(ha, dec, lat)
        self._alt = Angle(degrees=alt)
        self._az = Angle(degrees=az)

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = valueToInt(value)

    @property
    def errorRMS(self):
        return self._errorRMS

    @errorRMS.setter
    def errorRMS(self, value):
        self._errorRMS = valueToFloat(value)

    @property
    def errorAngle(self):
        return self._errorAngle

    @errorAngle.setter
    def errorAngle(self, value):
        if isinstance(value, Angle):
            self._errorAngle = value

        else:
            self._errorAngle = valueToAngle(value)

    @property
    def alt(self):
        return self._alt

    @alt.setter
    def alt(self, value):
        self._alt = valueToFloat(value)

    @property
    def az(self):
        return self._az

    @az.setter
    def az(self, value):
        self._az = valueToFloat(value)

    def errorRA(self):
        if self._errorRMS is not None and self._errorAngle is not None:
            return self._errorRMS * numpy.sin(self._errorAngle.radians)
        else:
            return None

    def errorDEC(self):
        if self._errorRMS is not None and self._errorAngle is not None:
            return self._errorRMS * numpy.cos(self._errorAngle.radians)
        else:
            return None

    def __gt__(self, other):
        if other > self._errorRMS:
            return True
        else:
            return False

    def __ge__(self, other):
        if other >= self._errorRMS:
            return True
        else:
            return False

    def __lt__(self, other):
        if other < self._errorRMS:
            return True
        else:
            return False

    def __le__(self, other):
        if other <= self._errorRMS:
            return True
        else:
            return False

    def __eq__(self, other):
        if other == self._errorRMS:
            return True
        else:
            return False
