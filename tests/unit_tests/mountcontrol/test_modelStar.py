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
import pytest
from mw4.mountcontrol import obsSite

# local imports
from mw4.mountcontrol.model import ModelStar

# external packages
from skyfield.api import Angle, Star, wgs84


@pytest.fixture(autouse=True, scope="function")
def function():
    obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)

    modelStar = ModelStar(obsSite=obsSite)
    yield modelStar


def test_properties_1(function):
    function.coord = ("12:30:00.00", "+30*30:00.0", "+30*30:00.0")
    assert function.coord is None
    assert function.coord is None


def test_properties_2(function):
    function.coord = ("EE", "EE")
    assert function.coord is None
    assert function.coord is None


def test_properties_3(function):
    function.coord = ("12:30:00.00", "+30*30:00.0")
    assert function.coord.dec.degrees == 30.5
    assert function.coord.ra.hours == 12.5
    assert round(function.az.degrees, 2) == 12.49
    assert round(function.alt.degrees, 2) == -58.68


def test_properties_4(function):
    function.coord = Star(ra_hours=12.5, dec_degrees=30.5)
    assert function.coord.dec.degrees == 30.5
    assert function.coord.ra.hours == 12.5
    assert round(function.az.degrees, 2) == 12.49
    assert round(function.alt.degrees, 2) == -58.68


def test_properties_4b(function):
    function.obsSite = None
    function.coord = Star(ra_hours=12.5, dec_degrees=30.5)


def test_properties_4c(function):
    function.obsSite.location = None
    function.coord = Star(ra_hours=12.5, dec_degrees=30.5)


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


def test_properties_9(function):
    function.errorAngle = None
    function.errorRMS = None
    assert function.errorRA() is None
    assert function.errorDEC() is None


def test_compare_1():
    star1 = ModelStar()
    star2 = ModelStar()
    star1.errorRMS = 1
    star2.errorRMS = 2
    assert star1 < star2
    assert star1 <= star2
    assert not star2 < star1
    assert not star2 <= star1


def test_compare_2():
    star1 = ModelStar()
    star2 = ModelStar()
    star1.errorRMS = 2
    star2.errorRMS = 1
    assert star1 > star2
    assert star1 >= star2
    assert not star2 > star1
    assert not star2 >= star1


def test_compare_3():
    star1 = ModelStar()
    star2 = ModelStar()
    star1.errorRMS = 1
    star2.errorRMS = 1
    assert star1 == star2


def test_compare_4():
    star1 = ModelStar()
    star2 = ModelStar()
    star1.errorRMS = 1
    star2.errorRMS = 2
    assert not star1 == star2
