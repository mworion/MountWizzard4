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
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from base import packageConfig
from resource import resources
import gui.utilities.toolsQtWidget
from gui.mainWindow.mainWindow import MainWindow
resources.qInitResources()


@pytest.fixture(autouse=True, scope='module')
def window(qapp):

    packageConfig.isAvailable = True
    with mock.patch.object(MainWindow,
                           'show'):
        window = MainWindow(app=App())
        yield window

    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)


def test_initConfig_1(window):
    window.app.config['mainW'] = {}
    window.initConfig()


def test_initConfig_2(window):
    del window.app.config['mainW']
    window.initConfig()


def test_initConfig_3(window):
    window.app.config['mainW'] = {}
    window.app.config['mainW']['winPosX'] = 100
    window.app.config['mainW']['winPosY'] = 100
    window.initConfig()


def test_initConfig_4(window):
    window.app.config['mainW'] = {}
    window.app.config['mainW']['winPosX'] = 10000
    window.app.config['mainW']['winPosY'] = 10000
    window.initConfig()


def test_storeConfig_1(window):
    with mock.patch.object(window.mainWindowAddons,
                           'storeConfig'):
        with mock.patch.object(window.externalWindows,
                               'storeConfig'):
            window.storeConfig()


def test_storeConfig_2(window):
    del window.app.config['mainW']
    with mock.patch.object(window.mainWindowAddons,
                           'storeConfig'):
        with mock.patch.object(window.externalWindows,
                               'storeConfig'):
            window.storeConfig()


def test_setupIcons_1(window):
    with mock.patch.object(window.mainWindowAddons,
                           'setupIcons'):
        window.setupIcons()


def test_updateColorSet_1(window):
    with mock.patch.object(window.mainWindowAddons,
                           'updateColorSet'):
        window.updateColorSet()


def test_closeEvent_1(window):
    with mock.patch.object(window.externalWindows,
                           'closeExtendedWindows'):
        with mock.patch.object(window.mainWindowAddons.addons['SettDevice'],
                               'stopDrivers'):
            with mock.patch.object(window.threadPool,
                                   'waitForDone'):
                window.closeEvent(QCloseEvent())


def test_enableTabsMovable(window):
    window.enableTabsMovable()


def test_quitSave_1(window):
    window.ui.profile.setText('test')
    with mock.patch.object(window,
                           'saveConfig'):
        with mock.patch.object(gui.mainWindow.mainW,
                               'saveProfile'):
            with mock.patch.object(window,
                                   'close'):
                suc = window.quitSave()
                assert suc


@patch('base.packageConfig.isAvailable', True)
def test_updateMountConnStat_1(window):
    suc = window.updateMountConnStat(True)
    assert suc
    assert window.deviceStat['mount']
    assert window.ui.mountConnected.text() == 'Mount 3D'


@patch('base.packageConfig.isAvailable', False)
def test_updateMountConnStat_2(window):
    suc = window.updateMountConnStat(True)
    assert suc
    assert window.deviceStat['mount']
    assert window.ui.mountConnected.text() == 'Mount'


@patch('base.packageConfig.isAvailable', True)
def test_updateMountConnStat_3(window):
    test = window.externalWindows.uiWindows
    window.uiWindows = {'showSimulatorW': {
        'button': window.ui.mountConnected,
        'classObj': QWidget(),
        'name': 'SimulatorDialog',
        'class': None,
        }
    }
    suc = window.updateMountConnStat(False)
    assert window.ui.mountConnected.text() == 'Mount'
    assert not window.deviceStat['mount']
    assert suc
    window.uiWindows = test

def test_updateMountWeatherStat_1(window):
    class S:
        weatherPressure = None
        weatherTemperature = None
        weatherStatus = None

    suc = window.updateMountWeatherStat(S())
    assert suc
    assert window.deviceStat['directWeather'] is None


def test_updateMountWeatherStat_2(window):
    class S:
        weatherPressure = 1000
        weatherTemperature = 10
        weatherStatus = None

    suc = window.updateMountWeatherStat(S())
    assert suc
    assert not window.deviceStat['directWeather']


def test_updateMountWeatherStat_3(window):
    class S:
        weatherPressure = 1000
        weatherTemperature = 10
        weatherStatus = True

    suc = window.updateMountWeatherStat(S())
    assert suc
    assert window.deviceStat['directWeather']


def test_smartwindowGui_0(window):
    window.deviceStat['mount'] = True
    window.deviceStat['camera'] = True
    window.deviceStat['plateSolve'] = True
    window.app.data.buildP = []
    window.ui.pauseModel.setProperty('pause', False)
    suc = window.smartwindowGui()
    assert suc
    assert window.ui.plateSolveSync.isEnabled()


def test_smartwindowGui_1(window):
    window.deviceStat['mount'] = True
    window.deviceStat['camera'] = True
    window.deviceStat['plateSolve'] = True
    window.app.data.buildP = [(0, 0)]
    suc = window.smartwindowGui()
    assert suc
    assert window.ui.runModel.isEnabled()
    assert window.ui.plateSolveSync.isEnabled()
    assert window.ui.dataModel.isEnabled()
    assert window.ui.runFlexure.isEnabled()
    assert window.ui.runHysteresis.isEnabled()


def test_smartwindowGui_2(window):
    window.deviceStat['mount'] = True
    window.deviceStat['camera'] = False
    window.deviceStat['plateSolve'] = True
    window.app.data.buildP = [(0, 0)]
    suc = window.smartwindowGui()
    assert suc
    assert not window.ui.runModel.isEnabled()
    assert not window.ui.plateSolveSync.isEnabled()
    assert not window.ui.dataModel.isEnabled()
    assert not window.ui.runFlexure.isEnabled()
    assert not window.ui.runHysteresis.isEnabled()


def test_smartwindowGui_3(window):
    window.deviceStat['mount'] = True
    suc = window.smartwindowGui()
    assert suc
    assert window.ui.refractionGroup.isEnabled()
    assert window.ui.dsoGroup.isEnabled()
    assert window.ui.mountCommandTable.isEnabled()


def test_smartwindowGui_4(window):
    window.deviceStat['mount'] = False
    suc = window.smartwindowGui()
    assert suc
    assert not window.ui.refractionGroup.isEnabled()
    assert not window.ui.dsoGroup.isEnabled()
    assert not window.ui.mountCommandTable.isEnabled()


def test_smartwindowGui_5(window):
    window.deviceStat['dome'] = True
    window.deviceStat['mount'] = True
    suc = window.smartwindowGui()
    assert suc
    assert window.ui.useDomeAz.isEnabled()


def test_smartwindowGui_6(window):
    window.deviceStat['dome'] = False
    window.deviceStat['mount'] = False
    suc = window.smartwindowGui()
    assert suc
    assert not window.ui.useDomeAz.isEnabled()


def test_smartTabGui_1(window):
    suc = window.smartTabGui()
    assert suc


def test_smartTabGui_2(window):
    window.deviceStat['power'] = True
    suc = window.smartTabGui()
    assert suc


def test_mountBoot1(window):
    with mock.patch.object(window.app.mount,
                           'bootMount',
                           return_value=True):
        suc = window.mountBoot()
        assert suc


def test_updateWindowsStats_1(window):
    test = window.externalWindows.uiWindows
    window.uiWindows = {'showMessageW': {'classObj': 1,
                                           'button': QPushButton()}}
    suc = window.updateWindowsStats()
    assert suc
    window.uiWindows = test


def test_updateWindowsStats_2(window):
    test = window.externalWindows.uiWindows
    window.uiWindows = {'showMessageW': {'classObj': None,
                                           'button': QPushButton()}}
    suc = window.updateWindowsStats()
    assert suc
    window.uiWindows = test


def test_setEnvironDeviceStats_1(window):
    window.ui.showTabEnviron.setChecked(True)
    window.app.mount.setting.statusRefraction = 0

    suc = window.setEnvironDeviceStats()
    assert suc
    assert window.deviceStat['refraction'] is None


def test_setEnvironDeviceStats_2(window):
    window.ui.showTabEnviron.setChecked(True)
    window.ui.refracManual.setChecked(True)
    window.app.mount.setting.statusRefraction = 1

    suc = window.setEnvironDeviceStats()
    assert suc
    assert window.deviceStat['refraction']


def test_setEnvironDeviceStats_3(window):
    window.ui.showTabEnviron.setChecked(True)
    window.ui.refracCont.setChecked(True)
    window.app.mount.setting.statusRefraction = 1
    window.refractionSource = 'onlineWeather'
    window.deviceStat['onlineWeather'] = False

    suc = window.setEnvironDeviceStats()
    assert suc
    assert not window.deviceStat['refraction']


def test_updateDeviceStats_1(window):
    window.deviceStatGui = {'onlineWeather': QWidget()}
    window.deviceStat = {'onlineWeather': True}
    suc = window.updateDeviceStats()
    assert suc


def test_updateDeviceStats_2(window):
    window.deviceStatGui = {'onlineWeather': QWidget()}
    window.deviceStat = {'onlineWeather': False}
    suc = window.updateDeviceStats()
    assert suc


def test_updateDeviceStats_3(window):
    window.deviceStatGui = {'onlineWeather': QWidget()}
    window.deviceStat = {'onlineWeather': None}
    suc = window.updateDeviceStats()
    assert suc


def test_updateControllerStatus_1(window):
    suc = window.updateControllerStatus()
    assert suc


def test_updateThreadAndOnlineStatus_1(window):
    window.app.mwGlob['workDir'] = 'tests/workDir'
    window.ui.isOnline.setChecked(True)
    with mock.patch.object(shutil,
                           'disk_usage',
                           return_value=(100, 100, 100)):
        suc = window.updateThreadAndOnlineStatus()
        assert suc


def test_updateThreadAndOnlineStatus_2(window):
    window.app.mwGlob['workDir'] = 'tests/workDir'
    window.ui.isOnline.setChecked(False)
    with mock.patch.object(shutil,
                           'disk_usage',
                           return_value=(100, 100, 100)):
        suc = window.updateThreadAndOnlineStatus()
        assert suc


def test_updateTime_1(window):
    suc = window.updateTime()
    assert suc


def test_updatePlateSolveStatus(window):
    suc = window.updatePlateSolveStatus('test')
    assert suc
    assert window.ui.plateSolveText.text() == 'test'


def test_updateDomeStatus(window):
    suc = window.updateDomeStatus('test')
    assert suc
    assert window.ui.domeText.text() == 'test'


def test_updateCameraStatus(window):
    suc = window.updateCameraStatus('test')
    assert suc
    assert window.ui.cameraText.text() == 'test'


def test_updateStatusGUI_1(window):
    class OB:
        @staticmethod
        def statusText():
            return None

    window.app.mount.obsSite.status = 0
    suc = window.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_2(window):
    class OB:
        @staticmethod
        def statusText():
            return 'test'

    window.app.mount.obsSite.status = 0
    suc = window.updateStatusGUI(OB)
    assert suc
    assert window.ui.statusText.text() == 'test'


def test_updateStatusGUI_3(window):
    class OB:
        @staticmethod
        def statusText():
            return None

    window.app.mount.obsSite.status = 5
    suc = window.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_4(window):
    class OB:
        @staticmethod
        def statusText():
            return None

    window.app.mount.obsSite.status = 1
    suc = window.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_5(window):
    class OB:
        @staticmethod
        def statusText():
            return None

    window.app.mount.obsSite.status = 10
    window.satStatus = False
    suc = window.updateStatusGUI(OB)
    assert suc


def test_setColorSet(window):
    suc = window.setColorSet()
    assert suc


def test_refreshColorSet(window):
    with mock.patch.object(window,
                           'setupIcons'):
        with mock.patch.object(window,
                               'setColorSet'):
            with mock.patch.object(window,
                                   'setStyleSheet'):
                suc = window.updateColorSet()
                assert suc


def test_checkExtension_1(window):
    val = window.checkExtension('tests/workDir/image/test.fit', 'fit')
    assert val == 'tests/workDir/image/test.fit'


def test_checkExtension_2(window):
    val = window.checkExtension('tests/workDir/image/test', '.fit')
    assert val == 'tests/workDir/image/test.fit'


def test_mountBoot1(window):
    with mock.patch.object(window.app.mount,
                           'bootMount',
                           return_value=False):
        suc = window.mountBoot()
        assert not suc


def test_mountShutdown1(window):
    with mock.patch.object(window.app.mount,
                           'shutdown',
                           return_value=True):
        suc = window.mountShutdown()
        assert suc


def test_mountShutdown2(window):
    with mock.patch.object(window.app.mount,
                           'shutdown',
                           return_value=False):
        suc = window.mountShutdown()
        assert not suc


def test_saveConfig1(window):
    with mock.patch.object(window,
                           'storeConfig'):
        with mock.patch.object(window.app,
                               'storeConfig'):
            with mock.patch.object(gui.mainWindow.mainW,
                                   'saveProfile',
                                   return_value=True):
                suc = window.saveConfig()
                assert suc


def test_saveConfig2(window):
    with mock.patch.object(window,
                           'storeConfig'):
        with mock.patch.object(window.app,
                               'storeConfig'):
            with mock.patch.object(gui.mainWindow.mainW,
                                   'saveProfile',
                                   return_value=False):
                suc = window.saveConfig()
                assert not suc


def test_switchProfile_1(window):
    loc = wgs84.latlon(latitude_degrees=10, longitude_degrees=10)
    with mock.patch.object(window.externalWindows,
                           'closeExtendedWindows'):
        with mock.patch.object(window.externalWindows,
                               'showExtendedWindows'):
            with mock.patch.object(window,
                                   'initConfig'):
                with mock.patch.object(window.app,
                                       'initConfig',
                                       return_value=loc):
                    with mock.patch.object(window,
                                           'stopDrivers'):
                        suc = window.switchProfile({'test': 1})
                        assert suc


def test_loadProfileGUI_1(window):
    with mock.patch.object(window,
                           'openFile',
                           return_value=(None, None, 'cfg')):
        suc = window.loadProfileGUI()
        assert not suc


def test_loadProfileGUI2(window):
    with mock.patch.object(window,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'loadProfile',
                               return_value={}):
            with mock.patch.object(window,
                                   'switchProfile'):
                suc = window.loadProfileGUI()
                assert not suc


def test_loadProfileGUI_3(window):
    with mock.patch.object(window,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'loadProfile',
                               return_value={'test': 1}):
            with mock.patch.object(window,
                                   'switchProfile'):
                suc = window.loadProfileGUI()
                assert suc


def test_addProfileGUI_1(window):
    with mock.patch.object(window,
                           'openFile',
                           return_value=(None, None, 'cfg')):
        suc = window.addProfileGUI()
        assert not suc


def test_addProfileGUI_2(window):
    with mock.patch.object(window,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'loadProfile',
                               return_value={}):
            with mock.patch.object(window,
                                   'storeConfig'):
                with mock.patch.object(window.app,
                                       'storeConfig'):
                    with mock.patch.object(window,
                                           'switchProfile'):
                        with mock.patch.object(gui.mainWindow.mainW,
                                               'blendProfile'):
                            suc = window.addProfileGUI()
                            assert not suc


def test_addProfileGUI_3(window):
    with mock.patch.object(window,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'loadProfile',
                               return_value={'test': 1}):
            with mock.patch.object(window,
                                   'storeConfig'):
                with mock.patch.object(window.app,
                                       'storeConfig'):
                    with mock.patch.object(window,
                                           'switchProfile'):
                        with mock.patch.object(gui.mainWindow.mainW,
                                               'blendProfile'):
                            suc = window.addProfileGUI()
                            assert suc


def test_saveConfigAs1(window):
    with mock.patch.object(window,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'saveProfile',
                               return_value=True):
            with mock.patch.object(window.app,
                                   'storeConfig'):
                with mock.patch.object(window,
                                       'storeConfig'):
                    suc = window.saveConfigAs()
                    assert suc


def test_saveConfigAs2(window):
    with mock.patch.object(window,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(gui.mainWindow.mainW,
                               'saveProfile',
                               return_value=False):
            with mock.patch.object(window.app,
                                   'storeConfig'):
                with mock.patch.object(window,
                                       'storeConfig'):
                    suc = window.saveConfigAs()
                    assert suc


def test_saveConfigAs3(window):
    with mock.patch.object(window,
                           'saveFile',
                           return_value=(None, None, 'cfg')):
        suc = window.saveConfigAs()
        assert not suc


def test_remoteCommand_1(window):
    suc = window.remoteCommand('')
    assert suc


def test_remoteCommand_2(window):
    with mock.patch.object(window,
                           'quitSave'):
        suc = window.remoteCommand('shutdown')
        assert suc


def test_remoteCommand_3(window):
    with mock.patch.object(window,
                           'mountShutdown'):
        suc = window.remoteCommand('shutdown mount')
        assert suc


def test_remoteCommand_4(window):
    with mock.patch.object(window,
                           'mountBoot'):
        suc = window.remoteCommand('boot mount')
        assert suc
