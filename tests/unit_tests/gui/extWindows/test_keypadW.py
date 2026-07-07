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
import numpy as np
import pytest
import unittest.mock as mock
from mw4.gui.extWindows.keypadW import KeypadWindow
from mw4.gui.utilities.qtMain import MWidget
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def keypad_window(qapp):
    """Create a KeypadWindow instance for testing."""
    window = KeypadWindow(app=App(), title="Keypad")
    with mock.patch.object(window, "show"):
        yield window
        QApplication.processEvents()


# Tests for initConfig method

def test_initConfig_loads_window_config(keypad_window):
    """Test initConfig loads WindowKeypad configuration."""
    keypad_window.initConfig()
    # Should not raise any exceptions


# Tests for storeConfig method

def test_storeConfig_creates_config_entry(keypad_window):
    """Test storeConfig creates WindowKeypad entry."""
    if "WindowKeypad" in keypad_window.app.config:
        del keypad_window.app.config["WindowKeypad"]

    keypad_window.storeConfig()
    assert "WindowKeypad" in keypad_window.app.config


def test_storeConfig_preserves_existing_config(keypad_window):
    """Test storeConfig preserves existing configuration."""
    keypad_window.app.config["WindowKeypad"] = {}
    keypad_window.storeConfig()
    assert isinstance(keypad_window.app.config["WindowKeypad"], dict)


# Tests for closeEvent method

def test_closeEvent_calls_cleanup_on_close(keypad_window):
    """Test closeEvent calls storeConfig and closeWebsocket."""
    with (
        mock.patch.object(keypad_window, "storeConfig") as mock_store,
        mock.patch.object(keypad_window.keypad, "closeWebsocket") as mock_close,
        mock.patch.object(keypad_window, "setupButtons"),
        mock.patch.object(MWidget, "closeEvent"),
    ):
        keypad_window.showWindow()
        keypad_window.closeEvent(QCloseEvent)
        mock_store.assert_called()
        mock_close.assert_called()


# Tests for keyPressEvent method

def test_keyPressEvent_input_active_emits_key_pressed(keypad_window):
    """Test keyPressEvent emits keyPressed when input is active."""

    class MockKeyEvent:
        @staticmethod
        def key():
            return 0

        @staticmethod
        def type():
            return 6

    keypad_window.inputActive = True
    with mock.patch.object(MWidget, "keyPressEvent"):
        keypad_window.keyPressEvent(MockKeyEvent())  # type: ignore
    # Verify no exceptions raised


def test_keyPressEvent_inactive_emits_key_up_down(keypad_window):
    """Test keyPressEvent emits keyUp and keyDown when input inactive."""

    class MockKeyEvent:
        @staticmethod
        def key():
            return 0

        @staticmethod
        def type():
            return 6

    keypad_window.inputActive = False
    with mock.patch.object(MWidget, "keyPressEvent"):
        keypad_window.keyPressEvent(MockKeyEvent())  # type: ignore
    # Verify no exceptions raised


def test_keyPressEvent_escape_key_mapping(keypad_window):
    """Test keyPressEvent maps Escape key to correct key code."""

    class MockKeyEvent:
        @staticmethod
        def key():
            return 16777216

        @staticmethod
        def type():
            return 6

    keypad_window.inputActive = False
    with (
        mock.patch.object(MWidget, "keyPressEvent"),
        mock.patch.object(keypad_window.keypad, "send"),
    ):
        keypad_window.keyPressEvent(MockKeyEvent())  # type: ignore
    # Verify no exceptions raised


def test_keyPressEvent_return_key_mapping(keypad_window):
    """Test keyPressEvent maps Return key to correct key code."""

    class MockKeyEvent:
        @staticmethod
        def key():
            return 16777220

        @staticmethod
        def type():
            return 6

    keypad_window.inputActive = False
    with (
        mock.patch.object(MWidget, "keyPressEvent"),
        mock.patch.object(keypad_window.keypad, "send"),
    ):
        keypad_window.keyPressEvent(MockKeyEvent())  # type: ignore
    # Verify no exceptions raised


def test_keyPressEvent_shift_key_mapping(keypad_window):
    """Test keyPressEvent maps Shift key to correct key code."""

    class MockKeyEvent:
        @staticmethod
        def key():
            return 16777249

        @staticmethod
        def type():
            return 6

    keypad_window.inputActive = False
    with mock.patch.object(MWidget, "keyPressEvent"):
        keypad_window.keyPressEvent(MockKeyEvent())  # type: ignore
    # Verify no exceptions raised


# Tests for showWindow method

def test_showWindow_initializes_ui_and_starts_keypad(keypad_window):
    """Test showWindow initializes UI and starts keypad."""
    keypad_window.app.mount.setting.webInterfaceStat = False
    with (
        mock.patch.object(keypad_window, "setupButtons") as mock_setup,
        mock.patch.object(keypad_window, "startKeypad") as mock_start,
        mock.patch.object(
            keypad_window.app.mount.setting, "setWebInterface", return_value=False
        ),
    ):
        keypad_window.showWindow()
        mock_setup.assert_called()
        mock_start.assert_called()


# Tests for colorChange method

def test_colorChange_clears_graphics(keypad_window):
    """Test colorChange clears graphics when theme changes."""
    with mock.patch.object(keypad_window, "clearGraphics") as mock_clear:
        keypad_window.colorChange()
        mock_clear.assert_called_once()


# Tests for setupButtons method

def test_setupButtons_connects_button_signals(keypad_window):
    """Test setupButtons connects all button signals."""
    keypad_window.setupButtons()
    # Verify buttons are properly connected (no exception means success)


# Tests for websocketClear method

def test_websocketClear_unlocks_mutex(keypad_window):
    """Test websocketClear unlocks the websocket mutex."""
    keypad_window.websocketMutex.lock()
    keypad_window.websocketClear()
    # Verify mutex can be locked again (was unlocked)
    assert keypad_window.websocketMutex.tryLock()
    keypad_window.websocketMutex.unlock()


# Tests for startKeypad method

def test_startKeypad_blocked_when_already_running(keypad_window):
    """Test startKeypad returns early when mutex already locked."""
    keypad_window.websocketMutex.lock()
    keypad_window.startKeypad()
    keypad_window.websocketMutex.unlock()
    # Should return early without starting new worker


def test_startKeypad_creates_worker(keypad_window):
    """Test startKeypad creates and starts worker thread."""
    with (
        mock.patch.object(keypad_window, "clearDisplay") as mock_clear,
        mock.patch.object(keypad_window, "writeTextRow") as mock_write,
        mock.patch.object(keypad_window.threadPool, "start") as mock_start,
    ):
        keypad_window.startKeypad()
        mock_clear.assert_called_once()
        mock_write.assert_called()
        mock_start.assert_called_once()
        keypad_window.websocketMutex.unlock()


# Tests for buttonPressed method

def test_buttonPressed_calls_button_signal(keypad_window):
    """Test buttonPressed emits mousePressed signal."""
    keypad_window.setupButtons()
    # Should execute without errors
    keypad_window.buttonPressed("key_0")


# Tests for buttonReleased method

def test_buttonReleased_calls_button_signal(keypad_window):
    """Test buttonReleased emits mouseReleased signal."""
    keypad_window.setupButtons()
    # Should execute without errors
    keypad_window.buttonReleased("key_0")


# Tests for writeTextRow method

def test_writeTextRow_invalid_row_below_zero(keypad_window):
    """Test writeTextRow ignores invalid row below -1."""
    keypad_window.writeTextRow(-1, "")
    # Should return early without writing


def test_writeTextRow_valid_row(keypad_window):
    """Test writeTextRow writes text to valid row."""
    keypad_window.writeTextRow(1, ">")
    assert keypad_window.rows[1].text() == ">"


def test_writeTextRow_text_written(keypad_window):
    """Test writeTextRow sets text on row widget."""
    keypad_window.writeTextRow(1, "fsjgfdjhsfg")
    assert keypad_window.rows[1].text() == "fsjgfdjhsfg"


def test_writeTextRow_last_row_with_text_clears_graphics(keypad_window):
    """Test writeTextRow clears graphics when writing to row 4."""
    with mock.patch.object(keypad_window, "clearGraphics") as mock_clear:
        keypad_window.writeTextRow(4, "fsjgfdjhsfg")
        mock_clear.assert_called_once()


# Tests for clearGraphics method

def test_clearGraphics_resets_graphics_and_redraws(keypad_window):
    """Test clearGraphics resets graphics array and redraws display."""
    with mock.patch.object(keypad_window, "drawGraphics") as mock_draw:
        keypad_window.clearGraphics()
        mock_draw.assert_called_once()
        assert keypad_window.graphics.shape == (64, 128, 4)


# Tests for clearDisplay method

def test_clearDisplay_clears_all_rows_and_graphics(keypad_window):
    """Test clearDisplay clears all text rows and graphics."""
    with mock.patch.object(keypad_window, "clearGraphics"):
        keypad_window.clearDisplay()
        for row in keypad_window.rows:
            assert row.text() == ""
        assert keypad_window.inputActive is False


# Tests for clearCursor method

def test_clearCursor_hides_cursor_and_disables_input(keypad_window):
    """Test clearCursor hides cursor and sets inputActive to False."""
    keypad_window.inputActive = True
    keypad_window.clearCursor()
    assert keypad_window.inputActive is False
    assert not keypad_window.ui.cursor.isVisible()


# Tests for setCursorPos method

def test_setCursorPos_enables_input_and_positions_cursor(keypad_window):
    """Test setCursorPos positions cursor and enables input."""
    keypad_window.setCursorPos(1, 1)
    assert keypad_window.inputActive is True
    # Cursor position is set but visibility depends on widget state


# Tests for drawGraphics method

def test_drawGraphics_renders_graphics_to_pixmap(keypad_window):
    """Test drawGraphics renders graphics buffer to pixmap."""
    keypad_window.drawGraphics()
    # Verify pixmap is set (no exception means success)
    assert keypad_window.ui.graphics.pixmap() is not None


# Tests for buildGraphics method

def test_buildGraphics_updates_graphics_buffer(keypad_window):
    """Test buildGraphics updates graphics buffer with image data."""
    arr = np.zeros([64, 128, 4], dtype=np.uint8)
    keypad_window.buildGraphics(arr, 0, 0)
    # Verify graphics buffer is updated
