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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages

# local import
from base.ethernet import checkFormatMAC


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown(qapp):
    pass


def test_checkFormatMAC_1():
    val = checkFormatMAC('')
    assert val is None


def test_checkFormatMAC_2():
    val = checkFormatMAC(1234)
    assert val is None


def test_checkFormatMAC_3():
    val = checkFormatMAC('00:00:00')
    assert val is None


def test_checkFormatMAC_4():
    val = checkFormatMAC('00:00:00:123:00:00')
    assert val is None


def test_checkFormatMAC_5():
    val = checkFormatMAC('00:00:00:12K:00:00')
    assert val is None


def test_checkFormatMAC_6():
    val = checkFormatMAC('00:00:00:12:00:00')
    assert val == '00:00:00:12:00:00'


def test_checkFormatMAC_7():
    val = checkFormatMAC('00:L0:00:12:00:00')
    assert val is None