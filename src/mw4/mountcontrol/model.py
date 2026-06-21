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
# Michael Würtenberger
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import logging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.convert import (
    sexagesimalizeToInt,
    stringToAngle,
    topoToAltAz,
    valueToAngle,
    valueToFloat,
    valueToInt,
)
from mw4.mountcontrol.modelStar import ModelStar
from mw4.mountcontrol.progStar import ProgStar
from skyfield.api import Angle, Star
from typing import Any


class Model:
    log = logging.getLogger("MW4")

    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self._starList: list = []
        self._nameList: list = []
        self._numberNames: int = 0
        self._numberStars: int = 0
        self.altitudeError: Angle = Angle(degrees=0)
        self.azimuthError: Angle = Angle(degrees=0)
        self.polarError: Angle = Angle(degrees=0)
        self.positionAngle: Angle = Angle(degrees=0)
        self.orthoError: Angle = Angle(degrees=0)
        self.altitudeTurns: float = 0
        self.azimuthTurns: float = 0
        self.terms: int = 0
        self.errorRMS: float = 0

    @property
    def starList(self) -> list[ModelStar]:
        return self._starList

    @starList.setter
    def starList(self, value: list[ModelStar]) -> None:
        self._starList = value

    @property
    def numberStars(self) -> int:
        return self._numberStars

    @numberStars.setter
    def numberStars(self, value: Any) -> None:
        self._numberStars = valueToInt(value)

    def addStar(self, value: ModelStar) -> None:
        self._starList.append(value)

    def delStar(self, value: int) -> None:
        value = valueToInt(value)
        if not (0 <= value < len(self._starList)):
            self.log.warning(f"invalid value: {value}")
            return
        self._starList.pop(value)

    def checkStarListOK(self) -> bool:
        return self._numberStars == len(self._starList)

    @property
    def nameList(self) -> list[str]:
        return self._nameList

    @nameList.setter
    def nameList(self, value: Any) -> None:
        self._nameList = (
            value if isinstance(value, list) and all(isinstance(x, str) for x in value) else []
        )

    @property
    def numberNames(self) -> int:
        return self._numberNames

    @numberNames.setter
    def numberNames(self, value: Any) -> None:
        self._numberNames = valueToInt(value)

    def addName(self, value: str) -> None:
        if not isinstance(value, str):
            self.log.warning(f"malformed value: {value}")
            return
        self._nameList.append(value)

    def parseNames(self, response: list, numberOfChunks: int) -> bool:
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        for name in response:
            if not name:
                continue
            self.addName(name)
        return True

    def parseNumberNames(self, response: list, numberOfChunks: int) -> bool:
        if len(response) != 1:
            self.log.warning("wrong number of chunks: expected exactly 1")
            return False
        self.numberNames = response[0]
        return True

    def getNameCount(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":modelcnt#"
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseNumberNames(response, numberOfChunks)
        return suc

    def getNames(self) -> bool:
        conn = Connection(self.parent)
        commandString = "".join(f":modelnam{i:d}#" for i in range(1, self.numberNames + 1))
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        self._nameList = []
        suc = self.parseNames(response, numberOfChunks)
        return suc

    def pollNames(self) -> bool:
        suc = self.getNameCount()
        if suc:
            suc = self.getNames()
        return suc

    def parseStars(self, response: list, numberOfChunks: int) -> bool:
        if len(response) != numberOfChunks:
            self.log.warning("Wrong number of chunks")
            return False
        for number, starData in enumerate(response):
            ra, dec, err, angle = starData.split(",")
            ra = stringToAngle(ra, preference="hours")
            dec = stringToAngle(dec, preference="degrees")
            coord = Star(ra=ra, dec=dec)
            errorRMS = valueToFloat(err)
            errorAngle = valueToAngle(angle)
            alt, az = topoToAltAz(ra, dec, self.parent.obsSite.location.latitude)
            modelStar = ModelStar(coord, errorRMS, errorAngle, number, alt, az)
            self.addStar(modelStar)
        return True

    def parseNumberStars(self, response: list[str], numberOfChunks: int) -> bool:
        if len(response) != numberOfChunks or len(response) == 0:
            self.log.warning("Wrong number of chunks")
            return False

        self.numberStars = response[0]
        if numberOfChunks < 2:
            self.log.warning("Wrong number of chunks")
            return False

        responseSplit = response[1].split(",")
        # if there are less than 3 points, we get 'E' as result of getain
        if response[0] in ["0", "1", "2"] and response[1] == "E":
            responseSplit = [None] * 9
        if len(responseSplit) != 9:
            self.log.warning("Wrong number of chunks in getain")
            return False

        self.azimuthError = valueToAngle(responseSplit[0], preference="degrees")
        self.altitudeError = valueToAngle(responseSplit[1], preference="degrees")
        self.polarError = valueToAngle(responseSplit[2], preference="degrees")
        self.positionAngle = valueToAngle(responseSplit[3], preference="degrees")
        self.orthoError = valueToAngle(responseSplit[4], preference="degrees")
        self.azimuthTurns = valueToFloat(responseSplit[5])
        self.altitudeTurns = valueToFloat(responseSplit[6])
        self.terms = valueToInt(responseSplit[7])
        self.errorRMS = valueToFloat(responseSplit[8])
        return True

    def getStarCount(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":getalst#:getain#"
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseNumberStars(response, numberOfChunks)
        return suc

    def getStars(self) -> bool:
        self._starList = []
        if self.numberStars == 0:
            return True

        commandString = "".join(f":getalp{i:d}#" for i in range(1, self.numberStars + 1))
        conn = Connection(self.parent)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseStars(response, numberOfChunks)
        return suc

    def pollStars(self) -> None:
        suc = self.getStarCount()
        if suc:
            self.getStars()

    def clearModel(self) -> bool:
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(":delalig#", responseCheck="")
        return suc

    def deletePoint(self, number: int) -> bool:
        if number < 0 or number > self._numberStars - 1:
            return False

        conn = Connection(self.parent)
        commandString = f":delalst{number + 1:d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def storeName(self, name: str) -> bool:
        conn = Connection(self.parent)
        commandString = f":modeldel0{name[:15]}#:modelsv0{name[:15]}#"
        suc, response, _ = conn.communicate(commandString)
        return suc and response[1] == "1"

    def loadName(self, name: str) -> bool:
        conn = Connection(self.parent)
        commandString = f":modelld0{name[:15]}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def deleteName(self, name: str) -> bool:
        conn = Connection(self.parent)
        commandString = f":modeldel0{name[:15]}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    @staticmethod
    def formatSexagesimalRA(hours: float) -> str:
        _, h, m, s, frac = sexagesimalizeToInt(hours, 1)
        return f"{h:02d}:{m:02d}:{s:02d}.{frac:1d}"

    @staticmethod
    def formatSexagesimalDec(degrees: float) -> str:
        sgn, h, m, s, frac = sexagesimalizeToInt(degrees, 1)
        sign = "+" if sgn >= 0 else "-"
        return f"{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}"

    @staticmethod
    def formatSexagesimalSidereal(hours: float) -> str:
        _, h, m, s, frac = sexagesimalizeToInt(hours, 2)
        return f"{h:02d}:{m:02d}:{s:02d}.{frac:02d}"

    def programModelFromStarList(self, build: list[ProgStar]) -> bool:
        parts = [":newalig#"]
        for aPoint in build:
            ra = self.formatSexagesimalRA(aPoint.mCoord.ra.hours)
            dec = self.formatSexagesimalDec(aPoint.mCoord.dec.degrees)
            pierside = aPoint.pierside

            raSolve = self.formatSexagesimalRA(aPoint.sCoord.ra.hours)
            decSolve = self.formatSexagesimalDec(aPoint.sCoord.dec.degrees)
            sidereal = self.formatSexagesimalSidereal(aPoint.sidereal.hours)

            comFormat = ":newalpt{0},{1},{2},{3},{4},{5}#"
            parts.append(comFormat.format(ra, dec, pierside, raSolve, decSolve, sidereal))

        conn = Connection(self.parent)
        commandString = "".join(parts) + ":endalig#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc
