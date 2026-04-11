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
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################

import unittest
from mw4.base.loggerMW import setupLogging
from mw4.mountcontrol.tleParams import TLEParams
from skyfield.api import Angle, load

setupLogging()


class ObsSite:
    UTC2TT = 69
    ts = load.timescale()


class TestConfigData(unittest.TestCase):
    def setUp(self):
        pass

    def testAzimuth(self):
        tleParams = TLEParams(ObsSite())
        tleParams.azimuth = Angle(degrees=10)
        assert tleParams.azimuth.degrees == 10

    def testAltitude(self):
        tleParams = TLEParams(ObsSite())
        tleParams.altitude = Angle(degrees=10)
        assert tleParams.altitude.degrees == 10

    def testRa(self):
        tleParams = TLEParams(ObsSite())
        tleParams.ra = Angle(hours=10)
        assert tleParams.ra.hours == 10

    def testDec(self):
        tleParams = TLEParams(ObsSite())
        tleParams.dec = Angle(degrees=10)
        assert tleParams.dec.degrees == 10

    def testFlip(self):
        tleParams = TLEParams(ObsSite())
        tleParams.flip = True
        assert tleParams.flip

    def testJdStartDefault(self):
        tleParams = TLEParams(ObsSite())
        result = tleParams.jdStart
        assert result is not None

    def testJdStartZero(self):
        tleParams = TLEParams(ObsSite())
        tleParams.jdStart = 0
        assert tleParams.jdStart.tt == 69

    def testJdStartValue(self):
        tleParams = TLEParams(ObsSite())
        tleParams.jdStart = 100
        assert tleParams.jdStart.tt == 169

    def testJdEndDefault(self):
        tleParams = TLEParams(ObsSite())
        result = tleParams.jdEnd
        assert result is not None

    def testJdEndZero(self):
        tleParams = TLEParams(ObsSite())
        tleParams.jdEnd = 0
        assert tleParams.jdEnd.tt == 69

    def testJdEndValue(self):
        tleParams = TLEParams(ObsSite())
        tleParams.jdEnd = 100
        assert tleParams.jdEnd.tt == 169

    def testMessage(self):
        tleParams = TLEParams(ObsSite())
        tleParams.message = "test"
        assert tleParams.message == "test"

    def testL0(self):
        tleParams = TLEParams(ObsSite())
        tleParams.l0 = "test"
        assert tleParams.l0 == "test"

    def testL1(self):
        tleParams = TLEParams(ObsSite())
        tleParams.l1 = "test"
        assert tleParams.l1 == "test"

    def testL2(self):
        tleParams = TLEParams(ObsSite())
        tleParams.l2 = "test"
        assert tleParams.l2 == "test"

    def testName(self):
        tleParams = TLEParams(ObsSite())
        tleParams.name = "test"
        assert tleParams.name == "test"
