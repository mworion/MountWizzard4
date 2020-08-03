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
# GUI with PyQT5 for python
#
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import os
import json
import random
import csv
# external packages
import numpy as np
import skyfield.api
# local imports
from mw4.base.loggerMW import CustomLogger
from mw4.base import transform

__all__ = ['HaDecToAltAz',
           'DataPoint',
           ]


def HaDecToAltAz(ha, dec, lat):
    """
    HaDecToAltAz is derived from http://www.stargazing.net/kepler/altaz.html

    :param ha: hour angle in [h]
    :param dec: declination in [deg]
    :param lat: latitude of observer
    :return: altitude and azimuth
    """

    ha = (ha * 360 / 24 + 360.0) % 360.0
    dec = np.radians(dec)
    ha = np.radians(ha)
    lat = np.radians(lat)
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
    value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
    value = np.clip(value, -1.0, 1.0)
    A = np.arccos(value)
    if np.sin(ha) >= 0.0:
        az = 2 * np.pi - A
    else:
        az = A
    az = np.degrees(az)
    alt = np.degrees(alt)
    return alt, az


class DataPoint(object):
    """
    The class Data inherits all information and handling of modeldata data and other
    attributes. this includes horizon data, model points data and their persistence

        >>> data = DataPoint(
        >>>                  app=None,
        >>>                  )
    """

    __all__ = ['DataPoint',
               'genGreaterCircle',
               'genGrid',
               'genInitial',
               'loadBuildP',
               'saveBuildP',
               'clearPoints',
               'deleteBelowHorizon',
               'sort',
               'loadHorizonP',
               'saveHorizonP',
               'clearHorizonP',
               'generateCelestialEquator',
               'generateDSOPath',
               'generateGoldenSpiral',
               'genAlign',
               'hip',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    # data for generating greater circles, dec and step only for east, west is reversed
    DEC = {'min': [-15, 0, 15, 30, 45, 60, 75],
           'norm': [-15, 0, 15, 30, 45, 60, 75],
           'med': [-15, -5, 5, 15, 25, 40, 55, 70, 85],
           'max': [-15, -5, 5, 15, 25, 35, 45, 55, 65, 75, 85],
           }
    STEP = {'min': [15, -15, 15, -15, 15, -30, 30],
            'norm': [10, -10, 10, -10, 10, -20, 20],
            'med': [10, -10, 10, -10, 10, -10, 10, -30, 30],
            'max': [10, -10, 10, -10, 10, -10, 10, -10, 10, -30, 30],
            }
    START = {'min': [-120, -5, -120, -5, -120, -5, -120,
                     5, 120, 5, 120, 5, 120, 5],
             'norm': [-120, -5, -120, -5, -120, -5, -120,
                      5, 120, 5, 120, 5, 120, 5],
             'med': [-120, -5, -120, -5, -120, -5, -120, -5, -120,
                     5, 120, 5, 120, 5, 120, 5, 120, 5],
             'max': [-120, -5, -120, -5, -120, -5, -120, -5, -120, -5, -120,
                     5, 120, 5, 120, 5, 120, 5, 120, 5, 120, 5],
             }
    STOP = {'min': [0, -120, 0, -120, 0, -120, 0,
                    120, 0, 120, 0, 120, 0, 120],
            'norm': [0, -120, 0, -120, 0, -120, 0,
                     120, 0, 120, 0, 120, 0, 120],
            'med': [0, -120, 0, -120, 0, -120, 0, -120, 0,
                    120, 0, 120, 0, 120, 0, 120, 0, 120, 0],
            'max': [0, -120, 0, -120, 0, -120, 0, -120, 0, -120, 0,
                    120, 0, 120, 0, 120, 0, 120, 0, 120, 0, 120, 0],
            }

    def __init__(self, app=None):

        self.app = app
        self.configDir = app.mwGlob['configDir']
        self._horizonP = list()
        self._buildP = list()

    @staticmethod
    def checkHorizonBoundaries(value):
        """
        checkHorizonBoundaries secures that the horizon always has the points (0, 0) at the
        beginning of the list and (0, 360) at the end of the list.

        :return: True for test purpose
        """

        if not value:
            retValue = [(0, 0), (0, 360)]
            return retValue

        retValue = list() + value

        if retValue[0] != (0, 0):
            retValue = [(0, 0)] + retValue

        horMax = len(retValue)
        if retValue[horMax - 1] != (0, 360):
            retValue = retValue + [(0, 360)]

        return retValue

    @property
    def horizonP(self):
        value = self.checkHorizonBoundaries(self._horizonP)
        return value

    @horizonP.setter
    def horizonP(self, value):
        if not isinstance(value, list):
            self._horizonP.clear()
            return
        if not all([isinstance(x, tuple) for x in value]):
            self.log.warning('Malformed value: {0}'.format(value))
            self._horizonP.clear()
            return
        self._horizonP.clear()
        self._horizonP += value
        return

    @property
    def buildP(self):
        return self._buildP

    @buildP.setter
    def buildP(self, value):
        if not isinstance(value, list):
            self._buildP = list()
            return
        if not all([isinstance(x, tuple) for x in value]):
            self.log.warning('Malformed value: {0}'.format(value))
            self._buildP = list()
            return
        self._buildP = value

    def addBuildP(self, value=None, position=None):
        """
        addBuildP extends the list of modeldata points. the new point could be added at the end
        of the list (default) or in any location in the list.

        :param value: value to be inserted
        :param position: position in list
        :return:
        """

        if value is None:
            return False
        if not isinstance(value, tuple):
            self.log.warning('malformed value: {0}'.format(value))
            return False
        if len(value) != 2:
            self.log.warning('malformed value: {0}'.format(value))
            return False
        if position is None:
            position = len(self._buildP)
        if not isinstance(position, (int, float)):
            self.log.warning('malformed position: {0}'.format(position))
            return False
        if self.app.mount.setting.horizonLimitHigh is not None:
            high = self.app.mount.setting.horizonLimitHigh
        else:
            high = 90
        if self.app.mount.setting.horizonLimitLow is not None:
            low = self.app.mount.setting.horizonLimitLow
        else:
            low = 0
        if value[0] > high:
            return False
        if value[0] < low:
            return False
        position = int(position)
        position = min(len(self._buildP), position)
        position = max(0, position)
        self._buildP.insert(position, value)
        return True

    def delBuildP(self, position):
        """
        delBuildP deletes one point from the modeldata points list at the given index.

        :param position:
        :return:
        """

        if not isinstance(position, (int, float)):
            self.log.warning('malformed position: {0}'.format(position))
            return False
        position = int(position)
        if position < 0 or position > len(self._buildP) - 1:
            self.log.warning('invalid position: {0}'.format(position))
            return False
        self._buildP.pop(position)
        return True

    def clearBuildP(self):
        self._buildP.clear()

    def addHorizonP(self, value=None, position=None):
        """
        addHorizonP extends the list of modeldata points. the new point could be added at the
        end of the list (default) or in any location in the list.

        :param value:
        :param position:
        :return:
        """

        if value is None:
            return False
        if not isinstance(value, tuple):
            self.log.warning('malformed value: {0}'.format(value))
            return False
        if len(value) != 2:
            self.log.warning('malformed value: {0}'.format(value))
            return False
        if position is None:
            position = len(self.horizonP)
        if not isinstance(position, (int, float)):
            self.log.warning('malformed position: {0}'.format(position))
            return False
        position = int(position)
        position = min(len(self._horizonP), position)
        position = max(0, position)
        self._horizonP.insert(position, value)
        return True

    def delHorizonP(self, position):
        """
        delHorizonP deletes one point from the modeldata points list at the given index.

        :param position:
        :return:
        """

        if not isinstance(position, (int, float)):
            self.log.warning('malformed position: {0}'.format(position))
            return False
        position = int(position)
        if position < 0 or position > len(self._horizonP) - 1:
            self.log.warning('invalid position: {0}'.format(position))
            return False
        self._horizonP.pop(position)
        return True

    def clearHorizonP(self):
        self._horizonP.clear()

    def isAboveHorizon(self, point):
        """
        isAboveHorizon calculates for a given point the relationship to the actual horizon
        and determines if this point is above the horizon line. for that there will be a
        linear interpolation for the horizon line points.

        :param point:
        :return:
        """

        if point[1] > 360:
            point = (point[0], 360)
        if point[1] < 0:
            point = (point[0], 0)
        x = range(0, 361)
        y = np.interp(x,
                      [i[1] for i in self.horizonP],
                      [i[0] for i in self.horizonP],
                      )
        if point[0] > y[int(point[1])]:
            return True
        else:
            return False

    def isCloseMeridian(self, point):
        """
        isCloseMeridian check if a point is in inner to meridian slew limit

        :param point:
        :return: status
        """

        slew = self.app.mount.setting.meridianLimitSlew
        track = self.app.mount.setting.meridianLimitTrack

        if slew is None or track is None:
            return True

        value = max(slew, track)

        lower = 180 - value
        upper = 180 + value
        if lower < point[1] < upper:
            return False
        else:
            return True

    def deleteBelowHorizon(self):
        """
        deleteBelowHorizon deletes all points which are below horizon line

        :return: true for test purpose
        """
        self._buildP = [x for x in self._buildP if self.isAboveHorizon(x)]
        return True

    def deleteCloseMeridian(self):
        """
        deleteCloseMeridian deletes all points which are too close to the meridian and
        therefore need to flip all the time

        :return: true for test purpose
        """
        self._buildP = [x for x in self._buildP if self.isCloseMeridian(x)]
        return True

    def sort(self, eastwest=False, highlow=False, pierside=None):
        """

        :param eastwest: flag if to be sorted east - west
        :param highlow:  flag if sorted high low altitude
        :param pierside:  start pierside sorting with this position
        :return: true for test purpose
        """

        if eastwest and highlow:
            return False
        if not eastwest and not highlow and pierside is None:
            return False

        east = [x for x in self._buildP if x[1] <= 180]
        west = [x for x in self._buildP if x[1] > 180]

        if eastwest:
            east = sorted(east, key=lambda x: -x[1])
            west = sorted(west, key=lambda x: -x[1])

        if highlow:
            east = sorted(east, key=lambda x: -x[0])
            west = sorted(west, key=lambda x: -x[0])

        if pierside == 'E':
            self._buildP = west + east
        else:
            self._buildP = east + west

        return True

    def loadJSON(self, fileName, ext):
        """

        :param fileName: name of file to be handled
        :param ext: extension of file to be handled
        :return: value: loaded data
        """
        fileName = self.configDir + '/' + fileName + ext
        if not os.path.isfile(fileName):
            return None

        try:
            with open(fileName, 'r') as handle:
                value = json.load(handle)
        except Exception as e:
            self.log.warning('Cannot BPTS load: {0}, error: {1}'.format(fileName, e))
            value = None
        else:
            value = [tuple(x) for x in value]
        return value

    def loadCSV(self, fileName, ext, delimiter=','):
        """

        :param fileName: name of file to be handled
        :param ext: extension of file to be handled
        :param delimiter: delimiter of file to be handled
        :return: value: loaded data
        """
        fileName = self.configDir + '/' + fileName + ext
        if not os.path.isfile(fileName):
            return None

        try:
            value = []
            with open(fileName, 'r') as handle:
                reader = csv.reader(handle, delimiter=delimiter)
                for x in reader:
                    x = x[:2]
                    convertedX = [float(val) for val in x]
                    if delimiter == ',':
                        value.append(convertedX)
                    else:
                        value.append(reversed(convertedX))
        except Exception as e:
            self.log.warning('Cannot CSV load: {0}, error: {1}'.format(fileName, e))
            value = None
        else:
            value = [tuple(x) for x in value]
        return value

    @staticmethod
    def checkFormat(value):
        if not isinstance(value, list):
            return False
        if not all([isinstance(x, tuple) for x in value]):
            return False
        if not all([len(x) == 2 for x in value]):
            return False
        return True

    def loadBuildP(self, fileName=None, ext='.bpts'):
        """
        loadBuildP loads a modeldata pints file and stores the data in the buildP list.
        necessary conversion are made.

        :param fileName: name of file to be handled
        :param ext: load extension type
        :return: success
        """

        if fileName is None:
            return False

        value = None
        if ext == '.csv':
            value = self.loadCSV(fileName, ext)
        elif ext == '.bpts':
            value = self.loadJSON(fileName, ext)
        elif ext == '.txt':
            value = self.loadCSV(fileName, ext, delimiter=':')

        if value is None:
            return False

        suc = self.checkFormat(value)

        if not suc:
            self.clearBuildP()
            return False
        self._buildP = value

        # backup solution
        if csv:
            self.saveBuildP(fileName=fileName)
        return True

    def saveBuildP(self, fileName=None):
        """
        saveBuildP saves the actual modeldata points list in a file in json dump format

        :param fileName: name of file to be handled
        :return: success
        """

        if fileName is None:
            return False

        fileName = self.configDir + '/' + fileName + '.bpts'

        with open(fileName, 'w') as handle:
            json.dump(self.buildP,
                      handle,
                      indent=4)
        return True

    def loadHorizonP(self, fileName=None, ext='.hpts'):
        """
        loadHorizonP loads a modeldata pints file and stores the data in the buildP list.
        necessary conversion are made.

        :param fileName: name of file to be handled
        :param ext: load extension type
        :return: success
        """

        if fileName is None:
            return False

        value = None
        if ext == '.csv':
            value = self.loadCSV(fileName, ext)
        elif ext == '.hpts':
            value = self.loadJSON(fileName, ext)
        elif ext == '.txt':
            value = self.loadCSV(fileName, ext, delimiter=':')

        suc = self.checkFormat(value)

        if not suc:
            self.clearHorizonP()
            return False

        self.horizonP = value

        # backup solution
        if csv:
            self.saveHorizonP(fileName=fileName)
        return True

    @staticmethod
    def checkBoundaries(points):
        """
        checkBoundaries removes point 0,0 and 0, 360 if present.

        :param points:
        :return: points
        """

        if points[0] == (0, 0):
            del points[0]
        if points[len(points) - 1] == (0, 360):
            del points[-1]
        return points

    def saveHorizonP(self, fileName=None):
        """
        saveHorizonP saves the actual modeldata points list in a file in json dump format

        :param fileName: name of file to be handled
        :return: success
        """

        if fileName is None:
            return False
        fileName = self.configDir + '/' + fileName + '.hpts'
        points = self.checkBoundaries(self.horizonP)
        with open(fileName, 'w') as handle:
            json.dump(points,
                      handle,
                      indent=4)
        return True

    def genHaDecParams(self, selection):
        """
        genHaDecParams selects the parameters for generating the boundaries for next
        step processing greater circles. the parameters are sorted for different targets
        actually for minimum slew distance between the points. defined is only the east
        side of data, the west side will be mirrored to the east one.

        :param selection: type of model we would like to use
        :return: yield tuple of dec value and step, start and stop for range
        """

        if selection not in self.DEC or selection not in self.STEP:
            return
        eastDec = self.DEC[selection]
        westDec = list(reversed(eastDec))
        decL = eastDec + westDec

        eastStepL = self.STEP[selection]
        westStepL = list(reversed(eastStepL))
        stepL = eastStepL + westStepL
        startL = self.START[selection]
        stopL = self.STOP[selection]

        for dec, step, start, stop in zip(decL, stepL, startL, stopL):
            yield dec, step, start, stop

    def genGreaterCircle(self, selection='norm'):
        """
        genGreaterCircle takes the generated boundaries for the rang routine and
        transforms ha, dec to alt az. reasonable values for the alt az values
        are 5 to 85 degrees.

        :param selection:
        :return: yields alt, az tuples which are above horizon
        """

        if not self.app.mount.obsSite.location:
            return False

        self.clearBuildP()
        lat = self.app.mount.obsSite.location.latitude.degrees
        for dec, step, start, stop in self.genHaDecParams(selection):
            for ha in range(start, stop, step):
                alt, az = HaDecToAltAz(ha / 10, dec, lat)
                # only values with above horizon = 0

                if 5 <= alt <= 85 and 2 < az < 358:
                    alt += random.uniform(-2, 2)
                    self.addBuildP((alt, az))
        return True

    @staticmethod
    def genGridGenerator(eastAlt, westAlt, minAz, stepAz, maxAz):
        """
        genGridGenerator generates the point values out of the given ranges of altitude
        and azimuth

        :param eastAlt:
        :param westAlt:
        :param minAz:
        :param stepAz:
        :param maxAz:
        :return:
        """

        for i, alt in enumerate(eastAlt):
            if i % 2:
                for az in range(minAz, 180, stepAz):
                    yield(alt, az)
            else:
                for az in range(180 - minAz, 0, -stepAz):
                    yield(alt, az)
        for i, alt in enumerate(westAlt):
            if i % 2:
                for az in range(180 + minAz, 360, stepAz):
                    yield(alt, az)
            else:
                for az in range(maxAz, 180, -stepAz):
                    yield(alt, az)

    def genGrid(self, minAlt=5, maxAlt=85, numbRows=5, numbCols=6):
        """
        genGrid generates a grid of points and transforms ha, dec to alt az. with given
        limits in alt, the min and max will be used as a hard condition. on az there is
        not given limit, therefore a split over the whole space (omitting the meridian)
        is done. the simplest way to avoid hitting the meridian is to enforce the number
        of cols to be a factor of 2. reasonable values for the grid are 5 to 85 degrees.
        defined is only the east side of data, the west side will be mirrored to the
        east one.
            the number of rows is 2 < x < 8
            the number of columns is 2 < x < 15

        :param minAlt: altitude min
        :param maxAlt: altitude max
        :param numbRows: numbRows
        :param numbCols: numbCols
        :return: yields alt, az tuples which are above horizon
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

        self.clearBuildP()
        for point in self.genGridGenerator(eastAlt, westAlt, minAz, stepAz, maxAz):
            self.addBuildP(point)
        return True

    def genAlign(self, altBase=30, azBase=10, numberBase=3):
        """
        genAlign generates a number of initial points for the first step of modeling. it
        adjusts the first align point in a matter, that the starting point is the closest
        to az = 0.

        :param altBase:
        :param azBase:
        :param numberBase:
        :return: yields alt, az tuples which are above horizon
        """

        if not 5 <= altBase <= 85:
            return False
        if not 2 < numberBase < 11:
            return False
        if not 0 <= azBase < 360:
            return False

        stepAz = int(360 / numberBase)
        altBase = int(altBase)
        azBase = int(azBase) % stepAz
        numberBase = int(numberBase)

        self.clearBuildP()
        for i in range(0, numberBase):
            az = azBase + i * stepAz
            self.addBuildP((altBase, az % 360))
        return True

    def generateCelestialEquator(self):
        """
        generateCelestialEquator calculates a line for greater circles like a celestial
        equator for showing the paths in the hemisphere window.

        :return: celestial equator
        """

        celestialEquator = list()
        if not self.app.mount.obsSite.location:
            return celestialEquator

        lat = self.app.mount.obsSite.location.latitude.degrees
        for dec in range(-15, 90, 15):
            for ha in range(- 119, 120, 2):
                az, alt = HaDecToAltAz(ha / 10, dec, lat)
                if alt > 0:
                    celestialEquator.append((az, alt))
        for ha in range(-115, 120, 10):
            for dec in range(- 90, 90, 2):
                az, alt = HaDecToAltAz(ha / 10, dec, lat)
                if alt > 0:
                    celestialEquator.append((az, alt))
        return celestialEquator

    def generateDSOPath(self, ra=0, dec=0, timeJD=0, location=None,
                        numberPoints=0, duration=0, timeShift=0):
        """
        generateDSOPath calculates a list of model points along the desired path beginning
        at ra, dec coordinates, which is in time duration hours long and consists of
        numberPoints model points. TimeShift moves the pearl of points to an earlier or
        later point in time.

        :param ra:
        :param dec:
        :param timeJD:
        :param location:
        :param numberPoints:
        :param duration:
        :param timeShift:
        :return: True for test purpose
        """

        if numberPoints < 1:
            return False
        if duration == 0:
            return False
        if location is None:
            return False

        numberPoints = int(numberPoints)

        self.clearBuildP()
        for i in range(0, numberPoints):
            startPoint = ra.hours - i * duration / numberPoints - timeShift
            raCalc = skyfield.api.Angle(hours=startPoint)
            az, alt = transform.J2000ToAltAz(raCalc, dec, timeJD, location)
            if alt.degrees > 0:
                self.addBuildP((alt.degrees, az.degrees % 360))

        return True

    def generateGoldenSpiral(self, numberPoints):
        """
        based on the evaluations and implementation of CR Drost from 17-05-24 found at:
        https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere
        the implementation of an equally distributed points cloud over on half of the
        hemisphere.

        :param numberPoints:
        :return: true for test purpose
        """

        if numberPoints < 50:
            return False

        self.clearBuildP()

        indices = np.arange(0, numberPoints, dtype=float) + 0.5
        phi = np.arccos(1 - 2 * indices / numberPoints)
        theta = np.pi * (1 + 5 ** 0.5) * indices

        altitude = 90 - np.degrees(phi)
        azimuth = np.degrees(theta) % 360

        for alt, az in zip(altitude, azimuth):
            # only adding above horizon
            if alt > 0:
                self.addBuildP((alt, az))
        return True
