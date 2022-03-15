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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest

# external packages

# local import
from gui.extWindows.hemisphere.editHorizon import EditHorizon
from tests.unit_tests.unitTestAddOns.baseTestSetupMixins import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    window = EditHorizon()
    window.app = App()
    window.ui = Ui_MainWindow()
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_loadHorizonMaskFile_1(function, qtbot):
    class Test:
        @staticmethod
        def drawHemisphere():
            return

    function.app.uiWindows = {'showHemisphereW': {'classObj': Test()}}
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadHorizonP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.loadHorizonMask()
                assert suc
            assert ['Horizon mask [test] loaded', 0] == blocker.args


def test_loadHorizonMaskFile_2(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('', '', '')):
        suc = function.loadHorizonMask()
        assert not suc


def test_loadHorizonMaskFile_3(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadHorizonP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.loadHorizonMask()
                assert suc
            assert ['Horizon mask [test] cannot no be loaded', 2] == blocker.args


def test_saveHorizonMaskFile_1(function, qtbot):
    function.ui.horizonFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveHorizonMask()
                assert suc
            assert ['Horizon mask [test] saved', 0] == blocker.args


def test_saveHorizonMaskFile_2(function, qtbot):
    function.ui.horizonFileName.setText('')
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.saveHorizonMask()
        assert not suc
    assert ['Horizon mask file name not given', 2] == blocker.args


def test_saveHorizonMaskFile_3(function, qtbot):
    function.ui.horizonFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveHorizonMask()
                assert suc
            assert ['Horizon mask [test] cannot no be saved', 2] == blocker.args


def test_saveHorizonMaskFileAs_1(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveHorizonMaskAs()
                assert suc
            assert ['Horizon mask [test] saved', 0] == blocker.args


def test_saveHorizonMaskFileAs_2(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('', '', '')):
        suc = function.saveHorizonMaskAs()
        assert not suc


def test_saveHorizonMaskFileAs_3(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveHorizonP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveHorizonMaskAs()
                assert suc
            assert ['Horizon mask [test] cannot no be saved', 2] == blocker.args


def test_clearHorizonMask(function):
    suc = function.clearHorizonMask()
    assert suc
