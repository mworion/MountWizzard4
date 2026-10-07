# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import os
from mw4.mountcontrol.obsSite import ObsSite
from pathlib import Path
from skyfield.api import Angle, wgs84
from unittest import mock


class Parent:
    loggingTrace = False
    pathToData = Path(os.getcwd() + "/data")

    class Config:
        hostAddress = None
        port = None

    config = Config()


def test_ObsSite_parseLocation_ok1():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "-011:35:00.0", "+48:07:00.0", "03"]
    suc = obsSite.parseLocation(response, 4)
    assert suc


def test_ObsSite_parseLocation_ok2():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "+011:35:00.0", "+48:07:00.0", "03"]
    suc = obsSite.parseLocation(response, 4)
    assert suc


def test_ObsSite_parseLocation_not_ok1():
    obsSite = ObsSite(parent=Parent())
    response = []
    suc = obsSite.parseLocation(response, 4)
    assert not suc


def test_ObsSite_parseLocation_not_ok2():
    obsSite = ObsSite(parent=Parent())

    response = ["+master", "-011:35:00.0", "+48:07:00.0", "03"]

    suc = obsSite.parseLocation(response, 4)
    assert suc


def test_ObsSite_parseLocation_not_ok3():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "-011:35:00.0", "+48:sdj.0", "03"]

    suc = obsSite.parseLocation(response, 4)
    assert suc


def test_ObsSite_parseLocation_not_ok4():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "-011:EE:00.0", "+48:07:00.0", "03"]

    suc = obsSite.parseLocation(response, 4)
    assert suc


def test_ObsSite_poll_ok():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "-011:35:00.0", "+48:07:00.0", "03"]

    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 4
        suc = obsSite.getLocation()
        assert suc


def test_ObsSite_poll_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "-011:35:00.0", "+48:07:00.0", "03"]

    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 4
        suc = obsSite.getLocation()
        assert not suc


def test_ObsSite_poll_not_ok2():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "-011:35:00.0", "+48:07:00.0", "03"]

    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 6
        suc = obsSite.getLocation()
        assert not suc


#
#
# testing pollSetting pointing
#
#


def test_ObsSite_parsePointing_ok1():
    obsSite = ObsSite(parent=Parent())

    response = [
        "13:15:35.68",
        "0.12",
        "V",
        "19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0",
        "2458352.10403639, 100, 100, 0.1, 0.1",
    ]
    suc = obsSite.parsePointing(response, 5)
    assert suc


def test_ObsSite_parsePointing_ok2():
    obsSite = ObsSite(parent=Parent())

    response = [
        "13:15:35.68",
        "0.12",
        "V",
        "19.44591,+88.0032,W,000.0000,+47.9945,2458352.10403639,5,0",
        "2458352.10403639, 100, 100, 0.1, 0.1",
    ]
    suc = obsSite.parsePointing(response, 5)
    assert suc
    assert isinstance(obsSite.Az, Angle)


def test_ObsSite_parsePointing_ok3():
    obsSite = ObsSite(parent=Parent())

    response = [
        "13:15:35.68",
        "0.12",
        "V",
        "19.44591,+88.0032,W,000.0001,+00.0000,2458352.10403639,5,0",
        "2458352.10403639, 100, 100, 0.1, 0.1",
    ]
    suc = obsSite.parsePointing(response, 5)
    assert suc
    assert isinstance(obsSite.Alt, Angle)


def test_ObsSite_parsePointing_shortInfo():
    obsSite = ObsSite(parent=Parent())
    obsSite.status = 0
    response = [
        "13:15:35.68",
        "0.12",
        "V",
        "19.44591,+88.0032,W,002.9803",
        "2458352.10403639, 100, 100, 0.1, 0.1",
    ]
    suc = obsSite.parsePointing(response, 5)
    assert not suc
    assert obsSite.status == 0


def test_ObsSite_parsePointing_shortAngular():
    obsSite = ObsSite(parent=Parent())
    response = [
        "13:15:35.68",
        "0.12",
        "V",
        "19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0",
        "2458352.10403639, 100",
    ]
    suc = obsSite.parsePointing(response, 5)
    assert not suc


def test_ObsSite_parseSetTargetResponse_empty():
    obsSite = ObsSite(parent=Parent())
    assert not obsSite.parseSetTargetResponse([])


def test_ObsSite_parseSetTargetResponse_shortFirst():
    obsSite = ObsSite(parent=Parent())
    response = ["11", "180:00:00.0", "12:30:00.00", "+45:30:00.0"]
    assert not obsSite.parseSetTargetResponse(response)


def test_ObsSite_parseSetTargetResponse_notSet():
    obsSite = ObsSite(parent=Parent())
    response = ["102+45:00:00.0", "180:00:00.0", "12:30:00.00", "+45:30:00.0"]
    assert not obsSite.parseSetTargetResponse(response)


def test_ObsSite_pollPointing_ok4():
    obsSite = ObsSite(parent=Parent())

    response = [
        "13:15:35.68",
        "0.12",
        "V",
        "19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0",
        "2458352.10403639, 100, 100, 0.1, 0.1",
    ]

    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 5
        suc = obsSite.pollPointing()
        assert suc


def test_ObsSite_pollPointing_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = [
        "13:15:35.68",
        "0.12",
        "19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0",
        "2458352.10403639, 100, 100, 0.1, 0.1",
    ]

    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 3
        suc = obsSite.pollPointing()
        assert not suc


def test_ObsSite_pollPointing_not_ok2():
    obsSite = ObsSite(parent=Parent())

    response = [
        "13:15:35.68",
        "0.12",
        "19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0",
        "2458352.10403639, 100, 100, 0.1, 0.1",
    ]

    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 5
        suc = obsSite.pollPointing()
        assert not suc


def test_startSlewing_1_1():
    obsSite = ObsSite(parent=Parent())
    response = "1#"

    obsSite.status = 0
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = obsSite.startSlewing(slewType="keep")
        assert not suc


def test_startSlewing_1_2():
    obsSite = ObsSite(parent=Parent())
    response = "1#"

    obsSite.status = 1
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = obsSite.startSlewing(slewType="keep")
        assert not suc


def test_startSlewing_3():
    obsSite = ObsSite(parent=Parent())
    response = "1#"

    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 3
        suc = obsSite.startSlewing(slewType="normal")
        assert not suc


def test_startSlewing_4():
    obsSite = ObsSite(parent=Parent())
    response = "0#"

    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.startSlewing(slewType="normal")
        assert suc


def test_ObsSite_setTargetAltAz_ok1():
    obsSite = ObsSite(parent=Parent())
    response = ["112+45:00:00.0", "180:00:00.0", "12:30:00.00", "+45:30:00.0"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 7
        suc = obsSite.setTargetAltAz(Angle(degrees=0), Angle(degrees=0))
        assert suc


def test_ObsSite_setTargetAltAz_not_ok3():
    obsSite = ObsSite(parent=Parent())
    response = ["00"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


def test_ObsSite_setTargetAltAz_not_ok4():
    obsSite = ObsSite(parent=Parent())
    response = ["00"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


def test_ObsSite_setTargetAltAz_not_ok5():
    obsSite = ObsSite(parent=Parent())
    response = ["0"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


def test_ObsSite_setTargetAltAz_not_ok6():
    obsSite = ObsSite(parent=Parent())
    response = ["1#2"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


def test_ObsSite_setTargetAltAz_not_ok7():
    obsSite = ObsSite(parent=Parent())

    response = ["1#2"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


#
#
# testing setTargetRaDec
#
#


def test_ObsSite_setTargetRaDec_ok1():
    obsSite = ObsSite(parent=Parent())
    response = ["112+45:00:00.0", "180:00:00.0", "12:30:00.00", "+45:30:00.0"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert suc


def test_ObsSite_setTargetRaDec_not_ok5():
    obsSite = ObsSite(parent=Parent())

    response = ["00"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


def test_ObsSite_setTargetRaDec_not_ok6():
    obsSite = ObsSite(parent=Parent())

    response = ["00"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


def test_ObsSite_setTargetRaDec_not_ok7():
    obsSite = ObsSite(parent=Parent())

    response = ["0"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


def test_ObsSite_setTargetRaDec_not_ok8():
    obsSite = ObsSite(parent=Parent())

    response = ["1#"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


def test_ObsSite_setTargetRaDec_not_ok9():
    obsSite = ObsSite(parent=Parent())

    response = ["1#"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


#
#
# testing shutdown
#
#


def test_ObsSite_shutdown_ok():
    obsSite = ObsSite(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.shutdown()
        assert suc


#
#
# testing setSite
#
#


def test_ObsSite_setLocation_ok():
    obsSite = ObsSite(parent=Parent())
    observer = wgs84.latlon(latitude_degrees=50, longitude_degrees=11, elevation_m=580)
    response = ["111"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.setLocation(observer)
        assert suc


def test_ObsSite_setLatitude_ok2():
    obsSite = ObsSite(parent=Parent())
    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.setLatitude(lat=Angle(degrees=50))
        assert suc


def test_ObsSite_setLongitude_ok2():
    obsSite = ObsSite(parent=Parent())
    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.setLongitude(lon=Angle(degrees=50))
        assert suc


def test_ObsSite_setElevation_ok1():
    obsSite = ObsSite(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.setElevation(500)
        assert suc


#
#
# testing startTracking
#
#


def test_ObsSite_startTracking_ok():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.startTracking()
        assert suc


def test_ObsSite_startTracking_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.startTracking()
        assert not suc


#
#
# testing stopTracking
#
#


def test_ObsSite_stopTracking_ok():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopTracking()
        assert suc


def test_ObsSite_stopTracking_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopTracking()
        assert not suc


#
#
# testing park
#
#


def test_ObsSite_park_ok():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.park()
        assert suc


def test_ObsSite_park_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.park()
        assert not suc


#
#
# testing unpark
#
#


def test_ObsSite_unpark_ok():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.unpark()
        assert suc


def test_ObsSite_unpark_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.unpark()
        assert not suc


#
#
# testing parkOnActualPosition
#
#


def test_ObsSite_parkOnActualPosition_ok():
    obsSite = ObsSite(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.parkOnActualPosition()
        assert suc


#
#
# testing stop
#
#


def test_ObsSite_stop_ok():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stop()
        assert suc


def test_ObsSite_stop_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stop()
        assert not suc


#
#
# testing flip
#
#


def test_ObsSite_flip_ok():
    obsSite = ObsSite(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.flip()
        assert suc


def test_moveNorth_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.moveNorth()
        assert not suc


def test_moveNorth_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.moveNorth()
        assert suc


def test_moveEast_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.moveEast()
        assert not suc


def test_moveEast_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.moveEast()
        assert suc


def test_moveSouth_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.moveSouth()
        assert not suc


def test_moveSouth_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.moveSouth()
        assert suc


def test_moveWest_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.moveWest()
        assert not suc


def test_moveWest_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.moveWest()
        assert suc


def test_stopMoveNorth_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveNorth()
        assert not suc


def test_stopMoveNorth_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveNorth()
        assert suc


def test_stopMoveEast_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveEast()
        assert not suc


def test_stopMoveEast_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveEast()
        assert suc


def test_stopMoveSouth_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveSouth()
        assert not suc


def test_stopMoveSouth_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveSouth()
        assert suc


def test_stopMoveWest_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveWest()
        assert not suc


def test_stopMoveWest_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveWest()
        assert suc


def test_stopMoveAll_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveAll()
        assert not suc


def test_stopMoveAll_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveAll()
        assert suc


def test_syncPositionToTarget_1():
    obsSite = ObsSite(parent=Parent())
    response = ["0", ""]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.syncPositionToTarget()
        assert not suc


def test_syncPositionToTarget_2():
    obsSite = ObsSite(parent=Parent())
    response = ["1", "Coordinates"]
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.syncPositionToTarget()
        assert suc


def test_syncPositionToTarget_shortResponse():
    obsSite = ObsSite(parent=Parent())
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, [""], 0
        suc = obsSite.syncPositionToTarget()
        assert not suc


def test_setHighPrecision_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.setHighPrecision()
        assert not suc


def test_setHighPrecision_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSiteCommands.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.setHighPrecision()
        assert suc
