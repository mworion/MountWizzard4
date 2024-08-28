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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import astropy

# external packages
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QPushButton
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.keypadW import KeypadWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = KeypadWindow(app=App())
    with mock.patch.object(func,
                           'show'):
        yield func


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if 'keypadW' in function.app.config:
        del function.app.config['keypadW']

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config['keypadW'] = {}

    function.storeConfig()


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'storeConfig'):
        with mock.patch.object(function.keypad,
                               'closeWebsocket'):
            with mock.patch.object(function,
                                   'setupButtons'):
                with mock.patch.object(MWidget,
                                       'closeEvent'):
                    function.showWindow()
                    function.closeEvent(QCloseEvent)


def test_keyPressEvent_1(function):
    class KeyEvent:
        @staticmethod
        def key():
            return 0

        @staticmethod
        def type():
            return 6

    function.inputActive = True
    with mock.patch.object(MWidget,
                           'keyPressEvent'):
        function.keyPressEvent(KeyEvent())


def test_keyPressEvent_2(function):
    class KeyEvent:
        @staticmethod
        def key():
            return 0

        @staticmethod
        def type():
            return 6

    function.inputActive = False
    with mock.patch.object(MWidget,
                           'keyPressEvent'):
        function.keyPressEvent(KeyEvent())


def test_keyPressEvent_3(function):
    class KeyEvent:
        @staticmethod
        def key():
            return 16777216

        @staticmethod
        def type():
            return 6

    function.inputActive = False
    with mock.patch.object(MWidget,
                           'keyPressEvent'):
        function.keyPressEvent(KeyEvent())


def test_keyPressEvent_4(function):
    class KeyEvent:
        @staticmethod
        def key():
            return 16777220

        @staticmethod
        def type():
            return 6

    function.inputActive = False
    with mock.patch.object(MWidget,
                           'keyPressEvent'):
        function.keyPressEvent(KeyEvent())


def test_keyPressEvent_5(function):
    class KeyEvent:
        @staticmethod
        def key():
            return 16777249

        @staticmethod
        def type():
            return 6

    function.inputActive = False
    with mock.patch.object(MWidget,
                           'keyPressEvent'):
        function.keyPressEvent(KeyEvent())


def test_showWindow_1(function):
    function.app.mount.setting.webInterfaceStat = False
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(function,
                               'show'):
            with mock.patch.object(function,
                                   'setupButtons'):
                with mock.patch.object(function,
                                       'startKeypad'):
                    with mock.patch.object(function.app.mount.setting,
                                           'setWebInterface',
                                           return_value=False):
                        function.showWindow()


def test_colorChange(function):
    with mock.patch.object(function,
                           'clearGraphics'):
        function.colorChange()


def test_setupButtons_1(function):
    function.setupButtons()


def test_websocketClear(function):
    function.websocketMutex.lock()
    function.websocketClear()


def test_startKeypad_1(function):
    function.websocketMutex.lock()
    suc = function.startKeypad()
    assert not suc
    function.websocketMutex.unlock()


def test_startKeypad_2(function):
    with mock.patch.object(function,
                           'clearDisplay'):
        with mock.patch.object(function,
                               'writeTextRow'):
            with mock.patch.object(function.threadPool,
                                   'start'):
                suc = function.startKeypad()
                assert suc
                function.websocketMutex.unlock()


def test_hostChanged_1(function):
    with mock.patch.object(function.keypad,
                           'closeWebsocket'):
        with mock.patch.object(function,
                               'startKeypad'):
            function.hostChanged()


def test_buttonPressed_1(function):
    def sender():
        return QPushButton()

    function.setupButtons()
    function.sender = sender
    suc = function.buttonPressed()
    assert not suc


def test_buttonPressed_2(function):
    def sender():
        return function.ui.b0

    function.setupButtons()
    function.sender = sender
    with mock.patch.object(function.keypad,
                           'send'):
        suc = function.buttonPressed()
        assert suc


def test_buttonReleased_1(function):
    def sender():
        return QPushButton()

    function.setupButtons()
    function.sender = sender
    suc = function.buttonReleased()
    assert not suc


def test_buttonReleased_2(function):
    def sender():
        return function.ui.b0
    function.setupButtons()
    function.sender = sender
    with mock.patch.object(function.keypad,
                           'send'):
        suc = function.buttonReleased()
        assert suc


def test_writeTextRow_1(function):
    suc = function.writeTextRow(-1, '')
    assert not suc


def test_writeTextRow_2(function):
    suc = function.writeTextRow(1, '>')
    assert suc


def test_writeTextRow_3(function):
    suc = function.writeTextRow(1, 'fsjgfdjhsfg')
    assert suc


def test_writeTextRow_4(function):
    with mock.patch.object(function,
                           'clearGraphics'):
        suc = function.writeTextRow(4, 'fsjgfdjhsfg')
        assert suc


def test_clearGraphics(function):
    with mock.patch.object(function,
                           'drawGraphics'):
        function.clearGraphics()


def test_clearDisplay(function):
    with mock.patch.object(function,
                           'clearGraphics'):
        function.clearDisplay()


def test_clearCursor(function):
    function.inputActive = True
    function.clearCursor()
    assert not function.inputActive


def test_setCursorPos(function):
    function.setCursorPos(1, 1)


def test_drawGraphics(function):
    function.drawGraphics()


def test_buildGraphics(function):
    arr = np.zeros([64, 128, 3], dtype=np.uint8)
    function.buildGraphics(arr, 0, 0)


