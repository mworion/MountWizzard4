# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.convert import sexagesimalizeToInt, valueToInt
from mw4.mountcontrol.mountContext import MountContext
from skyfield.api import Angle
from skyfield.toposlib import GeographicPosition
from typing import Any


class ObsSiteCommands:
    """Mixin with the mount command and response parsing methods of ObsSite.
    It relies on the attributes provided by ObsSite (parent, log, location,
    pointing and target properties).
    """

    parent: MountContext
    log = logging.getLogger("MW4")
    location: Any
    piersideTarget: Any

    def parseLocation(self, response: list, numberOfChunks: int) -> bool:
        """
        Due to compatibility with the LX200 protocol, east longitude is transmitted
        as negative; we invert the sign so that east longitude is positive internally.
        """
        if len(response) != numberOfChunks:
            self.log.warning("Wrong number of chunks")
            return False
        elev = response[0]
        # LX200 protocol encodes east as negative - swap sign to east-positive convention
        lon = response[1].replace("-", "+") if "-" in response[1] else response[1].replace("+", "-")
        lat = response[2]
        self.location = [lat, lon, elev]
        return True

    def getLocation(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":Gev#:Gg#:Gt#"
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parseLocation(response, numberOfChunks)

    def parsePointing(self, response: list, numberOfChunks: int) -> bool:
        if len(response) != numberOfChunks:
            self.log.warning("Wrong number of chunks")
            return False
        infoSplit = response[3].split(",")
        angularSplit = response[4].split(",")
        if len(infoSplit) < 8 or len(angularSplit) < 5:
            self.log.warning(f"Wrong number of fields: [{response}]")
            return False
        self.timeSidereal = response[0]
        self.ut1_utc = response[1].replace("L", "")
        self.statusSat = response[2]
        self.raJNow = infoSplit[0]
        self.decJNow = infoSplit[1]
        self.pierside = infoSplit[2]
        self.Az = infoSplit[3]
        self.Alt = infoSplit[4]
        self.timeJD = infoSplit[5]
        self.status = infoSplit[6]
        self.statusSlew = infoSplit[7] == "1"
        self.angularPosRA = angularSplit[1]
        self.angularPosDEC = angularSplit[3]
        self.errorAngularPosRA = angularSplit[2]
        self.errorAngularPosDEC = angularSplit[4]
        return True

    def pollPointing(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":GS#:GDUT#:TLESCK#:Ginfo#:GaE#"
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parsePointing(response, numberOfChunks)

    def startSlewing(self, slewType: str = "normal") -> bool:
        slewTypes = {
            "normal": ":MS#",
            "notrack": ":MA#",
            "stop": ":MaX#",
            "park": ":PaX#",
            "polar": ":MSap#",
            "ortho": ":MSao#",
            "keep": ":MS#" if self.status == 0 else ":MA#",
        }

        self.flipped = self.piersideTarget != self.pierside
        conn = Connection(self.parent)
        commandString = ":PO#" + slewTypes[slewType]
        suc, _, _ = conn.communicate(commandString, responseCheck="0")
        return suc

    def parseSetTargetResponse(self, response: list) -> bool:
        if len(response) != 4 or len(response[0]) < 3:
            self.log.debug(f"Missing return values: [{response}]")
            return False
        result = response[0][0:2]
        if result.count("0") > 0:
            self.log.debug(f"Coordinates could not be set: [{response}]")
            return False
        self.piersideTarget = valueToInt(response[0][2])
        self.AltTarget = response[0][3:]
        self.AzTarget = response[1]
        self.raJNowTarget = response[2]
        self.decJNowTarget = response[3]
        return valueToInt(response[0][2]) != 0

    def setTargetAltAz(self, alt: Angle, az: Angle) -> bool:
        sgn, h, m, s, frac = sexagesimalizeToInt(alt.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        setAlt = f":Sa{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"

        sgn, h, m, s, frac = sexagesimalizeToInt(az.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        setAz = f":Sz{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#"

        getTargetStatus = ":GTsid#:Ga#:Gz#:Gr#:Gd#"

        conn = Connection(self.parent)
        commandString = setAlt + setAz + getTargetStatus
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return False
        return self.parseSetTargetResponse(response)

    def setTargetRaDec(self, ra: Angle, dec: Angle) -> bool:
        sgn, h, m, s, frac = sexagesimalizeToInt(ra.hours, 2)
        setRa = f":Sr{h:02d}:{m:02d}:{s:02d}.{frac:02d}#"

        sgn, h, m, s, frac = sexagesimalizeToInt(dec.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        setDec = f":Sd{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"

        getTargetStatus = ":GTsid#:Ga#:Gz#:Gr#:Gd#"

        conn = Connection(self.parent)
        commandString = setRa + setDec + getTargetStatus
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return False
        return self.parseSetTargetResponse(response)

    def shutdown(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":shutdown#", responseCheck="1")
        return suc

    def setLocation(self, location: GeographicPosition) -> bool:
        conn = Connection(self.parent)

        sgn, h, m, s, frac = sexagesimalizeToInt(location.longitude.degrees, 1)
        sign = "+" if sgn < 0 else "-"
        setLon = f":Sg{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#"

        sgn, h, m, s, frac = sexagesimalizeToInt(location.latitude.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        setLat = f":St{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"

        sign = "+" if location.elevation.m > 0 else "-"
        setElev = f":Sev{sign}{location.elevation.m:06.1f}#"

        commandString = setLon + setLat + setElev
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setLatitude(self, lat: Angle) -> bool:
        conn = Connection(self.parent)
        sgn, h, m, s, frac = sexagesimalizeToInt(lat.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        commandString = f":St{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setLongitude(self, lon: Angle) -> bool:
        conn = Connection(self.parent)
        sgn, h, m, s, frac = sexagesimalizeToInt(lon.degrees, 1)
        sign = "+" if sgn < 0 else "-"
        commandString = f":Sg{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setElevation(self, elev: float) -> bool:
        conn = Connection(self.parent)
        sign = "+" if elev > 0 else "-"
        commandString = f":Sev{sign}{abs(elev):06.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def startTracking(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":PO#:AP#")
        return suc

    def stopTracking(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":RT9#")
        return suc

    def park(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":hP#")
        return suc

    def unpark(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":PO#")
        return suc

    def parkOnActualPosition(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":PiP#", responseCheck="1")
        return suc

    def stop(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":STOP#")
        return suc

    def flip(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":FLIP#", responseCheck="1")
        return suc

    def moveNorth(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":PO#:Mn#")
        return suc

    def moveEast(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":PO#:Me#")
        return suc

    def moveSouth(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":PO#:Ms#")
        return suc

    def moveWest(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":PO#:Mw#")
        return suc

    def stopMoveAll(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":Q#")
        return suc

    def stopMoveNorth(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":Qn#")
        return suc

    def stopMoveEast(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":Qe#")
        return suc

    def stopMoveSouth(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":Qs#")
        return suc

    def stopMoveWest(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":Qw#")
        return suc

    def syncPositionToTarget(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":CMCFG0#:CM#"
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return False
        if len(response) < 2:
            self.log.debug(f"Missing return values: [{response}]")
            return False
        return response[1].startswith("Coord")

    def setHighPrecision(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":U2#"
        suc, _, _ = conn.communicate(commandString)
        return suc
