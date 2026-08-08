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
from mw4.logic.keypad.keypad import KeyPad
from PySide6.QtCore import QObject, Signal
from unittest import mock
from websocket import WebSocketApp


@pytest.fixture(autouse=True, scope="module")
def keypad_signals():
    """Create mock signals for KeyPad instance."""

    class Signals(QObject):
        textRow = Signal(object, object)
        imgChunk = Signal(object, object, object)
        keyPressed = Signal(object)
        keyUp = Signal(object)
        keyDown = Signal(object)
        mousePressed = Signal(object)
        mouseReleased = Signal(object)
        cursorPos = Signal(object, object)
        clearCursor = Signal()

    return Signals()


@pytest.fixture
def keypad(keypad_signals):
    """Create a KeyPad instance for testing."""
    return KeyPad(signals=keypad_signals)


# Tests for expand7to8 method


def test_expand7to8_empty_list(keypad):
    """Test expand7to8 with empty input list."""
    result = keypad.expand7to8([], False)
    assert result == []


def test_expand7to8_no_fill(keypad):
    """Test expand7to8 with normal input without fill flag."""
    result = keypad.expand7to8([200, 100, 10, 34], False)
    assert result == [145, 144, 82]


def test_expand7to8_with_fill(keypad):
    """Test expand7to8 with normal input with fill flag enabled."""
    result = keypad.expand7to8([200, 100, 10, 34], True)
    assert result == [145, 144, 82, 32]


# Tests for convertChar method


def test_convertChar_unmapped_character(keypad):
    """Test convertChar with character not in translation map."""
    result = keypad.convertChar(150)
    assert result == 150


def test_convertChar_mapped_character(keypad):
    """Test convertChar with character that has translation mapping."""
    result = keypad.convertChar(223)
    assert result == 176


# Tests for dispText method


def test_dispText_processes_value(keypad):
    """Test dispText correctly processes and emits text row."""
    # dispText should execute without errors
    keypad.dispText([1, 1, 1, 1, 88])


# Tests for drawPixel method


def test_drawPixel_processes_pixel_data(keypad):
    """Test drawPixel correctly processes pixel data."""
    # drawPixel should execute without errors
    keypad.drawPixel([2, 1, 1, 40, 40, 40, 40, 40, 40, 40, 40])


# Tests for deletePixel method


def test_deletePixel_processes_pixel_data(keypad):
    """Test deletePixel correctly processes pixel deletion."""
    # deletePixel should execute without errors
    keypad.deletePixel([3, 1, 1, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40])


# Tests for dispatch method


def test_dispatch_empty_expanded_message(keypad):
    """Test dispatch with empty message after expansion."""
    with mock.patch.object(keypad, "expand7to8", return_value=[]):
        keypad.dispatch([])
        # Should return early without calling any handlers


def test_dispatch_type_1_text_row(keypad):
    """Test dispatch with message type 1 (text display)."""
    with (
        mock.patch.object(keypad, "expand7to8", return_value=[1, 1]),
        mock.patch.object(keypad, "dispText") as mock_disp,
    ):
        keypad.dispatch([1, 1])
        mock_disp.assert_called_once()


def test_dispatch_type_2_draw_pixel(keypad):
    """Test dispatch with message type 2 (draw pixel)."""
    with (
        mock.patch.object(keypad, "expand7to8", return_value=[2, 1]),
        mock.patch.object(keypad, "drawPixel") as mock_draw,
    ):
        keypad.dispatch([2, 1])
        mock_draw.assert_called_once()


def test_dispatch_type_3_delete_pixel(keypad):
    """Test dispatch with message type 3 (delete pixel)."""
    with (
        mock.patch.object(keypad, "expand7to8", return_value=[3, 1]),
        mock.patch.object(keypad, "deletePixel") as mock_delete,
    ):
        keypad.dispatch([3, 1])
        mock_delete.assert_called_once()


def test_dispatch_type_4_ignored(keypad):
    """Test dispatch with message type 4 (ignored)."""
    with mock.patch.object(keypad, "expand7to8", return_value=[4, 1]):
        keypad.dispatch([4, 1])
        # Type 4 is not handled, should pass silently


def test_dispatch_type_5_cursor_position(keypad):
    """Test dispatch with message type 5 (cursor position)."""
    with mock.patch.object(keypad, "expand7to8", return_value=[5, 1, 1]):
        keypad.dispatch([5, 1, 1])
        # Verify no exception raised


def test_dispatch_type_6_clear_cursor(keypad):
    """Test dispatch with message type 6 (clear cursor)."""
    with mock.patch.object(keypad, "expand7to8", return_value=[6]):
        keypad.dispatch([6])
        # Verify no exception raised


def test_dispatch_type_11_no_operation(keypad):
    """Test dispatch with message type 11 (no operation)."""
    with mock.patch.object(keypad, "expand7to8", return_value=[11, 1]):
        keypad.dispatch([11, 1])
        # Type 11 is not handled, should pass silently


def test_dispatch_type_12_no_operation(keypad):
    """Test dispatch with message type 12 (no operation)."""
    with mock.patch.object(keypad, "expand7to8", return_value=[12, 1]):
        keypad.dispatch([12, 1])
        # Type 12 is not handled, should pass silently


# Tests for checkDispatch method


def test_checkDispatch_with_valid_message_type_0(keypad):
    """Test checkDispatch with message type 0 calls dispatch."""
    with mock.patch.object(keypad, "dispatch") as mock_disp:
        keypad.checkDispatch([0, 100, 110, 120])
        mock_disp.assert_called_once()


# Tests for calcChecksum method


def test_calcChecksum_complex_message(keypad):
    """Test calcChecksum with complex message data."""
    msg = [
        2,
        0,
        128,
        192,
        160,
        145,
        130,
        201,
        130,
        160,
        144,
        140,
        166,
        134,
        193,
        196,
        226,
        237,
        152,
        141,
        165,
        227,
        203,
        204,
        192,
    ]
    result = keypad.calcChecksum(msg)
    assert result == 184


def test_calcChecksum_simple_message(keypad):
    """Test calcChecksum with simple message."""
    result = keypad.calcChecksum([2])
    assert result == 12


# Tests for send method


def test_send_with_none_websocket(keypad):
    """Test send when WebSocket is not initialized."""
    keypad.ws = None
    keypad.send([1, 2, 3])
    # Should return early without sending


def test_send_with_active_websocket(keypad):
    """Test send with active WebSocket connection."""

    class MockWS:
        def send(self, a, b):
            return

    keypad.ws = MockWS()  # type: ignore
    with mock.patch.object(keypad.ws, "send") as mock_send:
        keypad.send([1, 2, 3])
        mock_send.assert_called_once()


# Tests for mousePressed method


def test_mousePressed_valid_button(keypad):
    """Test mousePressed with valid button key."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.mousePressed("key_0")
        mock_send.assert_called_once()


def test_mousePressed_invalid_button(keypad):
    """Test mousePressed with invalid button key."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.mousePressed("invalid_key")
        mock_send.assert_not_called()


# Tests for mouseReleased method


def test_mouseReleased_valid_button(keypad):
    """Test mouseReleased with valid button key."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.mouseReleased("key_0")
        mock_send.assert_called_once()


def test_mouseReleased_invalid_button(keypad):
    """Test mouseReleased with invalid button key."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.mouseReleased("invalid_key")
        mock_send.assert_not_called()


# Tests for keyDown method


def test_keyDown_valid_key_code(keypad):
    """Test keyDown with valid key code."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.keyDown(48)
        mock_send.assert_called_once()


def test_keyDown_invalid_key_code(keypad):
    """Test keyDown with invalid key code."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.keyDown(0)
        mock_send.assert_not_called()


# Tests for keyUp method


def test_keyUp_valid_key_code(keypad):
    """Test keyUp with valid key code."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.keyUp(48)
        mock_send.assert_called_once()


def test_keyUp_invalid_key_code(keypad):
    """Test keyUp with invalid key code."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.keyUp(0)
        mock_send.assert_not_called()


# Tests for keyPressed method


def test_keyPressed_key_above_255_ignored(keypad):
    """Test keyPressed ignores keys above 255."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.keyPressed(1000)
        mock_send.assert_not_called()


def test_keyPressed_unmapped_character(keypad):
    """Test keyPressed with unmapped character."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.keyPressed(10)
        mock_send.assert_not_called()


def test_keyPressed_mapped_character(keypad):
    """Test keyPressed with valid mapped character."""
    with mock.patch.object(keypad, "send") as mock_send:
        keypad.keyPressed(54)  # ASCII code for '6'
        assert mock_send.call_count == 2  # keyDown and keyUp messages


# Tests for on_data method


def test_on_data_with_valid_message_frame(keypad):
    """Test on_data with valid message frame containing checksum."""
    data = [
        2,
        0,
        128,
        192,
        160,
        145,
        130,
        201,
        130,
        160,
        144,
        140,
        166,
        134,
        193,
        196,
        226,
        237,
        152,
        141,
        165,
        227,
        203,
        204,
        192,
        184,
        3,
    ]
    with mock.patch.object(keypad, "checkDispatch") as mock_disp:
        keypad.on_data(mock.Mock(), data, 0, False)  # type: ignore
        mock_disp.assert_called_once()


# Tests for on_close method


def test_on_close_clears_websocket(keypad):
    """Test on_close sets ws to None when connection closes."""
    keypad.ws = mock.Mock()  # type: ignore
    keypad.on_close(mock.Mock(), None, None)  # type: ignore
    assert keypad.ws is None


# Tests for workerWebsocket method


def test_workerWebsocket_already_connected_skips(keypad):
    """Test workerWebsocket skips if already connected."""
    keypad.ws = mock.Mock()
    with mock.patch.object(WebSocketApp, "__init__", return_value=None):
        keypad.workerWebsocket(host=("localhost", 8000))
        # Should skip creating new connection


def test_workerWebsocket_creates_new_connection(keypad):
    """Test workerWebsocket creates new WebSocket connection."""
    keypad.ws = None
    with mock.patch.object(WebSocketApp, "run_forever"):
        keypad.workerWebsocket(host=("localhost", 8000))
        assert keypad.ws is not None


# Tests for closeWebsocket method


def test_closeWebsocket_with_active_connection(keypad):
    """Test closeWebsocket closes active connection."""

    class MockWS:
        def close(self):
            pass

    keypad.ws = MockWS()  # type: ignore
    with mock.patch.object(keypad.ws, "close") as mock_close:
        keypad.closeWebsocket()
        mock_close.assert_called_once()


def test_closeWebsocket_with_no_connection(keypad):
    """Test closeWebsocket does nothing when no connection."""
    keypad.ws = None
    keypad.closeWebsocket()
    # Should not raise exception
