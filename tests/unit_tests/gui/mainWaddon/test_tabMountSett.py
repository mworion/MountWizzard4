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
import pytest
import astropy
import datetime

# external packages
import PySide6
from PySide6.QtWidgets import QWidget
from skyfield.api import Angle, wgs84

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabMountSett import MountSett
from mountcontrol.obsSite import ObsSite
from mountcontrol.setting import Setting


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = MountSett(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_updatePointGui_alt(function):
    obs = ObsSite()
    obs.Alt = Angle(degrees=45)
    function.updatePointGUI(obs)
    assert '45.00' == function.ui.ALT.text()


def test_updatePointGui_az(function):
    obs = ObsSite()
    obs.Az = Angle(degrees=45)
    function.updatePointGUI(obs)
    assert '45.00' == function.ui.AZ.text()


def test_updatePointGui_ra(function):
    function.ui.coordsJ2000.setChecked(True)
    obs = ObsSite()
    obs.raJNow = Angle(hours=0)
    obs.decJNow = Angle(degrees=0)
    function.updatePointGUI(obs)
    assert '23:58:44' == function.ui.RA.text()


def test_updatePointGui_dec_1(function):
    function.ui.coordsJ2000.setChecked(True)
    obs = ObsSite()
    obs.raJNow = Angle(hours=0)
    obs.decJNow = Angle(degrees=0)
    function.updatePointGUI(obs)
    assert '-00:08:11' == function.ui.DEC.text()


def test_updatePointGui_dec_2(function):
    function.app.mount.obsSite.decJNow = None
    obs = ObsSite()
    obs.raJNow = Angle(hours=0)
    obs.decJNow = None
    function.updatePointGUI(obs)
    assert '-' == function.ui.DEC.text()


def test_updatePointGui_pierside(function):
    obs = ObsSite()
    obs.pierside = 'W'
    function.updatePointGUI(obs)
    assert 'WEST' == function.ui.pierside.text()


def test_updatePointGui_ha_2(function):
    obs = ObsSite()
    obs.timeSidereal = None
    function.updatePointGUI(obs)
    assert '-' == function.ui.HA.text()


def test_updatePointGUI_sidereal_1(function):
    obs = ObsSite()
    obs.timeSidereal = Angle(hours=12)
    function.updatePointGUI(obs)
    assert '12:00:00' == function.ui.timeSidereal.text()


def test_updatePointGUI_sidereal_2(function):
    obs = ObsSite()
    obs.timeSidereal = None
    function.updatePointGUI(obs)
    assert '-' == function.ui.timeSidereal.text()


def test_updateSetting_slewRate(function):
    sett = Setting()
    sett.slewRate = 15
    function.updateSettingGUI(sett)
    assert '15' == function.ui.slewRate.text()


def test_updateSetting_timeToFlip(function):
    sett = Setting()
    sett.timeToFlip = 15
    function.updateSettingGUI(sett)
    assert ' 15' == function.ui.timeToFlip.text()


def test_updateSettingGUI_UTCExpire(function):
    sett = Setting()
    sett.UTCExpire = '2020-10-05'
    function.updateSettingGUI(sett)
    assert '2020-10-05' == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_1(function):
    sett = Setting()
    sett.UTCExpire = '2016-10-05'
    function.updateSettingGUI(sett)
    assert '2016-10-05' == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_2(function):
    tomorrow = datetime.date.today() + datetime.timedelta(days=15)
    value = tomorrow.strftime('%Y-%m-%d')
    sett = Setting()
    sett.UTCExpire = value
    function.updateSettingGUI(sett)
    assert value == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_3(function):
    tomorrow = datetime.date.today() + datetime.timedelta(days=40)
    value = tomorrow.strftime('%Y-%m-%d')
    sett = Setting()
    sett.UTCExpire = value
    function.updateSettingGUI(sett)
    assert value == function.ui.UTCExpire.text()


def test_updateSettingGUI_statusUnattendedFlip(function):
    value = True
    sett = Setting()
    sett.statusUnattendedFlip = value
    function.updateSettingGUI(sett)
    assert 'ON' == function.ui.statusUnattendedFlip.text()


def test_updateSettingGUI_statusDualAxisTracking(function):
    value = True
    sett = Setting()
    sett.statusDualAxisTracking = value
    function.updateSettingGUI(sett)
    assert 'ON' == function.ui.statusDualAxisTracking.text()


def test_updateSettingGUI_statusRefraction(function):
    value = True
    sett = Setting()
    sett.statusRefraction = value
    function.updateSettingGUI(sett)
    assert 'ON' == function.ui.statusRefraction.text()


def test_updateSettingGUI_1(function):
    sett = Setting()
    sett.gpsSynced = True
    function.updateSettingGUI(sett)
    assert function.ui.statusGPSSynced.text() == 'ON'


def test_updateSettingGUI_2(function):
    sett = Setting()
    sett.gpsSynced = False
    function.updateSettingGUI(sett)
    assert function.ui.statusGPSSynced.text() == 'OFF'


def test_updateSettingGUI_3(function):
    sett = Setting()
    sett.gpsSynced = None
    function.updateSettingGUI(sett)
    assert function.ui.statusGPSSynced.text() == 'OFF'


def test_updateSettingGUI_4(function):
    sett = Setting()
    sett.typeConnection = None
    sett.wakeOnLan = 'On'
    function.updateSettingGUI(sett)


def test_updateSettingGUI_5(function):
    sett = Setting()
    sett.typeConnection = 1
    sett.wakeOnLan = None
    function.updateSettingGUI(sett)


def test_updateSettingGUI_6(function):
    sett = Setting()
    sett.typeConnection = 1
    sett.wakeOnLan = 'OFF'
    function.updateSettingGUI(sett)


def test_updateSettingGUI_7(function):
    sett = Setting()
    sett.webInterfaceStat = False
    function.updateSettingGUI(sett)


def test_updateSettingGUI_8(function):
    sett = Setting()
    sett.webInterfaceStat = True
    function.updateSettingGUI(sett)


def test_updateSettingGUI_9(function):
    sett = Setting()
    sett.webInterfaceStat = None
    function.updateSettingGUI(sett)


def test_updateSettingGUI_10(function):
    sett = Setting()
    function.app.mount.obsSite.status = 1
    with mock.patch.object(sett,
                           'checkRateLunar',
                           return_value=True):
        function.updateSettingGUI(sett)


def test_updateSettingGUI_11(function):
    sett = Setting()
    function.app.mount.obsSite.status = 1
    with mock.patch.object(sett,
                           'checkRateSidereal',
                           return_value=True):
        function.updateSettingGUI(sett)


def test_updateSettingGUI_12(function):
    sett = Setting()
    function.app.mount.obsSite.status = 1
    with mock.patch.object(sett,
                           'checkRateSolar',
                           return_value=True):
        function.updateSettingGUI(sett)


def test_updateSettingGUI_13(function):
    sett = Setting()
    function.app.mount.obsSite.status = 10
    with mock.patch.object(sett,
                           'checkRateSolar',
                           return_value=True):
        function.updateSettingGUI(sett)


def test_updateSettingGUI_14(function):
    sett = Setting()
    function.app.mount.obsSite.status = None
    with mock.patch.object(sett,
                           'checkRateSolar',
                           return_value=True):
        function.updateSettingGUI(sett)


def test_updateSetting_slewRate_1(function):
    sett = Setting()
    value = 5
    sett.slewRate = value
    function.updateSettingGUI(sett)
    assert function.ui.slewRate.text() == ' 5'
    value = None
    sett.slewRate = value
    function.updateSettingGUI(sett)
    assert '-' == function.ui.slewRate.text()


def test_updateSetting_timeToFlip_1(function):
    sett = Setting()
    value = 5
    sett.timeToFlip = value
    function.updateSettingGUI(sett)
    assert function.ui.timeToFlip.text() == '  5'
    value = None
    sett.timeToFlip = value
    function.updateSettingGUI(sett)
    assert '-' == function.ui.timeToFlip.text()


def test_updateSetting_timeToMeridian_1(function):
    sett = Setting()
    sett.timeToFlip = 5
    sett.meridianLimitTrack = 0
    function.updateSettingGUI(sett)
    assert function.ui.timeToMeridian.text() == '  5'
    sett = Setting()
    sett.timeToFlip = None
    sett.meridianLimitTrack = None
    function.updateSettingGUI(sett)
    assert '-' == function.ui.timeToMeridian.text()


def test_updateSetting_refractionTemp(function):
    sett = Setting()
    sett.refractionTemp = 15
    function.updateSettingGUI(sett)
    assert '+15.0' == function.ui.refractionTemp.text()
    assert '+15.0' == function.ui.refractionTemp1.text()


def test_updateSetting_refractionPress(function):
    sett = Setting()
    sett.refractionPress = 1050.0
    function.updateSettingGUI(sett)
    assert str(1050.0) == function.ui.refractionPress.text()
    assert str(1050.0) == function.ui.refractionPress1.text()


def test_updateSetting_meridianLimitTrack_1(function):
    sett = Setting()
    sett.meridianLimitTrack = 15
    function.updateSettingGUI(sett)
    assert ' 15' == function.ui.meridianLimitTrack.text()


def test_updateSetting_meridianLimitSlew(function):
    sett = Setting()
    sett.meridianLimitSlew = 15
    function.updateSettingGUI(sett)
    assert ' 15' == function.ui.meridianLimitSlew.text()


def test_updateSetting_horizonLimitLow(function):
    sett = Setting()
    sett.horizonLimitLow = 0
    function.updateSettingGUI(sett)
    assert '  0' == function.ui.horizonLimitLow.text()


def test_updateSetting_horizonLimitHigh(function):
    sett = Setting()
    sett.horizonLimitHigh = 50
    function.updateSettingGUI(sett)
    assert ' 50' == function.ui.horizonLimitHigh.text()


def test_updateSetting_timeToMeridian(function):
    sett = Setting()
    sett.timeToFlip = 100
    sett.meridianLimitTrack = 15
    function.updateSettingGUI(sett)
    assert ' 40' == function.ui.timeToMeridian.text()


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
    function.updateLocGUI(function.app.mount.obsSite)


def test_updateLocGUI_3(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
    function.updateLocGUI(None)


def test_setMeridianLimitTrack_2(function):
    function.app.mount.setting.meridianLimitTrack = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = function.setMeridianLimitTrack()
        assert not suc


def test_setMeridianLimitTrack_3(function):
    function.app.mount.setting.meridianLimitTrack = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setMeridianLimitTrack',
                               return_value=False):
            suc = function.setMeridianLimitTrack()
            assert not suc


def test_setMeridianLimitTrack_4(function):
    function.app.mount.setting.meridianLimitTrack = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setMeridianLimitTrack',
                               return_value=True):
            suc = function.setMeridianLimitTrack()
            assert suc


def test_setMeridianLimitSlew_2(function):
    function.app.mount.setting.meridianLimitSlew = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = function.setMeridianLimitSlew()
        assert not suc


def test_setMeridianLimitSlew_3(function):
    function.app.mount.setting.meridianLimitSlew = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setMeridianLimitSlew',
                               return_value=False):
            suc = function.setMeridianLimitSlew()
            assert not suc


def test_setMeridianLimitSlew_4(function):
    function.app.mount.setting.meridianLimitSlew = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setMeridianLimitSlew',
                               return_value=True):
            suc = function.setMeridianLimitSlew()
            assert suc


def test_setHorizonLimitHigh_2(function):
    function.app.mount.setting.horizonLimitHigh = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = function.setHorizonLimitHigh()
        assert not suc


def test_setHorizonLimitHigh_3(function):
    function.app.mount.setting.horizonLimitHigh = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setHorizonLimitHigh',
                               return_value=False):
            suc = function.setHorizonLimitHigh()
            assert not suc


def test_setHorizonLimitHigh_4(function):
    function.app.mount.setting.horizonLimitHigh = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setHorizonLimitHigh',
                               return_value=True):
            suc = function.setHorizonLimitHigh()
            assert suc


def test_setHorizonLimitLow_2(function):
    function.app.mount.setting.horizonLimitLow = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = function.setHorizonLimitLow()
        assert not suc


def test_setHorizonLimitLow_3(function):
    function.app.mount.setting.horizonLimitLow = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setHorizonLimitLow',
                               return_value=False):
            suc = function.setHorizonLimitLow()
            assert not suc


def test_setHorizonLimitLow_4(function):
    function.app.mount.setting.horizonLimitLow = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setHorizonLimitLow',
                               return_value=True):
            suc = function.setHorizonLimitLow()
            assert suc


def test_setSlewRate_2(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = function.setSlewRate()
        assert not suc


def test_setSlewRate_3(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setSlewRate',
                               return_value=False):
            suc = function.setSlewRate()
            assert not suc


def test_setSlewRate_4(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
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
            function.setLocationValues()


def test_setLocationValues_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    function.app.deviceStat['mount'] = False
    with mock.patch.object(function,
                           'updateLocGUI'):
        function.setLocationValues()


def test_setLongitude_1(function):
    function.app.mount.obsSite.location = None
    suc = function.setLongitude()
    assert not suc


def test_setLongitude_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('011E 40 40', False)):
        suc = function.setLongitude()
        assert not suc


def test_setLongitude_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
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
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('48N 00 00', False)):
        suc = function.setLatitude()
        assert not suc


def test_setLatitude_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
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
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10.0, False)):
        suc = function.setElevation()
        assert not suc


def test_setElevation_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10.0, True)):
        with mock.patch.object(function,
                               'setLocationValues'):
            suc = function.setElevation()
            assert suc


def test_setUnattendedFlip_2(function):
    function.app.mount.setting.statusUnattendedFlip = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', False)):
        suc = function.setUnattendedFlip()
        assert not suc


def test_setUnattendedFlip_3(function):
    function.app.mount.setting.statusUnattendedFlip = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(function.app.mount.setting,
                               'setUnattendedFlip',
                               return_value=False):
            suc = function.setUnattendedFlip()
            assert not suc


def test_setUnattendedFlip_4(function):
    function.app.mount.setting.statusUnattendedFlip = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(function.app.mount.setting,
                               'setUnattendedFlip',
                               return_value=True):
            suc = function.setUnattendedFlip()
            assert suc


def test_setDualAxisTracking_2(function):
    function.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', False)):
        suc = function.setDualAxisTracking()
        assert not suc


def test_setDualAxisTracking_3(function):
    function.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(function.app.mount.setting,
                               'setDualAxisTracking',
                               return_value=False):
            suc = function.setDualAxisTracking()
            assert not suc


def test_setDualAxisTracking_4(function):
    function.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(function.app.mount.setting,
                               'setDualAxisTracking',
                               return_value=True):
            suc = function.setDualAxisTracking()
            assert suc


def test_setWOL_2(function):
    function.app.mount.setting.statusWOL = '0'
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', False)):
        suc = function.setWOL()
        assert not suc


def test_setWOL_3(function):
    function.app.mount.setting.statusWOL = '0'
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(function.app.mount.setting,
                               'setWOL',
                               return_value=False):
            suc = function.setWOL()
            assert not suc


def test_setWOL_4(function):
    function.app.mount.setting.statusWOL = '0'
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(function.app.mount.setting,
                               'setWOL',
                               return_value=True):
            suc = function.setWOL()
            assert suc


def test_setRefractionTemp_2(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, False)):
        suc = function.setRefractionTemp()
        assert not suc


def test_setRefractionTemp_3(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefractionTemp',
                               return_value=False):
            suc = function.setRefractionTemp()
            assert not suc


def test_setRefractionTemp_4(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefractionTemp',
                               return_value=True):
            suc = function.setRefractionTemp()
            assert suc


def test_setRefractionPress_2(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, False)):
        suc = function.setRefractionPress()
        assert not suc


def test_setRefractionPress_3(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefractionPress',
                               return_value=False):
            suc = function.setRefractionPress()
            assert not suc


def test_setRefractionPress_4(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefractionPress',
                               return_value=True):
            suc = function.setRefractionPress()
            assert suc


def test_setRefraction_2(function):
    function.app.mount.setting.statusRefraction = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', False)):
        suc = function.setRefraction()
        assert not suc


def test_setRefraction_3(function):
    function.app.mount.setting.statusRefraction = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefraction',
                               return_value=False):
            suc = function.setRefraction()
            assert not suc


def test_setRefraction_4(function):
    function.app.mount.setting.statusRefraction = True
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getItem',
                           return_value=('ON', True)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefraction',
                               return_value=True):
            suc = function.setRefraction()
            assert suc


def test_updatePointGui_ra_j2000(function):
    function.ui.coordsJ2000.setChecked(True)
    obs = ObsSite()
    obs.raJNow = Angle(hours=45)
    obs.decJNow = Angle(degrees=45)
    function.updatePointGUI(obs)


def test_setSettleTimeMount_2(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = function.setSettleTimeMount()
        assert not suc


def test_setSettleTimeMount_3(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setSettleTime',
                               return_value=False):
            suc = function.setSettleTimeMount()
            assert not suc


def test_setSettleTimeMount_4(function):
    function.app.mount.setting.slewRate = 10
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(function.app.mount.setting,
                               'setSettleTime',
                               return_value=True):
            suc = function.setSettleTimeMount()
            assert suc


def test_showOffset_1(function):
    function.ui.clockSync.setChecked(False)
    function.showOffset()


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount'
            '.obsSite.timeDiff', 0.003)
def test_showOffset_2(function):
    function.ui.clockSync.setChecked(True)
    function.showOffset()


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount'
            '.obsSite.timeDiff', 0.3)
def test_showOffset_3(function):
    function.ui.clockSync.setChecked(True)
    function.showOffset()


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite'
            '.timeDiff', 0.6)
def test_showOffset_4(function):
    function.ui.clockSync.setChecked(True)
    function.showOffset()
