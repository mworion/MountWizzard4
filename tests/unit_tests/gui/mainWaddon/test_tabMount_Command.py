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
import webbrowser

# external packages
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabMount_Command import MountCommand
import mountcontrol


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = MountCommand(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_openCommandProtocol_1(function):
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openCommandProtocol()


def test_openCommandProtocol_2(function):
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openCommandProtocol()


def test_openUpdateTimeDelta_1(function):
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openUpdateTimeDelta()


def test_openUpdateTimeDelta_2(function):
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openUpdateTimeDelta()


def test_openUpdateFirmware_1(function):
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openUpdateFirmware()


def test_openUpdateFirmware_2(function):
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openUpdateFirmware()


def test_openMountDocumentation_1(function):
    function.app.mount.firmware.product = "tester"
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openMountDocumentation()


def test_openMountDocumentation_2(function):
    function.app.mount.firmware.product = "10micron GM1000HPS"
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openMountDocumentation()


def test_openMountDocumentation_3(function):
    function.app.mount.firmware.product = "10micron GM1000HPS"
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openMountDocumentation()


def test_commandRaw_1(function):
    with mock.patch.object(
        mountcontrol.connection.Connection,
        "communicateRaw",
        return_value=(True, False, ""),
    ):
        function.commandRaw()


def test_commandRaw_2(function):
    with mock.patch.object(
        mountcontrol.connection.Connection,
        "communicateRaw",
        return_value=(True, True, ""),
    ):
        function.commandRaw()
