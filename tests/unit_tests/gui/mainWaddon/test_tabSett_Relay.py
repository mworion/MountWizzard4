############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

import pytest

# external packages
from PySide6.QtWidgets import QWidget

from mw4.gui.mainWaddon.tabSett_Relay import SettRelay
from mw4.gui.widgets.main_ui import Ui_MainWindow

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SettRelay(mainW)
    yield window
    mainW.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    with mock.patch.object(function, "updateRelayButtonText"):
        function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupRelayGui(function):
    assert len(function.relayDropDowns) == 8
    assert len(function.relayButtonTexts) == 8
    assert len(function.relayButtons) == 8
    for dropDown in function.relayDropDowns:
        val = dropDown.count()
        assert val == 2


def test_updateRelayButtonText_1(function):
    function.updateRelayButtonText()


def test_toggleRelay_1(function):
    function.ui.relayDevice.setCurrentIndex(0)
    function.relayButtonPressed(0)


def test_toggleRelay_2(function):
    function.ui.relayDevice.setCurrentIndex(1)
    with mock.patch.object(function.app.relay, "switch", return_value=False):
        function.relayButtonPressed(1)


def test_doRelayAction_1(function):
    function.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(function.app.relay, "switch", return_value=False):
        suc = function.doRelayAction(7)
        assert not suc


def test_doRelayAction_2(function):
    function.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(function.app.relay, "switch", return_value=True):
        suc = function.doRelayAction(7)
        assert suc


def test_doRelayAction_3(function):
    function.relayDropDowns[7].setCurrentIndex(2)
    suc = function.doRelayAction(7)
    assert not suc


def test_doRelayAction_4(function):
    function.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(function.app.relay, "pulse", return_value=False):
        suc = function.doRelayAction(7)
        assert not suc


def test_doRelayAction_5(function):
    function.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(function.app.relay, "pulse", return_value=True):
        suc = function.doRelayAction(7)
        assert suc


def test_relayButtonPressed_1(function):
    with mock.patch.object(function, "doRelayAction", return_value=False):
        function.relayButtonPressed(1)


def test_relayButtonPressed_2(function):
    with mock.patch.object(function, "doRelayAction", return_value=True):
        function.relayButtonPressed(2)


def test_updateRelayGui(function):
    function.relayButton = list()
    function.relayDropDown = list()
    function.relayText = list()
    function.app.relay.status = [0, 1, 0, 1, 0, 1, 0, 1]
    function.updateRelayGui()
