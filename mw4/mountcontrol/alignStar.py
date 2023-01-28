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
import skyfield.api

# local imports
from mountcontrol.convert import valueToAngle
from mountcontrol.convert import stringToAngle


class AlignStar(object):
    """
    The class AlignStar inherits all information and handling of the coordinates of
    a pointing direction of the nominal mount coordinates and the plate solved
    coordinates, which were derived from a taken image at the scope
    the coordinates both are in JNow topocentric

        >>> settings = AlignStar(
        >>>                     )

    coordinates could be from type skyfield.api.Star or just a tuple of (ha, dec) where
    the format should be float or the 10micron string format.

    """

    __all__ = ['AlignStar',
               ]

    log = logging.getLogger(__name__)

    def __init__(self,
                 mCoord=None,
                 pierside=None,
                 sCoord=None,
                 sidereal=None,
                 ):

        self.mCoord = mCoord
        self.pierside = pierside
        self.sCoord = sCoord
        self.sidereal = sidereal

    @property
    def mCoord(self):
        return self._mCoord

    @mCoord.setter
    def mCoord(self, value):
        if isinstance(value, skyfield.api.Star):
            self._mCoord = value
            return

        if not isinstance(value, (tuple, list)):
            self._mCoord = None
            return

        if len(value) != 2:
            self._mCoord = None
            return

        ra, dec = value
        if isinstance(ra, str):
            ra = stringToAngle(ra, preference='hours')
        if isinstance(ra, float):
            ra = valueToAngle(ra, preference='hours')
        if isinstance(dec, str):
            dec = stringToAngle(dec)
        if isinstance(dec, float):
            dec = valueToAngle(dec)

        if not ra or not dec:
            self._mCoord = None
            self.log.warning('Malformed value: {0}'.format(value))
            return

        self._mCoord = skyfield.api.Star(ra=ra,
                                         dec=dec)

    @property
    def pierside(self):
        return self._pierside

    @pierside.setter
    def pierside(self, value):
        if value in ['E', 'W', 'e', 'w']:
            value = value.capitalize()
            self._pierside = value

        else:
            self._pierside = None
            self.log.warning('Malformed value: {0}'.format(value))

    @property
    def sCoord(self):
        return self._sCoord

    @sCoord.setter
    def sCoord(self, value):
        if isinstance(value, skyfield.api.Star):
            self._sCoord = value
            return

        if not isinstance(value, (tuple, list)):
            self._sCoord = None
            return

        if len(value) != 2:
            self._sCoord = None
            return

        ra, dec = value
        if isinstance(ra, str):
            ra = stringToAngle(ra, preference='hours')
        if isinstance(ra, float):
            ra = valueToAngle(ra, preference='hours')
        if isinstance(dec, str):
            dec = stringToAngle(dec)
        if isinstance(dec, float):
            dec = valueToAngle(dec)

        if not ra or not dec:
            self._sCoord = None
            self.log.warning('Malformed value: {0}'.format(value))
            return

        self._sCoord = skyfield.api.Star(ra=ra,
                                         dec=dec)

    @property
    def sidereal(self):
        return self._sidereal

    @sidereal.setter
    def sidereal(self, value):
        if isinstance(value, str):
            self._sidereal = stringToAngle(value, preference='hours')

        elif isinstance(value, float):
            self._sidereal = valueToAngle(value, preference='hours')

        elif isinstance(value, skyfield.api.Angle):
            self._sidereal = value

        else:
            self._sidereal = None
