# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
import pytest
from mw4.logic.controllers.satellites.trackCalculations import (
    calcTrajectoryData,
    dataAgeColor,
    filterHorizon,
    formatSatPass,
    reduceTrajectory,
    satStatusText,
    selectStartEnd,
    shouldDomeFollow,
    trimBelowHorizon,
)
from skyfield.api import EarthSatellite, load, wgs84
from types import SimpleNamespace


@pytest.mark.parametrize(
    "status, expected",
    [
        ("V", "is slewing to transit start"),
        ("P", "is waiting for satellite"),
        ("S", "is catching satellite"),
        ("T", "is tracking satellite"),
        ("X", ""),
    ],
)
def test_satStatusText(status, expected):
    assert satStatusText(status) == expected


@pytest.mark.parametrize(
    "status, follow, dome, expected",
    [
        (10, True, True, True),
        (1, True, True, False),
        (10, False, True, False),
        (10, True, False, False),
    ],
)
def test_shouldDomeFollow(status, follow, dome, expected):
    assert shouldDomeFollow(status, follow, dome) is expected


def jd(value):
    return SimpleNamespace(tt=value)


ORBIT = {"rise": jd(10), "settle": jd(20), "flipEarly": jd(14), "flipLate": jd(16)}


@pytest.mark.parametrize(
    "orbits",
    [[], [{"settle": jd(1)}], [{"rise": jd(1)}]],
)
def test_selectStartEnd_incompleteOrbits(orbits):
    assert selectStartEnd(orbits, True, True) == (0, 0)


@pytest.mark.parametrize(
    "isBefore, isAfter, expected",
    [
        (True, True, (10, 20)),
        (True, False, (10, 16)),
        (False, True, (14, 20)),
        (False, False, (0, 0)),
    ],
)
def test_selectStartEnd_flipChoices(isBefore, isAfter, expected):
    assert selectStartEnd([ORBIT], isBefore, isAfter) == expected


def test_selectStartEnd_withoutFlipTimes():
    orbit = {"rise": jd(10), "settle": jd(20)}
    assert selectStartEnd([orbit], True, False) == (10, 20)
    assert selectStartEnd([orbit], False, True) == (10, 20)


def test_trimBelowHorizon_fromStart():
    alt = [1, 2, 45, 46, 3]
    az = [10, 20, 30, 40, 50]
    a, z, removed = trimBelowHorizon(alt, az, lambda p: p[0] > 40, fromEnd=False)
    assert removed == 2
    assert list(a) == [45, 46, 3]
    assert list(z) == [30, 40, 50]


def test_trimBelowHorizon_fromEnd():
    alt = [1, 45, 46, 3, 2]
    az = [10, 20, 30, 40, 50]
    a, z, removed = trimBelowHorizon(alt, az, lambda p: p[0] > 40, fromEnd=True)
    assert removed == 2
    assert list(a) == [1, 45, 46]
    assert list(z) == [10, 20, 30]


def test_trimBelowHorizon_nothingRemoved():
    alt = [45, 46]
    a, _, removed = trimBelowHorizon(alt, [1, 2], lambda p: True, fromEnd=False)
    assert removed == 0
    assert a is alt


def test_trimBelowHorizon_allBelow():
    a, z, removed = trimBelowHorizon([1, 2], [1, 2], lambda p: False, fromEnd=False)
    assert removed == 2
    assert len(a) == 0
    assert len(z) == 0


def test_filterHorizon():
    alt = np.array([1, 45, 46, 2, 3])
    az = np.array([10, 20, 30, 40, 50])
    start, end, a, z = filterHorizon(100, 200, alt, az, lambda p: p[0] > 40)
    assert start == pytest.approx(100 + 1 / 86400)
    assert end == pytest.approx(200 - 2 / 86400)
    assert list(a) == [45, 46]
    assert list(z) == [20, 30]


def test_calcTrajectoryData_tooShort():
    alt, az = calcTrajectoryData(
        100, 100, satellite=None, earth=None, location=None, ts=None, temperature=10, pressure=1000
    )
    assert len(alt) == 0
    assert len(az) == 0


def test_calcTrajectoryData():
    ts = load.timescale()
    tle = [
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    satellite = EarthSatellite(tle[0], tle[1], name="NOAA 8", ts=ts)
    earth = load("tests/testData/de440_mw4.bsp")["earth"]
    start = 2459215.0
    alt, az = calcTrajectoryData(
        start,
        start + 3 / 86400,
        satellite=satellite,
        earth=earth,
        location=wgs84.latlon(48.0, 11.0, 500),
        ts=ts,
        temperature=10,
        pressure=1000,
    )
    assert len(alt) == 3
    assert len(az) == 3


def test_formatSatPass_complete():
    orbit = {"rise": 1, "culminate": 2, "settle": 3, "flip": 4}
    result = formatSatPass(orbit, lambda t, f: f"{t}|{f}")
    assert result == {
        "rise": "1|%H:%M:%S",
        "date": "1|%d %b",
        "culminate": "2|%H:%M:%S",
        "settle": "3|%H:%M:%S",
        "flip": "4|%H:%M:%S",
    }


def test_formatSatPass_empty():
    result = formatSatPass({}, lambda t, f: "x")
    assert result == {
        "rise": "unknown",
        "date": "---",
        "culminate": "unknown",
        "settle": "unknown",
        "flip": "no flip",
    }


@pytest.mark.parametrize("days, color", [(11, "red"), (5, "yellow"), (1, ""), (3, ""), (10, "")])
def test_dataAgeColor(days, color):
    assert dataAgeColor(days) == color


def test_reduceTrajectory():
    alt, az = reduceTrajectory(np.arange(1900.0), np.arange(1900.0))
    assert len(alt) == len(az) == 950
    alt, az = reduceTrajectory(np.arange(10.0), np.arange(10.0))
    assert len(alt) == len(az) == 10
