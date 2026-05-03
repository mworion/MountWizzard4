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
# Licence APL2.0
#
###########################################################

import math
import mw4.mountcontrol
import unittest.mock as mock
from mw4.mountcontrol.convert import (
    convertDecToAngle,
    convertLatToAngle,
    convertLonToAngle,
    convertRaToAngle,
    convertToDMS,
    convertToHMS,
    formatDstrToText,
    formatHstrToText,
    formatLatLonToAngle,
    formatLatToText,
    formatLonToText,
    sexagesimalizeToInt,
    stringToAngle,
    stringToDegree,
    topoToAltAz,
    valueToAngle,
    valueToFloat,
    valueToInt,
)
from skyfield.api import Angle

#
#
# testing the conversion functions
#
#


def test_stringToDegree_ok1():
    parameter = "12:45:33.01"
    value = stringToDegree(parameter)
    assert math.isclose(value, 12.759169444444444, abs_tol=1e-6)


def test_stringToDegree_ok2():
    parameter = "12:45"
    value = stringToDegree(parameter)
    assert math.isclose(value, 12.75, abs_tol=1e-6)


def test_stringToDegree_ok3():
    parameter = "+56*30:00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, 56.5, abs_tol=1e-6)


def test_stringToDegree_ok4():
    parameter = "-56*30:00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, -56.5, abs_tol=1e-6)


def test_stringToDegree_ok5():
    parameter = "+56*30*00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, 56.5, abs_tol=1e-7)


def test_stringToDegree_ok6():
    parameter = "+56*30"
    value = stringToDegree(parameter)
    assert math.isclose(value, 56.5, abs_tol=1e-6)


def test_stringToDegree_ok7():
    parameter = "+56:30:00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, 56.5, abs_tol=1e-6)


def test_stringToDegree_ok8():
    parameter = "56deg 30'00.0\""
    value = stringToDegree(parameter)
    assert math.isclose(value, 56.5, abs_tol=1e-6)


def test_stringToDegree_ok9():
    parameter = "56 30 00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, 56.5, abs_tol=1e-6)


def test_stringToDegree_ok10():
    parameter = "11deg 35' 00.0\""
    value = stringToDegree(parameter)
    assert math.isclose(value, 11.5833333, abs_tol=1e-6)


def test_stringToDegree_bad1():
    parameter = ""
    value = stringToDegree(parameter)
    assert value == 0


def test_stringToDegree_bad2():
    parameter = "12:45:33:01.01"
    value = stringToDegree(parameter)
    assert value == 0


def test_stringToDegree_bad3():
    parameter = "++56*30:00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, 0, abs_tol=1e-7)


def test_stringToDegree_bad4():
    parameter = " 56*30:00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, 56.5, abs_tol=1e-6)


def test_stringToDegree_bad5():
    parameter = "--56*30:00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, 0, abs_tol=1e-7)


def test_stringToDegree_bad6():
    parameter = "-56*dd:00.0"
    value = stringToDegree(parameter)
    assert math.isclose(value, 0, abs_tol=1e-7)


def test_stringToDegree_bad7():
    parameter = "E"
    value = stringToDegree(parameter)
    assert math.isclose(value, 0, abs_tol=1e-7)


def test_stringToAngle_ok():
    parameter = "+50*30:00.0"
    value = stringToAngle(parameter)
    assert value.degrees == 50.5


def test_stringToAngle_ok1():
    parameter = "+50*30:00.0"
    value = stringToAngle(parameter, preference="hours")
    assert value.hours == 50.5


def test_stringToAngle_ok2():
    parameter = "+50*30:00.0"
    value = stringToAngle(parameter, preference="degrees")
    assert value.degrees == 50.5


def test_valueToAngle_ok():
    parameter = 50.5
    value = valueToAngle(parameter)
    assert value.degrees == 50.5


def test_valueToAngle_ok1():
    parameter = 50.5
    value = valueToAngle(parameter, preference="hours")
    assert value.hours == 50.5


def test_valueToAngle_ok2():
    parameter = 50.5
    value = valueToAngle(parameter, preference="degrees")
    assert value.degrees == 50.5


def test_valueToAngle_ok3():
    parameter = "50.5"
    value = valueToAngle(parameter, preference="degrees")
    assert value.degrees == 50.5


def test_valueToAngle_ok4():
    parameter = "00.000"
    value = valueToAngle(parameter, preference="degrees")
    assert value.degrees == 0


def test_stringToAngle_1():
    parameter = "00:10:50.00"
    value = stringToAngle(parameter, preference="hours")
    assert value.hours == 0.18055555555555555


def test_valueToInt_ok():
    parameter = "156"
    value = valueToInt(parameter)
    assert value == 156


def test_valueToInt_not_ok():
    parameter = "df"
    value = valueToInt(parameter)
    assert value == 0


def test_valueToFloat_ok():
    parameter = "156"
    value = valueToFloat(parameter)
    assert value == 156


def test_valueToFloat_not_ok_1():
    parameter = "df"
    value = valueToFloat(parameter)
    assert value == 0


def test_valueToFloat_not_ok_2():
    parameter = "E"
    value = valueToFloat(parameter)
    assert value == 0


def test_topoToAltAz_ok2():
    alt, az = topoToAltAz(Angle(hours=0), Angle(degrees=0), Angle(degrees=0))
    assert alt.degrees == 90
    assert az.degrees == 270


def test_topoToAltAz_ok3():
    alt, az = topoToAltAz(Angle(hours=12), Angle(degrees=0), Angle(degrees=0))
    assert alt.degrees == -90
    assert az.degrees == 270


def test_topoToAltAz_ok4():
    alt, az = topoToAltAz(Angle(hours=12), Angle(degrees=180), Angle(degrees=0))
    assert alt.degrees == 90
    assert az.degrees == 360


def test_topoToAltAz_ok5():
    alt, az = topoToAltAz(Angle(hours=-12), Angle(degrees=0), Angle(degrees=0))
    assert alt.degrees == -90
    assert az.degrees == 270


def test_topoToAltAz_ok6():
    alt, az = topoToAltAz(Angle(hours=23), Angle(degrees=0), Angle(degrees=0))
    assert math.isclose(alt.degrees, 75, abs_tol=1e-5)
    assert math.isclose(az.degrees, 90, abs_tol=1e-5)


def test_sexagesimalizeToInt_1():
    output = sexagesimalizeToInt(45 / 60 + 59.99999 / 3600)
    assert output[0] == +1
    assert output[1] == 0
    assert output[2] == 46
    assert output[3] == 0
    assert output[4] == 0


def test_sexagesimalizeToInt_2():
    output = sexagesimalizeToInt(45 / 60 + 59.9 / 3600, 1)
    assert output[0] == +1
    assert output[1] == 0
    assert output[2] == 45
    assert output[3] == 59
    assert output[4] == 9


def test_sexagesimalizeToInt_3():
    output = sexagesimalizeToInt(45 / 60 + 59.9 / 3600, 2)
    assert output[0] == +1
    assert output[1] == 0
    assert output[2] == 45
    assert output[3] == 59
    assert output[4] == 90


def test_convertToDMS_1():
    parameter = Angle(degrees=60)
    value = convertToDMS(parameter)
    assert value == "+60:00:00"


def test_convertToDMS_4():
    value = Angle(degrees=90.0)
    value = convertToDMS(value)
    assert value == "+90:00:00"


def test_convertToDMS_5():
    value = Angle(degrees=-90.0)
    value = convertToDMS(value)
    assert value == "-90:00:00"


def test_convertToHMS_1():
    parameter = Angle(hours=12)
    value = convertToHMS(parameter)
    assert value == "12:00:00"


def test_convertToHMS_4():
    value = Angle(hours=12.0)
    value = convertToHMS(value)
    assert value == "12:00:00"


def test_convertToHMS_5():
    value = Angle(hours=-12.0)
    value = convertToHMS(value)
    assert value == "12:00:00"


def test_stringToDegree_1():
    value = stringToDegree(100)
    assert value == 0


def test_stringToDegree_2():
    value = stringToDegree("")
    assert value == 0


def test_stringToDegree_3():
    value = stringToDegree("++")
    assert value == 0


def test_stringToDegree_4():
    value = stringToDegree("--")
    assert value == 0


def test_stringToDegree_5():
    value = stringToDegree("55:66:ff")
    assert value == 0


def test_stringToDegree_6():
    value = stringToDegree("55:30")
    assert value == 55.5


def test_formatLatLonToAngle_1():
    values = [
        ["+12.5", "SN", 12.5],
        ["12.5", "SN", 12.5],
        ["-12.5", "SN", -12.5],
        ["+12.5", "WE", 12.5],
        ["12.5", "WE", 12.5],
        ["-12.5", "WE", -12.5],
        ["12N 30 30.55", "SN", 12.508333],
        ["12N 30 30.5", "SN", 12.508333],
        ["12N 30 30,5", "SN", 12.508333],
        ["12 30 30.5N", "SN", 0],
        ["12 30 30.5 N", "SN", 0],
        ["+12N 30 30.5", "SN", 0],
        ["12N 30 30", "SN", 12.508333],
        ["12S 30 30", "SN", -12.508333],
        ["12N 30", "SN", 12.5],
        ["12NS 30", "SN", 0],
        ["12W ", "SN", 0],
        ["12E 30 30.55", "WE", 12.508333],
        ["12E 30 30.5", "WE", 12.508333],
        ["12 30 30.5E", "WE", 0],
        ["12 30 30.5 E", "WE", 0],
        ["+12E 30 30.5", "WE", 0],
        ["12E 30 30", "WE", 12.508333],
        ["12W 30 30", "WE", -12.508333],
        ["12E 30", "WE", 12.5],
        ["12WE 30", "WE", 0],
        ["12N ", "WE", 0],
        ["99N ", "SN", 0],
        ["99S ", "SN", 0],
        ["190E ", "WE", 0],
        ["190W ", "WE", 0],
        ["12N 30  30.5 ", "SN", 12.508333],
        ["12N  30 30.5", "SN", 12.508333],
        ["12N  30  30.5", "SN", 12.508333],
    ]
    for value in values:
        angle = formatLatLonToAngle(value[0], value[1])
        assert math.isclose(angle.degrees, value[2], abs_tol=0.000001)


def test_formatLat():
    with mock.patch.object(mw4.mountcontrol.convert, "formatLatLonToAngle", return_value=10):
        angle = convertLatToAngle("12345")
        assert angle == 10


def test_formatLon():
    with mock.patch.object(mw4.mountcontrol.convert, "formatLatLonToAngle", return_value=10):
        angle = convertLonToAngle("12345")
        assert angle == 10


def test_convertRaToAngle_1():
    values = [
        ["+12.5", 12.5],
        ["12,5", 12.5],
        ["-12.5", 0],
        ["-190.5", 0],
        ["190.5", 0],
        ["12H 30 30", 187.624999],
        ["12D 30 30", 0],
        ["12 30 30", 187.624999],
        ["12H 30 30.55", 187.624999],
        ["12H:30:30.55", 187.624999],
        ["12H  30 30", 187.624999],
        ["12H 30  30", 187.624999],
        ["12H  30   30.50", 187.624999],
        ["12  30 30", 187.624999],
        ["12 30  30", 187.624999],
        ["12  30   30.50", 187.624999],
    ]
    for value in values:
        angle = convertRaToAngle(value[0])
        assert math.isclose(angle._degrees, value[1], abs_tol=0.000001)


def test_convertDecToAngle_1():
    values = [
        ["+12.5", 12.5],
        ["12,5", 12.5],
        ["-12.5", -12.5],
        ["-90.5", 0],
        ["90.5", 0],
        ["12Deg 30 30", 12.508333],
        ["12Deg 30 30.55", 12.508333],
        ["12H 30 30.55", 0],
        ["12 30 30.55", 12.508333],
        ["-12Deg 30 30.55", -12.508333],
        ["-12Deg:30:30.55", -12.508333],
        ["-12 30 30.55", -12.508333],
        ["-12:30:30.55", -12.508333],
        ["12Deg 30  30.55", 12.508333],
        ["12Deg  30 30.55", 12.508333],
        ["12Deg  30  30.55", 12.508333],
        ["12 30  30.55", 12.508333],
        ["12  30 30.55", 12.508333],
        ["12  30  30.55", 12.508333],
    ]
    for value in values:
        angle = convertDecToAngle(value[0])
        assert math.isclose(angle._degrees, value[1], abs_tol=0.000001)


def test_formatHstrToText():
    values = [
        [Angle(hours=12), "12:00:00"],
        [Angle(hours=12.000001), "12:00:00"],
        [Angle(hours=6), "06:00:00"],
    ]
    for value in values:
        text = formatHstrToText(value[0])
        assert text == value[1]


def test_formatDstrToText():
    values = [
        [Angle(degrees=12), "+12:00:00"],
        [Angle(degrees=12.000001), "+12:00:00"],
        [Angle(degrees=6), "+06:00:00"],
        [Angle(degrees=-6), "-06:00:00"],
    ]
    for value in values:
        text = formatDstrToText(value[0])
        assert text == value[1]


def test_formatLatToText():
    values = [
        [Angle(degrees=12), "12N 00 00"],
        [Angle(degrees=12.000001), "12N 00 00"],
        [Angle(degrees=6), "06N 00 00"],
        [Angle(degrees=-6), "06S 00 00"],
    ]
    for value in values:
        text = formatLatToText(value[0])
        assert text == value[1]


def test_formatLonToText():
    values = [
        [Angle(degrees=12), "012E 00 00"],
        [Angle(degrees=12.000001), "012E 00 00"],
        [Angle(degrees=6), "006E 00 00"],
        [Angle(degrees=-6), "006W 00 00"],
    ]
    for value in values:
        text = formatLonToText(value[0])
        assert text == value[1]
