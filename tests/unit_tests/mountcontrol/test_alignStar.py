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
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest

# external packages
import skyfield.api
from skyfield.api import wgs84

# local imports
from mountcontrol.model import AlignStar
from mountcontrol import obsSite

obsSite.location = wgs84.latlon(latitude_degrees=0,
                                longitude_degrees=0,
                                elevation_m=0)


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    def test_APoint_mCoord_1(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = skyfield.api.Angle(hours=12.5)
        aPoint = AlignStar(mCoord=(p1, p2),
                           pierside='W',
                           sCoord=(p1, p2),
                           sidereal=p3,
                           )
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[1], 45, 6)
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[2], 33.01, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[1], 30, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[2], 0.5, 6)

        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[1], 45, 6)
        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[2], 33.01, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[1], 30, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[2], 0.5, 6)

    def test_APoint_mCoord_2(self):
        p1 = 12.5
        p2 = 56.5
        p3 = skyfield.api.Angle(hours=12.5)
        aPoint = AlignStar(mCoord=(p1, p2),
                           pierside='W',
                           sCoord=(p1, p2),
                           sidereal=p3,
                           )
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[1], 30, 6)
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[2], 0, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[1], 30, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[2], 0, 6)

        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[1], 30, 6)
        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[2], 0, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[1], 30, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[2], 0, 6)

    def test_APoint_mCoord_3(self):
        p3 = skyfield.api.Angle(hours=12.5)
        star = skyfield.api.Star(ra_hours=12.55, dec_degrees=56.55)
        aPoint = AlignStar(mCoord=star,
                           pierside='W',
                           sCoord=star,
                           sidereal=p3,
                           )
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[1], 33, 6)
        self.assertAlmostEqual(aPoint.mCoord.ra.hms()[2], 0, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[1], 33, 6)
        self.assertAlmostEqual(aPoint.mCoord.dec.dms()[2], 0, 6)

        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[0], 12, 6)
        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[1], 33, 6)
        self.assertAlmostEqual(aPoint.sCoord.ra.hms()[2], 0, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[0], 56, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[1], 33, 6)
        self.assertAlmostEqual(aPoint.sCoord.dec.dms()[2], 0, 6)

    def test_APoint_mCoord_4(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        aPoint = AlignStar(mCoord=(p1, p2, p3))
        self.assertEqual(None, aPoint.mCoord)

    def test_APoint_mCoord_5(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        aPoint = AlignStar(mCoord=[p1, p2, p3])
        self.assertEqual(None, aPoint.mCoord)

    def test_APoint_mCoord_6(self):
        aPoint = AlignStar(mCoord=56)
        self.assertEqual(None, aPoint.mCoord)

    def test_APoint_mCoord_7(self):
        p1 = '12:45:EE.01'
        aPoint = AlignStar(mCoord=(p1, 67))
        self.assertEqual(None, aPoint.mCoord)

    def test_APoint_sCoord_1(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        aPoint = AlignStar(sCoord=(p1, p2, p3))
        self.assertEqual(None, aPoint.sCoord)

    def test_APoint_sCoord_2(self):
        p1 = '12:45:33.01'
        p2 = '+56*30:00.5'
        p3 = '1234.5'
        aPoint = AlignStar(sCoord=[p1, p2, p3])
        self.assertEqual(None, aPoint.sCoord)

    def test_APoint_sCoord_3(self):
        aPoint = AlignStar(sCoord=56)
        self.assertEqual(None, aPoint.sCoord)

    def test_APoint_sCoord_4(self):
        p1 = '12:45:EE.01'
        aPoint = AlignStar(sCoord=(p1, 67))
        self.assertEqual(None, aPoint.sCoord)

    def test_APoint_pierside_1(self):
        aPoint = AlignStar()
        aPoint.pierside = 'E'
        self.assertEqual('E', aPoint.pierside)

    def test_APoint_pierside_2(self):
        aPoint = AlignStar()
        aPoint.pierside = 'x'
        self.assertEqual(aPoint.pierside, None)

    def test_APoint_sidereal_1(self):
        aPoint = AlignStar()
        aPoint.sidereal = 'E'
        self.assertEqual(None, aPoint.sidereal)

    def test_APoint_sidereal_2(self):
        aPoint = AlignStar()
        aPoint.sidereal = 12.5
        self.assertEqual(aPoint.sidereal.hours, 12.5)
