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
from unittest import mock

# external packages
from PyQt5.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
import gui.utilities
from mw4.gui.mainWmixin.tabTools_IERSTime import IERSTime
from mw4.logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    class Mixin(MWidget, IERSTime):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.databaseProcessing = DataWriter(self.app)
            self.threadPool = QThreadPool()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            IERSTime.__init__(self)

    window = Mixin()
    yield window
    window.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'tests/workDir/data'


def test_initConfig_2(function):
    temp = function.app.automation
    function.app.automation = None
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'tests/workDir/data'
    function.app.automation = temp


def test_initConfig_3(function):
    function.app.automation.installPath = 'test'
    suc = function.initConfig()
    assert suc
    assert function.installPath == 'test'


def test_storeConfig_1(function):
    function.thread = None
    suc = function.storeConfig()
    assert suc


def test_setupIERSSourceURLsDropDown(function):
    suc = function.setupIERSSourceURLsDropDown()
    assert suc


def test_progEarthRotationGUI_1(function):
    with mock.patch.object(function,
                           'checkUpdaterOK',
                           return_value=False):
        suc = function.progEarthRotationGUI()
        assert not suc


def test_progEarthRotationGUI_2(function):
    with mock.patch.object(function,
                           'checkUpdaterOK',
                           return_value=True):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=False):
            suc = function.progEarthRotationGUI()
            assert not suc


def test_progEarthRotationGUI_3(function):
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'checkUpdaterOK',
                               return_value=True):
            suc = function.progEarthRotationGUI()
            assert suc


def test_progEarthRotationData_1(function):
    with mock.patch.object(function,
                           'progEarthRotationGUI',
                           return_value=False):
        suc = function.progEarthRotationData()
        assert not suc


def test_progEarthRotationData_2(function):
    with mock.patch.object(function,
                           'progEarthRotationGUI',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeEarthRotationData',
                               return_value=False):
                suc = function.progEarthRotationData()
                assert not suc


def test_progEarthRotationData_3(function):
    with mock.patch.object(function,
                           'progEarthRotationGUI',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeEarthRotationData',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadEarthRotationData',
                                   return_value=False):
                suc = function.progEarthRotationData()
                assert not suc


def test_progEarthRotationData_4(function):
    with mock.patch.object(function,
                           'progEarthRotationGUI',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeEarthRotationData',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadEarthRotationData',
                                   return_value=True):
                suc = function.progEarthRotationData()
                assert suc


def test_startProgEarthRotationDataToMount_1(function):
    function.ui.isOnline.setChecked(True)
    with mock.patch.object(gui.mainWmixin.tabTools_IERSTime,
                           'DownloadPopup'):
        suc = function.startProgEarthRotationDataToMount()
        assert suc


def test_startProgEarthRotationDataToMount_2(function):
    function.ui.isOnline.setChecked(False)
    with mock.patch.object(function,
                           'progEarthRotationData',
                           return_value=True):
        suc = function.startProgEarthRotationDataToMount()
        assert not suc


def test_loadTimeDataFromSourceURLs_1(function):
    function.ui.isOnline.setChecked(False)
    with mock.patch.object(gui.mainWmixin.tabTools_IERSTime,
                           'DownloadPopup'):
        suc = function.loadTimeDataFromSourceURLs()
        assert not suc


def test_loadTimeDataFromSourceURLs_2(function):
    function.ui.isOnline.setChecked(True)
    with mock.patch.object(gui.mainWmixin.tabTools_IERSTime,
                           'DownloadPopup'):
        suc = function.loadTimeDataFromSourceURLs()
        assert suc
