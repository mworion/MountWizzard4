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
import sys
import unittest.mock as mock
import pytest

# external packages

# local import
from mw4 import update
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def app(qapp):
    yield


@mock.patch('sys.argv', ['python', '1', '10', '10', 'CLI'])
def test_main_1():
    with mock.patch.object(update,
                           'UpdateCLI'):
        update.main()


@mock.patch('sys.argv', ['python', '1', '10', '10', 'GUI'])
def test_main_2():
    class Test:
        @staticmethod
        def run():
            return

    with mock.patch.object(update,
                           'UpdateGUI',
                           return_value=Test()):
        update.main()
