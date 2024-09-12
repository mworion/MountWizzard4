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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
import numpy as np
from skyfield.api import Angle
from astropy.io import fits

# local import
from base.transform import JNowToJ2000
from mountcontrol.convert import convertToAngle, convertRaToAngle, convertDecToAngle
from mountcontrol.convert import formatLatToText, formatLonToText


log = logging.getLogger()


def getCoordinatesFromHeader(header: fits.Header) -> [Angle, Angle]:
    """
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
        log.debug('Decimal coordinates used')
    elif hasSexagesimal:
        ra = convertRaToAngle(header['OBJCTRA'])
        dec = convertDecToAngle(header['OBJCTDEC'])
        log.debug('Sexagesimal coordinates used')
    else:
        ra = Angle(hours=0)
        dec = Angle(degrees=0)
        log.debug('No coordinates found')

    return ra, dec


def getSQMFromHeader(header: fits.Header) -> float:
    """
    """
    for key in ['SQM', 'SKY-QLTY', 'MPSAS']:
        value = header.get(key)
        if value is not None:
            return float(value)
    return 0


def getExposureFromHeader(header: fits.Header) -> float:
    """
    """
    for key in ['EXPOSURE', 'EXPTIME']:
        value = header.get(key)
        if value is None:
            continue
        break
    else:
        return 0
    return float(value)


def getScaleFromHeader(header: fits.Header) -> float:
    """
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
        scale = 0
    return scale


def getCoordinatesFromWCSHeader(header: fits.Header) -> [Angle, Angle]:
    """
    """
    ra = Angle(hours=float(header.get('CRVAL1', 0)) * 24 / 360)
    dec = Angle(degrees=float(header.get('CRVAL2', 0)))
    return ra, dec


def calcAngleScaleFromWCSHeader(header: fits.Header) -> [float, float, bool]:
    """
    """
    CD11 = header.get('CD1_1', 0)
    CD12 = header.get('CD1_2', 0)
    CD21 = header.get('CD2_1', 0)
    CD22 = header.get('CD2_2', 0)

    mirrored = (CD11 * CD22 - CD12 * CD21) < 0
    angleRad = np.arctan2(CD12, CD11)
    angle = np.degrees(angleRad)
    scale = CD11 / np.cos(angleRad) * 3600

    return angle, scale, mirrored


def writeHeaderCamera(header: fits.Header, camera) -> fits.Header:
    """
    """
    data = camera.data
    header.append(('OBJECT', 'SKY_OBJECT', 'default name from MW4'))
    header.append(('AUTHOR', 'MountWizzard4', 'default name from MW4'))
    header.append(('FRAME', 'Light', 'Modeling works with light frames'))
    header.append(('EQUINOX', 2000, 'All data is stored in J2000'))
    header.append(('OBSERVER', 'MW4'))
    t = camera.obsSite.timeJD
    header.append(('DATE-OBS', t.tt_strftime('%Y-%m-%dT%H:%M:%S'), 'UTC mount'))
    header.append(('MJD-OBS', t.tt - 2400000.5, 'UTC mount'))
    header.append(('SITELAT', formatLatToText(camera.obsSite.location.latitude)))
    header.append(('SITELON', formatLonToText(camera.obsSite.location.longitude)))
    header.append(('SITEELEV', camera.obsSite.location.elevation.m))

    header.append(('PIXSIZE1', data['CCD_INFO.CCD_PIXEL_SIZE_X'] * camera.binning))
    header.append(('PIXSIZE2', data['CCD_INFO.CCD_PIXEL_SIZE_Y'] * camera.binning))
    header.append(('XPIXSZ', data['CCD_INFO.CCD_PIXEL_SIZE_X'] * camera.binning))
    header.append(('YPIXSZ', data['CCD_INFO.CCD_PIXEL_SIZE_Y'] * camera.binning))
    header.append(('XBINNING', camera.binning, 'MW4 same binning x/y'))
    header.append(('YBINNING', camera.binning, 'MW4 same binning x/y'))
    scale = camera.binning / camera.focalLength * 206.265
    header.append(('FOCALLEN', camera.focalLength, 'Data from driver / manual input'))
    header.append(('SCALE', data['CCD_INFO.CCD_PIXEL_SIZE_X'] * scale))
    header.append(('EXPTIME', camera.expTime))
    header.append(('CCD-TEMP', data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', 0)))
    return header

def writeHeaderPointing(header: fits.Header, camera) -> fits.Header:
    """
    """
    ra, dec = JNowToJ2000(camera.obsSite.raJNow, camera.obsSite.decJNow,
                          camera.obsSite.timeJD)
    header.append(('RA', ra._degrees, 'Float value in degree'))
    header.append(('DEC', dec.degrees, 'Float value in degree'))
    return header
