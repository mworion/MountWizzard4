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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import logging
import subprocess
import platform
import os

# external packages
from PyQt5.QtMultimedia import QSound
import requests
import importlib_metadata

# local import
from gui.mainWmixin.tabSettMisc import SettMisc
from tests.unit_tests.unitTestAddOns.baseTestSetupMixins import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, SettMisc):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.deviceStat = self.app.deviceStat
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SettMisc.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_setWeatherOnline_1(function):
    function.app.onlineWeather = None
    suc = function.setWeatherOnline()
    assert not suc


def test_setWeatherOnline_2(function):
    suc = function.setWeatherOnline()
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
        val = function.versionPackage('matplotlib')
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
        pack, comm, ver = function.versionPackage('matplotlib')
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
        pack, comm, _ = function.versionPackage('matplotlib')
        assert pack == '1.0.0b1'
        assert comm == 'test'


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
    function.isVenv()


def test_startUpdater_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(os,
                               'execl'):
            with mock.patch.object(function,
                                   'checkUpdateVersion',
                                   return_value=None):
                suc = function.startUpdater('1.2.3')
                assert not suc


def test_checkUpdateVersion_1(function):
    class Test:
        @staticmethod
        def json():
            return {'info': {'keywords': '5.15.4'}}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test(),
                           side_effect=Exception):
        suc = function.checkUpdateVersion('1.2.3')
        assert suc is None


def test_checkUpdateVersion_2(function):
    class Test:
        @staticmethod
        def json():
            return {'info': {'keywords': '5.15.4'}}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        with mock.patch.object(importlib_metadata,
                               'version',
                               return_value='5.15.4'):
            suc = function.checkUpdateVersion('1.2.3')
            assert suc


def test_checkUpdateVersion_3(function):
    class Test:
        @staticmethod
        def json():
            return {'info': {'keywords': '5.15.4'}}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        with mock.patch.object(importlib_metadata,
                               'version',
                               return_value='5.14.4'):
            suc = function.checkUpdateVersion('1.2.3')
            assert not suc


def test_startUpdater_2(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(os,
                               'execl'):
            with mock.patch.object(function,
                                   'checkUpdateVersion',
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
                                   'checkUpdateVersion',
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


def test_pushTime_1a(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def replace(a, b):
            return a + b

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        with mock.patch.object(platform,
                               'system',
                               return_value='Windows'):
            suc = function.pushTime()
            assert suc


def test_pushTime_1b(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def replace(a, b):
            return a + b

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        with mock.patch.object(platform,
                               'system',
                               return_value='Linux'):
            suc = function.pushTime()
            assert suc


def test_pushTime_1c(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def replace(a, b):
            return a + b

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        with mock.patch.object(platform,
                               'system',
                               return_value='Darwin'):
            suc = function.pushTime()
            assert suc


def test_pushTime_1d(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def replace(a, b):
            return a + b

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        with mock.patch.object(platform,
                               'system',
                               return_value='xxx'):
            suc = function.pushTime()
            assert suc


def test_pushTime_2(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def replace(a, b):
            return a + b

    class Test:
        returncode = '1'
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test(),
                           side_effect=Exception()):
        suc = function.pushTime()
        assert not suc


def test_pushTime_3(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def replace(a, b):
            return a + b

    class Test:
        returncode = '1'
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test(),
                           side_effect=subprocess.TimeoutExpired('res', 2)):
        suc = function.pushTime()
        assert not suc


def test_pushTime_4(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def replace(a, b):
            return a + b

    class Test:
        returncode = 1
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        suc = function.pushTime()
        assert not suc


def test_pushTime_5(function):
    a = function.app.mount.obsSite.timeJD
    function.app.mount.obsSite.timeJD = None
    suc = function.pushTime()
    assert not suc
    function.app.mount.obsSite.timeJD = a


def test_pushTimeHourly_1(function):
    function.ui.autoPushTime.setChecked(False)
    suc = function.pushTimeHourly()
    assert not suc


def test_pushTimeHourly_2(function):
    function.ui.autoPushTime.setChecked(True)
    suc = function.pushTimeHourly()
    assert suc


def test_toggleClockSync_1(function):
    function.ui.clockSync.setChecked(True)
    suc = function.toggleClockSync()
    assert suc


def test_toggleClockSync_2(function):
    function.ui.clockSync.setChecked(False)
    suc = function.toggleClockSync()
    assert suc


def test_syncClock_1(function):
    function.ui.syncTimePC2Mount.setChecked(False)
    suc = function.syncClock()
    assert not suc


def test_syncClock_2(function):
    function.ui.syncTimePC2Mount.setChecked(True)
    function.app.deviceStat['mount'] = False
    suc = function.syncClock()
    assert not suc


def test_syncClock_3(function):
    function.ui.syncTimePC2Mount.setChecked(True)
    function.ui.syncNotTracking.setChecked(True)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 0
    suc = function.syncClock()
    assert not suc


@mock.patch('tests.unit_tests.unitTestAddOns.App.mount.obsSite.timeDiff', 0.005)
def test_syncClock_4(function):
    function.ui.syncTimePC2Mount.setChecked(True)
    function.ui.syncNotTracking.setChecked(False)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    suc = function.syncClock()
    assert not suc


@mock.patch('tests.unit_tests.unitTestAddOns.App.mount.obsSite.timeDiff', 1)
def test_syncClock_5(function):
    function.ui.syncTimePC2Mount.setChecked(True)
    function.ui.syncNotTracking.setChecked(False)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite,
                           'adjustClock',
                           return_value=False):
        suc = function.syncClock()
        assert not suc


@mock.patch('tests.unit_tests.unitTestAddOns.App.mount.obsSite.timeDiff', -1)
def test_syncClock_6(function):
    function.ui.syncTimePC2Mount.setChecked(True)
    function.ui.syncNotTracking.setChecked(False)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite,
                           'adjustClock',
                           return_value=True):
        suc = function.syncClock()
        assert suc


def test_setVirtualStop(function):
    suc = function.setVirtualStop()
    assert suc
