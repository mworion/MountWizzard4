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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import glob
import json
import unittest.mock as mock
import faulthandler
faulthandler.enable()

# external packages
import pytest
import PyQt5

# local import
from mw4.mainApp import MountWizzard4


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown(qapp):
    global app

    mwGlob = {'configDir': 'mw4/test/config',
              'dataDir': 'mw4/test/data',
              'tempDir': 'mw4/test/temp',
              'imageDir': 'mw4/test/image',
              'modelDir': 'mw4/test/model',
              'workDir': 'mw4/test',
              }

    files = glob.glob('mw4/test/config/*.cfg')
    for f in files:
        os.remove(f)

    with mock.patch.object(PyQt5.QtWidgets.QWidget,
                           'show'):
        with mock.patch.object(PyQt5.QtCore.QTimer,
                               'start'):
            app = MountWizzard4(mwGlob=mwGlob, application=qapp)
            yield app


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown_func(qapp):

    if os.path.isfile('mw4/test/config/config.cfg'):
        os.remove('mw4/test/config/config.cfg')
    if os.path.isfile('mw4/test/config/new.cfg'):
        os.remove('mw4/test/config/new.cfg')
    if os.path.isfile('mw4/test/config/profile'):
        os.remove('mw4/test/config/profile')

    yield


def test_initConfig_1():
    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_initConfig_2():
    app.config['mainW'] = {}
    app.config['mainW']['loglevelDebug'] = True

    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_initConfig_3():
    app.config['mainW'] = {}
    app.config['mainW']['loglevelDeepDebug'] = True

    val = app.initConfig()
    assert val.longitude.degrees == 0


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_storeConfig_2():
    def Sender():
        return None

    app.sender = Sender

    suc = app.storeConfig()
    assert suc

    if app.uiWindows['showMessageW']['classObj']:
        del app.uiWindows['showMessageW']['classObj']


def test_sendUpdate_1():
    app.timerCounter = 0
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_2():
    app.timerCounter = 4
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_3():
    app.timerCounter = 19
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_4():
    app.timerCounter = 79
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_5():
    app.timerCounter = 574
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_6():
    app.timerCounter = 1800 - 12 - 1
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_7():
    app.timerCounter = 6000 - 13 - 1
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_8():
    app.timerCounter = 18000 - 14 - 1
    suc = app.sendUpdate()
    assert suc


def test_sendUpdate_9():
    app.timerCounter = 36000 - 15 - 1
    suc = app.sendUpdate()
    assert suc


def test_quit_1():
    with mock.patch.object(PyQt5.QtCore.QCoreApplication,
                           'quit'):
        suc = app.quit()
        assert suc


def test_defaultConfig():
    val = app.defaultConfig()
    assert val


def test_loadConfig_1():
    suc = app.loadConfig()
    assert not suc
    assert app.config['profileName'] == 'config'


def test_loadConfig_2():
    with open('mw4/test/config/profile', 'w') as outfile:
        outfile.write('config')

    suc = app.loadConfig()
    assert not suc
    assert app.config['profileName'] == 'config'


def test_loadConfig_3():
    with open('mw4/test/config/profile', 'w') as outfile:
        outfile.write('config')
    config = app.defaultConfig()

    with open('mw4/test/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    suc = app.loadConfig()
    assert suc
    assert app.config['profileName'] == 'config'
    assert app.config['version'] == '4.0'


def test_loadConfig_4():
    with open('mw4/test/config/profile', 'w') as outfile:
        outfile.write('config')
    config = app.defaultConfig()
    config['version'] = '5.0'

    with open('mw4/test/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    with mock.patch.object(json,
                           'load',
                           side_effect=Exception()):
        suc = app.loadConfig()
    assert not suc
    assert app.config['profileName'] == 'config'
    assert app.config['version'] == '4.0'


def test_saveConfig_1():
    app.config = {'profileName': 'config'}

    suc = app.saveConfig()
    assert suc
    assert os.path.isfile('mw4/test/config/config.cfg')
    assert os.path.isfile('mw4/test/config/profile')
    with open('mw4/test/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'


def test_saveConfig_2():
    app.config = {'profileName': 'config'}

    suc = app.saveConfig('config')
    assert suc
    assert os.path.isfile('mw4/test/config/config.cfg')
    assert os.path.isfile('mw4/test/config/profile')
    with open('mw4/test/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'config'


def test_saveConfig_3():
    app.config = {'profileName': 'new'}

    suc = app.saveConfig('new')
    assert suc
    assert os.path.isfile('mw4/test/config/new.cfg')
    assert os.path.isfile('mw4/test/config/profile')
    with open('mw4/test/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'new'


def test_saveConfig_4():
    app.config = {'profileName': 'new'}

    suc = app.saveConfig()
    assert suc
    assert os.path.isfile('mw4/test/config/new.cfg')
    assert os.path.isfile('mw4/test/config/profile')
    with open('mw4/test/config/profile', 'r') as infile:
        name = infile.readline().strip()
    assert name == 'new'


def test_loadMountData_1():
    app.mountUp = False
    suc = app.loadMountData(True)
    assert suc


def test_loadMountData_2():
    app.mountUp = False
    suc = app.loadMountData(False)
    assert not suc

"""
def test_loadMountData_3():
    app.mountUp = True
    with mock.patch.object(app.mainW,
                           'searchTwilightWorker'):
        with mock.patch.object(app.mainW,
                               'displayTwilightData'):
            suc = app.loadMountData(False)
            assert not suc
"""

def test_loadMountData_4():
    app.mountUp = True
    suc = app.loadMountData(True)
    assert suc


def test_writeMessageQueue():
    suc = app.writeMessageQueue('test', 1)
    assert suc
