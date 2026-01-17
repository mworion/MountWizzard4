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

import pytest
from mw4.mountcontrol.model import ModelStar
from skyfield.api import Angle, Star, wgs84
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    app = App()
    modelStar = ModelStar()
    yield modelStar


def test_properties_4(function):
    function.coord = Star(ra_hours=12.5, dec_degrees=30.5)
    assert function.coord.dec.degrees == 30.5
    assert function.coord.ra.hours == 12.5


def test_properties_5(function):
    function.number = 12.0
    assert function.number == 12
    function.errorRMS = 12.0
    assert function.errorRMS == 12


def test_properties_6(function):
    function.alt = Angle(degrees=12.0)
    assert function.alt.degrees == 12
    function.az = Angle(degrees=12.0)
    assert function.az.degrees == 12


def test_properties_7(function):
    function.errorAngle = Angle(degrees=12.0)
    assert function.errorAngle.degrees == 12
    function.errorAngle = Angle(degrees=12)
    assert function.errorAngle.degrees == 12


def test_properties_8(function):
    function.errorAngle = Angle(degrees=90)
    function.errorRMS = 1
    assert round(function.errorRA().degrees, 2) == 1
    assert round(function.errorDEC().degrees, 2) == 0
    function.errorAngle = Angle(degrees=180)
    function.errorRMS = 1
    assert round(function.errorRA().degrees, 2) == 0
    assert round(function.errorDEC().degrees, 2) == -1
