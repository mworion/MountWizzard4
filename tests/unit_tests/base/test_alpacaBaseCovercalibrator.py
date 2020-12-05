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
# written in python3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import pytest

# local import
from base.alpacaBase import Covercalibrator


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Covercalibrator()

    yield


def test_brightness():
    val = app.brightness()
    assert val is None


def test_calibratoroff():
    app.calibratoroff()


def test_calibratoron_1():
    val = app.calibratoron()
    assert val is None


def test_calibratoron_2():
    val = app.calibratoron(Brightness=1)
    assert val is None


def test_calibratorstate():
    val = app.calibratorstate()
    assert val is None


def test_closecover():
    app.closecover()


def test_opencover():
    app.opencover()


def test_haltcover():
    app.haltcover()


def test_coverstate():
    val = app.coverstate()
    assert val is None


def test_maxbrightness():
    val = app.maxbrightness()
    assert val is None

