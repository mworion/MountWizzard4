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
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
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
    assert val == "12345rgba(32, 144, 192, 255)12345\n"


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


@mock.patch("mw4.gui.utilities.qtMain.platform.system", return_value="Linux")
def test_positionWindow_linux_maximized(mock_platform, function):
    """Test setPositionWindow on Linux with maximized window dimensions."""
    max_height = function.maximumHeight()
    max_width = function.maximumWidth()
    config = {"height": max_height, "width": max_width}
    function.setPositionWindow(config)
    mock_platform.assert_called()


def test_getPositionWindow_1(function):
    config = {}
    result = function.getPositionWindow(config)
    assert "winPosX" in result
    assert "winPosY" in result
    assert "height" in result
    assert "width" in result
    assert result["winPosX"] >= 0
    assert result["winPosY"] >= 0
    assert result["height"] > 0
    assert result["width"] > 0


def test_setWindowTitle_1(function):
    function.setWindowTitle("Test Window")
    assert function.titleBar.title.text() == "Test Window"


def test_mousePressEvent_1(function):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    # Simulate mouse press at bottom-right corner to trigger resize
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(function.width() - 5, function.height() - 5),
        QPointF(function.width() - 5, function.height() - 5),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    function.mousePressEvent(event)
    assert function.isResizing is True


def test_mousePressEvent_2(function):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    # Simulate mouse press at center (not on resize area)
    # First reset state and ensure window is large enough
    function.isResizing = False
    function.resize(400, 400)
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(100, 100),
        QPointF(100, 100),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    function.mousePressEvent(event)
    assert function.isResizing is False


def test_mouseReleaseEvent_1(function):
    function.isResizing = True
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        QPointF(100, 100),
        QPointF(100, 100),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )
    function.mouseReleaseEvent(event)
    assert function.isResizing is False


def test_mouseMoveEvent_1(function):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    function.isResizing = True

    event = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPointF(500, 500),
        QPointF(500, 500),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    function.mouseMoveEvent(event)
    # After resize, size should change
    # Note: resize may be constrained by minimum size


def test_mouseMoveEvent_2(function):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    function.isResizing = False
    old_width = function.width()
    old_height = function.height()

    event = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPointF(500, 500),
        QPointF(500, 500),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    function.mouseMoveEvent(event)
    # When not resizing, size should not change
    assert function.width() == old_width
    assert function.height() == old_height
