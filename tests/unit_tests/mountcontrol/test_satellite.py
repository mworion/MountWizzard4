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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import unittest
import unittest.mock as mock
from mw4.base.loggerMW import setupLogging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.satellite import Satellite
from skyfield.api import Angle, load

setupLogging()


class TestConfigData(unittest.TestCase):
    def setUp(self):
        pass

    def test_parseGetTLE_1(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        t0 = "NOAA 8 [-]              "
        t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
        t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"
        cont = "$0A"
        response = [t0 + cont + t1 + cont + t2 + cont]

        suc = sat.parseGetTLE(response, 1)

        self.assertTrue(suc)
        self.assertEqual(sat.tleParams.name, "NOAA 8 [-]")
        self.assertEqual(sat.tleParams.l0, t0)
        self.assertEqual(sat.tleParams.l1, t1)
        self.assertEqual(sat.tleParams.l2, t2)

    def test_parseGetTLE_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        response = ["76129888407$0A"]

        suc = sat.parseGetTLE(response, 1)

        self.assertFalse(suc)
        self.assertEqual(sat.tleParams.name, "")
        self.assertEqual(sat.tleParams.l0, "")
        self.assertEqual(sat.tleParams.l1, "")
        self.assertEqual(sat.tleParams.l2, "")

    def test_parseGetTLE_3(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        response = ["76129888407$0A", ["hj"]]

        suc = sat.parseGetTLE(response, 1)

        self.assertFalse(suc)
        self.assertEqual(sat.tleParams.name, "")
        self.assertEqual(sat.tleParams.l0, "")
        self.assertEqual(sat.tleParams.l1, "")
        self.assertEqual(sat.tleParams.l2, "")

    def test_getTLE_1(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        t0 = "NOAA 8 [-]              "
        t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
        t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"
        cont = "$0A"
        response = [t0 + cont + t1 + cont + t2 + cont]

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, response, 1

            suc = sat.getTLE()
            self.assertFalse(suc)

    def test_getTLE_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        t0 = "NOAA 8 [-]              "
        t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
        t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"
        cont = "$0A"
        response = [t0 + cont + t1 + cont + t2 + cont]

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 1

            suc = sat.getTLE()
            self.assertTrue(suc)

    def test_getTLE_3(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        t0 = "NOAA 8 [-]              "
        t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
        t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"
        cont = "$0A"
        response = [t0 + cont + t1 + cont + t2 + cont]

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 2

            suc = sat.getTLE()
            self.assertFalse(suc)

    def test_getTLE_4(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "E", 1

            suc = sat.getTLE()
            self.assertFalse(suc)

    def test_getTLE_5(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, ["V", "V"], 2

            suc = sat.getTLE()
            self.assertFalse(suc)

    def test_setTLE_4(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        t0 = "NOAA 8 [-]              "
        t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
        t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "V", 1

            suc = sat.setTLE(line0=t0, line1=t1, line2=t2)
            self.assertTrue(suc)

    def test_setTLE_5(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        t0 = "NOAA 8 [-]              "
        t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
        t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407x"

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "V", 1

            suc = sat.setTLE(line0=t0, line1=t1, line2=t2)
            self.assertFalse(suc)

    def test_setTLE_6(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        t0 = "NOAA 8 [-]              "
        t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996x"
        t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "V", 1

            suc = sat.setTLE(line0=t0, line1=t1, line2=t2)
            self.assertFalse(suc)

    def test_setTLE_7(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        t0 = "NOAA 8 [-]              "
        t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
        t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, "V", 1

            suc = sat.setTLE(line0=t0, line1=t1, line2=t2)
            self.assertFalse(suc)

    def test_parseCalcTLE_1(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        response = ""

        suc = sat.parseCalcTLE(response, 1)
        self.assertFalse(suc)

    def test_parseCalcTLE_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        response = ""

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_3(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        response = []

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_4(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        response = ["E", "E", "E"]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_5(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = ""
        s1 = ""
        s2 = ""
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_6(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = "+23.12334,123.1234"
        s1 = "12.12345,+12.1234"
        s2 = "F"
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertTrue(suc)

    def test_parseCalcTLE_7(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = "+23.12334,123.1234"
        s1 = "12.12345,+12.1234"
        s2 = "12345678.1, 12345678.2, F"
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertTrue(suc)

    def test_parseCalcTLE_8(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = "E"
        s1 = ""
        s2 = ""
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_9(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = ""
        s1 = "E"
        s2 = ""
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_10(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = ""
        s1 = ""
        s2 = "E"
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_11(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = ""
        s1 = ""
        s2 = ""
        response = [s0, s1, s2, s2]

        suc = sat.parseCalcTLE(response, 4)
        self.assertFalse(suc)

    def test_parseCalcTLE_12(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = "+23.12334,123.1234"
        s1 = "12.12345"
        s2 = "N"
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_parseCalcTLE_13(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = "+23.12334,123.1234"
        s1 = "12.12345,+12.1234"
        s2 = "F,s"
        response = [s0, s1, s2]

        suc = sat.parseCalcTLE(response, 3)
        self.assertFalse(suc)

    def test_calcTLE_0(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        ts = load.timescale()
        julD = ts.tt_jd(1234567.8)

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, "E", 1

            suc = sat.calcTLE(julD=1234567.8)
            self.assertFalse(suc)

    def test_calcTLE_1(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        ts = load.timescale()
        julD = ts.tt_jd(1234567.8)

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, "E", 1

            suc = sat.calcTLE(julD=julD)
            self.assertFalse(suc)

    def test_calcTLE_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, "V", 1

            suc = sat.calcTLE(julD=1234567.8)
            self.assertFalse(suc)

    def test_calcTLE_3(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "V", 1

            suc = sat.calcTLE(julD=1234567.8)
            self.assertFalse(suc)

    def test_calcTLE_4(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = "+23.12334,123.1234"
        s1 = "12.12345,+12.1234"
        s2 = "12345678.1, 12345678.2, F"
        response = [s0, s1, s2]

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 1

            suc = sat.calcTLE(julD=1234567.8)
            self.assertFalse(suc)

    def test_calcTLE_5(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = "+23.12334,123.1234"
        s1 = "12.12345,+12.1234"
        s2 = "12345678.1, 12345678.2, F"
        response = [s0, s1, s2]

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 3

            suc = sat.calcTLE(julD=1234567.8)
            self.assertTrue(suc)

    def test_calcTLE_7(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        s0 = "+23.12334,123.1234"
        s1 = "12.12345,+12.1234"
        s2 = "12345678.1, 12345678.2, F"
        response = [s0, s1, s2]

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, response, 3

            suc = sat.calcTLE(julD=1234567.8, duration=0)
            self.assertFalse(suc)

    def test_slewTLE_1(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, "E", 1

            suc, mes = sat.slewTLE()
            self.assertFalse(suc)

    def test_slewTLE_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "X", 1

            suc, mes = sat.slewTLE()
            self.assertTrue(suc)
            self.assertEqual(mes, "Error")

    def test_slewTLE_3(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "V", 1

            suc, mes = sat.slewTLE()
            self.assertTrue(suc)
            self.assertEqual(mes, "Slewing to start and track")

    def test_slewTLE_4(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "V", 2

            suc, mes = sat.slewTLE()
            self.assertFalse(suc)

    def test_parseStatTLE_1(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        response = ""

        suc = sat.parseStatTLE(response, 3)
        self.assertFalse(suc)

    def test_parseStatTLE_2(self):
        class Parent:
            obsSite = None

        sat = Satellite(parent=Parent())
        response = ""

        suc = sat.parseStatTLE(response, 1)
        self.assertFalse(suc)

    def test_parseStatTLE_3(self):
        class Parent:
            obsSite = None

        sat = Satellite(parent=Parent())
        response = [""]

        suc = sat.parseStatTLE(response, 1)
        self.assertFalse(suc)
        self.assertEqual(sat.tleParams.message, "")

    def test_parseStatTLE_4(self):
        class Parent:
            obsSite = None

        sat = Satellite(parent=Parent())
        response = ["X"]

        suc = sat.parseStatTLE(response, 1)
        self.assertTrue(suc)
        self.assertEqual(sat.tleParams.message, "Error")

    def test_parseStatTLE_5(self):
        class Parent:
            obsSite = None

        sat = Satellite(parent=Parent())
        response = ["V"]

        suc = sat.parseStatTLE(response, 1)
        self.assertTrue(suc)
        self.assertEqual(sat.tleParams.message, "Slewing to the start of the transit")

    def test_parseStatTLE_6(self):
        class Parent:
            obsSite = None

        sat = Satellite(parent=Parent())
        response = ["V", "E"]

        suc = sat.parseStatTLE(response, 2)
        self.assertFalse(suc)

    def test_statTLE_1(self):
        class Parent:
            obsSite = None
            host = None

        sat = Satellite(parent=Parent())

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = False, "E", 1

            suc = sat.statTLE()
            self.assertFalse(suc)

    def test_statTLE_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())

        with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
            mConn.return_value.communicate.return_value = True, "E", 1

            suc = sat.statTLE()
            self.assertTrue(suc)

    def test_startProgTrajectory_6(self):
        ts = load.timescale()
        julD = ts.tt_jd(12345678)

        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["V"], 1)
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.startProgTrajectory(julD=julD)
            assert suc

    def test_progTrajectoryData_3(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (False, ["1", "2"], 1)
        alt = Angle(degrees=[10, 20, 30])
        az = Angle(degrees=[40, 50, 60])
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.addTrajectoryPoint(alt=alt, az=az)
            assert not suc

    def test_progTrajectoryData_4(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["1", "2"], 1)
        alt = Angle(degrees=[10, 20, 30])
        az = Angle(degrees=[40, 50, 60])
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.addTrajectoryPoint(alt=alt, az=az)
            assert not suc

    def test_progTrajectoryData_5(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["1", "2"], 2)
        alt = Angle(degrees=[10, 20, 30])
        az = Angle(degrees=[40, 50, 60])
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.addTrajectoryPoint(alt=alt, az=az)
            assert not suc

    def test_progTrajectoryData_6(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["1", "2", "E"], 3)
        alt = Angle(degrees=[10, 20, 30])
        az = Angle(degrees=[40, 50, 60])
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.addTrajectoryPoint(alt=alt, az=az)
            assert not suc

    def test_progTrajectoryData_7(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["1", "2", "3"], 3)
        alt = Angle(degrees=[10, 20, 30])
        az = Angle(degrees=[40, 50, 60])
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.addTrajectoryPoint(alt=alt, az=az)
            assert suc

    def test_preCalcTrajectory_1(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (False, ["V"], 1)
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.preCalcTrajectory()
            assert not suc

    def test_preCalcTrajectory_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (False, ["V"], 1)
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.preCalcTrajectory(replay=True)
            assert not suc

    def test_preCalcTrajectory_3(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["V"], 2)
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.preCalcTrajectory()
            assert not suc

    def test_preCalcTrajectory_4(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["V", "V"], 2)
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.preCalcTrajectory()
            assert not suc

    def test_preCalcTrajectory_5(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["E"], 1)
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.preCalcTrajectory()
            assert not suc

    def test_preCalcTrajectory_6(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["10, 10, F, F"], 1)
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.preCalcTrajectory()
            assert not suc

    def test_preCalcTrajectory_7(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        val = (True, ["10, 10, F"], 1)
        with mock.patch.object(Connection, "communicate", return_value=val):
            suc = sat.preCalcTrajectory()
            assert suc

    def test_getTrackingOffsets_1(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        suc = sat.getTrackingOffsets()
        self.assertFalse(suc)

    def test_getTrackingOffsets_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, [1, 2, 3], 1)):
            suc = sat.getTrackingOffsets()
            self.assertFalse(suc)

    def test_getTrackingOffsets_3(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, [1, 2, 3], 3)):
            suc = sat.getTrackingOffsets()
            self.assertFalse(suc)

    def test_getTrackingOffsets_4(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(
            Connection, "communicate", return_value=(True, [1, 2, 3, 4], 4)
        ):
            suc = sat.getTrackingOffsets()
            self.assertTrue(suc)

    def test_setTrackingFirst(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
            suc = sat.setTrackingFirst(first=Angle(degrees=1))
            self.assertTrue(suc)

    def test_setTrackingSecond(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
            suc = sat.setTrackingSecond(second=Angle(degrees=1))
            self.assertTrue(suc)

    def test_setTrackingFirstCorr(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
            suc = sat.setTrackingFirstCorr(firstCorr=Angle(degrees=1))
            self.assertTrue(suc)

    def test_setTrackingTime(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
            suc = sat.setTrackingTime(time=1)
            self.assertTrue(suc)

    def test_addTrackingFirst(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
            suc = sat.addTrackingFirst(first=Angle(degrees=1))
            self.assertTrue(suc)

    def test_addTrackingSecond(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
            suc = sat.addTrackingSecond(second=Angle(degrees=1))
            self.assertTrue(suc)

    def test_addTrackingFirstCorr(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
            suc = sat.addTrackingFirstCorr(firstCorr=Angle(degrees=1))
            self.assertTrue(suc)

    def test_addTrackingTime(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
            suc = sat.addTrackingTime(time=1)
            self.assertTrue(suc)

    def test_clearTrackingOffsets(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        class Parent:
            obsSite = ObsSite()
            host = None

        sat = Satellite(parent=Parent())
        with mock.patch.object(Connection, "communicate", return_value=(True, ["V"], 1)):
            suc = sat.clearTrackingOffsets()
            self.assertTrue(suc)
