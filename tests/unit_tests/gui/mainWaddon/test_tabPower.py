############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import pytest
from mw4.gui.mainWaddon.tabPower import Power
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QInputDialog, QWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Power(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_setGuiVersion_1(function):
    function.setGuiVersion()


def test_setGuiVersion_2(function):
    function.setGuiVersion(version=2)


def test_updatePowerGui_1(function):
    function.updatePowerGui()


def test_updatePowerGui_2(function):
    function.app.power.data = {"FIRMWARE_INFO.VERSION": "1.5"}
    function.updatePowerGui()


def test_setDew_1(function):
    with mock.patch.object(QInputDialog, "getInt", return_value=(0, False)):
        function.setDew("A")


def test_setDew_2(function):
    with mock.patch.object(QInputDialog, "getInt", return_value=(0, False)):
        function.setDew("A")


def test_setDew_3(function):
    with mock.patch.object(QInputDialog, "getInt", return_value=(0, False)):
        function.ui.dewA.setText("10")
        function.setDew("A")


def test_setDew_4(function):
    with mock.patch.object(QInputDialog, "getInt", return_value=(0, True)):
        function.setDew("A")


def test_setDew_5(function):
    with mock.patch.object(QInputDialog, "getInt", return_value=(0, True)):
        function.ui.dewA.setText("10")
        function.setDew("A")


def test_togglePowerPort_1(function):
    function.togglePowerPort("1")


def test_togglePowerBootPort_1(function):
    function.togglePowerBootPort("2")


def test_togglePowerBootPort_2(function):
    function.togglePowerBootPort("1")


def test_toggleHubUSB_1(function):
    function.toggleHubUSB()


def test_togglePortUSB_1(function):
    function.togglePortUSB("1")


def test_toggleAutoDew_1(function):
    function.toggleAutoDew()


def test_setAdjustableOutput_2(function):
    function.ui.adjustableOutput.setText("10")
    with mock.patch.object(QInputDialog, "getDouble", return_value=(0, False)):
        function.setAdjustableOutput()


def test_setAdjustableOutput_3(function):
    function.ui.adjustableOutput.setText("10")
    with mock.patch.object(QInputDialog, "getDouble", return_value=(0, True)):
        function.setAdjustableOutput()


def test_rebootUPB_1(function):
    with mock.patch.object(function.app.power, "reboot", return_value=False):
        suc = function.rebootUPB()
        assert not suc


def test_rebootUPB_2(function):
    with mock.patch.object(function.app.power, "reboot", return_value=True):
        suc = function.rebootUPB()
        assert suc
