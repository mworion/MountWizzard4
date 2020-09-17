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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages

# local import
from gui.extWindows.hemisphereW import HemisphereWindow
from tests.baseTestSetup import App


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    print('setup module')
    window = HemisphereWindow(app=App())
    yield window
    print('teardown module')


@pytest.fixture(autouse=True, scope='function')
def function(qtbot, module):
    print('setup function')
    yield 'function'
    print('teardown function')


def test_initConfig_1(module, function):
    print(module, function)
