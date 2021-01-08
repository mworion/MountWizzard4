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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest

# external packages
from skyfield.api import Angle

# local imports
from mountcontrol.convert import stringToDegree
from mountcontrol.convert import stringToAngle
from mountcontrol.convert import valueToFloat
from mountcontrol.convert import valueToAngle
from mountcontrol.convert import valueToInt
from mountcontrol.convert import topoToAltAz
from mountcontrol.convert import sexagesimalizeToInt
from mountcontrol.convert import checkIsHours
from mountcontrol.convert import convertToAngle
from mountcontrol.convert import convertToHMS
from mountcontrol.convert import convertToDMS


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    #
    #
    # testing the conversion functions
    #
    #

    def test_stringToDegree_ok1(self):
        parameter = '12:45:33.01'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(12.759169444444444, value, 6)

    def test_stringToDegree_ok2(self):
        parameter = '12:45'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(12.75, value, 6)

    def test_stringToDegree_ok3(self):
        parameter = '+56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok4(self):
        parameter = '-56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(value, -56.5, 6)

    def test_stringToDegree_ok5(self):
        parameter = '+56*30*00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value)

    def test_stringToDegree_ok6(self):
        parameter = '+56*30'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok7(self):
        parameter = '+56:30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok8(self):
        parameter = '56deg 30\'00.0"'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok9(self):
        parameter = '56 30 00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(56.5, value, 6)

    def test_stringToDegree_ok10(self):
        parameter = '11deg 35\' 00.0"'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(11.5833333, value, 6)

    def test_stringToDegree_bad1(self):
        parameter = ''
        value = stringToDegree(parameter)
        self.assertEqual(None, value)

    def test_stringToDegree_bad2(self):
        parameter = '12:45:33:01.01'
        value = stringToDegree(parameter)
        self.assertEqual(None, value)

    def test_stringToDegree_bad3(self):
        parameter = '++56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(None, value)

    def test_stringToDegree_bad4(self):
        parameter = ' 56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(value, 56.5, 6)

    def test_stringToDegree_bad5(self):
        parameter = '--56*30:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(None, value)

    def test_stringToDegree_bad6(self):
        parameter = '-56*dd:00.0'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(None, value)

    def test_stringToDegree_bad7(self):
        parameter = 'E'
        value = stringToDegree(parameter)
        self.assertAlmostEqual(None, value)

    def test_stringToAngle_ok(self):
        parameter = '+50*30:00.0'
        value = stringToAngle(parameter)
        self.assertEqual(50.5, value.degrees)

    def test_stringToAngle_ok1(self):
        parameter = '+50*30:00.0'
        value = stringToAngle(parameter, preference='hours')
        self.assertEqual(50.5, value.hours)

    def test_stringToAngle_ok2(self):
        parameter = '+50*30:00.0'
        value = stringToAngle(parameter, preference='degrees')
        self.assertEqual(50.5, value.degrees)

    def test_valueToAngle_ok(self):
        parameter = 50.5
        value = valueToAngle(parameter)
        self.assertEqual(50.5, value.degrees)

    def test_valueToAngle_ok1(self):
        parameter = 50.5
        value = valueToAngle(parameter, preference='hours')
        self.assertEqual(50.5, value.hours)

    def test_valueToAngle_ok2(self):
        parameter = 50.5
        value = valueToAngle(parameter, preference='degrees')
        self.assertEqual(50.5, value.degrees)

    def test_valueToAngle_ok3(self):
        parameter = '50.5'
        value = valueToAngle(parameter, preference='degrees')
        self.assertEqual(50.5, value.degrees)

    def test_valueToAngle_ok4(self):
        parameter = '00.000'
        value = valueToAngle(parameter, preference='degrees')
        self.assertEqual(0, value.degrees)

    def test_stringToAngle_not_ok1(self):
        parameter = 178
        value = stringToAngle(parameter)
        self.assertEqual(None, value)

    def test_stringToAngle_1(self):
        parameter = '00:10:50.00'
        value = stringToAngle(parameter, preference='hours')
        self.assertEqual(0.18055555555555555, value.hours)

    def test_valueToInt_ok(self):
        parameter = '156'
        value = valueToInt(parameter)
        self.assertEqual(156, value)

    def test_valueToInt_not_ok(self):
        parameter = 'df'
        value = valueToInt(parameter)
        self.assertEqual(None, value)

    def test_valueToFloat_ok(self):
        parameter = '156'
        value = valueToFloat(parameter)
        self.assertEqual(156, value)

    def test_valueToFloat_not_ok_1(self):
        parameter = 'df'
        value = valueToFloat(parameter)
        self.assertEqual(None, value)

    def test_valueToFloat_not_ok_2(self):
        parameter = 'E'
        value = valueToFloat(parameter)
        self.assertEqual(None, value)

    def test_topoToAltAz_ok1(self):
        alt, az = topoToAltAz(0, 0, None)
        self.assertEqual(None, alt)
        self.assertEqual(None, az)

    def test_topoToAltAz_ok2(self):
        alt, az = topoToAltAz(0, 0, 0)
        self.assertEqual(90, alt)
        self.assertEqual(270, az)

    def test_topoToAltAz_ok3(self):
        alt, az = topoToAltAz(12, 0, 0)
        self.assertEqual(-90, alt)
        self.assertEqual(270, az)

    def test_topoToAltAz_ok4(self):
        alt, az = topoToAltAz(12, 180, 0)
        self.assertEqual(90, alt)
        self.assertEqual(360, az)

    def test_topoToAltAz_ok5(self):
        alt, az = topoToAltAz(-12, 0, 0)
        self.assertEqual(-90, alt)
        self.assertEqual(270, az)

    def test_topoToAltAz_ok6(self):
        alt, az = topoToAltAz(23, 0, 0)
        self.assertEqual(75, alt)
        self.assertEqual(90, az)

    def test_sexagesimalizeToInt_1(self):
        output = sexagesimalizeToInt(45/60 + 59.99999/3600)
        self.assertEqual(output[0], +1)
        self.assertEqual(output[1], 0)
        self.assertEqual(output[2], 46)
        self.assertEqual(output[3], 0)
        self.assertEqual(output[4], 0)

    def test_sexagesimalizeToInt_2(self):
        output = sexagesimalizeToInt(45/60 + 59.9/3600, 1)
        self.assertEqual(output[0], +1)
        self.assertEqual(output[1], 0)
        self.assertEqual(output[2], 45)
        self.assertEqual(output[3], 59)
        self.assertEqual(output[4], 9)

    def test_sexagesimalizeToInt_3(self):
        output = sexagesimalizeToInt(45/60 + 59.9/3600, 2)
        self.assertEqual(output[0], +1)
        self.assertEqual(output[1], 0)
        self.assertEqual(output[2], 45)
        self.assertEqual(output[3], 59)
        self.assertEqual(output[4], 90)

    def test_checkIsHours_1(self):
        assert not checkIsHours(180)

    def test_checkIsHours_2(self):
        assert not checkIsHours(-180)

    def test_checkIsHours_3(self):
        assert not checkIsHours(12)

    def test_checkIsHours_4(self):
        assert not checkIsHours(0.0)

    def test_checkIsHours_5(self):
        assert not checkIsHours('+12*00:00.0')

    def test_checkIsHours_6(self):
        assert checkIsHours('12:00:00.0')

    def test_checkIsHours_7(self):
        suc = checkIsHours(0)
        assert not suc

    def test_checkIsHours_8(self):
        suc = checkIsHours('*55:67:77')
        assert not suc

    def test_checkIsHours_9(self):
        suc = checkIsHours('')
        assert suc

    def test_checkIsHours_10(self):
        suc = checkIsHours('+12 00:00.0')
        assert not suc

    def test_checkIsHours_11(self):
        suc = checkIsHours('-12 00:00.0')
        assert not suc

    def test_convertToAngle(self):
        val = convertToAngle('E')
        assert val is None

    def test_convertToDMS_1(self):
        parameter = Angle(degrees=60)
        value = convertToDMS(parameter)
        assert value == '+60:00:00'

    def test_convertToDMS_2(self):
        parameter = 60
        value = convertToDMS(parameter)
        assert value == '+60:00:00'

    def test_convertToDMS_3(self):
        parameter = '60'
        value = convertToDMS(parameter)
        assert value == ''

    def test_convertToDMS_4(self):
        value = Angle(degrees=90.0)
        value = convertToDMS(value)
        assert value == '+90:00:00'

    def test_convertToDMS_5(self):
        value = Angle(degrees=-90.0)
        value = convertToDMS(value)
        assert value == '-90:00:00'

    def test_convertToHMS_1(self):
        parameter = Angle(hours=12)
        value = convertToHMS(parameter)
        assert value == '12:00:00'

    def test_convertToHMS_2(self):
        parameter = 12
        value = convertToHMS(parameter)
        assert value == '12:00:00'

    def test_convertToHMS_3(self):
        parameter = '60'
        value = convertToHMS(parameter)
        assert value == ''

    def test_convertToHMS_4(self):
        value = Angle(hours=12.0)
        value = convertToHMS(value)
        assert value == '12:00:00'

    def test_convertToHMS_5(self):
        value = Angle(hours=-12.0)
        value = convertToHMS(value)
        assert value == '12:00:00'

    def test_stringToDegree_1(self):
        value = stringToDegree(100)
        assert value is None

    def test_stringToDegree_2(self):
        value = stringToDegree('')
        assert value is None

    def test_stringToDegree_3(self):
        value = stringToDegree('++')
        assert value is None

    def test_stringToDegree_4(self):
        value = stringToDegree('--')
        assert value is None

    def test_stringToDegree_5(self):
        value = stringToDegree('55:66:ff')
        assert value is None

    def test_stringToDegree_6(self):
        value = stringToDegree('55:30')
        assert value == 55.5

    def test_convertToAngle_1(self):
        value = convertToAngle(180.1234)
        assert value.degrees == 180.1234

    def test_convertToAngle_2(self):
        value = convertToAngle(180)
        assert value.degrees == 180

    def test_convertToAngle_3(self):
        value = convertToAngle(180.567, isHours=True)
        assert value.hours == 12.0378

    def test_convertToAngle_4(self):
        value = convertToAngle('12:00:00.0', isHours=True)
        assert value.hours == 12

    def test_convertToAngle_5(self):
        value = convertToAngle('+12:00:00.0')
        assert value.degrees == 12
