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
import pytest
import unittest.mock as mock
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from mountcontrol.mount import Mount
import numpy as np

# local import
from mw4.dome.dome import Dome


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)
        update1s = pyqtSignal()
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
    global app
    app = Dome(app=Test())

    yield

    app.threadPool.waitForDone(1000)


def test_properties_1():
    app.framework = 'indi'

    app.host = ('localhost', 7624)
    assert app.host == ('localhost', 7624)

    app.name = 'test'
    assert app.name == 'test'

    app.settlingTime = 10
    assert app.settlingTime == 10000


def test_properties_2():
    app.framework = 'test'

    app.host = ('localhost', 7624)
    assert app.host == ('localhost', 7624)

    app.name = 'test'
    assert app.name == 'test'

    app.settlingTime = 10
    assert app.settlingTime is None


def test_startCommunication_1():
    app.framework = ''
    suc = app.startCommunication()
    assert not suc


def test_startCommunication_2():
    app.framework = 'indi'
    suc = app.startCommunication()
    assert not suc


def test_stopCommunication_1():
    app.framework = ''
    suc = app.stopCommunication()
    assert not suc


def test_stopCommunication_2():
    app.framework = 'indi'
    suc = app.stopCommunication()
    assert suc


def test_slewDome_1():
    app.data = {}
    suc = app.slewDome()
    assert not suc


def test_slewDome_2():
    app.data = {'AZ': 1}
    app.framework = 'indi'
    suc = app.slewDome(geometry=False)
    assert not suc


def test_slewDome_3():
    app.data = {'AZ': 1}
    app.framework = 'indi'

    with mock.patch.object(app,
                           'calcGeometry',
                           return_value=(10, 10)):
        suc = app.slewDome(geometry=True)
        assert not suc


def test_slewDome_4():
    app.data = {'AZ': 1}
    app.framework = 'indi'

    with mock.patch.object(app,
                           'calcGeometry',
                           return_value=(np.nan, 10)):
        suc = app.slewDome(geometry=True)
        assert not suc


def test_slewDome_5():
    app.data = {'AZ': 1}
    app.framework = 'indi'

    with mock.patch.object(app,
                           'calcGeometry',
                           return_value=(10, np.nan)):
        suc = app.slewDome(geometry=True)
        assert not suc
