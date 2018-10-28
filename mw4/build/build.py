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


def topoToAzAlt(ra, dec, lat):
    alt = np.arcsin(np.sin(dec)*np.sin(lat) + np.cos(dec)*np.cos(lat)*np.cos(ra))
    value = (np.sin(dec) - np.sin(alt)*np.sin(lat))/(np.cos(alt)*np.cos(lat))
    value = np.clip(value, -1.0, 1.0)
    A = np.arccos(value)
    if np.sin(ra) >= 0.0:
        az = np.pi - A
    else:
        az = A
    return az, alt


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
                 lat=None,
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
