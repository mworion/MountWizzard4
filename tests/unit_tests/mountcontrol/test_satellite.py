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
from mw4.base.loggerMW import setupLogging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.satellite import Satellite
from skyfield.api import Angle, load
from tests.unit_tests.unitTestAddOns.baseTestApp import App

setupLogging()


def test_parseGetTLE_1():
    sat = Satellite(App().mount)
    t0 = "NOAA 8 [-]              "
    t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
    t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"
    cont = "$0A"
    response = [t0 + cont + t1 + cont + t2 + cont]

    suc = sat.parseGetTLE(response, 1)

    assert suc
    assert sat.tleParams.name == "NOAA 8 [-]"
    assert sat.tleParams.l0 == t0
    assert sat.tleParams.l1 == t1
    assert sat.tleParams.l2 == t2


def test_parseGetTLE_2():
    sat = Satellite(App().mount)
    response = ["76129888407$0A"]

    suc = sat.parseGetTLE(response, 1)

    assert not suc
    assert sat.tleParams.name == ""
    assert sat.tleParams.l0 == ""
    assert sat.tleParams.l1 == ""
    assert sat.tleParams.l2 == ""


def test_parseGetTLE_3():
    sat = Satellite(App().mount)
    response = ["76129888407$0A", ["hj"]]

    suc = sat.parseGetTLE(response, 1)

    assert not suc
    assert sat.tleParams.name == ""
    assert sat.tleParams.l0 == ""
    assert sat.tleParams.l1 == ""
    assert sat.tleParams.l2 == ""


def test_getTLE_1():
    sat = Satellite(App().mount)
    t0 = "NOAA 8 [-]              "
    t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
    t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"
    cont = "$0A"
    response = [t0 + cont + t1 + cont + t2 + cont]

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1

        suc = sat.getTLE()
        assert not suc


def test_getTLE_2():
    sat = Satellite(App().mount)
    t0 = "NOAA 8 [-]              "
    t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
    t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"
    cont = "$0A"
    response = [t0 + cont + t1 + cont + t2 + cont]

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1

        suc = sat.getTLE()
        assert suc


def test_getTLE_3():
    sat = Satellite(App().mount)
    t0 = "NOAA 8 [-]              "
    t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
    t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"
    cont = "$0A"
    response = [t0 + cont + t1 + cont + t2 + cont]

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2

        suc = sat.getTLE()
        assert not suc


def test_getTLE_4():
    sat = Satellite(App().mount)

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "E", 1

        suc = sat.getTLE()
        assert not suc


def test_getTLE_5():
    sat = Satellite(App().mount)

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, ["V", "V"], 2

        suc = sat.getTLE()
        assert not suc


def test_setTLE_4():
    sat = Satellite(App().mount)
    t0 = "NOAA 8 [-]              "
    t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
    t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "V", 1

        suc = sat.setTLE(line0=t0, line1=t1, line2=t2)
        assert suc


def test_setTLE_5():
    sat = Satellite(App().mount)
    t0 = "NOAA 8 [-]              "
    t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
    t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407x"

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "V", 1

        suc = sat.setTLE(line0=t0, line1=t1, line2=t2)
        assert not suc


def test_setTLE_6():
    sat = Satellite(App().mount)
    t0 = "NOAA 8 [-]              "
    t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996x"
    t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "V", 1

        suc = sat.setTLE(line0=t0, line1=t1, line2=t2)
        assert not suc


def test_setTLE_7():
    sat = Satellite(App().mount)
    t0 = "NOAA 8 [-]              "
    t1 = "1 13923U 83022A   19185.92877216 -.00000021  00000-0  89876-5 0  9996"
    t2 = "2 13923  98.5823 170.9975 0016143 125.4216 234.8476 14.28676129888407"

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, "V", 1

        suc = sat.setTLE(line0=t0, line1=t1, line2=t2)
        assert not suc


def test_parseCalcTLE_1():
    sat = Satellite(App().mount)
    response = ""

    suc = sat.parseCalcTLE(response, 1)
    assert not suc


def test_parseCalcTLE_2():
    sat = Satellite(App().mount)
    response = ""

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_parseCalcTLE_3():
    sat = Satellite(App().mount)
    response = []

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_parseCalcTLE_4():
    sat = Satellite(App().mount)
    response = ["E", "E", "E"]

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_parseCalcTLE_5():
    sat = Satellite(App().mount)
    s0 = ""
    s1 = ""
    s2 = ""
    response = [s0, s1, s2]

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_parseCalcTLE_6():
    sat = Satellite(App().mount)
    s0 = "+23.12334,123.1234"
    s1 = "12.12345,+12.1234"
    s2 = "F"
    response = [s0, s1, s2]

    suc = sat.parseCalcTLE(response, 3)
    assert suc


def test_parseCalcTLE_7():
    sat = Satellite(App().mount)
    s0 = "+23.12334,123.1234"
    s1 = "12.12345,+12.1234"
    s2 = "12345678.1, 12345678.2, F"
    response = [s0, s1, s2]

    suc = sat.parseCalcTLE(response, 3)
    assert suc


def test_parseCalcTLE_8():
    sat = Satellite(App().mount)
    s0 = "E"
    s1 = ""
    s2 = ""
    response = [s0, s1, s2]

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_parseCalcTLE_9():
    sat = Satellite(App().mount)
    s0 = ""
    s1 = "E"
    s2 = ""
    response = [s0, s1, s2]

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_parseCalcTLE_10():
    sat = Satellite(App().mount)
    s0 = ""
    s1 = ""
    s2 = "E"
    response = [s0, s1, s2]

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_parseCalcTLE_11():
    sat = Satellite(App().mount)
    s0 = ""
    s1 = ""
    s2 = ""
    response = [s0, s1, s2, s2]

    suc = sat.parseCalcTLE(response, 4)
    assert not suc


def test_parseCalcTLE_12():
    sat = Satellite(App().mount)
    s0 = "+23.12334,123.1234"
    s1 = "12.12345"
    s2 = "N"
    response = [s0, s1, s2]

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_parseCalcTLE_13():
    sat = Satellite(App().mount)
    s0 = "+23.12334,123.1234"
    s1 = "12.12345,+12.1234"
    s2 = "F,s"
    response = [s0, s1, s2]

    suc = sat.parseCalcTLE(response, 3)
    assert not suc


def test_calcTLE_0():
    sat = Satellite(App().mount)
    ts = load.timescale()
    ts.tt_jd(1234567.8)

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, "E", 1

        suc = sat.calcTLE(julD=1234567.8)
        assert not suc


def test_calcTLE_1():
    sat = Satellite(App().mount)
    ts = load.timescale()
    julD = ts.tt_jd(1234567.8)

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, "E", 1

        suc = sat.calcTLE(julD=julD)
        assert not suc


def test_calcTLE_2():
    sat = Satellite(App().mount)

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, "V", 1

        suc = sat.calcTLE(julD=1234567.8)
        assert not suc


def test_calcTLE_3():
    sat = Satellite(App().mount)

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "V", 1

        suc = sat.calcTLE(julD=1234567.8)
        assert not suc


def test_calcTLE_4():
    sat = Satellite(App().mount)
    s0 = "+23.12334,123.1234"
    s1 = "12.12345,+12.1234"
    s2 = "12345678.1, 12345678.2, F"
    response = [s0, s1, s2]

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1

        suc = sat.calcTLE(julD=1234567.8)
        assert not suc


def test_calcTLE_5():
    sat = Satellite(App().mount)
    s0 = "+23.12334,123.1234"
    s1 = "12.12345,+12.1234"
    s2 = "12345678.1, 12345678.2, F"
    response = [s0, s1, s2]

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 3

        suc = sat.calcTLE(julD=1234567.8)
        assert suc


def test_calcTLE_7():
    sat = Satellite(App().mount)
    s0 = "+23.12334,123.1234"
    s1 = "12.12345,+12.1234"
    s2 = "12345678.1, 12345678.2, F"
    response = [s0, s1, s2]

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 3

        suc = sat.calcTLE(julD=1234567.8, duration=0)
        assert not suc


def test_slewTLE_1():
    sat = Satellite(App().mount)
    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, "E", 1

        suc, mes = sat.slewTLE()
        assert not suc


def test_slewTLE_2():
    sat = Satellite(App().mount)
    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "X", 1

        suc, mes = sat.slewTLE()
        assert suc
        assert mes == "Error"


def test_slewTLE_3():
    sat = Satellite(App().mount)
    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "V", 1

        suc, mes = sat.slewTLE()
        assert suc
        assert mes == "Slewing to start and track"


def test_slewTLE_4():
    sat = Satellite(App().mount)
    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "V", 2

        suc, mes = sat.slewTLE()
        assert not suc


def test_parseStatTLE_1():
    sat = Satellite(App().mount)
    response = ""

    suc = sat.parseStatTLE(response, 3)
    assert not suc


def test_parseStatTLE_2():
    sat = Satellite(App().mount)
    response = ""

    suc = sat.parseStatTLE(response, 1)
    assert not suc


def test_parseStatTLE_3():
    sat = Satellite(App().mount)
    response = [""]

    suc = sat.parseStatTLE(response, 1)
    assert not suc
    assert sat.tleParams.message == ""


def test_parseStatTLE_4():
    sat = Satellite(App().mount)
    response = ["X"]

    suc = sat.parseStatTLE(response, 1)
    assert suc
    assert sat.tleParams.message == "Error"


def test_parseStatTLE_5():
    sat = Satellite(App().mount)
    response = ["V"]

    suc = sat.parseStatTLE(response, 1)
    assert suc
    assert sat.tleParams.message == "Slewing to the start of the transit"


def test_parseStatTLE_6():
    sat = Satellite(App().mount)
    response = ["V", "E"]

    suc = sat.parseStatTLE(response, 2)
    assert not suc


def test_statTLE_1():
    class Parent:
        obsSite = None
        host = None

    sat = Satellite(App().mount)

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, "E", 1

        suc = sat.statTLE()
        assert not suc


def test_statTLE_2():
    sat = Satellite(App().mount)

    with mock.patch("mw4.mountcontrol.satellite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, "E", 1

        suc = sat.statTLE()
        assert suc


def test_startProgTrajectory_6():
    ts = load.timescale()
    julD = ts.tt_jd(12345678)

    sat = Satellite(App().mount)
    val = (True, ["V"], 1)
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.startProgTrajectory(julD=julD)
        assert suc


def test_progTrajectoryData_3():
    sat = Satellite(App().mount)
    val = (False, ["1", "2"], 1)
    alt = Angle(degrees=[10, 20, 30])
    az = Angle(degrees=[40, 50, 60])
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.addTrajectoryPoint(alt=alt, az=az)
        assert not suc


def test_progTrajectoryData_4():
    sat = Satellite(App().mount)
    val = (True, ["1", "2"], 1)
    alt = Angle(degrees=[10, 20, 30])
    az = Angle(degrees=[40, 50, 60])
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.addTrajectoryPoint(alt=alt, az=az)
        assert not suc


def test_progTrajectoryData_5():
    sat = Satellite(App().mount)
    val = (True, ["1", "2"], 2)
    alt = Angle(degrees=[10, 20, 30])
    az = Angle(degrees=[40, 50, 60])
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.addTrajectoryPoint(alt=alt, az=az)
        assert not suc


def test_progTrajectoryData_6():
    sat = Satellite(App().mount)
    val = (True, ["1", "2", "E"], 3)
    alt = Angle(degrees=[10, 20, 30])
    az = Angle(degrees=[40, 50, 60])
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.addTrajectoryPoint(alt=alt, az=az)
        assert not suc


def test_progTrajectoryData_7():
    sat = Satellite(App().mount)
    val = (True, ["1", "2", "3"], 3)
    alt = Angle(degrees=[10, 20, 30])
    az = Angle(degrees=[40, 50, 60])
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.addTrajectoryPoint(alt=alt, az=az)
        assert suc


def test_preCalcTrajectory_1():
    sat = Satellite(App().mount)
    val = (False, ["V"], 1)
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.preCalcTrajectory()
        assert not suc


def test_preCalcTrajectory_2():
    sat = Satellite(App().mount)
    val = (False, ["V"], 1)
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.preCalcTrajectory(replay=True)
        assert not suc


def test_preCalcTrajectory_3():
    sat = Satellite(App().mount)
    val = (True, ["V"], 2)
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.preCalcTrajectory()
        assert not suc


def test_preCalcTrajectory_4():
    sat = Satellite(App().mount)
    val = (True, ["V", "V"], 2)
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.preCalcTrajectory()
        assert not suc


def test_preCalcTrajectory_5():
    sat = Satellite(App().mount)
    val = (True, ["E"], 1)
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.preCalcTrajectory()
        assert not suc


def test_preCalcTrajectory_6():
    sat = Satellite(App().mount)
    val = (True, ["10, 10, F, F"], 1)
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.preCalcTrajectory()
        assert not suc


def test_preCalcTrajectory_7():
    sat = Satellite(App().mount)
    val = (True, ["10, 10, F"], 1)
    with mock.patch.object(Connection, "communicate", return_value=val):
        suc = sat.preCalcTrajectory()
        assert suc


def test_getTrackingOffsets_1():
    sat = Satellite(App().mount)
    suc = sat.getTrackingOffsets()
    assert not suc


def test_getTrackingOffsets_2():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, [1, 2, 3], 1)):
        suc = sat.getTrackingOffsets()
        assert not suc


def test_getTrackingOffsets_3():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, [1, 2, 3], 3)):
        suc = sat.getTrackingOffsets()
        assert not suc


def test_getTrackingOffsets_4():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, [1, 2, 3, 4], 4)):
        suc = sat.getTrackingOffsets()
        assert suc


def test_setTrackingOffsets_1():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(False, [1, 2, 3, 4], 4)):
        suc = sat.setTrackingOffsets(RA=1, DEC=1, DECcorr=1, Time=1)
        assert not suc


def test_setTrackingOffsets_2():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, [1, 2, 3, 4], 1)):
        suc = sat.setTrackingOffsets(RA=1, DEC=1, DECcorr=1, Time=1)
        assert not suc


def test_setTrackingOffsets_3():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E", 2, 3], 3)):
        suc = sat.setTrackingOffsets(RA=1, DEC=1, DECcorr=1, Time=1)
        assert not suc


def test_setTrackingOffsets_4():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E", 2, 3, 4], 4)):
        suc = sat.setTrackingOffsets(RA=1, DEC=1, DECcorr=1, Time=1)
        assert not suc


def test_setTrackingOffsets_5():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, [1, 2, 3, 4], 4)):
        suc = sat.setTrackingOffsets(RA=1, DEC=1, DECcorr=1, Time=1)
        assert suc


def test_setTrackingFirst():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
        suc = sat.setTrackingFirst(first=Angle(degrees=1))
        assert suc


def test_setTrackingSecond():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
        suc = sat.setTrackingSecond(second=Angle(degrees=1))
        assert suc


def test_setTrackingFirstCorr():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
        suc = sat.setTrackingFirstCorr(firstCorr=Angle(degrees=1))
        assert suc


def test_setTrackingTime():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
        suc = sat.setTrackingTime(time=1)
        assert suc


def test_addTrackingFirst():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
        suc = sat.addTrackingFirst(first=Angle(degrees=1))
        assert suc


def test_addTrackingSecond():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
        suc = sat.addTrackingSecond(second=Angle(degrees=1))
        assert suc


def test_addTrackingFirstCorr():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
        suc = sat.addTrackingFirstCorr(firstCorr=Angle(degrees=1))
        assert suc


def test_addTrackingTime():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["E"], 1)):
        suc = sat.addTrackingTime(time=1)
        assert suc


def test_clearTrackingOffsets():
    sat = Satellite(App().mount)
    with mock.patch.object(Connection, "communicate", return_value=(True, ["V"], 1)):
        suc = sat.clearTrackingOffsets()
        assert suc
