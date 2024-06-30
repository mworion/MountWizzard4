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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import astropy

# external packages

# local import
from mw4 import update
from base.loggerMW import setupLogging

setupLogging()


@mock.patch('sys.argv', ['python', '1', '10', '10', 'CLI', '0'])
def test_main_1():
    class Test:
        def __init__(self, runnable=None, version=None):
            pass

    update.UpdateCLI = Test
    update.main()


@mock.patch('sys.argv', ['python', '1', '10', '10', 'GUI', '0'])
def test_main_2():
    class Test:
        def __init__(self, runnable=None, version=None, x=0, y=0, colorSet=0):
            pass

        @staticmethod
        def run():
            return

    update.UpdateGUI = Test
    update.main()
