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
import logging
import pytest
import unittest.mock as mock
from mw4.gui.utilities.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.utilities.qtMessageDialog import MWMessageDialog
from mw4.gui.widgets.main_ui import Ui_MainWindow
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
)
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


def test_messageDialog_yes(function):
    widget = QWidget()
    with mock.patch.object(MWMessageDialog, "question", return_value=True):
        result = function.messageDialog(widget, "title", "question?")
        assert result is True


def test_messageDialog_no(function):
    widget = QWidget()
    with mock.patch.object(MWMessageDialog, "question", return_value=False):
        result = function.messageDialog(widget, "title", "question?")
        assert result is False


def test_messageDialog_customButtons(function):
    widget = QWidget()
    with mock.patch.object(MWMessageDialog, "question", return_value=2):
        result = function.messageDialog(widget, "title", "question?", ["A", "B", "C"])
        assert result == 2


def test_messageDialog_customButtonsCancelled(function):
    widget = QWidget()
    with mock.patch.object(MWMessageDialog, "question", return_value=MWMessageDialog.Rejected):
        result = function.messageDialog(widget, "title", "question?", ["A", "B"])
        assert result == MWMessageDialog.Rejected


def test_openFile_success(function, tmp_path):
    window = QWidget()
    expected = tmp_path / "test.fits"
    with mock.patch.object(MWFileDialog, "getOpenFileName", return_value=expected):
        result = function.openFile(
            window=window, title="title", folder=tmp_path, filterSet="*.fits"
        )
        assert result == expected


def test_openFile_cancelled(function, tmp_path):
    window = QWidget()
    with mock.patch.object(MWFileDialog, "getOpenFileName", return_value=Path()):
        result = function.openFile(
            window=window, title="title", folder=tmp_path, filterSet="*.*"
        )
        assert result == Path()


def test_openMultipleFiles_success(function, tmp_path):
    window = QWidget()
    expected = [tmp_path / "a.fits", tmp_path / "b.fits"]
    with mock.patch.object(MWFileDialog, "getOpenFileNames", return_value=expected):
        result = function.openMultipleFiles(
            window=window, title="title", folder=tmp_path, filterSet="*.fits"
        )
        assert result == expected


def test_openMultipleFiles_cancelled(function, tmp_path):
    window = QWidget()
    with mock.patch.object(MWFileDialog, "getOpenFileNames", return_value=[]):
        result = function.openMultipleFiles(
            window=window, title="title", folder=tmp_path, filterSet="*.*"
        )
        assert result == []


def test_saveFile_success(function, tmp_path):
    window = QWidget()
    expected = tmp_path / "config.cfg"
    with mock.patch.object(MWFileDialog, "getSaveFileName", return_value=expected):
        result = function.saveFile(
            window=window, title="title", folder=tmp_path, filterSet="*.cfg"
        )
        assert result == expected


def test_saveFile_cancelled(function, tmp_path):
    window = QWidget()
    with mock.patch.object(MWFileDialog, "getSaveFileName", return_value=Path()):
        result = function.saveFile(
            window=window, title="title", folder=tmp_path, filterSet="*.*"
        )
        assert result == Path()


def test_saveFile_enableDir_ignored(function, tmp_path):
    window = QWidget()
    expected = tmp_path / "out.cfg"
    with mock.patch.object(MWFileDialog, "getSaveFileName", return_value=expected):
        result = function.saveFile(
            window=window,
            title="title",
            folder=tmp_path,
            filterSet="*.cfg",
            enableDir=True,
        )
        assert result == expected


def test_openDir_success(function, tmp_path):
    window = QWidget()
    expected = tmp_path / "data"
    with mock.patch.object(MWFileDialog, "getExistingDirectory", return_value=expected):
        result = function.openDir(window=window, title="title", folder=tmp_path)
        assert result == expected


def test_openDir_cancelled(function, tmp_path):
    window = QWidget()
    with mock.patch.object(MWFileDialog, "getExistingDirectory", return_value=Path()):
        result = function.openDir(window=window, title="title", folder=tmp_path)
        assert result == Path()


def test_positionWindow_1(function):
    config = {"winPosX": 100, "winPosY": 100, "height": 400, "width": 600}
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    function.setPositionWindow(config)


def test_positionWindow_2(function):
    config = {"winPosX": 900, "winPosY": 900, "height": 400, "width": 600}
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    function.setPositionWindow(config)
