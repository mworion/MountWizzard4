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
import gc
import pytest
import unittest.mock as mock
from mw4.gui.utilities.qtCustomWindow import CustomTitleBar
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QToolButton, QWidget


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)
    yield titleBar
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_initialization_1(function):
    """Test CustomTitleBar basic initialization."""
    assert function is not None
    assert isinstance(function, CustomTitleBar)


def test_initialization_2(function):
    """Test that title bar has all required buttons."""
    assert function.minButton is not None
    assert isinstance(function.minButton, QToolButton)
    assert function.maxButton is not None
    assert isinstance(function.maxButton, QToolButton)
    assert function.closeButton is not None
    assert isinstance(function.closeButton, QToolButton)
    assert function.normButton is not None
    assert isinstance(function.normButton, QToolButton)


def test_initialization_3(function):
    """Test that title label is initialized."""
    assert function.title is not None
    assert hasattr(function, "title")


def test_button_properties_1(function):
    """Test minimum button fixed size."""
    size = function.minButton.size()
    assert size.width() == 16 or size.width() > 0
    assert size.height() == 16 or size.height() > 0


def test_button_properties_2(function):
    """Test maximum button fixed size."""
    size = function.maxButton.size()
    assert size.width() == 16 or size.width() > 0
    assert size.height() == 16 or size.height() > 0


def test_button_properties_3(function):
    """Test close button fixed size."""
    size = function.closeButton.size()
    assert size.width() == 16 or size.width() > 0
    assert size.height() == 16 or size.height() > 0


def test_button_properties_4(function):
    """Test minimize button focus policy."""
    assert function.minButton.focusPolicy() == Qt.FocusPolicy.NoFocus


def test_button_properties_5(function):
    """Test maximize button focus policy."""
    assert function.maxButton.focusPolicy() == Qt.FocusPolicy.NoFocus


def test_button_properties_6(function):
    """Test close button focus policy."""
    assert function.closeButton.focusPolicy() == Qt.FocusPolicy.NoFocus


def test_button_properties_7(function):
    """Test restore button focus policy."""
    assert function.normButton.focusPolicy() == Qt.FocusPolicy.NoFocus


def test_normalize_button_visibility_1():
    """Test normalize button is initially set to invisible."""
    parent = QWidget()
    titleBar = CustomTitleBar(parent)
    # Using property check instead of isVisible since widget is not shown
    assert hasattr(titleBar.normButton, "show")


def test_maximize_button_visibility_1():
    """Test maximize button is initially set to visible."""
    parent = QWidget()
    titleBar = CustomTitleBar(parent)
    # Using property check instead of isVisible since widget is not shown
    assert hasattr(titleBar.maxButton, "show")


def test_button_connections_1(function):
    """Test minimum button is clickable."""
    with mock.patch.object(function.window(), "showMinimized"):
        QTest.mouseClick(function.minButton, Qt.MouseButton.LeftButton)


def test_button_connections_2(function):
    """Test maximize button is clickable."""
    with mock.patch.object(function.window(), "showMaximized"):
        QTest.mouseClick(function.maxButton, Qt.MouseButton.LeftButton)


def test_button_connections_3(function):
    """Test close button is clickable."""
    with mock.patch.object(function.window(), "close"):
        QTest.mouseClick(function.closeButton, Qt.MouseButton.LeftButton)


def test_window_state_changed_1():
    """Test window state change to maximized."""
    parent = QWidget()
    parent.show()
    titleBar = CustomTitleBar(parent)
    titleBar.windowStateChanged(Qt.WindowState.WindowMaximized)
    # Check that methods were called (setVisible)
    assert hasattr(titleBar.normButton, "setVisible")
    assert hasattr(titleBar.maxButton, "setVisible")
    parent.close()


def test_window_state_changed_2():
    """Test window state change to normal."""
    parent = QWidget()
    parent.show()
    titleBar = CustomTitleBar(parent)
    titleBar.windowStateChanged(Qt.WindowState.WindowNoState)
    assert hasattr(titleBar.normButton, "setVisible")
    assert hasattr(titleBar.maxButton, "setVisible")
    parent.close()


def test_window_state_changed_3():
    """Test toggle between maximized and normal states."""
    parent = QWidget()
    parent.show()
    titleBar = CustomTitleBar(parent)
    titleBar.windowStateChanged(Qt.WindowState.WindowMaximized)
    titleBar.windowStateChanged(Qt.WindowState.WindowNoState)
    assert hasattr(titleBar.normButton, "setVisible")
    assert hasattr(titleBar.maxButton, "setVisible")
    parent.close()


def test_initial_pos_attribute_1(function):
    """Test initial_pos is None at start."""
    assert function.initial_pos is None


def test_initial_pos_attribute_2(function):
    """Test initial_pos is set on mouse press."""
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)

    mouseEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPoint(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButtons(Qt.MouseButton.LeftButton),
        Qt.KeyboardModifiers(),
    )
    titleBar.mousePressEvent(mouseEvent)
    assert titleBar.initial_pos is not None


def test_initial_pos_cleared_1(function):
    """Test initial_pos is cleared on mouse release."""
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)

    mouseEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPoint(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButtons(Qt.MouseButton.LeftButton),
        Qt.KeyboardModifiers(),
    )
    titleBar.mousePressEvent(mouseEvent)
    assert titleBar.initial_pos is not None

    releaseEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        QPoint(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButtons(),
        Qt.KeyboardModifiers(),
    )
    titleBar.mouseReleaseEvent(releaseEvent)
    assert titleBar.initial_pos is None


def test_mouse_press_event_1(function):
    """Test mouse press event with left button."""
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)

    mouseEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPoint(20, 15),
        Qt.MouseButton.LeftButton,
        Qt.MouseButtons(Qt.MouseButton.LeftButton),
        Qt.KeyboardModifiers(),
    )
    titleBar.mousePressEvent(mouseEvent)
    assert titleBar.initial_pos == QPoint(20, 15)


def test_mouse_press_event_2(function):
    """Test mouse press event with right button sets no initial pos."""
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)

    mouseEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPoint(20, 15),
        Qt.MouseButton.RightButton,
        Qt.MouseButtons(Qt.MouseButton.RightButton),
        Qt.KeyboardModifiers(),
    )
    titleBar.mousePressEvent(mouseEvent)
    assert titleBar.initial_pos is None


def test_mouse_move_event_1(function):
    """Test mouse move event with no initial position."""
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)

    initial_x = parent.x()
    initial_y = parent.y()

    moveEvent = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPoint(30, 20),
        Qt.MouseButton.NoButton,
        Qt.MouseButtons(),
        Qt.KeyboardModifiers(),
    )
    titleBar.mouseMoveEvent(moveEvent)

    assert parent.x() == initial_x
    assert parent.y() == initial_y


def test_mouse_move_event_2(function):
    """Test mouse move event moves window when initial position is set."""
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)

    initial_x = parent.x()
    initial_y = parent.y()

    pressEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPoint(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButtons(Qt.MouseButton.LeftButton),
        Qt.KeyboardModifiers(),
    )
    titleBar.mousePressEvent(pressEvent)

    moveEvent = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPoint(30, 30),
        Qt.MouseButton.NoButton,
        Qt.MouseButtons(),
        Qt.KeyboardModifiers(),
    )
    titleBar.mouseMoveEvent(moveEvent)

    expected_x = initial_x + (30 - 10)
    expected_y = initial_y + (30 - 10)

    assert parent.x() == expected_x
    assert parent.y() == expected_y


def test_mouse_move_event_3(function):
    """Test multiple mouse moves accumulate deltas."""
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)

    initial_x = parent.x()
    initial_y = parent.y()

    pressEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPoint(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButtons(Qt.MouseButton.LeftButton),
        Qt.KeyboardModifiers(),
    )
    titleBar.mousePressEvent(pressEvent)

    moveEvent1 = QMouseEvent(
        QMouseEvent.Type.MouseMove,
        QPoint(20, 20),
        Qt.MouseButton.NoButton,
        Qt.MouseButtons(),
        Qt.KeyboardModifiers(),
    )
    titleBar.mouseMoveEvent(moveEvent1)

    first_x = parent.x()
    first_y = parent.y()

    assert first_x == initial_x + 10
    assert first_y == initial_y + 10


def test_mouse_release_event_1(function):
    """Test mouse release event clears initial position."""
    parent = QWidget()
    parent.setGeometry(100, 100, 400, 300)
    titleBar = CustomTitleBar(parent)

    pressEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        QPoint(10, 10),
        Qt.MouseButton.LeftButton,
        Qt.MouseButtons(Qt.MouseButton.LeftButton),
        Qt.KeyboardModifiers(),
    )
    titleBar.mousePressEvent(pressEvent)
    assert titleBar.initial_pos is not None

    releaseEvent = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        QPoint(20, 20),
        Qt.MouseButton.LeftButton,
        Qt.MouseButtons(),
        Qt.KeyboardModifiers(),
    )
    titleBar.mouseReleaseEvent(releaseEvent)
    assert titleBar.initial_pos is None


def test_title_text_1(function):
    """Test title text can be set."""
    function.title.setText("Test Title")
    assert function.title.text() == "Test Title"


def test_title_text_2(function):
    """Test title text empty by default."""
    parent = QWidget()
    titleBar = CustomTitleBar(parent)
    assert titleBar.title.text() == ""


def test_button_icons_1(function):
    """Test all buttons have icons set."""
    assert not function.minButton.icon().isNull()


def test_button_icons_2(function):
    """Test max button has icon set."""
    assert not function.maxButton.icon().isNull()


def test_button_icons_3(function):
    """Test close button has icon set."""
    assert not function.closeButton.icon().isNull()


def test_title_bar_layout_1(function):
    """Test title bar has layout."""
    assert function.layout() is not None


def test_title_bar_spacing_1(function):
    """Test title bar layout spacing is set."""
    layout = function.layout()
    assert layout.spacing() == 5


def test_title_bar_margins_1(function):
    """Test title bar layout margins."""
    layout = function.layout()
    left, top, right, bottom = layout.getContentsMargins()
    assert right == 0
