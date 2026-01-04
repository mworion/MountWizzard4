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

    def test_azimuth_2(self):
        tleParams = TLEParams(ObsSite())
        tleParams.azimuth = Angle(degrees=10)
        assert tleParams.azimuth.degrees == 10

    def test_altitude_2(self):
        tleParams = TLEParams(ObsSite())
        tleParams.altitude = Angle(degrees=10)
        assert tleParams.altitude.degrees == 10

    def test_ra_2(self):
        tleParams = TLEParams(ObsSite())
        tleParams.ra = Angle(hours=10)
        assert tleParams.ra.hours == 10

    def test_dec_2(self):
        tleParams = TLEParams(ObsSite())
        tleParams.dec = Angle(degrees=10)
        assert tleParams.dec.degrees == 10

    def test_flip_1(self):
        tleParams = TLEParams(ObsSite())
        tleParams.flip = True
        assert tleParams.flip

    def test_jdStart_1(self):
        tleParams = TLEParams(ObsSite())
        tleParams.jdStart = 0
        assert tleParams.jdStart.tt == 69

    def test_jdStart_2(self):
        tleParams = TLEParams(ObsSite())
        tleParams.jdStart = 100
        assert tleParams.jdStart.tt == 169

    def test_jdEnd_1(self):
        tleParams = TLEParams(ObsSite())
        tleParams.jdEnd = 0
        assert tleParams.jdEnd.tt == 69

    def test_jdEnd_2(self):
        tleParams = TLEParams(ObsSite())
        tleParams.jdEnd = 100
        assert tleParams.jdEnd.tt == 169

    def test_message_2(self):
        tleParams = TLEParams(ObsSite())
        tleParams.message = "test"
        assert tleParams.message == "test"

    def test_l0_1(self):
        tleParams = TLEParams(ObsSite())
        tleParams.l0 = "test"
        assert tleParams.l0 == "test"

    def test_l1_1(self):
        tleParams = TLEParams(ObsSite())
        tleParams.l1 = "test"
        assert tleParams.l1 == "test"

    def test_l2_1(self):
        tleParams = TLEParams(ObsSite())
        tleParams.l2 = "test"
        assert tleParams.l2 == "test"

    def test_name_1(self):
        tleParams = TLEParams(ObsSite())
        tleParams.name = "test"
        assert tleParams.name == "test"
