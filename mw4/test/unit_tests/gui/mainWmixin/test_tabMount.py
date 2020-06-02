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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import logging
import pytest
import faulthandler
faulthandler.enable()

# external packages
import PyQt5
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol import qtmount

# local import
from mw4.gui.mainWmixin.tabMount import Mount
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, app

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = qtmount.Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mwGlob = {'modelDir': 'mw4/test/model',
                  'imageDir': 'mw4/test/image'}
        uiWindows = {'showImageW': {'classObj': None}}

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = Mount(app=Test(), ui=ui,
                clickable=MWidget().clickable)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.guiSetText = MWidget().guiSetText
    app.deleteLater = MWidget().deleteLater
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()
    app.config = {'mainW': {}}
    app.deviceStat = {}

    qtbot.addWidget(app)

    yield

    app.threadPool.waitForDone(1000)


def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_updatePointGui_alt():
    value = '45'
    app.app.mount.obsSite.Alt = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '45.00' == app.ui.ALT.text()
    value = None
    app.app.mount.obsSite.Alt = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '-' == app.ui.ALT.text()


def test_updatePointGui_az():
    value = '45'
    app.app.mount.obsSite.Az = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '45.00' == app.ui.AZ.text()
    value = None
    app.app.mount.obsSite.Az = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '-' == app.ui.AZ.text()


def test_updatePointGui_ra():
    value = '45'
    app.app.mount.obsSite.raJNow = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '45:00:00' == app.ui.RA.text()
    value = None
    app.app.mount.obsSite.raJNow = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '-' == app.ui.RA.text()


def test_updatePointGui_dec():
    value = '45'
    app.app.mount.obsSite.decJNow = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '+45:00:00' == app.ui.DEC.text()
    value = None
    app.app.mount.obsSite.decJNow = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '-' == app.ui.DEC.text()


def test_updatePointGui_pierside():
    value = 'W'
    app.app.mount.obsSite.pierside = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert 'WEST' == app.ui.pierside.text()
    value = None
    app.app.mount.obsSite.pierside = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '-' == app.ui.pierside.text()


def test_updatePointGui_ha():
    value = '12'
    app.app.mount.obsSite.raJNow = value
    app.app.mount.obsSite.timeSidereal = '00:00:00'
    app.updatePointGUI(app.app.mount.obsSite)
    assert '12:00:00' == app.ui.HA.text()
    value = None
    app.app.mount.obsSite.timeSidereal = '00:00:00'
    app.app.mount.obsSite.raJNow = value
    app.updatePointGUI(app.app.mount.obsSite)
    assert '-' == app.ui.HA.text()


def test_updateTimeGui_sidereal():
    value = '45:45:45'
    app.app.mount.obsSite.timeSidereal = value
    app.updateTimeGUI(app.app.mount.obsSite)
    assert '45:45:45' == app.ui.timeSidereal.text()
    value = None
    app.app.mount.obsSite.timeSidereal = value
    app.updateTimeGUI(app.app.mount.obsSite)
    assert '-' == app.ui.timeSidereal.text()


"""
def test_updateStatusGui_statusText():
    app.app.mount.obsSite.status = 6
    app.updateStatusGUI(app.app.mount.obsSite)
    assert 'Slewing or going to stop' == app.ui.statusText.text()
    app.app.mount.obsSite.status = None
    app.updateStatusGUI(app.app.mount.obsSite)
    assert '-' == app.ui.statusText.text()
"""


def test_updateSetting_slewRate():
    value = '15'
    app.app.mount.setting.slewRate = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '15' == app.ui.slewRate.text()
    value = None
    app.app.mount.setting.slewRate = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.slewRate.text()


def test_updateSetting_timeToFlip():
    value = '15'
    app.app.mount.setting.timeToFlip = value
    app.updateSettingGUI(app.app.mount.setting)
    assert ' 15' == app.ui.timeToFlip.text()
    value = None
    app.app.mount.setting.timeToFlip = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.timeToFlip.text()


def test_updateSettingExt_UTCExpire():
    value = '2020-10-05'
    app.app.mount.setting.UTCExpire = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert value == app.ui.UTCExpire.text()
    value = None
    app.app.mount.setting.UTCExpire = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert '-' == app.ui.UTCExpire.text()


def test_updateSettingExt_UTCExpire1():
    value = '2016-10-05'
    app.app.mount.setting.UTCExpire = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert value == app.ui.UTCExpire.text()
    value = None
    app.app.mount.setting.UTCExpire = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert '-' == app.ui.UTCExpire.text()


def test_updateSettingExt_UTCExpire2():
    value = '2018-10-05'
    app.app.mount.setting.UTCExpire = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert value == app.ui.UTCExpire.text()
    value = None
    app.app.mount.setting.UTCExpire = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert '-' == app.ui.UTCExpire.text()


def test_updateSetting_statusUnattendedFlip():
    value = '1'
    app.app.mount.setting.statusUnattendedFlip = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert 'ON' == app.ui.statusUnattendedFlip.text()
    value = None
    app.app.mount.setting.statusUnattendedFlip = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert 'OFF' == app.ui.statusUnattendedFlip.text()


def test_updateSetting_statusDualAxisTracking():
    value = '1'
    app.app.mount.setting.statusDualAxisTracking = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert 'ON' == app.ui.statusDualAxisTracking.text()
    value = None
    app.app.mount.setting.statusDualAxisTracking = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert 'OFF' == app.ui.statusDualAxisTracking.text()


def test_updateSetting_statusRefraction():
    value = '1'
    app.app.mount.setting.statusRefraction = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert 'ON' == app.ui.statusRefraction.text()
    value = None
    app.app.mount.setting.statusRefraction = value
    app.updateSetStatGUI(app.app.mount.setting)
    assert 'OFF' == app.ui.statusRefraction.text()


def test_updateSetSyncGUI_1():
    app.app.mount.setting.gpsSynced = True
    suc = app.updateSetSyncGUI(app.app.mount.setting)
    assert app.ui.statusGPSSynced.text() == 'YES'
    assert suc


def test_updateSetSyncGUI_2():
    app.app.mount.setting.gpsSynced = False
    suc = app.updateSetSyncGUI(app.app.mount.setting)
    assert app.ui.statusGPSSynced.text() == 'NO'
    assert suc


def test_updateSetSyncGUI_3():
    app.app.mount.setting.typeConnection = None
    app.app.mount.setting.wakeOnLan = '0'
    suc = app.updateSetSyncGUI(app.app.mount.setting)
    assert suc


def test_updateSetSyncGUI_4():
    app.app.mount.setting.typeConnection = 1
    app.app.mount.setting.wakeOnLan = None
    suc = app.updateSetSyncGUI(app.app.mount.setting)
    assert suc


def test_tracking_speed1():
    with mock.patch.object(app.app.mount.obsSite,
                           'checkRateLunar',
                           return_value=True):
        suc = app.updateTrackingGui(app.app.mount.obsSite)
        assert suc


def test_tracking_speed2():
    with mock.patch.object(app.app.mount.obsSite,
                           'checkRateSidereal',
                           return_value=True):
        suc = app.updateTrackingGui(app.app.mount.obsSite)
        assert suc


def test_tracking_speed3():
    with mock.patch.object(app.app.mount.obsSite,
                           'checkRateSolar',
                           return_value=True):
        suc = app.updateTrackingGui(app.app.mount.obsSite)
        assert suc


def test_setLunarTracking1(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'setLunarTracking',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.setLunarTracking()
            assert suc
        assert ['Tracking set to Lunar', 0] == blocker.args


def test_setLunarTracking2(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'setLunarTracking',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.setLunarTracking()
            assert not suc
        assert ['Cannot set tracking to Lunar', 2] == blocker.args


def test_setSiderealTracking1(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'setSiderealTracking',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.setSiderealTracking()
            assert suc
        assert ['Tracking set to Sidereal', 0] == blocker.args


def test_setSiderealTracking2(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'setSiderealTracking',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.setSiderealTracking()
            assert not suc
        assert ['Cannot set tracking to Sidereal', 2] == blocker.args


def test_setSolarTracking1(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'setSolarTracking',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.setSolarTracking()
            assert suc
        assert ['Tracking set to Solar', 0] == blocker.args


def test_setSolarTracking2(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'setSolarTracking',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.setSolarTracking()
            assert not suc
        assert ['Cannot set tracking to Solar', 2] == blocker.args


def test_flipMount_1(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'flip',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.flipMount()
            assert not suc
        assert ['Cannot flip mount', 2] == blocker.args


def test_flipMount_2(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'flip',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.flipMount()
            assert suc
        assert ['Mount flipped', 0] == blocker.args


def test_stop1(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'stop',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.stop()
            assert suc
        assert ['Mount stopped', 0] == blocker.args


def test_stop2(qtbot):
    with mock.patch.object(app.app.mount.obsSite,
                           'stop',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.stop()
            assert not suc
        assert ['Cannot stop mount', 2] == blocker.args


def test_updateSetting_slewRate_1():
    value = '5'
    app.app.mount.setting.slewRate = value
    app.updateSettingGUI(app.app.mount.setting)
    assert app.ui.slewRate.text() == ' 5'
    value = None
    app.app.mount.setting.slewRate = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.slewRate.text()


def test_updateSetting_timeToFlip_1():
    value = '5'
    app.app.mount.setting.timeToFlip = value
    app.updateSettingGUI(app.app.mount.setting)
    assert app.ui.timeToFlip.text() == '  5'
    value = None
    app.app.mount.setting.timeToFlip = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.timeToFlip.text()


def test_updateSetting_timeToMeridian_1():
    app.app.mount.setting.timeToFlip = 5
    app.app.mount.setting.meridianLimitTrack = 0

    app.updateSettingGUI(app.app.mount.setting)
    assert app.ui.timeToMeridian.text() == '  5'

    app.app.mount.setting.timeToFlip = None
    app.app.mount.setting.meridianLimitTrack = None

    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.timeToMeridian.text()


def test_updateSetting_refractionTemp():
    value = '15'
    app.app.mount.setting.refractionTemp = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '+15.0' == app.ui.refractionTemp.text()
    assert '+15.0' == app.ui.refractionTemp1.text()
    value = None
    app.app.mount.setting.refractionTemp = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.refractionTemp.text()
    assert '-' == app.ui.refractionTemp1.text()


def test_updateSetting_refractionPress():
    value = '1050.0'
    app.app.mount.setting.refractionPress = value
    app.updateSettingGUI(app.app.mount.setting)
    assert value == app.ui.refractionPress.text()
    assert value == app.ui.refractionPress1.text()
    value = None
    app.app.mount.setting.refractionPress = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.refractionPress.text()
    assert '-' == app.ui.refractionPress1.text()


def test_updateSetting_meridianLimitTrack_1():
    value = '15'
    app.app.mount.setting.meridianLimitTrack = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '15.0' == app.ui.meridianLimitTrack.text()
    value = None
    app.app.mount.setting.meridianLimitTrack = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.meridianLimitTrack.text()


def test_updateSetting_meridianLimitSlew():
    value = '15'
    app.app.mount.setting.meridianLimitSlew = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '15.0' == app.ui.meridianLimitSlew.text()
    value = None
    app.app.mount.setting.meridianLimitSlew = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.meridianLimitSlew.text()


def test_updateSetting_horizonLimitLow():
    value = '0'
    app.app.mount.setting.horizonLimitLow = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '0.0' == app.ui.horizonLimitLow.text()
    value = None
    app.app.mount.setting.horizonLimitLow = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.horizonLimitLow.text()


def test_updateSetting_horizonLimitHigh():
    value = '50'
    app.app.mount.setting.horizonLimitHigh = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '50.0' == app.ui.horizonLimitHigh.text()
    value = None
    app.app.mount.setting.horizonLimitHigh = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.horizonLimitHigh.text()


def test_updateSetting_timeToMeridian():
    app.app.mount.setting.timeToFlip = '100'
    app.app.mount.setting.meridianLimitTrack = '15'

    app.updateSettingGUI(app.app.mount.setting)
    assert ' 40' == app.ui.timeToMeridian.text()
    value = None
    app.app.mount.setting.timeToFlip = value
    app.app.mount.setting.meridianLimitTrack = value
    app.updateSettingGUI(app.app.mount.setting)
    assert '-' == app.ui.timeToMeridian.text()


def test_updateLocGUI_1():
    app.app.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
    app.updateLocGUI(app.app.mount.obsSite)
    assert '11 00\' 00.0\"' == app.ui.siteLongitude.text()
    assert '49 00\' 00.0\"' == app.ui.siteLatitude.text()
    assert '500.0' == app.ui.siteElevation.text()


def test_updateLocGUI_2():
    app.app.mount.obsSite.location = None
    suc = app.updateLocGUI(app.app.mount.obsSite)
    assert not suc


def test_updateLocGUI_3():
    app.app.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
    suc = app.updateLocGUI(None)
    assert not suc


def test_updateTrackingGui_1():
    suc = app.updateTrackingGui(None)
    assert not suc


def test_updateTrackingGui_2():
    with mock.patch.object(app.app.mount.obsSite,
                           'checkRateLunar',
                           return_value=True):
        suc = app.updateTrackingGui(app.app.mount.obsSite)
        assert suc


def test_updateTrackingGui_3():
    with mock.patch.object(app.app.mount.obsSite,
                           'checkRateSolar',
                           return_value=True):
        suc = app.updateTrackingGui(app.app.mount.obsSite)
        assert suc


def test_updateTrackingGui_4():
    with mock.patch.object(app.app.mount.obsSite,
                           'checkRateSidereal',
                           return_value=True):
        suc = app.updateTrackingGui(app.app.mount.obsSite)
        assert suc


def test_changeTracking_ok1(qtbot):
    app.app.mount.obsSite.status = 0
    with mock.patch.object(app.app.mount.obsSite,
                           'stopTracking',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.changeTracking()
            assert suc
        assert ['Cannot stop tracking', 2] == blocker.args


def test_changeTracking_ok2(qtbot):
    app.app.mount.obsSite.status = 0
    with mock.patch.object(app.app.mount.obsSite,
                           'stopTracking',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.changeTracking()
            assert suc
        assert ['Stopped tracking', 0] == blocker.args


def test_changeTracking_ok3(qtbot):
    app.app.mount.obsSite.status = 1
    with mock.patch.object(app.app.mount.obsSite,
                           'startTracking',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.changeTracking()
            assert suc
        assert ['Cannot start tracking', 2] == blocker.args


def test_changeTracking_ok4(qtbot):
    app.app.mount.obsSite.status = 1
    with mock.patch.object(app.app.mount.obsSite,
                           'startTracking',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.changeTracking()
            assert suc
        assert ['Started tracking', 0] == blocker.args


def test_changePark_ok1(qtbot):
    app.app.mount.obsSite.status = 5
    with mock.patch.object(app.app.mount.obsSite,
                           'unpark',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.changePark()
            assert suc
        assert ['Cannot unpark mount', 2] == blocker.args


def test_changePark_ok2(qtbot):
    app.app.mount.obsSite.status = 5
    with mock.patch.object(app.app.mount.obsSite,
                           'unpark',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.changePark()
            assert suc
        assert ['Mount unparked', 0] == blocker.args


def test_changePark_ok3(qtbot):
    app.app.mount.obsSite.status = 1
    with mock.patch.object(app.app.mount.obsSite,
                           'park',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.changePark()
            assert suc
        assert ['Cannot park mount', 2] == blocker.args


def test_changePark_ok4(qtbot):
    app.app.mount.obsSite.status = 1
    with mock.patch.object(app.app.mount.obsSite,
                           'park',
                           return_value=True):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.changePark()
            assert suc
        assert ['Mount parked', 0] == blocker.args


def test_setMeridianLimitTrack_1(qtbot):
    app.deviceStat['mount'] = False
    app.app.mount.setting.meridianLimitTrack = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setMeridianLimitTrack()
        assert not suc


def test_setMeridianLimitTrack_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.meridianLimitTrack = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.setMeridianLimitTrack()
        assert not suc


def test_setMeridianLimitTrack_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.meridianLimitTrack = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setMeridianLimitTrack',
                               return_value=False):
            suc = app.setMeridianLimitTrack()
            assert not suc


def test_setMeridianLimitTrack_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.meridianLimitTrack = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setMeridianLimitTrack',
                               return_value=True):
            suc = app.setMeridianLimitTrack()
            assert suc


def test_setMeridianLimitSlew_1(qtbot):
    app.deviceStat['mount'] = False
    app.app.mount.setting.meridianLimitSlew = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setMeridianLimitSlew()
        assert not suc


def test_setMeridianLimitSlew_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.meridianLimitSlew = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.setMeridianLimitSlew()
        assert not suc


def test_setMeridianLimitSlew_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.meridianLimitSlew = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setMeridianLimitSlew',
                               return_value=False):
            suc = app.setMeridianLimitSlew()
            assert not suc


def test_setMeridianLimitSlew_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.meridianLimitSlew = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setMeridianLimitSlew',
                               return_value=True):
            suc = app.setMeridianLimitSlew()
            assert suc


def test_setHorizonLimitHigh_1(qtbot):
    app.deviceStat['mount'] = False
    app.app.mount.setting.horizonLimitHigh = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setHorizonLimitHigh()
        assert not suc


def test_setHorizonLimitHigh_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.horizonLimitHigh = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.setHorizonLimitHigh()
        assert not suc


def test_setHorizonLimitHigh_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.horizonLimitHigh = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setHorizonLimitHigh',
                               return_value=False):
            suc = app.setHorizonLimitHigh()
            assert not suc


def test_setHorizonLimitHigh_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.horizonLimitHigh = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setHorizonLimitHigh',
                               return_value=True):
            suc = app.setHorizonLimitHigh()
            assert suc


def test_setHorizonLimitLow_1(qtbot):
    app.deviceStat['mount'] = False
    app.app.mount.setting.horizonLimitLow = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setHorizonLimitLow()
        assert not suc


def test_setHorizonLimitLow_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.horizonLimitLow = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.setHorizonLimitLow()
        assert not suc


def test_setHorizonLimitLow_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.horizonLimitLow = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setHorizonLimitLow',
                               return_value=False):
            suc = app.setHorizonLimitLow()
            assert not suc


def test_setHorizonLimitLow_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.horizonLimitLow = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setHorizonLimitLow',
                               return_value=True):
            suc = app.setHorizonLimitLow()
            assert suc


def test_setSlewRate_1(qtbot):
    app.deviceStat['mount'] = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setSlewRate()
        assert not suc


def test_setSlewRate_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.slewRate = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.setSlewRate()
        assert not suc


def test_setSlewRate_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.slewRate = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setSlewRate',
                               return_value=False):
            suc = app.setSlewRate()
            assert not suc


def test_setSlewRate_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.slewRate = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.setting,
                               'setSlewRate',
                               return_value=True):
            suc = app.setSlewRate()
            assert suc


def test_setLongitude_1(qtbot):
    app.app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setLongitude()
        assert not suc


def test_setLongitude_2(qtbot):
    app.deviceStat['mount'] = False
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        suc = app.setLongitude()
        assert not suc


def test_setLongitude_3(qtbot):
    app.deviceStat['mount'] = True
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, False)):
        suc = app.setLongitude()
        assert not suc


def test_setLongitude_4(qtbot):
    app.deviceStat['mount'] = True
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.obsSite,
                               'setLongitude',
                               return_value=False):
            suc = app.setLongitude()
            assert not suc


def test_setLongitude_5(qtbot):
    app.deviceStat['mount'] = True
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.obsSite,
                               'setLongitude',
                               return_value=True):
            suc = app.setLongitude()
            assert suc


def test_setLatitude_1(qtbot):
    app.app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setLatitude()
        assert not suc


def test_setLatitude_2(qtbot):
    app.deviceStat['mount'] = True
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        suc = app.setLatitude()
        assert not suc


def test_setLatitude_3(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, False)):
        suc = app.setLatitude()
        assert not suc


def test_setLatitude_4(qtbot):
    app.deviceStat['mount'] = True
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.obsSite,
                               'setLatitude',
                               return_value=False):
            suc = app.setLatitude()
            assert not suc


def test_setLatitude_5(qtbot):
    app.deviceStat['mount'] = True
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.obsSite,
                               'setLatitude',
                               return_value=True):
            suc = app.setLatitude()
            assert suc


def test_setElevation_1(qtbot):
    app.app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setElevation()
        assert not suc


def test_setElevation_2(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, False)):
        suc = app.setElevation()
        assert not suc


def test_setElevation_3(qtbot):
    app.deviceStat['mount'] = True
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.obsSite,
                               'setElevation',
                               return_value=False):
            suc = app.setElevation()
            assert not suc


def test_setElevation_4(qtbot):
    app.deviceStat['mount'] = True
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        with mock.patch.object(app.app.mount.obsSite,
                               'setElevation',
                               return_value=True):
            suc = app.setElevation()
            assert suc


def test_setUnattendedFlip_1(qtbot):
    app.deviceStat['mount'] = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setUnattendedFlip()
        assert not suc


def test_setUnattendedFlip_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusUnattendedFlip = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', False)):
        suc = app.setUnattendedFlip()
        assert not suc


def test_setUnattendedFlip_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusUnattendedFlip = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(app.app.mount.setting,
                               'setUnattendedFlip',
                               return_value=False):
            suc = app.setUnattendedFlip()
            assert not suc


def test_setUnattendedFlip_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusUnattendedFlip = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(app.app.mount.setting,
                               'setUnattendedFlip',
                               return_value=True):
            suc = app.setUnattendedFlip()
            assert suc


def test_setDualAxisTracking_1(qtbot):
    app.deviceStat['mount'] = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setDualAxisTracking()
        assert not suc


def test_setDualAxisTracking_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', False)):
        suc = app.setDualAxisTracking()
        assert not suc


def test_setDualAxisTracking_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(app.app.mount.setting,
                               'setDualAxisTracking',
                               return_value=False):
            suc = app.setDualAxisTracking()
            assert not suc


def test_setDualAxisTracking_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(app.app.mount.setting,
                               'setDualAxisTracking',
                               return_value=True):
            suc = app.setDualAxisTracking()
            assert suc


def test_setRefraction_1(qtbot):
    app.deviceStat['mount'] = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setRefraction()
        assert not suc


def test_setRefraction_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusRefraction = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', False)):
        suc = app.setRefraction()
        assert not suc


def test_setRefraction_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusRefraction = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(app.app.mount.setting,
                               'setRefraction',
                               return_value=False):
            suc = app.setRefraction()
            assert not suc


def test_setRefraction_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusRefraction = True
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(app.app.mount.setting,
                               'setRefraction',
                               return_value=True):
            suc = app.setRefraction()
            assert suc


def test_setWOL_1(qtbot):
    app.deviceStat['mount'] = False
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.setWOL()
        assert not suc


def test_setWOL_2(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusWOL = '0'
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', False)):
        suc = app.setWOL()
        assert not suc


def test_setWOL_3(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusWOL = '0'
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(app.app.mount.setting,
                               'setWOL',
                               return_value=False):
            suc = app.setWOL()
            assert not suc


def test_setWOL_4(qtbot):
    app.deviceStat['mount'] = True
    app.app.mount.setting.statusWOL = '0'
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(app.app.mount.setting,
                               'setWOL',
                               return_value=True):
            suc = app.setWOL()
            assert suc
