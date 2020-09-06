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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import pytest

# local import
from base.alpacaBase import Focuser


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Focuser()

    yield


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
