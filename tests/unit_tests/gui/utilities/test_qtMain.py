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
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QWidget,
)
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from typing import ClassVar
from unittest import mock


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
        uiWindows: ClassVar = {"test1": {"classObj": None}, "test2": {"classObj": 1}}

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


def test_getEdges_1(function):
    """Test getEdges for right edge only."""
    from PySide6.QtCore import QPoint
    pos = QPoint(function.width() - 5, 100)
    edges = function.getEdges(pos)
    assert edges & Qt.Edge.RightEdge


def test_getEdges_2(function):
    """Test getEdges for bottom edge only."""
    from PySide6.QtCore import QPoint
    pos = QPoint(100, function.height() - 5)
    edges = function.getEdges(pos)
    assert edges & Qt.Edge.BottomEdge


def test_getEdges_3(function):
    """Test getEdges for bottom-right corner."""
    from PySide6.QtCore import QPoint
    pos = QPoint(function.width() - 5, function.height() - 5)
    edges = function.getEdges(pos)
    assert edges == (Qt.Edge.BottomEdge | Qt.Edge.RightEdge)


def test_getEdges_4(function):
    """Test getEdges for center (no edges)."""
    from PySide6.QtCore import QPoint
    pos = QPoint(100, 100)
    edges = function.getEdges(pos)
    assert edges == Qt.Edge(0)


def test_setResizeCursorShape_1(function):
    """Test setResizeCursorShape with no edges when no resize shape set."""
    function.cursorHasResizeShape = False
    function.setResizeCursorShape(Qt.Edge(0))
    assert function.cursorHasResizeShape is False


def test_setResizeCursorShape_2(function):
    """Test setResizeCursorShape with no edges resets existing resize shape."""
    function.cursorHasResizeShape = True
    function.setResizeCursorShape(Qt.Edge(0))
    assert function.cursorHasResizeShape is False


def test_setResizeCursorShape_3(function):
    """Test setResizeCursorShape with right and bottom edge."""
    function.setResizeCursorShape(Qt.Edge.BottomEdge | Qt.Edge.RightEdge)
    assert function.cursorHasResizeShape is True
    assert function.cursor().shape() == Qt.CursorShape.SizeFDiagCursor


def test_setResizeCursorShape_4(function):
    """Test setResizeCursorShape with right edge only."""
    function.setResizeCursorShape(Qt.Edge.RightEdge)
    assert function.cursorHasResizeShape is True
    assert function.cursor().shape() == Qt.CursorShape.SizeHorCursor


def test_setResizeCursorShape_5(function):
    """Test setResizeCursorShape with bottom edge only."""
    function.setResizeCursorShape(Qt.Edge.BottomEdge)
    assert function.cursorHasResizeShape is True
    assert function.cursor().shape() == Qt.CursorShape.SizeVerCursor


def test_eventFilter_leave_event(function):
    """Test eventFilter for leave event."""
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    event = QMouseEvent(
        QMouseEvent.Type.Leave,
        QPointF(0, 0),
        QPointF(0, 0),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    result = function.eventFilter(function, event)
    assert result is False


def test_eventFilter_hover_leave_event(function):
    """Test eventFilter for hover leave event."""
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    event = QMouseEvent(
        QMouseEvent.Type.HoverLeave,
        QPointF(0, 0),
        QPointF(0, 0),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    result = function.eventFilter(function, event)
    assert result is False


def test_eventFilter_mouse_move_inside_rect(function):
    """Test eventFilter for mouse move inside window."""
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    # Use coordinates in the middle of the window
    event = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPointF(50, 50),
        function.mapToGlobal(QPointF(50, 50).toPoint()),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    result = function.eventFilter(function, event)
    assert result is False


def test_eventFilter_mouse_move_outside_rect(function):
    """Test eventFilter for mouse move outside window."""
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    # Simulate a position that would be outside the window bounds
    event = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPointF(-100, -100),
        QPointF(-100, -100),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    result = function.eventFilter(function, event)
    assert result is False


def test_eventFilter_mouse_button_press_without_edges(function):
    """Test eventFilter for mouse button press away from resize area."""
    from PySide6.QtCore import QPoint, QPointF
    from PySide6.QtCore import Qt as QtCore
    from PySide6.QtGui import QMouseEvent

    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(100, 100),
        function.mapToGlobal(QPoint(100, 100)),
        QtCore.MouseButton.LeftButton,
        QtCore.MouseButton.LeftButton,
        QtCore.KeyboardModifier.NoModifier,
    )
    result = function.eventFilter(function, event)
    assert result is False


def test_eventFilter_mouse_button_press_with_edges(function):
    """Test eventFilter for mouse button press at resize area."""
    from PySide6.QtCore import QPoint, QPointF
    from PySide6.QtCore import Qt as QtCore
    from PySide6.QtGui import QMouseEvent

    # Create event at bottom-right corner
    corner_x = function.width() - 5
    corner_y = function.height() - 5

    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPointF(corner_x, corner_y),
        function.mapToGlobal(QPoint(corner_x, corner_y)),
        QtCore.MouseButton.LeftButton,
        QtCore.MouseButton.LeftButton,
        QtCore.KeyboardModifier.NoModifier,
    )

    # Mock windowHandle to avoid None issue in tests
    with mock.patch.object(function, "windowHandle") as mock_window:
        mock_window.return_value = mock.MagicMock()
        result = function.eventFilter(function, event)
        assert result is True


def test_wIcon_1(function):
    ui = QPushButton()
    function.wIcon(ui, "load")


def test_setPositionWindow_1(function):
    config = {"winPosX": 100, "winPosY": 100, "height": 400, "width": 600}
    function.setPositionWindow(config)


def test_setPositionWindow_2(function):
    config = {"height": 300, "width": 500}
    function.setPositionWindow(config)


@mock.patch("mw4.gui.utilities.qtMain.platform.system", return_value="Linux")
def test_positionWindow_linux_maximized(mock_platform, function):
    """Test setPositionWindow on Linux with maximized window dimensions."""
    max_height = function.maximumHeight()
    max_width = function.maximumWidth()
    config = {"height": max_height, "width": max_width}
    function.setPositionWindow(config)
    mock_platform.assert_called()


@mock.patch("mw4.gui.utilities.qtMain.platform.system", return_value="Darwin")
def test_positionWindow_macos_maximized(mock_platform, function):
    """Test setPositionWindow on macOS with maximized window dimensions."""
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


def test_setNoFocus_1(function):
    """Test setNoFocus sets NoFocus policy on all children."""
    parent_widget = QWidget()
    child1 = QPushButton(parent_widget)
    child2 = QPushButton(parent_widget)
    child1.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    child2.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    MWidget.setNoFocus(parent_widget)

    assert child1.focusPolicy() == Qt.FocusPolicy.NoFocus
    assert child2.focusPolicy() == Qt.FocusPolicy.NoFocus


def test_setNoFocus_2(function):
    """Test setNoFocus with nested children."""
    parent_widget = QWidget()
    child1 = QWidget(parent_widget)
    grandchild = QPushButton(child1)
    grandchild.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    MWidget.setNoFocus(parent_widget)

    assert grandchild.focusPolicy() == Qt.FocusPolicy.NoFocus
    assert child1.focusPolicy() == Qt.FocusPolicy.NoFocus
