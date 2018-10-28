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
                 lat=0,
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
    def topoToAzAlt(star, lat):
        if not isinstance(star, skyfield.starlib.Star):
            return None, None
        ra = star.ra.hours
        dec = star.dec.degrees
        alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ra))
        value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
        value = np.clip(value, -1.0, 1.0)
        A = np.arccos(value)
        if np.sin(ra) >= 0.0:
            az = np.pi - A
        else:
            az = A
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
    def genHaDec(generator):
        # first direction
        for dec, step, side in generator():
            for ha in range(115, -125, -step):
                if side:
                    yield ha, dec
        # reverse direction
        for dec, step, side in generator():
            for ha in range(- 125, 115, step):
                if not side:
                    yield ha, dec

    def genMinPoints(self):
        pass
