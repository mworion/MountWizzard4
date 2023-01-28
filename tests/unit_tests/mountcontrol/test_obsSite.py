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
import os
import platform

# external packages
from skyfield.api import Angle, Timescale, wgs84, Star, Loader

# local imports
import mountcontrol
from mountcontrol.obsSite import ObsSite
from base.loggerMW import setupLogging
setupLogging()


class TestConfigData(unittest.TestCase):

    def setUp(self):
        global pathToData
        pathToData = os.getcwd() + '/data'

    #
    #
    # testing the timescale reference
    #
    #

    def test_setLoaderAndTimescale_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        suc = obsSite.setLoaderAndTimescale()
        assert suc

    def test_setLoaderAndTimescale_2(self):
        obsSite = ObsSite()
        suc = obsSite.setLoaderAndTimescale()
        assert suc

    def test_setLoaderAndTimescale_3(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=True):
            with mock.patch.object(Loader,
                                   'timescale'):
                with mock.patch.object(Loader.timescale,
                                       'now'):
                    suc = obsSite.setLoaderAndTimescale()
                    assert suc

    def test_Data_without_ts(self):
        obsSite = ObsSite(pathToData='tests/workDir/data')
        self.assertEqual(isinstance(obsSite.ts, Timescale), True)

    def test_Data_with_ts(self):
        obsSite = ObsSite(pathToData=None)
        self.assertEqual(isinstance(obsSite.ts, Timescale), True)

    def test_Site_location_1(self):
        obsSite = ObsSite(pathToData=pathToData)

        elev = '999.9'
        lon = '+160*30:45.5'
        lat = '+45*30:45.5'
        obsSite.location = lat, lon, elev
        self.assertAlmostEqual(160, obsSite.location.longitude.dms()[0], 6)
        self.assertAlmostEqual(30, obsSite.location.longitude.dms()[1], 6)
        self.assertAlmostEqual(45.5, obsSite.location.longitude.dms()[2], 6)
        self.assertAlmostEqual(45, obsSite.location.latitude.dms()[0], 6)
        self.assertAlmostEqual(30, obsSite.location.latitude.dms()[1], 6)
        self.assertAlmostEqual(45.5, obsSite.location.latitude.dms()[2], 6)
        self.assertAlmostEqual(999.9, obsSite.location.elevation.m, 6)

    def test_Site_location_2(self):
        obsSite = ObsSite(pathToData=pathToData)

        elev = '999.9'
        lon = '+160*30:45.5'
        lat = '+45*30:45.5'
        obsSite.location = (lat, lon, elev)
        self.assertAlmostEqual(160, obsSite.location.longitude.dms()[0], 6)
        self.assertAlmostEqual(30, obsSite.location.longitude.dms()[1], 6)
        self.assertAlmostEqual(45.5, obsSite.location.longitude.dms()[2], 6)
        self.assertAlmostEqual(45, obsSite.location.latitude.dms()[0], 6)
        self.assertAlmostEqual(30, obsSite.location.latitude.dms()[1], 6)
        self.assertAlmostEqual(45.5, obsSite.location.latitude.dms()[2], 6)
        self.assertAlmostEqual(999.9, obsSite.location.elevation.m, 6)

    def test_Site_location_3(self):
        obsSite = ObsSite(pathToData=pathToData)

        elev = 100
        lon = 100
        lat = 45
        obsSite.location = wgs84.latlon(longitude_degrees=lon,
                                        latitude_degrees=lat,
                                        elevation_m=elev)
        self.assertAlmostEqual(100, obsSite.location.longitude.dms()[0], 6)
        self.assertAlmostEqual(0, obsSite.location.longitude.dms()[1], 6)
        self.assertAlmostEqual(0, obsSite.location.longitude.dms()[2], 6)
        self.assertAlmostEqual(45, obsSite.location.latitude.dms()[0], 6)
        self.assertAlmostEqual(0, obsSite.location.latitude.dms()[1], 6)
        self.assertAlmostEqual(0, obsSite.location.latitude.dms()[2], 6)
        self.assertAlmostEqual(100, obsSite.location.elevation.m, 6)

    def test_Site_location_4(self):
        obsSite = ObsSite(pathToData=pathToData)

        lon = '+160*30:45.5'
        lat = '+45*30:45.5'
        obsSite.location = (lat, lon)
        self.assertEqual(None, obsSite.location)
        self.assertEqual(None, obsSite._location)

    def test_Site_location_5(self):
        obsSite = ObsSite(pathToData=pathToData)

        lat = '+45*30:45.5'
        obsSite.location = lat
        self.assertEqual(None, obsSite.location)

    def test_Site_timeJD_1(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.ut1_utc = '0'
        obsSite.timeJD = '2458240.12345678'
        self.assertEqual(2458240.123457949, obsSite.timeJD.ut1)
        obsSite.timeJD = 2458240.12345678
        self.assertEqual(2458240.123457949, obsSite.timeJD.ut1)
        obsSite.timeJD = '2458240.a23e5678'
        self.assertAlmostEqual(obsSite.ts.now(), obsSite.timeJD, 4)
        self.assertEqual(None, obsSite._timeJD)

    def test_Site_timeJD_2(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.timeJD = obsSite.ts.now().tt - 69.184 / 86400
        self.assertAlmostEqual(obsSite.ts.now().tt, obsSite.timeJD.tt, 4)

    def test_timeDiff(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite._timeDiff = [10, 10, 10, 10, 10]
        obsSite.timeDiff = 20
        assert obsSite.timeDiff == 10

    def test_Site_ut1_utc(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.ut1_utc = '123.11'
        self.assertEqual(123.11 / 86400, obsSite.ut1_utc)

    def test_Site_utc_ut2(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.ut1_utc = None
        assert obsSite.ut1_utc is None

    def test_Site_timeSidereal_1(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.timeSidereal = '12:30:00.00'
        self.assertEqual(obsSite.timeSidereal.hours, 12.5)
        obsSite.timeSidereal = '12:aa:30.01'
        self.assertEqual(None, obsSite.timeSidereal)
        obsSite.timeSidereal = ['12:aa:30.01']
        self.assertEqual(None, obsSite.timeSidereal)
        self.assertEqual(None, obsSite._timeSidereal)
        obsSite.timeSidereal = 12.0
        self.assertEqual(obsSite.timeSidereal.hours, 12)
        obsSite.timeSidereal = Angle(hours=12.0)
        self.assertEqual(obsSite.timeSidereal.hours, 12)

    def test_Site_ra(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.raJNow = Angle(hours=34)
        self.assertEqual(34, obsSite.raJNow.hours)
        obsSite.raJNow = 34
        self.assertEqual(34, obsSite.raJNow.hours)
        self.assertEqual(34, obsSite._raJNow.hours)
        obsSite.raJNow = '34'
        self.assertEqual(34, obsSite.raJNow.hours)
        obsSite.raJNow = '34f'
        self.assertEqual(None, obsSite.raJNow)

    def test_Site_dec(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.decJNow = Angle(degrees=34)
        self.assertEqual(34, obsSite.decJNow.degrees)
        obsSite.decJNow = 34
        self.assertEqual(34, obsSite.decJNow.degrees)
        self.assertEqual(34, obsSite._decJNow.degrees)
        obsSite.decJNow = '34'
        self.assertEqual(34, obsSite.decJNow.degrees)
        obsSite.decJNow = '34f'
        self.assertEqual(None, obsSite.decJNow)

    def test_Site_alt(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.Alt = Angle(degrees=34)
        self.assertEqual(34, obsSite.Alt.degrees)
        obsSite.Alt = 34
        self.assertEqual(34, obsSite.Alt.degrees)
        self.assertEqual(34, obsSite._Alt.degrees)
        obsSite.Alt = '34'
        self.assertEqual(34, obsSite.Alt.degrees)
        obsSite.Alt = '34f'
        self.assertEqual(None, obsSite.Alt)

    def test_Site_az(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.Az = Angle(degrees=34)
        self.assertEqual(34, obsSite.Az.degrees)
        obsSite.Az = 34
        self.assertEqual(34, obsSite.Az.degrees)
        self.assertEqual(34, obsSite._Az.degrees)
        obsSite.Az = '34'
        self.assertEqual(34, obsSite.Az.degrees)
        obsSite.Az = '34f'
        self.assertEqual(None, obsSite.Az)

    def test_Site_pierside(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.pierside = 'E'
        self.assertEqual(obsSite.pierside, 'E')
        obsSite.pierside = 'e'
        self.assertEqual(obsSite.pierside, 'E')
        obsSite.pierside = 'w'
        self.assertEqual(obsSite.pierside, 'W')
        self.assertEqual(obsSite._pierside, 'W')
        obsSite.pierside = 'W'
        self.assertEqual(obsSite.pierside, 'W')
        obsSite.pierside = 'WW'
        self.assertEqual(obsSite.pierside, None)
        obsSite.pierside = '12'
        self.assertEqual(obsSite.pierside, None)
        obsSite.pierside = 17
        self.assertEqual(obsSite.pierside, None)

    def test_Site_raTarget(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.raJNowTarget = '*34:00:00.00'
        self.assertEqual(34, obsSite.raJNowTarget.hours)
        obsSite.raJNowTarget = 34
        self.assertEqual(None, obsSite.raJNowTarget)
        self.assertEqual(None, obsSite._raJNowTarget)
        obsSite.raJNowTarget = '34'
        self.assertEqual(None, obsSite.raJNowTarget)
        obsSite.raJNowTarget = '34f'
        self.assertEqual(None, obsSite.raJNowTarget)
        obsSite.raJNowTarget = Angle(hours=12)
        self.assertEqual(obsSite.raJNowTarget.hours, 12)

    def test_Site_haJNow_1(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.timeSidereal = 12
        obsSite.raJNow = Angle(hours=12)
        obsSite.haJNow is None

    def test_Site_haJNow_2(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.timeSidereal = Angle(hours=12)
        obsSite.raJNow = Angle(hours=12)
        obsSite.haJNow.hours == 0

    def test_Site_haJNowTarget_1(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.timeSidereal = 12
        obsSite.raJNowTarget = Angle(hours=12)
        obsSite.haJNowTarget is None

    def test_Site_haJNowTarget_2(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.timeSidereal = Angle(hours=12)
        obsSite.raJNowTarget = Angle(hours=12)
        obsSite.haJNowTarget.hours == 0

    def test_Site_decTarget(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.decJNowTarget = '*34:00:00.00'
        self.assertEqual(34, obsSite.decJNowTarget.degrees)
        obsSite.decJNowTarget = 34
        self.assertEqual(None, obsSite.decJNowTarget)
        self.assertEqual(None, obsSite._decJNowTarget)
        obsSite.decJNowTarget = '34'
        self.assertEqual(None, obsSite.decJNowTarget)
        obsSite.decJNowTarget = '34f'
        self.assertEqual(None, obsSite.decJNowTarget)
        obsSite.decJNowTarget = Angle(degrees=34)
        self.assertEqual(obsSite.decJNowTarget.degrees, 34)

    def test_Site_altTarget(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.AltTarget = '*34:00:00.00'
        self.assertEqual(34, obsSite.AltTarget.degrees)
        obsSite.AltTarget = 34
        self.assertEqual(None, obsSite.AltTarget)
        obsSite.AltTarget = Angle(degrees=34)
        self.assertEqual(obsSite.AltTarget.degrees, 34)
        self.assertEqual(obsSite._AltTarget.degrees, 34)
        obsSite.AltTarget = '34'
        self.assertEqual(None, obsSite.AltTarget)
        obsSite.AltTarget = '34f'
        self.assertEqual(None, obsSite.AltTarget)

    def test_Site_azTarget(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.AzTarget = '*34:00:00.00'
        self.assertEqual(34, obsSite.AzTarget.degrees)
        obsSite.AzTarget = 34
        self.assertEqual(None, obsSite.AzTarget)
        obsSite.AzTarget = Angle(degrees=34)
        self.assertEqual(obsSite.AzTarget.degrees, 34)
        self.assertEqual(obsSite._AzTarget.degrees, 34)
        obsSite.AzTarget = '34'
        self.assertEqual(None, obsSite.AzTarget)
        obsSite.AzTarget = '34f'
        self.assertEqual(None, obsSite.AzTarget)

    def test_angularPosRA_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.angularPosRA = 12
        assert obsSite.angularPosRA.degrees == 12

    def test_angularPosRA_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.angularPosRA = Angle(degrees=12)
        assert obsSite.angularPosRA.degrees == 12

    def test_angularPosDEC_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.angularPosDEC = 12
        assert obsSite.angularPosDEC.degrees == 12

    def test_angularPosDEC_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.angularPosDEC = Angle(degrees=12)
        assert obsSite.angularPosDEC.degrees == 12

    def test_errorAngularPosRA_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.errorAngularPosRA = 12
        assert obsSite.errorAngularPosRA.degrees == 12

    def test_errorAngularPosRA_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.errorAngularPosRA = Angle(degrees=12)
        assert obsSite.errorAngularPosRA.degrees == 12

    def test_errorAngularPosDEC_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.errorAngularPosDEC = 12
        assert obsSite.errorAngularPosDEC.degrees == 12

    def test_errorAngularPosDEC_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.errorAngularPosDEC = Angle(degrees=12)
        assert obsSite.errorAngularPosDEC.degrees == 12

    def test_angularPosRATarget_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.angularPosRATarget = 12
        assert obsSite.angularPosRATarget.degrees == 12

    def test_angularPosRATarget_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.angularPosRATarget = Angle(degrees=12)
        assert obsSite.angularPosRATarget.degrees == 12

    def test_angularPosDECTarget_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.angularPosDECTarget = 12
        assert obsSite.angularPosDECTarget.degrees == 12

    def test_angularPosDECTarget_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.angularPosDECTarget = Angle(degrees=12)
        assert obsSite.angularPosDECTarget.degrees == 12

    def test_Site_piersideTarget(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.piersideTarget = '2'
        self.assertEqual(obsSite.piersideTarget, 'W')
        obsSite.piersideTarget = '3'
        self.assertEqual(obsSite.piersideTarget, 'E')
        obsSite.piersideTarget = '3'
        self.assertEqual(obsSite.piersideTarget, 'E')
        self.assertEqual(obsSite._piersideTarget, 'E')
        obsSite.piersideTarget = '3'
        self.assertEqual(obsSite.piersideTarget, 'E')
        obsSite.piersideTarget = 'WW'
        self.assertEqual(obsSite.piersideTarget, None)
        obsSite.piersideTarget = '12'
        self.assertEqual(obsSite.piersideTarget, None)
        obsSite.piersideTarget = 0
        self.assertEqual(obsSite.piersideTarget, None)

    def test_Site_status(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.status = '1'
        self.assertEqual(1, obsSite.status)
        obsSite.status = 1
        self.assertEqual(1, obsSite.status)
        self.assertEqual(1, obsSite._status)
        obsSite.status = '1d'
        self.assertEqual(None, obsSite.status)
        obsSite.status = '1d'
        self.assertEqual(None, obsSite.status)
        obsSite.status = '0'
        self.assertEqual(0, obsSite.status)
        obsSite.status = '100'
        self.assertEqual(None, obsSite.status)

    def test_status_1(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.status = None
        self.assertEqual(None, obsSite.status)

    def test_status_2(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.status = 'E'
        self.assertEqual(None, obsSite.status)

    def test_status_3(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.status = '5'
        self.assertEqual(5, obsSite.status)

    def test_statusSat_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.statusSat = 1
        self.assertEqual(obsSite.statusSat, None)

    def test_statusSat_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        obsSite.statusSat = 'V'
        self.assertEqual(obsSite.statusSat, 'V')

    def test_Site_statusText_1(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.status = None
        self.assertEqual(None, obsSite.statusText())

    def test_Site_statusText_2(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.status = '1'
        self.assertEqual('Stopped after STOP', obsSite.statusText())

    def test_Site_statusSlew(self):
        obsSite = ObsSite(pathToData=pathToData)

        obsSite.statusSlew = '1'
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = 1
        self.assertEqual(True, obsSite.statusSlew)
        self.assertEqual(True, obsSite._statusSlew)
        obsSite.statusSlew = True
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = False
        self.assertEqual(False, obsSite.statusSlew)
        obsSite.statusSlew = 'True'
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = '100'
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = '-100'
        self.assertEqual(True, obsSite.statusSlew)
        obsSite.statusSlew = ''
        self.assertEqual(False, obsSite.statusSlew)
        obsSite.statusSlew = (0, 0)
        self.assertEqual(True, obsSite.statusSlew)

    def test_ObsSite_parseLocation_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['+0585.2', '-011:35:00.0', '+48:07:00.0', '03']
        suc = obsSite.parseLocation(response, 4)
        self.assertEqual(True, suc)

    def test_ObsSite_parseLocation_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['+0585.2', '+011:35:00.0', '+48:07:00.0', '03']
        suc = obsSite.parseLocation(response, 4)
        self.assertEqual(True, suc)

    def test_ObsSite_parseLocation_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        suc = obsSite.parseLocation(response, 4)
        self.assertEqual(False, suc)

    def test_ObsSite_parseLocation_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['+master', '-011:35:00.0', '+48:07:00.0', '03']

        suc = obsSite.parseLocation(response, 4)
        self.assertEqual(True, suc)

    def test_ObsSite_parseLocation_not_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['+0585.2', '-011:35:00.0', '+48:sdj.0', '03']

        suc = obsSite.parseLocation(response, 4)
        self.assertEqual(True, suc)

    def test_ObsSite_parseLocation_not_ok4(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['+0585.2', '-011:EE:00.0', '+48:07:00.0', '03']

        suc = obsSite.parseLocation(response, 4)
        self.assertEqual(True, suc)

    def test_ObsSite_poll_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['+0585.2', '-011:35:00.0', '+48:07:00.0', '03']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 4
            suc = obsSite.getLocation()
            self.assertEqual(True, suc)

    def test_ObsSite_poll_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['+0585.2', '-011:35:00.0', '+48:07:00.0', '03']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 4
            suc = obsSite.getLocation()
            self.assertEqual(False, suc)

    def test_ObsSite_poll_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['+0585.2', '-011:35:00.0', '+48:07:00.0', '03']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 6
            suc = obsSite.getLocation()
            self.assertEqual(False, suc)

    #
    #
    # testing pollSetting pointing
    #
    #

    def test_ObsSite_parsePointing_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['13:15:35.68', '0.12', 'V',
                    '19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0',
                    '2458352.10403639, 100, 100, 0.1, 0.1']
        suc = obsSite.parsePointing(response, 5)
        self.assertEqual(True, suc)

    def test_ObsSite_parsePointing_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['13:15:35.68', '0.12', 'V',
                    '19.44591,+88.0032,W,000.0000,+47.9945,2458352.10403639,5,0',
                    '2458352.10403639, 100, 100, 0.1, 0.1']
        suc = obsSite.parsePointing(response, 5)
        self.assertEqual(True, suc)
        self.assertEqual(type(obsSite.Az), Angle)

    def test_ObsSite_parsePointing_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['13:15:35.68', '0.12', 'V',
                    '19.44591,+88.0032,W,000.0001,+00.0000,2458352.10403639,5,0',
                    '2458352.10403639, 100, 100, 0.1, 0.1']
        suc = obsSite.parsePointing(response, 5)
        self.assertEqual(True, suc)
        self.assertEqual(type(obsSite.Alt), Angle)

    def test_ObsSite_pollPointing_ok4(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['13:15:35.68', '0.12', 'V',
                    '19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0',
                    '2458352.10403639, 100, 100, 0.1, 0.1']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 5
            suc = obsSite.pollPointing()
            self.assertEqual(True, suc)

    def test_ObsSite_pollPointing_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['13:15:35.68', '0.12',
                    '19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0',
                    '2458352.10403639, 100, 100, 0.1, 0.1']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 3
            suc = obsSite.pollPointing()
            self.assertEqual(False, suc)

    def test_ObsSite_pollPointing_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['13:15:35.68', '0.12',
                    '19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0',
                    '2458352.10403639, 100, 100, 0.1, 0.1']

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 5
            suc = obsSite.pollPointing()
            self.assertEqual(False, suc)

    def test_pollSyncClock_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(platform,
                               'system',
                               return_value='Windows'):
            with mock.patch.object(mountcontrol.obsSite.Connection,
                                   'communicate',
                                   return_value=(False, [], 0)):
                suc = obsSite.pollSyncClock()
                assert not suc

    def test_pollSyncClock_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(platform,
                               'system',
                               return_value='Linux'):
            with mock.patch.object(mountcontrol.obsSite.Connection,
                                   'communicate',
                                   return_value=(False, [], 0)):
                suc = obsSite.pollSyncClock()
                assert not suc

    def test_pollSyncClock_3(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(platform,
                               'system',
                               return_value='aarch64'):
            with mock.patch.object(mountcontrol.obsSite.Connection,
                                   'communicate',
                                   return_value=(False, [], 0)):
                suc = obsSite.pollSyncClock()
                assert not suc

    def test_pollSyncClock_4(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(platform,
                               'system',
                               return_value='Darwin'):
            with mock.patch.object(mountcontrol.obsSite.Connection,
                                   'communicate',
                                   return_value=(True, ['eee'], 1)):
                suc = obsSite.pollSyncClock()
                assert not suc

    def test_pollSyncClock_5(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(platform,
                               'system',
                               return_value='Darwin'):
            with mock.patch.object(mountcontrol.obsSite.Connection,
                                   'communicate',
                                   return_value=(True, ['12345678.1'], 1)):
                suc = obsSite.pollSyncClock()
                assert suc

    def test_adjustClock_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(False, ['0'], 1)):
            suc = obsSite.adjustClock(0)
            assert not suc

    def test_adjustClock_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, ['0'], 1)):
            suc = obsSite.adjustClock(0)
            assert not suc

    def test_adjustClock_3(self):
        obsSite = ObsSite(pathToData=pathToData)
        with mock.patch.object(mountcontrol.obsSite.Connection,
                               'communicate',
                               return_value=(True, ['1'], 1)):
            suc = obsSite.adjustClock(0)
            assert suc

    def test_startSlewing_1(self):
        obsSite = ObsSite(pathToData=pathToData)

        suc = obsSite.startSlewing(slewType='')
        self.assertEqual(suc, False)

    def test_startSlewing_1_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = '1#'

        obsSite.status = 0
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.startSlewing(slewType='keep')
            self.assertEqual(suc, False)

    def test_startSlewing_1_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = '1#'

        obsSite.status = 1
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.startSlewing(slewType='keep')
            self.assertEqual(suc, False)

    def test_startSlewing_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = '1#'

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.startSlewing(slewType='normal')
            self.assertEqual(suc, False)

    def test_startSlewing_3(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = '1#'

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 3
            suc = obsSite.startSlewing(slewType='normal')
            self.assertEqual(suc, False)

    def test_startSlewing_4(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = '0#'

        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.startSlewing(slewType='normal')
            self.assertEqual(suc, True)

    def test_ObsSite_setTargetAltAz_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['112+45:00:00.0', '180:00:00.0', '12:30:00.00', '+45:30:00.0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 7
            alt = Angle(degrees=30)
            az = Angle(degrees=30)
            suc = obsSite.setTargetAltAz(alt, az)
            self.assertEqual(True, suc)

    def test_ObsSite_setTargetAltAz_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        suc = obsSite.setTargetAltAz(alt_degrees=0, az_degrees=0)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAltAz_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        alt = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az_degrees=0)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAltAz_not_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAltAz_not_ok4(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['00']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = Angle(degrees=30)
            az = Angle(degrees=30)
            suc = obsSite.setTargetAltAz(alt, az)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAltAz_not_ok5(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = Angle(degrees=30)
            az = Angle(degrees=30)
            suc = obsSite.setTargetAltAz(alt, az)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAltAz_not_ok6(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1#2']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = Angle(degrees=30)
            az = Angle(degrees=30)
            suc = obsSite.setTargetAltAz(alt, az)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAltAz_not_ok7(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1#2']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            alt = Angle(degrees=30)
            az = Angle(degrees=30)
            suc = obsSite.setTargetAltAz(alt, az)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAltAz_not_ok8(self):
        obsSite = ObsSite(pathToData=pathToData)
        alt = Angle(hours=5, preference='hours')
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAltAz_not_ok9(self):
        obsSite = ObsSite(pathToData=pathToData)
        alt = Angle(degrees=30)
        az = Angle(hours=5, preference='hours')
        suc = obsSite.setTargetAltAz(alt, az)
        self.assertEqual(False, suc)

    #
    #
    # testing setTargetRaDec
    #
    #

    def test_ObsSite_setTargetRaDec_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['112+45:00:00.0', '180:00:00.0', '12:30:00.00', '+45:30:00.0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetRaDec(ra, dec)
            self.assertEqual(True, suc)

    def test_ObsSite_setTargetRaDec_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['112+45:00:00.0', '180:00:00.0', '12:30:00.00', '+45:30:00.0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            target = Star(ra=ra, dec=dec)
            suc = obsSite.setTargetRaDec(target=target)
            self.assertEqual(True, suc)

    def test_ObsSite_setTargetRaDec_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        suc = obsSite.setTargetRaDec(ra_hours=0, dec_degrees=0)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        suc = obsSite.setTargetRaDec(ra_hours=0, dec_degrees=0)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)
        ra = None
        dec = None
        target = None
        suc = obsSite.setTargetRaDec(ra, dec, target)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok4(self):
        obsSite = ObsSite(pathToData=pathToData)
        ra = Angle(hours=30, preference='hours')
        dec = None
        suc = obsSite.setTargetRaDec(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok5(self):
        obsSite = ObsSite(pathToData=pathToData)

        ra = Angle(hours=30, preference='hours')
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok6(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['00']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetRaDec(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok7(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetRaDec(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok8(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1#']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetRaDec(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok9(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1#']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetRaDec(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok10(self):
        obsSite = ObsSite(pathToData=pathToData)
        ra = Angle(degrees=30)
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetRaDec_not_ok11(self):
        obsSite = ObsSite(pathToData=pathToData)
        ra = Angle(degrees=30)
        dec = Angle(hours=5, preference='hours')
        suc = obsSite.setTargetRaDec(ra, dec)
        self.assertEqual(False, suc)

    #
    #
    # testing setTargetAngular
    #
    #

    def test_ObsSite_setTargetAngular_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['112+45:00:00.0', '180:00:00.0', '12:30:00.00', '+45:30:00.0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='degrees')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetAngular(ra, dec)
            self.assertEqual(True, suc)

    def test_ObsSite_setTargetAngular_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['112+45:00:00.0', '180:00:00.0', '12:30:00.00', '+45:30:00.0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='degrees')
            dec = Angle(degrees=30)
            target = Star(ra=ra, dec=dec)
            suc = obsSite.setTargetAngular(target=target)
            self.assertEqual(True, suc)

    def test_ObsSite_setTargetAngular_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        suc = obsSite.setTargetAngular(ra_degrees=0, dec_degrees=0)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        ra = None
        dec = None
        suc = obsSite.setTargetAngular(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)
        ra = None
        dec = None
        target = None
        suc = obsSite.setTargetAngular(ra, dec, target)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok4(self):
        obsSite = ObsSite(pathToData=pathToData)
        ra = Angle(hours=30, preference='hours')
        dec = None
        suc = obsSite.setTargetAngular(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok5(self):
        obsSite = ObsSite(pathToData=pathToData)

        ra = Angle(hours=30, preference='hours')
        dec = Angle(degrees=30)
        suc = obsSite.setTargetAngular(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok6(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['00']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetAngular(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok7(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 2
            ra = Angle(degrees=5)
            dec = Angle(degrees=30)
            suc = obsSite.setTargetAngular(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok8(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1#']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetAngular(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok9(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1#']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='hours')
            dec = Angle(degrees=30)
            suc = obsSite.setTargetAngular(ra, dec)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok10(self):
        obsSite = ObsSite(pathToData=pathToData)
        ra = Angle(degrees=30)
        dec = Angle(hours=5, preference='hours')
        suc = obsSite.setTargetAngular(ra, dec)
        self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok_11(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['002+45:00:00.0', '180:00:00.0', '12:30:00.00', '+45:30:00.0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(hours=5, preference='degrees')
            dec = Angle(degrees=30)
            target = Star(ra=ra, dec=dec)
            suc = obsSite.setTargetAngular(target=target)
            self.assertEqual(False, suc)

    def test_ObsSite_setTargetAngular_not_ok_12(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['112+45:00:00.0', '180:00:00.0', '12:30:00.00']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2
            ra = Angle(degrees=5)
            dec = Angle(degrees=30)
            target = Star(ra=ra, dec=dec)
            suc = obsSite.setTargetAngular(target=target)
            self.assertEqual(False, suc)

    #
    #
    # testing shutdown
    #
    #

    def test_ObsSite_shutdown_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.shutdown()
            self.assertEqual(True, suc)

    def test_ObsSite_shutdown_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.shutdown()
            self.assertEqual(False, suc)

    def test_ObsSite_shutdown_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.shutdown()
            self.assertEqual(False, suc)

    #
    #
    # testing setSite
    #
    #

    def test_ObsSite_setLocation_ok(self):
        obsSite = ObsSite(pathToData=pathToData)
        observer = wgs84.latlon(latitude_degrees=50,
                                longitude_degrees=11,
                                elevation_m=580)
        response = ['111']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLocation(observer)
            self.assertEqual(True, suc)

    def test_ObsSite_setLocation_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        observer = wgs84.latlon(latitude_degrees=50,
                                longitude_degrees=11,
                                elevation_m=580)
        response = ['101']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLocation(observer)
            self.assertEqual(False, suc)

    def test_ObsSite_setLocation_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        observer = wgs84.latlon(latitude_degrees=50,
                                longitude_degrees=11,
                                elevation_m=580)
        response = ['111']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setLocation(observer)
            self.assertEqual(False, suc)

    def test_ObsSite_setLocation_not_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['111']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setLocation(1234)
            self.assertEqual(False, suc)

    def test_ObsSite_setLatitude_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLatitude(lat_degrees=50)
            self.assertEqual(True, suc)

    def test_ObsSite_setLatitude_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLatitude(lat=Angle(degrees=50))
            self.assertEqual(True, suc)

    def test_ObsSite_setLatitude_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLatitude(lat='12 50 00.0')
            self.assertEqual(True, suc)

    def test_ObsSite_setLatitude_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLatitude(lat_degrees='50')
            self.assertEqual(False, suc)

    def test_ObsSite_setLatitude_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setLatitude(lat_degrees=50)
            self.assertEqual(False, suc)

    def test_ObsSite_setLatitude_not_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLatitude(lat_degrees=50)
            self.assertEqual(False, suc)

    def test_ObsSite_setLongitude_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLongitude(lon_degrees=50)
            self.assertEqual(True, suc)

    def test_ObsSite_setLongitude_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLongitude(lon=Angle(degrees=50))
            self.assertEqual(True, suc)

    def test_ObsSite_setLongitude_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLongitude(lon='12 50 50.00')
            self.assertEqual(True, suc)

    def test_ObsSite_setLongitude_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLongitude(lon_degrees='50')
            self.assertEqual(False, suc)

    def test_ObsSite_setLongitude_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setLongitude(lon_degrees=50)
            self.assertEqual(False, suc)

    def test_ObsSite_setLongitude_not_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setLongitude(lon_degrees=50)
            self.assertEqual(False, suc)

    def test_ObsSite_setElevation_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setElevation('500')
            self.assertEqual(True, suc)

    def test_ObsSite_setElevation_not_ok0(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setElevation(['test'])
            self.assertEqual(False, suc)

    def test_ObsSite_setElevation_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setElevation('er')
            self.assertEqual(False, suc)

    def test_ObsSite_setElevation_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.setElevation('500')
            self.assertEqual(False, suc)

    def test_ObsSite_setElevation_not_ok3(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.setElevation('500')
            self.assertEqual(False, suc)

    #
    #
    # testing startTracking
    #
    #

    def test_ObsSite_startTracking_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.startTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_startTracking_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.startTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing stopTracking
    #
    #

    def test_ObsSite_stopTracking_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stopTracking()
            self.assertEqual(True, suc)

    def test_ObsSite_stopTracking_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stopTracking()
            self.assertEqual(False, suc)

    #
    #
    # testing park
    #
    #

    def test_ObsSite_park_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.park()
            self.assertEqual(True, suc)

    def test_ObsSite_park_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.park()
            self.assertEqual(False, suc)

    #
    #
    # testing unpark
    #
    #

    def test_ObsSite_unpark_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.unpark()
            self.assertEqual(True, suc)

    def test_ObsSite_unpark_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.unpark()
            self.assertEqual(False, suc)

    #
    #
    # testing parkOnActualPosition
    #
    #

    def test_ObsSite_parkOnActualPosition_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.parkOnActualPosition()
            self.assertEqual(True, suc)

    def test_ObsSite_parkOnActualPosition_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.parkOnActualPosition()
            self.assertEqual(False, suc)

    def test_ObsSite_parkOnActualPosition_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.parkOnActualPosition()
            self.assertEqual(False, suc)

    #
    #
    # testing stop
    #
    #

    def test_ObsSite_stop_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stop()
            self.assertEqual(True, suc)

    def test_ObsSite_stop_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stop()
            self.assertEqual(False, suc)

    #
    #
    # testing flip
    #
    #

    def test_ObsSite_flip_ok(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.flip()
            self.assertEqual(True, suc)

    def test_ObsSite_flip_not_ok1(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['0']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = obsSite.flip()
            self.assertEqual(False, suc)

    def test_ObsSite_flip_not_ok2(self):
        obsSite = ObsSite(pathToData=pathToData)

        response = ['1']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = obsSite.flip()
            self.assertEqual(False, suc)

    def test_moveNorth_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.moveNorth()
            self.assertEqual(suc, False)

    def test_moveNorth_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.moveNorth()
            self.assertEqual(suc, True)

    def test_moveEast_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.moveEast()
            self.assertEqual(suc, False)

    def test_moveEast_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.moveEast()
            self.assertEqual(suc, True)

    def test_moveSouth_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.moveSouth()
            self.assertEqual(suc, False)

    def test_moveSouth_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.moveSouth()
            self.assertEqual(suc, True)

    def test_moveWest_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.moveWest()
            self.assertEqual(suc, False)

    def test_moveWest_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.moveWest()
            self.assertEqual(suc, True)

    def test_stopMoveNorth_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stopMoveNorth()
            self.assertEqual(suc, False)

    def test_stopMoveNorth_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stopMoveNorth()
            self.assertEqual(suc, True)

    def test_stopMoveEast_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stopMoveEast()
            self.assertEqual(suc, False)

    def test_stopMoveEast_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stopMoveEast()
            self.assertEqual(suc, True)

    def test_stopMoveSouth_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stopMoveSouth()
            self.assertEqual(suc, False)

    def test_stopMoveSouth_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stopMoveSouth()
            self.assertEqual(suc, True)

    def test_stopMoveWest_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stopMoveWest()
            self.assertEqual(suc, False)

    def test_stopMoveWest_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stopMoveWest()
            self.assertEqual(suc, True)

    def test_stopMoveAll_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.stopMoveAll()
            self.assertEqual(suc, False)

    def test_stopMoveAll_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.stopMoveAll()
            self.assertEqual(suc, True)

    def test_syncPositionToTarget_1(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = []
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = obsSite.syncPositionToTarget()
            self.assertEqual(suc, False)

    def test_syncPositionToTarget_2(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.syncPositionToTarget()
            self.assertEqual(suc, False)

    def test_syncPositionToTarget_3(self):
        obsSite = ObsSite(pathToData=pathToData)
        response = ['Coordinates']
        with mock.patch('mountcontrol.obsSite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = obsSite.syncPositionToTarget()
            self.assertEqual(suc, True)
