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
import skyfield
# local imports


class Data(object):
    """
    The class Data inherits all information and handling of build data and other
    attributes. this includes horizon data, model points data and their persistence

        >>> fw = Data(
        >>>           lat=None
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
        decList = (-15, 0, 15, 30, 45, 60, 75)
        stepList = (15, 15, 15, 15, 15, 30, 30)
        sideList = (1, 0, 1, 0, 1, 0, 1)

        for dec, step, side in zip(decList, stepList, sideList):
            yield dec, step, side

    @staticmethod
    def genDecNorm():
        decList = (-15, 0, 15, 30, 45, 60, 75)
        stepList = (10, 10, 10, 10, 10, 20, 20)
        sideList = (1, 0, 1, 0, 1, 0, 1)

        for dec, step, side in zip(decList, stepList, sideList):
            yield dec, step, side

    @staticmethod
    def genDecMax():
        decList = (-15, -5, 5, 15, 25, 35, 45, 55, 65, 75, 85)
        stepList = (10, 10, 10, 10, 10, 10, 10, 10, 10, 30, 30)
        sideList = (1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1)

        for dec, step, side in zip(decList, stepList, sideList):
            yield dec, step, side

    @staticmethod
    def genHaDec(generatorFun):
        for dec, step, side in generatorFun():
            if side:
                for ha in range(- 125, 115, step):
                    yield ha / 10, dec
            else:
                for ha in range(115, -125, -step):
                    yield ha / 10, dec

    def convertPoint(self, generatorFun):
        for ha, dec in self.genHaDec(generatorFun):
            alt, az = self.topoToAzAlt(ha, dec, self.lat)
            if alt > 0:
                yield alt, az
