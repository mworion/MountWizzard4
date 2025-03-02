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
# Python  v3.7.4
#
# Michael Würtenberger
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages

# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToFloat
from mountcontrol.convert import valueToInt
from mountcontrol.convert import valueToAngle
from mountcontrol.convert import sexagesimalizeToInt
from mountcontrol.progStar import ProgStar
from mountcontrol.modelStar import ModelStar


class Model(object):
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, parent):
        self.parent = parent
        self._starList = list()
        self._nameList = list()
        self._numberNames = 0
        self._numberStars = 0
        self._altitudeError = None
        self._azimuthError = None
        self._polarError = None
        self._positionAngle = None
        self._orthoError = None
        self._altitudeTurns = None
        self._azimuthTurns = None
        self._terms = None
        self._errorRMS = None

    @property
    def altitudeError(self):
        return self._altitudeError

    @altitudeError.setter
    def altitudeError(self, value):
        self._altitudeError = valueToAngle(value)

    @property
    def azimuthError(self):
        return self._azimuthError

    @azimuthError.setter
    def azimuthError(self, value):
        self._azimuthError = valueToAngle(value)

    @property
    def polarError(self):
        return self._polarError

    @polarError.setter
    def polarError(self, value):
        self._polarError = valueToAngle(value)

    @property
    def positionAngle(self):
        return self._positionAngle

    @positionAngle.setter
    def positionAngle(self, value):
        self._positionAngle = valueToAngle(value)

    @property
    def orthoError(self):
        return self._orthoError

    @orthoError.setter
    def orthoError(self, value):
        self._orthoError = valueToAngle(value)

    @property
    def altitudeTurns(self):
        return self._altitudeTurns

    @altitudeTurns.setter
    def altitudeTurns(self, value):
        self._altitudeTurns = valueToFloat(value)

    @property
    def azimuthTurns(self):
        return self._azimuthTurns

    @azimuthTurns.setter
    def azimuthTurns(self, value):
        self._azimuthTurns = valueToFloat(value)

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, value):
        # qci mount don't deliver this value
        if value == "":
            self.log.warning("QCI mount does not provide terms")
        self._terms = valueToFloat(value)

    @property
    def errorRMS(self):
        return self._errorRMS

    @errorRMS.setter
    def errorRMS(self, value):
        if value == "":
            self.log.warning("QCI mount does not provide RMS")
            return
        self._errorRMS = valueToFloat(value)

    @property
    def starList(self):
        return self._starList

    @starList.setter
    def starList(self, value):
        if not isinstance(value, list):
            self._starList = list()
            return
        if all([isinstance(x, ModelStar) for x in value]):
            self._starList = value
        else:
            self._starList = list()

    @property
    def numberStars(self):
        return self._numberStars

    @numberStars.setter
    def numberStars(self, value):
        if value is None:
            self._numberStars = None
        else:
            self._numberStars = valueToInt(value)

    def addStar(self, value: ModelStar) -> None:
        """ """
        self._starList.insert(len(self._starList), value)

    def delStar(self, value):
        """ """
        value = valueToInt(value)
        if value < 0 or value > len(self._starList) - 1:
            self.log.warning("invalid value: {0}".format(value))
            return
        self._starList.pop(value)

    def checkStarListOK(self):
        """ """
        if not self._numberStars:
            return False
        if self._numberStars == len(self._starList):
            return True
        else:
            return False

    @property
    def nameList(self):
        return self._nameList

    @nameList.setter
    def nameList(self, value):
        if not isinstance(value, list):
            self._nameList = list()
            return
        if all([isinstance(x, str) for x in value]):
            self._nameList = value
        else:
            self._nameList = list()

    @property
    def numberNames(self):
        return self._numberNames

    @numberNames.setter
    def numberNames(self, value):
        if value is None:
            self._numberNames = None
        else:
            self._numberNames = valueToInt(value)

    def addName(self, value: str) -> bool:
        """ """
        if not isinstance(value, str):
            self.log.warning("malformed value: {0}".format(value))
            return False
        self._nameList.insert(len(self._nameList), value)
        return True

    def delName(self, value: int) -> bool:
        """ """
        value = valueToInt(value)
        if value < 0 or value > len(self._nameList) - 1:
            self.log.warning("invalid value: {0}".format(value))
            return False
        self._nameList.pop(value)
        return True

    def checkNameListOK(self) -> bool:
        """ """
        if not self._numberNames:
            return False
        if self._numberNames == len(self._nameList):
            return True
        else:
            return False

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
            commandString += ":modelnam{0:d}#".format(i)

        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        self._nameList = list()
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
            ha, dec, err, angle = starData.split(",")
            modelStar = ModelStar(obsSite=self.parent.obsSite)
            modelStar.coord = (ha, dec)
            modelStar.errorRMS = err
            modelStar.errorAngle = angle
            modelStar.number = number + 1
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

        self.azimuthError = responseSplit[0]
        self.altitudeError = responseSplit[1]
        self.polarError = responseSplit[2]
        self.positionAngle = responseSplit[3]
        self.orthoError = responseSplit[4]
        self.azimuthTurns = responseSplit[5]
        self.altitudeTurns = responseSplit[6]
        self.terms = responseSplit[7]
        self.errorRMS = responseSplit[8]
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
        self._starList = list()
        if self.numberStars == 0:
            return True

        commandString = ""
        for i in range(1, self.numberStars + 1):
            commandString += ":getalp{0:d}#".format(i)

        conn = Connection(self.parent.host)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        suc = self.parseStars(response, numberOfChunks)
        return suc

    def pollStars(self):
        """ """
        suc = self.getStarCount()
        if suc:
            suc = self.getStars()
        return suc

    def pollCount(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":modelcnt#:getalst#"

        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning("Wrong number of chunks")
            return False

        if len(response) != 2:
            self.log.warning("Wrong number of chunks")
            return False

        self.numberNames = response[0]
        self.numberStars = response[1]
        return True

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
        commandString = ":delalst{0:d}#".format(number)
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
