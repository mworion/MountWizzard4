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
# Licence APL2.0
#
###########################################################
import unittest.mock as mock
from mw4.mountcontrol.setting import Setting
from packaging.version import Version
from tests.unit_tests.unitTestAddOns.baseTestApp import App

#
#
# testing the class Setting and it's attribute
#
#


def test_webInterfaceStat_1():
    sett = Setting(App().mount)
    sett.webInterfaceStat = False
    assert not sett.webInterfaceStat


def test_webInterfaceStat_2():
    sett = Setting(App().mount)
    sett.webInterfaceStat = True
    assert sett.webInterfaceStat


def test_Setting_slewRate():
    sett = Setting(App().mount)
    sett.slewRate = 67
    assert sett.slewRate == 67


def test_Setting_slewRateMin():
    sett = Setting(App().mount)
    sett.slewRateMin = 67
    assert sett.slewRateMin == 67


def test_Setting_slewRateMax():
    sett = Setting(App().mount)
    sett.slewRateMax = 67
    assert sett.slewRateMax == 67


def test_Setting_timeToFlip():
    sett = Setting(App().mount)
    sett.timeToFlip = 67
    assert sett.timeToFlip == 67


def test_Setting_meridianLimitTrack():
    sett = Setting(App().mount)
    sett.meridianLimitTrack = 67
    assert sett.meridianLimitTrack == 67


def test_Setting_meridianLimitSlew():
    sett = Setting(App().mount)
    sett.meridianLimitSlew = 67
    assert sett.meridianLimitSlew == 67


def test_Setting_timeToMeridian1():
    sett = Setting(App().mount)
    sett.timeToFlip = 10
    sett.meridianLimitTrack = 5
    assert sett.timeToMeridian() == -10


def test_Setting_timeToMeridian2():
    sett = Setting(App().mount)
    sett.timeToFlip = 0
    sett.meridianLimitTrack = 5
    assert sett.timeToMeridian() == -20


def test_Setting_refractionTemp():
    sett = Setting(App().mount)
    sett.refractionTemp = 67
    assert sett.refractionTemp == 67


def test_Setting_refractionPress():
    sett = Setting(App().mount)
    sett.refractionPress = 67
    assert sett.refractionPress == 67


def test_Setting_telescopeTempDEC():
    sett = Setting(App().mount)
    sett.telescopeTempDEC = 67
    assert sett.telescopeTempDEC == 67


def test_Setting_statusRefraction():
    sett = Setting(App().mount)
    sett.statusRefraction = 1
    assert sett.statusRefraction


def test_Setting_statusUnattendedFlip():
    sett = Setting(App().mount)
    sett.statusUnattendedFlip = 1
    assert sett.statusUnattendedFlip


def test_Setting_statusDualAxisTracking():
    sett = Setting(App().mount)
    sett.statusDualAxisTracking = 1
    assert sett.statusDualAxisTracking


def test_Setting_horizonLimitHigh():
    sett = Setting(App().mount)
    sett.horizonLimitHigh = 67
    assert sett.horizonLimitHigh == 67


def test_Setting_horizonLimitLow():
    sett = Setting(App().mount)
    sett.horizonLimitLow = 67
    assert sett.horizonLimitLow == 67


def test_Setting_UTCValid():
    sett = Setting(App().mount)
    sett.UTCValid = 1
    assert sett.UTCValid


def test_Setting_UTCExpire():
    sett = Setting(App().mount)
    sett.UTCExpire = 67
    assert sett.UTCExpire == 67


def test_Setting_typeConnection_1():
    sett = Setting(App().mount)
    sett.typeConnection = 5
    assert sett.typeConnection == 0


def test_Setting_typeConnection_2():
    sett = Setting(App().mount)
    sett.typeConnection = 3


def test_Setting_typeConnection_3():
    sett = Setting(App().mount)
    sett.typeConnection = -6
    assert sett.typeConnection == 0


def test_Setting_gpsSynced_1():
    sett = Setting(App().mount)
    sett.gpsSynced = True
    assert sett.gpsSynced


def test_Setting_addressLanMAC_1():
    sett = Setting(App().mount)
    value = "00:00:00:00:00:00"
    sett.addressLanMAC = "00:00:00:00:00:00"
    assert sett.addressLanMAC == value


def test_Setting_addressWirelessMAC_1():
    sett = Setting(App().mount)
    value = "00:00:00:00:00:00"
    sett.addressWirelessMAC = "00:00:00:00:00:00"
    assert sett.addressWirelessMAC == value


def test_Setting_wakeOnLan_1():
    sett = Setting(App().mount)
    sett.wakeOnLan = "N"
    assert sett.wakeOnLan == "None"


def test_Setting_wakeOnLan_2():
    sett = Setting(App().mount)
    sett.wakeOnLan = "0"
    assert sett.wakeOnLan == "OFF"


def test_Setting_wakeOnLan_3():
    sett = Setting(App().mount)
    sett.wakeOnLan = "1"
    assert sett.wakeOnLan == "ON"


def test_Setting_wakeOnLan_4():
    sett = Setting(App().mount)
    sett.wakeOnLan = "E"
    assert sett.wakeOnLan == "None"


def test_Setting_autoPowerOn_1():
    sett = Setting(App().mount)
    sett.autoPowerOn = "N"
    assert sett.autoPowerOn == "None"


def test_Setting_autoPowerOn_2():
    sett = Setting(App().mount)
    sett.autoPowerOn = "0"
    assert sett.autoPowerOn == "OFF"


def test_Setting_autoPowerOn_3():
    sett = Setting(App().mount)
    sett.autoPowerOn = "1"
    assert sett.autoPowerOn == "ON"


def test_Setting_autoPowerOn_4():
    sett = Setting(App().mount)
    sett.autoPowerOn = "E"
    assert sett.autoPowerOn == "None"


def test_Setting_weatherStatus_1():
    sett = Setting(App().mount)
    sett.weatherStatus = None
    assert sett.weatherStatus == 0
    assert sett._weatherStatus == 0


def test_Setting_weatherStatus_2():
    sett = Setting(App().mount)
    sett.weatherStatus = 0
    assert sett.weatherStatus == 0
    assert sett._weatherStatus == 0


def test_Setting_weatherStatus_3():
    sett = Setting(App().mount)
    sett.weatherStatus = 5
    assert sett.weatherStatus == 0
    assert sett._weatherStatus == 0


def test_Setting_weatherTemperature():
    sett = Setting(App().mount)
    sett.weatherTemperature = 1
    assert sett.weatherTemperature == 1


def test_Setting_weatherPressure():
    sett = Setting(App().mount)
    sett.weatherPressure = 1
    assert sett.weatherPressure == 1


def test_Setting_weatherHumidity():
    sett = Setting(App().mount)
    sett.weatherHumidity = 1
    assert sett.weatherHumidity == 1


def test_Setting_weatherDewPoint():
    sett = Setting(App().mount)
    sett.weatherDewPoint = 1
    assert sett.weatherDewPoint == 1


def test_Setting_weatherAge():
    sett = Setting(App().mount)
    sett.weatherAge = 1
    assert sett.weatherAge == 1
    assert sett.weatherAge == 1


def test_Setting_settleTime():
    sett = Setting(App().mount)
    sett.settleTime = 1
    assert sett.settleTime == 1


#
#
# testing pollSetting med
#
#


def test_Setting_parse_ok():
    sett = Setting(App().mount)
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
    suc = sett.parseSetting(response, 27)
    assert suc


def test_Setting_parse_ok_1():
    sett = Setting(App().mount)
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
    suc = sett.parseSetting(response, 27)
    assert suc


def test_Setting_parse_ok_2():
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


def test_Setting_parse_not_ok0():
    sett = Setting(App().mount)
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
    suc = sett.parseSetting(response, 27)
    assert not suc


def test_Setting_parse_not_ok1():
    sett = Setting(App().mount)
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
    suc = sett.parseSetting(response, 27)
    assert suc


def test_Setting_parse_not_ok2():
    sett = Setting(App().mount)
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
    suc = sett.parseSetting(response, 27)
    assert suc


def test_Setting_parse_not_ok3():
    sett = Setting(App().mount)
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

    suc = sett.parseSetting(response, 27)
    assert suc


def test_Setting_parse_not_ok4():
    sett = Setting(App().mount)
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

    suc = sett.parseSetting(response, 27)
    assert suc


def test_Setting_poll_ok1():
    sett = Setting(App().mount)

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
        suc = sett.pollSetting()
        assert suc


def test_Setting_poll_ok2():
    sett = Setting(App().mount)

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
        suc = sett.pollSetting()
        assert suc


def test_Setting_poll_not_ok1():
    sett = Setting(App().mount)

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
        suc = sett.pollSetting()
        assert not suc


def test_Setting_poll_not_ok2():
    sett = Setting(App().mount)

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
        suc = sett.pollSetting()
        assert not suc


#
#
# testing setDualAxisTracking
#
#


def test_Setting_setDualAxisTracking_ok():
    setting = Setting(App().mount)
    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setDualAxisTracking(1)
        assert suc


def test_Setting_setWOL_ok():
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


def test_Setting_setMeridianLimitTrack_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setMeridianLimitTrack(2)
        assert suc


def test_Setting_setMeridianLimitTrack_not_ok1():
    setting = Setting(App().mount)

    response = ["0"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setMeridianLimitTrack(0)
        assert not suc


def test_Setting_setMeridianLimitTrack_not_ok2():
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


def test_Setting_setMeridianLimitSlew_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setMeridianLimitSlew(5)
        assert suc


def test_Setting_setMeridianLimitSlew_not_ok1():
    setting = Setting(App().mount)

    response = ["0"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setMeridianLimitSlew(-10)
        assert not suc


def test_Setting_setMeridianLimitSlew_not_ok2():
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


def test_Setting_setHorizonLimitLow_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitLow(0)
        assert suc


def test_Setting_setHorizonLimitLow_not_ok3():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitLow(-30)
        assert not suc


def test_Setting_setHorizonLimitLow_not_ok4():
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


def test_Setting_setHorizonLimitHigh_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitHigh(80)
        assert suc


def test_Setting_setHorizonLimitHigh_not_ok3():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setHorizonLimitHigh(-1)
        assert not suc


def test_Setting_setHorizonLimitHigh_not_ok4():
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


def test_Setting_setRefractionTemp_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionTemp(5)
        assert suc


def test_Setting_setRefractionTemp_not_ok3():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionTemp(-45)
        assert not suc


def test_Setting_setRefractionTemp_not_ok4():
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


def test_Setting_setRefractionPress_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionPress(1000)
        assert suc


def test_Setting_setRefractionPress_not_ok3():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setRefractionPress(450)
        assert not suc


def test_Setting_setRefractionPress_not_ok4():
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


def test_Setting_setRefraction_ok():
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


def test_Setting_setRefractionParam_ok():
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        setting.setRefractionParam(temperature=5, pressure=800)


def test_Setting_setRefractionParam_not_ok4():
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setRefractionParam(temperature=-45, pressure=800)
        assert not suc


def test_Setting_setRefractionParam_not_ok5():
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setRefractionParam(temperature=85, pressure=800)
        assert not suc


def test_Setting_setRefractionParam_not_ok6():
    setting = Setting(App().mount)

    response = ["11"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setRefractionParam(temperature=5, pressure=300)
        assert not suc


def test_Setting_setRefractionParam_not_ok7():
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


def test_Setting_setSlewRate_ok():
    setting = Setting(App().mount)

    response = ["10"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        suc = setting.setSlewRate(5)
        assert suc


def test_Setting_setSlewRate_not_ok3():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewRate(0)
        assert not suc


def test_Setting_setSlewRate_not_ok4():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewRate(25)
        assert not suc


def test_setSlewSpeedMax_1():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewSpeedMax()
        assert suc


def test_setSlewSpeedMax_2():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setSlewSpeedMax()
        assert not suc


def test_setSlewSpeedHigh_1():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewSpeedHigh()
        assert suc


def test_setSlewSpeedHigh_2():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setSlewSpeedHigh()
        assert not suc


def test_setSlewSpeedMed_1():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewSpeedMed()
        assert suc


def test_setSlewSpeedMed_2():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = setting.setSlewSpeedMed()
        assert not suc


def test_setSlewSpeedLow_1():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSlewSpeedLow()
        assert suc


def test_setSlewSpeedLow_2():
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


def test_ObsSite_setUnattendedFlip_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setUnattendedFlip(1)
        assert suc


def test_ObsSite_setUnattendedFlip_not_ok1():
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


def test_setDirectWeatherUpdateType_3():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setDirectWeatherUpdateType(0)
        assert suc


def test_setDirectWeatherUpdateType_4():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setDirectWeatherUpdateType(-1)
        assert not suc


def test_setDirectWeatherUpdateType_5():
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


def test_ObsSite_setLunarTracking_ok():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = setting.setLunarTracking()
        assert suc


def test_ObsSite_setLunarTracking_not_ok1():
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


def test_ObsSite_setSiderealTracking_ok():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = setting.setSiderealTracking()
        assert suc


def test_ObsSite_setSiderealTracking_not_ok1():
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


def test_ObsSite_setSolarTracking_ok():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = setting.setSolarTracking()
        assert suc


def test_ObsSite_setSolarTracking_not_ok1():
    setting = Setting(App().mount)
    response = []
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = setting.setSolarTracking()
        assert not suc


def test_Checking_trackingRate1():
    setting = Setting(App().mount)
    setting.trackingRate = 62.4
    assert setting.checkRateLunar()
    assert not setting.checkRateSidereal()
    assert not setting.checkRateSolar()


def test_Checking_trackingRate2():
    setting = Setting(App().mount)
    setting.trackingRate = 60.2
    assert not setting.checkRateLunar()
    assert setting.checkRateSidereal()
    assert not setting.checkRateSolar()


def test_Checking_trackingRate3():
    setting = Setting(App().mount)
    setting.trackingRate = 60.3
    assert not setting.checkRateLunar()
    assert not setting.checkRateSidereal()
    assert setting.checkRateSolar()


def test_Checking_trackingRate4():
    setting = Setting(App().mount)
    setting.trackingRate = 6
    assert not setting.checkRateLunar()
    assert not setting.checkRateSidereal()
    assert not setting.checkRateSolar()


def test_ObsSite_trackingRate():
    setting = Setting(App().mount)
    setting.trackingRate = 67
    assert setting.trackingRate == 67


def test_setWebInterface_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setWebInterface(True)
        assert suc


def test_setSettleTime_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setSettleTime(5)
        assert suc


def test_setAutoPower_ok():
    setting = Setting(App().mount)

    response = ["1"]
    with mock.patch("mw4.mountcontrol.setting.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = setting.setAutoPower(True)
        assert suc
