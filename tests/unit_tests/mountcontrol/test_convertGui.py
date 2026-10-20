# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import math
import mw4.mountcontrol
from mw4.mountcontrol.convertGui import (
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
)
from skyfield.api import Angle
from unittest import mock


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
    with mock.patch.object(mw4.mountcontrol.convertGui, "formatLatLonToAngle", return_value=10):
        angle = convertLatToAngle("12345")
        assert angle == 10


def test_formatLon():
    with mock.patch.object(mw4.mountcontrol.convertGui, "formatLatLonToAngle", return_value=10):
        angle = convertLonToAngle("12345")
        assert angle == 10


def test_convertRaToAngle_1():
    values = [
        ["+12.5", 12.5],
        ["12,5", 12.5],
        ["-12.5", 0],
        ["-190.5", 0],
        ["190.5", 190.5],
        ["180.0", 180.0],
        ["360", 0],
        ["25H 30 30", 0],
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
        assert math.isclose(angle.degrees, value[1], abs_tol=0.000001)


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
        assert math.isclose(angle.degrees, value[1], abs_tol=0.000001)


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


def test_convertToDMS_zero():
    assert convertToDMS(Angle(degrees=0)) == "+00:00:00"


def test_convertDecToAngle_degreesOnly():
    assert math.isclose(convertDecToAngle("12Deg").degrees, 12, abs_tol=0.000001)
    assert math.isclose(convertDecToAngle("-12").degrees, -12, abs_tol=0.000001)


def test_convertDecToAngle_noSeconds():
    assert math.isclose(convertDecToAngle("12 30").degrees, 12.5, abs_tol=0.000001)


def test_convertRaToAngle_partialSexagesimal():
    assert math.isclose(convertRaToAngle("12H").hours, 12, abs_tol=0.000001)
    assert math.isclose(convertRaToAngle("12H 30").hours, 12.5, abs_tol=0.000001)
