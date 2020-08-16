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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import pytest

# local import
from base.alpacaBase import ObservingConditions


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = ObservingConditions()

    yield


def test_averageperiod_1():
    val = app.averageperiod()
    assert val is None


def test_averageperiod_2():
    val = app.averageperiod(AveragePeriod=0)
    assert val is None


def test_cloudcover():
    val = app.cloudcover()
    assert val is None


def test_dewpoint():
    val = app.dewpoint()
    assert val is None


def test_humidity():
    val = app.humidity()
    assert val is None


def test_pressure():
    val = app.pressure()
    assert val is None


def test_rainrate():
    val = app.rainrate()
    assert val is None


def test_skybrightness():
    val = app.skybrightness()
    assert val is None


def test_skyquality():
    val = app.skyquality()
    assert val is None


def test_skytemperature():
    val = app.skytemperature()
    assert val is None


def test_starfwhm():
    val = app.starfwhm()
    assert val is None


def test_temperature():
    val = app.temperature()
    assert val is None


def test_winddirection():
    val = app.winddirection()
    assert val is None


def test_windgust():
    val = app.windgust()
    assert val is None


def test_windspeed():
    val = app.windspeed()
    assert val is None


def test_refresh():
    val = app.refresh()
    assert val is None


def test_sensordescription():
    val = app.sensordescription()
    assert val is None


def test_timesincelastupdate():
    val = app.timesincelastupdate()
    assert val is None
