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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from mw4.environment.onlineWeather import OnlineWeather


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        update10s = pyqtSignal()
    global app
    app = OnlineWeather(app=Test())


def test_properties():
    app.keyAPI = 'test'
    assert app.keyAPI == 'test'
    app.online = True
    assert app.online


def test_startCommunication_1():
    app.running = False
    suc = app.startCommunication()
    assert suc
    assert app.running


def test_stopCommunication_1():
    app.running = True
    suc = app.stopCommunication()
    assert suc
    assert not app.running
