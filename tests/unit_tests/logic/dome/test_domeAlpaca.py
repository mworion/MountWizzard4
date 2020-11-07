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

# external packages
import PyQt5
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from logic.dome.domeAlpaca import DomeAlpaca
from logic.dome.dome import DomeSignals
from base.alpacaBase import AlpacaBase


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(str, int)

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = DomeAlpaca(app=Test(), signals=DomeSignals(), data={})

        yield


def test_waitSettlingAndEmit():
    suc = app.waitSettlingAndEmit()
    assert suc


def test_diffModulus_1():
    val = app.diffModulus(1, 359, 360)
    assert val == 2


def test_processPolledData_1():
    app.data['slewing'] = False
    app.slewing = False
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.processPolledData()
        assert suc


def test_processPolledData_2():
    app.data['slewing'] = True
    app.slewing = False
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.processPolledData()
        assert suc


def test_processPolledData_3():
    app.data['slewing'] = False
    app.slewing = True
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.processPolledData()
        assert suc


def test_processPolledData_4():
    app.data['slewing'] = False
    app.slewing = True
    app.targetAzimuth = 1
    with mock.patch.object(app.settlingWait,
                           'start'):
        suc = app.processPolledData()
        assert suc


def test_workerPollData_1():
    with mock.patch.object(AlpacaBase,
                           'get'):
        with mock.patch.object(app.client,
                               'shutterstatus',
                               return_value=0):
            suc = app.workerPollData()
            assert suc


def test_workerPollData_2():
    with mock.patch.object(AlpacaBase,
                           'get'):
        with mock.patch.object(app.client,
                               'shutterstatus',
                               return_value=1):
            suc = app.workerPollData()
            assert suc


def test_slewToAltAz_1():
    app.slewing = False
    with mock.patch.object(AlpacaBase,
                           'put'):
        suc = app.slewToAltAz()
        assert suc
        assert app.slewing
