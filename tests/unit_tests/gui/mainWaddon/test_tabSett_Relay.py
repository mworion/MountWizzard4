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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabSett_Relay import SettRelay
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    class Mixin(MWidget, SettRelay):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = self.app.deviceStat
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SettRelay.__init__(self)

    window = Mixin()
    yield window


def test_setupRelayGui(function):
    assert 8 == len(function.relayDropDowns)
    assert 8 == len(function.relayButtonTexts)
    assert 8 == len(function.relayButtons)
    for dropDown in function.relayDropDowns:
        val = dropDown.count()
        assert 2 == val


def test_toggleRelay_1(function):
    def Sender():
        return function.ui.relayButton0
    function.sender = Sender

    function.ui.relayDevice.setCurrentIndex(0)
    suc = function.relayButtonPressed()
    assert not suc


def test_toggleRelay_2(function):
    def Sender():
        return function.ui.relayButton0
    function.sender = Sender
    function.ui.relayDevice.setCurrentIndex(1)
    with mock.patch.object(function.app.relay,
                           'switch',
                           return_value=False):
        suc = function.relayButtonPressed()
        assert not suc


def test_doRelayAction_1(function):
    function.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(function.app.relay,
                           'switch',
                           return_value=False):
        suc = function.doRelayAction(7)
        assert not suc


def test_doRelayAction_2(function):
    function.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(function.app.relay,
                           'switch',
                           return_value=True):
        suc = function.doRelayAction(7)
        assert suc


def test_doRelayAction_3(function):
    function.relayDropDowns[7].setCurrentIndex(2)
    suc = function.doRelayAction(7)
    assert not suc


def test_doRelayAction_4(function):
    function.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(function.app.relay,
                           'pulse',
                           return_value=False):
        suc = function.doRelayAction(7)
        assert not suc


def test_doRelayAction_5(function):
    function.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(function.app.relay,
                           'pulse',
                           return_value=True):
        suc = function.doRelayAction(7)
        assert suc


def test_relayButtonPressed_1(function):
    def Sender():
        return function.ui.relayButton0
    function.sender = Sender

    with mock.patch.object(function,
                           'doRelayAction',
                           return_value=False):
        suc = function.relayButtonPressed()
        assert not suc


def test_relayButtonPressed_2(function):
    def Sender():
        return function.ui.relayButton0
    function.sender = Sender

    with mock.patch.object(function,
                           'doRelayAction',
                           return_value=True):
        suc = function.relayButtonPressed()
        assert suc
