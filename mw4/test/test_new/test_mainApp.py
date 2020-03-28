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
import os
import json
import unittest.mock as mock

# external packages
import pytest
import PyQt5

# local import
from mw4.mainApp import MountWizzard4
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app

    mwGlob = {'configDir': 'mw4/test/config',
              'dataDir': 'mw4/test/data',
              'tempDir': 'mw4/test/temp',
              'imageDir': 'mw4/test/image',
              'modelDir': 'mw4/test/model',
              'workDir': 'mw4/test',
              }

    if os.path.isfile('mw4/test/config/config.cfg'):
        os.remove('mw4/test/config/config.cfg')
    if os.path.isfile('mw4/test/config/new.cfg'):
        os.remove('mw4/test/config/new.cfg')

    app = MountWizzard4(mwGlob=mwGlob)
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)

    yield

    app.close()
    del app


def test_toggleWindow_1():
    def Sender():
        return app.mainW.ui.cameraSetup

    app.sender = Sender

    app.toggleWindow()


def test_toggleWindow_2():
    def Sender():
        return app.mainW.ui.openMessageW

    app.sender = Sender
    app.toggleWindow()
    assert app.uiWindows['showMessageW']['classObj'] is not None

    if app.uiWindows['showMessageW']['classObj']:
        del app.uiWindows['showMessageW']['classObj']


def test_toggleWindow_3():
    def Sender():
        return None

    app.sender = Sender
    app.toggleWindow('showMessageW')
    assert app.uiWindows['showMessageW']['classObj'] is not None

    if app.uiWindows['showMessageW']['classObj']:
        del app.uiWindows['showMessageW']['classObj']


def test_toggleWindow_4():
    def Sender():
        return None

    app.sender = Sender
    app.toggleWindow('showMessageW')
    app.toggleWindow('showMessageW')

    if app.uiWindows['showMessageW']['classObj']:
        del app.uiWindows['showMessageW']['classObj']


def test_deleteWindow_1():

    suc = app.deleteWindow()
    assert not suc


def test_deleteWindow_2():

    app.toggleWindow('showMessageW')
    suc = app.deleteWindow(app.uiWindows['showMessageW']['classObj'])
    assert suc

    if app.uiWindows['showMessageW']['classObj']:
        del app.uiWindows['showMessageW']['classObj']


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
    app.toggleWindow('showMessageW')

    suc = app.storeConfig()
    assert suc

    if app.uiWindows['showMessageW']['classObj']:
        del app.uiWindows['showMessageW']['classObj']


def test_showWindows_1():
    app.config['showMessageW'] = True

    suc = app.showWindows()
    assert suc

    if app.uiWindows['showMessageW']['classObj']:
        del app.uiWindows['showMessageW']['classObj']


def test_quit_1():
    with mock.patch.object(PyQt5.QtCore.QCoreApplication,
                           'quit'):
        suc = app.quit()
        assert suc


def test_quitSave_1():
    with mock.patch.object(PyQt5.QtCore.QCoreApplication,
                           'quit'):
        suc = app.quitSave()
        assert suc


def test_defaultConfig():
    val = app.defaultConfig()
    assert val


def test_loadConfig_1():
    suc = app.loadConfig()
    assert suc


def test_loadConfig_2():
    suc = app.loadConfig('config')
    assert suc


def test_loadConfig_3():
    suc = app.loadConfig('test')
    assert not suc


def test_loadConfig_4():
    config = {'test': 'test'}
    with open('mw4/test/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    with mock.patch.object(json,
                           'load',
                           side_effect=Exception()):
        suc = app.loadConfig('config')
        assert not suc


def test_loadConfig_5():
    config = {'reference': 'test'}
    with open('mw4/test/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    suc = app.loadConfig('config')
    assert not suc


def test_loadConfig_6():
    config = {'reference': 'new',
              'profileName': 'new'}

    with open('mw4/test/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    suc = app.loadConfig('config')
    assert not suc


def test_loadConfig_7():
    config = {'reference': 'new',
              'profileName': 'new'}

    with open('mw4/test/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)
    with open('mw4/test/config/new.cfg', 'w') as outfile:
        json.dump(config, outfile)

    suc = app.loadConfig('config')
    assert suc


def test_loadConfig_8():
    config = {'profileName': 'new'}

    with open('mw4/test/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)
    with open('mw4/test/config/new.cfg', 'w') as outfile:
        json.dump(config, outfile)

    suc = app.loadConfig('config')
    assert suc


def test_loadConfig_9():
    config = {'reference': 'config',
              'profileName': 'config'}

    with open('mw4/test/config/config.cfg', 'w') as outfile:
        json.dump(config, outfile)

    suc = app.loadConfig('config')
    assert suc


def test_saveConfig_1():
    app.config = {'profileName': 'config'}

    suc = app.saveConfig()
    assert suc
    assert os.path.isfile('mw4/test/config/config.cfg')


def test_saveConfig_2():
    app.config = {'profileName': 'config'}

    suc = app.saveConfig('config')
    assert suc
    assert os.path.isfile('mw4/test/config/config.cfg')


def test_saveConfig_3():
    app.config = {'reference': 'config',
                  'profileName': 'config'}

    suc = app.saveConfig('config')
    assert suc
    assert os.path.isfile('mw4/test/config/config.cfg')


def test_saveConfig_4():
    app.config = {'profileName': 'new'}

    suc = app.saveConfig('new')
    assert suc
    assert os.path.isfile('mw4/test/config/config.cfg')
    assert os.path.isfile('mw4/test/config/new.cfg')


def test_loadMountData_1():
    app.mountUp = False
    suc = app.loadMountData(True)
    assert suc


def test_loadMountData_2():
    app.mountUp = False
    suc = app.loadMountData(False)
    assert not suc


def test_loadMountData_3():
    app.mountUp = True
    suc = app.loadMountData(False)
    assert not suc


def test_loadMountData_4():
    app.mountUp = True
    suc = app.loadMountData(True)
    assert suc


def test_writeMessageQueue():
    suc = app.writeMessageQueue('test', 1)
    assert suc