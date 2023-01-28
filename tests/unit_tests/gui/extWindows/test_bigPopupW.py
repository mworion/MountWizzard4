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
import unittest.mock as mock
import pytest

# external packages
from PyQt5.QtGui import QCloseEvent

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import gui.extWindows.bigPopupW
from gui.extWindows.bigPopupW import BigPopup
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    window = BigPopup(App())
    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'bigPopupW' in function.app.config:
        del function.app.config['bigPopupW']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['bigPopupW'] = {}

    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_showWindow(function):
    with mock.patch.object(function,
                           'show'):
        suc = function.showWindow()
        assert suc


def test_colorChange(function):
    suc = function.colorChange()
    assert suc


def test_updateDeviceStats(function):
    suc = function.updateDeviceStats()
    assert suc


def test_updateStatus_1(function):
    function.app.mount.obsSite.status = 0
    suc = function.updateStatus()
    assert suc


def test_updateStatus_2(function):
    function.app.mount.obsSite.status = 1
    suc = function.updateStatus()
    assert suc
