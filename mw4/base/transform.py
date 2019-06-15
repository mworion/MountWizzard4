############################################################
# -*- coding: utf-8 -*-
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2016, 2017, 2018
#
# Licence APL2.0
#
############################################################
# standard libraries
import logging
from threading import Lock
# external packages
import numpy as np
# noinspection PyProtectedMember
from astropy import _erfa as ERFA
from skyfield.api import Angle
# local import


__all__ = [
    'J2000ToJNow',
    'J2000ToAltAz',
    'JNowToJ2000',
    'convertToAngle',
    'convertToDMS',
    'convertToHMS',
]
version = '0.1'
logger = logging.getLogger()

_lock = Lock()


def JNowToJ2000(ra, dec, timeJD):
    with _lock:
        ra = ra.radians
        dec = dec.radians

        ra = ERFA.anp(ra + ERFA.eo06a(timeJD.tt, 0.0))

        raConv, decConv, _ = ERFA.atic13(ra, dec, timeJD.ut1, 0.0)

        ra = Angle(radians=raConv, preference='hours')
        dec = Angle(radians=decConv, preference='degrees')
        return ra, dec


def J2000ToJNow(ra, dec, timeJD):
    with _lock:
        ra = ra.radians
        dec = dec.radians

        raConv, decConv, eo = ERFA.atci13(ra, dec, 0, 0, 0, 0, timeJD.ut1, 0)

        raConv = ERFA.anp(raConv - eo)
        ra = Angle(radians=raConv, preference='hours')
        dec = Angle(radians=decConv, preference='degrees')
        return ra, dec


def J2000ToAltAz(ra, dec, timeJD, location):
    with _lock:
        ra = ra.radians
        dec = dec.radians
        lat = location.latitude.radians
        lon = location.longitude.radians
        elevation = location.elevation.m

        aob, zob, hob, dob, rob, eo = ERFA.atco13(ra,
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


def checkIsHours(value):
    """
    checkIsHours tries to distinguish if the value describes hours or degrees

    :param value: string
    :return:
    """

    if not isinstance(value, str):
        return False

    if '*' in value:
        return False
    elif '+' in value:
        return False
    elif '-' in value:
        return False
    else:
        return True


def stringToDegree(value):
    """
    stringToDegree takes any form of HMS / DMS string format and tries to convert it
    to a decimal number.

    :param value:
    :return: value as decimal in degrees or None if not succeeded
    """

    if not isinstance(value, str):
        return None
    if not len(value):
        return None
    if value.count('+') > 1:
        return None
    if value.count('-') > 1:
        return None

    # managing different coding styles
    value = value.replace('*', ' ')
    value = value.replace(':', ' ')
    value = value.replace('deg', ' ')
    value = value.replace('"', ' ')
    value = value.replace('\'', ' ')
    value = value.split()

    try:
        value = [float(x) for x in value]
    except Exception as e:
        logger.debug(f'error: {e}, value: {value}')
        return None

    sign = 1 if value[0] > 0 else -1
    value[0] = abs(value[0])

    if len(value) == 3:
        value = sign * (value[0] + value[1] / 60 + value[2] / 3600)
        return value

    elif len(value) == 2:
        value = sign * (value[0] + value[1] / 60)
        return value

    else:
        return None


def convertToAngle(value, isHours=None):
    """
    convertToAngle ties to take any value and converts is to the right form in skyfield
    angles. if the value is a string, we convert it to float value. in case of isHours,
    we should have already a string, which represents hours inside. if the value is float
    and we expect to have hours, the float value is normally given in degrees, so we have
    to calculate the numbers in hours.

    :param value:
    :param isHours:
    :return: angle as skyfield angle
    """

    if isinstance(value, str):
        value = stringToDegree(value)
        if value is None:
            return None
    else:
        if isHours:
            value *= 24 / 360

    if isHours:
        angle = Angle(hours=value)
    else:
        angle = Angle(degrees=value)

    return angle


def convertToDMS(dec):
    """
    takes the given DEC value, which should be in DMS format (but different types) and
    convert it to solve-field readable string in sDD:MM:SS

    :param dec: declination as Angle
    :return: converted value as string
    """

    t = Angle.signed_dms(dec)
    sign = '+' if dec.degrees > 0 else '-'
    value = f'{sign}{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}'

    return value


def convertToHMS(ra):
    """
    takes the given RA value, which should be in HMS format (but different types) and
    convert it to solve-field readable string in HH:MM:SS

    :param ra: right ascension as Angle
    :return: converted value as string
    """

    t = Angle.signed_hms(ra)
    value = f'{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}'

    return value


def sphericalToCartesian(altitude=0, azimuth=0, radius=0):
    rcos_theta = radius * np.cos(altitude)
    x = rcos_theta * np.cos(azimuth)
    y = rcos_theta * np.sin(azimuth)
    z = radius * np.sin(altitude)
    return x, y, z


def cartesianToSpherical(x=0, y=0, z=0):
    hxy = np.hypot(x, y)
    radius = np.hypot(hxy, z)
    altitude = np.arctan2(z, hxy)
    azimuth = np.arctan2(y, x)
    return altitude, azimuth, radius


def polarToCartesian(theta=0, radius=0):
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    return x, y


def cartesianToPolar(x=0, y=0):
    radius = np.hypot(x, y)
    theta = np.arctan2(y, x)
    return theta, radius
