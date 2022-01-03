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
from unittest.mock import patch
import pytest
import glob
import os
import shutil
import logging

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtCore import QTimer
from mountcontrol.qtmount import Mount
from skyfield.api import wgs84
from skyfield.api import load

# local import
from gui.mainWindow.mainW import MainWindow
from gui.extWindows.imageW import ImageWindow
from logic.environment.sensorWeather import SensorWeather
from logic.environment.directWeather import DirectWeather
from logic.environment.onlineWeather import OnlineWeather
from logic.environment.weatherUPB import WeatherUPB
from logic.environment.skymeter import Skymeter
from logic.powerswitch.kmRelay import KMRelay
from logic.powerswitch.pegasusUPB import PegasusUPB
from logic.dome.dome import Dome
from logic.camera.camera import Camera
from logic.filter.filter import Filter
from logic.focuser.focuser import Focuser
from logic.cover.cover import Cover
from logic.modeldata.buildpoints import DataPoint
from logic.remote.remote import Remote
from logic.measure.measure import MeasureData
from logic.telescope.telescope import Telescope
from logic.astrometry.astrometry import Astrometry
from base.loggerMW import addLoggingLevel
from base import packageConfig
from resource import resources
resources.qInitResources()


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global eph
    eph = load('tests/testData/de421_23.bsp')


@pytest.fixture(autouse=True, scope='function')
def function_setup_teardown(qtbot):
    global app
    class Automation:
        automateFast = False
        automateSlow = False

    class Test1(QObject):
        threadPool = QThreadPool()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        update10s = pyqtSignal()
        update30s = pyqtSignal()
        update10m = pyqtSignal()
        update1s = pyqtSignal()
        update1h = pyqtSignal()
        start1s = pyqtSignal()
        start3s = pyqtSignal()
        start5s = pyqtSignal()
        colorChange = pyqtSignal()
        hostChanged = pyqtSignal()
        mwGlob = {'imageDir': 'tests/workDir/image',
                  'dataDir': 'tests/workDir/data',
                  'modelDir': 'tests/workDir/model',
                  'tempDir': 'tests/workDir/temp',
                  'configDir': 'tests/workDir/config'}

    @staticmethod
    def testShowWindows():
        return

    @staticmethod
    def testSave(name=None):
        return

    @staticmethod
    def testStore():
        return

    @staticmethod
    def testQuit():
        return

    @staticmethod
    def testInitConfig():
        return

    class Test(QObject):
        __version__ = 'test'
        config = {'mainW': {},
                  'showImageW': True}
        update1s = pyqtSignal()
        update1h = pyqtSignal()
        redrawSimulator = pyqtSignal()
        drawHorizonPoints = pyqtSignal()
        drawBuildPoints = pyqtSignal()
        buildPointsChanged = pyqtSignal()
        updateDomeSettings = pyqtSignal()
        showImage = pyqtSignal(str)
        update3s = pyqtSignal()
        update30m = pyqtSignal()
        update10m = pyqtSignal()
        update30s = pyqtSignal()
        start1s = pyqtSignal()
        start3s = pyqtSignal()
        start5s = pyqtSignal()
        sendSatelliteData = pyqtSignal()
        remoteCommand = pyqtSignal(str)
        threadPool = QThreadPool()
        colorChange = pyqtSignal()
        hostChanged = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                              longitude_degrees=10,
                                              elevation_m=500)
        camera = Camera(app=Test1())
        filter = Filter(app=Test1())
        focuser = Focuser(app=Test1())
        sensorWeather = SensorWeather(app=Test1())
        onlineWeather = OnlineWeather(app=Test1())
        directWeather = DirectWeather(app=Test1())
        powerWeather = WeatherUPB(app=Test1())
        skymeter = Skymeter(app=Test1())
        dome = Dome(app=Test1())
        cover = Cover(app=Test1())
        telescope = Telescope(app=Test1())
        relay = KMRelay()
        remote = Remote()
        data = DataPoint(app=Test1())
        ephemeris = eph
        measure = MeasureData(app=Test1())
        power = PegasusUPB(app=Test1())
        automation = Automation()
        astrometry = Astrometry(app=Test1())
        timer0_1s = QTimer()

        uiWindows = {'showImageW': {'classObj': None}}
        mwGlob = {'imageDir': 'tests/workDir/image',
                  'dataDir': 'tests/workDir/data',
                  'modelDir': 'tests/workDir/model',
                  'configDir': 'tests/workDir/config'}
        deviceStat = {'camera': True,
                      'astrometry': True,
                      'mount': True}
        quit = testQuit
        quitSave = testQuit
        loadConfig = testQuit
        saveConfig = testSave
        storeConfig = testStore
        showWindows = testShowWindows
        initConfig = testInitConfig

    shutil.copy('tests/testData/visual.txt', 'tests/workDir/data/visual.txt')

    with mock.patch.object(MainWindow,
                           'show'):
        with mock.patch.object(ImageWindow,
                               'show'):
            packageConfig.isAvailable = True
            app = MainWindow(app=Test())
            app.log = logging.getLogger()
            addLoggingLevel('TRACE', 5)
            addLoggingLevel('UI', 35)
            yield

    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)


def test_mwSuper():
    suc = app.mwSuper('')
    assert suc


def test_initConfig_1():
    app.app.config['mainW'] = {}
    with mock.patch.object(app,
                           'mwSuper'):
        suc = app.initConfig()
        assert suc


def test_initConfig_2():
    del app.app.config['mainW']
    with mock.patch.object(app,
                           'mwSuper'):
        suc = app.initConfig()
        assert suc


def test_initConfig_3():
    app.app.config['mainW'] = {}
    app.app.config['mainW']['winPosX'] = 100
    app.app.config['mainW']['winPosY'] = 100
    with mock.patch.object(app,
                           'mwSuper'):
        suc = app.initConfig()
        assert suc


def test_initConfig_4():
    app.app.config['mainW'] = {}
    app.app.config['mainW']['winPosX'] = 10000
    app.app.config['mainW']['winPosY'] = 10000
    with mock.patch.object(app,
                           'mwSuper'):
        suc = app.initConfig()
        assert suc


def test_storeConfigExtendedWindows_1():
    suc = app.storeConfigExtendedWindows()
    assert suc


def test_storeConfig_1():
    with mock.patch.object(app,
                           'mwSuper'):
        suc = app.storeConfig()
        assert suc


def test_storeConfig_2():
    del app.app.config['mainW']
    with mock.patch.object(app,
                           'mwSuper'):
        suc = app.storeConfig()
        assert suc


def test_closeEvent_1(qtbot):
    app.closeEvent(QCloseEvent())


def test_quitSave_1(qtbot):
    app.ui.profile.setText('test')
    suc = app.quitSave()
    assert suc


def test_setupIcons():
    suc = app.setupIcons()
    assert suc


@patch('base.packageConfig.isAvailable', True)
def test_updateMountConnStat_1():
    suc = app.updateMountConnStat(True)
    assert suc
    assert app.deviceStat['mount']
    assert app.ui.mountConnected.text() == 'Mount 3D'


@patch('base.packageConfig.isAvailable', False)
def test_updateMountConnStat_2():
    suc = app.updateMountConnStat(True)
    assert suc
    assert app.deviceStat['mount']
    assert app.ui.mountConnected.text() == 'Mount'


@patch('base.packageConfig.isAvailable', True)
def test_updateMountConnStat_3():
    app.uiWindows = {'showSimulatorW': {
        'button': app.ui.mountConnected,
        'classObj': QWidget(),
        'name': 'SimulatorDialog',
        'class': None,
        }
    }
    suc = app.updateMountConnStat(False)
    assert app.ui.mountConnected.text() == 'Mount'
    assert not app.deviceStat['mount']
    assert suc


def test_updateMountWeatherStat_1():
    class S:
        weatherPressure = None
        weatherTemperature = None
        weatherStatus = None

    suc = app.updateMountWeatherStat(S())
    assert suc
    assert app.deviceStat['directWeather'] is None


def test_updateMountWeatherStat_2():
    class S:
        weatherPressure = 1000
        weatherTemperature = 10
        weatherStatus = None

    suc = app.updateMountWeatherStat(S())
    assert suc
    assert not app.deviceStat['directWeather']


def test_updateMountWeatherStat_3():
    class S:
        weatherPressure = 1000
        weatherTemperature = 10
        weatherStatus = True

    suc = app.updateMountWeatherStat(S())
    assert suc
    assert app.deviceStat['directWeather']


def test_smartFunctionGui_1():
    app.deviceStat['mount'] = True
    app.deviceStat['camera'] = True
    app.deviceStat['astrometry'] = True
    app.app.data.buildP = [(0, 0)]
    suc = app.smartFunctionGui()
    assert suc
    assert app.ui.runModel.isEnabled()
    assert app.ui.plateSolveSync.isEnabled()


def test_smartFunctionGui_2():
    app.deviceStat['mount'] = True
    app.deviceStat['camera'] = False
    app.deviceStat['astrometry'] = True
    app.app.data.buildP = [(0, 0)]
    suc = app.smartFunctionGui()
    assert suc
    assert not app.ui.runModel.isEnabled()
    assert not app.ui.plateSolveSync.isEnabled()


def test_smartFunctionGui_3():
    app.deviceStat['mount'] = True
    suc = app.smartFunctionGui()
    assert suc
    assert app.ui.batchModel.isEnabled()


def test_smartFunctionGui_4():
    app.deviceStat['mount'] = False
    suc = app.smartFunctionGui()
    assert suc
    assert not app.ui.batchModel.isEnabled()


def test_smartFunctionGui_5():
    app.deviceStat['environOverall'] = None
    suc = app.smartFunctionGui()
    assert suc
    assert not app.ui.refractionGroup.isEnabled()
    assert not app.ui.setRefractionManual.isEnabled()


def test_smartFunctionGui_6():
    app.deviceStat['environOverall'] = True
    app.deviceStat['mount'] = True
    suc = app.smartFunctionGui()
    assert suc
    assert app.ui.refractionGroup.isEnabled()
    assert app.ui.setRefractionManual.isEnabled()


def test_smartFunctionGui_7():
    app.deviceStat['environOverall'] = True
    app.deviceStat['mount'] = False
    suc = app.smartFunctionGui()
    assert suc
    assert not app.ui.refractionGroup.isEnabled()
    assert not app.ui.setRefractionManual.isEnabled()


def test_smartFunctionGui_8():
    app.deviceStat['dome'] = False
    suc = app.smartFunctionGui()
    assert suc


def test_smartFunctionGui_9():
    app.deviceStat['dome'] = True
    suc = app.smartFunctionGui()
    assert suc


def test_smartTabGui_1():
    suc = app.smartTabGui()
    assert suc


def test_smartTabGui_2():
    app.deviceStat['power'] = True
    suc = app.smartTabGui()
    assert suc


def test_mountBoot1(qtbot):
    with mock.patch.object(app.app.mount,
                           'bootMount',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.mountBoot()
            assert suc
        assert ['Sent boot command to mount', 0] == blocker.args


def test_smartEnvironGui_1():
    app.deviceStat['directWeather'] = False
    app.deviceStat['sensorWeather'] = False
    app.deviceStat['onlineWeather'] = False
    app.deviceStat['skymeter'] = False
    app.deviceStat['powerWeather'] = False
    suc = app.smartEnvironGui()
    assert suc
    assert not app.ui.directWeatherGroup.isEnabled()
    assert not app.ui.sensorWeatherGroup.isEnabled()
    assert not app.ui.onlineWeatherGroup.isEnabled()
    assert not app.ui.skymeterGroup.isEnabled()
    assert not app.ui.powerGroup.isEnabled()


def test_smartEnvironGui_2():
    app.deviceStat['directWeather'] = True
    app.deviceStat['sensorWeather'] = True
    app.deviceStat['onlineWeather'] = True
    app.deviceStat['skymeter'] = True
    app.deviceStat['powerWeather'] = True
    suc = app.smartEnvironGui()
    assert suc
    assert app.ui.directWeatherGroup.isEnabled()
    assert app.ui.sensorWeatherGroup.isEnabled()
    assert app.ui.onlineWeatherGroup.isEnabled()
    assert app.ui.skymeterGroup.isEnabled()
    assert app.ui.powerGroup.isEnabled()


def test_smartEnvironGui_3():
    app.deviceStat['directWeather'] = None
    app.deviceStat['sensorWeather'] = None
    app.deviceStat['onlineWeather'] = None
    app.deviceStat['skymeter'] = None
    app.deviceStat['powerWeather'] = False
    suc = app.smartEnvironGui()
    assert suc
    assert not app.ui.directWeatherGroup.isEnabled()
    assert not app.ui.sensorWeatherGroup.isEnabled()
    assert not app.ui.onlineWeatherGroup.isEnabled()
    assert not app.ui.skymeterGroup.isEnabled()
    assert not app.ui.powerGroup.isEnabled()


def test_updateWindowsStats_1():
    app.app.uiWindows = {'showMessageW': {'classObj': 1,
                                          'button': QPushButton()}}
    suc = app.updateWindowsStats()
    assert suc


def test_updateWindowsStats_2():
    app.app.uiWindows = {'showMessageW': {'classObj': None,
                                          'button': QPushButton()}}
    suc = app.updateWindowsStats()
    assert suc


def test_updateDeviceStats_1():
    app.deviceStat = {'online': True}
    app.refractionSource = 'online'
    suc = app.updateDeviceStats()
    assert suc
    assert app.deviceStat['environOverall']


def test_updateDeviceStats_2():
    app.deviceStat = {'test': True}
    app.refractionSource = 'online'
    suc = app.updateDeviceStats()
    assert suc
    assert app.deviceStat['environOverall'] is None


def test_updateDeviceStats_3():
    app.deviceStat = {'online': True}
    app.refractionSource = 'online'
    suc = app.updateDeviceStats()
    assert suc


def test_updateDeviceStats_4():
    app.deviceStat = {}
    app.refractionSource = 'online'
    suc = app.updateDeviceStats()
    assert suc


def test_updateDeviceStats_5():
    app.deviceStat = {'online': False}
    app.refractionSource = 'online'
    suc = app.updateDeviceStats()
    assert suc


def test_updateTime_1():
    app.ui.isOnline.setChecked(True)
    suc = app.updateTime()
    assert suc


def test_updateTime_2():
    app.ui.isOnline.setChecked(False)
    suc = app.updateTime()
    assert suc


def test_updateAstrometryStatus():
    suc = app.updateAstrometryStatus('test')
    assert suc
    assert app.ui.astrometryText.text() == 'test'


def test_updateDomeStatus():
    suc = app.updateDomeStatus('test')
    assert suc
    assert app.ui.domeText.text() == 'test'


def test_updateCameraStatus():
    suc = app.updateCameraStatus('test')
    assert suc
    assert app.ui.cameraText.text() == 'test'


def test_updateStatusGUI_1():
    class OB:
        @staticmethod
        def statusText():
            return None

    app.app.mount.obsSite.status = 0
    suc = app.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_2():
    class OB:
        @staticmethod
        def statusText():
            return 'test'

    app.app.mount.obsSite.status = 0
    suc = app.updateStatusGUI(OB)
    assert suc
    assert app.ui.statusText.text() == 'test'


def test_updateStatusGUI_3():
    class OB:
        @staticmethod
        def statusText():
            return None

    app.app.mount.obsSite.status = 5
    suc = app.updateStatusGUI(OB)
    assert suc


def test_updateStatusGUI_4():
    class OB:
        @staticmethod
        def statusText():
            return None

    app.app.mount.obsSite.status = 1
    suc = app.updateStatusGUI(OB)
    assert suc


def test_deleteWindowResource_1():
    suc = app.deleteWindowResource()
    assert not suc


def test_deleteWindowResource_2():
    suc = app.deleteWindowResource(widget=app.ui.openImageW)
    assert suc


def test_deleteWindowResource_3():
    class Test:
        @staticmethod
        def objectName():
            return 'ImageDialog'

    suc = app.deleteWindowResource(widget=Test())
    assert suc


def test_setColorSet():
    suc = app.setColorSet()
    assert suc


def test_refreshColorSet():
    with mock.patch.object(app,
                           'setupIcons'):
        suc = app.refreshColorSet()
        assert suc


def test_buildWindow_1():
    class Test(QObject):
        destroyed = pyqtSignal()

    app.uiWindows['showImageW']['classObj'] = Test()

    suc = app.buildWindow('showImageW')
    assert suc


def test_toggleWindow_1():
    suc = app.toggleWindow()
    assert suc


def test_toggleWindow_2():
    def Sender():
        return app.ui.openImageW

    app.sender = Sender
    app.uiWindows['showImageW']['classObj'] = None

    with mock.patch.object(app,
                           'buildWindow'):
        suc = app.toggleWindow()
        assert suc


def test_toggleWindow_3():
    def Sender():
        return app.ui.openImageW

    app.sender = Sender
    suc = app.toggleWindow()
    assert suc


def test_showExtendedWindows_1():
    with mock.patch.object(app,
                           'buildWindow'):
        suc = app.showExtendedWindows()
        assert suc


def test_closeExtendedWindows_1():
    suc = app.closeExtendedWindows()
    assert suc


def test_checkExtension_1():
    val = app.checkExtension('tests/workDir/image/test.fit', 'fit')
    assert val == 'tests/workDir/image/test.fit'


def test_checkExtension_2():
    val = app.checkExtension('tests/workDir/image/test', '.fit')
    assert val == 'tests/workDir/image/test.fit'


def test_mountBoot2(qtbot):
    with mock.patch.object(app.app.mount,
                           'bootMount',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.mountBoot()
            assert not suc
        assert ['Mount cannot be booted', 2] == blocker.args


def test_mountShutdown1(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'shutdown',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.mountShutdown()
            assert suc
        assert ['Shutting mount down', 0] == blocker.args


def test_mountShutdown2(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'shutdown',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.mountShutdown()
            assert not suc
        assert ['Mount cannot be shutdown', 2] == blocker.args


def test_saveProfile1(qtbot):
    with mock.patch.object(app.app,
                           'saveConfig',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            app.saveProfile()
        assert ['Actual profile saved', 0] == blocker.args


def test_loadProfile1(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app.app,
                               'loadConfig',
                               return_value=True):
            with mock.patch.object(app,
                                   'closeExtendedWindows'):
                with mock.patch.object(app,
                                       'showExtendedWindows'):
                    with mock.patch.object(app,
                                           'initConfig'):
                        with qtbot.waitSignal(app.app.message) as blocker:
                            suc = app.loadProfile()
                            assert suc
                        assert ['Profile              [test] loaded', 0] == blocker.args


def test_loadProfile2(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app.app,
                               'loadConfig',
                               return_value=False):
            with mock.patch.object(app,
                                   'closeExtendedWindows'):
                with mock.patch.object(app,
                                       'showExtendedWindows'):
                    with mock.patch.object(app,
                                           'initConfig'):
                        with qtbot.waitSignal(app.app.message) as blocker:
                            suc = app.loadProfile()
                            assert suc
                        assert ['Profile              [test] cannot no be loaded', 2] == blocker.args


def test_loadProfile3(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=(None, None, 'cfg')):
        suc = app.loadProfile()
        assert not suc


def test_saveProfileAs1(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app.app,
                               'saveConfig',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveProfileAs()
                assert suc
            assert ['Profile              [test] saved', 0] == blocker.args


def test_saveProfileAs2(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app.app,
                               'saveConfig',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveProfileAs()
                assert suc
            assert ['Profile              [test] cannot no be saved', 2] == blocker.args


def test_saveProfileAs3(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=(None, None, 'cfg')):
        suc = app.saveProfileAs()
        assert not suc


def test_saveProfile2(qtbot):
    with mock.patch.object(app.app,
                           'saveConfig',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            app.saveProfile()
        assert ['Actual profile cannot not be saved', 2] == blocker.args


def test_remoteCommand_1():
    suc = app.remoteCommand('')
    assert suc


def test_remoteCommand_2(qtbot):
    with qtbot.waitSignal(app.app.message) as blocker:
        with mock.patch.object(app.app,
                               'quitSave'):
            suc = app.remoteCommand('shutdown')
            assert suc
            assert ['Actual profile cannot not be saved', 2] == blocker.args


def test_remoteCommand_3(qtbot):
    with qtbot.waitSignal(app.app.message) as blocker:
        with mock.patch.object(app,
                               'mountShutdown'):
            suc = app.remoteCommand('shutdown mount')
            assert suc
            assert ['Shutdown mount remotely', 2] == blocker.args


def test_remoteCommand_4(qtbot):
    with qtbot.waitSignal(app.app.message) as blocker:
        with mock.patch.object(app,
                               'mountBoot'):
            suc = app.remoteCommand('boot mount')
            assert suc
            assert ['Boot mount remotely', 2] == blocker.args
