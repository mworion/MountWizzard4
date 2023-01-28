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
from mountcontrol.firmware import Firmware


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass
    #
    #
    # testing firmware class it's attribute
    #
    #

    def test_Firmware_ok(self):
        fw = Firmware()

        fw.product = 'Test'
        self.assertEqual('Test', fw.product)
        self.assertEqual('Test', fw._product)
        fw.vString = '2.15.08'
        self.assertEqual('2.15.08', fw.vString)
        self.assertEqual('2.15.08', fw._vString)
        self.assertEqual(fw.number(), 21508)
        fw.vString = '2.16'
        self.assertEqual('2.16', fw.vString)
        self.assertEqual('2.16', fw._vString)
        self.assertEqual(fw.number(), 21600)
        fw.vString = '3.0'
        self.assertEqual('3.0', fw.vString)
        self.assertEqual('3.0', fw._vString)
        self.assertEqual(fw.number(), 30000)
        fw.hardware = '4.5'
        self.assertEqual('4.5', fw.hardware)
        self.assertEqual('4.5', fw._hardware)
        fw.date = '2018-07-08'
        self.assertEqual('2018-07-08', fw.date)
        self.assertEqual('2018-07-08', fw._date)
        fw.time = '14:50'
        self.assertEqual('14:50', fw.time)
        self.assertEqual('14:50', fw._time)
        self.assertEqual(True, fw.checkNewer(10000))

    def test_Firmware_not_ok_vString(self):
        fw = Firmware()

        fw.vString = '21508'
        self.assertEqual(None, fw.vString)
        fw.vString = '2.ee.15'
        self.assertEqual(None, fw.vString)
        fw.vString = ''
        self.assertEqual(None, fw.vString)
        fw._vString = '2.ee.15'
        self.assertEqual(None, fw.number())
        fw._vString = '2.16.16.15'
        self.assertEqual(None, fw.number())

    def test_Firmware_checkNewer_1(self):
        fw = Firmware()
        fw.vString = 5
        self.assertEqual(None, fw.checkNewer(100))

    def test_Firmware_checkNewer_2(self):
        fw = Firmware()
        fw.vString = '2.99.99'
        suc = fw.checkNewer(30000)
        assert not suc

    def test_Firmware_checkNewer_3(self):
        fw = Firmware()
        fw.vString = '2.99.99'
        suc = fw.checkNewer(29998)
        assert suc
    #
    #
    # testing pollSetting
    #
    #

    def test_Firmware_parse_ok1(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']
        suc = fw.parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_ok2(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']
        suc = fw.parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_not_ok1(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53']
        suc = fw.parse(response, 5)
        self.assertEqual(False, suc)

    def test_Firmware_parse_not_ok2(self):
        fw = Firmware()

        response = []
        suc = fw.parse(response, 5)
        self.assertEqual(False, suc)

    def test_Firmware_parse_not_ok3(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        suc = fw.parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_not_ok4(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.1514',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        suc = fw.parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_not_ok5(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        suc = fw.parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_parse_not_ok6(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        suc = fw.parse(response, 5)
        self.assertEqual(True, suc)

    def test_Firmware_poll_ok(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        with mock.patch('mountcontrol.firmware.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 5
            suc = fw.poll()
            self.assertEqual(True, suc)

    def test_Firmware_poll_not_ok1(self):
        fw = Firmware()

        response = ['Mar 19 2018', '2.15.14',
                    '10micron GM1000HPS', '15:56:53', 'Q-TYPE2012']

        with mock.patch('mountcontrol.firmware.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 5
            suc = fw.poll()
            self.assertEqual(False, suc)
