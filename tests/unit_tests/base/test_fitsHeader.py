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
import pytest

# external packages
from astropy.io import fits
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App, Camera
from base.loggerMW import setupLogging
from base.fitsHeader import getCoordinatesFromHeader, getSQMFromHeader
from base.fitsHeader import getExposureFromHeader, getScaleFromHeader
from base.fitsHeader import getCoordinatesFromWCSHeader, calcAngleScaleFromWCSHeader
from base.fitsHeader import writeHeaderCamera, writeHeaderPointing
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    pass


def test_getCoordinatesFromHeader_1():
    header = {
        'RA': 180,
        'DEC': 45,
    }
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getCoordinatesFromHeader_2():
    header = {
        'OBJCTRA': '12 00 00',
        'OBJCTDEC': '+45 00 00',
    }
    ra, dec = getCoordinatesFromHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getCoordinatesFromWCSHeader_1():
    header = {
        'CRVAL1': '180',
        'CRVAL2': '180.5',
    }
    ra, dec = getCoordinatesFromWCSHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 180.5


def test_getCoordinatesFromWCSHeader_2():
    header = {
        'CRVAL1': 180,
        'CRVAL2': 180.5,
    }
    ra, dec = getCoordinatesFromWCSHeader(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 180.5


def test_getSQMFromHeader_1():
    header = {
        'SQM': '17.0',
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_2():
    header = {
        'SKY-QLTY': '17.0',
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_3():
    header = {
        'MPSAS': '17.0',
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getSQMFromHeader_4():
    header = {
        'MPSAS': '15.0',
        'SKY-QLTY': '16.0',
        'SQM': '17.0',
    }
    sqm = getSQMFromHeader(header=header)
    assert sqm == 17.0


def test_getExposureFromHeader_1():
    header = {
        'EXPOSURE': '17.0',
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 17.0


def test_getExposureFromHeader_2():
    header = {
        'EXPTIME': '17.0',
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 17.0


def test_getExposureFromHeader_3():
    header = {
        'EXPTIME': '15.0',
        'EXPOSURE': '16.0',
    }
    exposure = getExposureFromHeader(header=header)
    assert exposure == 16.0


def test_getScaleFromHeader_1():
    header = {
        'SCALE': '1.333',
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 1.333


def test_getScaleFromHeader_2():
    header = {
        'FOCALLEN': '570',
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_getScaleFromHeader_3():
    header = {
        'FOCALLEN': '570',
        'XBINNING': '1',
    }
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_getScaleFromHeader_4():
    header = {
        'FOCALLEN': '570',
        'XBINNING': '1',
        'XPIXSZ': '3.69',
    }
    scale = getScaleFromHeader(header=header)
    assert round(scale, 3) == 1.335


def test_getScaleFromHeader_5():
    header = {
        'FOCALLEN': '570',
        'XBINNING': '1',
        'PIXSIZE1': '3.69',
    }
    scale = getScaleFromHeader(header=header)
    assert round(scale, 3) == 1.335


def test_getScaleFromHeader_6():
    header = {}
    scale = getScaleFromHeader(header=header)
    assert scale == 0


def test_calcAngleScaleFromWCSHeader_1():
    header = {
        'CD1_1': 0.0002777777777777778,
        'CD1_2': 0,
        'CD2_1': 0,
        'CD2_2': -0.0002777777777777778,
    }
    angle, scale, mirrored = calcAngleScaleFromWCSHeader(header=header)
    assert angle == 0
    assert scale == 1
    assert mirrored
    
    
def test_writeHeaderCamera(): 
    hdu = fits.PrimaryHDU(data=np.array([]))
    header = hdu.header
    camera = Camera()
    camera.data['CCD_INFO.CCD_PIXEL_SIZE_X'] = 3
    camera.data['CCD_INFO.CCD_PIXEL_SIZE_Y'] = 3
    camera.app = App()
    camera.obsSite = camera.app.mount.obsSite
    header = writeHeaderCamera(header, camera)
    
    
def test_writeHeaderPointing():
    hdu = fits.PrimaryHDU(data=np.array([]))
    header = hdu.header
    camera = Camera()
    camera.app = App()
    camera.obsSite = camera.app.mount.obsSite
    header = writeHeaderPointing(header, camera)
    


