############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import pytest
import unittest.mock as mock
from mw4.mountcontrol.setting import Setting
from packaging.version import Version
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    yield Setting(App().mount)


#
#
# testing the class Setting and it's attribute
#
#


def test_webInterfaceStat_1(function):
    function.webInterfaceStat = False
    assert not function.webInterfaceStat


def test_webInterfaceStat_2(function):
    function.webInterfaceStat = True
    assert function.webInterfaceStat


def test_Setting_slewRate(function):
    function.slewRate = 67
    assert function.slewRate == 67


def test_Setting_slewRateMin(function):
    function.slewRateMin = 67
    assert function.slewRateMin == 67


def test_Setting_slewRateMax(function):
    function.slewRateMax = 67
    assert function.slewRateMax == 67


def test_Setting_timeToFlip(function):
    function.timeToFlip = 67
    assert function.timeToFlip == 67


def test_Setting_meridianLimitTrack(function):
    function.meridianLimitTrack = 67
    assert function.meridianLimitTrack == 67


def test_Setting_meridianLimitSlew(function):
    function.meridianLimitSlew = 67
    assert function.meridianLimitSlew == 67


def test_Setting_timeToMeridian1(function):
    function.timeToFlip = 10
    function.meridianLimitTrack = 5
    assert function.timeToMeridian() == -10


def test_Setting_timeToMeridian2(function):
    function.timeToFlip = 0
    function.meridianLimitTrack = 5
    assert function.timeToMeridian() == -20


def test_Setting_refractionTemp(function):
    function.refractionTemp = 67
    assert function.refractionTemp == 67


def test_Setting_refractionPress(function):
    function.refractionPress = 67
    assert function.refractionPress == 67


def test_Setting_telescopeTempDEC(function):
    function.telescopeTempDEC = 67
    assert function.telescopeTempDEC == 67


def test_Setting_statusRefraction(function):
    function.statusRefraction = 1
    assert function.statusRefraction


def test_Setting_statusUnattendedFlip(function):
    function.statusUnattendedFlip = 1
    assert function.statusUnattendedFlip


def test_Setting_statusDualAxisTracking(function):
    function.statusDualAxisTracking = 1
    assert function.statusDualAxisTracking


def test_Setting_horizonLimitHigh(function):
    function.horizonLimitHigh = 67
    assert function.horizonLimitHigh == 67


def test_Setting_horizonLimitLow(function):
    function.horizonLimitLow = 67
    assert function.horizonLimitLow == 67


def test_Setting_UTCValid(function):
    function.UTCValid = 1
    assert function.UTCValid


def test_Setting_UTCExpire(function):
    function.UTCExpire = 67
    assert function.UTCExpire == 67


def test_Setting_typeConnection_1(function):
    function.typeConnection = 5
    assert function.typeConnection == 0


def test_Setting_typeConnection_2(function):
    function.typeConnection = 3


def test_Setting_typeConnection_3(function):
    function.typeConnection = -6
    assert function.typeConnection == 0


def test_Setting_gpsSynced_1(function):
    function.gpsSynced = True
    assert function.gpsSynced


def test_Setting_addressLanMAC_1(function):
    value = "00:00:00:00:00:00"
    function.addressLanMAC = "00:00:00:00:00:00"
    assert function.addressLanMAC == value


def test_Setting_addressWirelessMAC_1(function):
    value = "00:00:00:00:00:00"
    function.addressWirelessMAC = "00:00:00:00:00:00"
    assert function.addressWirelessMAC == value


def test_Setting_wakeOnLan_1(function):
    function.wakeOnLan = "N"
    assert function.wakeOnLan == "None"


def test_Setting_wakeOnLan_2(function):
    function.wakeOnLan = "0"
    assert function.wakeOnLan == "OFF"


def test_Setting_wakeOnLan_3(function):
    function.wakeOnLan = "1"
    assert function.wakeOnLan == "ON"


def test_Setting_wakeOnLan_4(function):
    function.wakeOnLan = "E"
    assert function.wakeOnLan == "None"


def test_Setting_autoPowerOn_1(function):
    function.autoPowerOn = "N"
    assert function.autoPowerOn == "None"


def test_Setting_autoPowerOn_2(function):
    function.autoPowerOn = "0"
    assert function.autoPowerOn == "OFF"


def test_Setting_autoPowerOn_3(function):
    function.autoPowerOn = "1"
    assert function.autoPowerOn == "ON"


def test_Setting_autoPowerOn_4(function):
    function.autoPowerOn = "E"
    assert function.autoPowerOn == "None"


def test_Setting_weatherStatus_1(function):
    function.weatherStatus = None
    assert function.weatherStatus == 0
    assert function._weatherStatus == 0


def test_Setting_weatherStatus_2(function):
    function.weatherStatus = 0
    assert function.weatherStatus == 0
    assert function._weatherStatus == 0


def test_Setting_weatherStatus_3(function):
    function.weatherStatus = 5
    assert function.weatherStatus == 0
    assert function._weatherStatus == 0


def test_Setting_weatherTemperature(function):
    function.weatherTemperature = 1
    assert function.weatherTemperature == 1


def test_Setting_weatherPressure(function):
    function.weatherPressure = 1
    assert function.weatherPressure == 1


def test_Setting_weatherHumidity(function):
    function.weatherHumidity = 1
    assert function.weatherHumidity == 1


def test_Setting_weatherDewPoint(function):
    function.weatherDewPoint = 1
    assert function.weatherDewPoint == 1


def test_Setting_weatherAge(function):
    function.weatherAge = 1
    assert function.weatherAge == 1
    assert function.weatherAge == 1


def test_Setting_settleTime(function):
    function.settleTime = 1
    assert function.settleTime == 1


#
#
# testing pollSetting med
#
#


def test_Setting_parse_ok(function):
    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]
    suc = function.parseSetting(response, 27)
    assert suc


def test_Setting_parse_ok_1(function):
    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "E",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]
    suc = function.parseSetting(response, 27)
    assert suc


def test_Setting_parse_ok_2(function):
    mount = App().mount
    mount.firmware.vString = Version("2.16.00")
    sett = Setting(mount)
    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "E",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
    ]
    with mock.patch.object(mount.firmware, "checkNewer", return_value=False):
        suc = sett.parseSetting(response, 24)
        assert suc


def test_Setting_parse_not_ok0(function):
    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0EEE.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "+20,5",
        "1",
        "A,G,N,H",
        "1",
    ]
    suc = function.parseSetting(response, 27)
    assert not suc


def test_Setting_parse_not_ok1(function):
    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0EEE.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]
    suc = function.parseSetting(response, 27)
    assert suc


def test_Setting_parse_not_ok2(function):
    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]
    suc = function.parseSetting(response, 27)
    assert suc


def test_Setting_parse_not_ok3(function):
    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]

    suc = function.parseSetting(response, 27)
    assert suc


def test_Setting_parse_not_ok4(function):
    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        ",2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]

    suc = function.parseSetting(response, 27)
    assert suc


def test_Setting_poll_ok1(function):

    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]

    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 27
        suc = function.pollSetting()
        assert suc


def test_Setting_poll_ok2(function):

    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]

    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 27
        suc = function.pollSetting()
        assert suc


def test_Setting_poll_not_ok1(function):

    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "00005.000",
        "1",
        "A,G,N,H",
        "1",
    ]

    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 27
        suc = function.pollSetting()
        assert not suc


def test_Setting_poll_not_ok2(function):

    response = [
        "15",
        "1",
        "20",
        "0426",
        "05",
        "+010.0",
        "0950.0",
        "60.2",
        "+033.0",
        "101+90*",
        "+00*",
        "E,2018-08-11",
        "1",
        "0",
        "00:00:00:00:00:00",
        "N",
        "0",
        "987.0,0100",
        "+20,5",
        "90.4",
        "-13,5",
        "60.2",
        "1",
        "A,G,N,H",
        "1",
    ]

    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 6
        suc = function.pollSetting()
        assert not suc


#
#
# testing setDualAxisTracking
#
#


def test_Setting_setDualAxisTracking_ok(function):
    setting = Setting(App().mount)
    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setDualAxisTracking(1)
        assert suc


def test_Setting_setWOL_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setWOL(True)
        assert suc


#
#
# testing setMeridianLimitTrack
#
#


def test_Setting_setMeridianLimitTrack_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setMeridianLimitTrack(2)
        assert suc


def test_Setting_setMeridianLimitTrack_not_ok1(function):
    setting = Setting(App().mount)

    response = ["0"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setMeridianLimitTrack(0)
        assert not suc


def test_Setting_setMeridianLimitTrack_not_ok2(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setMeridianLimitTrack(40)
        assert not suc


#
#
# testing setMeridianLimitSlew
#
#


def test_Setting_setMeridianLimitSlew_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setMeridianLimitSlew(5)
        assert suc


def test_Setting_setMeridianLimitSlew_not_ok1(function):
    setting = Setting(App().mount)

    response = ["0"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setMeridianLimitSlew(-10)
        assert not suc


def test_Setting_setMeridianLimitSlew_not_ok2(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setMeridianLimitSlew(50)
        assert not suc


#
#
# testing setHorizonLimitLow
#
#


def test_Setting_setHorizonLimitLow_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitLow(0)
        assert suc


def test_Setting_setHorizonLimitLow_not_ok3(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitLow(-30)
        assert not suc


def test_Setting_setHorizonLimitLow_not_ok4(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitLow(50)
        assert not suc


#
#
# testing setHorizonLimitLow
#
#


def test_Setting_setHorizonLimitHigh_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitHigh(80)
        assert suc


def test_Setting_setHorizonLimitHigh_not_ok3(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitHigh(-1)
        assert not suc


def test_Setting_setHorizonLimitHigh_not_ok4(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitHigh(100)
        assert not suc


#
#
# testing setRefractionTemp
#
#


def test_Setting_setRefractionTemp_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionTemp(5)
        assert suc


def test_Setting_setRefractionTemp_not_ok3(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionTemp(-45)
        assert not suc


def test_Setting_setRefractionTemp_not_ok4(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionTemp(85)
        assert not suc


#
#
# testing setRefractionPress
#
#


def test_Setting_setRefractionPress_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionPress(1000)
        assert suc


def test_Setting_setRefractionPress_not_ok3(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionPress(450)
        assert not suc


def test_Setting_setRefractionPress_not_ok4(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionPress(1400)
        assert not suc


#
#
# testing setRefraction
#
#


def test_Setting_setRefraction_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefraction(1)
        assert suc


#
#
# testing setRefractionParam
#
#


def test_Setting_setRefractionParam_ok(function):
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        setting.setRefractionParam(temperature=5, pressure=800)


def test_Setting_setRefractionParam_not_ok4(function):
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setRefractionParam(temperature=-45, pressure=800)
        assert not suc


def test_Setting_setRefractionParam_not_ok5(function):
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setRefractionParam(temperature=85, pressure=800)
        assert not suc


def test_Setting_setRefractionParam_not_ok6(function):
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setRefractionParam(temperature=5, pressure=300)
        assert not suc


def test_Setting_setRefractionParam_not_ok7(function):
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setRefractionParam(temperature=5, pressure=1500)
        assert not suc


#
#
# testing setSlewRate
#
#


def test_Setting_setSlewRate_ok(function):
    setting = Setting(App().mount)

    response = ["10"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setSlewRate(5)
        assert suc


def test_Setting_setSlewRate_not_ok3(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewRate(0)
        assert not suc


def test_Setting_setSlewRate_not_ok4(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewRate(25)
        assert not suc


def test_setSlewSpeedMax_1(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewSpeedMax()
        assert suc


def test_setSlewSpeedMax_2(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setSlewSpeedMax()
        assert not suc


def test_setSlewSpeedHigh_1(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewSpeedHigh()
        assert suc


def test_setSlewSpeedHigh_2(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setSlewSpeedHigh()
        assert not suc


def test_setSlewSpeedMed_1(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewSpeedMed()
        assert suc


def test_setSlewSpeedMed_2(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setSlewSpeedMed()
        assert not suc


def test_setSlewSpeedLow_1(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewSpeedLow()
        assert suc


def test_setSlewSpeedLow_2(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setSlewSpeedLow()
        assert not suc


#
#
# testing setUnattendedFlip
#
#


def test_ObsSite_setUnattendedFlip_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setUnattendedFlip(1)
        assert suc


def test_ObsSite_setUnattendedFlip_not_ok1(function):
    setting = Setting(App().mount)

    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = setting.setUnattendedFlip(1)
        assert not suc


#
#
# testing setUnattendedFlip
#
#


def test_setDirectWeatherUpdateType_3(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setDirectWeatherUpdateType(0)
        assert suc


def test_setDirectWeatherUpdateType_4(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setDirectWeatherUpdateType(-1)
        assert not suc


def test_setDirectWeatherUpdateType_5(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setDirectWeatherUpdateType(5)
        assert not suc


#
#
# testing setLunarTracking
#
#


def test_ObsSite_setLunarTracking_ok(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = setting.setLunarTracking()
        assert suc


def test_ObsSite_setLunarTracking_not_ok1(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = setting.setLunarTracking()
        assert not suc


#
#
# testing setSiderealTracking
#
#


def test_ObsSite_setSiderealTracking_ok(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = setting.setSiderealTracking()
        assert suc


def test_ObsSite_setSiderealTracking_not_ok1(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = setting.setSiderealTracking()
        assert not suc


#
#
# testing setSolarTracking
#
#


def test_ObsSite_setSolarTracking_ok(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = setting.setSolarTracking()
        assert suc


def test_ObsSite_setSolarTracking_not_ok1(function):
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = setting.setSolarTracking()
        assert not suc


def test_Checking_trackingRate1(function):
    setting = Setting(App().mount)
    setting.trackingRate = 62.4
    assert setting.checkRateLunar()
    assert not setting.checkRateSidereal()
    assert not setting.checkRateSolar()


def test_Checking_trackingRate2(function):
    setting = Setting(App().mount)
    setting.trackingRate = 60.2
    assert not setting.checkRateLunar()
    assert setting.checkRateSidereal()
    assert not setting.checkRateSolar()


def test_Checking_trackingRate3(function):
    setting = Setting(App().mount)
    setting.trackingRate = 60.3
    assert not setting.checkRateLunar()
    assert not setting.checkRateSidereal()
    assert setting.checkRateSolar()


def test_Checking_trackingRate4(function):
    setting = Setting(App().mount)
    setting.trackingRate = 6
    assert not setting.checkRateLunar()
    assert not setting.checkRateSidereal()
    assert not setting.checkRateSolar()


def test_ObsSite_trackingRate(function):
    setting = Setting(App().mount)
    setting.trackingRate = 67
    assert setting.trackingRate == 67


def test_setWebInterface_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setWebInterface(True)
        assert suc


def test_setSettleTime_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSettleTime(5)
        assert suc


def test_setAutoPower_ok(function):
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setAutoPower(True)
        assert suc
