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
from mw4.logic.keypad.keypad import KeyPad
from PySide6.QtCore import QObject, Signal
from unittest import mock
from websocket import WebSocketApp


@pytest.fixture(autouse=True, scope="function")
def function():
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

    func = KeyPad(signals=Signals())
    yield func


def test_expand7to8_1(function):
    valIn = []
    val = function.expand7to8(valIn, False)
    assert val == []


def test_expand7to8_2(function):
    valIn = [200, 100, 10, 34]
    val = function.expand7to8(valIn, False)
    assert val == [145, 144, 82]


def test_expand7to8_3(function):
    valIn = [200, 100, 10, 34]
    val = function.expand7to8(valIn, True)
    assert val == [145, 144, 82, 32]


def test_convertChar_1(function):
    val = function.convertChar(150)
    assert val == 150


def test_convertChar_2(function):
    val = function.convertChar(223)
    assert val == 176


def test_dispText(function):
    value = [1, 1, 1, 1, 88]
    function.dispText(value)


def test_drawPixel(function):
    value = [2, 1, 1, 40, 40, 40, 40, 40, 40, 40, 40]
    function.drawPixel(value)


def test_deletePixel(function):
    value = [3, 1, 1, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40]
    function.deletePixel(value)


def test_dispatch_0(function):
    msg = []
    with mock.patch.object(function, "expand7to8", return_value=msg):
        function.dispatch(msg)


def test_dispatch_1(function):
    msg = [1, 1]
    with mock.patch.object(function, "expand7to8", return_value=msg):
        with mock.patch.object(function, "dispText"):
            function.dispatch(msg)


def test_dispatch_2(function):
    msg = [2, 1]
    with mock.patch.object(function, "expand7to8", return_value=msg):
        with mock.patch.object(function, "drawPixel"):
            function.dispatch(msg)


def test_dispatch_3(function):
    msg = [3, 1]
    with mock.patch.object(function, "expand7to8", return_value=msg):
        with mock.patch.object(function, "deletePixel"):
            function.dispatch(msg)


def test_dispatch_5(function):
    msg = [4, 1]
    with mock.patch.object(function, "expand7to8", return_value=msg):
        function.dispatch(msg)


def test_dispatch_6(function):
    msg = [5, 1, 1]
    with mock.patch.object(function, "expand7to8", return_value=msg):
        function.dispatch(msg)


def test_dispatch_7(function):
    msg = [6, 1]
    with mock.patch.object(function, "expand7to8", return_value=msg):
        function.dispatch(msg)


def test_dispatch_8(function):
    msg = [11, 1]
    with mock.patch.object(function, "expand7to8", return_value=msg):
        function.dispatch(msg)


def test_dispatch_9(function):
    msg = [12, 1]
    with mock.patch.object(function, "expand7to8", return_value=msg):
        function.dispatch(msg)


def test_checkDispatch_1(function):
    msg = [0, 100, 110, 120]
    with mock.patch.object(function, "dispatch"):
        function.checkDispatch(msg)


def test_calcChecksum_1(function):
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
    val = function.calcChecksum(msg)
    assert val == 184


def test_calcChecksum_2(function):
    msg = [2]
    val = function.calcChecksum(msg)
    assert val == 12


def test_send_1(function):
    function.ws = None
    function.send([1, 2, 3])


def test_send_2(function):
    class WS:
        @staticmethod
        def send(a, b):
            return

    function.ws = WS
    function.send("test")


def test_mousePressed_1(function):
    with mock.patch.object(function, "send"):
        function.mousePressed("key_0")


def test_mousePressed_2(function):
    with mock.patch.object(function, "send"):
        function.mousePressed("test")


def test_mouseReleased_1(function):
    with mock.patch.object(function, "send"):
        function.mouseReleased("key_0")


def test_mouseReleased_2(function):
    with mock.patch.object(function, "send"):
        function.mouseReleased("test")


def test_keyDown_1(function):
    with mock.patch.object(function, "send"):
        function.keyDown(48)


def test_keyDown_2(function):
    with mock.patch.object(function, "send"):
        function.keyDown(0)


def test_keyUp_1(function):
    with mock.patch.object(function, "send"):
        function.keyUp(48)


def test_keyUp_2(function):
    with mock.patch.object(function, "send"):
        function.keyUp(0)


def test_keyPressed_1(function):
    function.keyPressed(1000)


def test_keyPressed_2(function):
    function.keyPressed(10)


def test_keyPressed_3(function):
    with mock.patch.object(function, "send"):
        with mock.patch.object(function, "calcChecksum"):
            function.keyPressed(54)


def test_on_data_1(function):
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
    with mock.patch.object(function, "checkDispatch"):
        function.on_data(0, data, 0, 0)


def test_on_close(function):
    function.on_close(0, 0, 0)


def test_workerWebsocket_2(function):
    function.workerWebsocket(host="1234")


def test_workerWebsocket_3(function):
    class WS:
        def send(self, a, b):
            return

    function.ws = WS()
    function.workerWebsocket(host=("localhost", 8000))


def test_workerWebsocket_4(function):
    with mock.patch.object(WebSocketApp, "run_forever"):
        function.workerWebsocket(host=("localhost", 8000))


def test_closeWebsocket(function):
    class WS:
        def close(self):
            return

    function.ws = WS()

    function.closeWebsocket()
