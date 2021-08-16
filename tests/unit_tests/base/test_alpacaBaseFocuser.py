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
    val is None


def test_ismoving():
    val = app.ismoving()
    val is None


def test_maxincrement():
    val = app.maxincrement()
    val is None


def test_maxstep():
    val = app.maxstep()
    val is None


def test_position():
    val = app.position()
    val is None


def test_stepsize():
    val = app.stepsize()
    val is None


def test_tempcomp_1():
    val = app.tempcomp()
    val is None


def test_tempcomp_2():
    val = app.tempcomp(TempComp=1)
    val is None


def test_tempcompavailable():
    val = app.tempcompavailable()
    val is None


def test_temperature():
    val = app.temperature()
    val is None


def test_halt():
    val = app.halt()
    val is None


def test_move_1():
    val = app.move()
    val is None


def test_move_2():
    val = app.move(Position=1)
    val is None
