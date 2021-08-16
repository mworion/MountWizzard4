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
from base.alpacaBase import FilterWheel


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = FilterWheel()

    yield


def test_focusoffsets():
    val = app.focusoffsets()
    val is None


def test_names():
    val = app.names()
    val is None


def test_position_1():
    val = app.position()
    val is None


def test_position_2():
    val = app.position(Position=0)
    val is None
