# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import re
from mw4.mountcontrol.convert import sexagesimalizeToInt
from skyfield.api import Angle


def convertToDMS(dec: Angle) -> str:
    t = Angle.signed_dms(dec)
    sign = "+" if dec.degrees >= 0 else "-"
    value = f"{sign}{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}"
    return value


def convertToHMS(ra: Angle) -> str:
    t = Angle.signed_hms(ra)
    value = f"{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}"
    return value


def formatLatLonToAngle(value: str, pf: str) -> Angle:
    value = value.strip()
    p1 = re.compile(r"(\d{1,3})([" + pf + r"])\s*(\d\d)?\s*(\d\d)?[.,]?(\d*)?")
    p2 = re.compile(r"([-+]?)(\d{1,3})[.,]?(\d*)?")
    isSexagesimal = p1.fullmatch(value) is not None
    isFloat = p2.fullmatch(value) is not None

    elements = p2.split(value)
    if isFloat:
        angle = float(value.replace(",", "."))

    elif isSexagesimal:
        angle = float(elements[2])
        if len(elements) > 5:
            angle += float(elements[6]) / 60
        if len(elements) > 9:
            angle += float(elements[10]) / 3600
        if elements[4].startswith(pf[0]):
            angle = -angle
    else:
        angle = 0

    maxAbs = 90 if "N" in pf else 180

    if angle > maxAbs or angle < -maxAbs:
        angle = 0

    return Angle(degrees=angle)


def convertLatToAngle(value: str) -> Angle:
    return formatLatLonToAngle(value, "SN")


def convertLonToAngle(value: str) -> Angle:
    return formatLatLonToAngle(value, "WE")


def parseCoordToAngleString(value: str, coordType: str) -> tuple[bool, bool, list[str] | str]:
    """
    Parse a coordinate string for RA or Dec into match flags and captured groups.

    coordType selects the unit keyword that appears immediately after the degrees
    digits: use 'H' for right ascension (e.g. '12H 30 30') and 'Deg' for
    declination (e.g. '12Deg 30 30').

    Returns (isSexagesimal, isFloat, elements) where elements is the list of
    captured groups from the matching pattern, or an empty string if no pattern
    matched.
    """
    value = value.strip()
    p1 = re.compile(rf"([+-]?)(\d{{1,3}}){coordType}[\s:]*(\d\d)?[\s:]*(\d\d)?[.,]?(\d*)?")
    p2 = re.compile(r"([+-]?)(\d{1,3})[\s:]+(\d\d)?[\s:]*(\d\d)?[.,]?(\d*)?")
    p3 = re.compile(r"([+-]?)(\d{1,3})[.,]?(\d*)?")
    isP1 = p1.fullmatch(value) is not None
    isP2 = p2.fullmatch(value) is not None
    isSexagesimal = isP1 or isP2
    isFloat = p3.fullmatch(value) is not None

    if isP1:
        elements = p1.split(value)
    elif isP2:
        elements = p2.split(value)
    else:
        elements = ""

    return isSexagesimal, isFloat, elements


def convertRaToAngle(value: str) -> Angle:
    isSexagesimal, isFloat, elements = parseCoordToAngleString(value, "H")

    if isFloat:
        # plain numbers are interpreted as degrees (0 <= value < 360)
        angle = float(value.replace(",", "."))
        if angle >= 360 or angle < 0:
            angle = 0
        return Angle(hours=angle / 360 * 24)

    if isSexagesimal:
        angle = float(elements[2])
        if elements[3] is not None:
            angle += float(elements[3]) / 60
        if elements[4] is not None:
            angle += float(elements[4]) / 3600
    else:
        angle = 0

    if angle >= 24 or angle < 0:
        angle = 0

    return Angle(hours=angle)


def convertDecToAngle(value: str) -> Angle:
    isSexagesimal, isFloat, elements = parseCoordToAngleString(value, "Deg")

    if isFloat:
        angle = float(value.replace(",", "."))

    elif isSexagesimal:
        angle = float(elements[2])
        if elements[3] is not None:
            angle += float(elements[3]) / 60
        if elements[4] is not None:
            angle += float(elements[4]) / 3600
        if elements[1].startswith("-"):
            angle = -angle
    else:
        angle = 0

    if angle > 90 or angle < -90:
        angle = 0

    return Angle(degrees=angle)


def formatHstrToText(angle: Angle) -> str:
    formatStr = "{1:02}:{2:02}:{3:02}"
    return angle.hstr(format=formatStr)


def formatDstrToText(angle: Angle) -> str:
    formatStr = "{0:+>1}{1:02}:{2:02}:{3:02}"
    return angle.dstr(format=formatStr)


def formatLatToText(angle: Angle) -> str:
    sgn, h, m, s, _ = sexagesimalizeToInt(angle.degrees, 0)
    sign = "N" if sgn >= 0 else "S"
    return f"{h:02d}{sign} {m:02d} {s:02d}"


def formatLonToText(angle: Angle) -> str:
    sgn, h, m, s, _ = sexagesimalizeToInt(angle.degrees, 0)
    sign = "E" if sgn >= 0 else "W"
    return f"{h:03d}{sign} {m:02d} {s:02d}"
