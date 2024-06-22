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
import unittest.mock as mock
from unittest.mock import patch
import pytest
import glob
import os
import shutil
import logging
import builtins

# external packages
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QPushButton, QWidget
from skyfield.api import wgs84

# local import
import gui.utilities.toolsQtWidget
from gui.mainWindow.mainW import MainWindow
from gui.extWindows.imageW import ImageWindow
from base.loggerMW import addLoggingLevel
from base import packageConfig
from resource import resources
from tests.unit_tests.unitTestAddOns.baseTestApp import App
resources.qInitResources()


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    shutil.copy('tests/testData/visual.txt', 'tests/workDir/data/visual.txt')
    with mock.patch.object(MainWindow,
                           'show'):
        with mock.patch.object(ImageWindow,
                               'show'):
            packageConfig.isAvailable = True
            func = MainWindow(app=App())
            func.log = logging.getLogger()
            addLoggingLevel('TRACE', 5)
            addLoggingLevel('UI', 35)
            yield func

    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.initConfig()
        assert suc


def test_initConfig_2(function):
    del function.app.config['mainW']
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.initConfig()
        assert suc


def test_initConfig_3(function):
    function.app.config['mainW'] = {}
    function.app.config['mainW']['winPosX'] = 100
    function.app.config['mainW']['winPosY'] = 100
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.initConfig()
        assert suc


def test_initConfig_4(function):
    function.app.config['mainW'] = {}
    function.app.config['mainW']['winPosX'] = 10000
    function.app.config['mainW']['winPosY'] = 10000
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.initConfig()
        assert suc


def test_storeConfig_1(function):
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.storeConfig()
        assert suc


def test_storeConfig_2(function):
    del function.app.config['mainW']
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.storeConfig()
        assert suc


def test_closeEvent_1(function):
    with mock.patch.object(builtins,
                           'super'):
        with mock.patch.object(function.extWindows,
                               'closeExtendedWindows'):
            with mock.patch.object(function,
                                   'stopDrivers'):
                with mock.patch.object(function.threadPool,
                                       'waitForDone'):
                    function.closeEvent(QCloseEvent())


def test_enableTabsMovable(function):
    suc = function.enableTabsMovable()
    assert suc


def test_quitSave_1(function):
    function.ui.profile.setText('test')
    with mock.patch.object(function,
                           'saveConfig'):
        with mock.patch.object(gui.mainWindow.mainW,
                               'saveProfile'):
            with mock.patch.object(function,
                                   'close'):
                suc = function.quitSave()
                assert suc


def test_setupIcons(function):
    suc = function.setupIcons()
    assert suc


@patch('base.packageConfig.isAvailable', True)
def test_updateMountConnStat_1(function):
    suc = function.updateMountConnStat(True)
    assert suc
    assert function.deviceStat['mount']
    assert function.ui.mountConnected.text() == 'Mount 3D'


@patch('base.packageConfig.isAvailable', False)
def test_updateMountConnStat_2(function):
    suc = function.updateMountConnStat(True)
    assert suc
    assert function.deviceStat['mount']
    assert function.ui.mountConnected.text() == 'Mount'


@patch('base.packageConfig.isAvailable', True)
def test_updateMountConnStat_3(function):
    test = function.extWindows.uiWindows
    function.uiWindows = {'showSimulatorW': {
        'button': function.ui.mountConnected,
        'classObj': QWidget(),
        'name': 'SimulatorDialog',
        'class': None,
        }
    }
    suc = function.updateMountConnStat(False)
    assert function.ui.mountConnected.text() == 'Mount'
    assert not function.deviceStat['mount']
    assert suc
    function.uiWindows = test

def test_updateMountWeatherStat_1(function):
    class S:
        weatherPressure = None
        weatherTemperature = None
        weatherStatus = None

    suc = function.updateMountWeatherStat(S())
    assert suc
    assert function.deviceStat['directWeather'] is None


def test_updateMountWeatherStat_2(function):
    class S:
        weatherPressure = 1000
        weatherTemperature = 10
        weatherStatus = None

    suc = function.updateMountWeatherStat(S())
    assert suc
    assert not function.deviceStat['directWeather']


def test_updateMountWeatherStat_3(function):
    class S:
        weatherPressure = 1000
        weatherTemperature = 10
        weatherStatus = True

    suc = function.updateMountWeatherStat(S())
    assert suc
    assert function.deviceStat['directWeather']


def test_smartFunctionGui_0(function):
    function.deviceStat['mount'] = True
    function.deviceStat['camera'] = True
    function.deviceStat['plateSolve'] = True
    function.app.data.buildP = []
    function.ui.pauseModel.setProperty('pause', False)
    suc = function.smartFunctionGui()
    assert suc
    assert function.ui.plateSolveSync.isEnabled()


def test_smartFunctionGui_1(function):
    function.deviceStat['mount'] = True
    function.deviceStat['camera'] = True
    function.deviceStat['plateSolve'] = True
    function.app.data.buildP = [(0, 0)]
    suc = function.smartFunctionGui()
    assert suc
    assert function.ui.runModel.isEnabled()
    assert function.ui.plateSolveSync.isEnabled()
    assert function.ui.dataModel.isEnabled()
    assert function.ui.runFlexure.isEnabled()
    assert function.ui.runHysteresis.isEnabled()


def test_smartFunctionGui_2(function):
    function.deviceStat['mount'] = True
    function.deviceStat['camera'] = False
    function.deviceStat['plateSolve'] = True
    function.app.data.buildP = [(0, 0)]
    suc = function.smartFunctionGui()
    assert suc
    assert not function.ui.runModel.isEnabled()
    assert not function.ui.plateSolveSync.isEnabled()
    assert not function.ui.dataModel.isEnabled()
    assert not function.ui.runFlexure.isEnabled()
    assert not function.ui.runHysteresis.isEnabled()


def test_smartFunctionGui_3(function):
    function.deviceStat['mount'] = True
    suc = function.smartFunctionGui()
    assert suc
    assert function.ui.refractionGroup.isEnabled()
    assert function.ui.dsoGroup.isEnabled()
    assert function.ui.mountCommandTable.isEnabled()


def test_smartFunctionGui_4(function):
    function.deviceStat['mount'] = False
    suc = function.smartFunctionGui()
    assert suc
    assert not function.ui.refractionGroup.isEnabled()
    assert not function.ui.dsoGroup.isEnabled()
    assert not function.ui.mountCommandTable.isEnabled()


def test_smartFunctionGui_5(function):
    function.deviceStat['dome'] = True
    function.deviceStat['mount'] = True
    suc = function.smartFunctionGui()
    assert suc
    assert function.ui.useDomeAz.isEnabled()


def test_smartFunctionGui_6(function):
    function.deviceStat['dome'] = False
    function.deviceStat['mount'] = False
    suc = function.smartFunctionGui()
    assert suc
    assert not function.ui.useDomeAz.isEnabled()


def test_smartTabGui_1(function):
    suc = function.smartTabGui()
    assert suc


def test_smartTabGui_2(function):
    function.deviceStat['power'] = True
    suc = function.smartTabGui()
    assert suc


def test_mountBoot1(function):
    with mock.patch.object(function.app.mount,
                           'bootMount',
                           return_value=True):
        suc = function.mountBoot()
        assert suc


def test_updateWindowsStats_1(function):
    test = function.extWindows.uiWindows
    function.uiWindows = {'showMessageW': {'classObj': 1,
                                           'button': QPushButton()}}
    suc = function.updateWindowsStats()
    assert suc
    function.uiWindows = test


def test_updateWindowsStats_2(function):
    test = function.extWindows.uiWindows
    function.uiWindows = {'showMessageW': {'classObj': None,
                                           'button': QPushButton()}}
    suc = function.updateWindowsStats()
    assert suc
    function.uiWindows = test


def test_setEnvironDeviceStats_1(function):
    function.ui.showTabEnviron.setChecked(True)
    function.app.mount.setting.statusRefraction = 0

    suc = function.setEnvironDeviceStats()
    assert suc
    assert function.deviceStat['refraction'] is None


def test_setEnvironDeviceStats_2(function):
    function.ui.showTabEnviron.setChecked(True)
    function.ui.refracManual.setChecked(True)
    function.app.mount.setting.statusRefraction = 1

    suc = function.setEnvironDeviceStats()
    assert suc
    assert function.deviceStat['refraction']


def test_setEnvironDeviceStats_3(function):
    function.ui.showTabEnviron.setChecked(True)
    function.ui.refracCont.setChecked(True)
    function.app.mount.setting.statusRefraction = 1
    function.refractionSource = 'onlineWeather'
    function.deviceStat['onlineWeather'] = False

    suc = function.setEnvironDeviceStats()
    assert suc
    assert not function.deviceStat['refraction']


def test_updateDeviceStats_1(function):
    function.deviceStatGui = {'onlineWeather': QWidget()}
    function.deviceStat = {'onlineWeather': True}
    suc = function.updateDeviceStats()
    assert suc


def test_updateDeviceStats_2(function):
    function.deviceStatGui = {'onlineWeather': QWidget()}
    function.deviceStat = {'onlineWeather': False}
    suc = function.updateDeviceStats()
    assert suc


def test_updateDeviceStats_3(function):
    function.deviceStatGui = {'onlineWeather': QWidget()}
    function.deviceStat = {'onlineWeather': None}
    suc = function.updateDeviceStats()
    assert suc


def test_updateControllerStatus_1(function):
    suc = function.updateControllerStatus()
    assert suc


def test_updateThreadAndOnlineStatus_1(function):
    function.app.mwGlob['workDir'] = 'tests/workDir'
    function.ui.isOnline.setChecked(True)
    with mock.patch.object(shutil,
                           'disk_usage',
                           return_value=(100, 100, 100)):
        suc = function.updateThreadAndOnlineStatus()
        assert suc


def test_updateThreadAndOnlineStatus_2(function):
    function.app.mwGlob['workDir'] = 'tests/workDir'
    function.ui.isOnline.setChecked(False)
    with mock.patch.object(shutil,
                           'disk_usage',
                           return_value=(100, 100, 100)):
        suc = function.updateThreadAndOnlineStatus()
        assert suc


def test_updateTime_1(function):
    suc = function.updateTime()
    assert suc


def test_updatePlateSolveStatus(function):
    suc = function.updatePlateSolveStatus('test')
    assert suc
    assert function.ui.plateSolveText.text() == 'test'


def test_updateDomeStatus(function):
    suc = function.updateDomeStatus('test')
    assert suc
    assert function.ui.domeText.text() == 'test'


def test_updateCameraStatus(function):
    suc = function.updateCameraStatus('test')
    assert suc
    assert function.ui.cameraText.text() == 'test'


def test_updateStatusGUI_1(function):
    class OB:
        @staticmethod
        def statusText():
            return None

    function.app.mount.obsSite.status = 0
    suc = function.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_2(function):
    class OB:
        @staticmethod
        def statusText():
            return 'test'

    function.app.mount.obsSite.status = 0
    suc = function.updateStatusGUI(OB)
    assert suc
    assert function.ui.statusText.text() == 'test'


def test_updateStatusGUI_3(function):
    class OB:
        @staticmethod
        def statusText():
            return None

    function.app.mount.obsSite.status = 5
    suc = function.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_4(function):
    class OB:
        @staticmethod
        def statusText():
            return None

    function.app.mount.obsSite.status = 1
    suc = function.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_5(function):
    class OB:
        @staticmethod
        def statusText():
            return None

    function.app.mount.obsSite.status = 10
    function.satStatus = False
    suc = function.updateStatusGUI(OB)
    assert suc


def test_setColorSet(function):
    suc = function.setColorSet()
    assert suc


def test_refreshColorSet(function):
    with mock.patch.object(function,
                           'setupIcons'):
        with mock.patch.object(function,
                               'setColorSet'):
            with mock.patch.object(function,
                                   'setStyleSheet'):
                suc = function.refreshColorSet()
                assert suc


def test_checkExtension_1(function):
    val = function.checkExtension('tests/workDir/image/test.fit', 'fit')
    assert val == 'tests/workDir/image/test.fit'


def test_checkExtension_2(function):
    val = function.checkExtension('tests/workDir/image/test', '.fit')
    assert val == 'tests/workDir/image/test.fit'


def test_mountBoot1(function):
    with mock.patch.object(function.app.mount,
                           'bootMount',
                           return_value=False):
        suc = function.mountBoot()
        assert not suc


def test_mountShutdown1(function):
    with mock.patch.object(function.app.mount,
                           'shutdown',
                           return_value=True):
        suc = function.mountShutdown()
        assert suc


def test_mountShutdown2(function):
    with mock.patch.object(function.app.mount,
                           'shutdown',
                           return_value=False):
        suc = function.mountShutdown()
        assert not suc


def test_saveConfig1(function):
    with mock.patch.object(function,
                           'storeConfig'):
        with mock.patch.object(function.app,
                               'storeConfig'):
            with mock.patch.object(gui.mainWindow.mainW,
                                   'saveProfile',
                                   return_value=True):
                suc = function.saveConfig()
                assert suc


def test_saveConfig2(function):
    with mock.patch.object(function,
                           'storeConfig'):
        with mock.patch.object(function.app,
                               'storeConfig'):
            with mock.patch.object(gui.mainWindow.mainW,
                                   'saveProfile',
                                   return_value=False):
                suc = function.saveConfig()
                assert not suc


def test_switchProfile_1(function):
    loc = wgs84.latlon(latitude_degrees=10, longitude_degrees=10)
    with mock.patch.object(function.extWindows,
                           'closeExtendedWindows'):
        with mock.patch.object(function.extWindows,
                               'showExtendedWindows'):
            with mock.patch.object(function,
                                   'initConfig'):
                with mock.patch.object(function.app,
                                       'initConfig',
                                       return_value=loc):
                    with mock.patch.object(function,
                                           'stopDrivers'):
                        suc = function.switchProfile({'test': 1})
                        assert suc


def test_loadProfileGUI_1(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=(None, None, 'cfg')):
        suc = function.loadProfileGUI()
        assert not suc


def test_loadProfileGUI2(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'loadProfile',
                               return_value={}):
            with mock.patch.object(function,
                                   'switchProfile'):
                suc = function.loadProfileGUI()
                assert not suc


def test_loadProfileGUI_3(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'loadProfile',
                               return_value={'test': 1}):
            with mock.patch.object(function,
                                   'switchProfile'):
                suc = function.loadProfileGUI()
                assert suc


def test_addProfileGUI_1(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=(None, None, 'cfg')):
        suc = function.addProfileGUI()
        assert not suc


def test_addProfileGUI_2(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'loadProfile',
                               return_value={}):
            with mock.patch.object(function,
                                   'storeConfig'):
                with mock.patch.object(function.app,
                                       'storeConfig'):
                    with mock.patch.object(function,
                                           'switchProfile'):
                        with mock.patch.object(gui.mainWindow.mainW,
                                               'blendProfile'):
                            suc = function.addProfileGUI()
                            assert not suc


def test_addProfileGUI_3(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'loadProfile',
                               return_value={'test': 1}):
            with mock.patch.object(function,
                                   'storeConfig'):
                with mock.patch.object(function.app,
                                       'storeConfig'):
                    with mock.patch.object(function,
                                           'switchProfile'):
                        with mock.patch.object(gui.mainWindow.mainW,
                                               'blendProfile'):
                            suc = function.addProfileGUI()
                            assert suc


def test_saveConfigAs1(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'saveProfile',
                               return_value=True):
            with mock.patch.object(function.app,
                                   'storeConfig'):
                with mock.patch.object(function,
                                       'storeConfig'):
                    suc = function.saveConfigAs()
                    assert suc


def test_saveConfigAs2(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'saveProfile',
                               return_value=False):
            with mock.patch.object(function.app,
                                   'storeConfig'):
                with mock.patch.object(function,
                                       'storeConfig'):
                    suc = function.saveConfigAs()
                    assert suc


def test_saveConfigAs3(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=(None, None, 'cfg')):
        suc = function.saveConfigAs()
        assert not suc


def test_remoteCommand_1(function):
    suc = function.remoteCommand('')
    assert suc


def test_remoteCommand_2(function):
    with mock.patch.object(function,
                           'quitSave'):
        suc = function.remoteCommand('shutdown')
        assert suc


def test_remoteCommand_3(function):
    with mock.patch.object(function,
                           'mountShutdown'):
        suc = function.remoteCommand('shutdown mount')
        assert suc


def test_remoteCommand_4(function):
    with mock.patch.object(function,
                           'mountBoot'):
        suc = function.remoteCommand('boot mount')
        assert suc
