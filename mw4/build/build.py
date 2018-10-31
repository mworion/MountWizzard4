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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
import numpy as np
# local imports


class Data(object):
    """
    The class Data inherits all information and handling of build data and other
    attributes. this includes horizon data, model points data and their persistence

        >>> fw = Data(
        >>>           lat=48
        >>>              )
    """

    __all__ = ['Data',
               ]
    version = '0.1'
    logger = logging.getLogger(__name__)

    # data for generating greater circles
    DEC = {'min': (-15, 0, 15, 30, 45, 60, 75,
                   75, 60, 45, 30, 15, 0, -15),
           'norm': (-15, 0, 15, 30, 45, 60, 75,
                    75, 60, 45, 30, 15, 0, -15),
           'med': (-15, -5, 5, 15, 25, 35, 45, 55, 65, 75, 85,
                   85, 75, 65, 55, 45, 35, 25, 15, 5, -5, -15),
           'max': (-15, -5, 5, 15, 25, 35, 45, 55, 65, 75, 85,
                   85, 75, 65, 55, 45, 35, 25, 15, 5, -5, -15),
           }
    STEP = {'min': (15, -15, 15, -15, 15, -30, 30,
                    30, -30, 15, -15, 15, -15, 15),
            'norm': (10, -10, 10, -10, 10, -20, 20,
                     20, -20, 10, -10, 10, -10, 10),
            'med': (10, -10, 10, -10, 10, -10, 10, -30, 30,
                    30, -30, 10, -10, 10, -10, 10, -10, 10),
            'max': (10, -10, 10, -10, 10, -10, 10, -10, 10, -30, 30,
                    30, -30, 10, -10, 10, -10, 10, -10, 10, -10, 10),
            }
    START = (-120, -5, -120, -5, -120, -5, -120, -5, -120, -5, -120,
             5, 120, 5, 120, 5, 120, 5, 120, 5, 120, 5, 120, 5, 120)
    STOP = (0, -120, 0, -120, 0, -120, 0, -120, 0, -120, 0,
            120, 0, 120, 0, 120, 0, 120, 0, 120, 0, 120, 0)

    def __init__(self,
                 lat=48,
                 ):

        self.lat = lat
        self._horizonPFile = None
        self._buildPFile = None
        self._horizonP = list()
        self._buildP = list()

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, value):
        self._lat = value

    @property
    def horizonPFile(self):
        return self._horizonPFile

    @horizonPFile.setter
    def horizonPFile(self, value):
        self._horizonPFile = value

    @property
    def buildPFile(self):
        return self._buildPFile

    @buildPFile.setter
    def buildPFile(self, value):
        self._buildPFile = value

    @staticmethod
    def topoToAzAlt(ha, dec, lat):
        ha = (ha * 360 / 24 + 360.0) % 360.0
        dec = np.radians(dec)
        ha = np.radians(ha)
        lat = np.radians(lat)
        alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
        value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
        # value = np.clip(value, -1.0, 1.0)
        A = np.arccos(value)
        if np.sin(ha) >= 0.0:
            az = 2*np.pi - A
        else:
            az = A
        az = np.degrees(az)
        alt = np.degrees(alt)
        return alt, az

    @property
    def buildP(self):
        return self._buildP

    @buildP.setter
    def buildP(self, value):
        if not isinstance(value, list):
            self._buildP = list()
            return
        if not all([isinstance(x, tuple) for x in value]):
            self.logger.error('malformed value: {0}'.format(value))
            self._buildP = list()
            return
        self._buildP = value

    def addBuildP(self):
        if not isinstance(value, list):
            self.logger.error('malformed value: {0}'.format(value))
            return
        if len(value) != 2:
            self.logger.error('malformed value: {0}'.format(value))
            return
        self._buildP.insert(len(self._buildP), value)

    def delBuildP(self):
        if not isinstance(value, (int, float)):
            self.logger.error('malformed value: {0}'.format(value))
            return
        value = int(value)
        if value < 0 or value > len(self._starList) - 1:
            self.logger.error('invalid value: {0}'.format(value))
            return
        self._buildP.pop(value)

    def clearBuildP(self):
        self._buildP = list()

    @property
    def horizonP(self):
        return self._horizonP

    @horizonP.setter
    def horizonP(self, value):
        if not isinstance(value, list):
            self._horizonP = list()
            return
        if not all([isinstance(x, tuple) for x in value]):
            self.logger.error('malformed value: {0}'.format(value))
            self._horizonP = list()
            return
        self._horizonP = value

    def addHorizonP(self):
        if not isinstance(value, list):
            self.logger.error('malformed value: {0}'.format(value))
            return
        if len(value) != 2:
            self.logger.error('malformed value: {0}'.format(value))
            return
        self._horizonP.insert(len(self._horizonP), value)

    def delHorizonP(self):
        if not isinstance(value, (int, float)):
            self.logger.error('malformed value: {0}'.format(value))
            return
        value = int(value)
        if value < 0 or value > len(self._horizonP) - 1:
            self.logger.error('invalid value: {0}'.format(value))
            return
        self._horizonP.pop(value)

    def clearHorizonP(self):
        self._horizonP = list()

    def genHaDecParams(self, selection):
        """
        genHaDecParams selects the parameters for generating the boundaries for next
        step processing greater circles. the parameters are sorted for different targets
        actually for minimum slew distance between the points.

        :param selection: type of model we would like to use
        :return: yield tuple of dec value and step, start and stop for range
        """

        if selection not in self.DEC or selection not in self.STEP:
            return
        decL = self.DEC[selection]
        stepL = self.STEP[selection]

        for dec, step, start, stop in zip(decL, stepL, self.START, self.STOP):
            yield dec, step, start, stop

    def genGreaterCircle(self, selection):
        """
        genGreaterCircle takes the generated boundaries for the rang routine and
        transforms ha, dec to alt az.

        :param selection:
        :return: yields alt, az tuples which are above horizon
        """
        for dec, step, start, stop in self.genHaDecParams(selection):
            for ha in range(start, stop, step):
                alt, az = self.topoToAzAlt(ha/10, dec, self.lat)
                # only values with above horizon = 0
                if alt > 0:
                    yield alt, az
