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
from base.alpacaBase import Switch


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = Switch()

    yield


def test_maxswitch():
    app.maxswitch()


def test_canwrite():
    val = app.canwrite(Id=0)
    val is None


def test_getswitch():
    val = app.getswitch(Id=0)
    val is None


def test_getswitchdescription():
    val = app.getswitchdescription()
    val is None


def test_getswitchname():
    val = app.getswitchname()
    val is None


def test_getswitchvalue():
    val = app.getswitchvalue()
    val is None


def test_minswitchvalue():
    val = app.minswitchvalue()
    val is None


def test_setswitch():
    val = app.setswitch(Id=0, State=True)
    val is None


def test_setswitchname():
    val = app.setswitchname(Id=0, Name='test')
    val is None


def test_setswitchvalue():
    val = app.setswitchvalue(Id=0, Value='test')
    val is None


def test_switchstep():
    val = app.switchstep(Id=0)
    val is None
