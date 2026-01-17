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
# Licence APL2.0
#
###########################################################
import logging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.convert import (
    sexagesimalizeToInt,
    valueToAngle,
    valueToFloat,
    valueToInt,
    stringToAngle,
    topoToAltAz,
)
from mw4.mountcontrol.modelStar import ModelStar
from mw4.mountcontrol.progStar import ProgStar
from skyfield.api import Angle, Star


class Model:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, parent):
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
    def starList(self):
        return self._starList

    @starList.setter
    def starList(self, value: list[ModelStar]):
        self._starList = value

    @property
    def numberStars(self):
        return self._numberStars

    @numberStars.setter
    def numberStars(self, value):
        self._numberStars = valueToInt(value)

    def addStar(self, value: ModelStar) -> None:
        """ """
        self._starList.append(value)

    def delStar(self, value: int):
        """ """
        value = valueToInt(value)
        if value < 0 or value > len(self._starList) - 1:
            self.log.warning(f"invalid value: {value}")
            return
        self._starList.pop(value)

    def checkStarListOK(self):
        """ """
        return self._numberStars == len(self._starList)

    @property
    def nameList(self):
        return self._nameList

    @nameList.setter
    def nameList(self, value):
        if not isinstance(value, list):
            self._nameList = []
            return
        if all(isinstance(x, str) for x in value):
            self._nameList = value
        else:
            self._nameList = []

    @property
    def numberNames(self):
        return self._numberNames

    @numberNames.setter
    def numberNames(self, value):
        self._numberNames = valueToInt(value)

    def addName(self, value: str) -> None:
        """ """
        if not isinstance(value, str):
            self.log.warning(f"malformed value: {value}")
            return
        self._nameList.insert(len(self._nameList), value)

    def parseNames(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        for name in response:
            if not name:
                continue
            self.addName(name)
        return True

    def parseNumberNames(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        if len(response) != 1:
            self.log.warning("wrong number of chunks")
            return False
        self.numberNames = response[0]
        return True

    def getNameCount(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":modelcnt#"
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseNumberNames(response, numberOfChunks)
        return suc

    def getNames(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ""
        for i in range(1, self.numberNames + 1):
            commandString += f":modelnam{i:d}#"

        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        self._nameList = []
        suc = self.parseNames(response, numberOfChunks)
        return suc

    def pollNames(self) -> bool:
        """ """
        suc = self.getNameCount()
        if suc:
            suc = self.getNames()
        return suc

    def parseStars(self, response: list, numberOfChunks: int) -> bool:
        """ """
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
            modelStar = ModelStar(coord, errorRMS, errorAngle, number + 1, alt, az)
            self.addStar(modelStar)
        return True

    def parseNumberStars(self, response: list, numberOfChunks: int) -> bool:
        """ """
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
        self.terms = valueToFloat(responseSplit[7])
        self.errorRMS = valueToFloat(responseSplit[8])
        return True

    def getStarCount(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":getalst#:getain#"
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseNumberStars(response, numberOfChunks)
        return suc

    def getStars(self) -> bool:
        """ """
        self._starList = []
        if self.numberStars == 0:
            return True

        commandString = ""
        for i in range(1, self.numberStars + 1):
            commandString += f":getalp{i:d}#"

        conn = Connection(self.parent.host)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseStars(response, numberOfChunks)
        return suc

    def pollStars(self) -> None:
        """ """
        suc = self.getStarCount()
        if suc:
            self.getStars()

    def clearModel(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":delalig#", responseCheck="")
        return suc

    def deletePoint(self, number: int) -> bool:
        """ """
        if number < 1 or number > self._numberStars:
            return False

        conn = Connection(self.parent.host)
        commandString = f":delalst{number:d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def storeName(self, name: str) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":modeldel0{name[:15]}#:modelsv0{name[:15]}#"
        suc, response, _ = conn.communicate(commandString)
        return suc and response[1] == "1"

    def loadName(self, name: str) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":modelld0{name[:15]}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def deleteName(self, name: str) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":modeldel0{name[:15]}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def programModelFromStarList(self, build: list[ProgStar]) -> bool:
        """ """
        commandString = ":newalig#"
        for aPoint in build:
            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.mCoord.ra.hours, 1)
            ra = f"{h:02d}:{m:02d}:{s:02d}.{frac:1d}"

            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.mCoord.dec.degrees, 1)
            sign = "+" if sgn >= 0 else "-"
            dec = f"{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}"

            pierside = aPoint.pierside

            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.sCoord.ra.hours, 1)
            raSolve = f"{h:02d}:{m:02d}:{s:02d}.{frac:1d}"

            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.sCoord.dec.degrees, 1)
            sign = "+" if sgn >= 0 else "-"
            decSolve = f"{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}"

            sgn, h, m, s, frac = sexagesimalizeToInt(aPoint.sidereal.hours, 2)
            sidereal = f"{h:02d}:{m:02d}:{s:02d}.{frac:02d}"

            comFormat = ":newalpt{0},{1},{2},{3},{4},{5}#"
            value = comFormat.format(ra, dec, pierside, raSolve, decSolve, sidereal)
            commandString += value

        conn = Connection(self.parent.host)
        commandString += ":endalig#"
        suc, _, _ = conn.communicate(commandString, responseCheck="V")
        return suc
