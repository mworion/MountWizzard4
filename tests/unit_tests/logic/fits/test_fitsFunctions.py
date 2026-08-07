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
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

import mw4.logic
import numpy as np
import pytest
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
    writeSolutionToHeader,
)
from skyfield.units import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App, Camera
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function() -> None:
    pass


def test_getImageHeader_1() -> None:
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with mock.patch.object(fits, "open", return_value=hdu):
        header = getImageHeader("test")
        assert header == hdu[0].header


def test_getCoordinatesFromHeader_0() -> None:
    header = {}
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == Angle(hours=0).hours
    assert dec.degrees == Angle(degrees=0).degrees


def test_getCoordinatesFromHeader_1() -> None:
    header = {
        "RA": 180,
        "DEC": 45,
    }
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getCoordinatesFromHeader_2() -> None:
    header = {
        "OBJCTRA": "12 00 00",
        "OBJCTDEC": "+45 00 00",
    }
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getCoordinatesFromHeader_3() -> None:
    header = {
        "RA": 180,
        "DEC": 45,
        "OBJCTRA": "01 00 00",
        "OBJCTDEC": "+10 00 00",
    }
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getSQMFromHeader_0() -> None:
    header = {
        "test": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 0


def test_getSQMFromHeader_1() -> None:
    header = {
        "SQM": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_2() -> None:
    header = {
        "SKY-QLTY": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_3() -> None:
    header = {
        "MPSAS": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_4() -> None:
    header = {
        "MPSAS": "15.0",
        "SKY-QLTY": "16.0",
        "SQM": "17.0",
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getExposureFromHeader_0() -> None:
    header = {
        "test": "17.0",
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 0


def test_getExposureFromHeader_1() -> None:
    header = {
        "EXPOSURE": "17.0",
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 17.0


def test_getExposureFromHeader_2() -> None:
    header = {
        "EXPTIME": "17.0",
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 17.0


def test_getExposureFromHeader_3() -> None:
    header = {
        "EXPTIME": "15.0",
        "EXPOSURE": "16.0",
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 16.0


def test_getScaleFromHeader_1() -> None:
    header = {
        "SCALE": "1.333",
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 1.333


def test_getScaleFromHeader_2() -> None:
    header = {
        "FOCALLEN": "570",
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_getScaleFromHeader_3() -> None:
    header = {
        "FOCALLEN": "570",
        "XBINNING": "1",
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_getScaleFromHeader_4() -> None:
    header = {
        "FOCALLEN": "570",
        "XBINNING": "1",
        "XPIXSZ": "3.69",
    }
    scale = getScaleFromHeader(header=header)
    assert round(scale, 3) == 1.335


def test_getScaleFromHeader_5() -> None:
    header = {
        "FOCALLEN": "570",
        "XBINNING": "1",
        "PIXSIZE1": "3.69",
    }
    scale = getScaleFromHeader(header=header)
    assert round(scale, 3) == 1.335


def test_getScaleFromHeader_6() -> None:
    header = {}
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_getScaleFromHeader_7() -> None:
    header = {
        "FOCALLEN": "570",
        "XBINNING": "1",
        "XPIXSZ": "3.0",
        "PIXSIZE1": "4.0",
    }
    scale = getScaleFromHeader(header=header)
    assert round(scale, 3) == 1.447


def test_getHintFromImageFile_1() -> None:
    with (
        mock.patch.object(mw4.logic.fits.fitsFunction, "getImageHeader"),
        mock.patch.object(
            mw4.logic.fits.fitsFunction,
            "getCoordinatesFromHeader",
            return_value=(Angle(hours=12), Angle(degrees=45)),
        ),
        mock.patch.object(mw4.logic.fits.fitsFunction, "getScaleFromHeader", return_value=1),
    ):
        ra, dec, scale = getHintFromImageFile("test")
        assert ra.hours == 12.0
        assert dec.degrees == 45.0
        assert scale == 1


def test_getCoordinatesFromWCSHeader_1() -> None:
    header = {
        "CRVAL1": 180,
        "CRVAL2": 45,
    }
    ra, dec = getCoordinatesFromWCSHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_calcAngleScaleFromWCSHeader_1() -> None:
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


def test_calcAngleScaleFromWCSHeader_2() -> None:
    header = {
        "CD1_1": 0.0002777777777777778,
        "CD1_2": 0,
        "CD2_1": 0,
        "CD2_2": 0.0002777777777777778,
    }
    angle, scale, mirrored = calcAngleScaleFromWCSHeader(header=header)
    assert angle.degrees == 0
    assert scale == 1
    assert not mirrored


def test_writeHeaderCamera() -> None:
    hdu = fits.PrimaryHDU(data=np.array([]))
    header = hdu.header
    camera = Camera()
    camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 3
    camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 3
    app = App()
    obsSite = app.mount.obsSite
    result = writeHeaderCamera(header, camera, obsSite)
    assert result["OBJECT"] == "SKY_OBJECT"
    assert result["AUTHOR"] == "MountWizzard4"
    assert result["FRAME"] == "Light"
    assert result["EQUINOX"] == 2000
    assert result["OBSERVER"] == "MW4"
    assert result["SITELAT"] == "20N 00 00"
    assert result["SITELON"] == "010E 00 00"
    assert result["SITEELEV"] == 500
    assert result["PIXSIZE1"] == 3
    assert result["PIXSIZE2"] == 3
    assert result["XPIXSZ"] == 3
    assert result["YPIXSZ"] == 3
    assert result["XBINNING"] == 1
    assert result["YBINNING"] == 1
    assert result["FOCALLEN"] == 100
    assert result["SCALE"] == pytest.approx(3 * 1 / 100 * 206.265)
    assert result["EXPTIME"] == 0
    assert result["CCD-TEMP"] == 0


def test_writeHeaderCamera_withoutFocalLength() -> None:
    hdu = fits.PrimaryHDU(data=np.array([]))
    header = hdu.header
    camera = Camera()
    camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 3
    camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 3
    camera.focalLength = 0
    app = App()
    obsSite = app.mount.obsSite

    with (
        mock.patch.object(mw4.logic.fits.fitsFunction.log, "warning") as warningMock,
        pytest.raises(UnboundLocalError),
    ):
        writeHeaderCamera(header, camera, obsSite)

    warningMock.assert_called_once_with("camera.focalLength not set")


def test_writeHeaderPointing() -> None:
    hdu = fits.PrimaryHDU(data=np.array([]))
    header = hdu.header
    app = App()
    obsSite = app.mount.obsSite
    result = writeHeaderPointing(header, obsSite)
    assert result["RA"] == pytest.approx(359.72275429697004)
    assert result["DEC"] == pytest.approx(-0.12045998771078002)


def test_writeSolutionToHeader_1() -> None:
    hdu = fits.PrimaryHDU(data=np.array([]))
    header = hdu.header
    solution = {
        "raJ2000S": Angle(hours=12),
        "decJ2000S": Angle(degrees=45),
        "angleS": Angle(degrees=0),
        "scaleS": 1.5,
        "mirroredS": False,
    }
    result = writeSolutionToHeader(header, solution)
    assert result["RA"] == 180
    assert result["DEC"] == 45
    assert result["SCALE"] == 1.5
    assert result["PIXSCALE"] == 1.5
    assert result["ANGLE"] == 0
    assert result["MIRRORED"] is False


def test_updateImageFileHeaderWithSolution_1() -> None:
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    solution = {
        "raJ2000S": Angle(hours=12),
        "decJ2000S": Angle(degrees=45),
        "angleS": Angle(degrees=0),
        "scaleS": 0,
        "mirroredS": False,
    }
    with mock.patch.object(fits, "open", return_value=hdu):
        updateImageFileHeaderWithSolution("test", solution)
    assert hdu[0].header["RA"] == 180
    assert hdu[0].header["DEC"] == 45
    assert hdu[0].header["ANGLE"] == 0
    assert hdu[0].header["SCALE"] == 0
    assert hdu[0].header["PIXSCALE"] == 0
    assert hdu[0].header["MIRRORED"] is False


def test_getSolutionFromWCSHeader_1() -> None:
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
    assert solution["errorRMS_S"] == 0


def test_getSolutionFromWCSHeader_2() -> None:
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
