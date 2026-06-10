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

import math
import mw4.mountcontrol
import os
import platform
import unittest.mock as mock
from mw4.mountcontrol.obsSite import ObsSite
from pathlib import Path
from skyfield.api import Angle, Loader, Timescale, wgs84


class Parent:
    host = None
    loggingTrace = False
    pathToData = Path(os.getcwd() + "/data")


#
#
# testing the timescale reference
#
#


def test_setLoaderAndTimescale_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.setLoaderAndTimescale()


def test_setLoaderAndTimescale_2():
    obsSite = ObsSite(parent=Parent())
    obsSite.setLoaderAndTimescale()


def test_setLoaderAndTimescale_3():
    obsSite = ObsSite(parent=Parent())
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(Loader, "timescale"),
        mock.patch.object(Loader.timescale, "now"),
    ):
        obsSite.setLoaderAndTimescale()


def test_Data_without_ts():
    obsSite = ObsSite(parent=Parent())
    assert isinstance(obsSite.ts, Timescale)


def test_Data_with_ts():
    obsSite = ObsSite(parent=Parent())
    assert isinstance(obsSite.ts, Timescale)


def test_Site_location_1():
    obsSite = ObsSite(parent=Parent())

    elev = "999.9"
    lon = "+160*30:45.5"
    lat = "+45*30:45.5"
    obsSite.location = lat, lon, elev
    assert math.isclose(obsSite.location.longitude.dms()[0], 160, abs_tol=1e-6)
    assert math.isclose(obsSite.location.longitude.dms()[1], 30, abs_tol=1e-6)
    assert math.isclose(obsSite.location.longitude.dms()[2], 45.5, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[0], 45, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[1], 30, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[2], 45.5, abs_tol=1e-6)
    assert math.isclose(obsSite.location.elevation.m, 999.9, abs_tol=1e-6)


def test_Site_location_2():
    obsSite = ObsSite(parent=Parent())

    elev = "999.9"
    lon = "+160*30:45.5"
    lat = "+45*30:45.5"
    obsSite.location = (lat, lon, elev)
    assert math.isclose(obsSite.location.longitude.dms()[0], 160, abs_tol=1e-6)
    assert math.isclose(obsSite.location.longitude.dms()[1], 30, abs_tol=1e-6)
    assert math.isclose(obsSite.location.longitude.dms()[2], 45.5, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[0], 45, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[1], 30, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[2], 45.5, abs_tol=1e-6)
    assert math.isclose(obsSite.location.elevation.m, 999.9, abs_tol=1e-6)


def test_Site_location_3():
    obsSite = ObsSite(parent=Parent())

    elev = 100
    lon = 100
    lat = 45
    obsSite.location = wgs84.latlon(
        longitude_degrees=lon, latitude_degrees=lat, elevation_m=elev
    )
    assert math.isclose(obsSite.location.longitude.dms()[0], 100, abs_tol=1e-6)
    assert math.isclose(obsSite.location.longitude.dms()[1], 0, abs_tol=1e-6)
    assert math.isclose(obsSite.location.longitude.dms()[2], 0, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[0], 45, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[1], 0, abs_tol=1e-6)
    assert math.isclose(obsSite.location.latitude.dms()[2], 0, abs_tol=1e-6)
    assert math.isclose(obsSite.location.elevation.m, 100, abs_tol=1e-6)


def test_Site_location_4():
    obsSite = ObsSite(parent=Parent())

    lon = "+160*30:45.5"
    lat = "+45*30:45.5"
    obsSite.location = (lat, lon)
    assert obsSite.location.latitude.degrees == 0
    assert obsSite._location.longitude.degrees == 0


def test_Site_location_5():
    obsSite = ObsSite(parent=Parent())

    lat = "+45*30:45.5"
    obsSite.location = lat
    assert obsSite.location.latitude.degrees == 0


def test_Site_timeJD_1():
    parent = Parent()
    parent.mountIsUp = True
    obsSite = ObsSite(parent)

    obsSite.ut1_utc = "0"
    obsSite.timeJD = "2458240.12345678"
    assert obsSite.timeJD.ut1 == 2458240.123457949
    obsSite.timeJD = 2458240.12345678
    assert obsSite.timeJD.ut1 == 2458240.123457949


def test_Site_timeJD_2():
    parent = Parent()
    parent.mountIsUp = True
    obsSite = ObsSite(parent)

    obsSite.timeJD = obsSite.ts.now().tt - 69.184 / 86400
    assert math.isclose(obsSite.ts.now().tt, obsSite.timeJD.tt, abs_tol=1e-4)


def test_Site_timeJD_3():
    parent = Parent()
    parent.mountIsUp = False
    obsSite = ObsSite(parent)

    obsSite.timeJD = obsSite.ts.now().tt - 69.184 / 86400
    assert math.isclose(obsSite.ts.now().tt, obsSite.timeJD.tt, abs_tol=1e-4)


def test_timeDiff():
    obsSite = ObsSite(parent=Parent())
    obsSite._timeDiff = [10, 10, 10, 10, 10]
    obsSite.timeDiff = 20
    assert obsSite.timeDiff == 10


def test_Site_ut1_utc():
    obsSite = ObsSite(parent=Parent())

    obsSite.ut1_utc = "123.11"
    assert obsSite.ut1_utc == 123.11 / 86400


def test_Site_utc_ut2():
    obsSite = ObsSite(parent=Parent())

    obsSite.ut1_utc = None
    assert obsSite.ut1_utc == 0


def test_Site_timeSidereal_1():
    obsSite = ObsSite(parent=Parent())

    obsSite.timeSidereal = "12:30:00.00"
    assert obsSite.timeSidereal.hours == 12.5
    obsSite.timeSidereal = "12:aa:30.01"
    assert obsSite.timeSidereal.hours == 0
    obsSite.timeSidereal = ["12:aa:30.01"]
    assert obsSite.timeSidereal.hours == 0
    assert obsSite._timeSidereal.hours == 0
    obsSite.timeSidereal = 12.0
    assert obsSite.timeSidereal.hours == 12
    obsSite.timeSidereal = Angle(hours=12.0)
    assert obsSite.timeSidereal.hours == 12


def test_Site_ra():
    obsSite = ObsSite(parent=Parent())

    obsSite.raJNow = Angle(hours=34)
    assert obsSite.raJNow.hours == 34
    obsSite.raJNow = 34
    assert obsSite.raJNow.hours == 34
    assert obsSite._raJNow.hours == 34
    obsSite.raJNow = "34"
    assert obsSite.raJNow.hours == 34
    obsSite.raJNow = "34f"
    assert obsSite.raJNow.hours == 0


def test_Site_dec():
    obsSite = ObsSite(parent=Parent())

    obsSite.decJNow = Angle(degrees=34)
    assert obsSite.decJNow.degrees == 34
    obsSite.decJNow = 34
    assert obsSite.decJNow.degrees == 34
    assert obsSite._decJNow.degrees == 34
    obsSite.decJNow = "34"
    assert obsSite.decJNow.degrees == 34
    obsSite.decJNow = "34f"
    assert obsSite.decJNow.degrees == 0


def test_Site_alt():
    obsSite = ObsSite(parent=Parent())

    obsSite.Alt = Angle(degrees=34)
    assert obsSite.Alt.degrees == 34
    obsSite.Alt = 34
    assert obsSite.Alt.degrees == 34
    assert obsSite._Alt.degrees == 34
    obsSite.Alt = "34"
    assert obsSite.Alt.degrees == 34
    obsSite.Alt = "34f"
    assert obsSite.Alt.degrees == 0


def test_Site_az():
    obsSite = ObsSite(parent=Parent())

    obsSite.Az = Angle(degrees=34)
    assert obsSite.Az.degrees == 34
    obsSite.Az = 34
    assert obsSite.Az.degrees == 34
    assert obsSite._Az.degrees == 34
    obsSite.Az = "34"
    assert obsSite.Az.degrees == 34
    obsSite.Az = "34f"
    assert obsSite.Az.degrees == 0


def test_Site_pierside():
    obsSite = ObsSite(parent=Parent())

    obsSite.pierside = "E"
    assert obsSite.pierside == "E"
    obsSite.pierside = "e"
    assert obsSite.pierside == "E"
    obsSite.pierside = "w"
    assert obsSite.pierside == "W"
    assert obsSite._pierside == "W"
    obsSite.pierside = "W"
    assert obsSite.pierside == "W"
    obsSite.pierside = "WW"
    assert obsSite.pierside == "W"
    obsSite.pierside = "12"
    assert obsSite.pierside == "W"
    obsSite.pierside = 17
    assert obsSite.pierside == "W"


def test_Site_raTarget():
    obsSite = ObsSite(parent=Parent())

    obsSite.raJNowTarget = "*34:00:00.00"
    assert obsSite.raJNowTarget.hours == 34
    obsSite.raJNowTarget = 34
    assert obsSite.raJNowTarget.hours == 0
    assert obsSite._raJNowTarget.hours == 0
    obsSite.raJNowTarget = "34"
    assert obsSite.raJNowTarget.hours == 0
    obsSite.raJNowTarget = "34f"
    assert obsSite.raJNowTarget.hours == 0
    obsSite.raJNowTarget = Angle(hours=12)
    assert obsSite.raJNowTarget.hours == 12


def test_Site_haJNow_1():
    obsSite = ObsSite(parent=Parent())

    obsSite.timeSidereal = 12
    obsSite.raJNow = Angle(hours=12)
    obsSite.haJNow.hours == 0


def test_Site_haJNow_2():
    obsSite = ObsSite(parent=Parent())

    obsSite.timeSidereal = Angle(hours=12)
    obsSite.raJNow = Angle(hours=12)
    obsSite.haJNow.hours == Angle(hours=0)


def test_Site_haJNowTarget_1():
    obsSite = ObsSite(parent=Parent())

    obsSite.timeSidereal = 12
    obsSite.raJNowTarget = Angle(hours=12)
    obsSite.haJNowTarget is None


def test_Site_haJNowTarget_2():
    obsSite = ObsSite(parent=Parent())

    obsSite.timeSidereal = Angle(hours=12)
    obsSite.raJNowTarget = Angle(hours=12)
    obsSite.haJNowTarget.hours == 0


def test_Site_decTarget():
    obsSite = ObsSite(parent=Parent())

    obsSite.decJNowTarget = "*34:00:00.00"
    assert obsSite.decJNowTarget.degrees == 34
    obsSite.decJNowTarget = 34
    assert obsSite.decJNowTarget.degrees == 0
    assert obsSite._decJNowTarget.degrees == 0
    obsSite.decJNowTarget = "34"
    assert obsSite.decJNowTarget.degrees == 0
    obsSite.decJNowTarget = "34f"
    assert obsSite.decJNowTarget.degrees == 0
    obsSite.decJNowTarget = Angle(degrees=34)
    assert obsSite.decJNowTarget.degrees == 34


def test_Site_altTarget():
    obsSite = ObsSite(parent=Parent())

    obsSite.AltTarget = "*34:00:00.00"
    assert obsSite.AltTarget.degrees == 34
    obsSite.AltTarget = 34
    assert obsSite.AltTarget.degrees == 0
    obsSite.AltTarget = Angle(degrees=34)
    assert obsSite.AltTarget.degrees == 34
    assert obsSite._AltTarget.degrees == 34
    obsSite.AltTarget = "34"
    assert obsSite.AltTarget.degrees == 0
    obsSite.AltTarget = "34f"
    assert obsSite.AltTarget.degrees == 0


def test_Site_azTarget():
    obsSite = ObsSite(parent=Parent())

    obsSite.AzTarget = "*34:00:00.00"
    assert obsSite.AzTarget.degrees == 34
    obsSite.AzTarget = 34
    assert obsSite.AzTarget.degrees == 0
    obsSite.AzTarget = Angle(degrees=34)
    assert obsSite.AzTarget.degrees == 34
    assert obsSite._AzTarget.degrees == 34
    obsSite.AzTarget = "34"
    assert obsSite.AzTarget.degrees == 0
    obsSite.AzTarget = "34f"
    assert obsSite.AzTarget.degrees == 0


def test_angularPosRA_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.angularPosRA = 12
    assert obsSite.angularPosRA.degrees == 12


def test_angularPosRA_2():
    obsSite = ObsSite(parent=Parent())
    obsSite.angularPosRA = Angle(degrees=12)
    assert obsSite.angularPosRA.degrees == 12


def test_angularPosDEC_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.angularPosDEC = 12
    assert obsSite.angularPosDEC.degrees == 12


def test_angularPosDEC_2():
    obsSite = ObsSite(parent=Parent())
    obsSite.angularPosDEC = Angle(degrees=12)
    assert obsSite.angularPosDEC.degrees == 12


def test_errorAngularPosRA_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.errorAngularPosRA = 12
    assert obsSite.errorAngularPosRA.degrees == 12


def test_errorAngularPosRA_2():
    obsSite = ObsSite(parent=Parent())
    obsSite.errorAngularPosRA = Angle(degrees=12)
    assert obsSite.errorAngularPosRA.degrees == 12


def test_errorAngularPosDEC_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.errorAngularPosDEC = 12
    assert obsSite.errorAngularPosDEC.degrees == 12


def test_errorAngularPosDEC_2():
    obsSite = ObsSite(parent=Parent())
    obsSite.errorAngularPosDEC = Angle(degrees=12)
    assert obsSite.errorAngularPosDEC.degrees == 12


def test_angularPosRATarget_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.angularPosRATarget = 12
    assert obsSite.angularPosRATarget.degrees == 12


def test_angularPosRATarget_2():
    obsSite = ObsSite(parent=Parent())
    obsSite.angularPosRATarget = Angle(degrees=12)
    assert obsSite.angularPosRATarget.degrees == 12


def test_angularPosDECTarget_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.angularPosDECTarget = 12
    assert obsSite.angularPosDECTarget.degrees == 12


def test_angularPosDECTarget_2():
    obsSite = ObsSite(parent=Parent())
    obsSite.angularPosDECTarget = Angle(degrees=12)
    assert obsSite.angularPosDECTarget.degrees == 12


def test_Site_piersideTarget():
    obsSite = ObsSite(parent=Parent())

    obsSite.piersideTarget = 2
    assert obsSite.piersideTarget == "W"
    obsSite.piersideTarget = 3
    assert obsSite.piersideTarget == "E"
    obsSite.piersideTarget = 0
    assert obsSite.piersideTarget == "E"
    obsSite.piersideTarget = 2
    assert obsSite.piersideTarget == "W"
    obsSite.piersideTarget = 3
    assert obsSite.piersideTarget == "E"


def test_Site_status():
    obsSite = ObsSite(parent=Parent())

    obsSite.status = "1"
    assert obsSite.status == 1
    obsSite.status = "1d"
    assert obsSite.status == 0
    obsSite.status = "1d"
    assert obsSite.status == 0
    obsSite.status = "0"
    assert obsSite.status == 0
    obsSite.status = "100"
    assert obsSite.status == 99


def test_status_1():
    obsSite = ObsSite(parent=Parent())

    obsSite.status = None
    assert obsSite.status == 0


def test_status_2():
    obsSite = ObsSite(parent=Parent())

    obsSite.status = "E"
    assert obsSite.status == 0


def test_status_3():
    obsSite = ObsSite(parent=Parent())

    obsSite.status = "5"
    assert obsSite.status == 5


def test_status_isTracking():
    obsSite = ObsSite(parent=Parent())
    obsSite.status = "0"
    assert obsSite.isTracking is True
    obsSite.status = "5"
    assert obsSite.isTracking is False


def test_status_isStopped():
    obsSite = ObsSite(parent=Parent())
    obsSite.status = "1"
    assert obsSite.isStopped is True
    obsSite.status = "0"
    assert obsSite.isStopped is False


def test_status_isParked():
    obsSite = ObsSite(parent=Parent())
    obsSite.status = "5"
    assert obsSite.isParked is True
    obsSite.status = "0"
    assert obsSite.isParked is False


def test_status_isFollowingSatellite():
    obsSite = ObsSite(parent=Parent())
    obsSite.status = "10"
    assert obsSite.isFollowingSatellite is True
    obsSite.status = "0"
    assert obsSite.isFollowingSatellite is False


def test_Site_statusText_2():
    obsSite = ObsSite(parent=Parent())

    obsSite.status = "1"
    assert obsSite.statusText() == "stopped after STOP"


def test_Site_statusText_3():
    obsSite = ObsSite(parent=Parent())

    obsSite.status = "2"
    assert obsSite.statusText() == "slewing park position"


def test_statusSat_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.statusSat = 1
    assert obsSite.statusSat == "E"


def test_statusSat_2():
    obsSite = ObsSite(parent=Parent())
    obsSite.statusSat = "V"
    assert obsSite.statusSat == "V"


def test_statusSatText_1():
    obsSite = ObsSite(parent=Parent())
    obsSite.statusSat = "V"
    assert obsSite.statusSatText() == "slewing to transit"


def test_Site_statusSlew():
    obsSite = ObsSite(parent=Parent())

    obsSite.statusSlew = "1"
    assert obsSite.statusSlew
    obsSite.statusSlew = 1
    assert obsSite.statusSlew
    assert obsSite._statusSlew
    obsSite.statusSlew = True
    assert obsSite.statusSlew
    obsSite.statusSlew = False
    assert not obsSite.statusSlew
    obsSite.statusSlew = "True"
    assert obsSite.statusSlew
    obsSite.statusSlew = "100"
    assert obsSite.statusSlew
    obsSite.statusSlew = "-100"
    assert obsSite.statusSlew
    obsSite.statusSlew = ""
    assert not obsSite.statusSlew
    obsSite.statusSlew = (0, 0)
    assert obsSite.statusSlew


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

    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 4
        suc = obsSite.getLocation()
        assert suc


def test_ObsSite_poll_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "-011:35:00.0", "+48:07:00.0", "03"]

    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 4
        suc = obsSite.getLocation()
        assert not suc


def test_ObsSite_poll_not_ok2():
    obsSite = ObsSite(parent=Parent())

    response = ["+0585.2", "-011:35:00.0", "+48:07:00.0", "03"]

    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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


def test_ObsSite_pollPointing_ok4():
    obsSite = ObsSite(parent=Parent())

    response = [
        "13:15:35.68",
        "0.12",
        "V",
        "19.44591,+88.0032,W,002.9803,+47.9945,2458352.10403639,5,0",
        "2458352.10403639, 100, 100, 0.1, 0.1",
    ]

    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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

    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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

    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 5
        suc = obsSite.pollPointing()
        assert not suc


def test_pollSyncClock_1():
    obsSite = ObsSite(parent=Parent())
    with (
        mock.patch.object(platform, "system", return_value="Windows"),
        mock.patch.object(
            mw4.mountcontrol.obsSite.Connection, "communicate", return_value=(False, [], 0)
        ),
    ):
        suc = obsSite.pollSyncClock()
        assert not suc


def test_pollSyncClock_2():
    obsSite = ObsSite(parent=Parent())
    with (
        mock.patch.object(platform, "system", return_value="Linux"),
        mock.patch.object(
            mw4.mountcontrol.obsSite.Connection, "communicate", return_value=(False, [], 0)
        ),
    ):
        suc = obsSite.pollSyncClock()
        assert not suc


def test_pollSyncClock_3():
    obsSite = ObsSite(parent=Parent())
    with (
        mock.patch.object(platform, "system", return_value="aarch64"),
        mock.patch.object(
            mw4.mountcontrol.obsSite.Connection, "communicate", return_value=(False, [], 0)
        ),
    ):
        suc = obsSite.pollSyncClock()
        assert not suc


def test_pollSyncClock_4():
    obsSite = ObsSite(parent=Parent())
    with (
        mock.patch.object(platform, "system", return_value="Darwin"),
        mock.patch.object(
            mw4.mountcontrol.obsSite.Connection, "communicate", return_value=(True, ["eee"], 1)
        ),
    ):
        suc = obsSite.pollSyncClock()
        assert suc


def test_pollSyncClock_5():
    obsSite = ObsSite(parent=Parent())
    with (
        mock.patch.object(platform, "system", return_value="Darwin"),
        mock.patch.object(
            mw4.mountcontrol.obsSite.Connection,
            "communicate",
            return_value=(True, ["12345678.1"], 1),
        ),
    ):
        suc = obsSite.pollSyncClock()
        assert suc


def test_adjustClock_1():
    obsSite = ObsSite(parent=Parent())
    with mock.patch.object(
        mw4.mountcontrol.obsSite.Connection,
        "communicate",
        return_value=(False, ["0"], 1),
    ):
        suc = obsSite.adjustClock(0)
        assert not suc


def test_startSlewing_1_1():
    obsSite = ObsSite(parent=Parent())
    response = "1#"

    obsSite.status = 0
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = obsSite.startSlewing(slewType="keep")
        assert not suc


def test_startSlewing_1_2():
    obsSite = ObsSite(parent=Parent())
    response = "1#"

    obsSite.status = 1
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = obsSite.startSlewing(slewType="keep")
        assert not suc


def test_startSlewing_3():
    obsSite = ObsSite(parent=Parent())
    response = "1#"

    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 3
        suc = obsSite.startSlewing(slewType="normal")
        assert not suc


def test_startSlewing_4():
    obsSite = ObsSite(parent=Parent())
    response = "0#"

    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.startSlewing(slewType="normal")
        assert suc


def test_ObsSite_setTargetAltAz_ok1():
    obsSite = ObsSite(parent=Parent())
    response = ["112+45:00:00.0", "180:00:00.0", "12:30:00.00", "+45:30:00.0"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 7
        suc = obsSite.setTargetAltAz(Angle(degrees=0), Angle(degrees=0))
        assert suc


def test_ObsSite_setTargetAltAz_not_ok3():
    obsSite = ObsSite(parent=Parent())
    response = ["00"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


def test_ObsSite_setTargetAltAz_not_ok4():
    obsSite = ObsSite(parent=Parent())
    response = ["00"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


def test_ObsSite_setTargetAltAz_not_ok5():
    obsSite = ObsSite(parent=Parent())
    response = ["0"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


def test_ObsSite_setTargetAltAz_not_ok6():
    obsSite = ObsSite(parent=Parent())
    response = ["1#2"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        alt = Angle(degrees=30)
        az = Angle(degrees=30)
        suc = obsSite.setTargetAltAz(alt, az)
        assert not suc


def test_ObsSite_setTargetAltAz_not_ok7():
    obsSite = ObsSite(parent=Parent())

    response = ["1#2"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert suc


def test_ObsSite_setTargetRaDec_not_ok5():
    obsSite = ObsSite(parent=Parent())

    response = ["00"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


def test_ObsSite_setTargetRaDec_not_ok6():
    obsSite = ObsSite(parent=Parent())

    response = ["00"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


def test_ObsSite_setTargetRaDec_not_ok7():
    obsSite = ObsSite(parent=Parent())

    response = ["0"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


def test_ObsSite_setTargetRaDec_not_ok8():
    obsSite = ObsSite(parent=Parent())

    response = ["1#"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 2
        ra = Angle(hours=5, preference="hours")
        dec = Angle(degrees=30)
        suc = obsSite.setTargetRaDec(ra, dec)
        assert not suc


def test_ObsSite_setTargetRaDec_not_ok9():
    obsSite = ObsSite(parent=Parent())

    response = ["1#"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.setLocation(observer)
        assert suc


def test_ObsSite_setLatitude_ok2():
    obsSite = ObsSite(parent=Parent())
    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.setLatitude(lat=Angle(degrees=50))
        assert suc


def test_ObsSite_setLongitude_ok2():
    obsSite = ObsSite(parent=Parent())
    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.setLongitude(lon=Angle(degrees=50))
        assert suc


def test_ObsSite_setElevation_ok1():
    obsSite = ObsSite(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.startTracking()
        assert suc


def test_ObsSite_startTracking_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopTracking()
        assert suc


def test_ObsSite_stopTracking_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.park()
        assert suc


def test_ObsSite_park_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.unpark()
        assert suc


def test_ObsSite_unpark_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stop()
        assert suc


def test_ObsSite_stop_not_ok1():
    obsSite = ObsSite(parent=Parent())

    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
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
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 1
        suc = obsSite.flip()
        assert suc


def test_moveNorth_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.moveNorth()
        assert not suc


def test_moveNorth_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.moveNorth()
        assert suc


def test_moveEast_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.moveEast()
        assert not suc


def test_moveEast_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.moveEast()
        assert suc


def test_moveSouth_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.moveSouth()
        assert not suc


def test_moveSouth_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.moveSouth()
        assert suc


def test_moveWest_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.moveWest()
        assert not suc


def test_moveWest_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.moveWest()
        assert suc


def test_stopMoveNorth_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveNorth()
        assert not suc


def test_stopMoveNorth_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveNorth()
        assert suc


def test_stopMoveEast_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveEast()
        assert not suc


def test_stopMoveEast_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveEast()
        assert suc


def test_stopMoveSouth_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveSouth()
        assert not suc


def test_stopMoveSouth_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveSouth()
        assert suc


def test_stopMoveWest_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveWest()
        assert not suc


def test_stopMoveWest_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveWest()
        assert suc


def test_stopMoveAll_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.stopMoveAll()
        assert not suc


def test_stopMoveAll_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.stopMoveAll()
        assert suc


def test_syncPositionToTarget_1():
    obsSite = ObsSite(parent=Parent())
    response = ["0", ""]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.syncPositionToTarget()
        assert not suc


def test_syncPositionToTarget_2():
    obsSite = ObsSite(parent=Parent())
    response = ["1", "Coordinates"]
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.syncPositionToTarget()
        assert suc


def test_setHighPrecision_1():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = obsSite.setHighPrecision()
        assert not suc


def test_setHighPrecision_2():
    obsSite = ObsSite(parent=Parent())
    response = []
    with mock.patch("mw4.mountcontrol.obsSite.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = obsSite.setHighPrecision()
        assert suc
