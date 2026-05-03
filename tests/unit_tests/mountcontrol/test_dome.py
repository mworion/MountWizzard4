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
from mw4.mountcontrol.dome import Dome
from skyfield.api import Angle


def test_property_1():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    dome.shutterState = "1"
    dome.flapState = "1"
    dome.slew = "1"
    dome.azimuth = "1800"

    assert dome.shutterState == 1
    assert dome.flapState == 1
    assert dome.slew
    assert dome.azimuth == 180


def test_property_2():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    dome.shutterState = "-1"
    dome.flapState = "-1"
    dome.slew = "-1"
    dome.azimuth = "5400"

    assert dome.slew
    assert dome.azimuth == 180


def test_property_3():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    dome.shutterState = "5"
    dome.flapState = "5"
    dome.slew = "e"
    dome.azimuth = "e"


def test_property_4():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    dome.shutterState = "e"
    dome.flapState = "e"


def test_Dome_parse_1():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["0", "0", "0", "1800"]
    suc = dome.parse(response, 4)
    assert suc
    assert dome.shutterState == 0
    assert dome.flapState == 0
    assert not dome.slew
    assert dome.azimuth == 180


def test_Dome_parse_2():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1", "2", "1", "5400"]
    suc = dome.parse(response, 4)
    assert suc
    assert dome.shutterState == 1
    assert dome.flapState == 2
    assert dome.slew
    assert dome.azimuth == 180


def test_Dome_parse_3():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1", "2", "1"]
    suc = dome.parse(response, 4)
    assert not suc


def test_Dome_parse_4():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["e", "e", "e", "e"]
    suc = dome.parse(response, 4)
    assert suc


def test_Dome_parse_5():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["5", "-1", "1", "5400"]
    suc = dome.parse(response, 4)
    assert suc
    assert dome.slew


def test_Dome_poll_1():
    class Parent:
        host = None

    dome = Dome(parent=Parent())
    response = ["0", "0", "0", "1800"]

    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 4
        suc = dome.poll()
        assert not suc


def test_Dome_poll_2():
    class Parent:
        host = None

    dome = Dome(parent=Parent())
    response = ["0", "0", "0", "1800"]

    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 4
        suc = dome.poll()
        assert suc


def test_openShutter_1():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = dome.openShutter()
        assert not suc


def test_openShutter_3():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = dome.openShutter()
        assert suc


def test_closeShutter_1():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = dome.closeShutter()
        assert not suc


def test_closeShutter_3():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = dome.closeShutter()
        assert suc


def test_openFlap_1():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = dome.openFlap()
        assert not suc


def test_openFlap_3():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = dome.openFlap()
        assert suc


def test_closeFlap_1():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = dome.closeFlap()
        assert not suc


def test_closeFlap_3():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = dome.closeFlap()
        assert suc


def test_slewDome_2():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 1
        suc = dome.slewDome(azimuth=Angle(degrees=100))
        assert not suc


def test_enableInternalDomeControl_1():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["1"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 0
        suc = dome.enableInternalDomeControl()
        assert not suc


def test_enableInternalDomeControl_2():
    class Parent:
        host = None

    dome = Dome(parent=Parent())

    response = ["0"]
    with mock.patch("mw4.mountcontrol.dome.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 0
        suc = dome.enableInternalDomeControl()
        assert suc
