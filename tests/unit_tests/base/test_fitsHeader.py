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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages

# local import
from mw4.base.loggerMW import setupLogging
from mw4.base.fitsHeader import getCoordinates, getSQM, getExposure, getScale
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    pass


def test_getCoordinates_1():
    header = {
        'RA': 180,
        'DEC': 45,
    }
    ra, dec = getCoordinates(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getCoordinates_2():
    header = {
        'OBJCTRA': '12 00 00',
        'OBJCTDEC': '+45 00 00',
    }
    ra, dec = getCoordinates(header=header)
    assert ra.hours == 12.0
    assert dec.degrees == 45.0


def test_getCoordinates_3():
    ra, dec = getCoordinates()
    assert ra.hours == 0
    assert dec.degrees == 0


def test_getSQM_0():
    sqm = getSQM()
    assert sqm is None


def test_getSQM_1():
    header = {
        'SQM': '17.0',
    }
    sqm = getSQM(header=header)
    assert sqm == 17.0


def test_getSQM_2():
    header = {
        'SKY-QLTY': '17.0',
    }
    sqm = getSQM(header=header)
    assert sqm == 17.0


def test_getSQM_3():
    header = {
        'MPSAS': '17.0',
    }
    sqm = getSQM(header=header)
    assert sqm == 17.0


def test_getSQM_4():
    header = {
        'MPSAS': '15.0',
        'SKY-QLTY': '16.0',
        'SQM': '17.0',
    }
    sqm = getSQM(header=header)
    assert sqm == 17.0


def test_getExposure_0():
    exposure = getExposure()
    assert exposure is None


def test_getExposure_1():
    header = {
        'EXPOSURE': '17.0',
    }
    exposure = getExposure(header=header)
    assert exposure == 17.0


def test_getExposure_2():
    header = {
        'EXPTIME': '17.0',
    }
    exposure = getExposure(header=header)
    assert exposure == 17.0


def test_getExposure_3():
    header = {
        'EXPTIME': '15.0',
        'EXPOSURE': '16.0',
    }
    exposure = getExposure(header=header)
    assert exposure == 16.0


def test_getScale_0():
    scale = getScale()
    assert scale is None


def test_getScale_1():
    header = {
        'SCALE': '1.333',
    }
    scale = getScale(header=header)
    assert scale == 1.333


def test_getScale_2():
    header = {
        'FOCALLEN': '570',
    }
    scale = getScale(header=header)
    assert scale is None


def test_getScale_3():
    header = {
        'FOCALLEN': '570',
        'XBINNING': '1',
    }
    scale = getScale(header=header)
    assert scale is None


def test_getScale_4():
    header = {
        'FOCALLEN': '570',
        'XBINNING': '1',
        'XPIXSZ': '3.69',
    }
    scale = getScale(header=header)
    assert round(scale, 3) == 1.335


def test_getScale_5():
    header = {
        'FOCALLEN': '570',
        'XBINNING': '1',
        'PIXSIZE1': '3.69',
    }
    scale = getScale(header=header)
    assert round(scale, 3) == 1.335


def test_getScale_5():
    header = {
    }
    scale = getScale(header=header)
    assert scale is None
