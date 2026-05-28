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
import unittest.mock as mock
from mw4.mountcontrol.firmware import Firmware
from packaging.version import Version

#
#
# testing Firmware class attributes
#
#


def test_Firmware_ok():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    fw.vString = "2.15.08"
    assert fw.vString == Version("2.15.08")
    assert fw._vString == Version("2.15.08")
    fw.vString = "2.16"
    assert fw.vString == Version("2.16")
    assert fw._vString == Version("2.16")
    fw.vString = "3.0"
    assert fw.vString == Version("3.0")
    assert fw._vString == Version("3.0")


def test_Firmware_checkNewer_2():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    fw.vString = "2.99.99"
    suc = fw.checkNewer("3")
    assert not suc


def test_Firmware_checkNewer_3():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    fw.vString = "2.99.99"
    suc = fw.checkNewer("2.99.98")
    assert suc


def test_isHW2024_1():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    fw.hardware = "Q-TYPE2024"
    suc = fw.isHW2024()
    assert suc
    suc = fw.isHW2012()
    assert not suc


def test_isHW2012_1():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    fw.hardware = "Q-TYPE2012"
    suc = fw.isHW2012()
    assert suc
    suc = fw.isHW2024()
    assert not suc


#
#
# testing parse
#
#


def test_Firmware_parse_empty():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    # connection returns 0 chunks but parse expects 5
    suc = fw.parse([], 5)
    assert not suc


def test_Firmware_parse_chunks_4():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    # connection returns 4 chunks but parse expects 5
    response = ["Mar 19 2018", "2.15.14", "10micron GM1000HPS", "15:56:53"]
    suc = fw.parse(response, 5)
    assert not suc


def test_Firmware_parse_chunks_5():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    response = [
        "Mar 19 2018",
        "2.15.14",
        "10micron GM1000HPS",
        "15:56:53",
        "Q-TYPE2012",
    ]
    suc = fw.parse(response, 5)
    assert suc
    assert fw.date == "Mar 19 2018"
    assert fw.vString == Version("2.15.14")
    assert fw.product == "10micron GM1000HPS"
    assert fw.time == "15:56:53"
    assert fw.hardware == "Q-TYPE2012"


def test_Firmware_parse_chunks_6():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())
    # connection returns 6 chunks but parse expects 5
    response = [
        "Mar 19 2018",
        "2.15.14",
        "10micron GM1000HPS",
        "15:56:53",
        "Q-TYPE2012",
        "A,G,N,H",
    ]
    suc = fw.parse(response, 5)
    assert not suc


#
#
# testing poll
#
#


def test_Firmware_poll_ok():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())

    response = [
        "Mar 19 2018",
        "2.15.14",
        "10micron GM1000HPS",
        "15:56:53",
        "Q-TYPE2012",
    ]

    with mock.patch("mw4.mountcontrol.firmware.Connection") as mConn:
        mConn.return_value.communicate.return_value = True, response, 5
        suc = fw.poll()
        assert suc


def test_Firmware_poll_not_ok1():
    class Parent:
        host = None

    fw = Firmware(parent=Parent())

    response = [
        "Mar 19 2018",
        "2.15.14",
        "10micron GM1000HPS",
        "15:56:53",
        "Q-TYPE2012",
    ]

    with mock.patch("mw4.mountcontrol.firmware.Connection") as mConn:
        mConn.return_value.communicate.return_value = False, response, 5
        suc = fw.poll()
        assert not suc
