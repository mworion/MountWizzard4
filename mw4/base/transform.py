############################################################
# -*- coding: utf-8 -*-
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# (c) 2016, 2017, 2018#
# Licence APL2.0
#
############################################################
# standard libraries
import logging
from threading import Lock

# external packages
import numpy as np

# noinspection PyProtectedMember
import erfa
from skyfield.api import Angle

# local import

__all__ = [
    'J2000ToJNow',
    'J2000ToAltAz',
    'JNowToJ2000',
]

log = logging.getLogger()

lock = Lock()


def JNowToJ2000(ra, dec, timeJD):
    """
    JNowToJ2000 uses the ERFA library which actually is included in the astropy package for
    doing the transform. If future releases of astropy this might be a separate package and
    will be imported and used adequately.

    :param ra:
    :param dec:
    :param timeJD:
    :return:
    """

    if not isinstance(ra, Angle):
        return Angle(hours=0), Angle(degrees=0)

    if not isinstance(dec, Angle):
        return Angle(hours=0), Angle(degrees=0)

    with lock:
        ra = ra.radians
        dec = dec.radians

        ra = erfa.anp(ra + erfa.eo06a(timeJD.tt, 0.0))

        raConv, decConv, _ = erfa.atic13(ra, dec, timeJD.ut1, 0.0)

        ra = Angle(radians=raConv, preference='hours')
        dec = Angle(radians=decConv, preference='degrees')
        return ra, dec


def J2000ToJNow(ra, dec, timeJD):
    """
    J2000ToJNow uses the ERFA library which actually is included in the astropy package for
    doing the transform. If future releases of astropy this might be a separate package and
    will be imported and used adequately.

    :param ra:
    :param dec:
    :param timeJD:
    :return:
    """

    if not isinstance(ra, Angle):
        return Angle(hours=0), Angle(degrees=0)

    if not isinstance(dec, Angle):
        return Angle(hours=0), Angle(degrees=0)

    with lock:
        ra = ra.radians
        dec = dec.radians

        raConv, decConv, eo = erfa.atci13(ra, dec, 0, 0, 0, 0, timeJD.ut1, 0)

        raConv = erfa.anp(raConv - eo)
        ra = Angle(radians=raConv, preference='hours')
        dec = Angle(radians=decConv, preference='degrees')
        return ra, dec


def J2000ToAltAz(ra, dec, timeJD, location):
    """
    J2000ToAltAz uses the ERFA library which actually is included in the astropy package for
    doing the transform. If future releases of astropy this might be a separate package and
    will be imported and used adequately.

    Please be aware, that all refraction corrections are made in the mount itself, so all
    parameters which are related to RC are set to zero.

    :param ra:
    :param dec:
    :param timeJD:
    :param location:
    :return:
    """

    if not isinstance(ra, Angle):
        return Angle(degrees=0), Angle(degrees=0)

    if not isinstance(dec, Angle):
        return Angle(degrees=0), Angle(degrees=0)

    with lock:
        ra = ra.radians
        dec = dec.radians
        lat = location.latitude.radians
        lon = location.longitude.radians
        elevation = location.elevation.m

        aob, zob, hob, dob, rob, eo = erfa.atco13(ra,
                                                  dec,
                                                  0.0,
                                                  0.0,
                                                  0.0,
                                                  0.0,
                                                  timeJD.ut1,
                                                  0.0,
                                                  0,
                                                  lon,
                                                  lat,
                                                  elevation,
                                                  0.0,
                                                  0.0,
                                                  0.0,
                                                  0.0,
                                                  0.0,
                                                  0.0)
        decConv = np.pi / 2 - zob

        ra = Angle(radians=aob, preference='degrees')
        dec = Angle(radians=decConv, preference='degrees')

        return ra, dec
