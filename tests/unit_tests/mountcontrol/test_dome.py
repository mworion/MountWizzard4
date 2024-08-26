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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest
import unittest.mock as mock

# external packages
from skyfield.api import Angle

# local imports
from mountcontrol.dome import Dome


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    def test_property_1(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        dome.shutterState = '1'
        dome.flapState = '1'
        dome.slew = '1'
        dome.azimuth = '1800'

        self.assertEqual(dome.shutterState, 1)
        self.assertEqual(dome.flapState, 1)
        self.assertTrue(dome.slew)
        self.assertEqual(dome.azimuth, 180)

    def test_property_2(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        dome.shutterState = '-1'
        dome.flapState = '-1'
        dome.slew = '-1'
        dome.azimuth = '5400'

        self.assertIsNone(dome.shutterState)
        self.assertIsNone(dome.flapState)
        self.assertTrue(dome.slew)
        self.assertEqual(dome.azimuth, 180)

    def test_property_3(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        dome.shutterState = '5'
        dome.flapState = '5'
        dome.slew = 'e'
        dome.azimuth = 'e'

        self.assertIsNone(dome.shutterState)
        self.assertIsNone(dome.flapState)
        self.assertIsNone(dome.slew)
        self.assertIsNone(dome.azimuth)

    def test_property_4(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        dome.shutterState = 'e'
        dome.flapState = 'e'

        self.assertIsNone(dome.shutterState)
        self.assertIsNone(dome.flapState)

    def test_Dome_parse_1(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['0', '0', '0', '1800']
        suc = dome.parse(response, 4)
        self.assertTrue(suc)
        self.assertEqual(dome.shutterState, 0)
        self.assertEqual(dome.flapState, 0)
        self.assertFalse(dome.slew)
        self.assertEqual(dome.azimuth, 180)

    def test_Dome_parse_2(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1', '2', '1', '5400']
        suc = dome.parse(response, 4)
        self.assertTrue(suc)
        self.assertEqual(dome.shutterState, 1)
        self.assertEqual(dome.flapState, 2)
        self.assertTrue(dome.slew)
        self.assertEqual(dome.azimuth, 180)

    def test_Dome_parse_3(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1', '2', '1']
        suc = dome.parse(response, 4)
        self.assertFalse(suc)

    def test_Dome_parse_4(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['e', 'e', 'e', 'e']
        suc = dome.parse(response, 4)
        self.assertTrue(suc)
        self.assertIsNone(dome.shutterState)
        self.assertIsNone(dome.flapState)
        self.assertIsNone(dome.slew)
        self.assertIsNone(dome.azimuth)

    def test_Dome_parse_5(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['5', '-1', '1', '5400']
        suc = dome.parse(response, 4)
        self.assertTrue(suc)
        self.assertIsNone(dome.shutterState)
        self.assertIsNone(dome.flapState)
        self.assertTrue(dome.slew)

    def test_Dome_poll_1(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())
        response = ['0', '0', '0', '1800']

        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 4
            suc = dome.poll()
            self.assertFalse(suc)

    def test_Dome_poll_2(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())
        response = ['0', '0', '0', '1800']

        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 4
            suc = dome.poll()
            self.assertTrue(suc)

    def test_openShutter_1(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.openShutter()
            self.assertFalse(suc)

    def test_openShutter_3(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.openShutter()
            self.assertTrue(suc)

    def test_closeShutter_1(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.closeShutter()
            self.assertFalse(suc)

    def test_closeShutter_3(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.closeShutter()
            self.assertTrue(suc)

    def test_openFlap_1(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.openFlap()
            self.assertFalse(suc)

    def test_openFlap_3(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.openFlap()
            self.assertTrue(suc)

    def test_closeFlap_1(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.closeFlap()
            self.assertFalse(suc)

    def test_closeFlap_3(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.closeFlap()
            self.assertTrue(suc)

    def test_slewDome_2(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = dome.slewDome(azimuth=Angle(degrees=100))
            self.assertFalse(suc)

    def test_enableInternalDomeControl_1(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.enableInternalDomeControl()
            self.assertFalse(suc)

    def test_enableInternalDomeControl_2(self):
        class Parent:
            host = None
        dome = Dome(parent=Parent())

        response = ['0']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.enableInternalDomeControl()
            self.assertTrue(suc)
