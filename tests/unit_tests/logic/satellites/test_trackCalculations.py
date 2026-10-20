# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
import pytest
from mw4.logic.satellites.trackCalculations import (
    calcTrajectoryData,
    filterHorizon,
    selectStartEnd,
    trimBelowHorizon,
)
from skyfield.api import EarthSatellite, load, wgs84
from types import SimpleNamespace


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
    alt, az = calcTrajectoryData(100, 100, None, None, None, None, 10, 1000)
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
        start, start + 3 / 86400, satellite, earth, wgs84.latlon(48.0, 11.0, 500), ts, 10, 1000
    )
    assert len(alt) == 3
    assert len(az) == 3
