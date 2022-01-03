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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import os
import socket

# external packages
import wakeonlan
from PyQt5.QtCore import QThreadPool, QTimer

# local imports
from indibase.indiBase import INDISignals
from indibase.qtIndiBase import Client


@pytest.fixture(autouse=True, scope='function')
def function():
    client = Client(host='127.0.0.1')
    yield client


def test_qtClient_1():
    test = Client(host='127.0.0.1')
    del test


def test_qtClient_2():
    test = Client(host='127.0.0.1', threadPool=QThreadPool())
    del test


def test_indiBaseSignals(function):
    INDISignals()


def test_checkServerUp_1(function):
    with mock.patch.object(socket.socket,
                           'connect',
                           side_effect=Exception):
        with mock.patch.object(socket.socket,
                               'shutdown'):
            with mock.patch.object(socket.socket,
                                   'close'):
                suc = function.checkServerUp()
                assert not suc


def test_checkServerUp_2(function):
    with mock.patch.object(socket.socket,
                           'connect'):
        with mock.patch.object(socket.socket,
                               'shutdown'):
            with mock.patch.object(socket.socket,
                                   'close'):
                suc = function.checkServerUp()
                assert suc


def test_checkServerUpResult_1(function):
    function.connected = False
    with mock.patch.object(function,
                           'connectServer',
                           return_value=False):
        suc = function.checkServerUpResult(True)
        assert not suc


def test_checkServerUpResult_2(function):
    function.connected = False
    with mock.patch.object(function,
                           'connectServer',
                           return_value=True):
        suc = function.checkServerUpResult(True)
        assert suc


def test_checkServerUpResult_3(function):
    function.connected = True
    with mock.patch.object(function,
                           'connectServer',
                           return_value=True):
        suc = function.checkServerUpResult(True)
        assert not suc


def test_checkServerUpResult_4(function):
    function.connected = False
    with mock.patch.object(function,
                           'connectServer',
                           return_value=True):
        suc = function.checkServerUpResult(False)
        assert not suc


def test_errorCycleCheckServerUp(function):
    suc = function.errorCycleCheckServerUp('test')
    assert suc

def test_clearCycleCheckServerUp_1(function):
    function.mutexServerUp.lock()
    suc = function.clearCycleCheckServerUp()
    assert suc


def test_cycleCheckServerUp_1(function):
    function.host = ()
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleCheckServerUp()
        assert not suc


def test_cycleCheckServerUp_2(function):
    function.host = ('localhost', 80)
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleCheckServerUp()
        assert suc
        function.mutexServerUp.unlock()


def test_cycleCheckServerUp_3(function):
    function.host = ('localhost', 80)
    function.mutexServerUp.lock()
    with mock.patch.object(QThreadPool,
                           'start'):
        suc = function.cycleCheckServerUp()
        function.mutexServerUp.unlock()
        assert not suc


def test_startTimers(function):
    with mock.patch.object(QTimer,
                           'start'):
        suc = function.startTimers()
        assert suc


def test_stopTimers(function):
    with mock.patch.object(QTimer,
                           'stop'):
        with mock.patch.object(QThreadPool,
                               'waitForDone'):
            suc = function.stopTimers()
            assert suc
