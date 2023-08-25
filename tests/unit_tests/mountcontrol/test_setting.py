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
import unittest
import unittest.mock as mock
# external packages
# local imports
from mountcontrol.setting import Setting


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    #
    #
    # testing the class Setting and it's attribute
    #
    #

    def test_webInterfaceStat_1(self):
        sett = Setting()
        sett.webInterfaceStat = '0'
        assert not sett.webInterfaceStat

    def test_webInterfaceStat_2(self):
        sett = Setting()
        sett.webInterfaceStat = '1'
        assert sett.webInterfaceStat

    def test_webInterfaceStat_3(self):
        sett = Setting()
        sett.webInterfaceStat = 'E'
        assert sett.webInterfaceStat is None

    def test_Setting_slewRate(self):
        sett = Setting()
        sett.slewRate = '67'
        self.assertEqual(67, sett.slewRate)
        self.assertEqual(67, sett._slewRate)

    def test_Setting_slewRateMin(self):
        sett = Setting()
        sett.slewRateMin = '67'
        self.assertEqual(67, sett.slewRateMin)
        self.assertEqual(67, sett._slewRateMin)

    def test_Setting_slewRateMax(self):
        sett = Setting()
        sett.slewRateMax = '67'
        self.assertEqual(67, sett.slewRateMax)
        self.assertEqual(67, sett._slewRateMax)

    def test_Setting_timeToFlip(self):
        sett = Setting()
        sett.timeToFlip = '67'
        self.assertEqual(67, sett.timeToFlip)
        self.assertEqual(67, sett._timeToFlip)

    def test_Setting_meridianLimitTrack(self):
        sett = Setting()
        sett.meridianLimitTrack = '67'
        self.assertEqual(67, sett.meridianLimitTrack)
        self.assertEqual(67, sett._meridianLimitTrack)

    def test_Setting_meridianLimitSlew(self):
        sett = Setting()
        sett.meridianLimitSlew = '67'
        self.assertEqual(67, sett.meridianLimitSlew)
        self.assertEqual(67, sett._meridianLimitSlew)

    def test_Setting_timeToMeridian1(self):
        sett = Setting()
        sett.timeToFlip = '10'
        sett.meridianLimitTrack = '5'
        self.assertEqual(-10, sett.timeToMeridian())

    def test_Setting_timeToMeridian2(self):
        sett = Setting()
        sett.timeToFlip = None
        sett.meridianLimitTrack = '5'
        self.assertEqual(None, sett.timeToMeridian())

    def test_Setting_refractionTemp(self):
        sett = Setting()
        sett.refractionTemp = '67'
        self.assertEqual(67, sett.refractionTemp)
        self.assertEqual(67, sett._refractionTemp)

    def test_Setting_refractionPress(self):
        sett = Setting()
        sett.refractionPress = '67'
        self.assertEqual(67, sett.refractionPress)
        self.assertEqual(67, sett._refractionPress)

    def test_Setting_telescopeTempDEC(self):
        sett = Setting()
        sett.telescopeTempDEC = '67'
        self.assertEqual(67, sett.telescopeTempDEC)

    def test_Setting_statusRefraction(self):
        sett = Setting()
        sett.statusRefraction = 1
        self.assertEqual(True, sett.statusRefraction)
        self.assertEqual(True, sett._statusRefraction)

    def test_Setting_statusUnattendedFlip(self):
        sett = Setting()
        sett.statusUnattendedFlip = 1
        self.assertEqual(True, sett.statusUnattendedFlip)
        self.assertEqual(True, sett._statusUnattendedFlip)

    def test_Setting_statusDualAxisTracking(self):
        sett = Setting()
        sett.statusDualAxisTracking = 1
        self.assertEqual(True, sett.statusDualAxisTracking)
        self.assertEqual(True, sett._statusDualAxisTracking)

    def test_Setting_horizonLimitHigh(self):
        sett = Setting()
        sett.horizonLimitHigh = '67'
        self.assertEqual(67, sett.horizonLimitHigh)
        self.assertEqual(67, sett._horizonLimitHigh)

    def test_Setting_horizonLimitLow(self):
        sett = Setting()
        sett.horizonLimitLow = '67'
        self.assertEqual(67, sett.horizonLimitLow)
        self.assertEqual(67, sett._horizonLimitLow)

    def test_Setting_UTCValid(self):
        sett = Setting()
        sett.UTCValid = 1
        self.assertEqual(True, sett.UTCValid)
        self.assertEqual(True, sett._UTCValid)

    def test_Setting_UTCExpire(self):
        sett = Setting()
        sett.UTCExpire = '67'
        self.assertEqual('67', sett.UTCExpire)
        self.assertEqual('67', sett._UTCExpire)

    def test_Setting_UTCExpire1(self):
        sett = Setting()
        sett.UTCExpire = 67
        self.assertEqual(None, sett.UTCExpire)
        self.assertEqual(None, sett._UTCExpire)

    def test_Setting_typeConnection_1(self):
        sett = Setting()
        sett.typeConnection = 5
        self.assertEqual(None, sett.typeConnection)
        self.assertEqual(None, sett._typeConnection)

    def test_Setting_typeConnection_2(self):
        sett = Setting()
        sett.typeConnection = 3
        self.assertEqual(3, sett.typeConnection)
        self.assertEqual(3, sett._typeConnection)

    def test_Setting_typeConnection_3(self):
        sett = Setting()
        sett.typeConnection = None
        self.assertEqual(None, sett.typeConnection)
        self.assertEqual(None, sett._typeConnection)

    def test_Setting_gpsSynced_1(self):
        sett = Setting()
        sett.gpsSynced = 5
        self.assertEqual(True, sett.gpsSynced)
        self.assertEqual(True, sett._gpsSynced)

    def test_Setting_gpsSynced_2(self):
        sett = Setting()
        sett.gpsSynced = 0
        self.assertEqual(False, sett.gpsSynced)
        self.assertEqual(False, sett._gpsSynced)

    def test_Setting_addressLanMAC_1(self):
        sett = Setting()
        value = '00:00:00:00:00:00'
        sett.addressLanMAC = '00:00:00:00:00:00'
        self.assertEqual(value, sett.addressLanMAC)
        self.assertEqual(value, sett._addressLanMAC)

    def test_Setting_addressWirelessMAC_1(self):
        sett = Setting()
        value = '00:00:00:00:00:00'
        sett.addressWirelessMAC = '00:00:00:00:00:00'
        self.assertEqual(value, sett.addressWirelessMAC)
        self.assertEqual(value, sett._addressWirelessMAC)

    def test_Setting_wakeOnLan_1(self):
        sett = Setting()
        sett.wakeOnLan = 'N'
        self.assertEqual('None', sett.wakeOnLan)
        self.assertEqual('None', sett._wakeOnLan)

    def test_Setting_wakeOnLan_2(self):
        sett = Setting()
        sett.wakeOnLan = '0'
        self.assertEqual('OFF', sett.wakeOnLan)
        self.assertEqual('OFF', sett._wakeOnLan)

    def test_Setting_wakeOnLan_3(self):
        sett = Setting()
        sett.wakeOnLan = '1'
        self.assertEqual('ON', sett.wakeOnLan)
        self.assertEqual('ON', sett._wakeOnLan)

    def test_Setting_wakeOnLan_4(self):
        sett = Setting()
        sett.wakeOnLan = 'E'
        assert sett.wakeOnLan is None
        assert sett._wakeOnLan is None

    def test_Setting_weatherStatus_1(self):
        sett = Setting()
        sett.weatherStatus = None
        assert sett.weatherStatus is None
        assert sett._weatherStatus is None

    def test_Setting_weatherStatus_2(self):
        sett = Setting()
        sett.weatherStatus = 0
        self.assertEqual(0, sett.weatherStatus)
        self.assertEqual(0, sett._weatherStatus)

    def test_Setting_weatherStatus_3(self):
        sett = Setting()
        sett.weatherStatus = 5
        assert sett.weatherStatus is None
        assert sett._weatherStatus is None

    def test_Setting_weatherTemperature(self):
        sett = Setting()
        sett.weatherTemperature = 1
        self.assertEqual(1, sett.weatherTemperature)
        self.assertEqual(1, sett._weatherTemperature)

    def test_Setting_weatherPressure(self):
        sett = Setting()
        sett.weatherPressure = 1
        self.assertEqual(1, sett.weatherPressure)
        self.assertEqual(1, sett._weatherPressure)

    def test_Setting_weatherHumidity(self):
        sett = Setting()
        sett.weatherHumidity = 1
        self.assertEqual(1, sett.weatherHumidity)
        self.assertEqual(1, sett._weatherHumidity)

    def test_Setting_weatherDewPoint(self):
        sett = Setting()
        sett.weatherDewPoint = 1
        self.assertEqual(1, sett.weatherDewPoint)
        self.assertEqual(1, sett._weatherDewPoint)

    def test_Setting_weatherAge(self):
        sett = Setting()
        sett.weatherAge = 1
        self.assertEqual(1, sett.weatherAge)
        self.assertEqual(1, sett.weatherAge)

    def test_Setting_settleTime(self):
        sett = Setting()
        sett.settleTime = '1'
        self.assertEqual(1, sett.settleTime)
        self.assertEqual(1, sett._settleTime)

    #
    #
    # testing pollSetting med
    #
    #

    def test_Setting_parse_ok(self):
        sett = Setting()
        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*',
                    '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']
        suc = sett.parseSetting(response,  24)
        self.assertEqual(True, suc)

    def test_Setting_parse_ok_1(self):
        sett = Setting()
        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*',
                    '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', 'E', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']
        suc = sett.parseSetting(response,  24)
        self.assertEqual(True, suc)

    def test_Setting_parse_not_ok0(self):
        sett = Setting()
        response = ['15', '1', '20', '0426', '05', '+010.0', '0EEE.0', '60.2', '+033.0',
                    '101+90*',
                    '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5']
        suc = sett.parseSetting(response,  24)
        self.assertEqual(False, suc)

    def test_Setting_parse_not_ok1(self):
        sett = Setting()
        response = ['15', '1', '20', '0426', '05', '+010.0', '0EEE.0', '60.2', '+033.0',
                    '101+90*',
                    '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']
        suc = sett.parseSetting(response,  24)
        self.assertEqual(True, suc)

    def test_Setting_parse_not_ok2(self):
        sett = Setting()
        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '+90*',
                    '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']
        suc = sett.parseSetting(response,  24)
        self.assertEqual(True, suc)

    def test_Setting_parse_not_ok3(self):
        sett = Setting()
        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*',
                    '+00', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']

        suc = sett.parseSetting(response,  24)
        self.assertEqual(True, suc)

    def test_Setting_parse_not_ok4(self):
        sett = Setting(
                       )
        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*',
                    '+00*', ',2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']

        suc = sett.parseSetting(response,  24)

        self.assertEqual(True, suc)

    def test_Setting_poll_ok1(self):
        sett = Setting()

        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*', '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']

        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response,  24
            suc = sett.pollSetting()
            self.assertEqual(True, suc)

    def test_Setting_poll_ok2(self):
        sett = Setting()

        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*', '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']

        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response,  24
            suc = sett.pollSetting()
            self.assertEqual(True, suc)

    def test_Setting_poll_not_ok1(self):
        sett = Setting()

        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*', '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1',
                    '00005.000']

        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response,  24
            suc = sett.pollSetting()
            self.assertEqual(False, suc)

    def test_Setting_poll_not_ok2(self):
        sett = Setting()

        response = ['15', '1', '20', '0426', '05', '+010.0', '0950.0', '60.2', '+033.0',
                    '101+90*', '+00*', 'E,2018-08-11', '1', '0', '00:00:00:00:00:00', 'N',
                    '0', '987.0,0100', '+20,5', '90.4', '-13,5', '60.2', '1']

        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 6
            suc = sett.pollSetting()
            self.assertEqual(False, suc)

    #
    #
    # testing setDualAxisTracking
    #
    #

    def test_Setting_setDualAxisTracking_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setDualAxisTracking(1)
            self.assertEqual(True, suc)

    def test_Setting_setDualAxisTracking_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setDualAxisTracking(1)
            self.assertEqual(False, suc)

    def test_Setting_setDualAxisTracking_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setDualAxisTracking(1)
            self.assertEqual(False, suc)

    def test_Setting_setWOL_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setWOL(True)
            self.assertEqual(True, suc)

    def test_Setting_setWOL_not_ok1(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setWOL(True)
            self.assertEqual(False, suc)

    def test_Setting_setWOL_not_ok2(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setWOL(True)
            self.assertEqual(False, suc)

    #
    #
    # testing setMeridianLimitTrack
    #
    #

    def test_Setting_setMeridianLimitTrack_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setMeridianLimitTrack(2)
            self.assertEqual(True, suc)

    def test_Setting_setMeridianLimitTrack_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setMeridianLimitTrack(0)
            self.assertEqual(False, suc)

    def test_Setting_setMeridianLimitTrack_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setMeridianLimitTrack(40)
            self.assertEqual(False, suc)

    def test_Setting_setMeridianLimitTrack_not_ok3(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setMeridianLimitTrack(20)
            self.assertEqual(False, suc)

    def test_Setting_setMeridianLimitTrack_not_ok4(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setMeridianLimitTrack(20)
            self.assertEqual(False, suc)

    #
    #
    # testing setMeridianLimitSlew
    #
    #

    def test_Setting_setMeridianLimitSlew_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setMeridianLimitSlew(5)
            self.assertEqual(True, suc)

    def test_Setting_setMeridianLimitSlew_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setMeridianLimitSlew(-10)
            self.assertEqual(False, suc)

    def test_Setting_setMeridianLimitSlew_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setMeridianLimitSlew(50)
            self.assertEqual(False, suc)

    def test_Setting_setMeridianLimitSlew_not_ok3(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setMeridianLimitSlew(5)
            self.assertEqual(False, suc)

    def test_Setting_setMeridianLimitSlew_not_ok4(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setMeridianLimitSlew(5)
            self.assertEqual(False, suc)

    #
    #
    # testing setHorizonLimitLow
    #
    #

    def test_Setting_setHorizonLimitLow_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setHorizonLimitLow(0)
            self.assertEqual(True, suc)

    def test_Setting_setHorizonLimitLow_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setHorizonLimitLow(0)
            self.assertEqual(False, suc)

    def test_Setting_setHorizonLimitLow_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setHorizonLimitLow(0)
            self.assertEqual(False, suc)

    def test_Setting_setHorizonLimitLow_not_ok3(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setHorizonLimitLow(-30)
            self.assertEqual(False, suc)

    def test_Setting_setHorizonLimitLow_not_ok4(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setHorizonLimitLow(50)
            self.assertEqual(False, suc)

    #
    #
    # testing setHorizonLimitLow
    #
    #

    def test_Setting_setHorizonLimitHigh_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setHorizonLimitHigh(80)
            self.assertEqual(True, suc)

    def test_Setting_setHorizonLimitHigh_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setHorizonLimitHigh(80)
            self.assertEqual(False, suc)

    def test_Setting_setHorizonLimitHigh_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setHorizonLimitHigh(80)
            self.assertEqual(False, suc)

    def test_Setting_setHorizonLimitHigh_not_ok3(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setHorizonLimitHigh(-1)
            self.assertEqual(False, suc)

    def test_Setting_setHorizonLimitHigh_not_ok4(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setHorizonLimitHigh(100)
            self.assertEqual(False, suc)

    #
    #
    # testing setRefractionTemp
    #
    #

    def test_Setting_setRefractionTemp_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionTemp(5)
            self.assertEqual(True, suc)

    def test_Setting_setRefractionTemp_not_ok0(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionTemp(None)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionTemp_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionTemp(5)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionTemp_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setRefractionTemp(5)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionTemp_not_ok3(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionTemp(-45)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionTemp_not_ok4(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionTemp(85)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionTemp_not_ok5(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionTemp(-0)
            self.assertEqual(True, suc)

    #
    #
    # testing setRefractionPress
    #
    #

    def test_Setting_setRefractionPress_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionPress(1000)
            self.assertEqual(True, suc)

    def test_Setting_setRefractionPress_not_ok0(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionPress(None)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionPress_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionPress(1000)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionPress_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setRefractionPress(1000)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionPress_not_ok3(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionPress(450)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionPress_not_ok4(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefractionPress(1400)
            self.assertEqual(False, suc)

    #
    #
    # testing setRefraction
    #
    #

    def test_Setting_setRefraction_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefraction(1)
            self.assertEqual(True, suc)

    def test_Setting_setRefraction_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setRefraction(1)
            self.assertEqual(False, suc)

    def test_Setting_setRefraction_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setRefraction(1)
            self.assertEqual(False, suc)

    #
    #
    # testing setRefractionParam
    #
    #

    def test_Setting_setRefractionParam_ok(self):
        setting = Setting()

        response = ['11']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=5,
                                             pressure=800)
            self.assertEqual(True, suc)

    def test_Setting_setRefractionParam_not_ok(self):
        setting = Setting()

        response = ['01']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=None,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionParam_not_ok0(self):
        setting = Setting()

        response = ['01']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=5,
                                             pressure=None)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionParam_not_ok1(self):
        setting = Setting()

        response = ['01']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=5,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionParam_not_ok2(self):
        setting = Setting()

        response = ['10']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=5,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionParam_not_ok3(self):
        setting = Setting()

        response = ['11']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 2
            suc = setting.setRefractionParam(temperature=5,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionParam_not_ok4(self):
        setting = Setting()

        response = ['11']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=-45,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionParam_not_ok5(self):
        setting = Setting()

        response = ['11']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=85,
                                             pressure=800)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionParam_not_ok6(self):
        setting = Setting()

        response = ['11']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=5,
                                             pressure=300)
            self.assertEqual(False, suc)

    def test_Setting_setRefractionParam_not_ok7(self):
        setting = Setting()

        response = ['11']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setRefractionParam(temperature=5,
                                             pressure=1500)
            self.assertEqual(False, suc)

    #
    #
    # testing setSlewRate
    #
    #

    def test_Setting_setSlewRate_ok(self):
        setting = Setting()

        response = ['10']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setSlewRate(5)
            self.assertEqual(True, suc)

    def test_Setting_setSlewRate_not_ok(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewRate('E')
            self.assertEqual(False, suc)

    def test_Setting_setSlewRate_not_ok0(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewRate(None)
            self.assertEqual(False, suc)

    def test_Setting_setSlewRate_not_ok1(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewRate(5)
            self.assertEqual(False, suc)

    def test_Setting_setSlewRate_not_ok1a(self):
        setting = Setting()

        response = ['01']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setSlewRate(5)
            self.assertEqual(False, suc)

    def test_Setting_setSlewRate_not_ok1b(self):
        setting = Setting()

        response = ['11']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setSlewRate(5)
            self.assertEqual(False, suc)

    def test_Setting_setSlewRate_not_ok1c(self):
        setting = Setting()

        response = ['00']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            suc = setting.setSlewRate(5)
            self.assertEqual(False, suc)

    def test_Setting_setSlewRate_not_ok2(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setSlewRate(5)
            self.assertEqual(False, suc)

    def test_Setting_setSlewRate_not_ok3(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewRate(0)
            self.assertEqual(False, suc)

    def test_Setting_setSlewRate_not_ok4(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewRate(25)
            self.assertEqual(False, suc)

    def test_setSlewSpeedMax_1(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewSpeedMax()
            self.assertEqual(suc, True)

    def test_setSlewSpeedMax_2(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setSlewSpeedMax()
            self.assertEqual(suc, False)

    def test_setSlewSpeedHigh_1(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewSpeedHigh()
            self.assertEqual(suc, True)

    def test_setSlewSpeedHigh_2(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setSlewSpeedHigh()
            self.assertEqual(suc, False)

    def test_setSlewSpeedMed_1(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewSpeedMed()
            self.assertEqual(suc, True)

    def test_setSlewSpeedMed_2(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setSlewSpeedMed()
            self.assertEqual(suc, False)

    def test_setSlewSpeedLow_1(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSlewSpeedLow()
            self.assertEqual(suc, True)

    def test_setSlewSpeedLow_2(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setSlewSpeedLow()
            self.assertEqual(suc, False)

    #
    #
    # testing setUnattendedFlip
    #
    #

    def test_ObsSite_setUnattendedFlip_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setUnattendedFlip(1)
            self.assertEqual(True, suc)

    def test_ObsSite_setUnattendedFlip_not_ok1(self):
        setting = Setting()

        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = setting.setUnattendedFlip(1)
            self.assertEqual(False, suc)

    #
    #
    # testing setUnattendedFlip
    #
    #

    def test_setDirectWeatherUpdateType_1(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setDirectWeatherUpdateType(0)
            self.assertEqual(suc, False)

    def test_setDirectWeatherUpdateType_2(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setDirectWeatherUpdateType(0)
            self.assertEqual(suc, False)

    def test_setDirectWeatherUpdateType_3(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setDirectWeatherUpdateType(0)
            self.assertEqual(suc, True)

    def test_setDirectWeatherUpdateType_4(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setDirectWeatherUpdateType(-1)
            self.assertEqual(suc, False)

    def test_setDirectWeatherUpdateType_5(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setDirectWeatherUpdateType(5)
            self.assertEqual(suc, False)

    #
    #
    # testing setLunarTracking
    #
    #

    def test_ObsSite_setLunarTracking_ok(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = setting.setLunarTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_setLunarTracking_not_ok1(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = setting.setLunarTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing setSiderealTracking
    #
    #

    def test_ObsSite_setSiderealTracking_ok(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = setting.setSiderealTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_setSiderealTracking_not_ok1(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = setting.setSiderealTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing setSolarTracking
    #
    #

    def test_ObsSite_setSolarTracking_ok(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = setting.setSolarTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_setSolarTracking_not_ok1(self):
        setting = Setting()
        response = []
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = setting.setSolarTracking()
            self.assertEqual(False, suc)

    def test_Checking_trackingRate1(self):
        setting = Setting()
        setting.trackingRate = '62.4'
        self.assertEqual(True, setting.checkRateLunar())
        self.assertEqual(False, setting.checkRateSidereal())
        self.assertEqual(False, setting.checkRateSolar())

    def test_Checking_trackingRate2(self):
        setting = Setting()
        setting.trackingRate = '60.2'
        self.assertEqual(False, setting.checkRateLunar())
        self.assertEqual(True, setting.checkRateSidereal())
        self.assertEqual(False, setting.checkRateSolar())

    def test_Checking_trackingRate3(self):
        setting = Setting()
        setting.trackingRate = '60.3'
        self.assertEqual(False, setting.checkRateLunar())
        self.assertEqual(False, setting.checkRateSidereal())
        self.assertEqual(True, setting.checkRateSolar())

    def test_Checking_trackingRate4(self):
        setting = Setting()
        setting.trackingRate = '6'
        self.assertEqual(False, setting.checkRateLunar())
        self.assertEqual(False, setting.checkRateSidereal())
        self.assertEqual(False, setting.checkRateSolar())

    def test_ObsSite_trackingRate(self):
        setting = Setting()
        setting.trackingRate = '67'
        self.assertEqual(67, setting.trackingRate)

    def test_setWebInterface_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setWebInterface(True)
            self.assertEqual(True, suc)

    def test_setWebInterface_not_ok1(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setWebInterface(True)
            self.assertEqual(False, suc)

    def test_setWebInterface_not_ok2(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setWebInterface(True)
            self.assertEqual(False, suc)

    def test_setSettleTime_ok(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSettleTime(5)
            self.assertEqual(True, suc)

    def test_setSettleTime_not_ok1(self):
        setting = Setting()

        response = ['1']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = setting.setSettleTime(5)
            self.assertEqual(False, suc)

    def test_setSettleTime_not_ok2(self):
        setting = Setting()

        response = ['0']
        with mock.patch('mountcontrol.setting.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = setting.setSettleTime(5)
            self.assertEqual(False, suc)
