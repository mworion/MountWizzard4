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
#
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
def module_setup_teardown():
    global app
    app = Remote(app=App())
    yield


def test_startCommunication_1():
    app.tcpServer = 1
    suc = app.startCommunication()
    assert not suc


def test_startCommunication_2():
    app.tcpServer = None
    suc = app.startCommunication()
    assert suc


def test_startCommunication_3():
    app.tcpServer = None
    server = QtNetwork.QTcpServer(app)
    hostAddress = QtNetwork.QHostAddress('127.0.0.1')
    server.listen(hostAddress, 3490)
    suc = app.startCommunication()
    assert not suc


def test_stopCommunication_1():
    app.tcpServer = 1
    suc = app.stopCommunication()
    assert suc


def test_stopCommunication_2():
    app.clientConnection = QtNetwork.QTcpServer(app)
    suc = app.stopCommunication()
    assert suc


def test_addConnection_1():
    app.tcpServer = None
    suc = app.addConnection()
    assert not suc


def test_addConnection_2():
    app.tcpServer = QtNetwork.QTcpServer(app)
    with mock.patch.object(app.tcpServer,
                           'nextPendingConnection',
                           return_value=0):
        suc = app.addConnection()
        assert not suc


def test_addConnection_3():
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
    app.tcpServer = QtNetwork.QTcpServer(app)
    with mock.patch.object(app.tcpServer,
                           'nextPendingConnection',
                           return_value=Test()):
        suc = app.addConnection()
        assert suc


def test_receiveMessage_1():
    class Test():
        @staticmethod
        def bytesAvailable():
            return 0

    app.clientConnection = Test()
    suc = app.receiveMessage()
    assert not suc


def test_receiveMessage_2():
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
        def read(number):
            return 'Test'.encode('ascii')

    app.clientConnection = Test()
    suc = app.receiveMessage()
    assert suc


def test_receiveMessage_3():
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
        def read(number):
            return 'shutdown'.encode('ascii')

    app.clientConnection = Test()
    suc = app.receiveMessage()
    assert suc


def test_removeConnection_1():
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

    app.clientConnection = Test()
    suc = app.removeConnection()
    assert suc


def test_handleError_1():
    class Test():
        @staticmethod
        def peerAddress():
            return Test()

        @staticmethod
        def toString():
            return 'Test'

    app.clientConnection = Test()
    suc = app.handleError('test')
    assert suc
