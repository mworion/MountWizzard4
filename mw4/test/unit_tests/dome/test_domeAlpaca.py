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
from mw4.dome.domeAlpaca import DomeAlpaca
from mw4.dome.dome import DomeSignals
from mw4.base.alpacaBase import AlpacaBase


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    app = DomeAlpaca(app=Test(), signals=DomeSignals(), data={})

    yield


def test_getInitialConfig_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.getInitialConfig()
        assert suc


def test_waitSettlingAndEmit():
    suc = app.waitSettlingAndEmit()
    assert suc


def test_emitData_1():
    app.data['slewing'] = False
    app.slewing = False
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.emitData()
        assert suc


def test_emitData_2():
    app.data['slewing'] = True
    app.slewing = False
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.emitData()
        assert suc


def test_emitData_3():
    app.data['slewing'] = False
    app.slewing = True
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.emitData()
        assert suc


def test_workerPollData_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        suc = app.workerPollData()
        assert suc


def test_slewToAltAz_1():
    app.slewing = False
    with mock.patch.object(AlpacaBase,
                           'put'):
        suc = app.slewToAltAz()
        assert suc
        assert app.slewing
