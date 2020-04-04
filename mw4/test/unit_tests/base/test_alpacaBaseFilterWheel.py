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
from mw4.base.alpacaBase import FilterWheel


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = FilterWheel()
    yield
    del app


def test_focusoffsets():
    val = app.focusoffsets()
    assert val is None


def test_names():
    val = app.names()
    assert val is None


def test_position_1():
    val = app.position()
    assert val is None


def test_position_2():
    val = app.position(Position=0)
    assert val is None
