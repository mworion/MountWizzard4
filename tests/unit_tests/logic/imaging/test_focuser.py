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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import platform
import pytest
from unittest import mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.imaging.focuser import Focuser


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
    global app
    app = Focuser(app=Test())

    yield

    app.threadPool.waitForDone(1000)


def test_properties():
    app.framework = 'indi'
    app.host = ('localhost', 7624)
    assert app.host == ('localhost', 7624)

    app.deviceName = 'test'
    assert app.deviceName == 'test'


def test_startCommunication_1():
    app.framework = ''
    suc = app.startCommunication()
    assert not suc


def test_startCommunication_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'startCommunication',
                           return_value=True):
        suc = app.startCommunication()
        assert suc


@pytest.mark.skipif(platform.system() != 'Windows', reason='Win only')
def test_startCommunication_3():
    app.framework = 'ascom'
    with mock.patch.object(app.run['ascom'],
                           'startCommunication',
                           return_value=True):
        suc = app.startCommunication()
        assert suc


def test_startCommunication_4():
    app.framework = 'alpaca'
    with mock.patch.object(app.run['alpaca'],
                           'startCommunication',
                           return_value=True):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication_1():
    app.framework = ''
    suc = app.stopCommunication()
    assert not suc


def test_stopCommunication_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'stopCommunication',
                           return_value=True):
        suc = app.stopCommunication()
        assert suc


@pytest.mark.skipif(platform.system() != 'Windows', reason='Win only')
def test_stopCommunication_3():
    app.framework = 'ascom'
    with mock.patch.object(app.run['ascom'],
                           'stopCommunication',
                           return_value=True):
        suc = app.stopCommunication()
        assert suc


def test_stopCommunication_4():
    app.framework = 'alpaca'
    with mock.patch.object(app.run['alpaca'],
                           'stopCommunication',
                           return_value=True):
        suc = app.stopCommunication()
        assert suc


def test_move_1():
    app.framework = ''
    suc = app.move()
    assert not suc


def test_move_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'move',
                           return_value=True):
        suc = app.move()
        assert suc


@pytest.mark.skipif(platform.system() != 'Windows', reason='Win only')
def test_move_3():
    app.framework = 'ascom'
    with mock.patch.object(app.run['ascom'],
                           'move',
                           return_value=True):
        suc = app.move()
        assert suc


def test_move_4():
    app.framework = 'alpaca'
    with mock.patch.object(app.run['alpaca'],
                           'move',
                           return_value=True):
        suc = app.move()
        assert suc


def test_halt_1():
    app.framework = ''
    suc = app.halt()
    assert not suc


def test_halt_2():
    app.framework = 'indi'
    with mock.patch.object(app.run['indi'],
                           'halt',
                           return_value=True):
        suc = app.halt()
        assert suc


@pytest.mark.skipif(platform.system() != 'Windows', reason='Win only')
def test_halt_3():
    app.framework = 'ascom'
    with mock.patch.object(app.run['ascom'],
                           'halt',
                           return_value=True):
        suc = app.halt()
        assert suc


def test_halt_4():
    app.framework = 'alpaca'
    with mock.patch.object(app.run['alpaca'],
                           'halt',
                           return_value=True):
        suc = app.halt()
        assert suc
