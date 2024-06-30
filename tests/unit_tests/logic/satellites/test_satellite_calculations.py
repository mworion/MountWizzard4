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
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import astropy
from unittest import mock

# external packages
import numpy as np
from skyfield.api import EarthSatellite, Angle, wgs84

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import logic
from logic.satellites.satellite_calculations import findSunlit, findSatUp
from logic.satellites.satellite_calculations import checkTwilight, calcSatSunPhase
from logic.satellites.satellite_calculations import findRangeRate, calcAppMag


@pytest.fixture(autouse=True, scope='function')
def function():
    yield App()


def test_findSunlit(function):
    class SAT:
        class FRAME:
            def __init__(self, x):
                pass

            @staticmethod
            def is_sunlit(x):
                return True

        at = FRAME

    sat = SAT()
    eph = None
    tEv = None
    val = findSunlit(sat, eph, tEv)
    assert val


def test_findSatUp_1(function):
    class SAT:
        @staticmethod
        def find_events(x, y, z, altitude_degrees):
            return [], []

    sat = SAT()
    val = findSatUp(sat, 0, 0, 0, alt=0)
    assert not val[0]
    assert not len(val[1])


def test_findSatUp_2(function):
    class SAT:
        @staticmethod
        def find_events(x, y, z, altitude_degrees):
            return np.array([5, 7, 7]), np.array([1, 0, 0])

    sat = SAT()
    val = findSatUp(sat, 0, 0, 0, alt=0)
    assert val[0]
    assert val[1] == [5]


def test_checkTwilight_1(function):
    ephemeris = function.ephemeris
    loc = wgs84.latlon(latitude_degrees=49, longitude_degrees=-11)
    tEv = function.mount.obsSite.ts.tt_jd(2459215.5)
    val = checkTwilight(ephemeris, loc, [False, tEv])
    assert val == 4


def test_checkTwilight_2(function):
    ephemeris = function.ephemeris
    loc = wgs84.latlon(latitude_degrees=49, longitude_degrees=-11)
    tEv = function.mount.obsSite.ts.tt_jd(2459215.5)
    val = checkTwilight(ephemeris, loc, [True, [tEv]])
    assert val == 0


def test_findRangeRate(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    loc = wgs84.latlon(latitude_degrees=49, longitude_degrees=-11)
    tEv = function.mount.obsSite.ts.tt_jd(2459215.5)
    val = findRangeRate(sat, loc, tEv)
    assert round(val[0], 3) == 5694.271
    assert round(val[1], 3) == -0.678
    assert round(val[2], 3) == 0.004
    assert round(val[3], 3) == 0.079


def test_calcSatSunPhase_1(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    loc = wgs84.latlon(latitude_degrees=49, longitude_degrees=-11)
    ephemeris = function.ephemeris
    tEv = function.mount.obsSite.ts.tt_jd(2459215.5)
    val = calcSatSunPhase(sat, loc, ephemeris, tEv)
    assert round(val.degrees, 3) == 129.843


def test_calcAppMag_1(function):
    tle = ["NOAA 8",
           "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
           "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954"]
    sat = EarthSatellite(tle[1], tle[2],  name=tle[0])
    loc = wgs84.latlon(latitude_degrees=49, longitude_degrees=-11)
    ephemeris = function.ephemeris
    satRange = 483
    phase = Angle(degrees=113)
    tEv = function.mount.obsSite.ts.now()
    with mock.patch.object(logic.satellites.satellite_calculations,
                           'calcSatSunPhase',
                           return_value=phase):
        val = calcAppMag(sat, loc, ephemeris, satRange, tEv)
        assert round(val, 4) == -2.0456
