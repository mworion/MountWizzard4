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

    def __init__(self,
                 lat=48,
                 ):

        self.lat = lat
        self._horizonFile = None
        self._pointFile = None
        self._horizon = list()
        self._point = list()

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, value):
        self._lat = value

    @property
    def horizonFile(self):
        return self._horizonFile

    @horizonFile.setter
    def horizonFile(self, value):
        self._horizonFile = value

    @property
    def pointFile(self):
        return self._pointFile

    @pointFile.setter
    def pointFile(self, value):
        self._pointFile = value

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

    def addPoint(self):
        pass

    def clearPointList(self):
        self._point = list()

    def addHorizon(self):
        pass

    def clearHorizonList(self):
        self._horizon = list()

    @staticmethod
    def genDecMin():
        decL = (-15, 0, 15, 30, 45, 60, 75,
                75, 60, 45, 30, 15, 0, -15)
        stepL = (15, -15, 15, -15, 15, -30, 30,
                 30, -30, 15, -15, 15, -15, 15)
        startL = (-120, -5, -120, -5, -120, -5, -120,
                  5, 120, 5, 120, 5, 120, 5, 120, 5,)
        stopL = (0, -120, 0, -120, 0, -120, 0,
                 120, 0, 120, 0, 120, 0, 120)

        for dec, step, start, stop in zip(decL, stepL, startL, stopL):
            yield dec, step, start, stop

    @staticmethod
    def genDecNorm():
        decL = (-15, 0, 15, 30, 45, 60, 75,
                75, 60, 45, 30, 15, 0, -15)
        stepL = (10, -10, 10, -10, 10, -20, 20,
                 20, -20, 10, -10, 10, -10, 10)
        startL = (-120, -5, -120, -5, -120, -5, -120,
                  5, 120, 5, 120, 5, 120, 5, 120, 5)
        stopL = (0, -120, 0, -120, 0, -120, 0,
                 120, 0, 120, 0, 120, 0, 120)

        for dec, step, start, stop in zip(decL, stepL, startL, stopL):
            yield dec, step, start, stop

    @staticmethod
    def genDecMax():
        decL = (-15, -5, 5, 15, 25, 35, 45, 55, 65, 75, 85,
                85, 75, 65, 55, 45, 35, 25, 15, 5, -5, -15)
        stepL = (10, -10, 10, -10, 10, -10, 10, -10, 10, -30, 30,
                 30, -30, 10, -10, 10, -10, 10, -10, 10, -10, 10)
        startL = (-120, -5, -120, -5, -120, -5, -120, -5, -120, -5, -120,
                  5, 120, 5, 120, 5, 120, 5, 120, 5, 120, 5, 120, 5, 120)
        stopL = (0, -120, 0, -120, 0, -120, 0, -120, 0, -120, 0,
                 120, 0, 120, 0, 120, 0, 120, 0, 120, 0, 120, 0)

        for dec, step, start, stop in zip(decL, stepL, startL, stopL):
            yield dec, step, start, stop

    def genGreaterCircle(self, generatorFun):
        for dec, step, start, stop in generatorFun():
            for ha in range(start, stop, step):
                alt, az = self.topoToAzAlt(ha/10, dec, self.lat)
                if alt > 0:
                    yield alt, az
