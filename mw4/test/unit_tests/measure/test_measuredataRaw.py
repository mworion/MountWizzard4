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
import pytest
import unittest.mock as mock
import faulthandler
faulthandler.enable()

# external packages
import PyQt5

# local import
from mw4.measure.measureRaw import MeasureDataRaw


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():

    class Test1:
        @staticmethod
        def setEmptyData():
            return

        @staticmethod
        def measureTask():
            return True

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = MeasureDataRaw(parent=Test1())
        yield


def test_startCommunication():
    with mock.patch.object(app.timerTask,
                           'start'):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication():
    with mock.patch.object(app.timerTask,
                           'stop'):
        suc = app.stopCommunication()
        assert suc


def test_measureTask():
    suc = app.measureTask()
    assert suc
