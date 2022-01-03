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
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.environment.skymeter import Skymeter


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
    global app
    app = Skymeter(app=Test())

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
