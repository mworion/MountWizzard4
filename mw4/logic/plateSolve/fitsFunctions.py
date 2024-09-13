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
import os
from pathlib import Path

# external packages
from astropy.io import fits
from skyfield.api import Angle
import numpy as np

# local imports
from base.fitsHeader import getCoordinatesFromHeader, calcAngleScaleFromWCSHeader


def getSolutionFromWCSHeader(wcsHeader: fits.Header, imageHeader: fits.Header) -> None:
    """
    CRVAL1 and CRVAL2 give the center coordinate as right ascension and
    declination or longitude and latitude in decimal degrees.
    """
    raJ2000 = convertToAngle(header.get('CRVAL1', 0), isHours=True)
    decJ2000 = convertToAngle(header.get('CRVAL2', 0), isHours=False)
    
    angle, scale, mirrored = self.calcAngleScaleFromWCSHeader(header=wcsHeader)
    raMount, decMount = getCoordinatesFromHeader(header=imageHeader)

    deltaRA = Angle(degrees=(raJ2000._degrees - raMount._degrees))
    deltaDEC = Angle(degrees=(decJ2000.degrees - decMount.degrees))
    error = np.sqrt(np.square(deltaRA) + np.square(deltaDEC))

    solution = {
        'raJ2000S': raJ2000,
        'decJ2000S': decJ2000,
        'errorRA_S': deltaRA,
        'errorDEC_S': deltaDEC,
        'angleS': angle,
        'scaleS': scale,
        'errorRMS_S': error,
        'mirroredS': mirrored,
    }
    return solution
    
    
def writeSolutionToHeader(header: fits.Header, solution: dict) -> fits.Header: 
    """
    """
    header.append(('RA', solution['raJ2000S'], 'MW4 - processed'))
    header.append(('DEC', solution['decJ2000S'], 'MW4 - processed'))
    header.append(('SCALE', solution['scaleS'], 'MW4 - processed'))
    header.append(('PIXSCALE', solution['scaleS'], 'MW4 - processed'))
    header.append(('ANGLE', solution['angleS'], 'MW4 - processed'))
    header.append(('MIRRORED', solution['mirroredS'], 'MW4 - processed'))
    return header


def getImageHeader(imagePath: Path) -> fits.Header:
    """
    """
    with fits.open(imagePath) as HDU:
        return HDU[0].header

def readImageHeaderHintData(imagePath: Path) -> [Angle, Angle, float]:
    """
    """
    header = getImageHeader(imagePath)
    raHint, decHint = getCoordinatesFromHeader(header)
    scaleHint = getScaleFromHeader(header)
    return raHint, decHint, scaleHint

def updateImageFileHeaderWithSolution(imagePath: Path, solution: dict) -> fits.Header:
    """
    """
    with fits.open(imagePath, mode='update', output_verify='silentfix+warn') as HDU:
        HDU[0].header = writeSolutionToHeader(HDU[0].header, solution)
