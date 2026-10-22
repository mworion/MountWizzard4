# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from collections.abc import Callable
from typing import Any

SECONDS_PER_DAY = 86400
# the mount accepts at most 900 s of trajectory data
MAX_TRAJECTORY_SECONDS = 900


def selectStartEnd(
    satOrbits: list[dict[str, Any]], isBefore: bool, isAfter: bool
) -> tuple[float, float]:
    """
    selects the start and end of a satellite pass in terrestrial time (jd) depending on
    the choice for before and / or after the meridian flip.
    """
    if not satOrbits:
        return 0, 0
    orbit = satOrbits[0]
    if "rise" not in orbit or "settle" not in orbit:
        return 0, 0

    start = orbit["rise"].tt
    end = orbit["settle"].tt
    if isBefore and isAfter:
        return start, end
    if isBefore and "flipLate" in orbit:
        end = orbit["flipLate"].tt
    elif isAfter and "flipEarly" in orbit:
        start = orbit["flipEarly"].tt
    elif not (isBefore or isAfter):
        return 0, 0
    return start, end


def calcTrajectoryData(
    start: float,
    end: float,
    *,
    satellite: Any,
    earth: Any,
    location: Any,
    ts: Any,
    temperature: float,
    pressure: float,
) -> tuple[np.ndarray, np.ndarray]:
    duration = min(end - start, MAX_TRAJECTORY_SECONDS / SECONDS_PER_DAY)
    if duration < 1 / SECONDS_PER_DAY:
        return np.array([]), np.array([])

    timeSeries = start + np.arange(0, duration, 1 / SECONDS_PER_DAY)
    timeVec = ts.tt_jd(timeSeries)
    topocentric = (earth + location).at(timeVec).observe(earth + satellite).apparent()
    alt, az, _ = topocentric.altaz(pressure_mbar=pressure, temperature_C=temperature)
    return alt.degrees, az.degrees


def trimBelowHorizon(
    alt: np.ndarray, az: np.ndarray, isAboveHorizon: Callable[[list[float]], bool], fromEnd: bool
) -> tuple[np.ndarray, np.ndarray, int]:
    """
    removes points below the horizon from the start (or the end) until the first point
    above the horizon is found. returns the shortened arrays and the count of removed points.
    """
    pairs = list(zip(alt, az, strict=True))
    if fromEnd:
        pairs.reverse()
    removed = 0
    for altitude, azimuth in pairs:
        if isAboveHorizon([altitude, azimuth]):
            break
        removed += 1
    if not removed:
        return alt, az, 0
    alt, az = np.asarray(alt), np.asarray(az)
    if fromEnd:
        return alt[:-removed], az[:-removed], removed
    return alt[removed:], az[removed:], removed


def filterHorizon(
    start: float,
    end: float,
    alt: np.ndarray,
    az: np.ndarray,
    isAboveHorizon: Callable[[list[float]], bool],
) -> tuple[float, float, np.ndarray, np.ndarray]:
    alt, az, delayStart = trimBelowHorizon(alt, az, isAboveHorizon, fromEnd=False)
    alt, az, delayEnd = trimBelowHorizon(alt, az, isAboveHorizon, fromEnd=True)
    return start + delayStart / SECONDS_PER_DAY, end - delayEnd / SECONDS_PER_DAY, alt, az


def formatSatPass(
    satOrbit: dict[str, Any], convertTime: Callable[[Any, str], str]
) -> dict[str, str]:
    """
    builds the display texts of one satellite pass. convertTime formats a time object
    with a strftime format string (time zone handling stays with the caller).
    """
    fString = "%H:%M:%S"
    result: dict[str, str] = {}
    riseT = satOrbit.get("rise")
    if riseT is not None:
        result["rise"] = convertTime(riseT, fString)
        result["date"] = convertTime(riseT, "%d %b")
    else:
        result["rise"] = "unknown"
        result["date"] = "---"
    for key, missingText in (("culminate", "unknown"), ("settle", "unknown"), ("flip", "no flip")):
        value = satOrbit.get(key)
        result[key] = convertTime(value, fString) if value is not None else missingText
    return result


def dataAgeColor(days: float) -> str:
    """returns the style color for the age of satellite data in days."""
    if days > 10:
        return "red"
    if 3 < days < 10:
        return "yellow"
    return ""


def reduceTrajectory(alt: np.ndarray, az: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """limits the trajectory to the point count the mount accepts."""
    factor = max(int(len(alt) / MAX_TRAJECTORY_SECONDS), 1)
    return np.array_split(alt, factor)[0], np.array_split(az, factor)[0]
