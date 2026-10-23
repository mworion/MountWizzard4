# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.almanac.almanacCalculations import (
    MOON_NODE_MAX,
    MOON_RISE_MAX,
    MoonPhaseData,
    calcMoonNodes,
    calcMoonPhase,
    calcMoonRiseSet,
    calcTwilightData,
    phasesText,
)
from pathlib import Path
from skyfield.api import load, wgs84
from skyfield.jpllib import SpiceKernel


@pytest.fixture(scope="module")
def sky() -> tuple:
    ephemeris = SpiceKernel(str(Path("tests/testData/de440_mw4.bsp")))
    ts = load.timescale()
    location = wgs84.latlon(latitude_degrees=20, longitude_degrees=10, elevation_m=500)
    return ephemeris, ts, ts.tt_jd(2460000.5), location


def test_phasesText() -> None:
    assert phasesText[0.5] == "New moon"
    assert phasesText[50] == "Full moon"


def test_calcTwilightData(sky: tuple) -> None:
    ephemeris, ts, timeJD, location = sky
    times, events = calcTwilightData(ephemeris, ts, timeJD, location, 0, 1)
    assert len(times) == len(events) > 0


def test_calcMoonRiseSet(sky: tuple) -> None:
    ephemeris, ts, timeJD, location = sky
    times, events = calcMoonRiseSet(ephemeris, ts, timeJD, location)
    assert len(times) == len(events) <= MOON_RISE_MAX


def test_calcMoonNodes(sky: tuple) -> None:
    ephemeris, ts, timeJD, _ = sky
    times, events = calcMoonNodes(ephemeris, ts, timeJD)
    assert len(times) == len(events) <= MOON_NODE_MAX


def test_calcMoonPhase(sky: tuple) -> None:
    ephemeris, ts, timeJD, location = sky
    data = calcMoonPhase(ephemeris, ts, timeJD, location)
    assert isinstance(data, MoonPhaseData)
    assert 0 <= data.degree < 360
    assert data.percent == pytest.approx(data.degree / 360 * 100)
