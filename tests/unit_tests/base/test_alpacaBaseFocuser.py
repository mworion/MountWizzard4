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
from base.alpacaBase import Focuser


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Focuser()

    yield


def test_absolut():
    val = app.absolut()
    assert val == []


def test_ismoving():
    val = app.ismoving()
    assert val == []


def test_maxincrement():
    val = app.maxincrement()
    assert val == []


def test_maxstep():
    val = app.maxstep()
    assert val == []


def test_position():
    val = app.position()
    assert val == []


def test_stepsize():
    val = app.stepsize()
    assert val == []


def test_tempcomp_1():
    val = app.tempcomp()
    assert val == []


def test_tempcomp_2():
    val = app.tempcomp(TempComp=1)
    assert val == []


def test_tempcompavailable():
    val = app.tempcompavailable()
    assert val == []


def test_temperature():
    val = app.temperature()
    assert val == []


def test_halt():
    val = app.halt()
    assert val == []


def test_move_1():
    val = app.move()
    assert val == []


def test_move_2():
    val = app.move(Position=1)
    assert val == []
