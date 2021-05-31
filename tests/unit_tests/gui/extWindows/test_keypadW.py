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
import unittest.mock as mock
import pytest

# external packages
from PyQt5 import sip
from PyQt5.QtGui import QCloseEvent

# local import
from tests.baseTestSetupExtWindows import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.keypadW import KeypadWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = KeypadWindow(app=App())
    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc

    function.app.config['keypadW'] = {'winPosX': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    suc = function.initConfig()
    assert suc

    function.app.config['keypadW'] = {'winPosY': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_4(function):
    function.app.config['keypadW'] = {}
    function.app.config['keypadW']['winPosX'] = 100
    function.app.config['keypadW']['winPosY'] = 100
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'keypadW' in function.app.config:
        del function.app.config['keypadW']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['keypadW'] = {}

    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(sip,
                           'delete'):
        with mock.patch.object(function,
                               'show'):
            with mock.patch.object(function,
                                   'showUrl'):
                with mock.patch.object(MWidget,
                                       'closeEvent'):
                    function.showWindow()
                    function.closeEvent(QCloseEvent)


def test_showWindow_1(function):
    function.app.mount.setting.webInterfaceStat = 0
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(function,
                               'showUrl'):
            with mock.patch.object(function.app.mount.setting,
                                   'setWebInterface',
                                   return_value=False):
                suc = function.showWindow()
                assert suc
                function.browser.loadFinished.disconnect(function.loadFinished)


def test_loadFinished_1(function):
    function.loadFinished()


def test_showUrl_1(function):
    function.app.mount.host = ('', 3492)
    function.showUrl()


def test_showUrl_2(function):
    function.app.mount.host = ('localhost', 3492)
    function.showUrl()
