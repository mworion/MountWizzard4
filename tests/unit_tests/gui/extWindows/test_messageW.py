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
from PyQt5.QtGui import QCloseEvent

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.messageW import MessageWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = MessageWindow(app=App())
    yield func


def test_initConfig_1(function):
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


def test_colorChange(function):
    with mock.patch.object(function,
                           'setupMessage'):
        with mock.patch.object(function,
                               'clearMessageTable'):
            suc = function.colorChange()
            assert suc


def test_clearMessageTable_1(function):
    suc = function.clearMessageTable()
    assert suc


def test_writeMessage_1(function):
    suc = function.writeMessage()
    assert suc


def test_writeMessage_2(function):
    function.app.messageQueue.put((0, 'test', 'test', 'test'))
    suc = function.writeMessage()
    assert suc
