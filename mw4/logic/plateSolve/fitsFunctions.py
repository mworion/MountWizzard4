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
from pathlib import Path

# external packages
from astropy.io import fits
from skyfield.api import Angle
import numpy as np

# local imports
from mountcontrol.convert import convertToAngle
from base.fitsHeader import getCoordinatesFromHeader, getScaleFromHeader, calcAngleScaleFromWCSHeader


def getSolutionFromWCSHeader(wcsHeader: fits.Header, imageHeader: fits.Header) -> dict:
    """
    CRVAL1 and CRVAL2 give the center coordinate as right ascension and
    declination or longitude and latitude in decimal degrees.
    """
    raJ2000 = convertToAngle(wcsHeader.get('CRVAL1', 0), isHours=True)
    decJ2000 = convertToAngle(wcsHeader.get('CRVAL2', 0), isHours=False)
    
    angle, scale, mirrored = calcAngleScaleFromWCSHeader(header=wcsHeader)
    raMount, decMount = getCoordinatesFromHeader(header=imageHeader)

    deltaRA_raw = raJ2000._degrees - raMount._degrees
    deltaDEC_raw = decJ2000.degrees - decMount.degrees
    error = np.sqrt(np.square(deltaRA_raw) + np.square(deltaDEC_raw))

    solution = {
        'raJ2000S': raJ2000,
        'decJ2000S': decJ2000,
        'errorRA_S': Angle(degrees=deltaRA_raw),
        'errorDEC_S': Angle(degrees=deltaDEC_raw),
        'angleS': angle,
        'scaleS': scale,
        'errorRMS_S': error,
        'mirroredS': mirrored,
    }
    return solution
    
    
def writeSolutionToHeader(header: fits.Header, solution: dict) -> fits.Header: 
    """
    """
    header.append(('RA', solution['raJ2000S']._degrees, 'MW4 - processed'))
    header.append(('DEC', solution['decJ2000S'].degrees, 'MW4 - processed'))
    header.append(('SCALE', solution['scaleS'], 'MW4 - processed'))
    header.append(('PIXSCALE', solution['scaleS'], 'MW4 - processed'))
    header.append(('ANGLE', solution['angleS'].degrees, 'MW4 - processed'))
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
