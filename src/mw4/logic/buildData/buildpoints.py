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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import csv
import json
import logging
import random
from pathlib import Path

# external packages
import numpy as np
from scipy.spatial import distance
from skyfield import almanac
from skyfield.api import Angle, Star, Timescale
from skyfield.toposlib import GeographicPosition

# local imports
from mw4.base import transform


def HaDecToAltAz(ha: float, dec: float, lat: float) -> tuple[float, float]:
    """
    HaDecToAltAz is derived from http://www.stargazing.net/kepler/altaz.html
    """
    ha = (ha * 360 / 24 + 360.0) % 360.0
    dec = np.radians(dec)
    ha = np.radians(ha)
    lat = np.radians(lat)
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
    value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
    value = np.clip(value, -1.0, 1.0)
    A = np.arccos(value)
    az = 2 * np.pi - A if np.sin(ha) >= 0.0 else A
    az = float(np.degrees(az))
    alt = float(np.degrees(alt))
    return alt, az


class DataPoint:
    """ """

    FAILED = 0
    UNPROCESSED = 1
    SOLVED = 2

    log = logging.getLogger("MW4")

    DEC_N = {
        "min": [-15, 0, 15, 30, 45, 60, 75],
        "norm": [-15, 0, 15, 30, 45, 60, 75],
        "med": [-15, -5, 5, 15, 25, 40, 55, 70, 85],
        "max": [-15, -5, 5, 15, 25, 35, 45, 55, 65, 75, 85],
    }

    DEC_S = {
        "min": [-75, -60, -45, -30, -15, 0, 15],
        "norm": [-75, -60, -45, -30, -15, 0, 15],
        "med": [-85, -70, -55, -40, -25, -15, -5, 5, 15],
        "max": [-85, -75, -65, -55, -45, -35, -25, -15, -5, 5, 15],
    }

    STEP_N = {
        "min": [15, -15, 15, -15, 15, -30, 30],
        "norm": [10, -10, 10, -10, 10, -20, 20],
        "med": [10, -10, 10, -10, 10, -15, 15, -20, 20],
        "max": [10, -10, 10, -10, 10, -10, 10, -20, 20, -30, 30],
    }

    STEP_S = {
        "min": [30, -30, 15, -15, 15, -15, 15],
        "norm": [20, -20, 10, -10, 10, -10, 10],
        "med": [20, -20, 15, -15, 10, -10, 10, -10, 10],
        "max": [30, -30, 20, -20, 10, -10, 10, -10, 10, -10, 10],
    }
    START = {
        "min": [-120, -5, -120, -5, -120, -5, -120, 5, 120, 5, 120, 5, 120, 5],
        "norm": [-120, -5, -120, -5, -120, -5, -120, 5, 120, 5, 120, 5, 120, 5],
        "med": [
            -120,
            -5,
            -120,
            -5,
            -120,
            -5,
            -120,
            -5,
            -120,
            5,
            120,
            5,
            120,
            5,
            120,
            5,
            120,
            5,
        ],
        "max": [
            -120,
            -5,
            -120,
            -5,
            -120,
            -5,
            -120,
            -5,
            -120,
            -5,
            -120,
            5,
            120,
            5,
            120,
            5,
            120,
            5,
            120,
            5,
            120,
            5,
        ],
    }
    STOP = {
        "min": [0, -120, 0, -120, 0, -120, 0, 120, 0, 120, 0, 120, 0, 120],
        "norm": [0, -120, 0, -120, 0, -120, 0, 120, 0, 120, 0, 120, 0, 120],
        "med": [
            0,
            -120,
            0,
            -120,
            0,
            -120,
            0,
            -120,
            0,
            120,
            0,
            120,
            0,
            120,
            0,
            120,
            0,
            120,
            0,
        ],
        "max": [
            0,
            -120,
            0,
            -120,
            0,
            -120,
            0,
            -120,
            0,
            -120,
            0,
            120,
            0,
            120,
            0,
            120,
            0,
            120,
            0,
            120,
            0,
            120,
            0,
        ],
    }

    def __init__(self, app):
        self.app = app
        self.configDir: Path = app.mwGlob["configDir"]
        self._horizonP: list = []
        self._buildP: list = []

    @property
    def horizonP(self):
        return self._horizonP

    @horizonP.setter
    def horizonP(self, value: list[list]):
        self._horizonP = value

    @property
    def buildP(self):
        return self._buildP

    @buildP.setter
    def buildP(self, value: list[list]):
        self._buildP = value

    def addBuildP(self, value: tuple[int, int, int], position: int | None = None) -> None:
        """ """
        if position is None:
            position = len(self._buildP)

        high = self.app.mount.setting.horizonLimitHigh or 90
        low = self.app.mount.setting.horizonLimitLow or 0

        if value[0] > high:
            return
        if value[0] < low:
            return

        position = min(len(self._buildP), position)
        position = max(0, position)
        self._buildP.insert(position, value)

    def delBuildP(self, position: int) -> None:
        """ """
        if position < 0 or position > len(self._buildP) - 1:
            self.log.info(f"invalid position: {position}")
            return
        self._buildP.pop(position)

    def clearBuildP(self) -> None:
        """ """
        self._buildP.clear()

    def setStatusBuildP(self, number: int, status: int) -> None:
        """ """
        if 0 <= number < len(self._buildP):
            self._buildP[number][2] = status

    def setStatusBuildPSolved(self, number: int) -> None:
        """ """
        self.setStatusBuildP(number, self.SOLVED)

    def setStatusBuildPFailed(self, number: int) -> None:
        """ """
        self.setStatusBuildP(number, self.FAILED)

    def addHorizonP(self, value: tuple[int, int], position: int | None = None) -> None:
        """ """
        if position is None:
            position = len(self.horizonP)

        position = min(len(self._horizonP), position)
        position = max(0, position)
        self._horizonP.insert(position, value)

    def delHorizonP(self, position: int) -> None:
        """ """
        if 0 <= position < len(self._horizonP):
            self._horizonP.pop(position)

    def clearHorizonP(self) -> None:
        """"""
        self._horizonP.clear()

    @staticmethod
    def isCloseHorizonLine(
        point: tuple[int, int], margin: int, horizonI: list[tuple[int, int]]
    ) -> bool:
        """
        https://codereview.stackexchange.com/questions
        /28207/finding-the-closest-point-to-a-list-of-points
        """
        pointRef = np.asarray([point[1], point[0]])
        closest_index = distance.cdist([pointRef], horizonI).argmin()
        pointClose = horizonI[closest_index]
        val = np.sqrt(np.sum((pointRef - pointClose) ** 2))

        return val < margin

    def isAboveHorizon(self, point: tuple[int, int]) -> bool:
        """ """
        if point[1] > 360:
            point = (point[0], 360)
        if point[1] < 0:
            point = (point[0], 0)

        x = range(0, 361)
        if self.horizonP:
            xRef = [i[1] for i in self.horizonP]
            yRef = [i[0] for i in self.horizonP]
        else:
            xRef = [0]
            yRef = [0]

        y = np.interp(x, xRef, yRef)
        return point[0] > y[int(point[1])]

    def isCloseMeridian(self, point: tuple[int, int]) -> bool:
        """ """
        slew = self.app.mount.setting.meridianLimitSlew
        track = self.app.mount.setting.meridianLimitTrack

        if slew is None or track is None:
            return False

        value = max(slew, track)
        lower = 180 - value
        upper = 180 + value

        return lower < point[1] < upper

    def deleteBelowHorizon(self) -> None:
        """ """
        self._buildP = [x for x in self._buildP if self.isAboveHorizon(x)]

    def deleteCloseMeridian(self) -> None:
        """ """
        self._buildP = [x for x in self._buildP if not self.isCloseMeridian(x)]

    def deleteCloseHorizonLine(self, margin: int) -> None:
        """ """
        if not self.horizonP:
            return

        altH, azH = zip(*self.horizonP)
        azI = range(0, 361, 1)
        altI = np.interp(azI, azH, altH)
        horizonI = np.asarray([[x, y] for x, y in zip(azI, altI)])
        self._buildP = [
            x for x in self._buildP if not self.isCloseHorizonLine(x, margin, horizonI)
        ]

    def sort(
        self,
        points=list[tuple[int, int]],
        eastwest: bool = False,
        highlow: bool = False,
        sortDomeAz: bool = None,
        pierside: str = None,
    ):
        """ """
        east = [x for x in points if x[1] <= 180]
        west = [x for x in points if x[1] > 180]

        if eastwest:
            east = sorted(east, key=lambda x: -x[1])
            west = sorted(west, key=lambda x: -x[1])
        elif highlow:
            east = sorted(east, key=lambda x: -x[0])
            west = sorted(west, key=lambda x: -x[0])
        elif sortDomeAz:
            east = sorted(east, key=lambda x: -x[3])
            west = sorted(west, key=lambda x: -x[3])

        if pierside == "W" or pierside is None:
            self.buildP = east + west
        else:
            self.buildP = west + east

        return True

    def loadModel(self, fullFileName: Path) -> list[tuple[int, int]] | None:
        """ """
        with open(fullFileName) as handle:
            try:
                value = [[p["altitude"], p["azimuth"]] for p in json.load(handle)]
            except Exception as e:
                self.log.info(f"Cannot Model load: {fullFileName}, error: {e}")
                value = None
        return value

    def loadBPTS(self, fullFileName: Path) -> list[tuple[int, int]] | None:
        """ """
        with open(fullFileName) as f:
            try:
                value = json.load(f)
            except Exception as e:
                self.log.info(f"Cannot BPTS load: {fullFileName}, error: {e}")
                value = None
        return value

    def loadCSV(self, fullFileName: Path) -> list[tuple[int, int]] | None:
        """ """
        with open(fullFileName) as f:
            testLine = f.readline()

        delimiter = ";" if ";" in testLine else ","
        with open(fullFileName, encoding="utf-8-sig") as csvFile:
            try:
                reader = csv.reader(csvFile, delimiter=delimiter)
                value = [[int(row[0]), int(row[1])] for row in reader]
            except Exception as e:
                self.log.info(f"Cannot CSV load: {fullFileName}, error: {e}")
                value = None
        return value

    @staticmethod
    def checkFormat(value: tuple[float, float]) -> bool:
        """ """
        if not all(isinstance(x, list) for x in value):
            return False

        return all(len(x) == 2 for x in value)

    def loadBuildP(self, fullFileName: Path, ext: str = ".bpts") -> bool:
        """ """
        if not fullFileName.is_file():
            return False

        value = None
        if ext == ".csv":
            value = self.loadCSV(fullFileName)
        elif ext == ".bpts":
            value = self.loadBPTS(fullFileName)
        elif ext == ".model":
            value = self.loadModel(fullFileName)

        if value is None:
            return False
            
        points = [(x[0], x[1], self.UNPROCESSED) for x in value]
        self._buildP = points 
        self.saveBuildP(fullFileName.stem) 
        return True

    def saveBuildP(self, fileName: str) -> None:
        """ """
        fileName = self.configDir / (fileName + ".bpts")
        points = [(x[0], x[1]) for x in self.buildP]
        with open(fileName, "w") as handle:
            json.dump(points, handle, indent=4)

    def loadHorizonP(self, fileName: str, ext=".hpts") -> bool:
        """ """
        fullFileName = self.configDir / (fileName + ext)
        if not fullFileName.is_file():
            return False

        value = None
        if ext == ".csv":
            value = self.loadCSV(fullFileName)
        elif ext == ".hpts":
            value = self.loadBPTS(fullFileName)

        if value is None:
            return False

        self.horizonP = value
        self.horizonP.sort(key=lambda x: x[1])
        return True

    def saveHorizonP(self, fileName: str) -> None:
        """ """
        fullFileName = self.configDir / (fileName + ".hpts")
        with open(fullFileName, "w") as handle:
            json.dump(self.horizonP, handle, indent=4)

    def genHaDecParams(self, selection: str, lat: float) -> tuple[int, int, int, int]:
        """
        genHaDecParams selects the parameters for generating the boundaries for
         the next step processing greater circles. the parameters are sorted for
        different targets actually for minimum slew distance between the points.
        defined is only the east side of data, the west side will be mirrored to
        the east one.
        """
        if lat < 0:
            DEC = self.DEC_S
            STEP = self.STEP_S
        else:
            DEC = self.DEC_N
            STEP = self.STEP_N

        if selection not in DEC or selection not in STEP:
            return

        eastDec = DEC[selection]
        westDec = list(reversed(eastDec))
        decL = eastDec + westDec

        eastStepL = STEP[selection]
        westStepL = list(reversed(eastStepL))
        stepL = eastStepL + westStepL
        startL = self.START[selection]
        stopL = self.STOP[selection]

        yield from zip(decL, stepL, startL, stopL)

    def genGreaterCircle(self, selection: str = "norm") -> bool:
        """
        genGreaterCircle takes the generated boundaries for the range routine and
        transforms ha, dec to alt az. reasonable values for the alt az values
        are 5 to 85 degrees.
        """
        if not self.app.mount.obsSite.location:
            return False

        lat = self.app.mount.obsSite.location.latitude.degrees
        for dec, step, start, stop in self.genHaDecParams(selection, lat):
            for ha in range(start, stop, step):
                alt, az = HaDecToAltAz(ha / 10, dec, lat)

                # only values with the above horizon = 0
                if 5 <= alt <= 85 and 2 < az < 358:
                    self.addBuildP([alt, az, self.UNPROCESSED])
        return True

    def genGridGenerator(
        self, eastAlt: int, westAlt: int, minAz: int, stepAz: int, maxAz: int
    ) -> tuple[int, int, int]:
        """ """
        for i, alt in enumerate(eastAlt):
            if i % 2:
                for az in range(minAz, 180, stepAz):
                    yield [alt, az, self.UNPROCESSED]
            else:
                for az in range(180 - minAz, 0, -stepAz):
                    yield [alt, az, self.UNPROCESSED]

        for i, alt in enumerate(westAlt):
            if i % 2:
                for az in range(180 + minAz, 360, stepAz):
                    yield [alt, az, self.UNPROCESSED]
            else:
                for az in range(maxAz, 180, -stepAz):
                    yield [alt, az, self.UNPROCESSED]

    def genGrid(
        self,
        minAlt: int = 5,
        maxAlt: int = 85,
        numbRows: int = 5,
        numbCols: int = 6,
    ) -> bool:
        """
        genGrid generates a grid of points and transforms ha, dec to alt az.
        with given limits in alt, the min and max will be used as a hard
        condition. on az there is no given limit; therefore, a split over the
        whole space (omitting the meridian) is done. the simplest way to avoid
        hitting the meridian is to enforce the number of cols to be a factor of
        2. reasonable values for the grid are 5 to 85 degrees. defined is only
        the east side of data, the west side will be mirrored to the east one.
            the number of rows is 2 < x < 8
            the number of columns is 2 < x < 15
        """
        if not 5 <= minAlt <= 85:
            return False
        if not 5 <= maxAlt <= 85:
            return False
        if not maxAlt > minAlt:
            return False
        if not 1 < numbRows < 9:
            return False
        if not 1 < numbCols < 16:
            return False
        if numbCols % 2:
            return False

        minAlt = int(minAlt)
        maxAlt = int(maxAlt)
        numbCols = int(numbCols)
        numbRows = int(numbRows)

        stepAlt = int((maxAlt - minAlt) / (numbRows - 1))
        eastAlt = list(range(minAlt, maxAlt + 1, stepAlt))
        westAlt = list(reversed(eastAlt))

        stepAz = int(360 / numbCols)
        minAz = int(180 / numbCols)
        maxAz = 360 - minAz

        for point in self.genGridGenerator(eastAlt, westAlt, minAz, stepAz, maxAz):
            self.addBuildP(point)

        return True

    def genAlign(
        self, altBase: int = 30, azBase: int = 10, numberBase: int = 3) -> bool:
        """ """
        if not 5 <= altBase <= 85:
            return False
        if not 2 < numberBase < 13:
            return False
        if not 0 <= azBase < 360:
            return False

        stepAz = int(360 / numberBase)
        altBase = int(altBase)
        azBase = int(azBase) % stepAz
        numberBase = int(numberBase)

        for i in range(0, numberBase):
            az = azBase + i * stepAz
            self.addBuildP([altBase, az % 360, self.UNPROCESSED])

        return True

    def generateCelestialEquator(self) -> list[tuple[int, int]]:
        """ """
        celestialEquator = []
        if not self.app.mount.obsSite.location:
            return celestialEquator

        lat = self.app.mount.obsSite.location.latitude.degrees

        for dec in range(-75, 90, 15):
            for ha in range(-119, 120, 2):
                alt, az = HaDecToAltAz(ha / 10, dec, lat)
                if alt > 0:
                    celestialEquator.append((alt, az))

        for ha in range(-115, 120, 10):
            for dec in range(-90, 90, 2):
                alt, az = HaDecToAltAz(ha / 10, dec, lat)
                if alt > 0:
                    celestialEquator.append((alt, az))

        return celestialEquator

    def calcPath(
        self,
        ts: Timescale,
        numberPoints: int,
        edgeDSO: float,
        ha: Angle,
        dec: Angle,
        location: GeographicPosition,
    ) -> list[tuple[int, int, int]]:
        """ """
        buildP = []
        for i in range(numberPoints):
            starTime = ts.tt_jd(edgeDSO + i / numberPoints)
            az, alt = transform.J2000ToAltAz(ha, dec, starTime, location)
            if alt.degrees > 0:
                buildP.append([alt.degrees, az.degrees % 360, self.UNPROCESSED])
        return buildP

    def generateDSOPath(
        self,
        ha: Angle,
        dec: Angle,
        timeJD: float,
        location: GeographicPosition,
        numberPoints: int,
        keep: bool = False,
    ) -> None:
        """ """
        if not keep:
            self.clearBuildP()

        star = Star(ra=ha, dec=dec)
        startTime = timeJD
        ts = self.app.mount.obsSite.ts
        endTime = ts.tt_jd(timeJD.tt + 1.1)
        eph = self.app.ephemeris
        f = almanac.risings_and_settings(eph, star, location)
        f.step_days = 0.08
        t, y = almanac.find_discrete(startTime, endTime, f)

        index = next((x for x in y if x == 1), None)
        edgeDSO = int(ts.now().tt) - 0.5 if index is None else t[index].tt

        number = numberPoints
        buildPs = []
        while len(buildPs) < numberPoints:
            buildPs = self.calcPath(ts, number, edgeDSO, ha, dec, location)
            number += 1
        for buildP in buildPs:
            self.addBuildP(buildP)

    def generateGoldenSpiral(self, numberPoints: int) -> None:
        """
        https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere
        """
        indices = np.arange(0, numberPoints, dtype=float) + 0.5
        phi = np.arccos(1 - 2 * indices / numberPoints)
        theta = np.pi * (1 + 5**0.5) * indices

        altitude = 90 - np.degrees(phi)
        azimuth = np.degrees(theta) % 360

        for alt, az in zip(altitude, azimuth):
            if alt > 0:
                self.addBuildP([int(alt), int(az), self.UNPROCESSED])

    def ditherPoints(self) -> None:
        """ """
        for i, point in enumerate(self.buildP):
            alt = point[0]
            az = point[1]
            alt += random.uniform(-1, 1)
            az += random.uniform(-1, 1)
            self.buildP[i] = [alt, az, self.UNPROCESSED]
