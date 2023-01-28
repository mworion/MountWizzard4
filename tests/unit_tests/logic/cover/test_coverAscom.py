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
import platform

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.cover.coverAscom import CoverAscom
from base.driverDataClass import Signals

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'
        CoverState = 1

        @staticmethod
        def CloseCover():
            return True

        @staticmethod
        def OpenCover():
            return True

        @staticmethod
        def HaltCover():
            return True

        @staticmethod
        def CalibratorOn():
            return True

        @staticmethod
        def CalibratorOff():
            return True

        @staticmethod
        def Brightness(a):
            return True

    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        func = CoverAscom(app=App(), signals=Signals(), data={})
        func.client = Test1()
        func.clientProps = []
        yield func


def test_workerPollData_1(function):
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=1):
        with mock.patch.object(function,
                               'storePropertyToData'):
            suc = function.workerPollData()
            assert suc


def test_closeCover_1(function):
    function.deviceConnected = False
    suc = function.closeCover()
    assert not suc


def test_closeCover_2(function):
    function.deviceConnected = True
    suc = function.closeCover()
    assert suc


def test_closeCover_3(function):
    function.deviceConnected = True
    suc = function.closeCover()
    assert suc


def test_openCover_1(function):
    function.deviceConnected = False
    suc = function.openCover()
    assert not suc


def test_openCover_2(function):
    function.deviceConnected = True
    suc = function.openCover()
    assert suc


def test_openCover_3(function):
    function.deviceConnected = True
    suc = function.openCover()
    assert suc


def test_haltCover_1(function):
    function.deviceConnected = False
    suc = function.haltCover()
    assert not suc


def test_haltCover_2(function):
    function.deviceConnected = True
    suc = function.haltCover()
    assert suc


def test_haltCover_3(function):
    function.deviceConnected = True
    suc = function.haltCover()
    assert suc


def test_lightOn_1(function):
    function.deviceConnected = False
    suc = function.lightOn()
    assert not suc


def test_lightOn_2(function):
    function.deviceConnected = True
    suc = function.lightOn()
    assert suc


def test_lightOn_3(function):
    function.deviceConnected = True
    suc = function.lightOn()
    assert suc


def test_lightOff_1(function):
    function.deviceConnected = False
    suc = function.lightOff()
    assert not suc


def test_lightOff_2(function):
    function.deviceConnected = True
    suc = function.lightOff()
    assert suc


def test_lightOff_3(function):
    function.deviceConnected = True
    suc = function.lightOff()
    assert suc


def test_lightIntensity_1(function):
    function.deviceConnected = False
    suc = function.lightIntensity(0)
    assert not suc


def test_lightIntensity_2(function):
    function.deviceConnected = True
    suc = function.lightIntensity(0)
    assert suc


def test_lightIntensity_3(function):
    function.deviceConnected = True
    suc = function.lightIntensity(0)
    assert suc
