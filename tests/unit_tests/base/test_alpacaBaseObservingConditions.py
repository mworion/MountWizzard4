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
# written in python3, (c) 2019-2021 by mworion
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
    assert val == []


def test_averageperiod_2():
    val = app.averageperiod(AveragePeriod=0)
    assert val == []


def test_cloudcover():
    val = app.cloudcover()
    assert val == []


def test_dewpoint():
    val = app.dewpoint()
    assert val == []


def test_humidity():
    val = app.humidity()
    assert val == []


def test_pressure():
    val = app.pressure()
    assert val == []


def test_rainrate():
    val = app.rainrate()
    assert val == []


def test_skybrightness():
    val = app.skybrightness()
    assert val == []


def test_skyquality():
    val = app.skyquality()
    assert val == []


def test_skytemperature():
    val = app.skytemperature()
    assert val == []


def test_starfwhm():
    val = app.starfwhm()
    assert val == []


def test_temperature():
    val = app.temperature()
    assert val == []


def test_winddirection():
    val = app.winddirection()
    assert val == []


def test_windgust():
    val = app.windgust()
    assert val == []


def test_windspeed():
    val = app.windspeed()
    assert val == []


def test_refresh():
    val = app.refresh()
    assert val == []


def test_sensordescription():
    val = app.sensordescription()
    assert val == []


def test_timesincelastupdate():
    val = app.timesincelastupdate()
    assert val == []
