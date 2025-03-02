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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
from pathlib import Path

# external packages
import numpy as np
from astropy.io import fits
from skyfield.units import Angle

# local import
from base.transform import JNowToJ2000
from mountcontrol.convert import convertToAngle, convertRaToAngle, convertDecToAngle
from mountcontrol.convert import formatLatToText, formatLonToText


log = logging.getLogger()


def getImageHeader(imagePath: Path) -> fits.Header:
    """ """
    with fits.open(imagePath) as HDU:
        return HDU[0].header


def getCoordinatesFromHeader(header: fits.Header) -> [Angle, Angle]:
    """ """
    if "RA" in header and "DEC" in header:
        hasDecimal = True
    else:
        hasDecimal = False

    if "OBJCTRA" in header and "OBJCTDEC" in header:
        hasSexagesimal = True
    else:
        hasSexagesimal = False

    if hasDecimal:
        ra = convertToAngle(header["RA"], isHours=True)
        dec = convertToAngle(header["DEC"], isHours=False)
        log.debug("Decimal coordinates used")
    elif hasSexagesimal:
        ra = convertRaToAngle(header["OBJCTRA"])
        dec = convertDecToAngle(header["OBJCTDEC"])
        log.debug("Sexagesimal coordinates used")
    else:
        ra = None
        dec = None
        log.debug("No coordinates found")

    return ra, dec


def getSQMFromHeader(header: fits.Header) -> float:
    """ """
    for key in ["SQM", "SKY-QLTY", "MPSAS"]:
        value = header.get(key)
        if value is not None:
            return float(value)
    return 0


def getExposureFromHeader(header: fits.Header) -> float:
    """ """
    for key in ["EXPOSURE", "EXPTIME"]:
        value = header.get(key)
        if value is None:
            continue
        break
    else:
        return 0.0
    return float(value)


def getScaleFromHeader(header: fits.Header) -> float:
    """ """
    hasScale = "SCALE" in header
    focalLength = float(header.get("FOCALLEN", 0))
    binning = float(header.get("XBINNING", 0))
    pixelSize = max(float(header.get("XPIXSZ", 0)), float(header.get("PIXSIZE1", 0)))
    hasAlternatives = focalLength and binning and pixelSize

    if hasScale:
        scale = float(header.get("SCALE", 0))
    elif hasAlternatives:
        scale = pixelSize * binning / focalLength * 206.265
    else:
        scale = 0
    return scale


def getHintFromImageFile(imagePath: Path) -> [Angle, Angle, float]:
    """ """
    header = getImageHeader(imagePath)
    raHint, decHint = getCoordinatesFromHeader(header)
    scaleHint = getScaleFromHeader(header)
    return raHint, decHint, scaleHint


def getCoordinatesFromWCSHeader(header: fits.Header) -> [Angle, Angle]:
    """ """
    ra = Angle(hours=float(header.get("CRVAL1", 0)) * 24 / 360)
    dec = Angle(degrees=float(header.get("CRVAL2", 0)))
    return ra, dec


def calcAngleScaleFromWCSHeader(header: fits.Header) -> [Angle, float, bool]:
    """ """
    CD11 = header.get("CD1_1", 0)
    CD12 = header.get("CD1_2", 0)
    CD21 = header.get("CD2_1", 0)
    CD22 = header.get("CD2_2", 0)

    mirrored = (CD11 * CD22 - CD12 * CD21) < 0
    angleRad = np.arctan2(CD12, CD11)
    angle = Angle(radians=np.degrees(angleRad))
    scale = CD11 / np.cos(angleRad) * 3600

    return angle, scale, mirrored


def writeHeaderCamera(header: fits.Header, camera) -> fits.Header:
    """ """
    data = camera.data
    header.append(("OBJECT", "SKY_OBJECT", "default name from MW4"))
    header.append(("AUTHOR", "MountWizzard4", "default name from MW4"))
    header.append(("FRAME", "Light", "Modeling works with light frames"))
    header.append(("EQUINOX", 2000, "All data is stored in J2000"))
    header.append(("OBSERVER", "MW4"))
    t = camera.obsSite.timeJD
    header.append(("DATE-OBS", t.tt_strftime("%Y-%m-%dT%H:%M:%S"), "UTC mount"))
    header.append(("MJD-OBS", t.tt - 2400000.5, "UTC mount"))
    header.append(("SITELAT", formatLatToText(camera.obsSite.location.latitude)))
    header.append(("SITELON", formatLonToText(camera.obsSite.location.longitude)))
    header.append(("SITEELEV", camera.obsSite.location.elevation.m))

    header.append(("PIXSIZE1", data["CCD_INFO.CCD_PIXEL_SIZE_X"] * camera.binning))
    header.append(("PIXSIZE2", data["CCD_INFO.CCD_PIXEL_SIZE_Y"] * camera.binning))
    header.append(("XPIXSZ", data["CCD_INFO.CCD_PIXEL_SIZE_X"] * camera.binning))
    header.append(("YPIXSZ", data["CCD_INFO.CCD_PIXEL_SIZE_Y"] * camera.binning))
    header.append(("XBINNING", camera.binning, "MW4 same binning x/y"))
    header.append(("YBINNING", camera.binning, "MW4 same binning x/y"))
    scale = camera.binning / camera.focalLength * 206.265
    header.append(("FOCALLEN", camera.focalLength, "Data from driver / manual input"))
    header.append(("SCALE", data["CCD_INFO.CCD_PIXEL_SIZE_X"] * scale))
    header.append(("EXPTIME", camera.exposureTime))
    header.append(("CCD-TEMP", data.get("CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE", 0)))
    return header


def writeHeaderPointing(header: fits.Header, camera) -> fits.Header:
    """ """
    ra, dec = JNowToJ2000(camera.obsSite.raJNow, camera.obsSite.decJNow, camera.obsSite.timeJD)
    header.append(("RA", ra._degrees, "Float value in degree"))
    header.append(("DEC", dec.degrees, "Float value in degree"))
    return header


def writeSolutionToHeader(header: fits.Header, solution: dict) -> fits.Header:
    """ """
    header.append(("RA", solution["raJ2000S"]._degrees, "MW4 - processed"))
    header.append(("DEC", solution["decJ2000S"].degrees, "MW4 - processed"))
    header.append(("SCALE", solution["scaleS"], "MW4 - processed"))
    header.append(("PIXSCALE", solution["scaleS"], "MW4 - processed"))
    header.append(("ANGLE", solution["angleS"].degrees, "MW4 - processed"))
    header.append(("MIRRORED", solution["mirroredS"], "MW4 - processed"))
    return header


def updateImageFileHeaderWithSolution(imagePath: Path, solution: dict) -> None:
    """ """
    with fits.open(imagePath, mode="update", output_verify="silentfix+warn") as HDU:
        HDU[0].header = writeSolutionToHeader(HDU[0].header, solution)


def getSolutionFromWCSHeader(wcsHeader: fits.Header, imageHeader: fits.Header) -> dict:
    """
    CRVAL1 and CRVAL2 give the center coordinate as right ascension and
    declination or longitude and latitude in decimal degrees.
    """
    raJ2000 = convertToAngle(wcsHeader.get("CRVAL1", 0), isHours=True)
    decJ2000 = convertToAngle(wcsHeader.get("CRVAL2", 0), isHours=False)

    angle, scale, mirrored = calcAngleScaleFromWCSHeader(header=wcsHeader)
    raMount, decMount = getCoordinatesFromHeader(header=imageHeader)

    deltaRA_raw = raJ2000._degrees - raMount._degrees
    deltaDEC_raw = decJ2000.degrees - decMount.degrees
    error = np.sqrt(np.square(deltaRA_raw) + np.square(deltaDEC_raw))

    solution = {
        "raJ2000S": raJ2000,
        "decJ2000S": decJ2000,
        "errorRA_S": Angle(degrees=deltaRA_raw),
        "errorDEC_S": Angle(degrees=deltaDEC_raw),
        "angleS": angle,
        "scaleS": scale,
        "errorRMS_S": error,
        "mirroredS": mirrored,
    }
    return solution
