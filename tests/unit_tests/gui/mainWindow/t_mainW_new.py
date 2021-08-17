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
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import gc

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton

# local import
from tests.unit_tests.importAddOns.baseTestSetupMainWindow import App
from gui.mainWindow.mainW import MainWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = MainWindow(App())
    yield window


def test_mwSuper(function):
    suc = function.mwSuper('')
    assert suc


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
    function.app.config['mainW']['winPosX'] = 10000
    function.app.config['mainW']['winPosY'] = 10000
    with mock.patch.object(function,
                           'mwSuper'):
        suc = function.initConfig()
        assert suc


def test_storeConfigExtendedWindows_1(function):
    suc = function.storeConfigExtendedWindows()
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


def test_closeEvent_1(function, qtbot):
    function.closeEvent(QCloseEvent())


def test_quitSave_1(function, qtbot):
    function.ui.profile.setText('test')
    suc = function.quitSave()
    assert suc


def test_setupIcons(function):
    suc = function.setupIcons()
    assert suc


def test_updateMountConnStat_1(function):
    suc = function.updateMountConnStat(True)
    assert suc
    assert function.deviceStat['mount']


def test_updateMountConnStat_2(function):
    suc = function.updateMountConnStat(False)
    assert suc
    assert not function.deviceStat['mount']


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


def test_smartFunctionGui_1(function):
    function.deviceStat['mount'] = True
    function.deviceStat['camera'] = True
    function.deviceStat['astrometry'] = True
    function.app.data.buildP = [(0, 0)]
    suc = function.smartFunctionGui()
    assert suc
    assert function.ui.runModel.isEnabled()
    assert function.ui.plateSolveSync.isEnabled()


def test_smartFunctionGui_2(function):
    function.deviceStat['mount'] = True
    function.deviceStat['camera'] = False
    function.deviceStat['astrometry'] = True
    function.app.data.buildP = [(0, 0)]
    suc = function.smartFunctionGui()
    assert suc
    assert not function.ui.runModel.isEnabled()
    assert not function.ui.plateSolveSync.isEnabled()


def test_smartFunctionGui_3(function):
    function.deviceStat['mount'] = True
    suc = function.smartFunctionGui()
    assert suc
    assert function.ui.batchModel.isEnabled()


def test_smartFunctionGui_4(function):
    function.deviceStat['mount'] = False
    suc = function.smartFunctionGui()
    assert suc
    assert not function.ui.batchModel.isEnabled()


def test_smartFunctionGui_5(function):
    function.deviceStat['environOverall'] = None
    suc = function.smartFunctionGui()
    assert suc
    assert not function.ui.refractionGroup.isEnabled()
    assert not function.ui.setRefractionManual.isEnabled()


def test_smartFunctionGui_6(function):
    function.deviceStat['environOverall'] = True
    function.deviceStat['mount'] = True
    suc = function.smartFunctionGui()
    assert suc
    assert function.ui.refractionGroup.isEnabled()
    assert function.ui.setRefractionManual.isEnabled()


def test_smartFunctionGui_7(function):
    function.deviceStat['environOverall'] = True
    function.deviceStat['mount'] = False
    suc = function.smartFunctionGui()
    assert suc
    assert not function.ui.refractionGroup.isEnabled()
    assert not function.ui.setRefractionManual.isEnabled()


def test_smartTabGui_1(function):
    suc = function.smartTabGui()
    assert suc


def test_mountBoot1(function, qtbot):
    with mock.patch.object(function.app.mount,
                           'bootMount',
                           return_value=True):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.mountBoot()
            assert suc
        assert ['Sent boot command to mount', 0] == blocker.args


def test_smartEnvironGui_1(function):
    function.deviceStat['directWeather'] = False
    function.deviceStat['sensorWeather'] = False
    function.deviceStat['onlineWeather'] = False
    function.deviceStat['skymeter'] = False
    function.deviceStat['powerWeather'] = False
    suc = function.smartEnvironGui()
    assert suc
    assert not function.ui.directWeatherGroup.isEnabled()
    assert not function.ui.sensorWeatherGroup.isEnabled()
    assert not function.ui.onlineWeatherGroup.isEnabled()
    assert not function.ui.skymeterGroup.isEnabled()
    assert not function.ui.powerGroup.isEnabled()


def test_smartEnvironGui_2(function):
    function.deviceStat['directWeather'] = True
    function.deviceStat['sensorWeather'] = True
    function.deviceStat['onlineWeather'] = True
    function.deviceStat['skymeter'] = True
    function.deviceStat['powerWeather'] = True
    suc = function.smartEnvironGui()
    assert suc
    assert function.ui.directWeatherGroup.isEnabled()
    assert function.ui.sensorWeatherGroup.isEnabled()
    assert function.ui.onlineWeatherGroup.isEnabled()
    assert function.ui.skymeterGroup.isEnabled()
    assert function.ui.powerGroup.isEnabled()


def test_smartEnvironGui_3(function):
    function.deviceStat['directWeather'] = None
    function.deviceStat['sensorWeather'] = None
    function.deviceStat['onlineWeather'] = None
    function.deviceStat['skymeter'] = None
    function.deviceStat['powerWeather'] = False
    suc = function.smartEnvironGui()
    assert suc
    assert not function.ui.directWeatherGroup.isEnabled()
    assert not function.ui.sensorWeatherGroup.isEnabled()
    assert not function.ui.onlineWeatherGroup.isEnabled()
    assert not function.ui.skymeterGroup.isEnabled()
    assert not function.ui.powerGroup.isEnabled()


def test_updateWindowsStats_1(function):
    function.function.uiWindows = {'showMessageW': {'classObj': 1,
                                          'button': QPushButton()}}
    suc = function.updateWindowsStats()
    assert suc


def test_updateDeviceStats_1(function):
    function.deviceStat = {'online': True}
    function.refractionSource = 'online'
    suc = function.updateDeviceStats()
    assert suc
    assert function.deviceStat['environOverall']


def test_updateDeviceStats_2(function):
    function.deviceStat = {'test': True}
    function.refractionSource = 'online'
    suc = function.updateDeviceStats()
    assert suc
    assert function.deviceStat['environOverall'] is None


def test_updateDeviceStats_3(function):
    function.deviceStat = {'online': True}
    function.refractionSource = 'online'
    suc = function.updateDeviceStats()
    assert suc


def test_updateDeviceStats_4(function):
    function.deviceStat = {}
    function.refractionSource = 'online'
    suc = function.updateDeviceStats()
    assert suc


def test_updateOnlineWeatherStat_1(function):
    suc = function.updateOnlineWeatherStat(True)
    assert suc
    assert function.deviceStat['onlineWeather']


def test_updateOnlineWeatherStat_2(function):
    suc = function.updateOnlineWeatherStat(False)
    assert suc
    assert not function.deviceStat['onlineWeather']


def test_updateTime_1(function):
    function.ui.isOnline.setChecked(True)
    suc = function.updateTime()
    assert suc


def test_updateTime_2(function):
    function.ui.isOnline.setChecked(False)
    suc = function.updateTime()
    assert suc


def test_updateAstrometryStatus(function):
    suc = function.updateAstrometryStatus('test')
    assert suc
    assert function.ui.astrometryText.text() == 'test'


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
        def statusText(function):
            return None

    function.app.mount.obsSite.status = 0
    suc = function.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_2(function):
    class OB:
        @staticmethod
        def statusText(function):
            return 'test'

    function.app.mount.obsSite.status = 0
    suc = function.updateStatusGUI(OB)
    assert suc
    assert function.ui.statusText.text() == 'test'


def test_updateStatusGUI_3(function):
    class OB:
        @staticmethod
        def statusText(function):
            return None

    function.app.mount.obsSite.status = 5
    suc = function.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_4(function):
    class OB:
        @staticmethod
        def statusText(function):
            return None

    function.app.mount.obsSite.status = 1
    suc = function.updateStatusGUI(OB)
    assert suc


def test_deleteWindowResource_1(function):
    suc = function.deleteWindowResource()
    assert not suc


def test_deleteWindowResource_2(function):
    suc = function.deleteWindowResource(widget=function.ui.openImageW)
    assert suc


def test_deleteWindowResource_3(function):
    class Test:
        @staticmethod
        def objectName(function):
            return 'ImageDialog'

    with mock.patch.object(gc,
                           'collect'):
        suc = function.deleteWindowResource(widget=Test())
        assert suc


def test_buildWindow_1(function):
    class Test(QObject):
        destroyed = pyqtSignal()

    function.uiWindows['showImageW']['classObj'] = Test()

    suc = function.buildWindow('showImageW')
    assert suc


def test_toggleWindow_1(function):
    suc = function.toggleWindow()
    assert suc


def test_toggleWindow_2(function):
    def Sender(function):
        return function.ui.openImageW

    function.sender = Sender
    function.uiWindows['showImageW']['classObj'] = None

    with mock.patch.object(function,
                           'buildWindow'):
        suc = function.toggleWindow()
        assert suc


def test_toggleWindow_3(function):
    def Sender(function):
        return function.ui.openImageW

    function.sender = Sender
    function.uiWindows['showImageW']['classObj'] = 1

    suc = function.toggleWindow()
    assert suc


def test_showExtendedWindows_1(function):
    with mock.patch.object(function,
                           'buildWindow'):
        suc = function.showExtendedWindows()
        assert suc


def test_closeExtendedWindows_1(function):
    suc = function.closeExtendedWindows()
    assert suc


def test_checkExtension_1(function):
    val = function.checkExtension('tests/image/test.fit', 'fit')
    assert val == 'tests/image/test.fit'


def test_checkExtension_2(function):
    val = function.checkExtension('tests/image/test', '.fit')
    assert val == 'tests/image/test.fit'


def test_mountBoot2(function, qtbot):
    with mock.patch.object(function.app.mount,
                           'bootMount',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.mountBoot()
            assert not suc
        assert ['Mount cannot be booted', 2] == blocker.args


def test_mountShutdown1(function, qtbot):
    with mock.patch.object(function.app.mount.obsSite,
                           'shutdown',
                           return_value=True):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.mountShutdown()
            assert suc
        assert ['Shutting mount down', 0] == blocker.args


def test_mountShutdown2(function, qtbot):
    with mock.patch.object(function.app.mount.obsSite,
                           'shutdown',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.mountShutdown()
            assert not suc
        assert ['Mount cannot be shutdown', 2] == blocker.args


def test_saveProfile1(function, qtbot):
    with mock.patch.object(function.app,
                           'saveConfig',
                           return_value=True):
        with qtbot.waitSignal(function.app.message) as blocker:
            app.saveProfile()
        assert ['Actual profile saved', 0] == blocker.args


def test_loadProfile1(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(function.app,
                               'loadConfig',
                               return_value=True):
            with mock.patch.object(function,
                                   'closeExtendedWindows'):
                with mock.patch.object(function,
                                       'showExtendedWindows'):
                    with mock.patch.object(function,
                                           'initConfig'):
                        with qtbot.waitSignal(function.app.message) as blocker:
                            suc = function.loadProfile()
                            assert suc
                        assert ['Profile              [test] loaded', 0] == blocker.args


def test_loadProfile2(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(function.app,
                               'loadConfig',
                               return_value=False):
            with mock.patch.object(function,
                                   'closeExtendedWindows'):
                with mock.patch.object(function,
                                       'showExtendedWindows'):
                    with mock.patch.object(function,
                                           'initConfig'):
                        with qtbot.waitSignal(function.app.message) as blocker:
                            suc = function.loadProfile()
                            assert suc
                        assert ['Profile              [test] cannot no be loaded', 2] == blocker.args


def test_loadProfile3(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=(None, None, 'cfg')):
        suc = function.loadProfile()
        assert not suc


def test_saveProfileAs1(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(function.app,
                               'saveConfig',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveProfileAs()
                assert suc
            assert ['Profile              [test] saved', 0] == blocker.args


def test_saveProfileAs2(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(function.app,
                               'saveConfig',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveProfileAs()
                assert suc
            assert ['Profile              [test] cannot no be saved', 2] == blocker.args


def test_saveProfileAs3(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=(None, None, 'cfg')):
        suc = function.saveProfileAs()
        assert not suc


def test_saveProfile2(function, qtbot):
    with mock.patch.object(function.app,
                           'saveConfig',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            function.saveProfile()
        assert ['Actual profile cannot not be saved', 2] == blocker.args


def test_remoteCommand_1(function):
    suc = function.remoteCommand('')
    assert suc


def test_remoteCommand_2(function, qtbot):
    with qtbot.waitSignal(function.app.message) as blocker:
        with mock.patch.object(function.app,
                               'quitSave'):
            suc = function.remoteCommand('shutdown')
            assert suc
            assert ['Actual profile cannot not be saved', 2] == blocker.args


def test_remoteCommand_3(function, qtbot):
    with qtbot.waitSignal(function.app.message) as blocker:
        with mock.patch.object(function,
                               'mountShutdown'):
            suc = function.remoteCommand('shutdown mount')
            assert suc
            assert ['Shutdown mount remotely', 2] == blocker.args


def test_remoteCommand_4(function, qtbot):
    with qtbot.waitSignal(function.app.message) as blocker:
        with mock.patch.object(function,
                               'mountBoot'):
            suc = function.remoteCommand('boot mount')
            assert suc
            assert ['Boot mount remotely', 2] == blocker.args
