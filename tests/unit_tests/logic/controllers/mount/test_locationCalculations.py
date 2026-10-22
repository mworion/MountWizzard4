# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.controllers.mount.locationCalculations import buildLocation
from skyfield.api import Angle, wgs84


@pytest.fixture
def current():
    return wgs84.latlon(longitude_degrees=11, latitude_degrees=48, elevation_m=500)


def test_buildLocation_nothingGiven(current):
    topo, text = buildLocation(current)
    assert topo.latitude.degrees == pytest.approx(48)
    assert topo.longitude.degrees == pytest.approx(11)
    assert topo.elevation.m == pytest.approx(500)
    assert text == "Location set to:     [48.00 deg, 11.00 deg, 500.0 m]"


def test_buildLocation_lat(current):
    topo, _ = buildLocation(current, lat=Angle(degrees=10))
    assert topo.latitude.degrees == pytest.approx(10)
    assert topo.longitude.degrees == pytest.approx(11)
    assert topo.elevation.m == pytest.approx(500)


def test_buildLocation_lon(current):
    topo, _ = buildLocation(current, lon=Angle(degrees=20))
    assert topo.latitude.degrees == pytest.approx(48)
    assert topo.longitude.degrees == pytest.approx(20)


def test_buildLocation_elev(current):
    topo, text = buildLocation(current, elev=100)
    assert topo.elevation.m == pytest.approx(100)
    assert text.endswith("100.0 m]")
