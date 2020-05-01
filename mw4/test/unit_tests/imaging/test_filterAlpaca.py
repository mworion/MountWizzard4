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
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from mw4.imaging.filterAlpaca import FilterAlpaca
from mw4.imaging.filter import FilterSignals
from mw4.base.alpacaBase import AlpacaBase


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = FilterAlpaca(app=Test(), signals=FilterSignals(), data={})

    yield


def test_getInitialConfig_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.getInitialConfig()
        assert suc


def test_getInitialConfig_2():
    with mock.patch.object(app.client,
                           'names',
                           return_value=['test', 'test1']):
        suc = app.getInitialConfig()
        assert suc
        assert app.data['FILTER_NAME.FILTER_SLOT_NAME_0'] == 'test'
        assert app.data['FILTER_NAME.FILTER_SLOT_NAME_1'] == 'test1'


def test_workerPollData_1():
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=-1):
        suc = app.workerPollData()
        assert not suc


def test_workerPollData_2():
    with mock.patch.object(AlpacaBase,
                           'get',
                           return_value=1):
        suc = app.workerPollData()
        assert suc
        assert app.data['FILTER_SLOT.FILTER_SLOT_VALUE'] == 1


def test_sendFilterNumber_1():
    with mock.patch.object(AlpacaBase,
                           'put'):
        suc = app.sendFilterNumber()
        assert suc
