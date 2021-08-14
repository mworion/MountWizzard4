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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from skyfield.api import Angle

# local import
from gui.utilities.toolsQtWidget import MWidget
from mountcontrol.convert import convertToAngle

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
        hasCoordFloat = True
    else:
        hasCoordFloat = False

    if 'OBJCTRA' in header and 'OBJCTDEC' in header:
        hasCoordDeg = True
    else:
        hasCoordDeg = False

    if hasCoordFloat:
        ra = convertToAngle(header['RA'], isHours=True)
        dec = convertToAngle(header['DEC'], isHours=False)
    elif hasCoordDeg:
        ra = MWidget.convertRaToAngle(header['OBJCTRA'])
        dec = MWidget.convertDecToAngle(header['OBJCTDEC'])
    else:
        ra = Angle(hours=0)
        dec = Angle(degrees=0)

    log.debug(f'HasFloat: [{hasCoordFloat}], HasDeg: [{hasCoordDeg}]')
    log.debug(f'Ra:[{ra}], Dec: [{dec}], Header:[{header}]')

    return ra, dec


def getSQM(header={}):
    """
    :param header:
    :return:
    """
    sqm = max(float(header.get('SQM', 0)),
              float(header.get('SKY-QLTY', 0)),
              float(header.get('MPSAS', 0)),
              )
    return sqm


def getExposure(header={}):
    """
    :param header:
    :return:
    """
    expTime = max(float(header.get('EXPOSURE', 0)),
                  float(header.get('EXPTIME', 0)),
                  )
    return expTime


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
        scale = 1.0

    return scale
