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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock

# external packages
import pytest

# local import
from mw4.base.alpacaBase import Focuser


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Focuser()
    yield
    del app


def test_averageperiod_1():
    val = app.averageperiod()
    assert val is None


def test_averageperiod_2():
    val = app.averageperiod(AveragePeriod=1)
    assert val is None


def test_absolut():
    val = app.absolut()
    assert val is None


def test_ismoving():
    val = app.ismoving()
    assert val is None


def test_maxincrement():
    val = app.maxincrement()
    assert val is None


def test_maxstep():
    val = app.maxstep()
    assert val is None


def test_position():
    val = app.position()
    assert val is None


def test_stepsize():
    val = app.stepsize()
    assert val is None


def test_tempcomp_1():
    val = app.tempcomp()
    assert val is None


def test_tempcomp_2():
    val = app.tempcomp(TempComp=1)
    assert val is None


def test_tempcompavailable():
    val = app.tempcompavailable()
    assert val is None


def test_temperature():
    val = app.temperature()
    assert val is None


def test_halt():
    val = app.halt()
    assert val is None


def test_move_1():
    val = app.move()
    assert val is None


def test_move_2():
    val = app.move(Position=1)
    assert val is None
