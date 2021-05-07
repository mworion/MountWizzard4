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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import glob
import json
import unittest.mock as mock
import logging
import platform
import shutil
import time

# external packages
import pytest
import PyQt5

# local import
from mainApp import MountWizzard4
from base.loggerMW import addLoggingLevel


@pytest.fixture(autouse=True, scope='module')
def app(qapp):
    global mwGlob
    mwGlob = {'configDir': 'tests/config',
              'dataDir': 'tests/data',
              'tempDir': 'tests/temp',
              'imageDir': 'tests/image',
              'modelDir': 'tests/model',
              'workDir': 'mw4/test',
              }

    files = glob.glob('tests/config/*.cfg')
    for f in files:
        os.remove(f)

    shutil.copy(r'tests/testData/de421_23.bsp', r'tests/data/de421_23.bsp')

    with mock.patch.object(PyQt5.QtWidgets.QWidget,
                           'show'):
        with mock.patch.object(PyQt5.QtCore.QTimer,
                               'start'):
            with mock.patch.object(PyQt5.QtCore.QBasicTimer,
                                   'start'):
                app = MountWizzard4(mwGlob=mwGlob, application=qapp)
                app.log = logging.getLogger()
                addLoggingLevel('TRACE', 5)
                addLoggingLevel('UI', 35)
                yield app
                time.sleep(10)


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown_func(app):

    if os.path.isfile('tests/config/config.cfg'):
        os.remove('tests/config/config.cfg')
    if os.path.isfile('tests/config/new.cfg'):
        os.remove('tests/config/new.cfg')
    if os.path.isfile('tests/config/profile'):
        os.remove('tests/config/profile')

    yield


def test_checkAndSetAutomation_1(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='test'):
        val = app.checkAndSetAutomation()
        assert val is None


def test_checkAndSetAutomation_2(app):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(platform,
                               'python_version',
                               return_value='3.8.1'):
            val = app.checkAndSetAutomation()
            assert val is None


def test_initConfig_1(app):
    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_initConfig_2(app):
    app.config['mainW'] = {}
    app.config['mainW']['loglevelDebug'] = True

    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_initConfig_3(app):
    app.config['mainW'] = {}
    app.config['mainW']['loglevelDeepDebug'] = True

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


def test_sendUpdate_1(app):
    app.timerCounter = 0
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_2(app):
    app.timerCounter = 4
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_3(app):
    app.timerCounter = 19
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_4(app):
    app.timerCounter = 79
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_5(app):
    app.timerCounter = 574
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_6(app):
    app.timerCounter = 1800 - 12 - 1
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_7(app):
    app.timerCounter = 6000 - 13 - 1
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_8(app):
    app.timerCounter = 18000 - 14 - 1
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_9(app):
    app.timerCounter = 36000 - 15 - 1
    suc = app.sendUpdate()
    assert suc


def test_quit_1(app):
    with mock.patch.object(PyQt5.QtCore.QCoreApplication,
                           'quit'):
        suc = app.quit()
        assert suc


def test_defaultConfig(app):
    val = app.defaultConfig()
    assert val


def test_loadConfig_1(app):
    suc = app.loadConfig()
    assert not suc
    assert app.config['profileName'] == 'config'


def test_loadConfig_2(app):
    with open('tests/config/profile', 'w') as outfile:
        outfile.write('config')

    suc = app.loadConfig()
    assert not suc
    assert app.config['profileName'] == 'config'


def test_loadConfig_3(app):
    with open('tests/config/profile', 'w') as outfile:
        outfile.write('config')
    config = app.defaultConfig()

    with open('tests/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    suc = app.loadConfig()
    assert suc
    assert app.config['profileName'] == 'config'
    assert app.config['version'] == '4.0'


def test_loadConfig_4(app):
    with open('tests/config/profile', 'w') as outfile:
        outfile.write('config')
    config = app.defaultConfig()
    config['version'] = '5.0'

    with open('tests/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    with mock.patch.object(json,
                           'load',
                           side_effect=Exception()):
        suc = app.loadConfig()
    assert not suc
    assert app.config['profileName'] == 'config'
    assert app.config['version'] == '4.0'


def test_convertData(app):
    val = app.convertData('test')
    assert val == 'test'


def test_saveConfig_1(app):
    app.config = {'profileName': 'config'}

    suc = app.saveConfig()
    assert suc
    assert os.path.isfile('tests/config/config.cfg')
    assert os.path.isfile('tests/config/profile')
    with open('tests/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'


def test_saveConfig_2(app):
    app.config = {'profileName': 'config'}

    suc = app.saveConfig('config')
    assert suc
    assert os.path.isfile('tests/config/config.cfg')
    assert os.path.isfile('tests/config/profile')
    with open('tests/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'


def test_saveConfig_3(app):
    app.config = {'profileName': 'new'}

    suc = app.saveConfig('new')
    assert suc
    assert os.path.isfile('tests/config/new.cfg')
    assert os.path.isfile('tests/config/profile')
    with open('tests/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'new'


def test_saveConfig_4(app):
    app.config = {'profileName': 'new'}

    suc = app.saveConfig()
    assert suc
    assert os.path.isfile('tests/config/new.cfg')
    assert os.path.isfile('tests/config/profile')
    with open('tests/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'new'


def test_loadMountData_1(app):
    app.mountUp = False
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
        suc = app.loadMountData(False)
        assert not suc


def test_loadMountData_4(app):
    app.mountUp = True
    suc = app.loadMountData(True)
    assert suc


def test_writeMessageQueue(app):
    suc = app.writeMessageQueue('test', 1)
    assert suc
