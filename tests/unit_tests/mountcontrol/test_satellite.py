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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest
import unittest.mock as mock

# external packages
from skyfield.api import Angle

# local imports
from mountcontrol.satellite import Satellite, TLEParams


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    def test_azimuth_1(self):
        tleParams = TLEParams()
        tleParams.azimuth = 10
        assert tleParams.azimuth.degrees == 10

    def test_azimuth_2(self):
        tleParams = TLEParams()
        tleParams.azimuth = Angle(degrees=10)
        assert tleParams.azimuth.degrees == 10

    def test_altitude_1(self):
        tleParams = TLEParams()
        tleParams.altitude = 10
        assert tleParams.altitude.degrees == 10

    def test_altitude_2(self):
        tleParams = TLEParams()
        tleParams.altitude = Angle(degrees=10)
        assert tleParams.altitude.degrees == 10

    def test_ra_1(self):
        tleParams = TLEParams()
        tleParams.ra = 10
        assert tleParams.ra.hours == 10

    def test_ra_2(self):
        tleParams = TLEParams()
        tleParams.ra = Angle(hours=10)
        assert tleParams.ra.hours == 10

    def test_dec_1(self):
        tleParams = TLEParams()
        tleParams.dec = 10
        assert tleParams.dec.degrees == 10

    def test_dec_2(self):
        tleParams = TLEParams()
        tleParams.dec = Angle(degrees=10)
        assert tleParams.dec.degrees == 10

    def test_flip_1(self):
        tleParams = TLEParams()
        tleParams.flip = True
        assert tleParams.flip

    def test_flip_2(self):
        tleParams = TLEParams()
        tleParams.flip = 'F'
        assert tleParams.flip

    def test_jdStart_1(self):
        tleParams = TLEParams()
        tleParams.jdStart = None
        assert tleParams.jdStart is None

    def test_jdStart_2(self):
        tleParams = TLEParams()
        tleParams.jdStart = '100'
        assert tleParams.jdStart == 100

    def test_jdEnd_1(self):
        tleParams = TLEParams()
        tleParams.jdEnd = None
        assert tleParams.jdEnd is None

    def test_jdEnd_2(self):
        tleParams = TLEParams()
        tleParams.jdEnd = '100'
        assert tleParams.jdEnd == 100

    def test_message_1(self):
        tleParams = TLEParams()
        tleParams.message = None
        assert tleParams.message is None

    def test_message_2(self):
        tleParams = TLEParams()
        tleParams.message = 'test'
        assert tleParams.message == 'test'

    def test_l0_1(self):
        tleParams = TLEParams()
        tleParams.l0 = 'test'
        assert tleParams.l0 == 'test'

    def test_l1_1(self):
        tleParams = TLEParams()
        tleParams.l1 = 'test'
        assert tleParams.l1 == 'test'

    def test_l2_1(self):
        tleParams = TLEParams()
        tleParams.l2 = 'test'
        assert tleParams.l2 == 'test'

    def test_name_1(self):
        tleParams = TLEParams()
        tleParams.name = 'test'
        assert tleParams.name == 'test'

    def test_parseGetTLE_1(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'
        cont = '$0A'
        response = [t0 + cont + t1 + cont + t2 + cont]

        suc = sat.parseGetTLE(response, 1)

        self.assertTrue(suc)
        self.assertEqual(sat.tleParams.name, 'NOAA 8 [-]')
        self.assertEqual(sat.tleParams.l0, t0)
        self.assertEqual(sat.tleParams.l1, t1)
        self.assertEqual(sat.tleParams.l2, t2)

    def test_parseGetTLE_2(self):
        sat = Satellite()
        response = ['76129888407$0A']

        suc = sat.parseGetTLE(response, 1)

        self.assertFalse(suc)
        self.assertEqual(sat.tleParams.name, None)
        self.assertEqual(sat.tleParams.l0, None)
        self.assertEqual(sat.tleParams.l1, None)
        self.assertEqual(sat.tleParams.l2, None)

    def test_parseGetTLE_3(self):
        sat = Satellite()
        response = ['76129888407$0A', ['hj']]

        suc = sat.parseGetTLE(response, 1)

        self.assertFalse(suc)
        self.assertEqual(sat.tleParams.name, None)
        self.assertEqual(sat.tleParams.l0, None)
        self.assertEqual(sat.tleParams.l1, None)
        self.assertEqual(sat.tleParams.l2, None)

    def test_getTLE_1(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'
        cont = '$0A'
        response = [t0 + cont + t1 + cont + t2 + cont]

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1

            suc = sat.getTLE()
            self.assertFalse(suc)

    def test_getTLE_2(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'
        cont = '$0A'
        response = [t0 + cont + t1 + cont + t2 + cont]

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1

            suc = sat.getTLE()
            self.assertTrue(suc)

    def test_getTLE_3(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'
        cont = '$0A'
        response = [t0 + cont + t1 + cont + t2 + cont]

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 2

            suc = sat.getTLE()
            self.assertFalse(suc)

    def test_getTLE_4(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'E', 1

            suc = sat.getTLE()
            self.assertFalse(suc)

    def test_getTLE_5(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, ['V', 'V'], 2

            suc = sat.getTLE()
            self.assertFalse(suc)

    def test_setTLE_1(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, 'E', 1

            suc = sat.setTLE()
            self.assertFalse(suc)

    def test_setTLE_2(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'E', 1

            suc = sat.setTLE()
            self.assertFalse(suc)

    def test_setTLE_3(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'V', 1

            suc = sat.setTLE()
            self.assertFalse(suc)

    def test_setTLE_4(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'V', 1

            suc = sat.setTLE(line0=t0,
                             line1=t1,
                             line2=t2)
            self.assertTrue(suc)

    def test_setTLE_5(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407x'

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'V', 1

            suc = sat.setTLE(line0=t0,
                             line1=t1,
                             line2=t2)
            self.assertFalse(suc)

    def test_setTLE_6(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996x'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'V', 1

            suc = sat.setTLE(line0=t0,
                             line1=t1,
                             line2=t2)
            self.assertFalse(suc)

    def test_setTLE_7(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, 'V', 1

            suc = sat.setTLE(line0=t0,
                             line1=t1,
                             line2=t2)
            self.assertFalse(suc)

    def test_setTLE_8(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'E', 1

            suc = sat.setTLE(line0=t0,
                             line1=t1,
                             line2=t2)
            self.assertFalse(suc)

    def test_setTLE_9(self):
        sat = Satellite()
        t0 = 'NOAA 8 [-]              '
        t1 = '1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996'
        t2 = '2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407'

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'V', 2

            suc = sat.setTLE(line0=t0,
                             line1=t1,
                             line2=t2)
            self.assertFalse(suc)

    def test_parseCalcTLE_1(self):
        sat = Satellite()
        response = ''

        suc = sat.parseCalcTLE(response, 1)
        self.assertFalse(suc)

    def test_parseCalcTLE_2(self):
        sat = Satellite()
        response = ''

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_3(self):
        sat = Satellite()
        response = []

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_4(self):
        sat = Satellite()
        response = ['E', 'E', 'E']

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_5(self):
        sat = Satellite()
        s0 = ''
        s1 = ''
        s2 = ''
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_6(self):
        sat = Satellite()
        s0 = '+23.12334,123.1234'
        s1 = '12.12345,+12.1234'
        s2 = 'F'
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertTrue(suc)

    def test_parseCalcTLE_7(self):
        sat = Satellite()
        s0 = '+23.12334,123.1234'
        s1 = '12.12345,+12.1234'
        s2 = '12345678.1, 12345678.2, F'
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertTrue(suc)

    def test_parseCalcTLE_8(self):
        sat = Satellite()
        s0 = 'E'
        s1 = ''
        s2 = ''
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_9(self):
        sat = Satellite()
        s0 = ''
        s1 = 'E'
        s2 = ''
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_10(self):
        sat = Satellite()
        s0 = ''
        s1 = ''
        s2 = 'E'
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_11(self):
        sat = Satellite()
        s0 = ''
        s1 = ''
        s2 = ''
        response = [s0, s1, s2, s2]

        suc = sat.parseCalcTLE(response, 4)
        self.assertFalse(suc)

    def test_parseCalcTLE_12(self):
        sat = Satellite()
        s0 = '+23.12334,123.1234'
        s1 = '12.12345'
        s2 = 'N'
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_13(self):
        sat = Satellite()
        s0 = '+23.12334,123.1234'
        s1 = '12.12345,+12.1234'
        s2 = 'F,s'
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_calcTLE_1(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, 'E', 1

            suc = sat.calcTLE(julD=1234567.8)
            self.assertFalse(suc)

    def test_calcTLE_2(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, 'V', 1

            suc = sat.calcTLE(julD=1234567.8)
            self.assertFalse(suc)

    def test_calcTLE_3(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'V', 1

            suc = sat.calcTLE(julD=1234567.8)
            self.assertFalse(suc)

    def test_calcTLE_4(self):
        sat = Satellite()
        s0 = '+23.12334,123.1234'
        s1 = '12.12345,+12.1234'
        s2 = '12345678.1, 12345678.2, F'
        response = [s0, s1, s2]

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1

            suc = sat.calcTLE(julD=1234567.8)
            self.assertFalse(suc)

    def test_calcTLE_5(self):
        sat = Satellite()
        s0 = '+23.12334,123.1234'
        s1 = '12.12345,+12.1234'
        s2 = '12345678.1, 12345678.2, F'
        response = [s0, s1, s2]

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 3

            suc = sat.calcTLE(julD=1234567.8)
            self.assertTrue(suc)

    def test_calcTLE_6(self):
        sat = Satellite()
        s0 = '+23.12334,123.1234'
        s1 = '12.12345,+12.1234'
        s2 = '12345678.1, 12345678.2, F'
        response = [s0, s1, s2]

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 3

            suc = sat.calcTLE()
            self.assertFalse(suc)

    def test_calcTLE_7(self):
        sat = Satellite()
        s0 = '+23.12334,123.1234'
        s1 = '12.12345,+12.1234'
        s2 = '12345678.1, 12345678.2, F'
        response = [s0, s1, s2]

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 3

            suc = sat.calcTLE(julD=1234567.8, duration=0)
            self.assertFalse(suc)

    def test_slewTLE_1(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, 'E', 1

            suc, mes = sat.slewTLE()
            self.assertFalse(suc)

    def test_slewTLE_2(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'X', 1

            suc, mes = sat.slewTLE()
            self.assertTrue(suc)
            self.assertEqual(mes, 'Error')

    def test_slewTLE_3(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'V', 1

            suc, mes = sat.slewTLE()
            self.assertTrue(suc)
            self.assertEqual(mes, 'Slewing to start and track')

    def test_slewTLE_4(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'V', 2

            suc, mes = sat.slewTLE()
            self.assertFalse(suc)

    def test_parseStatTLE_1(self):
        sat = Satellite()
        response = ''

        suc = sat.parseStatTLE(response, 3)
        self.assertFalse(suc)

    def test_parseStatTLE_2(self):
        sat = Satellite()
        response = ''

        suc = sat.parseStatTLE(response, 1)
        self.assertFalse(suc)

    def test_parseStatTLE_3(self):
        sat = Satellite()
        response = ['']

        suc = sat.parseStatTLE(response, 1)
        self.assertFalse(suc)
        self.assertEqual(sat.tleParams.message, None)

    def test_parseStatTLE_4(self):
        sat = Satellite()
        response = ['X']

        suc = sat.parseStatTLE(response, 1)
        self.assertTrue(suc)
        self.assertEqual(sat.tleParams.message, 'Error')

    def test_parseStatTLE_5(self):
        sat = Satellite()
        response = ['V']

        suc = sat.parseStatTLE(response, 1)
        self.assertTrue(suc)
        self.assertEqual(sat.tleParams.message, 'Slewing to the start of the transit')

    def test_parseStatTLE_6(self):
        sat = Satellite()
        response = ['V', 'E']

        suc = sat.parseStatTLE(response, 2)
        self.assertFalse(suc)

    def test_statTLE_1(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, 'E', 1

            suc = sat.statTLE()
            self.assertFalse(suc)

    def test_statTLE_2(self):
        sat = Satellite()

        with mock.patch('mountcontrol.satellite.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, 'E', 1

            suc = sat.statTLE()
            self.assertTrue(suc)
