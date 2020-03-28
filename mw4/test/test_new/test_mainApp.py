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
    suc = app.loadConfig()
    assert suc
