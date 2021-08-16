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
    val is None


def test_averageperiod_2():
    val = app.averageperiod(AveragePeriod=0)
    val is None


def test_cloudcover():
    val = app.cloudcover()
    val is None


def test_dewpoint():
    val = app.dewpoint()
    val is None


def test_humidity():
    val = app.humidity()
    val is None


def test_pressure():
    val = app.pressure()
    val is None


def test_rainrate():
    val = app.rainrate()
    val is None


def test_skybrightness():
    val = app.skybrightness()
    val is None


def test_skyquality():
    val = app.skyquality()
    val is None


def test_skytemperature():
    val = app.skytemperature()
    val is None


def test_starfwhm():
    val = app.starfwhm()
    val is None


def test_temperature():
    val = app.temperature()
    val is None


def test_winddirection():
    val = app.winddirection()
    val is None


def test_windgust():
    val = app.windgust()
    val is None


def test_windspeed():
    val = app.windspeed()
    val is None


def test_refresh():
    val = app.refresh()
    val is None


def test_sensordescription():
    val = app.sensordescription()
    val is None


def test_timesincelastupdate():
    val = app.timesincelastupdate()
    val is None
