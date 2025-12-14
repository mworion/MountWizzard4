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
from mw4.mountcontrol.firmware import Firmware
from packaging.version import Version


class TestConfigData(unittest.TestCase):
    def setUp(self):
        pass

    #
    #
    # testing firmware class it's attribute
    #
    #

    def test_Firmware_ok(self):
        class Parent:
            host = None

        fw = Firmware(parent=Parent())

        fw.product = "Test"
        self.assertEqual("Test", fw.product)
        self.assertEqual("Test", fw._product)
        fw.vString = "2.15.08"
        self.assertEqual(Version("2.15.08"), fw.vString)
        self.assertEqual(Version("2.15.08"), fw._vString)
        fw.vString = "2.16"
        self.assertEqual(Version("2.16"), fw.vString)
        self.assertEqual(Version("2.16"), fw._vString)
        fw.vString = "3.0"
        self.assertEqual(Version("3.0"), fw.vString)
        self.assertEqual(Version("3.0"), fw._vString)
        fw.hardware = "4.5"
        self.assertEqual("4.5", fw.hardware)
        self.assertEqual("4.5", fw._hardware)
        fw.date = "2018-07-08"
        self.assertEqual("2018-07-08", fw.date)
        self.assertEqual("2018-07-08", fw._date)
        fw.time = "14:50"
        self.assertEqual("14:50", fw.time)
        self.assertEqual("14:50", fw._time)

    def test_Firmware_checkNewer_2(self):
        class Parent:
            host = None

        fw = Firmware(parent=Parent())
        fw.vString = "2.99.99"
        suc = fw.checkNewer("3")
        assert not suc

    def test_Firmware_checkNewer_3(self):
        class Parent:
            host = None

        fw = Firmware(parent=Parent())
        fw.vString = "2.99.99"
        suc = fw.checkNewer("2.99.98")
        assert suc

    #
    #
    # testing pollSetting
    #
    #

    def test_Firmware_parse_ok1(self):
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
        self.assertTrue(suc)

    def test_Firmware_parse_ok2(self):
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
        self.assertTrue(suc)

    def test_Firmware_parse_not_ok1(self):
        class Parent:
            host = None

        fw = Firmware(parent=Parent())

        response = ["Mar 19 2018", "2.15.14", "10micron GM1000HPS", "15:56:53"]
        suc = fw.parse(response, 5)
        self.assertFalse(suc)

    def test_Firmware_parse_not_ok2(self):
        class Parent:
            host = None

        fw = Firmware(parent=Parent())

        response = []
        suc = fw.parse(response, 5)
        self.assertFalse(suc)

    def test_Firmware_parse_not_ok3(self):
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
        self.assertTrue(suc)

    def test_Firmware_parse_not_ok4(self):
        class Parent:
            host = None

        fw = Firmware(parent=Parent())

        response = [
            "Mar 19 2018",
            "2.1514",
            "10micron GM1000HPS",
            "15:56:53",
            "Q-TYPE2012",
        ]

        suc = fw.parse(response, 5)
        self.assertTrue(suc)

    def test_Firmware_parse_not_ok5(self):
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
        self.assertTrue(suc)

    def test_Firmware_parse_not_ok6(self):
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
        self.assertTrue(suc)

    def test_Firmware_poll_ok(self):
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
            self.assertTrue(suc)

    def test_Firmware_poll_not_ok1(self):
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
            self.assertFalse(suc)
