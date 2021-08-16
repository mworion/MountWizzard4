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
from base.alpacaBase import Dome


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Dome()

    yield


def test_altitude():
    val = app.altitude()
    assert val == []


def test_athome():
    val = app.athome()
    assert val == []


def test_atpark():
    val = app.atpark()
    assert val == []


def test_azimuth():
    val = app.azimuth()
    assert val == []


def test_canfindhome():
    val = app.canfindhome()
    assert val == []


def test_canpark():
    val = app.canpark()
    assert val == []


def test_cansetaltitude():
    val = app.cansetaltitude()
    assert val == []


def test_cansetazimuth():
    val = app.cansetazimuth()
    assert val == []


def test_cansetpark():
    val = app.cansetpark()
    assert val == []


def test_cansetshutter():
    val = app.cansetshutter()
    assert val == []


def test_canslave():
    val = app.canslave()
    assert val == []


def test_cansyncazimuth():
    val = app.cansyncazimuth()
    assert val == []


def test_shutterstatus():
    val = app.shutterstatus()
    assert val == []


def test_slaved_1():
    val = app.slaved()
    assert val == []


def test_slaved_2():
    val = app.slaved(Slaved=True)
    assert val == []


def test_slewing():
    val = app.slewing()
    assert val == []


def test_abortslew():
    val = app.abortslew()
    assert val == []


def test_closeshutter():
    val = app.closeshutter()
    assert val == []


def test_findhome():
    val = app.findhome()
    assert val == []


def test_openshutter():
    val = app.openshutter()
    assert val == []


def test_park():
    val = app.park()
    assert val == []


def test_setpark():
    val = app.setpark()
    assert val == []


def test_slewtoaltitude():
    val = app.slewtoaltitude(Altitude=10)
    assert val == []


def test_slewtoazimuth():
    val = app.slewtoazimuth(Azimuth=10)
    assert val == []


def test_synctoazimuth():
    val = app.synctoazimuth(Azimuth=10)
    assert val == []
