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

__all__ = ['getCoordinates',
           'getSQM',
           'getExposure',
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
        ra = Angle(degrees=float(header['RA']))
        dec = Angle(degrees=float(header['DEC']))
    elif hasCoordDeg:
        ra = MWidget.convertRaToAngle(header['OBJCTRA'])
        dec = MWidget.convertDecToAngle(header['OBJCTDEC'])
    else:
        ra = Angle(hours=0)
        dec = Angle(degrees=0)

    return ra, dec


def getSQM(header={}):
    """
    :param header:
    :return:
    """
    sqm = max(header.get('SQM', 0),
              header.get('SKY-QLTY', 0),
              header.get('MPSAS', 0),
              )
    return sqm


def getExposure(header={}):
    """
    :param header:
    :return:
    """
    expTime = max(header.get('EXPOSURE', 0),
                  header.get('EXPTIME', 0)
                  )
    return expTime
