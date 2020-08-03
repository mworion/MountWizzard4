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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import logging
import subprocess
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtMultimedia import QSound
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
import requests
import importlib_metadata

# local import
from mw4.gui.mainWmixin.tabSettMisc import SettMisc
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.base.loggerMW import CustomLogger
from mw4.dome.dome import Dome
from mw4.imaging.camera import Camera
from mw4.astrometry.astrometry import Astrometry
from mw4.environment.onlineWeather import OnlineWeather


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='mw4/test/data')
        update1s = pyqtSignal()
        update10s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='mw4/test/data')
        dome = Dome(app=Test1())
        camera = Camera(app=Test1())
        astrometry = Astrometry(app=Test1())
        onlineWeather = OnlineWeather(app=Test1())

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettMisc(app=Test(), ui=ui,
                   clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.deviceStat = dict()
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()

    qtbot.addWidget(app)

    yield

    app.threadPool.waitForDone(1000)


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_initConfig_2():
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setWeatherOnline_1():
    app.app.onlineWeather = None
    suc = app.setWeatherOnline()
    assert not suc


def test_setWeatherOnline_2():
    suc = app.setWeatherOnline()
    assert suc


def test_setupIERS_1():
    app.ui.isOnline.setChecked(False)
    suc = app.setupIERS()
    assert suc


def test_setupIERS_2():
    app.ui.isOnline.setChecked(True)
    suc = app.setupIERS()
    assert suc


def test_versionPackage_1():
    class Test:
        status_code = 300

        @staticmethod
        def json():
            return {'releases': {}}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test(),
                           side_effect=Exception()):
        val = app.versionPackage('matplotlib')
        assert val is None


def test_versionPackage_2():
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return {'releases': {'1.0.0': 1,
                                 '1.1.0b1': 2}}

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.versionPackage('matplotlib')
        assert val == '1.0.0'


def test_versionPackage_3():
    class Test:
        status_code = 200

        @staticmethod
        def json():
            return {'releases': {'1.0.0': 1,
                                 '1.0.0b1': 2}}

    app.ui.versionBeta.setChecked(True)
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        val = app.versionPackage('matplotlib')
        assert val == '1.0.0b1'


def test_showUpdates_1():
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        suc = app.showUpdates()
        assert not suc


def test_showUpdates_2():
    app.ui.isOnline.setChecked(True)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        with mock.patch.object(app,
                               'versionPackage',
                               return_value=None):
            suc = app.showUpdates()
            assert not suc


def test_showUpdates_3():
    app.ui.isOnline.setChecked(True)
    with mock.patch.object(importlib_metadata,
                           'version',
                           return_value='0.148.8'):
        with mock.patch.object(app,
                               'versionPackage',
                               return_value='0.148.9'):
            suc = app.showUpdates()
            assert suc


def test_isVenv_1():
    app.isVenv()


def test_formatPIP_1():
    line = app.formatPIP()
    assert line == ''


def test_formatPIP_2():
    line = app.formatPIP('   ')
    assert line == ''


def test_formatPIP_3():
    line = app.formatPIP('Requirement already satisfied: mountcontrol in /Users (0.157)')
    assert line == 'Requirement already satisfied : mountcontrol'


def test_formatPIP_4():
    line = app.formatPIP('Collecting mountcontrol==0.157')
    assert line == 'Collecting mountcontrol'


def test_formatPIP_5():
    line = app.formatPIP('Installing collected packages: mountcontrol')
    assert line == 'Installing collected packages'


def test_formatPIP_6():
    line = app.formatPIP('Successfully installed mountcontrol-0.156')
    assert line == 'Successfully installed mountcontrol-0.156'


def test_runInstall_1():
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
        with mock.patch.object(app,
                               'formatPIP',
                               return_value=''):
            suc, val = app.runInstall()
            assert suc


def test_runInstall_2():
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def readline():
            return ['test1', 'test2']

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
        with mock.patch.object(app,
                               'formatPIP',
                               return_value=''):
            suc, val = app.runInstall()
            assert not suc


def test_runInstall_3():
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
                           return_value=Test(),
                           side_effect=Exception('TimeoutExpired')):
        with mock.patch.object(app,
                               'formatPIP',
                               return_value=''):
            suc, val = app.runInstall()
            assert not suc


def test_installFinished_1():
    app.mutexInstall.lock()
    suc = app.installFinished(None)
    assert not suc


def test_installFinished_2():
    app.mutexInstall.lock()
    suc = app.installFinished((False, '0.148.8'))
    assert not suc


def test_installFinished_3():
    app.mutexInstall.lock()
    suc = app.installFinished((True, '0.148.8'))
    assert suc


def test_installVersion_1():
    with mock.patch.object(app,
                           'isVenv',
                           return_value=False):
        suc = app.installVersion()
        assert not suc


def test_installVersion_2():
    app.mutexInstall.lock()
    with mock.patch.object(app,
                           'isVenv',
                           return_value=True):
        suc = app.installVersion()
        assert not suc


def test_installVersion_3():
    with mock.patch.object(app,
                           'isVenv',
                           return_value=True):
        with mock.patch.object(app.threadPool,
                               'start',
                               return_value=True):
            suc = app.installVersion()
            assert suc


def test_setLoggingLevel1(qtbot):
    app.ui.loglevelDebug.setChecked(True)
    app.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 20


def test_setLoggingLevel2(qtbot):
    app.ui.loglevelInfo.setChecked(True)
    app.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 30


def test_setLoggingLevel3(qtbot):
    app.ui.loglevelDeepDebug.setChecked(True)
    app.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 10


def test_updateFwGui_productName():
    value = 'Test1234'
    app.app.mount.firmware.product = value
    app.updateFwGui(app.app.mount.firmware)
    assert value == app.ui.product.text()
    value = None
    app.app.mount.firmware.product = value
    app.updateFwGui(app.app.mount.firmware)
    assert '-' == app.ui.product.text()


def test_updateFwGui_hwVersion():
    value = 'Test1234'
    app.app.mount.firmware.hardware = value
    app.updateFwGui(app.app.mount.firmware)
    assert value == app.ui.hardware.text()
    value = None
    app.app.mount.firmware.hardware = value
    app.updateFwGui(app.app.mount.firmware)
    assert '-' == app.ui.hardware.text()


def test_updateFwGui_numberString():
    value = '2.15.18'
    app.app.mount.firmware.vString = value
    app.updateFwGui(app.app.mount.firmware)
    assert value == app.ui.vString.text()
    value = None
    app.app.mount.firmware.vString = value
    app.updateFwGui(app.app.mount.firmware)
    assert '-' == app.ui.vString.text()


def test_updateFwGui_fwdate():
    value = 'Test1234'
    app.app.mount.firmware.date = value
    app.updateFwGui(app.app.mount.firmware)
    assert value == app.ui.fwdate.text()
    value = None
    app.app.mount.firmware.date = value
    app.updateFwGui(app.app.mount.firmware)
    assert '-' == app.ui.fwdate.text()


def test_updateFwGui_fwtime():
    value = 'Test1234'
    app.app.mount.firmware.time = value
    app.updateFwGui(app.app.mount.firmware)
    assert value == app.ui.fwtime.text()
    value = None
    app.app.mount.firmware.time = value
    app.updateFwGui(app.app.mount.firmware)
    assert '-' == app.ui.fwtime.text()


def test_playAudioDomeSlewFinished_1():
    with mock.patch.object(QSound,
                           'play'):
        suc = app.playSound('DomeSlew')
        # todo not suc is wrong, just workaround
        assert not suc


def test_playAudioMountSlewFinished_1():
    with mock.patch.object(QSound,
                           'play'):
        suc = app.playSound('MountSlew')
        assert not suc


def test_playAudioMountAlert_1():
    with mock.patch.object(QSound,
                           'play'):
        suc = app.playSound('MountAlert')
        assert not suc


def test_playAudioModelFinished_1():
    with mock.patch.object(QSound,
                           'play'):
        suc = app.playSound('ModelFinished')
        assert not suc


def test_playSound_1():
    suc = app.playSound()
    assert not suc


def test_playSound_2():
    suc = app.playSound('test')
    assert not suc


def test_playSound_3():
    app.audioSignalsSet['Pan1'] = 'test'
    app.guiAudioList['MountSlew'] = app.ui.soundMountSlewFinished
    app.guiAudioList['MountSlew'].addItem('Pan1')
    with mock.patch.object(QSound,
                           'play'):
        suc = app.playSound('MountSlew')
        assert suc
