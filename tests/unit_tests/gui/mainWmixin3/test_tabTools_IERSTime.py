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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock

# external packages
from PyQt6.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
import gui.utilities
from gui.mainWmixin.tabTools_IERSTime import IERSTime
from logic.databaseProcessing.dataWriter import DataWriter


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
    assert function.tempDir == 'tests/workDir/temp'


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc
    assert function.tempDir == 'tests/workDir/temp'


def test_storeConfig_1(function):
    function.thread = None
    suc = function.storeConfig()
    assert suc


def test_setupIERSSourceURLsDropDown(function):
    suc = function.setupIERSSourceURLsDropDown()
    assert suc


def test_progEarthRotationData_1(function):
    with mock.patch.object(function.databaseProcessing,
                           'writeEarthRotationData',
                           return_value=False):
        suc = function.progEarthRotationData()
        assert not suc


def test_progEarthRotationData_2(function):
    with mock.patch.object(function.databaseProcessing,
                           'writeEarthRotationData',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'progDataToMount',
                               return_value=False):
            suc = function.progEarthRotationData()
            assert not suc


def test_progEarthRotationData_3(function):
    with mock.patch.object(function.databaseProcessing,
                           'writeEarthRotationData',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'progDataToMount',
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