# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
import numpy as np
from mw4.base.transform import diffModulusSign
from mw4.mountcontrol.angleProperty import AngleProperty
from mw4.mountcontrol.convert import (
    stringToAngle,
    stringToDegree,
    valueToAngle,
    valueToFloat,
    valueToInt,
)
from mw4.mountcontrol.mountContext import MountContext
from mw4.mountcontrol.mountStatus import STATUS_LABELS, MountStatus
from mw4.mountcontrol.obsSiteCommands import ObsSiteCommands
from skyfield.api import Angle, Loader, load, wgs84
from skyfield.timelib import Time, Timescale
from skyfield.toposlib import GeographicPosition
from typing import ClassVar


class ObsSite(ObsSiteCommands):
    """
    The class Site inherits all information and handling site data
    attributes of the connected mount and provides the abstracted interface
    to a 10-micron mount. As the mount's time base is julian date, we use this
    value as time base as well. For that reason we should remind how the mount
    calculates the julian date. It is derived from utc. To basically on the
    timeJD for skyfield we calculate julian date from ut1 based on julian date
    from mount based on utc and the value delta utc, ut1 also given from the
    mount.

    The Site class needs as a parameter a ts object from skyfield.api to
    be able to make all the necessary calculations about time from and to mount
    """

    log = logging.getLogger("MW4")

    # Derived from MountStatus / STATUS_LABELS - do not duplicate.
    _STATUS_VALID: frozenset[int] = frozenset(int(s) for s in MountStatus)
    STAT: ClassVar[dict[str, str]] = {str(int(s)): label for s, label in STATUS_LABELS.items()}

    STAT_SAT: ClassVar = {
        "V": "slewing to transit",
        "P": "stopped, waiting sat",
        "S": "slewing to catch sat",
        "T": "tracking the sat",
        "Q": "transit ended",
        "E": "no slew requested",
    }

    def __init__(self, parent: MountContext, verbose: bool = False) -> None:
        self.parent = parent
        self.pathToData = parent.pathToData
        self.verbose = verbose
        self.loader: Loader | None = None
        self.AzDirection: int = 1
        self.flipped: bool = False
        self.lastAz: float = 0
        self._location: GeographicPosition = wgs84.latlon(
            latitude_degrees=0, longitude_degrees=0, elevation_m=0
        )
        self.ts: Timescale = load.timescale(builtin=True)
        self._timeJD: Time = self.ts.now()
        self.ut1_utc: float = 0
        self._timeSidereal: Angle = Angle(hours=0)
        self._raJNow: Angle = Angle(hours=0)
        self._raJNowTarget: Angle = Angle(hours=0)
        self._decJNow: Angle = Angle(degrees=0)
        self._decJNowTarget: Angle = Angle(degrees=0)
        self._haJNow: Angle = Angle(hours=0)
        self._haJNowTarget: Angle = Angle(degrees=0)
        self._angularPosRA: Angle = Angle(degrees=0)
        self._angularPosDEC: Angle = Angle(degrees=0)
        self._errorAngularPosRA: Angle = Angle(degrees=0)
        self._errorAngularPosDEC: Angle = Angle(degrees=0)
        self._angularPosRATarget: Angle = Angle(degrees=0)
        self._angularPosDECTarget: Angle = Angle(degrees=0)
        self._pierside: str = "E"
        self._piersideTarget: str = "E"
        self._Alt: Angle = Angle(degrees=0)
        self._AltTarget: Angle = Angle(degrees=0)
        self._Az: Angle = Angle(degrees=0)
        self._AzTarget: Angle = Angle(degrees=0)
        self._status: int = MountStatus.ERROR
        self._statusSat: str = "E"
        self._statusSlew: bool = False
        self.UTC2TT: float = 0
        self.setLoaderAndTimescale()

    def setLoaderAndTimescale(self) -> None:
        timescaleFile = self.pathToData / "finals2000A.all"
        if timescaleFile.is_file():
            self.loader = Loader(self.pathToData, verbose=self.verbose)
            self.ts = self.loader.timescale(builtin=False)
            self.log.info("Using downloaded timescale version")
        else:
            self.loader = load
            self.ts = self.loader.timescale(builtin=True)
            self.log.info("Using built-in timescale version")

        t = self.ts.now()
        self.UTC2TT = (t.delta_t + t.dut1) / 86400

    @property
    def location(self) -> GeographicPosition:
        return self._location

    @location.setter
    def location(self, value: GeographicPosition | list | tuple) -> None:
        if isinstance(value, GeographicPosition):
            self._location = value
            return

        if not isinstance(value, list | tuple):
            self.log.info(f"Malformed value: {value}")
            return

        if len(value) != 3:
            self.log.info(f"Malformed value: {value}")
            return

        lat, lon, elev = value
        lat = stringToDegree(lat)
        lon = stringToDegree(lon)
        elev = valueToFloat(elev)
        self._location = wgs84.latlon(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elev)

    @property
    def timeJD(self) -> Time:
        if self.parent.mountIsUp:
            return self._timeJD
        return self.ts.now()

    @timeJD.setter
    def timeJD(self, value: str | float | None) -> None:
        value = valueToFloat(value)
        self._timeJD = self.ts.tt_jd(value + self.UTC2TT)

    @property
    def ut1_utc(self) -> float:
        return self._ut1_utc

    @ut1_utc.setter
    def ut1_utc(self, value: str | float | None) -> None:
        value = valueToFloat(value)
        self._ut1_utc = value / 86400

    @property
    def timeSidereal(self) -> Angle:
        return self._timeSidereal

    @timeSidereal.setter
    def timeSidereal(self, value: str | float | Angle) -> None:
        if isinstance(value, str):
            self._timeSidereal = stringToAngle(value, preference="hours")
        elif isinstance(value, (int, float)):
            self._timeSidereal = valueToAngle(value, preference="hours")
        elif isinstance(value, Angle):
            self._timeSidereal = value

    raJNow = AngleProperty("hours")

    raJNowTarget = AngleProperty("hours", parser="string")

    @property
    def haJNow(self) -> Angle:
        # ha, is always positive between 0 and 24 hours
        ha = (self._timeSidereal.hours - self._raJNow.hours + 24) % 24
        return Angle(hours=ha)

    @property
    def haJNowTarget(self) -> Angle:
        # ha, is always positive between 0 and 24 hours
        ha = (self._timeSidereal.hours - self._raJNowTarget.hours + 24) % 24
        return Angle(hours=ha)

    decJNow = AngleProperty("degrees")

    decJNowTarget = AngleProperty("degrees", parser="string")

    angularPosRA = AngleProperty("degrees")

    angularPosDEC = AngleProperty("degrees")

    errorAngularPosRA = AngleProperty("degrees")

    errorAngularPosDEC = AngleProperty("degrees")

    angularPosRATarget = AngleProperty("degrees")

    angularPosDECTarget = AngleProperty("degrees")

    @property
    def pierside(self) -> str:
        return self._pierside

    @pierside.setter
    def pierside(self, value: str) -> None:
        if value in ["E", "W", "e", "w"]:
            value = value.capitalize()
            self._pierside = value
        else:
            self.log.info(f"Malformed value: {value}")

    @property
    def piersideTarget(self) -> str:
        return self._piersideTarget

    @piersideTarget.setter
    def piersideTarget(self, value: int) -> None:
        if value == 2:
            self._piersideTarget = "W"
        elif value == 3:
            self._piersideTarget = "E"

    Alt = AngleProperty("degrees")

    AltTarget = AngleProperty("degrees", parser="string")

    @property
    def Az(self) -> Angle:
        return self._Az

    @Az.setter
    def Az(self, value: Angle | str | float | None) -> None:
        if isinstance(value, Angle):
            self._Az = value
        else:
            self._Az = valueToAngle(value, preference="degrees")

        az = self._Az.degrees
        direction = np.sign(diffModulusSign(self.lastAz, az, 360))
        self.AzDirection = direction
        self.lastAz = az

    AzTarget = AngleProperty("degrees", parser="string")

    @property
    def status(self) -> int:
        return self._status

    @status.setter
    def status(self, value: str | float | None) -> None:
        self._status = valueToInt(value)
        if self._status not in self._STATUS_VALID:
            self._status = MountStatus.ERROR

    @property
    def isTracking(self) -> bool:
        return self._status == MountStatus.TRACKING

    @property
    def isStopped(self) -> bool:
        return self._status == MountStatus.STOPPED

    @property
    def isParked(self) -> bool:
        return self._status == MountStatus.PARKED

    @property
    def isFollowingSatellite(self) -> bool:
        return self._status == MountStatus.FOLLOWING_SATELLITE

    def statusText(self) -> str:
        reference = f"{self._status:d}"
        text = self.STAT.get(reference, "unknown Status")
        # Slewing states already convey motion; the "settle" suffix only
        # applies to other states while the mount is settling.
        if self._status in (MountStatus.SLEWING_TO_PARK, MountStatus.SLEWING):
            return text
        return text + " - settle" if self.statusSlew else text

    @property
    def statusSat(self) -> str:
        return self._statusSat

    @statusSat.setter
    def statusSat(self, value: str) -> None:
        self._statusSat = value
        if self._statusSat not in ["V", "P", "S", "T", "Q", "E"]:
            self._statusSat = "E"

    def statusSatText(self) -> str:
        return self.STAT_SAT.get(self._statusSat, "error")

    @property
    def statusSlew(self) -> bool:
        return self._statusSlew

    @statusSlew.setter
    def statusSlew(self, value: bool | int | str) -> None:
        self._statusSlew = bool(value)
