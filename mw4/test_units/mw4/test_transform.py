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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages
from skyfield.api import Angle
# local import
from mw4.base import transform


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
    value = transform.convertToAngle(180)
    assert value.degrees == 180


def test_convertToAngle_2():
    value = transform.convertToAngle(180)
    assert value.degrees == 180


def test_convertToAngle_3():
    value = transform.convertToAngle(180, isHours=True)
    assert value.hours == 12


def test_convertToAngle_4():
    value = transform.convertToAngle('12:00:00.0', isHours=True)
    assert value.hours == 12


def test_convertToAngle_4():
    value = transform.convertToAngle('+12:00:00.0')
    assert value.degrees == 12


def test_convertToHMS_1():
    value = Angle(hours=12.0)
    value = transform.convertToHMS(value)
    assert value == '12:00:00'


def test_convertToHMS_2():
    value = Angle(hours=-12.0)
    value = transform.convertToHMS(value)
    assert value == '12:00:00'


def test_convertToDMS_1():
    value = Angle(degrees=90.0)
    value = transform.convertToDMS(value)
    assert value == '+90:00:00'


def test_convertToDMS_2():
    value = Angle(degrees=-90.0)
    value = transform.convertToDMS(value)
    assert value == '-90:00:00'
