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
import astropy
import unittest.mock as mock

# external packages
import PySide6

# local import
from logic.measure.measureRaw import MeasureDataRaw


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        @staticmethod
        def setEmptyData():
            return

        @staticmethod
        def measureTask():
            return True

    with mock.patch.object(PySide6.QtCore.QTimer,
                           'start'):
        func = MeasureDataRaw(parent=Test1())
        yield func


def test_startCommunication(function):
    with mock.patch.object(function.timerTask,
                           'start'):
        suc = function.startCommunication()
        assert suc


def test_stopCommunication(function):
    with mock.patch.object(function.timerTask,
                           'stop'):
        suc = function.stopCommunication()
        assert suc


def test_measureTask(function):
    suc = function.measureTask()
    assert suc
