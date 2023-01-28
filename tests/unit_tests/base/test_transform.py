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
from skyfield.api import Angle
from skyfield.api import wgs84

# local import
from base import transform


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    pass


def test_JNowToJ2000_1():
    class Test:
        tt = 2458687
        ut1 = 1

    ra, dec = transform.JNowToJ2000(180, 180, Test())
    assert ra.hours == 0
    assert dec.degrees == 0


def test_JNowToJ2000_2():
    class Test:
        tt = 2458687
        ut1 = 1

    ra, dec = transform.JNowToJ2000(Angle(hours=12), 180, Test())
    assert ra.hours == 0.0
    assert dec.degrees == 0.0


def test_JNowToJ2000_3():
    class Test:
        tt = 2458687
        ut1 = 1

    ra, dec = transform.JNowToJ2000(Angle(hours=12), Angle(degrees=180), Test())
    assert ra.hours != 0
    assert dec.degrees != 0


def test_J2000T0JNow_1():
    class Test:
        tt = 2458687
        ut1 = 1

    ra, dec = transform.J2000ToJNow(180, 180, Test())
    assert ra.hours == 0
    assert dec.degrees == 0


def test_J2000T0JNow_2():
    class Test:
        tt = 2458687
        ut1 = 1

    ra, dec = transform.J2000ToJNow(Angle(hours=12), 180, Test())
    assert ra.hours == 0
    assert dec.degrees == 0


def test_J2000T0JNow_3():
    class Test:
        tt = 2458687
        ut1 = 1

    ra, dec = transform.J2000ToJNow(Angle(hours=12), Angle(degrees=180), Test())
    assert ra.hours != 0
    assert dec.degrees != 0


def test_J2000T0AltAz_1():
    class Test:
        tt = 2458849.50000
        ut1 = 2458849.50000

    loc = wgs84.latlon(latitude_degrees=42.3583, longitude_degrees=-71.0636)
    alt, az = transform.J2000ToAltAz(180, 180, Test(), loc)
    assert alt.degrees == 0
    assert az.degrees == 0


def test_J2000T0AltAz_2():
    class Test:
        tt = 2458849.50000
        ut1 = 2458849.50000

    loc = wgs84.latlon(latitude_degrees=42.3583, longitude_degrees=-71.0636)
    alt, az = transform.J2000ToAltAz(Angle(hours=12), 45, Test(), loc)
    assert alt.degrees == 0
    assert az.degrees == 0


def test_J2000T0AltAz_3():
    class Test:
        tt = 2458849.50000
        ut1 = 2458849.50000

    loc = wgs84.latlon(latitude_degrees=42.3583, longitude_degrees=-71.0636)
    alt, az = transform.J2000ToAltAz(Angle(hours=12), Angle(degrees=45), Test(), loc)
    assert alt.degrees != 0
    assert az.degrees != 0


def test_diffModulusAbs_1():
    val = transform.diffModulusAbs(1, 20, 360)
    assert val == 19


def test_diffModulusAbs_2():
    val = transform.diffModulusAbs(350, 10, 360)
    assert val == 20


def test_diffModulusAbs_3():
    val = transform.diffModulusAbs(-10, 340, 360)
    assert val == 10


def test_diffModulusSign_1():
    val = transform.diffModulusSign(1, 20, 360)
    assert val == 19


def test_diffModulusSign_2():
    val = transform.diffModulusSign(350, 10, 360)
    assert val == 20


def test_diffModulusSign_3():
    val = transform.diffModulusSign(-10, 340, 360)
    assert val == -10


def test_diffModulusSign_4():
    val = transform.diffModulusSign(330, 320, 360)
    assert val == -10


def test_diffModulusSign_5():
    val = transform.diffModulusSign(-10, -20, 360)
    assert val == -10
