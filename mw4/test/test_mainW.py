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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import logging
import pytest
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp

test = PyQt5.QtWidgets.QApplication([])
mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'dataDir': './mw4/test/config',
          'modeldata': 'test',
          }

'''
@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global spy
    global app

    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    yield
    spy = None
    app = None
'''
app = mainApp.MountWizzard4(mwGlob=mwGlob)
spy = PyQt5.QtTest.QSignalSpy(app.message)


#
#
# testing mainW gui booting shutdown
#
#

def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_3():
    app.config['mainW'] = {}
    app.config['mainW']['winPosX'] = 10000
    app.config['mainW']['winPosY'] = 10000
    suc = app.mainW.initConfig()
    assert suc


def test_mountBoot1(qtbot):
    with mock.patch.object(app.mount,
                           'bootMount',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.mountBoot()
            assert suc
        assert ['Mount booted', 0] == blocker.args


def test_mountBoot2(qtbot):
    with mock.patch.object(app.mount,
                           'bootMount',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.mountBoot()
            assert not suc
        assert ['Mount cannot be booted', 2] == blocker.args


def test_mountShutdown1(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'shutdown',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.mountShutdown()
            assert suc
        assert ['Shutting mount down', 0] == blocker.args


def test_mountShutdown2(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'shutdown',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.mountShutdown()
            assert not suc
        assert ['Mount cannot be shutdown', 2] == blocker.args


#
#
# testing mainW gui updateMountConnStat
#
#


def test_updateMountConnStat():
    suc = app.mainW.updateMountConnStat(True)
    assert suc
    assert 'green' == app.mainW.ui.mountConnected.property('color')
    suc = app.mainW.updateMountConnStat(False)
    assert suc
    assert 'red' == app.mainW.ui.mountConnected.property('color')

#
#
# testing mainW gui update Gui
#
#


def test_clearMountGUI():
    suc = app.mainW.clearMountGUI()
    assert suc


def test_updateGui():
    suc = app.mainW.updateGUI()
    assert suc


def test_updateTask():
    suc = app.mainW.updateTask()
    assert suc


def test_closeEvent():

    app.mainW.showStatus = True
    app.mainW.closeEvent(1)

    assert not app.mainW.showStatus


def test_saveProfile1(qtbot):
    with mock.patch.object(app,
                           'saveConfig',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            app.mainW.saveProfile()
        assert ['Actual profile saved', 0] == blocker.args


def test_loadProfile1(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app,
                               'loadConfig',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadProfile()
                assert suc
            assert ['Profile: [test] loaded', 0] == blocker.args


def test_loadProfile2(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app,
                               'loadConfig',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadProfile()
                assert suc
            assert ['Profile: [test] cannot no be loaded', 2] == blocker.args


def test_loadProfile3(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=(None, 'test', 'cfg')):
        suc = app.mainW.loadProfile()
        assert not suc


def test_saveProfileAs1(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app,
                               'saveConfig',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveProfileAs()
                assert suc
            assert ['Profile: [test] saved', 0] == blocker.args


def test_saveProfileAs2(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app,
                               'saveConfig',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveProfileAs()
                assert suc
            assert ['Profile: [test] cannot no be saved', 2] == blocker.args


def test_saveProfileAs3(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=(None, 'test', 'cfg')):
        suc = app.mainW.saveProfileAs()
        assert not suc


def test_saveProfile2(qtbot):
    with mock.patch.object(app,
                           'saveConfig',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            app.mainW.saveProfile()
        assert ['Actual profile cannot not be saved', 2] == blocker.args


def test_enableRelay1(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(True)
    with mock.patch.object(app.relay,
                           'startTimers',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRelay()
            assert suc
        assert ['Relay enabled', 0] == blocker.args


def test_enableRelay2(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(False)
    with mock.patch.object(app.relay,
                           'startTimers',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRelay()
            assert suc
        assert ['Relay disabled', 0] == blocker.args


def test_relayHost():
    app.mainW.ui.relayHost.setText('test')
    app.mainW.relayHost()

    assert app.relay.host == ('test', 80)


def test_relayUser():
    app.mainW.ui.relayUser.setText('test')
    app.mainW.relayUser()

    assert app.relay.user == 'test'


def test_relayPassword():
    app.mainW.ui.relayPassword.setText('test')
    app.mainW.relayPassword()

    assert app.relay.password == 'test'


def test_mountHost():
    app.mainW.ui.mountHost.setText('test')
    app.mainW.mountHost()

    assert app.mount.host == ('test', 3492)


def test_mountMAC():
    app.mainW.ui.mountMAC.setText('00:00:00:00:00:00')
    app.mainW.mountMAC()

    assert app.mount.MAC == '00:00:00:00:00:00'


def test_indiHost():
    app.mainW.ui.indiHost.setText('TEST')
    app.mainW.indiHost()
    assert app.environment.client.host == ('TEST', 7624)


def test_localWeatherName():
    app.mainW.ui.localWeatherName.setText('TEST')
    app.mainW.localWeatherName()
    assert 'TEST' == app.environment.wDevice['local']['name']


def test_globalWeatherName():
    app.mainW.ui.globalWeatherName.setText('TEST')
    app.mainW.globalWeatherName()
    assert 'TEST' == app.environment.wDevice['global']['name']


def test_sqmWeatherName():
    app.mainW.ui.sqmName.setText('TEST')
    app.mainW.sqmName()
    assert 'TEST' == app.environment.wDevice['sqm']['name']


def test_config():
    app.config = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': None,
        'mainW': {},
    }
    app.saveConfig()
    app.mainW.initConfig()
    app.mainW.storeConfig()
