############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest

from mw4.base.loggerMW import setupLogging

# local imports
from mw4.mountcontrol.tleParams import TLEParams

# external packages
from skyfield.api import Angle, load

setupLogging()


class TestConfigData(unittest.TestCase):
    def setUp(self):
        pass

    def test_azimuth_1(self):
        tleParams = TLEParams()
        tleParams.azimuth = 10
        assert tleParams.azimuth.degrees == 10

    def test_azimuth_2(self):
        tleParams = TLEParams()
        tleParams.azimuth = Angle(degrees=10)
        assert tleParams.azimuth.degrees == 10

    def test_altitude_1(self):
        tleParams = TLEParams()
        tleParams.altitude = 10
        assert tleParams.altitude.degrees == 10

    def test_altitude_2(self):
        tleParams = TLEParams()
        tleParams.altitude = Angle(degrees=10)
        assert tleParams.altitude.degrees == 10

    def test_ra_1(self):
        tleParams = TLEParams()
        tleParams.ra = 10
        assert tleParams.ra.hours == 10

    def test_ra_2(self):
        tleParams = TLEParams()
        tleParams.ra = Angle(hours=10)
        assert tleParams.ra.hours == 10

    def test_dec_1(self):
        tleParams = TLEParams()
        tleParams.dec = 10
        assert tleParams.dec.degrees == 10

    def test_dec_2(self):
        tleParams = TLEParams()
        tleParams.dec = Angle(degrees=10)
        assert tleParams.dec.degrees == 10

    def test_flip_1(self):
        tleParams = TLEParams()
        tleParams.flip = True
        assert tleParams.flip

    def test_flip_2(self):
        tleParams = TLEParams()
        tleParams.flip = "F"
        assert tleParams.flip

    def test_jdStart_1(self):
        tleParams = TLEParams()
        tleParams.jdStart = None
        assert tleParams.jdStart is None

    def test_jdStart_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        tleParams = TLEParams(obsSite=ObsSite())
        tleParams.jdStart = "100"
        assert tleParams.jdStart.tt == 169

    def test_jdEnd_1(self):
        tleParams = TLEParams()
        tleParams.jdEnd = None
        assert tleParams.jdEnd is None

    def test_jdEnd_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        tleParams = TLEParams(obsSite=ObsSite())
        tleParams.jdEnd = "100"
        assert tleParams.jdEnd.tt == 169

    def test_message_1(self):
        tleParams = TLEParams()
        tleParams.message = None
        assert tleParams.message is None

    def test_message_2(self):
        tleParams = TLEParams()
        tleParams.message = "test"
        assert tleParams.message == "test"

    def test_l0_1(self):
        tleParams = TLEParams()
        tleParams.l0 = "test"
        assert tleParams.l0 == "test"

    def test_l1_1(self):
        tleParams = TLEParams()
        tleParams.l1 = "test"
        assert tleParams.l1 == "test"

    def test_l2_1(self):
        tleParams = TLEParams()
        tleParams.l2 = "test"
        assert tleParams.l2 == "test"

    def test_name_1(self):
        tleParams = TLEParams()
        tleParams.name = "test"
        assert tleParams.name == "test"
