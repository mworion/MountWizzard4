# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import math
import pytest
from mw4.mountcontrol.convert import (
    sexagesimalizeToInt,
    stringToAngle,
    stringToDegree,
    topoToAltAz,
    validatePierside,
    valueToAngle,
    valueToFloat,
    valueToInt,
)
from skyfield.api import Angle


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


@pytest.mark.parametrize(
    "value, expected",
    [("E", "E"), ("w", "W"), ("W", "W"), ("x", None), ("", None), (1, None), (None, None)],
)
def test_validatePierside(value, expected):
    assert validatePierside(value) == expected


def test_valueToInt_none():
    assert valueToInt(None) == 0
