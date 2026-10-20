# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.convert import sexagesimalizeToInt, valueToInt
from mw4.mountcontrol.mountContext import MountContext
from mw4.mountcontrol.mountStatus import MountStatus
from skyfield.api import Angle
from skyfield.toposlib import GeographicPosition
from typing import ClassVar


class ObsSiteCommands:
    """Mixin with the mount command and response parsing methods of ObsSite.
    It relies on the attributes provided by ObsSite (parent, log, location,
    pointing and target properties).
    """

    parent: MountContext
    log = logging.getLogger("MW4")
    PIERSIDE_CODES: ClassVar[dict[int, str]] = {2: "W", 3: "E"}
    location: GeographicPosition | list | tuple
    status: int
    pierside: str
    piersideTarget: str
    flipped: bool

    def sendCommand(self, commandString: str, responseCheck: str = "") -> bool:
        """Send a command to the mount and return only the success flag."""
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(commandString, responseCheck=responseCheck)
        return suc

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
            self.log.warning("Wrong number of fields: [%s]", response)
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
            "keep": ":MS#" if self.status == MountStatus.TRACKING else ":MA#",
        }
        if slewType not in slewTypes:
            self.log.warning("Unknown slew type: [%s]", slewType)
            return False

        self.flipped = self.piersideTarget != self.pierside
        return self.sendCommand(":PO#" + slewTypes[slewType], responseCheck="0")

    def parseSetTargetResponse(self, response: list) -> bool:
        if len(response) != 4 or len(response[0]) < 3:
            self.log.debug("Missing return values: [%s]", response)
            return False
        result = response[0][0:2]
        if result.count("0") > 0:
            self.log.debug("Coordinates could not be set: [%s]", response)
            return False
        pierCode = valueToInt(response[0][2])
        # the mount codes the target pierside as 2 (west) and 3 (east)
        if pierCode in self.PIERSIDE_CODES:
            self.piersideTarget = self.PIERSIDE_CODES[pierCode]
        self.AltTarget = response[0][3:]
        self.AzTarget = response[1]
        self.raJNowTarget = response[2]
        self.decJNowTarget = response[3]
        return pierCode != 0

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
        return self.sendCommand(":shutdown#", responseCheck="1")

    def setLocation(self, location: GeographicPosition) -> bool:
        sgn, h, m, s, frac = sexagesimalizeToInt(location.longitude.degrees, 1)
        sign = "+" if sgn < 0 else "-"
        setLon = f":Sg{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#"

        sgn, h, m, s, frac = sexagesimalizeToInt(location.latitude.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        setLat = f":St{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"

        sign = "+" if location.elevation.m >= 0 else "-"
        setElev = f":Sev{sign}{location.elevation.m:06.1f}#"

        return self.sendCommand(setLon + setLat + setElev, responseCheck="1")

    def setLatitude(self, lat: Angle) -> bool:
        sgn, h, m, s, frac = sexagesimalizeToInt(lat.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        commandString = f":St{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"
        return self.sendCommand(commandString, responseCheck="1")

    def setLongitude(self, lon: Angle) -> bool:
        sgn, h, m, s, frac = sexagesimalizeToInt(lon.degrees, 1)
        sign = "+" if sgn < 0 else "-"
        commandString = f":Sg{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#"
        return self.sendCommand(commandString, responseCheck="1")

    def setElevation(self, elev: float) -> bool:
        sign = "+" if elev >= 0 else "-"
        commandString = f":Sev{sign}{abs(elev):06.1f}#"
        return self.sendCommand(commandString, responseCheck="1")

    def startTracking(self) -> bool:
        return self.sendCommand(":PO#:AP#")

    def stopTracking(self) -> bool:
        return self.sendCommand(":RT9#")

    def park(self) -> bool:
        return self.sendCommand(":hP#")

    def unpark(self) -> bool:
        return self.sendCommand(":PO#")

    def parkOnActualPosition(self) -> bool:
        return self.sendCommand(":PiP#", responseCheck="1")

    def stop(self) -> bool:
        return self.sendCommand(":STOP#")

    def flip(self) -> bool:
        return self.sendCommand(":FLIP#", responseCheck="1")

    def moveNorth(self) -> bool:
        return self.sendCommand(":PO#:Mn#")

    def moveEast(self) -> bool:
        return self.sendCommand(":PO#:Me#")

    def moveSouth(self) -> bool:
        return self.sendCommand(":PO#:Ms#")

    def moveWest(self) -> bool:
        return self.sendCommand(":PO#:Mw#")

    def stopMoveAll(self) -> bool:
        return self.sendCommand(":Q#")

    def stopMoveNorth(self) -> bool:
        return self.sendCommand(":Qn#")

    def stopMoveEast(self) -> bool:
        return self.sendCommand(":Qe#")

    def stopMoveSouth(self) -> bool:
        return self.sendCommand(":Qs#")

    def stopMoveWest(self) -> bool:
        return self.sendCommand(":Qw#")

    def syncPositionToTarget(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":CMCFG0#:CM#"
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return False
        if len(response) < 2:
            self.log.debug("Missing return values: [%s]", response)
            return False
        return response[1].startswith("Coord")

    def setHighPrecision(self) -> bool:
        return self.sendCommand(":U2#")
