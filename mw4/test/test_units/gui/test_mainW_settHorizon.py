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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
# external packages
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showHemisphereW'] = True
    app.toggleHemisphereWindow()
    yield


def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.mainW.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setupIcons():
    suc = app.mainW.setupIcons()
    assert suc


def test_loadHorizonMaskFile_1(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('build', 'test_mountwizzard', 'bpts')):
        with mock.patch.object(app.data,
                               'loadHorizonP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadHorizonMask()
                assert suc
            assert ['Horizon mask [test_mountwizzard] loaded', 0] == blocker.args


def test_loadHorizonMaskFile_2(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('', '', '')):
        suc = app.mainW.loadHorizonMask()
        assert not suc


def test_loadHorizonMaskFile_3(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('build', 'test_mountwizzard', 'bpts')):
        with mock.patch.object(app.data,
                               'loadHorizonP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadHorizonMask()
                assert suc
            assert ['Horizon mask [test_mountwizzard] cannot no be loaded', 2] == blocker.args


def test_saveHorizonMaskFile_1(qtbot):
    app.mainW.ui.horizonFileName.setText('test_mountwizzard')
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test_mountwizzard', 'bpts')):
        with mock.patch.object(app.data,
                               'saveHorizonP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveHorizonMask()
                assert suc
            assert ['Horizon mask [test_mountwizzard] saved', 0] == blocker.args


def test_saveHorizonMaskFile_2(qtbot):
    app.mainW.ui.horizonFileName.setText('')
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.saveHorizonMask()
        assert not suc
    assert ['Horizon mask file name not given', 2] == blocker.args


def test_saveHorizonMaskFile_3(qtbot):
    app.mainW.ui.horizonFileName.setText('test_mountwizzard')
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test_mountwizzard', 'bpts')):
        with mock.patch.object(app.data,
                               'saveHorizonP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveHorizonMask()
                assert suc
            assert ['Horizon mask [test_mountwizzard] cannot no be saved', 2] == blocker.args


def test_saveHorizonMaskFileAs_1(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test_mountwizzard', 'bpts')):
        with mock.patch.object(app.data,
                               'saveHorizonP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveHorizonMaskAs()
                assert suc
            assert ['Horizon mask [test_mountwizzard] saved', 0] == blocker.args


def test_saveHorizonMaskFileAs_2(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('', '', '')):
        suc = app.mainW.saveHorizonMaskAs()
        assert not suc


def test_saveHorizonMaskFileAs_3(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test_mountwizzard', 'bpts')):
        with mock.patch.object(app.data,
                               'saveHorizonP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveHorizonMaskAs()
                assert suc
            assert ['Horizon mask [test_mountwizzard] cannot no be saved', 2] == blocker.args
