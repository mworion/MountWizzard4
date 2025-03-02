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

# external packages
from skyfield.api import Angle

# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToFloat
from mountcontrol.tleParams import TLEParams
from mountcontrol.trajectoryParams import TrajectoryParams


class Satellite(object):
    """ """

    log = logging.getLogger("MW4")

    TLES = {
        "E": "No transit pre calculated",
        "F": "Slew failed",
        "V": "Slewing to start and track",
        "S": "Slewing to catch satellite",
        "Q": "Transit ended, no tracking",
    }

    TLESCK = {
        "V": "Slewing to the start of the transit",
        "P": "Waiting for the satellite",
        "S": "Slewing to catch satellite",
        "T": "Tracking the satellite",
        "Q": "Transit ended, no tracking",
        "E": "No slew to satellite requested",
    }

    def __init__(self, parent):
        self.parent = parent
        self.obsSite = parent.obsSite
        self.tleParams = TLEParams(obsSite=parent.obsSite)
        self.trajectoryParams = TrajectoryParams(obsSite=parent.obsSite)

    def parseGetTLE(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        if response[0] == "E":
            return False

        lines = response[0].split("$0A")
        if len(lines) != 4:
            return False

        self.tleParams.name = lines[0].rstrip()
        self.tleParams.l0 = lines[0]
        self.tleParams.l1 = lines[1]
        self.tleParams.l2 = lines[2]
        return True

    def getTLE(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, response, numberOfChunks = conn.communicate(":TLEG#")
        if not suc:
            return False
        return self.parseGetTLE(response, numberOfChunks)

    def setTLE(self, line0: str, line1: str, line2: str) -> bool:
        """
        The TLE format is described here:
        https://www.celestrak.com/NORAD/documentation/tle-fmt.asp
        For example, loading the NOAA 14 element set of that page can be
        accomplished with:
        TLEL0NOAA·14·················
        1·23455U·94089A···97320.90946019··.00000140··00000-0··10191-3·0··2621
        2·23455··99.0090·272.6745·0008546·223.1686·136.8816·14.11711747148495
        """
        if len(line1) != 69 or len(line2) != 69:
            return False

        commandString = f":TLEL0{line0}$0a{line1}$0a{line2}#"
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def parseCalcTLE(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        if len(response) != 3:
            self.log.warning("wrong number of chunks")
            return False
        if "E" in response:
            return False

        value = response[0].split(",")
        if len(value) != 2:
            return False
        alt, az = value

        value = response[1].split(",")
        if len(value) != 2:
            return False
        ra, dec = value

        value = response[2].split(",")
        if len(value) == 3:
            start, end, flip = value
        elif len(value) == 1:
            flip = value[0]
            start = None
            end = None
        else:
            return False

        self.tleParams.altitude = alt
        self.tleParams.azimuth = az
        self.tleParams.ra = ra
        self.tleParams.dec = dec
        self.tleParams.flip = flip
        self.tleParams.jdStart = start
        self.tleParams.jdEnd = end
        return True

    def calcTLE(self, julD: float, duration: int = 1440) -> bool:
        """
        transformation UTC <-> TT time system needed
        """
        if not 0 < duration < 1441:
            return False

        julD -= self.obsSite.UTC2TT
        conn = Connection(self.parent.host)
        command = f":TLEGAZ{julD}#:TLEGEQ{julD}#:TLEP{julD},{duration}#"
        suc, response, numberOfChunks = conn.communicate(command)
        if not suc:
            return False
        return self.parseCalcTLE(response, numberOfChunks)

    def getCoordsFromTLE(self, julD: float) -> bool:
        """
        need to do transformation UTC <-> TT time system
        """
        julD -= self.obsSite.UTC2TT

        conn = Connection(self.parent.host)
        command = f":TLEGAZ{julD}#:TLEGEQ{julD}#"
        suc, response, _ = conn.communicate(command)
        if not suc:
            return False

        value = response[0].split(",")
        if len(value) != 2:
            return False

        alt, az = value
        self.tleParams.altitude = alt
        self.tleParams.azimuth = az

        value = response[1].split(",")
        if len(value) != 2:
            return False

        self.tleParams.ra, self.tleParams.dec = value
        return True

    def slewTLE(self) -> tuple:
        """ """
        conn = Connection(self.parent.host)
        suc, response, numberOfChunks = conn.communicate(":TLES#")
        if numberOfChunks != 1:
            return False, "Error"

        message = self.TLES.get(response[0], "Error")
        return suc, message

    def parseStatTLE(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        if len(response) != 1:
            self.log.warning("wrong number of chunks")
            return False
        if not response[0]:
            return False

        self.tleParams.message = self.TLESCK.get(response[0], "Error")
        return True

    def statTLE(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, response, numberOfChunks = conn.communicate(":TLESCK#")
        if not suc:
            return False
        return self.parseStatTLE(response, numberOfChunks)

    def startProgTrajectory(self, julD: float) -> bool:
        """
        transformation UTC <-> TT time system needed at the beginning
        """
        julD -= self.obsSite.UTC2TT

        commandString = f":TRNEW{julD}#"
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def addTrajectoryPoint(self, alt: Angle, az: Angle) -> bool:
        """ """
        commandString = ""
        az = az.degrees
        alt = alt.degrees
        for azimuth, altitude in zip(az, alt):
            commandString += f":TRADD{azimuth},{altitude}#"

        conn = Connection(self.parent.host)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        if len(response) != len(az):
            self.log.warning("wrong number of chunks")
            return False

        for i in range(0, len(az)):
            if response[i] == "E":
                return False

        return True

    def preCalcTrajectory(self, replay: bool = False) -> bool:
        """ """
        self.trajectoryParams.flip = None
        self.trajectoryParams.jdStart = None
        self.trajectoryParams.jdEnd = None

        cmd = ":TRREPLAY#" if replay else ":TRP#"
        conn = Connection(self.parent.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        if len(response) != 1:
            self.log.warning("wrong number of chunks")
            return False

        # should be 'E' only , actually wrong 'N' in
        if response[0] in ["E", "N"]:
            return False

        value = response[0].split(",")
        if len(value) == 3:
            start, end, flip = value
        else:
            return False

        self.trajectoryParams.flip = flip
        self.trajectoryParams.jdStart = start
        self.trajectoryParams.jdEnd = end
        return True

    def getTrackingOffsets(self) -> bool:
        """ """
        cmd = ":TROFFGET1#:TROFFGET2#:TROFFGET3#:TROFFGET4#"
        conn = Connection(self.parent.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        if len(response) != 4:
            self.log.warning("wrong number of chunks")
            return False

        val = valueToFloat(response[0])
        if val is not None:
            self.trajectoryParams.offsetRA = val

        val = valueToFloat(response[1])
        if val is not None:
            self.trajectoryParams.offsetDEC = val

        val = valueToFloat(response[2])
        if val is not None:
            self.trajectoryParams.offsetDECcorr = val

        val = valueToFloat(response[3])
        if val is not None:
            self.trajectoryParams.offsetTime = val

        return True

    def setTrackingFirst(self, first: Angle) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":TROFFSET1,{first.degrees:+05.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def setTrackingSecond(self, second: Angle) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":TROFFSET2,{second.degrees:+05.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def setTrackingFirstCorr(self, firstCorr: Angle) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":TROFFSET3,{firstCorr.degrees:+05.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def setTrackingTime(self, time: float) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":TROFFSET4,{time:+05.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def addTrackingFirst(self, first: Angle) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":TROFFADD1,{first.degrees:+05.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def addTrackingSecond(self, second: Angle) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":TROFFADD2,{second.degrees:+05.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def addTrackingFirstCorr(self, firstCorr: Angle) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":TROFFADD3,{firstCorr.degrees:+05.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def addTrackingTime(self, time: float) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":TROFFADD4,{time:+05.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc

    def clearTrackingOffsets(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":TROFFCLR#", responseCheck="V")
        return suc
