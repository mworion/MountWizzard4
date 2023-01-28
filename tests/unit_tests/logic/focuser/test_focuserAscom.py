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

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.focuser.focuserAscom import FocuserAscom
from base.driverDataClass import Signals

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        @staticmethod
        def move(a):
            return True

        @staticmethod
        def halt():
            return True

        Position = 1
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    func = FocuserAscom(app=App(), signals=Signals(), data={})
    func.clientProps = []
    func.client = Test1()
    yield func


def test_workerPollData_1(function):
    with mock.patch.object(function,
                           'getAndStoreAscomProperty'):
        suc = function.workerPollData()
        assert suc


def test_move_1(function):
    function.deviceConnected = True
    suc = function.move(3)
    assert suc


def test_move_2(function):
    function.deviceConnected = False
    suc = function.move(3)
    assert not suc


def test_halt_1(function):
    function.deviceConnected = True
    suc = function.halt()
    assert suc


def test_halt_2(function):
    function.deviceConnected = False
    suc = function.halt()
    assert not suc
