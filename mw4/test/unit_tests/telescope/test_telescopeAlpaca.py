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
from mw4.telescope.telescopeAlpaca import TelescopeAlpaca
from mw4.telescope.telescope import TelescopeSignals
from mw4.base.alpacaBase import AlpacaBase


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
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
                           return_value=0.1):
        with mock.patch.object(app.client,
                               'focallength',
                               return_value=0.57):
            suc = app.getInitialConfig()
            assert suc
            assert app.data['TELESCOPE_INFO.TELESCOPE_APERTURE'] == 100
            assert app.data['TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH'] == 570

