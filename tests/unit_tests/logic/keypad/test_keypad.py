############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal
from websocket import WebSocketApp

# local import
from logic.keypad.keypad import KeyPad


@pytest.fixture(autouse=True, scope='function')
def function():
    class Signals(QObject):
        textRow = pyqtSignal(object, object)
        imgChunk = pyqtSignal(object, object, object)
        keyPressed = pyqtSignal(object)
        cursorPos = pyqtSignal(object, object)

    window = KeyPad(signals=Signals())
    yield window


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


def test_dispatch_1(function):
    valIn = []
    suc = function.dispatch(valIn)
    assert not suc


def test_dispatch_2(function):
    msg = [1, 1, 1, 1, 88]
    with mock.patch.object(function,
                           'expand7to8',
                           return_value=msg):
        suc = function.dispatch(msg)
        assert suc


def test_dispatch_3(function):
    msg = [2, 1, 1, 40, 40, 40, 40, 40, 40, 40, 40]
    with mock.patch.object(function,
                           'expand7to8',
                           return_value=msg):
        suc = function.dispatch(msg)
        assert suc


def test_dispatch_4(function):
    msg = [3, 1, 1, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40]
    with mock.patch.object(function,
                           'expand7to8',
                           return_value=msg):
        suc = function.dispatch(msg)
        assert suc


def test_dispatch_5(function):
    msg = [4, 1]
    with mock.patch.object(function,
                           'expand7to8',
                           return_value=msg):
        suc = function.dispatch(msg)
        assert suc


def test_dispatch_6(function):
    msg = [5, 1, 1]
    with mock.patch.object(function,
                           'expand7to8',
                           return_value=msg):
        suc = function.dispatch(msg)
        assert suc


def test_dispatch_7(function):
    msg = [6, 1]
    with mock.patch.object(function,
                           'expand7to8',
                           return_value=msg):
        suc = function.dispatch(msg)
        assert suc


def test_dispatch_8(function):
    msg = [11, 1]
    with mock.patch.object(function,
                           'expand7to8',
                           return_value=msg):
        suc = function.dispatch(msg)
        assert suc


def test_dispatch_9(function):
    msg = [12, 1]
    with mock.patch.object(function,
                           'expand7to8',
                           return_value=msg):
        suc = function.dispatch(msg)
        assert suc


def test_checkDispatch_1(function):
    msg = [0, 100, 110, 120]
    with mock.patch.object(function,
                           'dispatch'):
        suc = function.checkDispatch(msg)
        assert suc


def test_calcChecksum_1(function):
    msg = [2, 0, 128, 192, 160, 145, 130, 201, 130, 160, 144, 140,
           166, 134, 193, 196,
           226, 237, 152, 141, 165, 227, 203, 204, 192]
    val = function.calcChecksum(msg)
    assert val == 184


def test_calcChecksum_2(function):
    msg = [2]
    val = function.calcChecksum(msg)
    assert val == 12


def test_mousePressed_1(function):
    class WS:
        def send(self, a, b):
            return
    function.ws = WS()
    suc = function.mousePressed(88)
    assert suc


def test_mouseReleased_1(function):
    class WS:
        def send(self, a, b):
            return
    function.ws = WS()
    suc = function.mouseReleased(88)
    assert suc


def test_keyPressed_1(function):
    with mock.patch.object(function,
                           'mousePressed'):
        with mock.patch.object(function,
                               'mouseReleased'):
            suc = function.keyPressed(88)
            assert suc


def test_on_data_1(function):
    data = [2, 0, 128, 192, 160, 145, 130, 201, 130, 160, 144, 140,
            166, 134, 193, 196,
            226, 237, 152, 141, 165, 227, 203, 204, 192, 184, 3]
    with mock.patch.object(function,
                           'checkDispatch'):
        suc = function.on_data(0, data, 0, 0)
        assert suc


def test_on_close(function):
    suc = function.on_close(0, 0, 0)
    assert suc


def test_workerWebsocket_1(function):
    suc = function.workerWebsocket(host=None)
    assert not suc


def test_workerWebsocket_2(function):
    suc = function.workerWebsocket(host='1234')
    assert not suc


def test_workerWebsocket_3(function):
    class WS:
        def send(self, a, b):
            return

    function.ws = WS()
    suc = function.workerWebsocket(host=('127.0.0.1', 8000))
    assert not suc


def test_workerWebsocket_4(function):
    with mock.patch.object(WebSocketApp,
                           'run_forever'):
        suc = function.workerWebsocket(host=('127.0.0.1', 8000))
        assert suc


def test_closeWebsocket(function):
    class WS:
        def close(self):
            return

    function.ws = WS()

    suc = function.closeWebsocket()
    assert suc