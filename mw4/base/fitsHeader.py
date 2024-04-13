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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
import numpy as np
from skyfield.api import Angle

# local import
from mountcontrol.convert import convertToAngle, convertRaToAngle, convertDecToAngle

__all__ = ['getCoordinates',
           'getSQM',
           'getExposure',
           'getScale',
           ]

log = logging.getLogger()


def getCoordinates(header=None):
    """
    :param header:
    :return:
    """
    if header is None:
        header = {}

    if 'RA' in header and 'DEC' in header:
        hasDecimal = True
    else:
        hasDecimal = False

    if 'OBJCTRA' in header and 'OBJCTDEC' in header:
        hasSexagesimal = True
    else:
        hasSexagesimal = False

    if hasDecimal:
        ra = convertToAngle(header['RA'], isHours=True)
        dec = convertToAngle(header['DEC'], isHours=False)
        log.debug('Decimal coordinates used')
    elif hasSexagesimal:
        ra = convertRaToAngle(header['OBJCTRA'])
        dec = convertDecToAngle(header['OBJCTDEC'])
        log.debug('Sexagesimal coordinates used')
    else:
        ra = Angle(hours=0)
        dec = Angle(degrees=0)
        log.debug('No coordinates found')

    log.trace(f'Header:[{header}]')
    log.debug(f'Ra:[{ra}][{ra.hours}][{ra._degrees}], Dec: [{dec}][{dec.degrees}]')

    return ra, dec


def getCoordinatesWCS(header=None):
    """
    :param header:
    :return:
    """
    ra = Angle(hours=float(header.get('CRVAL1')) * 24 / 360)
    dec = Angle(degrees=float(header.get('CRVAL2')))

    return ra, dec


def getSQM(header=None):
    """
    :param header:
    :return:
    """
    if header is None:
        header = {}

    for key in ['SQM', 'SKY-QLTY', 'MPSAS']:
        value = header.get(key)
        if value is None:
            continue
        break
    else:
        return None
    return float(value)


def getExposure(header=None):
    """
    :param header:
    :return:
    """
    if header is None:
        header = {}

    for key in ['EXPOSURE', 'EXPTIME']:
        value = header.get(key)
        if value is None:
            continue
        break
    else:
        return None
    return float(value)


def getScale(header=None):
    """
    :param header:
    :return:
    """
    if header is None:
        header = {}

    hasScale = 'SCALE' in header
    focalLength = float(header.get('FOCALLEN', 0))
    binning = float(header.get('XBINNING', 0))
    pixelSize = max(float(header.get('XPIXSZ', 0)),
                    float(header.get('PIXSIZE1', 0)),
                    )
    hasAlternatives = focalLength and binning and pixelSize

    if hasScale:
        scale = float(header.get('SCALE', 0))
    elif hasAlternatives:
        scale = pixelSize * binning / focalLength * 206.265
    else:
        scale = None

    return scale


def calcAngleScaleFromWCS(wcsHeader=None):
    """
    calcAngleScaleFromWCS as the name says. important is to use the numpy
    arctan2 function, because it handles the zero points and extend the
    calculation back to the full range from -pi to pi

    :return: angle in degrees and scale in arc second per pixel (app) and
             status if image is mirrored (not rotated for 180 degrees because
             of the mount flip)
    """
    CD11 = wcsHeader.get('CD1_1', 0)
    CD12 = wcsHeader.get('CD1_2', 0)
    CD21 = wcsHeader.get('CD2_1', 0)
    CD22 = wcsHeader.get('CD2_2', 0)

    mirrored = (CD11 * CD22 - CD12 * CD21) < 0

    angleRad = np.arctan2(CD12, CD11)
    angle = np.degrees(angleRad)
    scale = CD11 / np.cos(angleRad) * 3600

    return angle, scale, mirrored
