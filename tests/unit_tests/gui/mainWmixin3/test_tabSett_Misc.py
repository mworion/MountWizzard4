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
import sys
import pytest
from unittest import mock
import logging
import platform
import os
import webbrowser

# external packages
from PyQt5.QtMultimedia import QSound
import requests
import importlib_metadata
import hid

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.mainWmixin.tabSett_Misc import SettMisc
import gui.mainWmixin.tabSett_Misc
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    class Mixin(MWidget, SettMisc):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = self.app.deviceStat
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SettMisc.__init__(self)

    window = Mixin()
    yield window
    window.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    with mock.patch.object(function,
                           'populateGameControllerList'):
        suc = function.initConfig()
        assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_sendGameControllerSignals_1(function):
    act = [0, 0, 0, 0, 0, 0, 0]
    old = [1, 1, 1, 1, 1, 1, 1]
    suc = function.sendGameControllerSignals(act, old)
    assert suc


def test_readGameController_1(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

    function.gameControllerRunning = True
    with mock.patch.object(Gamepad,
                           'read',
                           side_effect=Exception):
        val = function.readGameController(Gamepad())
        assert len(val) == 0


def test_readGameController_2(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return []

    function.gameControllerRunning = False
    val = function.readGameController(Gamepad())
    assert len(val) == 0


def test_readGameController_3(function):
    class Gamepad:
        @staticmethod
        def read(a):
            function.gameControllerRunning = False
            return [0] * 12

    function.gameControllerRunning = True
    val = function.readGameController(Gamepad())
    assert len(val) == 12


def test_readGameController_4(function):
    class Gamepad:
        @staticmethod
        def read(a):
            function.gameControllerRunning = False
            return []

    function.gameControllerRunning = True
    val = function.readGameController(Gamepad())
    assert len(val) == 0


def test_workerGameController_1(function):
    function.gameControllerRunning = False
    suc = function.workerGameController()
    assert not suc


def test_convertData_1(function):
    val = function.convertData('test', [])
    assert val[0] == 0
    assert val[1] == 0
    assert val[2] == 0
    assert val[3] == 0
    assert val[4] == 0
    assert val[5] == 0
    assert val[6] == 0


def test_convertData_2(function):
    iR = [0, 1, 2, 3, 0, 5, 0, 7, 0, 9, 0, 11]
    name = 'Pro Controller'
    val = function.convertData(name, iR)
    assert val[0] == 1
    assert val[1] == 2
    assert val[2] == 3
    assert val[3] == 5
    assert val[4] == 7
    assert val[5] == 9
    assert val[6] == 11


def test_convertData_3(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b1111
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_convertData_4(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b11100]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b110
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_convertData_5(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b10100]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b100
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_convertData_6(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b1100]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b10
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_convertData_7(function):
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b100]
    name = 'Controller (XBOX 360 For Windows)'
    val = function.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b0
    assert val[3] == 1
    assert val[4] == 3
    assert val[5] == 5
    assert val[6] == 7


def test_isNewerData_1(function):
    suc = function.isNewerData([], [])
    assert not suc


def test_isNewerData_2(function):
    suc = function.isNewerData([2], [2])
    assert not suc


def test_isNewerData_3(function):
    suc = function.isNewerData([2], [0])
    assert suc


def test_workerGameController_2(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

        @staticmethod
        def open(a, b):
            return

        @staticmethod
        def set_nonblocking(a):
            return

    function.gameControllerRunning = False
    function.ui.gameControllerList.clear()
    function.ui.gameControllerList.addItem('test')
    function.ui.gameControllerList.setCurrentIndex(0)
    function.gameControllerList['test'] = {'vendorId': 1, 'productId': 1}
    with mock.patch.object(hid,
                           'device',
                           return_value=Gamepad()):
        suc = function.workerGameController()
        assert suc


def test_workerGameController_3(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

        @staticmethod
        def open(a, b):
            return

        @staticmethod
        def set_nonblocking(a):
            return

    def gc(a):
        function.gameControllerRunning = False
        return []

    function.gameControllerRunning = True
    temp = function.readGameController
    function.readGameController = gc
    function.ui.gameControllerList.clear()
    function.ui.gameControllerList.addItem('test')
    function.ui.gameControllerList.setCurrentIndex(0)
    function.gameControllerList['test'] = {'vendorId': 1, 'productId': 1}
    with mock.patch.object(hid,
                           'device',
                           return_value=Gamepad()):
        with mock.patch.object(gui.mainWmixin.tabSett_Misc,
                               'sleepAndEvents'):
            suc = function.workerGameController()
            assert suc
    function.readGameController = temp


def test_workerGameController_4(function):
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

        @staticmethod
        def open(a, b):
            return

        @staticmethod
        def set_nonblocking(a):
            return

    def gc(a):
        function.gameControllerRunning = False
        return [1] * 12

    function.gameControllerRunning = True
    temp = function.readGameController
    function.readGameController = gc
    function.ui.gameControllerList.clear()
    function.ui.gameControllerList.addItem('test')
    function.ui.gameControllerList.setCurrentIndex(0)
    function.gameControllerList['test'] = {'vendorId': 1, 'productId': 1}
    with mock.patch.object(hid,
                           'device',
                           return_value=Gamepad()):
        with mock.patch.object(gui.mainWmixin.tabSett_Misc,
                               'sleepAndEvents'):
            with mock.patch.object(function,
                                   'sendGameControllerSignals'):
                suc = function.workerGameController()
                assert suc
    function.readGameController = temp


def test_startGameController(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.startGameController()
        assert suc


def test_isValidGameControllers_1(function):
    suc = function.isValidGameControllers('test')
    assert not suc


def test_isValidGameControllers_2(function):
    suc = function.isValidGameControllers('Game')
    assert suc


def test_populateGameControllerList_1(function):
    function.ui.gameControllerGroup.setChecked(False)
    function.gameControllerRunning = True
    suc = function.populateGameControllerList()
    assert not suc


def test_populateGameControllerList_2(function):
    function.ui.gameControllerGroup.setChecked(True)
    function.gameControllerRunning = True
    suc = function.populateGameControllerList()
    assert not suc


def test_populateGameControllerList_3(function):
    function.ui.gameControllerGroup.setChecked(True)
    function.gameControllerRunning = False
    device = [{'product_string': 'test',
               'vendor_id': 1,
               'product_id': 1}]
    with mock.patch.object(hid,
                           'enumerate',
                           return_value=device):
        with mock.patch.object(function,
                               'isValidGameControllers',
                               return_value=False):
            suc = function.populateGameControllerList()
            assert not suc


def test_populateGameControllerList_4(function):
    function.ui.gameControllerGroup.setChecked(True)
    function.gameControllerRunning = False
    device = [{'product_string': 'test',
               'vendor_id': 1,
               'product_id': 1}]
    with mock.patch.object(hid,
                           'enumerate',
                           return_value=device):
        with mock.patch.object(function,
                               'isValidGameControllers',
                               return_value=True):
            with mock.patch.object(function,
                                   'startGameController'):
                suc = function.populateGameControllerList()
                assert suc
                assert function.gameControllerRunning


def test_setWeatherOnline_1(function):
    function.app.onlineWeather = None
    suc = function.setWeatherOnline()
    assert not suc


def test_setWeatherOnline_2(function):
    suc = function.setWeatherOnline()
    assert suc


def test_setSeeingOnline_1(function):
    function.app.seeingWeather = None
    suc = function.setSeeingOnline()
    assert not suc


def test_setSeeingOnline_2(function):
    suc = function.setSeeingOnline()
    assert suc


def test_setupIERS_1(function):
    function.ui.isOnline.setChecked(False)
    suc = function.setupIERS()
    assert suc


def test_setupIERS_2(function):
    function.ui.isOnline.setChecked(True)
    suc = function.setupIERS()
    assert suc


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
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        suc = function.showUpdates()
        assert not suc


def test_showUpdates_2(function):
    function.ui.isOnline.setChecked(True)
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


def test_checkNewQt5LibNeeded_0(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = function.checkNewQt5LibNeeded('1.2.3')
        assert suc


def test_checkNewQt5LibNeeded_1(function):
    class Test:
        @staticmethod
        def json():
            return {'info': {'keywords': '5.15.4'}}

    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(requests,
                               'get',
                               return_value=Test(),
                               side_effect=Exception):
            suc = function.checkNewQt5LibNeeded('1.2.3')
            assert suc is None


def test_checkNewQt5LibNeeded_2(function):
    class Test:
        @staticmethod
        def json():
            return {'info': {'keywords': '5.15.4'}}

    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(requests,
                               'get',
                               return_value=Test()):
            with mock.patch.object(importlib_metadata,
                                   'version',
                                   return_value='5.15.4'):
                suc = function.checkNewQt5LibNeeded('1.2.3')
                assert suc


def test_checkNewQt5LibNeeded_3(function):
    class Test:
        @staticmethod
        def json():
            return {'info': {'keywords': '5.15.4'}}

    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(requests,
                               'get',
                               return_value=Test()):
            with mock.patch.object(importlib_metadata,
                                   'version',
                                   return_value='5.14.4'):
                suc = function.checkNewQt5LibNeeded('1.2.3')
                assert not suc


def test_startUpdater_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(os,
                               'execl'):
            with mock.patch.object(function,
                                   'checkNewQt5LibNeeded',
                                   return_value=None):
                suc = function.startUpdater('1.2.3')
                assert not suc


def test_startUpdater_2(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(os,
                               'execl'):
            with mock.patch.object(function,
                                   'checkNewQt5LibNeeded',
                                   return_value=True):
                suc = function.startUpdater('1.2.3')
                assert suc


def test_startUpdater_3(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(os,
                               'execl'):
            with mock.patch.object(function,
                                   'checkNewQt5LibNeeded',
                                   return_value=False):
                suc = function.startUpdater('1.2.3')
                assert suc


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


def test_playAudioDomeSlewFinished_1(function):
    with mock.patch.object(QSound,
                           'play'):
        suc = function.playSound('DomeSlew')
        assert not suc


def test_playAudioMountSlewFinished_1(function):
    with mock.patch.object(QSound,
                           'play'):
        suc = function.playSound('MountSlew')
        assert not suc


def test_playAudioMountAlert_1(function):
    with mock.patch.object(QSound,
                           'play'):
        suc = function.playSound('MountAlert')
        assert not suc


def test_playAudioModelFinished_1(function):
    with mock.patch.object(QSound,
                           'play'):
        suc = function.playSound('ModelFinished')
        assert not suc


def test_setupAudioSignals_1(function):
    suc = function.setupAudioSignals()
    assert suc


def test_playSound_1(function):
    suc = function.playSound()
    assert not suc


def test_playSound_2(function):
    function.audioSignalsSet['Pan1'] = 'test'
    function.guiAudioList['MountSlew'] = function.ui.soundMountSlewFinished
    function.guiAudioList['MountSlew'].addItem('Pan1')
    with mock.patch.object(QSound,
                           'play'):
        suc = function.playSound('MountSlew')
        assert suc


def test_playSound_3(function):
    function.audioSignalsSet['Pan1'] = 'test'
    function.guiAudioList['MountSlew'] = function.ui.soundMountSlewFinished
    function.guiAudioList['MountSlew'].addItem('Pan5')

    with mock.patch.object(QSound,
                           'play'):
        suc = function.playSound('MountSlew')
        assert not suc


@pytest.mark.skipif(platform.system() != 'Windows', reason="need windows")
def test_setAutomationSpeed_1(function):
    with mock.patch.object(gui.mainWmixin.tabSett_Misc,
                           'checkAutomation',
                           return_value=False):
        suc = function.setAutomationSpeed()
        assert not suc


@pytest.mark.skipif(platform.system() != 'Windows', reason="need windows")
def test_setAutomationSpeed_2(function):
    with mock.patch.object(gui.mainWmixin.tabSett_Misc,
                           'checkAutomation',
                           return_value=True):
        suc = function.setAutomationSpeed()
        assert suc


def test_openPDF_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openPDF()
        assert suc


def test_openPDF_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openPDF()
        assert suc


def test_setAddProfileGUI(function):
    suc = function.setAddProfileGUI()
    assert suc


def test_minimizeGUI(function):
    suc = function.minimizeGUI()
    assert suc
