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
from mw4.test.test_setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


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
        assert ['Sent boot command to mount', 0] == blocker.args


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


def test_updateMountConnStat():
    suc = app.mainW.updateMountConnStat(True)
    assert suc
    assert 'green' == app.mainW.ui.mountConnected.property('color')
    suc = app.mainW.updateMountConnStat(False)
    assert suc
    assert 'red' == app.mainW.ui.mountConnected.property('color')


def test_clearMountGUI():
    suc = app.mainW.clearGUI()
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
                           return_value=(None, None, 'cfg')):
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
                           return_value=(None, None, 'cfg')):
        suc = app.mainW.saveProfileAs()
        assert not suc


def test_saveProfile2(qtbot):
    with mock.patch.object(app,
                           'saveConfig',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            app.mainW.saveProfile()
        assert ['Actual profile cannot not be saved', 2] == blocker.args


def test_mountHost():
    app.mainW.ui.mountHost.setText('test')
    app.mainW.mountHost()

    assert app.mount.host == ('test', 3492)


def test_mountMAC():
    app.mainW.ui.mountMAC.setText('00:00:00:00:00:00')
    app.mainW.mountMAC()

    assert app.mount.MAC == '00:00:00:00:00:00'


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
