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
from mw4.base.alpacaBase import Dome


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Dome()


def test_altitude():
    val = app.altitude()
    assert val is None


def test_athome():
    val = app.athome()
    assert val is None


def test_atpark():
    val = app.atpark()
    assert val is None


def test_azimuth():
    val = app.azimuth()
    assert val is None


def test_canfindhome():
    val = app.canfindhome()
    assert val is None


def test_canpark():
    val = app.canpark()
    assert val is None


def test_cansetaltitude():
    val = app.cansetaltitude()
    assert val is None


def test_cansetazimuth():
    val = app.cansetazimuth()
    assert val is None


def test_cansetpark():
    val = app.cansetpark()
    assert val is None


def test_cansetshutter():
    val = app.cansetshutter()
    assert val is None


def test_canslave():
    val = app.canslave()
    assert val is None


def test_cansyncazimuth():
    val = app.cansyncazimuth()
    assert val is None


def test_shutterstatus():
    val = app.shutterstatus()
    assert val is None


def test_slaved_1():
    val = app.slaved()
    assert val is None


def test_slaved_2():
    val = app.slaved(Slaved=True)
    assert val is None


def test_slewing():
    val = app.slewing()
    assert val is None


def test_abortslew():
    val = app.abortslew()
    assert val is None


def test_closeshutter():
    val = app.closeshutter()
    assert val is None


def test_findhome():
    val = app.findhome()
    assert val is None


def test_openshutter():
    val = app.openshutter()
    assert val is None


def test_park():
    val = app.park()
    assert val is None


def test_setpark():
    val = app.setpark()
    assert val is None


def test_slewtoaltitude():
    val = app.slewtoaltitude(Altitude=10)
    assert val is None


def test_slewtoazimuth():
    val = app.slewtoazimuth(Azimuth=10)
    assert val is None


def test_synctoazimuth():
    val = app.synctoazimuth(Azimuth=10)
    assert val is None
