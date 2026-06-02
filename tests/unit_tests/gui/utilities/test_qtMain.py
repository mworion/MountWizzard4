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
import logging
import os
import pytest
import unittest.mock as mock
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from pathlib import Path
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
)
from skyfield.api import load
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    window = MWidget()
    window.app = App()
    window.ui = Ui_MainWindow()
    window.ui.setupUi(window)
    yield window


def test_saveWindowAsPNG(function):
    class Save:
        @staticmethod
        def save(a):
            return

    window = QWidget()
    window.app = App()
    window.log = logging.getLogger("MW4")
    with mock.patch.object(QWidget, "grab", return_value=Save()):
        function.saveWindowAsPNG(window)


def test_saveAllWindowsAsPNG_1(function):
    class ExternalWindows:
        uiWindows = {"test1": {"classObj": None}, "test2": {"classObj": 1}}

    window = QWidget()
    window.app = App()
    window.app.mainW.externalWindows = ExternalWindows()

    with mock.patch.object(function, "saveWindowAsPNG"):
        function.saveAllWindowsAsPNG(window)


def test_keyPressEvent_1(function):
    class Key:
        @staticmethod
        def key():
            return 16777268

    with mock.patch.object(function, "saveWindowAsPNG"):
        function.keyPressEvent(Key())


def test_keyPressEvent_2(function):
    class Key:
        @staticmethod
        def key():
            return 16777269

    with mock.patch.object(function, "saveAllWindowsAsPNG"):
        function.keyPressEvent(Key())


def test_keyPressEvent_3(function):
    class Key:
        @staticmethod
        def key():
            return 1

    with mock.patch.object(QWidget, "keyPressEvent"):
        function.keyPressEvent(Key())


def test_changeEvent_1(function):
    from PySide6.QtCore import QEvent

    class MockEvent:
        @staticmethod
        def type():
            return QEvent.Type.WindowStateChange

        @staticmethod
        def accept():
            pass

    with (
        mock.patch.object(function, "windowState", return_value=0),
        mock.patch.object(function.titleBar, "windowStateChanged"),
        mock.patch.object(QMainWindow, "changeEvent"),
    ):
        function.changeEvent(MockEvent())


def test_wIcon_1(function):
    ui = QPushButton()
    function.wIcon(ui, "load")


def test_renderStyle_1(function):
    inp = "12345$M_PRIM$12345"
    function.colorSet = 0
    val = function.renderStyle(inp).strip(" ")
    assert val == "12345#2090C012345\n"


def test_renderStyle_2(function):
    inp = "12345$M_TEST$12345"
    function.colorSet = 0
    val = function.renderStyle(inp).strip(" ")
    assert val == "12345$M_TEST$12345\n"


def test_initUI_1(function):
    with (
        mock.patch.object(function, "setMouseTracking"),
        mock.patch.object(function, "setWindowIcon"),
    ):
        function.initUI()


def test_prepareFileDialog_1(function):
    window = QWidget()
    suc = function.prepareFileDialog(window=window)
    assert suc


def test_prepareFileDialog_2(function):
    window = QWidget()
    suc = function.prepareFileDialog(window=window, enableDir=True)
    assert suc


def test_runDialog_1(function):
    dialog = QFileDialog()
    with mock.patch.object(QFileDialog, "exec", return_value=0):
        val = function.runDialog(dialog)
        assert val == 0


def test_messageDialog_1(function):
    widget = QWidget()
    with mock.patch.object(function, "runDialog", return_value=QMessageBox.StandardButton.No):
        suc = function.messageDialog(widget, "test", "test")
        assert not suc


def test_messageDialog_2(function):
    widget = QWidget()
    with mock.patch.object(function, "runDialog", return_value=QMessageBox.StandardButton.Yes):
        suc = function.messageDialog(widget, "test", "test")
        assert suc


def test_messageDialog_3(function):
    widget = QWidget()
    with mock.patch.object(function, "runDialog", return_value=QMessageBox.StandardButton.Yes):
        suc = function.messageDialog(widget, "test", "test", ["A", "B"])
        assert suc


def test_openFile_5(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=0):
        full = function.openFile(
            window=window, title="title", folder=Path("."), filterSet="*.*"
        )
        assert full == Path()


def test_openFile_6(function):
    window = QWidget()
    with (
        mock.patch.object(function, "runDialog", return_value=1),
        mock.patch.object(QFileDialog, "selectedFiles", return_value=["test1"]),
    ):
        full = function.openFile(
            window=window, title="title", folder=Path("."), filterSet="*.*"
        )
        assert full == Path("test1")


def test_openMultipleFiles_1(function):
    window = QWidget()
    with (
        mock.patch.object(function, "runDialog", return_value=1),
        mock.patch.object(QFileDialog, "selectedFiles", return_value=["test1", "test2"]),
    ):
        full = function.openMultipleFiles(
            window=window, title="title", folder=Path("."), filterSet="*.*"
        )
        assert full == [Path("test1"), Path("test2")]


def test_saveFile_5(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=0):
        full = function.saveFile(
            window=window, title="title", folder=Path("."), filterSet="*.*"
        )
        assert full == Path()


def test_saveFile_6(function):
    window = QWidget()
    with (
        mock.patch.object(function, "runDialog", return_value=1),
        mock.patch.object(QFileDialog, "selectedFiles", return_value=["tests/test.txt"]),
    ):
        function.saveFile(window=window, title="title", folder=Path("."), filterSet="*.*")


def test_openDir_4(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=1):
        full = function.openDir(window=window, title="title", folder=Path("."))
        assert full == Path(os.getcwd())


def test_openDir_5(function):
    window = QWidget()
    with mock.patch.object(function, "runDialog", return_value=None):
        full = function.openDir(window=window, title="title", folder=Path("."))
        assert full == Path()


def test_convertTime_1(function):
    ts = load.timescale()
    t = ts.tt(2000, 1, 1, 12, 0)
    function.ui.unitTimeUTC.setChecked(True)
    val = function.convertTime(t, "%H:%M")
    assert val


def test_convertTime_2(function):
    ts = load.timescale()
    t = ts.tt(2000, 1, 1, 12, 0)
    function.ui.unitTimeLocal.setChecked(True)
    val = function.convertTime(t, "%H:%M")
    assert val


def test_timeZoneString_1(function):
    function.ui.unitTimeUTC.setChecked(True)
    val = function.timeZoneString()
    assert val == "(time is UTC)"


def test_timeZoneString_2(function):
    function.ui.unitTimeLocal.setChecked(True)
    val = function.timeZoneString()
    assert val == "(time is local)"


def test_positionWindow_1(function):
    config = {"winPosX": 100, "winPosY": 100, "height": 400, "width": 600}
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    function.positionWindow(config)


def test_positionWindow_2(function):
    config = {"winPosX": 900, "winPosY": 900, "height": 400, "width": 600}
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    function.positionWindow(config)
