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
# written in python3 , (c) 2019, 2020 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from indibase.indiBase import Client
from indibase import indiXML


@pytest.fixture(autouse=True, scope='function')
def function():
    function = Client()
    yield function


def test_properties_1(function):
    function.host = 'localhost'
    assert function.host == ('localhost', 7624)


def test_properties_2(function):
    function.host = 12
    assert function.host is None


def test_clearParser(function):
    suc = function.clearParser()
    assert suc


def test_setServer_1(function):
    suc = function.setServer()
    assert not suc
    assert not function.connected


def test_setServer_2(function):
    function.connected = True
    suc = function.setServer('localhost')
    assert suc
    assert not function.connected
    assert function.host == ('localhost', 7624)


def test_watchDevice_1(function):
    with mock.patch.object(indiXML,
                           'clientGetProperties'):
        with mock.patch.object(function,
                               '_sendCmd',
                               return_value=False):
            suc = function.watchDevice('test')
            assert not suc


def test_watchDevice_2(function):
    with mock.patch.object(indiXML,
                           'clientGetProperties'):
        with mock.patch.object(function,
                               '_sendCmd',
                               return_value=True):
            suc = function.watchDevice('')
            assert suc


def test_connectServer_1(function):
    function._host = None
    with mock.patch.object(function.socket,
                           'connectToHost'):
        with mock.patch.object(function.socket,
                               'waitForConnected',
                               return_value=True):
            suc = function.connectServer()
            assert not suc


def test_connectServer_2(function):
    function._host = ('localhost', 7624)
    function.connected = True
    suc = function.connectServer()
    assert suc


def test_connectServer_3(function):
    function._host = ('localhost', 7624)
    function.connected = False
    with mock.patch.object(function.socket,
                           'connectToHost'):
        with mock.patch.object(function.socket,
                               'waitForConnected',
                               return_value=False):
            suc = function.connectServer()
            assert not suc
            assert not function.connected


def test_connectServer_4(function):
    function._host = ('localhost', 7624)
    function.connected = False
    with mock.patch.object(function.socket,
                           'connectToHost'):
        with mock.patch.object(function.socket,
                               'waitForConnected',
                               return_value=True):
            suc = function.connectServer()
            assert suc
            assert function.connected


def test_clearDevices_1(function):
    function.devices = {'test1', 'test2'}
    suc = function.clearDevices()
    assert suc
    assert function.devices == {}


def test_clearDevices_2(function):
    function.devices = {'test1', 'test2'}
    suc = function.clearDevices('test1')
    assert suc
    assert function.devices == {}
