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
    val is None


def test_calibratoroff():
    app.calibratoroff()


def test_calibratoron_1():
    val = app.calibratoron()
    val is None


def test_calibratoron_2():
    val = app.calibratoron(Brightness=1)
    val is None


def test_calibratorstate():
    val = app.calibratorstate()
    val is None


def test_closecover():
    app.closecover()


def test_opencover():
    app.opencover()


def test_haltcover():
    app.haltcover()


def test_coverstate():
    val = app.coverstate()
    val is None


def test_maxbrightness():
    val = app.maxbrightness()
    val is None

