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
import unittest.mock as mock
import pytest
import datetime

# external packages
import PyQt5
from PyQt5.QtWidgets import QWidget
from skyfield.api import Angle, wgs84

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.mainWmixin.tabMountSett import MountSett


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    class Mixin(MWidget, MountSett):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = self.app.deviceStat
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            MountSett.__init__(self)

    window = Mixin()
    yield window


def test_updatePointGui_alt(function):
    value = Angle(degrees=45)
    function.app.mount.obsSite.Alt = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '45.00' == function.ui.ALT.text()
    value = None
    function.app.mount.obsSite.Alt = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.ALT.text()


def test_updatePointGui_az(function):
    value = Angle(degrees=45)
    function.app.mount.obsSite.Az = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '45.00' == function.ui.AZ.text()
    value = None
    function.app.mount.obsSite.Az = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.AZ.text()


def test_updatePointGui_ra(function):
    function.ui.coordsJ2000.setChecked(True)
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.updatePointGUI(function.app.mount.obsSite)
    assert '23:58:53' == function.ui.RA.text()


def test_updatePointGui_dec_1(function):
    function.ui.coordsJ2000.setChecked(True)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-00:07:13' == function.ui.DEC.text()


def test_updatePointGui_dec_2(function):
    function.app.mount.obsSite.decJNow = None
    function.ui.coordsJ2000.setChecked(False)
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.DEC.text()


def test_updatePointGui_pierside(function):
    value = 'W'
    function.app.mount.obsSite.pierside = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert 'WEST' == function.ui.pierside.text()


def test_updatePointGui_ha_1(function):
    value = Angle(hours=12)
    function.app.mount.obsSite.haJNow = value
    function.app.mount.obsSite.timeSidereal = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '12:00:00' == function.ui.HA.text()


def test_updatePointGui_ha_2(function):
    value = None
    function.app.mount.obsSite.timeSidereal = value
    function.app.mount.obsSite.haJNow = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.HA.text()


def test_updatePointGUI_sidereal_1(function):
    value = Angle(hours=12)
    function.app.mount.obsSite.timeSidereal = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '12:00:00' == function.ui.timeSidereal.text()


def test_updatePointGUI_sidereal_2(function):
    value = None
    function.app.mount.obsSite.timeSidereal = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.timeSidereal.text()


def test_updateSetting_slewRate(function):
    value = 15
    function.app.mount.setting.slewRate = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '15' == function.ui.slewRate.text()
    value = None
    function.app.mount.setting.slewRate = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.slewRate.text()


def test_updateSetting_timeToFlip(function):
    value = 15
    function.app.mount.setting.timeToFlip = value
    function.updateSettingGUI(function.app.mount.setting)
    assert ' 15' == function.ui.timeToFlip.text()
    value = None
    function.app.mount.setting.timeToFlip = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.timeToFlip.text()


def test_updateSettingGUI_UTCExpire(function):
    value = '2020-10-05'
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert value == function.ui.UTCExpire.text()
    value = None
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_1(function):
    value = '2016-10-05'
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert value == function.ui.UTCExpire.text()
    value = None
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_2(function):
    tomorrow = datetime.date.today() + datetime.timedelta(days=15)
    value = tomorrow.strftime('%Y-%m-%d')
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert value == function.ui.UTCExpire.text()
    value = None
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_3(function):
    tomorrow = datetime.date.today() + datetime.timedelta(days=40)
    value = tomorrow.strftime('%Y-%m-%d')
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert value == function.ui.UTCExpire.text()
    value = None
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.UTCExpire.text()


def test_updateSettingGUI_statusUnattendedFlip(function):
    value = True
    function.app.mount.setting.statusUnattendedFlip = value
    function.updateSettingGUI(function.app.mount.setting)
    assert 'ON' == function.ui.statusUnattendedFlip.text()
    value = None
    function.app.mount.setting.statusUnattendedFlip = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.statusUnattendedFlip.text()


def test_updateSettingGUI_statusDualAxisTracking(function):
    value = True
    function.app.mount.setting.statusDualAxisTracking = value
    function.updateSettingGUI(function.app.mount.setting)
    assert 'ON' == function.ui.statusDualAxisTracking.text()
    value = None
    function.app.mount.setting.statusDualAxisTracking = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.statusDualAxisTracking.text()


def test_updateSettingGUI_statusRefraction(function):
    value = True
    function.app.mount.setting.statusRefraction = value
    function.updateSettingGUI(function.app.mount.setting)
    assert 'ON' == function.ui.statusRefraction.text()
    value = None
    function.app.mount.setting.statusRefraction = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.statusRefraction.text()


def test_updateSettingGUI_1(function):
    function.app.mount.setting.gpsSynced = True
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.statusGPSSynced.text() == 'ON'
    assert suc


def test_updateSettingGUI_2(function):
    function.app.mount.setting.gpsSynced = False
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.statusGPSSynced.text() == 'OFF'
    assert suc


def test_updateSettingGUI_3(function):
    function.app.mount.setting.gpsSynced = None
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.statusGPSSynced.text() == '-'
    assert suc


def test_updateSettingGUI_4(function):
    function.app.mount.setting.typeConnection = None
    function.app.mount.setting.wakeOnLan = 'On'
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert suc


def test_updateSettingGUI_5(function):
    function.app.mount.setting.typeConnection = 1
    function.app.mount.setting.wakeOnLan = None
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert suc


def test_updateSettingGUI_6(function):
    function.app.mount.setting.typeConnection = 1
    function.app.mount.setting.wakeOnLan = 'OFF'
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert suc


def test_updateSettingGUI_7(function):
    function.app.mount.setting.webInterfaceStat = False
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert suc


def test_updateSettingGUI_8(function):
    function.app.mount.setting.webInterfaceStat = True
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert suc


def test_updateSettingGUI_9(function):
    function.app.mount.setting.webInterfaceStat = None
    suc = function.updateSettingGUI(function.app.mount.setting)
    assert suc


def test_updateSettingGUI_1(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.setting,
                           'checkRateLunar',
                           return_value=True):
        suc = function.updateSettingGUI(function.app.mount.setting)
        assert suc


def test_updateSettingGUI_2(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.setting,
                           'checkRateSidereal',
                           return_value=True):
        suc = function.updateSettingGUI(function.app.mount.setting)
        assert suc


def test_updateSettingGUI_3(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.setting,
                           'checkRateSolar',
                           return_value=True):
        suc = function.updateSettingGUI(function.app.mount.setting)
        assert suc


def test_updateSettingGUI_4(function):
    function.app.mount.obsSite.status = 10
    with mock.patch.object(function.app.mount.setting,
                           'checkRateSolar',
                           return_value=True):
        suc = function.updateSettingGUI(function.app.mount.setting)
        assert suc


def test_updateSettingGUI_5(function):
    function.app.mount.obsSite.status = None
    with mock.patch.object(function.app.mount.setting,
                           'checkRateSolar',
                           return_value=True):
        suc = function.updateSettingGUI(function.app.mount.setting)
        assert suc


def test_updateSetting_slewRate_1(function):
    value = 5
    function.app.mount.setting.slewRate = value
    function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.slewRate.text() == ' 5'
    value = None
    function.app.mount.setting.slewRate = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.slewRate.text()


def test_updateSetting_timeToFlip_1(function):
    value = 5
    function.app.mount.setting.timeToFlip = value
    function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.timeToFlip.text() == '  5'
    value = None
    function.app.mount.setting.timeToFlip = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.timeToFlip.text()


def test_updateSetting_timeToMeridian_1(function):
    function.app.mount.setting.timeToFlip = 5
    function.app.mount.setting.meridianLimitTrack = 0

    function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.timeToMeridian.text() == '  0'

    function.app.mount.setting.timeToFlip = None
    function.app.mount.setting.meridianLimitTrack = None

    function.updateSettingGUI(function.app.mount.setting)
    assert '  0' == function.ui.timeToMeridian.text()


def test_updateSetting_refractionTemp(function):
    value = 15
    function.app.mount.setting.refractionTemp = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '+15.0' == function.ui.refractionTemp.text()
    assert '+15.0' == function.ui.refractionTemp1.text()
    value = None
    function.app.mount.setting.refractionTemp = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.refractionTemp.text()
    assert '-' == function.ui.refractionTemp1.text()


def test_updateSetting_refractionPress(function):
    value = 1050.0
    function.app.mount.setting.refractionPress = value
    function.updateSettingGUI(function.app.mount.setting)
    assert str(value) == function.ui.refractionPress.text()
    assert str(value) == function.ui.refractionPress1.text()
    value = None
    function.app.mount.setting.refractionPress = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.refractionPress.text()
    assert '-' == function.ui.refractionPress1.text()


def test_updateSetting_meridianLimitTrack_1(function):
    value = 15
    function.app.mount.setting.meridianLimitTrack = value
    function.updateSettingGUI(function.app.mount.setting)
    assert ' 15' == function.ui.meridianLimitTrack.text()
    value = None
    function.app.mount.setting.meridianLimitTrack = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.meridianLimitTrack.text()


def test_updateSetting_meridianLimitSlew(function):
    value = 15
    function.app.mount.setting.meridianLimitSlew = value
    function.updateSettingGUI(function.app.mount.setting)
    assert ' 15' == function.ui.meridianLimitSlew.text()
    value = None
    function.app.mount.setting.meridianLimitSlew = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.meridianLimitSlew.text()


def test_updateSetting_horizonLimitLow(function):
    value = 0
    function.app.mount.setting.horizonLimitLow = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '  0' == function.ui.horizonLimitLow.text()
    value = None
    function.app.mount.setting.horizonLimitLow = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.horizonLimitLow.text()


def test_updateSetting_horizonLimitHigh(function):
    value = 50
    function.app.mount.setting.horizonLimitHigh = value
    function.updateSettingGUI(function.app.mount.setting)
    assert ' 50' == function.ui.horizonLimitHigh.text()
    value = None
    function.app.mount.setting.horizonLimitHigh = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '-' == function.ui.horizonLimitHigh.text()


def test_updateSetting_timeToMeridian(function):
    function.app.mount.setting.timeToFlip = 100
    function.app.mount.setting.meridianLimitTrack = 15

    function.updateSettingGUI(function.app.mount.setting)
    assert '  0' == function.ui.timeToMeridian.text()
    value = None
    function.app.mount.setting.timeToFlip = value
    function.app.mount.setting.meridianLimitTrack = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '  0' == function.ui.timeToMeridian.text()


def test_updateLocGUI_1(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=11,
                                                       latitude_degrees=49,
                                                       elevation_m=500)
    function.updateLocGUI(function.app.mount.obsSite)
    assert '011E 00 00' == function.ui.siteLongitude.text()
    assert '49N 00 00' == function.ui.siteLatitude.text()
    assert '500.0' == function.ui.siteElevation.text()


def test_updateLocGUI_2(function):
    function.app.mount.obsSite.location = None
    suc = function.updateLocGUI(function.app.mount.obsSite)
    assert not suc


def test_updateLocGUI_3(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
    suc = function.updateLocGUI(None)
    assert not suc


def test_checkMount_1(function):
    function.app.deviceStat['mount'] = False
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        suc = function.checkMount()
        assert not suc


def test_checkMount_2(function):
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        suc = function.checkMount()
        assert suc


def test_changeTrackingGameController_1(function):
    with mock.patch.object(function,
                           'changeTracking'):
        suc = function.changeTrackingGameController(4)
        assert suc


def test_changeTracking_ok1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.changeTracking()
        assert not suc


def test_changeTracking_ok2(function, qtbot):
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'stopTracking',
                               return_value=False):
            suc = function.changeTracking()
            assert suc


def test_changeTracking_ok3(function, qtbot):
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'stopTracking',
                               return_value=True):
            suc = function.changeTracking()
            assert suc


def test_changeTracking_ok4(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'startTracking',
                               return_value=True):
            suc = function.changeTracking()
            assert suc


def test_changeTracking_ok5(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'startTracking',
                               return_value=False):
            suc = function.changeTracking()
            assert suc


def test_changeParkGameController_1(function):
    with mock.patch.object(function,
                           'changePark'):
        suc = function.changeParkGameController(1)
        assert suc


def test_changePark_ok1(function):
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'unpark',
                               return_value=False):
            suc = function.changePark()
            assert suc


def test_changePark_ok2(function):
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'unpark',
                               return_value=True):
            suc = function.changePark()
            assert suc


def test_changePark_ok3(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'park',
                               return_value=False):
            suc = function.changePark()
            assert suc


def test_changePark_ok4(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'park',
                               return_value=True):
            suc = function.changePark()
            assert suc


def test_changePark_notok(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        with mock.patch.object(function.app.mount.obsSite,
                               'park',
                               return_value=True):
            suc = function.changePark()
            assert not suc


def test_setLunarTracking_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setLunarTracking',
                               return_value=True):
            suc = function.setLunarTracking()
            assert suc


def test_setLunarTracking_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setLunarTracking',
                               return_value=False):
            suc = function.setLunarTracking()
            assert not suc


def test_setLunarTracking_3(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        with mock.patch.object(function.app.mount.setting,
                               'setLunarTracking',
                               return_value=True):
            suc = function.setLunarTracking()
            assert not suc


def test_setSiderealTracking_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setSiderealTracking()
        assert not suc


def test_setSiderealTracking_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setSiderealTracking',
                               return_value=False):
            suc = function.setSiderealTracking()
            assert not suc


def test_setSiderealTracking_3(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setSiderealTracking',
                               return_value=True):
            suc = function.setSiderealTracking()
            assert suc


def test_setSolarTracking_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setSolarTracking()
        assert not suc


def test_setSolarTracking_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setSolarTracking',
                               return_value=False):
            suc = function.setSolarTracking()
            assert not suc


def test_setSolarTracking_3(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setSolarTracking',
                               return_value=True):
            suc = function.setSolarTracking()
            assert suc


def test_flipMountGameController_1(function):
    with mock.patch.object(function,
                           'flipMount'):
        suc = function.flipMountGameController(2)
        assert suc


def test_flipMount_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'flip',
                               return_value=False):
            suc = function.flipMount()
            assert not suc


def test_flipMount_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'flip',
                               return_value=True):
            suc = function.flipMount()
            assert suc


def test_flipMount_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        with mock.patch.object(function.app.mount.obsSite,
                               'flip',
                               return_value=True):
            suc = function.flipMount()
            assert not suc


def test_stopGameController_1(function):
    with mock.patch.object(function,
                           'flipMount'):
        suc = function.stopGameController(8)
        assert suc


def test_stop_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'stop',
                               return_value=True):
            suc = function.stop()
            assert suc


def test_stop_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'stop',
                               return_value=False):
            suc = function.stop()
            assert not suc


def test_test_stop_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        with mock.patch.object(function.app.mount.obsSite,
                               'stop',
                               return_value=True):
            suc = function.stop()
            assert not suc


def test_setMeridianLimitTrack_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        function.app.mount.setting.meridianLimitTrack = None
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'critical',
                               return_value=True):
            suc = function.setMeridianLimitTrack()
            assert not suc


def test_setMeridianLimitTrack_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitTrack = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setMeridianLimitTrack()
            assert not suc


def test_setMeridianLimitTrack_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitTrack = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setMeridianLimitTrack',
                                   return_value=False):
                suc = function.setMeridianLimitTrack()
                assert not suc


def test_setMeridianLimitTrack_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitTrack = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setMeridianLimitTrack',
                                   return_value=True):
                suc = function.setMeridianLimitTrack()
                assert suc


def test_setMeridianLimitSlew_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        function.app.mount.setting.meridianLimitSlew = None
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'critical',
                               return_value=True):
            suc = function.setMeridianLimitSlew()
            assert not suc


def test_setMeridianLimitSlew_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitSlew = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setMeridianLimitSlew()
            assert not suc


def test_setMeridianLimitSlew_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitSlew = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setMeridianLimitSlew',
                                   return_value=False):
                suc = function.setMeridianLimitSlew()
                assert not suc


def test_setMeridianLimitSlew_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitSlew = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setMeridianLimitSlew',
                                   return_value=True):
                suc = function.setMeridianLimitSlew()
                assert suc


def test_setHorizonLimitHigh_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        function.app.mount.setting.horizonLimitHigh = None
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'critical',
                               return_value=True):
            suc = function.setHorizonLimitHigh()
            assert not suc


def test_setHorizonLimitHigh_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitHigh = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setHorizonLimitHigh()
            assert not suc


def test_setHorizonLimitHigh_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitHigh = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setHorizonLimitHigh',
                                   return_value=False):
                suc = function.setHorizonLimitHigh()
                assert not suc


def test_setHorizonLimitHigh_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitHigh = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setHorizonLimitHigh',
                                   return_value=True):
                suc = function.setHorizonLimitHigh()
                assert suc


def test_setHorizonLimitLow_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        function.app.mount.setting.horizonLimitLow = None
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'critical',
                               return_value=True):
            suc = function.setHorizonLimitLow()
            assert not suc


def test_setHorizonLimitLow_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitLow = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setHorizonLimitLow()
            assert not suc


def test_setHorizonLimitLow_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitLow = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setHorizonLimitLow',
                                   return_value=False):
                suc = function.setHorizonLimitLow()
                assert not suc


def test_setHorizonLimitLow_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitLow = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setHorizonLimitLow',
                                   return_value=True):
                suc = function.setHorizonLimitLow()
                assert suc


def test_setSlewRate_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setSlewRate()
        assert not suc


def test_setSlewRate_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setSlewRate()
            assert not suc


def test_setSlewRate_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setSlewRate',
                                   return_value=False):
                suc = function.setSlewRate()
                assert not suc


def test_setSlewRate_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setSlewRate',
                                   return_value=True):
                suc = function.setSlewRate()
                assert suc


def test_setLocationValues_1(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function.app.mount,
                           'getLocation'):
        with mock.patch.object(function.app.mount.obsSite,
                               'setLocation'):
            suc = function.setLocationValues()
            assert suc


def test_setLocationValues_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    function.app.deviceStat['mount'] = False
    with mock.patch.object(function,
                           'updateLocGUI'):
        suc = function.setLocationValues()
        assert suc


def test_setLongitude_1(function):
    function.app.mount.obsSite.location = None
    suc = function.setLongitude()
    assert not suc


def test_setLongitude_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('011E 40 40', False)):
        suc = function.setLongitude()
        assert not suc


def test_setLongitude_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('011E 40 40', True)):
        with mock.patch.object(function,
                               'setLocationValues'):
            suc = function.setLongitude()
            assert suc


def test_setLatitude_1(function):
    function.app.mount.obsSite.location = None
    suc = function.setLatitude()
    assert not suc


def test_setLatitude_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('48N 00 00', False)):
        suc = function.setLatitude()
        assert not suc


def test_setLatitude_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('48N 00 00', True)):
        with mock.patch.object(function,
                               'setLocationValues'):
            suc = function.setLatitude()
            assert suc


def test_setElevation_1(function):
    function.app.mount.obsSite.location = None
    suc = function.setElevation()
    assert not suc


def test_setElevation_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10.0, False)):
        suc = function.setElevation()
        assert not suc


def test_setElevation_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10.0, True)):
        with mock.patch.object(function,
                               'setLocationValues'):
            suc = function.setElevation()
            assert suc


def test_setUnattendedFlip_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setUnattendedFlip()
        assert not suc


def test_setUnattendedFlip_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusUnattendedFlip = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', False)):
            suc = function.setUnattendedFlip()
            assert not suc


def test_setUnattendedFlip_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusUnattendedFlip = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setUnattendedFlip',
                                   return_value=False):
                suc = function.setUnattendedFlip()
                assert not suc


def test_setUnattendedFlip_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusUnattendedFlip = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setUnattendedFlip',
                                   return_value=True):
                suc = function.setUnattendedFlip()
                assert suc


def test_setDualAxisTracking_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setDualAxisTracking()
        assert not suc


def test_setDualAxisTracking_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusDualAxisTracking = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', False)):
            suc = function.setDualAxisTracking()
            assert not suc


def test_setDualAxisTracking_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusDualAxisTracking = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setDualAxisTracking',
                                   return_value=False):
                suc = function.setDualAxisTracking()
                assert not suc


def test_setDualAxisTracking_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusDualAxisTracking = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setDualAxisTracking',
                                   return_value=True):
                suc = function.setDualAxisTracking()
                assert suc


def test_setRefractionTemp_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setRefractionTemp()
        assert not suc


def test_setRefractionTemp_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, False)):
            suc = function.setRefractionTemp()
            assert not suc


def test_setRefractionTemp_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefractionTemp',
                                   return_value=False):
                suc = function.setRefractionTemp()
                assert not suc


def test_setRefractionTemp_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefractionTemp',
                                   return_value=True):
                suc = function.setRefractionTemp()
                assert suc


def test_setRefractionPress_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setRefractionPress()
        assert not suc


def test_setRefractionPress_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, False)):
            suc = function.setRefractionPress()
            assert not suc


def test_setRefractionPress_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefractionPress',
                                   return_value=False):
                suc = function.setRefractionPress()
                assert not suc


def test_setRefractionPress_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefractionPress',
                                   return_value=True):
                suc = function.setRefractionPress()
                assert suc


def test_setRefraction_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setRefraction()
        assert not suc


def test_setRefraction_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusRefraction = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', False)):
            suc = function.setRefraction()
            assert not suc


def test_setRefraction_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusRefraction = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefraction',
                                   return_value=False):
                suc = function.setRefraction()
                assert not suc


def test_setRefraction_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusRefraction = True
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefraction',
                                   return_value=True):
                suc = function.setRefraction()
                assert suc


def test_setWOL_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setWOL()
        assert not suc


def test_setWOL_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusWOL = '0'
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', False)):
            suc = function.setWOL()
            assert not suc


def test_setWOL_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusWOL = '0'
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setWOL',
                                   return_value=False):
                suc = function.setWOL()
                assert not suc


def test_setWOL_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusWOL = '0'
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setWOL',
                                   return_value=True):
                suc = function.setWOL()
                assert suc


def test_updatePointGui_ra_j2000(function):
    function.ui.coordsJ2000.setChecked(True)
    value = Angle(hours=45)
    function.app.mount.obsSite.raJNow = value
    value = Angle(degrees=45)
    function.app.mount.obsSite.decJNow = value
    function.updatePointGUI(function.app.mount.obsSite)


def test_setSettleTimeMount_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setSettleTimeMount()
        assert not suc


def test_setSettleTimeMount_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setSettleTimeMount()
            assert not suc


def test_setSettleTimeMount_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setSettleTime',
                                   return_value=False):
                suc = function.setSettleTimeMount()
                assert not suc


def test_setSettleTimeMount_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setSettleTime',
                                   return_value=True):
                suc = function.setSettleTimeMount()
                assert suc


def test_showOffset_1(function):
    function.ui.clockSync.setChecked(False)
    suc = function.showOffset()
    assert suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount'
            '.obsSite.timeDiff', 0.003)
def test_showOffset_2(function):
    function.ui.clockSync.setChecked(True)
    suc = function.showOffset()
    assert suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount'
            '.obsSite.timeDiff', 0.3)
def test_showOffset_3(function):
    function.ui.clockSync.setChecked(True)
    suc = function.showOffset()
    assert suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite'
            '.timeDiff', 0.6)
def test_showOffset_4(function):
    function.ui.clockSync.setChecked(True)
    suc = function.showOffset()
    assert suc
