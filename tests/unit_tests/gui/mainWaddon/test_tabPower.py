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
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

import pytest
from mw4.gui.mainWaddon.tabPower import Power
from mw4.gui.utilities.nativeQt.qtInputDialog import MWInputDialog
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QWidget
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
    assert function.version == 1


def test_setGuiVersion_2(function):
    function.setGuiVersion(version=2)
    assert function.version == 2


def test_setGuiVersion_3(function):
    function.setGuiVersion(version=3)
    assert function.version == 3


def test_updatePowerGui_1(function):
    function.setGuiVersion(version=1)
    function.updatePowerGui()


def test_updatePowerGui_2(function):
    function.setGuiVersion(version=2)
    function.app.dReg.d["power"].instance.data = {"DEW_LABELS.DEW_CHANNEL_1": 5}
    function.updatePowerGui()
    function.setGuiVersion(version=1)


def test_setDewCycle_1(function):
    with mock.patch.object(MWInputDialog, "getInt", return_value=(0, False)):
        assert not function.setDewCycle("1", None)


def test_setDewCycle_2(function):
    with (
        mock.patch.object(MWInputDialog, "getInt", return_value=(0, True)),
        mock.patch.object(function.app.dReg.d["power"].instance, "sendDew", return_value=True),
    ):
        function.ui.dewCycle1.setText("10")
        assert function.setDewCycle("1", None)


def test_togglePowerPort_1(function):
    with mock.patch.object(
        function.app.dReg.d["power"].instance, "togglePowerPort", return_value=True
    ):
        function.togglePowerPort("1")


def test_toggleHubUSB_1(function):
    with mock.patch.object(
        function.app.dReg.d["power"].instance, "toggleHubUSB", return_value=True
    ):
        function.toggleHubUSB()


def test_togglePortUSB_1(function):
    with mock.patch.object(
        function.app.dReg.d["power"].instance, "togglePortUSB", return_value=True
    ):
        function.togglePortUSB("1")


def test_setAdjustableOutput_1(function):
    function.ui.adjustableOutput.setText("-")
    with mock.patch.object(MWInputDialog, "getDouble", return_value=(0, False)):
        assert not function.setAdjustableOutput()


def test_setAdjustableOutput_2(function):
    function.ui.adjustableOutput.setText("10")
    with mock.patch.object(MWInputDialog, "getDouble", return_value=(0, False)):
        assert not function.setAdjustableOutput()


def test_setAdjustableOutput_3(function):
    function.ui.adjustableOutput.setText("10")
    with (
        mock.patch.object(MWInputDialog, "getDouble", return_value=(0, True)),
        mock.patch.object(function.app.dReg.d["power"].instance, "sendAdjustableOutput"),
    ):
        assert function.setAdjustableOutput()


def test_rebootUPB_1(function):
    with mock.patch.object(function.app.dReg.d["power"].instance, "reboot") as reboot:
        function.rebootUPB()
        reboot.assert_called_once()
