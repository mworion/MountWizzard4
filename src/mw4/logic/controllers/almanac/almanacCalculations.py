# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass
from range_key_dict import RangeKeyDict
from skyfield import almanac
from skyfield.timelib import Time, Timescale
from skyfield.toposlib import GeographicPosition
from skyfield.trigonometry import position_angle_of
from typing import Any

MOON_RISE_DAYS: int = 2
MOON_RISE_MAX: int = 3
MOON_NODE_DAYS: int = 29
MOON_NODE_MAX: int = 2

phasesText = RangeKeyDict(
    {
        (0, 1): "New moon",
        (1, 23): "Waxing crescent",
        (23, 27): "First quarter",
        (27, 48): "Waxing gibbous",
        (48, 52): "Full moon",
        (52, 73): "Waning gibbous",
        (73, 77): "Third quarter",
        (77, 99): "Waning crescent",
        (99, 100): "New moon ",
    }
)


@dataclass
class MoonPhaseData:
    illumination: float
    degree: float
    percent: float
    angle: Any
    moonTimes: Any
    moonEvents: Any
    nodeTimes: Any
    nodeEvents: Any


def calcTwilightData(
    ephemeris: Any,
    ts: Timescale,
    timeJD: Time,
    location: GeographicPosition,
    tWinL: int,
    tWinH: int,
) -> tuple[Any, Any]:
    t0 = ts.tt_jd(int(timeJD.tt) - tWinL)
    t1 = ts.tt_jd(int(timeJD.tt) + tWinH + 1)
    f = almanac.dark_twilight_day(ephemeris, location)
    return almanac.find_discrete(t0, t1, f)


def calcMoonRiseSet(
    ephemeris: Any, ts: Timescale, timeJD: Time, location: GeographicPosition
) -> tuple[Any, Any]:
    t0 = ts.tt_jd(int(timeJD.tt))
    t1 = ts.tt_jd(int(timeJD.tt) + MOON_RISE_DAYS)
    f = almanac.risings_and_settings(ephemeris, ephemeris["moon"], location)
    moonTimes, moonEvents = almanac.find_discrete(t0, t1, f)
    return moonTimes[0:MOON_RISE_MAX], moonEvents[0:MOON_RISE_MAX]


def calcMoonNodes(ephemeris: Any, ts: Timescale, timeJD: Time) -> tuple[Any, Any]:
    t0 = ts.tt_jd(int(timeJD.tt))
    t1 = ts.tt_jd(int(timeJD.tt) + MOON_NODE_DAYS)
    f = almanac.moon_nodes(ephemeris)
    nodeTimes, nodeEvents = almanac.find_discrete(t0, t1, f)
    return nodeTimes[0:MOON_NODE_MAX], nodeEvents[0:MOON_NODE_MAX]


def calcMoonPhase(
    ephemeris: Any, ts: Timescale, timeJD: Time, location: GeographicPosition
) -> MoonPhaseData:
    sun = ephemeris["sun"]
    moon = ephemeris["moon"]
    earth = ephemeris["earth"]
    e = earth.at(timeJD)

    # pyrefly: ignore[missing-attribute]
    _, sunLon, _ = e.observe(sun).apparent().ecliptic_latlon()
    # pyrefly: ignore[missing-attribute]
    _, moonLon, _ = e.observe(moon).apparent().ecliptic_latlon()

    mpIllumination = almanac.fraction_illuminated(ephemeris, "moon", ts.now())
    mpDegree = (moonLon.degrees - sunLon.degrees) % 360.0
    mpPercent = mpDegree / 360 * 100

    locObserver = (location + earth).at(timeJD)
    moonApparent = locObserver.observe(moon).apparent()
    sunApparent = locObserver.observe(sun).apparent()
    moonAngle = position_angle_of(moonApparent.altaz(), sunApparent.altaz())

    moonTimes, moonEvents = calcMoonRiseSet(ephemeris, ts, timeJD, location)
    nodeTimes, nodeEvents = calcMoonNodes(ephemeris, ts, timeJD)
    return MoonPhaseData(
        illumination=mpIllumination,
        degree=mpDegree,
        percent=mpPercent,
        angle=moonAngle,
        moonTimes=moonTimes,
        moonEvents=moonEvents,
        nodeTimes=nodeTimes,
        nodeEvents=nodeEvents,
    )
