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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import shutil

# external packages
from PySide6.QtCore import QTimer, QBasicTimer, QCoreApplication
from PySide6.QtWidgets import QWidget

# local import
from mainApp import MountWizzard4
from gui.mainWaddon.astroObjects import AstroObjects
from base.loggerMW import setupLogging
from mw4.resource import resources as res
res.qInitResources()
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def app(qapp):
    mwGlob = {'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'tempDir': 'tests/workDir/temp',
              'imageDir': 'tests/workDir/image',
              'modelDir': 'tests/workDir/model',
              'workDir': 'tests/workdir',
              }

    shutil.copy('tests/testData/de440_mw4.bsp', 'tests/workDir/data/de440_mw4.bsp')
    shutil.copy('tests/testData/test.run', 'tests/workDir/test.run')

    class Test:
        def emit(self):
            return

    with mock.patch.object(QWidget,
                           'show'):
        with mock.patch.object(QTimer,
                               'start'):
            with mock.patch.object(QBasicTimer,
                                   'start'):
                with mock.patch.object(AstroObjects,
                                       'loadSourceUrl'):
                    app = MountWizzard4(mwGlob=mwGlob, application=qapp)
                    app.update1s = Test()
                    yield app

    app.threadPool.waitForDone(1000)


def test_storeStatusOperationRunning(app):
    app.storeStatusOperationRunning(4)
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
    app.storeConfig()


def test_sendStart_1(app):
    app.timerCounter = 10
    app.sendStart()


def test_sendStart_2(app):
    app.timerCounter = 30
    app.sendStart()


def test_sendStart_3(app):
    app.timerCounter = 50
    app.sendStart()


def test_sendStart_4(app):
    app.timerCounter = 100
    app.sendStart()


def test_sendStart_5(app):
    app.timerCounter = 300
    app.sendStart()


def test_sendCyclic_1(app):
    app.timerCounter = 0
    app.sendCyclic()


def test_sendCyclic_2(app):
    app.timerCounter = 4
    app.sendCyclic()


def test_sendCyclic_3(app):
    app.timerCounter = 19
    app.sendCyclic()


def test_sendCyclic_4(app):
    app.timerCounter = 79
    app.sendCyclic()


def test_sendCyclic_5(app):
    app.timerCounter = 574
    app.sendCyclic()


def test_sendCyclic_6(app):
    app.timerCounter = 1800 - 12 - 1
    app.sendCyclic()


def test_sendCyclic_7(app):
    app.timerCounter = 6000 - 13 - 1
    app.sendCyclic()


def test_sendCyclic_8(app):
    app.timerCounter = 18000 - 14 - 1
    app.sendCyclic()


def test_sendCyclic_9(app):
    app.timerCounter = 36000 - 15 - 1
    app.sendCyclic()


def test_aboutToQuit_1(app):
    app.aboutToQuit()


def test_quit_1(app):
    with mock.patch.object(QCoreApplication,
                           'quit'):
        with mock.patch.object(app.mount,
                               'stopAllMountTimers'):
            app.quit()


def test_loadHorizonData_1(app):
    app.loadHorizonData()


def test_writeMessageQueue(app):
    app.writeMessageQueue(1, 'test', 'test', 'test')
