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
    val is None


def test_athome():
    val = app.athome()
    val is None


def test_atpark():
    val = app.atpark()
    val is None


def test_azimuth():
    val = app.azimuth()
    val is None


def test_canfindhome():
    val = app.canfindhome()
    val is None


def test_canpark():
    val = app.canpark()
    val is None


def test_cansetaltitude():
    val = app.cansetaltitude()
    val is None


def test_cansetazimuth():
    val = app.cansetazimuth()
    val is None


def test_cansetpark():
    val = app.cansetpark()
    val is None


def test_cansetshutter():
    val = app.cansetshutter()
    val is None


def test_canslave():
    val = app.canslave()
    val is None


def test_cansyncazimuth():
    val = app.cansyncazimuth()
    val is None


def test_shutterstatus():
    val = app.shutterstatus()
    val is None


def test_slaved_1():
    val = app.slaved()
    val is None


def test_slaved_2():
    val = app.slaved(Slaved=True)
    val is None


def test_slewing():
    val = app.slewing()
    val is None


def test_abortslew():
    val = app.abortslew()
    val is None


def test_closeshutter():
    val = app.closeshutter()
    val is None


def test_findhome():
    val = app.findhome()
    val is None


def test_openshutter():
    val = app.openshutter()
    val is None


def test_park():
    val = app.park()
    val is None


def test_setpark():
    val = app.setpark()
    val is None


def test_slewtoaltitude():
    val = app.slewtoaltitude(Altitude=10)
    val is None


def test_slewtoazimuth():
    val = app.slewtoazimuth(Azimuth=10)
    val is None


def test_synctoazimuth():
    val = app.synctoazimuth(Azimuth=10)
    val is None
