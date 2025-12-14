############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import mw4.logic
import numpy as np
import pytest
import unittest.mock as mock
from astropy.io import fits
from mw4.logic.fits.fitsFunction import (
    calcAngleScaleFromWCSHeader,
    getCoordinatesFromHeader,
    getCoordinatesFromWCSHeader,
    getExposureFromHeader,
    getHintFromImageFile,
    getImageHeader,
    getScaleFromHeader,
    getSolutionFromWCSHeader,
    getSQMFromHeader,
    updateImageFileHeaderWithSolution,
    writeHeaderCamera,
    writeHeaderPointing,
)
from skyfield.units import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App, Camera


@pytest.fixture(autouse=True, scope="module")
def function():
    pass


def test_getImageHeader_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(fits, "open", return_value=hdu):
        header = getImageHeader("test")
        assert header == hdu[0].header


def test_getCoordinatesFromHeader_0():
    header = {}
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == Angle(hours=0).hours
    assert dec.degrees == Angle(degrees=0).degrees


def test_getCoordinatesFromHeader_1():
    header = {
        "RA": 180,
        "DEC": 45,
    }
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getCoordinatesFromHeader_2():
    header = {
        "OBJCTRA": "12 00 00",
        "OBJCTDEC": "+45 00 00",
    }
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getSQMFromHeader_0():
    header = {
        "test": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 0


def test_getSQMFromHeader_1():
    header = {
        "SQM": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_2():
    header = {
        "SKY-QLTY": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_3():
    header = {
        "MPSAS": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_4():
    header = {
        "MPSAS": "15.0",
        "SKY-QLTY": "16.0",
        "SQM": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getExposureFromHeader_0():
    header = {
        "test": "17.0",
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 0


def test_getExposureFromHeader_1():
    header = {
        "EXPOSURE": "17.0",
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 17.0


def test_getExposureFromHeader_2():
    header = {
        "EXPTIME": "17.0",
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 17.0


def test_getExposureFromHeader_3():
    header = {
        "EXPTIME": "15.0",
        "EXPOSURE": "16.0",
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 16.0


def test_getScaleFromHeader_1():
    header = {
        "SCALE": "1.333",
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 1.333


def test_getScaleFromHeader_2():
    header = {
        "FOCALLEN": "570",
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_getScaleFromHeader_3():
    header = {
        "FOCALLEN": "570",
        "XBINNING": "1",
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_getScaleFromHeader_4():
    header = {
        "FOCALLEN": "570",
        "XBINNING": "1",
        "XPIXSZ": "3.69",
    }
    scale = getScaleFromHeader(header=header)
    assert round(scale, 3) == 1.335


def test_getScaleFromHeader_5():
    header = {
        "FOCALLEN": "570",
        "XBINNING": "1",
        "PIXSIZE1": "3.69",
    }
    scale = getScaleFromHeader(header=header)
    assert round(scale, 3) == 1.335


def test_getScaleFromHeader_6():
    header = {}
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_getHintFromImageFile_1():
    with mock.patch.object(mw4.logic.fits.fitsFunction, "getImageHeader"):
        with mock.patch.object(
            mw4.logic.fits.fitsFunction,
            "getCoordinatesFromHeader",
            return_value=(Angle(hours=12), Angle(degrees=45)),
        ):
            with mock.patch.object(
                mw4.logic.fits.fitsFunction, "getScaleFromHeader", return_value=1
            ):
                ra, dec, scale = getHintFromImageFile("test")
                assert ra.hours == 12.0
                assert dec.degrees == 45.0
                assert scale == 1


def test_getCoordinatesFromWCSHeader_1():
    header = {
        "CRVAL1": 180,
        "CRVAL2": 45,
    }
    ra, dec = getCoordinatesFromWCSHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_calcAngleScaleFromWCSHeader_1():
    header = {
        "CD1_1": 0.0002777777777777778,
        "CD1_2": 0,
        "CD2_1": 0,
        "CD2_2": -0.0002777777777777778,
    }
    angle, scale, mirrored = calcAngleScaleFromWCSHeader(header=header)
    assert angle.degrees == 0
    assert scale == 1
    assert mirrored


def test_writeHeaderCamera():
    hdu = fits.PrimaryHDU(data=np.array([]))
    header = hdu.header
    camera = Camera()
    camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 3
    camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 3
    camera.app = App()
    camera.obsSite = camera.app.mount.obsSite
    writeHeaderCamera(header, camera)


def test_writeHeaderPointing():
    hdu = fits.PrimaryHDU(data=np.array([]))
    header = hdu.header
    camera = Camera()
    camera.app = App()
    camera.obsSite = camera.app.mount.obsSite
    writeHeaderPointing(header, camera)


def test_updateImageFileHeaderWithSolution_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    solution = {
        "raJ2000S": Angle(hours=12),
        "decJ2000S": Angle(degrees=45),
        "angleS": Angle(degrees=0),
        "scaleS": 0,
        "mirroredS": False,
    }
    with mock.patch.object(fits, "open", return_value=hdu):
        updateImageFileHeaderWithSolution("test", solution)


def test_getSolutionFromWCSHeader_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    imageHeader = hdu[0].header
    header.set("CRVAL1", 180.0)
    header.set("CRVAL2", 60.0)
    imageHeader.set("RA", 180.0)
    imageHeader.set("DEC", 60.0)
    solution = getSolutionFromWCSHeader(header, imageHeader)
    assert solution["raJ2000S"].hours == 12
    assert solution["decJ2000S"].degrees == 60
    assert solution["angleS"].degrees == 0
    assert solution["scaleS"] == 0
    assert not solution["mirroredS"]


def test_getSolutionFromWCSHeader_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("CRVAL1", 180.0)
    header.set("CRVAL2", 60.0)
    imageHeader = hdu[0].header
    imageHeader.set("RA", 180.0)
    imageHeader.set("DEC", 60.0)
    solution = getSolutionFromWCSHeader(header, imageHeader)
    assert solution["raJ2000S"].hours == 12
    assert solution["decJ2000S"].degrees == 60
    assert solution["angleS"].degrees == 0
    assert solution["scaleS"] == 0
    assert not solution["mirroredS"]
