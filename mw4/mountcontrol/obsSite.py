############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform

# external packages
from skyfield.api import wgs84, Angle, load, Loader
from skyfield.toposlib import GeographicPosition
import numpy as np

# local imports
from base.transform import diffModulusSign
from .connection import Connection
from .convert import stringToAngle
from .convert import stringToDegree
from .convert import valueToFloat
from .convert import valueToInt
from .convert import valueToAngle
from .convert import sexagesimalizeToInt


class ObsSite(object):
    """
    The class Site inherits all information and handling of site data
    attributes of the connected mount and provides the abstracted interface
    to a 10 micron mount. as the mount's time base is julian date, we use this
    value as time base as well. for that reason we should remind how the mount
    calculates the julian date. it is derived from utc. to basically on the
    timeJD for skyfield we calculate julian date from ut1 based on julian date
    from mount based on utc and the value delta utc, ut1 also given from the
    mount.

    The Site class needs as parameter a ts object from skyfield.api to
    be able to make all the necessary calculations about time from and to mount
    """

    log = logging.getLogger("MW4")

    STAT = {
        "0": "Tracking",
        "1": "Stopped after STOP",
        "2": "Slewing to park position",
        "3": "Unparking",
        "4": "Slewing to home position",
        "5": "Parked",
        "6": "Slewing or going to stop",
        "7": "Tracking Off no move",
        "8": "Motor low temperature",
        "9": "Tracking outside limits",
        "10": "Following Satellite",
        "11": "User OK Needed",
        "98": "Unknown Status",
        "99": "Error",
    }

    def __init__(self, parent, verbose=False):
        self.parent = parent
        self.pathToData = parent.pathToData
        self.verbose = verbose
        self.loader = None
        self.AzDirection = None
        self.flipped = False
        self.lastAz = None
        self._location = None
        self.ts = None
        self._timeJD = None
        self.timePC = None
        self._timeDiff = np.full(25, 0.0)
        self.ut1_utc = None
        self._timeSidereal = None
        self._raJNow = None
        self._raJNowTarget = None
        self._decJNow = None
        self._decJNowTarget = None
        self._haJNow = None
        self._haJNowTarget = None
        self._angularPosRA = None
        self._angularPosDEC = None
        self._errorAngularPosRA = None
        self._errorAngularPosDEC = None
        self._angularPosRATarget = None
        self._angularPosDECTarget = None
        self._pierside = None
        self._piersideTarget = None
        self._Alt = None
        self._AltTarget = None
        self._Az = None
        self._AzTarget = None
        self._status = None
        self._statusSat = None
        self._statusSlew = None
        self.UTC2TT = None
        self.setLoaderAndTimescale()

    def setLoaderAndTimescale(self) -> None:
        """ """
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
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if isinstance(value, GeographicPosition):
            self._location = value
            return

        if not isinstance(value, (list, tuple)):
            self._location = None
            self.log.info(f"Malformed value: {value}")
            return

        if len(value) != 3:
            self._location = None
            self.log.info(f"Malformed value: {value}")
            return

        lat, lon, elev = value
        lat = stringToDegree(lat)
        lon = stringToDegree(lon)
        elev = valueToFloat(elev)
        if lat is None or lon is None or elev is None:
            self._location = None
            self.log.info(f"Malformed value: {value}")
            return

        self._location = wgs84.latlon(
            latitude_degrees=lat, longitude_degrees=lon, elevation_m=elev
        )

    @property
    def timeJD(self):
        if self._timeJD is None:
            return self.ts.now()
        else:
            return self._timeJD

    @timeJD.setter
    def timeJD(self, value):
        value = valueToFloat(value)
        if value:
            self._timeJD = self.ts.tt_jd(value + self.UTC2TT)
        else:
            self._timeJD = None

    @property
    def timeDiff(self):
        return np.mean(self._timeDiff)

    @timeDiff.setter
    def timeDiff(self, value):
        return

    @property
    def ut1_utc(self):
        return self._ut1_utc

    @ut1_utc.setter
    def ut1_utc(self, value):
        value = valueToFloat(value)
        if value is not None:
            self._ut1_utc = value / 86400
        else:
            self._ut1_utc = None

    @property
    def timeSidereal(self):
        return self._timeSidereal

    @timeSidereal.setter
    def timeSidereal(self, value):
        if isinstance(value, str):
            self._timeSidereal = stringToAngle(value, preference="hours")
        elif isinstance(value, float):
            self._timeSidereal = valueToAngle(value, preference="hours")
        elif isinstance(value, Angle):
            self._timeSidereal = value
        else:
            self._timeSidereal = None

    @property
    def raJNow(self):
        return self._raJNow

    @raJNow.setter
    def raJNow(self, value):
        if isinstance(value, Angle):
            self._raJNow = value
            return
        self._raJNow = valueToAngle(value, preference="hours")

    @property
    def raJNowTarget(self):
        return self._raJNowTarget

    @raJNowTarget.setter
    def raJNowTarget(self, value):
        if isinstance(value, Angle):
            self._raJNowTarget = value
            return
        self._raJNowTarget = stringToAngle(value, preference="hours")

    @property
    def haJNow(self):
        if self._timeSidereal is None or self._raJNow is None:
            return None
        else:
            # ha is always positive between 0 and 24 hours
            ha = (self._timeSidereal.hours - self._raJNow.hours + 24) % 24
            return Angle(hours=ha)

    @property
    def haJNowTarget(self):
        if self._timeSidereal is None or self._raJNowTarget is None:
            return None
        else:
            # ha is always positive between 0 and 24 hours
            ha = (self._timeSidereal.hours - self._raJNowTarget.hours + 24) % 24
            return Angle(hours=ha)

    @property
    def decJNow(self):
        return self._decJNow

    @decJNow.setter
    def decJNow(self, value):
        if isinstance(value, Angle):
            self._decJNow = value
            return
        self._decJNow = valueToAngle(value, preference="degrees")

    @property
    def decJNowTarget(self):
        return self._decJNowTarget

    @decJNowTarget.setter
    def decJNowTarget(self, value):
        if isinstance(value, Angle):
            self._decJNowTarget = value
            return
        self._decJNowTarget = stringToAngle(value, preference="degrees")

    @property
    def angularPosRA(self):
        return self._angularPosRA

    @angularPosRA.setter
    def angularPosRA(self, value):
        if isinstance(value, Angle):
            self._angularPosRA = value
            return
        self._angularPosRA = valueToAngle(value, preference="degrees")

    @property
    def angularPosDEC(self):
        return self._angularPosDEC

    @angularPosDEC.setter
    def angularPosDEC(self, value):
        if isinstance(value, Angle):
            self._angularPosDEC = value
            return
        self._angularPosDEC = valueToAngle(value, preference="degrees")

    @property
    def errorAngularPosRA(self):
        return self._errorAngularPosRA

    @errorAngularPosRA.setter
    def errorAngularPosRA(self, value):
        if isinstance(value, Angle):
            self._errorAngularPosRA = value
            return
        self._errorAngularPosRA = valueToAngle(value, preference="degrees")

    @property
    def errorAngularPosDEC(self):
        return self._errorAngularPosDEC

    @errorAngularPosDEC.setter
    def errorAngularPosDEC(self, value):
        if isinstance(value, Angle):
            self._errorAngularPosDEC = value
            return
        self._errorAngularPosDEC = valueToAngle(value, preference="degrees")

    @property
    def angularPosRATarget(self):
        return self._angularPosRATarget

    @angularPosRATarget.setter
    def angularPosRATarget(self, value):
        if isinstance(value, Angle):
            self._angularPosRATarget = value
            return
        self._angularPosRATarget = valueToAngle(value, preference="degrees")

    @property
    def angularPosDECTarget(self):
        return self._angularPosDECTarget

    @angularPosDECTarget.setter
    def angularPosDECTarget(self, value):
        if isinstance(value, Angle):
            self._angularPosDECTarget = value
            return
        self._angularPosDECTarget = valueToAngle(value, preference="degrees")

    @property
    def pierside(self):
        return self._pierside

    @pierside.setter
    def pierside(self, value):
        if value in ["E", "W", "e", "w"]:
            value = value.capitalize()
            self._pierside = value
        else:
            self._pierside = None
            self.log.info(f"Malformed value: {value}")

    @property
    def piersideTarget(self):
        return self._piersideTarget

    @piersideTarget.setter
    def piersideTarget(self, value):
        if value == "2":
            self._piersideTarget = "W"
        elif value == "3":
            self._piersideTarget = "E"
        else:
            self._piersideTarget = None
            self.log.info(f"Malformed value: {value}")

    @property
    def Alt(self):
        return self._Alt

    @Alt.setter
    def Alt(self, value):
        if isinstance(value, Angle):
            self._Alt = value
            return
        self._Alt = valueToAngle(value, preference="degrees")

    @property
    def AltTarget(self):
        return self._AltTarget

    @AltTarget.setter
    def AltTarget(self, value):
        if isinstance(value, Angle):
            self._AltTarget = value
            return
        self._AltTarget = stringToAngle(value, preference="degrees")

    @property
    def Az(self):
        return self._Az

    @Az.setter
    def Az(self, value):
        if isinstance(value, Angle):
            self._Az = value
        else:
            self._Az = valueToAngle(value, preference="degrees")

        if self._Az is None:
            self.AzDirection = 0
            return

        az = self._Az.degrees
        if self.lastAz is None:
            self.AzDirection = 0
        else:
            direction = np.sign(diffModulusSign(self.lastAz, az, 360))
            self.AzDirection = direction
        self.lastAz = az

    @property
    def AzTarget(self):
        return self._AzTarget

    @AzTarget.setter
    def AzTarget(self, value):
        if isinstance(value, Angle):
            self._AzTarget = value
            return
        self._AzTarget = stringToAngle(value, preference="degrees")

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = valueToInt(value)
        if self._status not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 98, 99]:
            self._status = None

    @property
    def statusSat(self):
        return self._statusSat

    @statusSat.setter
    def statusSat(self, value):
        self._statusSat = value
        if self._statusSat not in ["V", "P", "S", "T", "Q", "E"]:
            self._statusSat = None

    def statusText(self):
        if self._status is None:
            return None
        reference = f"{self._status:d}"
        if reference in self.STAT:
            return self.STAT[reference]

    @property
    def statusSlew(self):
        return self._statusSlew

    @statusSlew.setter
    def statusSlew(self, value):
        self._statusSlew = bool(value)

    def parseLocation(self, response: list, numberOfChunks: int) -> bool:
        """
        due to compatibility to LX200 protocol east is negative, so we change that
        in class we would like to keep the correct sign for east is positive
        """
        if len(response) != numberOfChunks:
            self.log.warning("Wrong number of chunks")
            return False
        elev = response[0]
        lon = None
        if "-" in response[1]:
            lon = response[1].replace("-", "+")
        if "+" in response[1]:
            lon = response[1].replace("+", "-")
        lat = response[2]
        self.location = [lat, lon, elev]
        return True

    def getLocation(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":U2#:Gev#:Gg#:Gt#"
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parseLocation(response, numberOfChunks)

    def parsePointing(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("Wrong number of chunks")
            return False
        self.timeSidereal = response[0]
        self.ut1_utc = response[1].replace("L", "")
        self.statusSat = response[2]
        responseSplit = response[3].split(",")
        self.raJNow = responseSplit[0]
        self.decJNow = responseSplit[1]
        self.pierside = responseSplit[2]
        self.Az = responseSplit[3]
        self.Alt = responseSplit[4]
        self.timeJD = responseSplit[5]
        self.status = responseSplit[6]
        self.statusSlew = responseSplit[7] == "1"
        responseSplit = response[4].split(",")
        self.angularPosRA = responseSplit[1]
        self.angularPosDEC = responseSplit[3]
        self.errorAngularPosRA = responseSplit[2]
        self.errorAngularPosDEC = responseSplit[4]
        return True

    def pollPointing(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":U2#:GS#:GDUT#:TLESCK#:Ginfo#:GaE#"
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parsePointing(response, numberOfChunks)

    def pollSyncClock(self) -> bool:
        """ """
        if platform.system() == "Windows":
            corrTerm = -0.001
        elif platform.system() == "Linux":
            corrTerm = -0.001
        elif platform.system() == "Darwin":
            corrTerm = -0.011
        else:
            corrTerm = 0
        conn = Connection(self.parent.host)
        commandString = ":GJD1#"
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return False

        self.timePC = self.ts.now()
        timeMount = valueToFloat(response[0])
        if timeMount is None:
            return False
        timeMount = self.ts.tt_jd(timeMount + self.UTC2TT)
        self._timeDiff = np.roll(self._timeDiff, 1)
        delta = (self.timePC - timeMount) * 86400 + corrTerm
        self._timeDiff[0] = delta
        return True

    def adjustClock(self, delta: float) -> bool:
        """ """
        conn = Connection(self.parent.host)
        sign = "+" if delta >= 0 else "-"
        delta = abs(delta)
        delta = min(delta, 999)
        commandString = f":NUtim{sign}{delta:03.0f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def startSlewing(self, slewType: str = "normal"):
        """ """
        slewTypes = dict(
            normal=":MS#",
            notrack=":MA#",
            stop=":MaX#",
            park=":PaX#",
            polar=":MSap#",
            ortho=":MSao#",
            keep="",
        )

        keepSlewType = ":MS#" if self.status == 0 else ":MA#"
        slewTypes["keep"] = keepSlewType

        self.flipped = self._piersideTarget != self.pierside
        conn = Connection(self.parent.host)
        commandString = ":PO#" + slewTypes[slewType]
        suc, _, _ = conn.communicate(commandString, responseCheck="0")
        return suc

    def setTargetAltAz(self, alt: Angle, az: Angle):
        """ """
        sgn, h, m, s, frac = sexagesimalizeToInt(alt.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        setAlt = f":Sa{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"

        sgn, h, m, s, frac = sexagesimalizeToInt(az.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        setAz = f":Sz{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#"

        getTargetStatus = ":U2#:GTsid#:Ga#:Gz#:Gr#:Gd#"

        conn = Connection(self.parent.host)
        commandString = setAlt + setAz + getTargetStatus
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return False

        result = response[0][0:2]
        if result.count("0") > 0:
            self.log.debug(f"Coordinates could not be set: [{response}]")
            return False

        if len(response) != 4:
            self.log.debug(f"Missing return values: [{response}]")
            return False

        self.piersideTarget = response[0][2]
        self.AltTarget = response[0][3:]
        self.AzTarget = response[1]
        self.raJNowTarget = response[2]
        self.decJNowTarget = response[3]
        return suc

    def setTargetRaDec(self, ra: Angle, dec: Angle) -> bool:
        """ """
        sgn, h, m, s, frac = sexagesimalizeToInt(ra.hours, 2)
        setRa = f":Sr{h:02d}:{m:02d}:{s:02d}.{frac:02d}#"

        sgn, h, m, s, frac = sexagesimalizeToInt(dec.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        setDec = f":Sd{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"

        getTargetStatus = ":U2#:GTsid#:Ga#:Gz#:Gr#:Gd#"

        conn = Connection(self.parent.host)
        commandString = setRa + setDec + getTargetStatus
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return False

        result = response[0][0:2]
        if result.count("0") > 0:
            self.log.debug(f"Coordinates could not be set: [{response}]")
            return False

        if len(response) != 4:
            self.log.debug(f"Missing return values: [{response}]")
            return False

        self.piersideTarget = response[0][2]
        self.AltTarget = response[0][3:]
        self.AzTarget = response[1]
        self.raJNowTarget = response[2]
        self.decJNowTarget = response[3]
        return suc

    def shutdown(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":shutdown#", responseCheck="1")
        return suc

    def setLocation(self, location: GeographicPosition) -> bool:
        """ """
        conn = Connection(self.parent.host)

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
        """ """
        conn = Connection(self.parent.host)
        sgn, h, m, s, frac = sexagesimalizeToInt(lat.degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        commandString = f":St{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setLongitude(self, lon: Angle) -> bool:
        """ """
        conn = Connection(self.parent.host)
        sgn, h, m, s, frac = sexagesimalizeToInt(lon.degrees, 1)
        sign = "+" if sgn < 0 else "-"
        commandString = f":Sg{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setElevation(self, elev: (int, float)) -> bool:
        """ """
        conn = Connection(self.parent.host)
        sign = "+" if elev > 0 else "-"
        commandString = f":Sev{sign}{abs(elev):06.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def startTracking(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":PO#:AP#")
        return suc

    def stopTracking(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":RT9#")
        return suc

    def park(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":hP#")
        return suc

    def unpark(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":PO#")
        return suc

    def parkOnActualPosition(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":PiP#", responseCheck="1")
        return suc

    def stop(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":STOP#")
        return suc

    def flip(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":FLIP#", responseCheck="1")
        return suc

    def moveNorth(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":PO#:Mn#")
        return suc

    def moveEast(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":PO#:Me#")
        return suc

    def moveSouth(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":PO#:Ms#")
        return suc

    def moveWest(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":PO#:Mw#")
        return suc

    def stopMoveAll(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":Q#")
        return suc

    def stopMoveNorth(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":Qn#")
        return suc

    def stopMoveEast(self):
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":Qe#")
        return suc

    def stopMoveSouth(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":Qs#")
        return suc

    def stopMoveWest(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":Qw#")
        return suc

    def syncPositionToTarget(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":CMCFG0#:CM#"
        suc, response, _ = conn.communicate(commandString)
        if not suc:
            return False
        return response[1].startswith("Coord")
