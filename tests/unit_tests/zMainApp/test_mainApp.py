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
import os
import unittest.mock as mock
import logging
import platform
import shutil

# external packages
from PyQt5.QtCore import QTimer, QBasicTimer, QCoreApplication
from PyQt5.QtWidgets import QWidget

# local import
from mw4.base.packageConfig import checkAutomation
if checkAutomation():
    from mw4.logic.automation.automateWindows import AutomateWindows
from mw4.mainApp import MountWizzard4
from mw4.base.loggerMW import setupLogging
import mw4.resource.resources as res
res.qInitResources()
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def app(qapp):
    global mwGlob
    mwGlob = {'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'tempDir': 'tests/workDir/temp',
              'imageDir': 'tests/workDir/image',
              'modelDir': 'tests/workDir/model',
              'workDir': 'tests/workdir',
              }

    shutil.copy('tests/testData/de440_mw4.bsp', 'tests/workDir/data/de440_mw4.bsp')
    shutil.copy('tests/testData/test.run', 'tests/workDir/test.run')

    with mock.patch.object(QWidget,
                           'show'):
        with mock.patch.object(QTimer,
                               'start'):
            with mock.patch.object(QBasicTimer,
                                   'start'):
                app = MountWizzard4(mwGlob=mwGlob, application=qapp)
                app.log = logging.getLogger()
                with mock.patch.object(app.mainW,
                                       'setupSatelliteNameList'):
                    yield app
                    app.threadPool.waitForDone(5000)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown_func(app):

    if os.path.isfile('tests/workDir/config/config.cfg'):
        os.remove('tests/workDir/config/config.cfg')
    if os.path.isfile('tests/workDir/config/new.cfg'):
        os.remove('tests/workDir/config/new.cfg')
    if os.path.isfile('tests/workDir/config/profile'):
        os.remove('tests/workDir/config/profile')
    yield


def test_checkAndSetAutomation_1(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        val = app.checkAndSetAutomation()
        assert val is None


@pytest.mark.skipif(platform.system() != 'Windows',
                    reason="requires windows")
def test_checkAndSetAutomation_2(app):
    with mock.patch.object(AutomateWindows,
                           'findAppSetup',
                           return_value=(False, '', '', '')):
        with mock.patch.object(platform,
                               'system',
                               return_value='Windows'):
            val = app.checkAndSetAutomation()
            assert val is not None


@pytest.mark.skipif(platform.system() != 'Windows',
                    reason="requires windows")
def test_checkAndSetAutomation_3(app):
    with mock.patch.object(AutomateWindows,
                           'findAppSetup',
                           return_value=(True, '', '', 'Test')):
        with mock.patch.object(platform,
                               'system',
                               return_value='Windows'):
            val = app.checkAndSetAutomation()
            assert val is not None


def test_storeStatusOperationRunning(app):
    suc = app.storeStatusOperationRunning(4)
    assert suc
    assert app.statusOperationRunning == 4


def test_initConfig_1(app):
    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_initConfig_2(app):
    app.config['mainW'] = {}
    app.config['mainW']['loglevelDebug'] = True

    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_initConfig_4(app):
    app.config['mainW'] = {}
    app.config['mainW']['loglevelTrace'] = True

    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_storeConfig_1(app):
    suc = app.storeConfig()
    assert suc


def test_storeConfig_2(app):
    def Sender(app):
        return None

    app.sender = Sender

    suc = app.storeConfig()
    assert suc

    if app.uiWindows['showMessageW']['classObj']:
        del app.uiWindows['showMessageW']['classObj']


def test_sendStart_1(app):
    app.timerCounter = 10
    suc = app.sendStart()
    assert suc


def test_sendStart_2(app):
    app.timerCounter = 30
    suc = app.sendStart()
    assert suc


def test_sendStart_3(app):
    app.timerCounter = 50
    suc = app.sendStart()
    assert suc


def test_sendStart_4(app):
    app.timerCounter = 100
    suc = app.sendStart()
    assert suc


def test_sendStart_5(app):
    app.timerCounter = 300
    suc = app.sendStart()
    assert suc


def test_sendCyclic_1(app):
    app.timerCounter = 0
    suc = app.sendCyclic()
    assert suc


def test_sendCyclic_2(app):
    app.timerCounter = 4
    suc = app.sendCyclic()
    assert suc


def test_sendCyclic_3(app):
    app.timerCounter = 19
    suc = app.sendCyclic()
    assert suc


def test_sendCyclic_4(app):
    app.timerCounter = 79
    suc = app.sendCyclic()
    assert suc


def test_sendCyclic_5(app):
    app.timerCounter = 574
    suc = app.sendCyclic()
    assert suc


def test_sendCyclic_6(app):
    app.timerCounter = 1800 - 12 - 1
    suc = app.sendCyclic()
    assert suc


def test_sendCyclic_7(app):
    app.timerCounter = 6000 - 13 - 1
    suc = app.sendCyclic()
    assert suc


def test_sendCyclic_8(app):
    app.timerCounter = 18000 - 14 - 1
    suc = app.sendCyclic()
    assert suc


def test_sendCyclic_9(app):
    app.timerCounter = 36000 - 15 - 1
    suc = app.sendCyclic()
    assert suc


def test_quit_1(app):
    with mock.patch.object(QCoreApplication,
                           'quit'):
        with mock.patch.object(app.mount,
                               'stopTimers'):
            suc = app.quit()
            assert suc


def test_loadMountData_1(app):
    app.mountUp = False
    with mock.patch.object(app.mount,
                           'cycleSetting'):
        with mock.patch.object(app.mount,
                               'getFW'):
            with mock.patch.object(app.mount,
                                   'getLocation'):
                with mock.patch.object(app.mainW,
                                       'refreshName'):
                    with mock.patch.object(app.mainW,
                                           'refreshModel'):
                        with mock.patch.object(app.mount,
                                               'getTLE'):
                            suc = app.loadMountData(True)
                            assert suc


def test_loadMountData_2(app):
    app.mountUp = False
    suc = app.loadMountData(False)
    assert not suc


def test_loadMountData_3(app):
    app.mountUp = True
    with mock.patch.object(app.mainW,
                           'calcTwilightData',
                           return_value=([], [])):
        with mock.patch.object(app.mount,
                               'resetData'):
            suc = app.loadMountData(False)
            assert not suc


def test_loadMountData_4(app):
    app.mountUp = True
    suc = app.loadMountData(True)
    assert suc


def test_writeMessageQueue(app):
    suc = app.writeMessageQueue(1, 'test', 'test', 'test')
    assert suc
