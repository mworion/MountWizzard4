# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from skyfield.api import Angle


def stringToDegree(value: str) -> float:
    """
    stringToDegree takes any form of HMS / DMS string format and tries to
    convert it to a decimal number.
    """
    if not isinstance(value, str):
        return 0.0
    if not len(value):
        return 0.0
    if value.count("+") > 1:
        return 0.0
    if value.count("-") > 1:
        return 0.0
    if value == "E":
        return 0.0

    value = value.replace("*", " ")
    value = value.replace(":", " ")
    value = value.replace("deg", " ")
    value = value.replace('"', " ")
    value = value.replace("'", " ")
    value = value.split()

    try:
        value = [float(x) for x in value]
    except ValueError:
        return 0.0

    sign = 1 if value[0] >= 0 else -1
    value[0] = abs(value[0])

    if len(value) == 3:
        return sign * (value[0] + value[1] / 60 + value[2] / 3600)
    if len(value) == 2:
        return sign * (value[0] + value[1] / 60)
    return 0.0


def angleFromValue(value: float, preference: str) -> Angle:
    """
    Build a Skyfield Angle from a numeric value according to preference.
    preference 'degrees' creates a degree-based Angle; anything else creates
    an hours-based Angle.
    """
    if preference == "degrees":
        return Angle(degrees=value, preference="degrees")
    return Angle(hours=value, preference="hours")


def stringToAngle(value: str, preference: str = "degrees") -> Angle:
    return angleFromValue(stringToDegree(value), preference)


def valueToFloat(value: str | float | None) -> float:
    if value == "E" or value is None:
        return 0
    try:
        value = float(value)
    except (ValueError, TypeError):
        value = 0
    return value


def valueToAngle(value: str | float | None, preference: str = "degrees") -> Angle:
    return angleFromValue(valueToFloat(value), preference)


def valueToInt(value: str | float | None) -> int:
    if value is None:
        return 0
    try:
        value = int(value)
    except (ValueError, TypeError):
        value = 0
    return value


def validatePierside(value: str) -> str | None:
    """
    validatePierside returns the upper case pierside ('E' or 'W') for a valid
    input and None for anything else.
    """
    if isinstance(value, str) and value.upper() in ("E", "W"):
        return value.upper()
    return None


def topoToAltAz(ha: Angle, dec: Angle, lat: Angle) -> tuple[Angle, Angle]:
    ha = (ha.radians + 2 * np.pi) % (2 * np.pi)
    dec = dec.radians
    lat = lat.radians
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
    value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
    value = np.clip(value, -1, 1)
    A = np.arccos(value)
    A = np.degrees(A)
    alt = np.degrees(alt)
    az = 360.0 - A if np.sin(ha) >= 0.0 else A
    return Angle(degrees=alt), Angle(degrees=az)


def sexagesimalizeToInt(value: float, decimals: int = 0) -> tuple[int, int, int, int, int]:
    sign = int(np.sign(value))
    value = abs(value)
    power = 10**decimals
    n = int(7200 * power * value + 1) // 2
    n, fraction = divmod(n, power)
    n, seconds = divmod(n, 60)
    n, minutes = divmod(n, 60)

    return sign, n, minutes, seconds, fraction
