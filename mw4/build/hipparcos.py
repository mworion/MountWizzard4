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
# Python  v3.6.7
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
import astropy._erfa as erfa
# local imports
from mw4.build.alignstars import generateAlignStars


class Hipparcos(object):
    """
    The class Data inherits all information and handling of build data and other
    attributes. this includes horizon data, model points data and their persistence

        >>> hip = Hipparcos(
        >>>                 app=app
        >>>                 mwGlob=mwglob
        >>>                 )
    """

    __all__ = ['Hipparcos',
               ]
    version = '0.2'
    logger = logging.getLogger(__name__)

    def __init__(self,
                 app=None,
                 mwGlob=None,
                 ):

        self.app = app
        self.mwGlob = mwGlob
        self.lat = app.mount.obsSite.location.latitude.degrees
        self.alignStars = generateAlignStars()
        self.calculateAlignStarPositions()

    def calculateAlignStarPositions(self):
        """
        calculateAlignStarPositions does from actual observer position the star coordinates
        in alt, az for the given align stars

        :return: list for alt, az and hipNo
        """

        location = self.app.mount.obsSite.location
        t = self.app.mount.obsSite.ts.now()
        star = list(self.alignStars.values())
        name = list(self.alignStars.keys())

        aob, zob, hob, dob, rob, eo = erfa.atco13([x[0] for x in star],
                                                  [x[1] for x in star],
                                                  [x[2] for x in star],
                                                  [x[3] for x in star],
                                                  [x[4] for x in star],
                                                  [x[5] for x in star],
                                                  t.ut1,
                                                  0.0,
                                                  t.dut1,
                                                  location.longitude.radians,
                                                  location.latitude.radians,
                                                  location.elevation.m,
                                                  0.0,
                                                  0.0,
                                                  0.0,
                                                  0.0,
                                                  0.0,
                                                  0.0)
        az = aob * 360 / 2 / np.pi
        alt = 90.0 - zob * 360 / 2 / np.pi

        return alt, az, name
