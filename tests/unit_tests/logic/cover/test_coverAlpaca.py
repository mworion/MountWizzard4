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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.cover.coverAlpaca import CoverAlpaca
from base.driverDataClass import Signals


@pytest.fixture(autouse=True, scope='function')
def function():
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        func = CoverAlpaca(app=App(), signals=Signals(), data={})
        yield func


def test_workerPollData_1(function):
    function.deviceConnected = False
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=1):
        suc = function.workerPollData()
        assert not suc


def test_workerPollData_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=1):
        with mock.patch.object(function,
                               'storePropertyToData'):
            suc = function.workerPollData()
            assert suc


def test_closeCover_1(function):
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.closeCover()
        assert not suc


def test_closeCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.closeCover()
        assert suc


def test_openCover_1(function):
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.openCover()
        assert not suc


def test_openCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.openCover()
        assert suc


def test_haltCover_1(function):
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.haltCover()
        assert not suc


def test_haltCover_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.haltCover()
        assert suc


def test_lightOn_1(function):
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=0):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            suc = function.lightOn()
            assert not suc


def test_lightOn_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty',
                           return_value=0):
        with mock.patch.object(function,
                               'setAlpacaProperty'):
            suc = function.lightOn()
            assert suc


def test_lightOff_1(function):
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.lightOff()
        assert not suc


def test_lightOff_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'getAlpacaProperty'):
        suc = function.lightOff()
        assert suc


def test_lightIntensity_1(function):
    with mock.patch.object(function,
                           'setAlpacaProperty'):
        suc = function.lightIntensity(0)
        assert not suc


def test_lightIntensity_2(function):
    function.deviceConnected = True
    with mock.patch.object(function,
                           'setAlpacaProperty'):
        suc = function.lightIntensity(0)
        assert suc

