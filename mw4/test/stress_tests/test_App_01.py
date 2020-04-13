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
import sys
import unittest.mock as mock
import faulthandler

# external packages
import pytest

# local import
from mw4 import loader


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():

    testArgv = ['run', 'test']
    faulthandler.enable()

    with mock.patch.object(sys,
                           'argv',
                           testArgv):
        with mock.patch.object(sys,
                               'exit'):
            loader.main()

        yield


def test_1():
    pass


def test_2():
    pass


def test_3():
    pass


def test_4():
    pass


def test_5():
    pass

