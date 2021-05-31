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

# external packages
from PyQt5.QtGui import QCloseEvent

# local import
from tests.baseTestSetupExtWindows import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.messageW import MessageWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = MessageWindow(app=App())
    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc

    function.app.config['messageW'] = {'winPosX': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_3(function):
    suc = function.initConfig()
    assert suc

    function.app.config['messageW'] = {'winPosY': 10000}
    suc = function.initConfig()
    assert suc


def test_initConfig_4(function):
    function.app.config['messageW'] = {}
    function.app.config['messageW']['winPosX'] = 100
    function.app.config['messageW']['winPosY'] = 100
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'messageW' in function.app.config:
        del function.app.config['messageW']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['messageW'] = {}

    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_clearWindow_1(function):
    suc = function.clearWindow()
    assert suc


def test_writeMessage_1(function):
    suc = function.writeMessage()
    assert suc


def test_writeMessage_2(function):
    function.app.messageQueue.put(('test', 0))
    suc = function.writeMessage()
    assert suc


def test_writeMessage_3(function):
    function.app.messageQueue.put(('test', -1))
    suc = function.writeMessage()
    assert suc


def test_writeMessage_4(function):
    function.app.messageQueue.put(('test', 10))
    suc = function.writeMessage()
    assert suc


def test_writeMessage_5(function):
    function.app.messageQueue.put(('test', 0x100))
    suc = function.writeMessage()
    assert suc
