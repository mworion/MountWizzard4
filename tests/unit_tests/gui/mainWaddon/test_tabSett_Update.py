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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import pytest
import astropy
from unittest import mock
import logging
import platform
import os
import webbrowser

# external packages
from PySide6.QtWidgets import QWidget
import requests
import importlib_metadata

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabSett_Update import SettUpdate
from gui.widgets.main_ui import Ui_MainWindow
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SettUpdate(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setWeatherOnline_1(function):
    temp = function.app.onlineWeather
    function.app.onlineWeather = None
    suc = function.setWeatherOnline()
    assert not suc
    function.app.onlineWeather = temp


def test_setWeatherOnline_2(function):
    suc = function.setWeatherOnline()
    assert suc


def test_setSeeingOnline_1(function):
    temp = function.app.seeingWeather
    function.app.seeingWeather = None
    suc = function.setSeeingOnline()
    assert not suc
    function.app.seeingWeather = temp


def test_setSeeingOnline_2(function):
    suc = function.setSeeingOnline()
    assert suc


def test_setupIERS_1(function):
    function.ui.isOnline.setChecked(False)
    function.setupIERS()


def test_setupIERS_2(function):
    function.ui.isOnline.setChecked(True)
    function.setupIERS()


def test_versionPackage_1(function):
    class Test:
        status_code = 300

        @staticmethod
        def json():
            return {'releases': {}}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test(),
                           side_effect=Exception()):
        val = function.versionPackage('astropy')
        assert val[0] is None
        assert val[1] is None


def test_versionPackage_2(function):
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return {'releases': {'1.0.0': [{'comment_text': 'test'}],
                                 '1.0.0b1': [{'comment_text': 'test'}]}}

    function.ui.versionBeta.setChecked(False)
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        pack, comm, ver = function.versionPackage('astropy')
        assert pack == '1.0.0'
        assert comm == 'test'
        assert ver == ['1.0.0', '1.0.0b1']


def test_versionPackage_3(function):
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return {'releases': {'1.0.0': [{'comment_text': 'test'}],
                                 '1.0.0b1': [{'comment_text': 'test'}]}}

    function.ui.versionBeta.setChecked(True)
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        pack, comm, _ = function.versionPackage('astropy')
        assert pack == '1.0.0b1'
        assert comm == 'test'


def test_versionPackage_4(function):
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return {'releases': {'1.0.0': [{'comment_text': 'test'}],
                                 '1.0.1': [{'comment_text': 'test'}]}}

    function.ui.versionBeta.setChecked(True)
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = function.versionPackage('astropy')
        assert val[0] is None
        assert val[1] is None


def test_showUpdates_1(function):
    function.ui.isOnline.setChecked(False)
    function.ui.versionReleaseNotes.setChecked(False)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        suc = function.showUpdates()
        assert not suc


def test_showUpdates_2(function):
    function.ui.isOnline.setChecked(True)
    function.ui.versionReleaseNotes.setChecked(False)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=(None, None, [])):
            suc = function.showUpdates()
            assert not suc


def test_showUpdates_3(function):
    function.ui.isOnline.setChecked(True)
    function.ui.versionReleaseNotes.setChecked(False)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.10'):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=('0.148.9', 'test', ['1.2.3'])):
            suc = function.showUpdates()
            assert suc


def test_showUpdates_4(function):
    function.ui.isOnline.setChecked(True)
    function.ui.versionReleaseNotes.setChecked(False)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=('0.148.9', 'test', ['1.2.3'])):
            suc = function.showUpdates()
            assert suc


def test_showUpdates_5(function):
    function.ui.isOnline.setChecked(True)
    function.ui.versionReleaseNotes.setChecked(True)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=('0.148.9', '', ['1.2.3'])):
            suc = function.showUpdates()
            assert suc


def test_showUpdates_6(function):
    function.ui.isOnline.setChecked(True)
    function.ui.versionReleaseNotes.setChecked(True)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=('0.148.9', 'test', ['1.2.3'])):
            suc = function.showUpdates()
            assert suc


def test_isVenv_1(function):
    setattr(sys, 'real_prefix', '')
    function.isVenv()


def test_startUpdater_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(os,
                               'execl'):
            function.startUpdater('1.2.3')


def test_startUpdater_2(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(os,
                               'execl'):
            function.startUpdater('1.2.3')


def test_installVersion_1(function):
    with mock.patch.object(function,
                           'isVenv',
                           return_value=False):
        suc = function.installVersion()
        assert not suc


def test_installVersion_2(function):
    function.ui.versionAvailable.setText('2.1.1')
    with mock.patch.object(function,
                           'isVenv',
                           return_value=True):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=(None, None, ['1.2.3'])):
            suc = function.installVersion()
            assert not suc


def test_installVersion_3(function):
    function.ui.versionAvailable.setText('1.2.3')
    with mock.patch.object(function,
                           'isVenv',
                           return_value=True):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=(None, None, ['1.2.3'])):
            with mock.patch.object(function,
                                   'startUpdater'):
                suc = function.installVersion()
                assert suc


def test_setLoggingLevel1(function, qtbot):
    function.ui.loglevelDebug.setChecked(True)
    function.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 10


def test_setLoggingLevel2(function, qtbot):
    function.ui.loglevelStandard.setChecked(True)
    function.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 20


def test_setLoggingLevel3(function, qtbot):
    function.ui.loglevelTrace.setChecked(True)
    function.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 5


def test_openPDF_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        function.openPDF()


def test_openPDF_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        function.openPDF()
