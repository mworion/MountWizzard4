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
import datetime

# external packages
import PySide6
from PySide6.QtWidgets import QWidget
from skyfield.api import Angle, wgs84

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabMountSett import MountSett


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.threadPool = mainW.app.threadPool
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = MountSett(mainW)
    yield window


def test_updatePointGui_alt(function):
    value = Angle(degrees=45)
    function.app.mount.obsSite.Alt = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '45.00' == function.ui.ALT.text()


def test_updatePointGui_az(function):
    value = Angle(degrees=45)
    function.app.mount.obsSite.Az = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '45.00' == function.ui.AZ.text()


def test_updatePointGui_ra(function):
    function.ui.coordsJ2000.setChecked(True)
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
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


def test_updateSetting_timeToFlip(function):
    value = 15
    function.app.mount.setting.timeToFlip = value
    function.updateSettingGUI(function.app.mount.setting)
    assert ' 15' == function.ui.timeToFlip.text()


def test_updateSettingGUI_UTCExpire(function):
    value = '2020-10-05'
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert value == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_1(function):
    value = '2016-10-05'
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert value == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_2(function):
    tomorrow = datetime.date.today() + datetime.timedelta(days=15)
    value = tomorrow.strftime('%Y-%m-%d')
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert value == function.ui.UTCExpire.text()


def test_updateSettingGUI_UTCExpire_3(function):
    tomorrow = datetime.date.today() + datetime.timedelta(days=40)
    value = tomorrow.strftime('%Y-%m-%d')
    function.app.mount.setting.UTCExpire = value
    function.updateSettingGUI(function.app.mount.setting)
    assert value == function.ui.UTCExpire.text()


def test_updateSettingGUI_statusUnattendedFlip(function):
    value = True
    function.app.mount.setting.statusUnattendedFlip = value
    function.updateSettingGUI(function.app.mount.setting)
    assert 'ON' == function.ui.statusUnattendedFlip.text()


def test_updateSettingGUI_statusDualAxisTracking(function):
    value = True
    function.app.mount.setting.statusDualAxisTracking = value
    function.updateSettingGUI(function.app.mount.setting)
    assert 'ON' == function.ui.statusDualAxisTracking.text()


def test_updateSettingGUI_statusRefraction(function):
    value = True
    function.app.mount.setting.statusRefraction = value
    function.updateSettingGUI(function.app.mount.setting)
    assert 'ON' == function.ui.statusRefraction.text()


def test_updateSettingGUI_1(function):
    function.app.mount.setting.gpsSynced = True
    function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.statusGPSSynced.text() == 'ON'


def test_updateSettingGUI_2(function):
    function.app.mount.setting.gpsSynced = False
    function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.statusGPSSynced.text() == 'OFF'


def test_updateSettingGUI_3(function):
    function.app.mount.setting.gpsSynced = None
    function.updateSettingGUI(function.app.mount.setting)
    assert function.ui.statusGPSSynced.text() == '-'


def test_updateSettingGUI_4(function):
    function.app.mount.setting.typeConnection = None
    function.app.mount.setting.wakeOnLan = 'On'
    function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_5(function):
    function.app.mount.setting.typeConnection = 1
    function.app.mount.setting.wakeOnLan = None
    function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_6(function):
    function.app.mount.setting.typeConnection = 1
    function.app.mount.setting.wakeOnLan = 'OFF'
    function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_7(function):
    function.app.mount.setting.webInterfaceStat = False
    function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_8(function):
    function.app.mount.setting.webInterfaceStat = True
    suc = function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_9(function):
    function.app.mount.setting.webInterfaceStat = None
    function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_10(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.setting,
                           'checkRateLunar',
                           return_value=True):
        function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_11(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.setting,
                           'checkRateSidereal',
                           return_value=True):
        function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_12(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.setting,
                           'checkRateSolar',
                           return_value=True):
        function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_13(function):
    function.app.mount.obsSite.status = 10
    with mock.patch.object(function.app.mount.setting,
                           'checkRateSolar',
                           return_value=True):
        function.updateSettingGUI(function.app.mount.setting)


def test_updateSettingGUI_14(function):
    function.app.mount.obsSite.status = None
    with mock.patch.object(function.app.mount.setting,
                           'checkRateSolar',
                           return_value=True):
        function.updateSettingGUI(function.app.mount.setting)


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


def test_updateSetting_refractionPress(function):
    value = 1050.0
    function.app.mount.setting.refractionPress = value
    function.updateSettingGUI(function.app.mount.setting)
    assert str(value) == function.ui.refractionPress.text()
    assert str(value) == function.ui.refractionPress1.text()


def test_updateSetting_meridianLimitTrack_1(function):
    value = 15
    function.app.mount.setting.meridianLimitTrack = value
    function.updateSettingGUI(function.app.mount.setting)
    assert ' 15' == function.ui.meridianLimitTrack.text()


def test_updateSetting_meridianLimitSlew(function):
    value = 15
    function.app.mount.setting.meridianLimitSlew = value
    function.updateSettingGUI(function.app.mount.setting)
    assert ' 15' == function.ui.meridianLimitSlew.text()


def test_updateSetting_horizonLimitLow(function):
    value = 0
    function.app.mount.setting.horizonLimitLow = value
    function.updateSettingGUI(function.app.mount.setting)
    assert '  0' == function.ui.horizonLimitLow.text()


def test_updateSetting_horizonLimitHigh(function):
    value = 50
    function.app.mount.setting.horizonLimitHigh = value
    function.updateSettingGUI(function.app.mount.setting)
    assert ' 50' == function.ui.horizonLimitHigh.text()


def test_updateSetting_timeToMeridian(function):
    function.app.mount.setting.timeToFlip = 100
    function.app.mount.setting.meridianLimitTrack = 15

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
    value = Angle(hours=45)
    function.app.mount.obsSite.raJNow = value
    value = Angle(degrees=45)
    function.app.mount.obsSite.decJNow = value
    function.updatePointGUI(function.app.mount.obsSite)


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
