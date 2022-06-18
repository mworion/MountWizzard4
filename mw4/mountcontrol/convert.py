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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import numpy as np
import re

# external packages
from skyfield.api import Angle

# local imports

__all__ = [
    'stringToDegree',
    'stringToAngle',
    'valueToAngle',
    'valueToFloat',
    'valueToInt',
    'topoToAltAz',
    'sexagesimalizeToInt',
    'checkIsHours',
    'convertToAngle',
    'convertToDMS',
    'convertToHMS',
    'formatLatLonToAngle',
    'convertLatToAngle',
    'convertLonToAngle',
    'convertRaToAngle',
    'convertDecToAngle',
    'formatHstrToText',
    'formatDstrToText',
    'formatLatToText',
    'formatLonToText',
]

log = logging.getLogger()

# conversion from value, which is
# sDD*MM:SS.S format to decimal value
# HH:MM:SS.SS format to decimal value
# sHH:MM:SS.SS format to decimal value


def stringToDegree(value):
    """
    stringToDegree takes any form of HMS / DMS string format and tries to
    convert it to a decimal number.

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
    if value == 'E':
        return None

    value = value.replace('*', ' ')
    value = value.replace(':', ' ')
    value = value.replace('deg', ' ')
    value = value.replace('"', ' ')
    value = value.replace('\'', ' ')
    value = value.split()

    try:
        value = [float(x) for x in value]
    except Exception:
        return None

    sign = 1 if value[0] >= 0 else -1
    value[0] = abs(value[0])

    if len(value) == 3:
        value = sign * (value[0] + value[1] / 60 + value[2] / 3600)
        return value

    elif len(value) == 2:
        value = sign * (value[0] + value[1] / 60)
        return value
    else:
        return None


def stringToAngle(value, preference='degrees'):
    """
    :param value:
    :param preference:
    :return:
    """
    value = stringToDegree(value)
    if value is not None:
        if preference == 'degrees':
            value = Angle(degrees=value, preference='degrees')
        else:
            value = Angle(hours=value, preference='hours')

    return value


def valueToAngle(value, preference='degrees'):
    """
    :param value:
    :param preference:
    :return:
    """
    value = valueToFloat(value)
    if value is not None:
        if preference == 'degrees':
            value = Angle(degrees=value, preference='degrees')
        else:
            value = Angle(hours=value, preference='hours')

    return value


def valueToFloat(value):
    """
    :param value:
    :return:
    """
    if value == 'E':
        return None
    try:
        value = float(value)
    except Exception:
        value = None
    return value


def valueToInt(value):
    """
    :param value:
    :return:
    """
    try:
        value = int(value)
    except Exception:
        value = None
    return value


def topoToAltAz(ha, dec, lat):
    """
    :param ha:
    :param dec:
    :param lat:
    :return:
    """
    if lat is None:
        log.warning('lat nof defined')
        return None, None

    ha = (ha * 360 / 24 + 360.0) % 360.0
    dec = np.radians(dec)
    ha = np.radians(ha)
    lat = np.radians(lat)
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
    value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))

    value = np.clip(value, -1, 1)

    A = np.arccos(value)
    A = np.degrees(A)
    alt = np.degrees(alt)

    if np.sin(ha) >= 0.0:
        az = 360.0 - A
    else:
        az = A

    return alt, az


def sexagesimalizeToInt(value, decimals=0):
    """
    :param value:
    :param decimals:
    :return:
    """
    sign = int(np.sign(value))
    value = abs(value)
    power = 10 ** decimals
    n = int(7200 * power * value + 1) // 2
    n, fraction = divmod(n, power)
    n, seconds = divmod(n, 60)
    n, minutes = divmod(n, 60)

    return sign, n, minutes, seconds, fraction


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
    if '+' in value:
        return False
    if '-' in value:
        return False

    return True


def convertToAngle(value, isHours=None):
    """
    convertToAngle ties to take any value and converts is to the right form in
    skyfield angles. if the value is a string, we convert it to float value. in
    case of isHours, we should have already a string, which represents hours
    inside. if the value is float and we expect to have hours, the float value is
    normally given in degrees, so we have to calculate the numbers in hours.

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
    takes the given DEC value, which should be in DMS format (but different
    types) and convert it to solve-field readable string in sDD:MM:SS

    :param dec: declination as Angle
    :return: converted value as string
    """
    if isinstance(dec, (float, int)):
        dec = Angle(degrees=dec)
    if isinstance(dec, str):
        return ''

    t = Angle.signed_dms(dec)
    sign = '+' if dec.degrees > 0 else '-'
    value = f'{sign}{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}'
    return value


def convertToHMS(ra):
    """
    takes the given RA value, which should be in HMS format (but different
    types) and convert it to solve-field readable string in HH:MM:SS

    :param ra: right ascension as Angle
    :return: converted value as string
    """
    if isinstance(ra, (float, int)):
        ra = Angle(hours=ra)

    if isinstance(ra, str):
        return ''

    t = Angle.signed_hms(ra)
    value = f'{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}'

    return value


def formatLatLonToAngle(value, pf):
    """
    :param value:
    :param pf: double character, first indicates the negative sign
    :return:
    """
    if value is None:
        return None

    value = value.strip()
    p1 = re.compile(r'(\d{1,3})([' + pf + r'])\s*(\d\d)?\s*(\d\d)?[.,]?(\d*)?')
    p2 = re.compile(r'([-+]?)(\d{1,3})[.,]?(\d*)?')
    isSexagesimal = p1.fullmatch(value) is not None
    isFloat = p2.fullmatch(value) is not None

    elements = p2.split(value)
    if isFloat:
        angle = float(value.replace(',', '.'))

    elif isSexagesimal:
        angle = float(elements[2])
        if len(elements) > 5:
            angle += float(elements[6]) / 60
        if len(elements) > 9:
            angle += float(elements[10]) / 3600
        if elements[4].startswith(pf[0]):
            angle = -angle
    else:
        return None

    if 'N' in pf:
        maxAbs = 90
    else:
        maxAbs = 180

    if angle > maxAbs:
        return None
    elif angle < -maxAbs:
        return None

    angle = Angle(degrees=angle)
    return angle


def convertLatToAngle(value):
    """
    :param value:
    :return:
    """
    angle = formatLatLonToAngle(value, 'SN')
    return angle


def convertLonToAngle(value):
    """
    :param value:
    :return:
    """
    angle = formatLatLonToAngle(value, 'WE')
    return angle


def convertRaToAngle(value):
    """
    :param value:
    :return:
    """
    if value is None:
        return None
    if isinstance(value, (float, int)):
        value = str(value)

    value = value.strip()
    p1 = re.compile(r'([+-]?)(\d{1,3})H[\s:]*(\d\d)?[\s:]*(\d\d)?[.,]?(\d*)?')
    p2 = re.compile(r'([+-]?)(\d{1,3})[\s:]+(\d\d)?[\s:]*(\d\d)?[.,]?(\d*)?')
    p3 = re.compile(r'([+-]?)(\d{1,3})[.,]?(\d*)?')
    isP1 = p1.fullmatch(value) is not None
    isP2 = p2.fullmatch(value) is not None
    isSexagesimal = isP1 or isP2
    isFloat = p3.fullmatch(value) is not None

    if isP1:
        elements = p1.split(value)
    elif isP2:
        elements = p2.split(value)
    else:
        elements = ''

    if isFloat:
        angle = float(value.replace(',', '.'))
    elif isSexagesimal:
        angle = float(elements[2])
        if elements[3] is not None:
            angle += float(elements[3]) / 60
        if elements[4] is not None:
            angle += float(elements[4]) / 3600
    else:
        return None

    if angle >= 24:
        return None
    if angle < 0:
        return None
    if isFloat:
        angle = Angle(hours=angle / 360 * 24)
    elif isSexagesimal:
        angle = Angle(hours=angle)

    return angle


def convertDecToAngle(value):
    """
    :param value:
    :return:
    """
    if value is None:
        return None
    if isinstance(value, (float, int)):
        value = str(value)

    value = value.strip()
    p1 = re.compile(r'([+-]?)(\d{1,3})Deg[\s:]*(\d\d)?[\s:]*(\d\d)?[.,]?(\d*)?')
    p2 = re.compile(r'([+-]?)(\d{1,3})[\s:]+(\d\d)?[\s:]*(\d\d)?[.,]?(\d*)?')
    p3 = re.compile(r'([+-]?)(\d{1,3})[.,]?(\d*)?')
    isP1 = p1.fullmatch(value) is not None
    isP2 = p2.fullmatch(value) is not None
    isSexagesimal = isP1 or isP2
    isFloat = p3.fullmatch(value) is not None

    if isP1:
        elements = p1.split(value)
    elif isP2:
        elements = p2.split(value)
    else:
        elements = ''

    if isFloat:
        angle = float(value.replace(',', '.'))

    elif isSexagesimal:
        angle = float(elements[2])
        if elements[3] is not None:
            angle += float(elements[3]) / 60
        if elements[4] is not None:
            angle += float(elements[4]) / 3600
        if elements[1].startswith('-'):
            angle = -angle
    else:
        return None

    if angle > 90:
        return None
    if angle < -90:
        return None

    angle = Angle(degrees=angle)
    return angle


def formatHstrToText(angle):
    """
    :param angle:
    :return:
    """
    formatStr = '{1:02}:{2:02}:{3:02}'
    return angle.hstr(format=formatStr)


def formatDstrToText(angle):
    """
    :param angle:
    :return:
    """
    formatStr = '{0:+>1}{1:02}:{2:02}:{3:02}'
    return angle.dstr(format=formatStr)


def formatLatToText(angle):
    """
    :param angle:
    :return:
    """
    sgn, h, m, s, frac = sexagesimalizeToInt(angle.degrees, 0)
    sign = 'N' if sgn >= 0 else 'S'
    text = f'{h:02d}{sign} {m:02d} {s:02d}'
    return text


def formatLonToText(angle):
    """
    :param angle:
    :return:
    """
    sgn, h, m, s, frac = sexagesimalizeToInt(angle.degrees, 0)
    sign = 'E' if sgn >= 0 else 'W'
    text = f'{h:03d}{sign} {m:02d} {s:02d}'
    return text
