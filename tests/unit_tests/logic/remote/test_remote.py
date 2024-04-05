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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QObject
from PyQt5 import QtNetwork
from PyQt5.QtCore import pyqtSignal

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.remote.remote import Remote


@pytest.fixture(autouse=True, scope='function')
def function():
    func = Remote(app=App())
    yield func


def test_startCommunication_1(function):
    with mock.patch.object(QtNetwork.QTcpServer,
                           'listen',
                           return_value=True):
        suc = function.startCommunication()
        assert suc


def test_startCommunication_2(function):
    with mock.patch.object(QtNetwork.QTcpServer,
                           'listen',
                           return_value=False):
        suc = function.startCommunication()
        assert not suc


def test_stopCommunication_1(function):
    function.tcpServer = QtNetwork.QTcpServer()
    with mock.patch.object(function.tcpServer,
                           'listen',
                           return_value=True):
        with mock.patch.object(function.tcpServer,
                               'close',
                               return_value=True):
            suc = function.stopCommunication()
            assert suc


def test_addConnection_1(function):
    function.tcpServer = None
    suc = function.addConnection()
    assert not suc


def test_addConnection_2(function):
    function.tcpServer = QtNetwork.QTcpServer(function)
    with mock.patch.object(function.tcpServer,
                           'nextPendingConnection',
                           return_value=0):
        suc = function.addConnection()
        assert not suc


def test_addConnection_3(function):
    class Test(QObject):
        nextBlockSize = 0
        readyRead = pyqtSignal()
        disconnected = pyqtSignal()
        error = pyqtSignal()

        @staticmethod
        def peerAddress():
            return Test()

        @staticmethod
        def toString():
            return 'Test'
    function.tcpServer = QtNetwork.QTcpServer(function)
    with mock.patch.object(function.tcpServer,
                           'nextPendingConnection',
                           return_value=Test()):
        suc = function.addConnection()
        assert suc


def test_receiveMessage_1(function):
    class Test():
        @staticmethod
        def bytesAvailable():
            return 0

    function.clientConnection = Test()
    suc = function.receiveMessage()
    assert not suc


def test_receiveMessage_2(function):
    class Test():
        @staticmethod
        def bytesAvailable():
            return 1

        @staticmethod
        def peerAddress():
            return Test()

        @staticmethod
        def toString():
            return 'Test'

        @staticmethod
        def read(a):
            return 'Test'.encode('ascii')

    function.clientConnection = Test()
    suc = function.receiveMessage()
    assert suc


def test_receiveMessage_3(function):
    class Test():
        @staticmethod
        def bytesAvailable():
            return 1

        @staticmethod
        def peerAddress():
            return Test()

        @staticmethod
        def toString():
            return 'Test'

        @staticmethod
        def read(a):
            return 'shutdown'.encode('ascii')

    function.clientConnection = Test()
    suc = function.receiveMessage()
    assert suc


def test_removeConnection_1(function):
    class Test():
        @staticmethod
        def peerAddress():
            return Test()

        @staticmethod
        def toString():
            return 'Test'

        @staticmethod
        def close():
            return

    function.clientConnection = Test()
    suc = function.removeConnection()
    assert suc


def test_handleError_1(function):
    class Test():
        @staticmethod
        def peerAddress():
            return Test()

        @staticmethod
        def toString():
            return 'Test'

    function.clientConnection = Test()
    suc = function.handleError('test')
    assert suc
