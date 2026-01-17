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
import logging
import numpy as np
import re
from skyfield.api import Angle
from typing import Any

log = logging.getLogger()


def stringToDegree(value: str) -> float:
    """
    stringToDegree takes any form of HMS / DMS string format and tries to
    convert it to a decimal number.
    """
    if not isinstance(value, str):
        return 0
    if not len(value):
        return 0
    if value.count("+") > 1:
        return 0
    if value.count("-") > 1:
        return 0
    if value == "E":
        return 0

    value = value.replace("*", " ")
    value = value.replace(":", " ")
    value = value.replace("deg", " ")
    value = value.replace('"', " ")
    value = value.replace("'", " ")
    value = value.split()

    try:
        value = [float(x) for x in value]
    except Exception:
        return 0

    sign = 1 if value[0] >= 0 else -1
    value[0] = abs(value[0])

    if len(value) == 3:
        value = sign * (value[0] + value[1] / 60 + value[2] / 3600)
        return value

    elif len(value) == 2:
        value = sign * (value[0] + value[1] / 60)
        return value
    else:
        return 0


def stringToAngle(value: str, preference: str = "degrees") -> Angle:
    """ """
    value = stringToDegree(value)
    if preference == "degrees":
        value = Angle(degrees=value, preference="degrees")
    else:
        value = Angle(hours=value, preference="hours")
    return value


def valueToFloat(value: Any) -> float:
    """ """
    if value == "E":
        return 0
    try:
        value = float(value)
    except Exception:
        value = 0
    return value


def valueToAngle(value: Any, preference: str = "degrees") -> Angle:
    """ """
    value = valueToFloat(value)
    if preference == "degrees":
        value = Angle(degrees=value, preference="degrees")
    else:
        value = Angle(hours=value, preference="hours")
    return value


def valueToInt(value: Any) -> int:
    """ """
    try:
        value = int(value)
    except Exception:
        value = 0
    return value


def topoToAltAz(ha: Angle, dec: Angle, lat: Angle) -> tuple[Angle, Angle]:
    """ """
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
    """ """
    sign = int(np.sign(value))
    value = abs(value)
    power = 10**decimals
    n = int(7200 * power * value + 1) // 2
    n, fraction = divmod(n, power)
    n, seconds = divmod(n, 60)
    n, minutes = divmod(n, 60)

    return sign, n, minutes, seconds, fraction


def checkIsHours(value: str) -> bool:
    """ """
    if not isinstance(value, str):
        return False
    if "*" in value:
        return False
    if "+" in value:
        return False
    return "-" not in value


def convertToDMS(dec: Angle | float | int) -> str:
    """
    takes the given DEC value, which should be in DMS format (but different
    types) and convert it to solve-field readable string in sDD:MM:SS
    """
    if isinstance(dec, float | int):
        dec = Angle(degrees=dec)

    t = Angle.signed_dms(dec)
    sign = "+" if dec.degrees > 0 else "-"
    value = f"{sign}{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}"
    return value


def convertToHMS(ra: Angle | float | int) -> str:
    """
    takes the given RA value, which should be in HMS format (but different
    types) and convert it to solve-field readable string in HH:MM:SS
    """
    if isinstance(ra, float | int):
        ra = Angle(hours=ra)
    t = Angle.signed_hms(ra)
    value = f"{t[1]:02.0f}:{t[2]:02.0f}:{t[3]:02.0f}"
    return value


def formatLatLonToAngle(value: str, pf: str) -> float:
    """ """
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


def convertLatToAngle(value: str) -> float:
    """ """
    return formatLatLonToAngle(value, "SN")


def convertLonToAngle(value: str) -> float:
    """ """
    return formatLatLonToAngle(value, "WE")


def parseRaToAngleString(value: str) -> tuple[bool, bool, list[str]]:
    """ """
    value = value.strip()
    p1 = re.compile(r"([+-]?)(\d{1,3})H[\s:]*(\d\d)?[\s:]*(\d\d)?[.,]?(\d*)?")
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
    """ """
    isSexagesimal, isFloat, elements = parseRaToAngleString(value)

    if isFloat:
        angle = float(value.replace(",", "."))
    elif isSexagesimal:
        angle = float(elements[2])
        if elements[3] is not None:
            angle += float(elements[3]) / 60
        if elements[4] is not None:
            angle += float(elements[4]) / 3600
    else:
        angle = 0

    if angle >= 24 or angle < 0:
        angle = 0

    return Angle(hours=angle / 360 * 24) if isFloat else Angle(hours=angle)


def parseDecToAngleString(value: str) -> tuple[bool, bool, list[str]]:
    """ """
    value = value.strip()
    p1 = re.compile(r"([+-]?)(\d{1,3})Deg[\s:]*(\d\d)?[\s:]*(\d\d)?[.,]?(\d*)?")
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


def convertDecToAngle(value: str) -> Angle:
    """ """
    isSexagesimal, isFloat, elements = parseDecToAngleString(value)

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
    """ """
    formatStr = "{1:02}:{2:02}:{3:02}"
    return angle.hstr(format=formatStr)


def formatDstrToText(angle: Angle) -> str:
    """ """
    formatStr = "{0:+>1}{1:02}:{2:02}:{3:02}"
    return angle.dstr(format=formatStr)


def formatLatToText(angle: Angle) -> str:
    """ """
    sgn, h, m, s, frac = sexagesimalizeToInt(angle.degrees, 0)
    sign = "N" if sgn >= 0 else "S"
    text = f"{h:02d}{sign} {m:02d} {s:02d}"
    return text


def formatLonToText(angle: Angle) -> str:
    """ """
    sgn, h, m, s, frac = sexagesimalizeToInt(angle.degrees, 0)
    sign = "E" if sgn >= 0 else "W"
    text = f"{h:03d}{sign} {m:02d} {s:02d}"
    return text
