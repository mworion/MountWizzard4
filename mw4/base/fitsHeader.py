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

# external packages
from skyfield.api import Angle

# local import
from mountcontrol.convert import convertToAngle, convertRaToAngle, convertDecToAngle

__all__ = ['getCoordinates',
           'getSQM',
           'getExposure',
           'getScale',
           ]

log = logging.getLogger()


def getCoordinates(header={}):
    """
    :param header:
    :return:
    """
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
    elif hasSexagesimal:
        ra = convertRaToAngle(header['OBJCTRA'])
        dec = convertDecToAngle(header['OBJCTDEC'])
    else:
        ra = Angle(hours=0)
        dec = Angle(degrees=0)

    log.trace(f'HasFloat: [{hasDecimal}], HasDeg: [{hasSexagesimal}], '
              f'Header:[{header}]')
    log.debug(f'HasFloat: [{hasDecimal}], HasDeg: [{hasSexagesimal}]')
    log.debug(f'Ra:[{ra}][{ra.hours}], Dec: [{dec}][{dec.degrees}]')

    return ra, dec


def getSQM(header={}):
    """
    :param header:
    :return:
    """
    for key in ['SQM', 'SKY-QLTY', 'MPSAS']:
        value = header.get(key)
        if value is None:
            continue
        break
    else:
        return None
    return float(value)


def getExposure(header={}):
    """
    :param header:
    :return:
    """
    for key in ['EXPOSURE', 'EXPTIME']:
        value = header.get(key)
        if value is None:
            continue
        break
    else:
        return None
    return float(value)


def getScale(header={}):
    """
    :param header:
    :return:
    """
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
