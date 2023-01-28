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
from logic.telescope.telescopeAscom import TelescopeAscom
from base.driverDataClass import Signals
from base.ascomClass import AscomClass

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        ApertureDiameter = 100
        FocalLength = 570
        connected = True
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        func = TelescopeAscom(app=App(), signals=Signals(), data={})
        func.client = Test1()
        func.clientProps = []
        yield func


def test_workerGetInitialConfig_1(function):
    with mock.patch.object(AscomClass,
                           'workerGetInitialConfig',
                           return_value=True):
        suc = function.workerGetInitialConfig()
        assert suc


def test_workerGetInitialConfig_2(function):
    with mock.patch.object(function,
                           'getAscomProperty',
                           return_value=0.57):
        suc = function.workerGetInitialConfig()
        assert suc
        assert function.data['TELESCOPE_INFO.TELESCOPE_APERTURE'] == 570.0
        assert function.data['TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH'] == 570.0

