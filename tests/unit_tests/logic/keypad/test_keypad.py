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


def test_checkDispatch_1(function):
    valIn = [0, 100, 110, 120]
    with mock.patch.object(function,
                           'dispatch'):
        suc = function.checkDispatch(valIn)
        assert suc
