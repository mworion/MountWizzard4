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
from tests.baseTestSetupMixins import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from base import packageConfig
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
        pack, comm = function.versionPackage('matplotlib')
        assert pack == '1.0.0'
        assert comm == 'test'


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
        pack, comm = function.versionPackage('matplotlib')
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
                               return_value=(None, None)):
            suc = function.showUpdates()
            assert not suc


def test_showUpdates_3(function):
    function.ui.isOnline.setChecked(True)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.10'):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=('0.148.9', 'test')):
            suc = function.showUpdates()
            assert suc


def test_showUpdates_4(function):
    function.ui.isOnline.setChecked(True)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        with mock.patch.object(function,
                               'versionPackage',
                               return_value=('0.148.9', 'test')):
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
                               return_value=('0.148.9', '')):
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
                               return_value=('0.148.9', 'test')):
            suc = function.showUpdates()
            assert suc


def test_isVenv_1(function):
    function.isVenv()


def test_formatPIP_1(function):
    line = function.formatPIP()
    assert line == ''


def test_formatPIP_2(function):
    line = function.formatPIP('   ')
    assert line == ''


def test_formatPIP_3(function):
    line = function.formatPIP('Requirement already satisfied: mountcontrol in /Users (0.157)')
    assert line == 'Requirement already satisfied : mountcontrol'


def test_formatPIP_4(function):
    line = function.formatPIP('Collecting mountcontrol==0.157')
    assert line == 'Collecting mountcontrol'


def test_formatPIP_5(function):
    line = function.formatPIP('Installing collected packages: mountcontrol')
    assert line == 'Installing collected packages'


def test_formatPIP_6(function):
    line = function.formatPIP('Successfully installed mountcontrol-0.156')
    assert line == 'Successfully installed mountcontrol-0.156'


def test_restartProgram(function):
    with mock.patch.object(os,
                           'execl'):
        function.restartProgram()


def test_runInstall_1(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def readline():
            return ''

        @staticmethod
        def replace(a, b):
            return ''

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
        with mock.patch.object(function,
                               'formatPIP',
                               return_value='test'):
            suc, val = function.runInstall()
            assert suc


def test_runInstall_2(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def readline():
            return

        @staticmethod
        def replace(a, b):
            return ''

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test(),
                           side_effect=Exception()):
        with mock.patch.object(function,
                               'formatPIP',
                               return_value=''):
            suc, val = function.runInstall()
            assert not suc


def test_runInstall_3(function):
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def readline():
            return

        @staticmethod
        def replace(a, b):
            return ''

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test(),
                           side_effect=subprocess.TimeoutExpired('res', 2)):
        with mock.patch.object(function,
                               'formatPIP',
                               return_value=''):
            suc, val = function.runInstall()
            assert not suc


def test_installFinished_1(function):
    function.mutexInstall.lock()
    with mock.patch.object(function,
                           'restartProgram'):
        suc = function.installFinished(None)
        assert not suc


def test_installFinished_2(function):
    function.mutexInstall.lock()
    with mock.patch.object(function,
                           'restartProgram'):
        suc = function.installFinished((False, '0.148.8'))
        assert not suc


def test_installFinished_3(function):
    function.mutexInstall.lock()
    function.ui.automaticRestart.setChecked(True)
    with mock.patch.object(function,
                           'restartProgram'):
        suc = function.installFinished((True, '0.148.8'))
        assert suc


def test_installVersion_1(function):
    packageConfig.isWindows = True
    with mock.patch.object(function,
                           'isVenv',
                           return_value=False):
        suc = function.installVersion()
        assert not suc


def test_installVersion_2(function):
    function.mutexInstall.lock()
    packageConfig.isWindows = False
    with mock.patch.object(function,
                           'isVenv',
                           return_value=True):
        suc = function.installVersion()
        assert not suc


def test_installVersion_3(function):
    with mock.patch.object(function,
                           'isVenv',
                           return_value=True):
        with mock.patch.object(function.threadPool,
                               'start',
                               return_value=True):
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
    assert val == 30


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
    packageConfig.isAvailable = False
    suc = function.setupAudioSignals()
    assert not suc


def test_setupAudioSignals_2(function):
    packageConfig.isAvailable = True
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


def test_setVirtualStop(function):
    suc = function.setVirtualStop()
    assert suc
