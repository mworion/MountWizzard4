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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
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
from mw4.modeldata.alignstars import generateAlignStars


class Hipparcos(object):
    """
    The class Data inherits all information and handling of hipparcos data and other
    attributes. this includes data about the alignment stars defined in generateAlignStars,
    their ra dec coordinates, proper motion, parallax and radial velocity and the
    calculation of data for display and slew commands

        >>> hip = Hipparcos(
        >>>                 app=app
        >>>                 mwGlob=mwglob
        >>>                 )
    """

    __all__ = ['Hipparcos',
               'calculateAlignStarsPositionsAltAz',
               'getAlignStarRaDecFromIndex',
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
        self.name = list()
        self.alt = list()
        self.az = list()
        self.alignStars = generateAlignStars()
        self.calculateAlignStarPositionsAltAz()

    def calculateAlignStarPositionsAltAz(self):
        """
        calculateAlignStarPositionsAltAz does calculate the star coordinates from give data
        out of generated star list. calculation routines are from astropy erfa. atco13 does
        the results based on proper motion, parallax and radial velocity and need J2000
        coordinates. because of using the hipparcos catalogue, which is based on J1991,
        25 epoch the pre calculation from J1991,25 to J2000 is done already when generating
        the alignstars file. there is no refraction data taken into account, because we need
        this only for display purpose and for this, the accuracy is more than sufficient.

        :return: lists for alt, az and name of star
        """

        location = self.app.mount.obsSite.location
        if location is None:
            return False
        t = self.app.mount.obsSite.timeJD
        star = list(self.alignStars.values())
        self.name = list(self.alignStars.keys())

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
        self.az = aob * 360 / 2 / np.pi
        self.alt = 90.0 - zob * 360 / 2 / np.pi
        return True

    def getAlignStarRaDecFromName(self, name):
        """
        getAlignStarRaDecFromName does calculate the star coordinates from give data
        out of generated star list. calculation routines are from astropy erfa. atco13 does
        the results based on proper motion, parallax and radial velocity and need J2000
        coordinates. because of using the hipparcos catalogue, which is based on J1991,
        25 epoch the pre calculation from J1991,25 to J2000 is done already when generating
        the alignstars file. there is no refraction data taken into account, because we need
        this only for display purpose and for this, the accuracy is more than sufficient.

        the return values are in JNow epoch as the mount only handles this epoch !

        :param name: name of star
        :return: values for ra, dec in hours / degrees in JNow epoch !
        """

        if name not in self.alignStars:
            return None, None
        t = self.app.mount.obsSite.ts.now()
        values = self.alignStars[name]

        ra, dec, eo = erfa.atci13(values[0],
                                  values[1],
                                  values[2],
                                  values[3],
                                  values[4],
                                  values[5],
                                  t.ut1,
                                  0.0,
                                  )
        ra = erfa.anp(ra - eo) * 24 / 2 / np.pi
        dec = dec * 360 / 2 / np.pi

        return ra, dec
