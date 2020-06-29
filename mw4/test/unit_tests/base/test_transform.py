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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import faulthandler
faulthandler.enable()

# external packages
from skyfield.api import Angle
from skyfield.api import Topos
import numpy as np

# local import
from mw4.base import transform


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

    ra, dec = transform.J2000ToJNow(Angle(hours=12), Angle(degrees=180), Test())
    assert ra.hours != 0
    assert dec.degrees != 0


def test_J2000T0AltAz_1():
    class Test:
        tt = 2458849.50000
        ut1 = 0.5

    loc = Topos('42.3583 N', '71.0636 W')
    alt, az = transform.J2000ToAltAz(180, 180, Test(), loc)
    assert alt.degrees == 0
    assert az.degrees == 0


def test_J2000T0AltAz_2():
    class Test:
        tt = 2458849.50000
        ut1 = 0.5

    loc = Topos('42.3583 N', '71.0636 W')
    alt, az = transform.J2000ToAltAz(Angle(hours=12), Angle(degrees=45), Test(), loc)
    assert alt.degrees != 0
    assert az.degrees != 0


def test_checkIsHours_1():
    assert not transform.checkIsHours(180)


def test_checkIsHours_2():
    assert not transform.checkIsHours(-180)


def test_checkIsHours_3():
    assert not transform.checkIsHours(12)


def test_checkIsHours_4():
    assert not transform.checkIsHours(0.0)


def test_checkIsHours_5():
    assert not transform.checkIsHours('+12*00:00.0')


def test_checkIsHours_6():
    assert transform.checkIsHours('12:00:00.0')


def test_checkIsHours_7():
    suc = transform.checkIsHours(0)
    assert not suc


def test_checkIsHours_8():
    suc = transform.checkIsHours('*55:67:77')
    assert not suc


def test_checkIsHours_9():
    suc = transform.checkIsHours('')
    assert suc


def test_stringToDegree_ok1():
    parameter = '12:45:33.01'
    value = transform.stringToDegree(parameter)
    assert 12.759169444444444 == value


def test_stringToDegree_ok2():
    parameter = '12:45'
    value = transform.stringToDegree(parameter)
    assert 12.75 == value


def test_stringToDegree_ok3():
    parameter = '+56*30:00.0'
    value = transform.stringToDegree(parameter)
    assert 56.5 == value


def test_stringToDegree_ok4():
    parameter = '-56*30:00.0'
    value = transform.stringToDegree(parameter)
    assert value == -56.5


def test_stringToDegree_ok5():
    parameter = '+56*30*00.0'
    value = transform.stringToDegree(parameter)
    assert 56.5 == value


def test_stringToDegree_ok6():
    parameter = '+56*30'
    value = transform.stringToDegree(parameter)
    assert 56.5 == value


def test_stringToDegree_ok7():
    parameter = '+56:30:00.0'
    value = transform.stringToDegree(parameter)
    assert 56.5 == value


def test_stringToDegree_ok8():
    parameter = '56deg 30\'00.0"'
    value = transform.stringToDegree(parameter)
    assert 56.5 == value


def test_stringToDegree_ok9():
    parameter = '56 30 00.0'
    value = transform.stringToDegree(parameter)
    assert 56.5 == value


def test_stringToDegree_ok10():
    parameter = '11deg 30\' 00.0"'
    value = transform.stringToDegree(parameter)
    assert 11.5 == value


def test_stringToDegree_bad1():
    parameter = ''
    value = transform.stringToDegree(parameter)
    assert value is None


def test_stringToDegree_bad2():
    parameter = '12:45:33:01.01'
    value = transform.stringToDegree(parameter)
    assert value is None


def test_stringToDegree_bad3():
    parameter = '++56*30:00.0'
    value = transform.stringToDegree(parameter)
    assert value is None


def test_stringToDegree_bad4():
    parameter = ' 56*30:00.0'
    value = transform.stringToDegree(parameter)
    assert value == 56.5


def test_stringToDegree_bad5():
    parameter = '--56*30:00.0'
    value = transform.stringToDegree(parameter)
    assert value is None


def test_stringToDegree_bad6():
    parameter = '-56*dd:00.0'
    value = transform.stringToDegree(parameter)
    assert value is None


def test_convertToDMS_1():
    parameter = Angle(degrees=60)
    value = transform.convertToDMS(parameter)
    assert value == '+60:00:00'


def test_convertToDMS_2():
    parameter = 60
    value = transform.convertToDMS(parameter)
    assert value == '+60:00:00'


def test_convertToDMS_3():
    parameter = '60'
    value = transform.convertToDMS(parameter)
    assert value == ''


def test_convertToDMS_4():
    value = Angle(degrees=90.0)
    value = transform.convertToDMS(value)
    assert value == '+90:00:00'


def test_convertToDMS_5():
    value = Angle(degrees=-90.0)
    value = transform.convertToDMS(value)
    assert value == '-90:00:00'


def test_convertToHMS_1():
    parameter = Angle(hours=12)
    value = transform.convertToHMS(parameter)
    assert value == '12:00:00'


def test_convertToHMS_2():
    parameter = 12
    value = transform.convertToHMS(parameter)
    assert value == '12:00:00'


def test_convertToHMS_3():
    parameter = '60'
    value = transform.convertToHMS(parameter)
    assert value == ''


def test_convertToHMS_4():
    value = Angle(hours=12.0)
    value = transform.convertToHMS(value)
    assert value == '12:00:00'


def test_convertToHMS_5():
    value = Angle(hours=-12.0)
    value = transform.convertToHMS(value)
    assert value == '12:00:00'


def test_sphericalToCartesian_1():
    x, y, z = transform.sphericalToCartesian(np.radians(90), 0, 1)
    assert round(x, 6) == 0
    assert round(y, 6) == 0
    assert round(z, 6) == 1


def test_sphericalToCartesian_2():
    x, y, z = transform.sphericalToCartesian(0, 0, 1)
    assert round(x, 6) == 1
    assert round(y, 6) == 0
    assert round(z, 6) == 0


def test_sphericalToCartesian_3():
    x, y, z = transform.sphericalToCartesian(0, np.radians(90), 1)
    assert round(x, 6) == 0
    assert round(y, 6) == 1
    assert round(z, 6) == 0


def test_sphericalToCartesian_4():
    x, y, z = transform.sphericalToCartesian(0, np.radians(45), 1)
    assert round(x, 6) == 0.707107
    assert round(y, 6) == 0.707107
    assert round(z, 6) == 0


def test_cartesianToSpherical_1():
    alt, az, ra = transform.cartesianToSpherical(0, 0, 1)
    assert round(alt, 6) == round(np.radians(90), 6)
    assert round(az, 6) == 0
    assert round(ra, 6) == 1


def test_cartesianToSpherical_2():
    alt, az, ra = transform.cartesianToSpherical(1, 0, 0)
    assert round(alt, 6) == 0
    assert round(az, 6) == 0
    assert round(ra, 6) == 1


def test_cartesianToSpherical_3():
    alt, az, ra = transform.cartesianToSpherical(0, 1, 0)
    assert round(alt, 6) == 0
    assert round(az, 6) == round(np.radians(90), 6)
    assert round(ra, 6) == 1


def test_cartesianToSpherical_4():
    alt, az, ra = transform.cartesianToSpherical(0.707107, 0.707107, 0)
    assert round(alt, 6) == 0
    assert round(az, 6) == round(np.radians(45), 6)
    assert round(ra, 6) == 1


def test_polarToCartesian_1():
    x, y = transform.polarToCartesian(np.radians(90), 1)
    assert round(x, 6) == 0
    assert round(y, 6) == 1


def test_polarToCartesian_2():
    x, y = transform.polarToCartesian(0, 1)
    assert round(x, 6) == 1
    assert round(y, 6) == 0


def test_polarToCartesian_3():
    x, y = transform.polarToCartesian(np.radians(45), 1)
    assert round(x, 6) == 0.707107
    assert round(y, 6) == 0.707107


def test_cartesianToPolar_1():
    theta, radius = transform.cartesianToPolar(0, 1)
    assert round(theta, 6) == round(np.radians(90), 6)
    assert round(radius, 6) == 1


def test_cartesianToPolar_2():
    theta, radius = transform.cartesianToPolar(1, 0)
    assert round(theta, 6) == 0
    assert round(radius, 6) == 1


def test_cartesianToPolar_3():
    theta, radius = transform.cartesianToPolar(0.707107, 0.707107)
    assert round(theta, 6) == round(np.radians(45), 6)
    assert round(radius, 6) == 1


def test_stringToDegree_1():
    value = transform.stringToDegree(100)
    assert value is None


def test_stringToDegree_2():
    value = transform.stringToDegree('')
    assert value is None


def test_stringToDegree_3():
    value = transform.stringToDegree('++')
    assert value is None


def test_stringToDegree_4():
    value = transform.stringToDegree('--')
    assert value is None


def test_stringToDegree_5():
    value = transform.stringToDegree('55:66:ff')
    assert value is None


def test_stringToDegree_6():
    value = transform.stringToDegree('55:30')
    assert value == 55.5


def test_convertToAngle_1():
    value = transform.convertToAngle(180.1234)
    assert value.degrees == 180.1234


def test_convertToAngle_2():
    value = transform.convertToAngle(180)
    assert value.degrees == 180


def test_convertToAngle_3():
    value = transform.convertToAngle(180.567, isHours=True)
    assert value.hours == 12.0378


def test_convertToAngle_4():
    value = transform.convertToAngle('12:00:00.0', isHours=True)
    assert value.hours == 12


def test_convertToAngle_5():
    value = transform.convertToAngle('+12:00:00.0')
    assert value.degrees == 12
