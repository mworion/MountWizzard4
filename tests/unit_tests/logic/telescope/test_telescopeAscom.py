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
import pytest
import unittest.mock as mock
import platform

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from logic.telescope.telescopeAscom import TelescopeAscom
from logic.telescope.telescope import TelescopeSignals
from base.ascomClass import AscomClass

if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test1:
        ApertureDiameter = 100
        FocalLength = 570
        connected = True
        Name = 'test'
        DriverVersion = '1'
        DriverInfo = 'test1'

    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = TelescopeAscom(app=Test(), signals=TelescopeSignals(), data={})
        app.client = Test1()
        app.clientProps = []
        yield


def test_workerGetInitialConfig_1():
    with mock.patch.object(AscomClass,
                           'workerGetInitialConfig',
                           return_value=True):
        suc = app.workerGetInitialConfig()
        assert suc


def test_workerGetInitialConfig_2():
    with mock.patch.object(app,
                           'getAscomProperty',
                           return_value=0.57):
        suc = app.workerGetInitialConfig()
        assert suc
        assert app.data['TELESCOPE_INFO.TELESCOPE_APERTURE'] == 570.0
        assert app.data['TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH'] == 570.0

