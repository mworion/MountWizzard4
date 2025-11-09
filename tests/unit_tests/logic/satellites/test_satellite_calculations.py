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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock

# external packages
import numpy as np
import pytest
from skyfield.api import Angle, EarthSatellite, wgs84
from skyfield.timelib import Time

import mw4.logic
from mw4.logic.satellites.satellite_calculations import (
    addMeridianTransit,
    calcAppMag,
    calcPassEvents,
    calcSatelliteMeridianTransit,
    calcSatPasses,
    calcSatSunPhase,
    checkTwilight,
    collectAllOrbits,
    extractCorrectOrbits,
    findRangeRate,
    findSatUp,
    findSunlit,
    sortFlipEvents,
)

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="function")
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
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    loc = wgs84.latlon(latitude_degrees=49, longitude_degrees=-11)
    tEv = function.mount.obsSite.ts.tt_jd(2459215.5)
    val = findRangeRate(sat, loc, tEv)
    assert round(val[0], 3) == 5694.271
    assert round(val[1], 3) == -0.678
    assert round(val[2], 3) == 0.004
    assert round(val[3], 3) == 0.079


def test_calcSatSunPhase_1(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    loc = wgs84.latlon(latitude_degrees=49, longitude_degrees=-11)
    ephemeris = function.ephemeris
    tEv = function.mount.obsSite.ts.tt_jd(2459215.5)
    val = calcSatSunPhase(sat, loc, ephemeris, tEv)
    assert round(val.degrees, 3) == 129.843


def test_calcAppMag_1(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    loc = wgs84.latlon(latitude_degrees=49, longitude_degrees=-11)
    ephemeris = function.ephemeris
    satRange = 483
    phase = Angle(degrees=113)
    tEv = function.mount.obsSite.ts.now()
    with mock.patch.object(
        mw4.logic.satellites.satellite_calculations, "calcSatSunPhase", return_value=phase
    ):
        val = calcAppMag(sat, loc, ephemeris, satRange, tEv)
        assert round(val, 4) == -2.0456


def test_calcSatelliteMeridianTransit(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]

    satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    loc = wgs84.latlon(latitude_degrees=48, longitude_degrees=11, elevation_m=500)
    calcSatelliteMeridianTransit(satellite, loc, 0)


def test_calcPassEvents_1(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]

    satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    obsSite = function.mount.obsSite
    t, e = calcPassEvents(satellite, obsSite, None)
    assert isinstance(t, Time)
    assert isinstance(e, np.ndarray)


def test_calcPassEvents_2(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]

    satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    obsSite = function.mount.obsSite
    t, e = calcPassEvents(satellite, obsSite, 1)
    assert isinstance(t, Time)
    assert isinstance(e, np.ndarray)


def test_collectAllOrbits_1(function):
    ts = function.mount.obsSite.ts

    now = ts.tt_jd(2459215.4)
    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)
    t2 = ts.tt_jd(2459215.7)
    t3 = ts.tt_jd(2459215.8)
    t4 = ts.tt_jd(2459215.9)
    t5 = ts.tt_jd(2459216.0)
    t6 = ts.tt_jd(2459216.1)
    t7 = ts.tt_jd(2459216.2)
    t8 = ts.tt_jd(2459216.3)

    times = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
    events = [0, 1, 2, 0, 1, 2, 0, 1, 2]
    with mock.patch.object(function.mount.obsSite.ts, "now", return_value=now):
        satOrbits = collectAllOrbits(times, events, function.mount.obsSite)
        assert len(satOrbits) == 3


def test_collectAllOrbits_2(function):
    ts = function.mount.obsSite.ts

    now = ts.tt_jd(2459215.4)
    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)
    t2 = ts.tt_jd(2459215.7)
    t3 = ts.tt_jd(2459215.8)
    t4 = ts.tt_jd(2459215.9)
    t5 = ts.tt_jd(2459216.0)
    t6 = ts.tt_jd(2459216.1)
    t7 = ts.tt_jd(2459216.2)
    t8 = ts.tt_jd(2459216.3)

    times = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
    events = [0, 1, 2, 2, 1, 1, 0, 1, 1]
    with mock.patch.object(function.mount.obsSite.ts, "now", return_value=now):
        satOrbits = collectAllOrbits(times, events, function.mount.obsSite)
        assert len(satOrbits) == 2


def test_collectAllOrbits_3(function):
    ts = function.mount.obsSite.ts

    now = ts.tt_jd(2459216.1)
    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)
    t2 = ts.tt_jd(2459215.7)
    t3 = ts.tt_jd(2459215.8)
    t4 = ts.tt_jd(2459215.9)
    t5 = ts.tt_jd(2459216.0)
    t6 = ts.tt_jd(2459216.1)
    t7 = ts.tt_jd(2459216.2)
    t8 = ts.tt_jd(2459216.3)

    times = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
    events = [0, 1, 2, 0, 1, 2, 0, 1, 2]

    with mock.patch.object(function.mount.obsSite.ts, "now", return_value=now):
        satOrbits = collectAllOrbits(times, events, function.mount.obsSite)
        assert len(satOrbits) == 1


def test_collectAllOrbits_4(function):
    ts = function.mount.obsSite.ts

    now = ts.tt_jd(2459217.1)
    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)
    t2 = ts.tt_jd(2459215.7)
    t3 = ts.tt_jd(2459215.8)
    t4 = ts.tt_jd(2459215.9)
    t5 = ts.tt_jd(2459216.0)
    t6 = ts.tt_jd(2459216.1)
    t7 = ts.tt_jd(2459216.2)
    t8 = ts.tt_jd(2459216.3)

    times = [t0, t1, t2, t3, t4, t5, t6, t7, t8]
    events = [0, 1, 2, 0, 1, 2, 0, 1, 2]

    satOrbits = collectAllOrbits(times, events, now)
    assert len(satOrbits) == 0


def test_extractCorrectOrbits_1(function):
    ts = function.mount.obsSite.ts
    t0 = ts.tt_jd(2459215.5)

    times = np.array([t0])
    events = np.array([1])

    satOrbits = collectAllOrbits(times, events, function.mount.obsSite)
    print(satOrbits)
    satOrbits = extractCorrectOrbits(times, events, satOrbits)
    print(satOrbits)
    assert len(satOrbits) == 1


def test_extractCorrectOrbits_2(function):
    ts = function.mount.obsSite.ts

    t0 = ts.tt_jd(2459215.5)
    t1 = ts.tt_jd(2459215.6)

    times = [t0, t1]
    events = [0, 1]
    satOrbits = collectAllOrbits(times, events, function.mount.obsSite)

    print(satOrbits)
    satOrbits = extractCorrectOrbits(times, events, satOrbits)
    print(satOrbits)
    assert len(satOrbits) == 0


def test_sortFlipEvents_0(function):
    ts = function.mount.obsSite.ts
    satOrbit = {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)}
    t0 = []
    t1 = [ts.tt_jd(2459215.5)]
    t2 = [ts.tt_jd(2459215.6)]
    satOrbit = sortFlipEvents(satOrbit, t0, t1, t2)
    assert "flip" not in satOrbit


def test_sortFlipEvents_1(function):
    ts = function.mount.obsSite.ts
    satOrbit = {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = [ts.tt_jd(2459215.5)]
    t2 = [ts.tt_jd(2459215.6)]
    satOrbit = sortFlipEvents(satOrbit, t0, t1, t2)
    assert "flip" in satOrbit


def test_sortFlipEvents_2(function):
    ts = function.mount.obsSite.ts
    satOrbit = {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = [ts.tt_jd(2459215.6)]
    t2 = [ts.tt_jd(2459215.5)]
    satOrbit = sortFlipEvents(satOrbit, t0, t1, t2)


def test_sortFlipEvents_3(function):
    ts = function.mount.obsSite.ts
    satOrbit = {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = [ts.tt_jd(2459215.65)]
    t2 = []
    satOrbit = sortFlipEvents(satOrbit, t0, t1, t2)
    assert "flipLate" in satOrbit


def test_sortFlipEvents_4(function):
    ts = function.mount.obsSite.ts
    satOrbit = {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = [ts.tt_jd(2459215.55)]
    t2 = []
    satOrbit = sortFlipEvents(satOrbit, t0, t1, t2)
    assert "flipEarly" in satOrbit


def test_sortFlipEvents_5(function):
    ts = function.mount.obsSite.ts
    satOrbit = {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = []
    t2 = [ts.tt_jd(2459215.55)]
    satOrbit = sortFlipEvents(satOrbit, t0, t1, t2)
    assert "flipEarly" in satOrbit


def test_sortFlipEvents_6(function):
    ts = function.mount.obsSite.ts
    satOrbit = {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)}
    t0 = [ts.tt_jd(2459215.5)]
    t1 = []
    t2 = [ts.tt_jd(2459215.65)]
    satOrbit = sortFlipEvents(satOrbit, t0, t1, t2)
    assert "flipLate" in satOrbit


def test_addMeridianTransit_1(function):
    location = wgs84.latlon(latitude_degrees=48, longitude_degrees=11, elevation_m=500)
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    ts = function.mount.obsSite.ts
    setting = function.mount.setting
    satellite = EarthSatellite(tle[1], tle[2], name=tle[0])

    satOrbits = [
        {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)},
        {"rise": ts.tt_jd(2459216.5), "settle": ts.tt_jd(2459216.7)},
    ]
    addMeridianTransit(satellite, satOrbits, location, setting)


def test_addMeridianTransit_2(function):
    location = wgs84.latlon(latitude_degrees=48, longitude_degrees=11, elevation_m=500)
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    ts = function.mount.obsSite.ts
    setting = function.mount.setting
    function.mount.setting.meridianLimitTrack = None
    satellite = EarthSatellite(tle[1], tle[2], name=tle[0])

    satOrbits = [
        {"rise": ts.tt_jd(2459215.5), "settle": ts.tt_jd(2459215.7)},
        {"rise": ts.tt_jd(2459216.5), "settle": ts.tt_jd(2459216.7)},
    ]
    addMeridianTransit(satellite, satOrbits, location, setting)


def test_calcSatPasses_1(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]

    satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    obsSite = function.mount.obsSite
    setting = function.mount.setting
    with mock.patch.object(
        mw4.logic.satellites.satellite_calculations, "calcPassEvents", return_value=(1, 1)
    ):
        with mock.patch.object(
            mw4.logic.satellites.satellite_calculations, "collectAllOrbits", return_value=[]
        ):
            with mock.patch.object(
                mw4.logic.satellites.satellite_calculations,
                "extractCorrectOrbits",
                return_value=[],
            ):
                with mock.patch.object(
                    mw4.logic.satellites.satellite_calculations,
                    "addMeridianTransit",
                    return_value=[],
                ):
                    calcSatPasses(satellite, obsSite, setting)
