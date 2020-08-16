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
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from logic.telescope import TelescopeAlpaca
from logic.telescope.telescope import TelescopeSignals
from mw4.base.alpacaBase import AlpacaBase


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = TelescopeAlpaca(app=Test(), signals=TelescopeSignals(), data={})

        yield


def test_getInitialConfig_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.getInitialConfig()
        assert suc


def test_getInitialConfig_2():
    with mock.patch.object(app.client,
                           'aperturediameter',
                           return_value=100):
        with mock.patch.object(app.client,
                               'focallength',
                               return_value=570):
            suc = app.getInitialConfig()
            assert suc
            assert app.data['TELESCOPE_INFO.TELESCOPE_APERTURE'] == 100
            assert app.data['TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH'] == 570

