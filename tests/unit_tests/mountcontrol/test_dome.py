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
from skyfield.api import Angle

# local imports
from mountcontrol.dome import Dome


class TestConfigData(unittest.TestCase):

    def setUp(self):
        pass

    def test_property_1(self):
        dome = Dome()

        dome.shutterState = '1'
        dome.flapState = '1'
        dome.slew = '1'
        dome.azimuth = '1800'

        self.assertEqual(dome.shutterState, 1)
        self.assertEqual(dome.flapState, 1)
        self.assertEqual(dome.slew, True)
        self.assertEqual(dome.azimuth, 180)

    def test_property_2(self):
        dome = Dome()

        dome.shutterState = '-1'
        dome.flapState = '-1'
        dome.slew = '-1'
        dome.azimuth = '5400'

        self.assertEqual(dome.shutterState, None)
        self.assertEqual(dome.flapState, None)
        self.assertEqual(dome.slew, True)
        self.assertEqual(dome.azimuth, 180)

    def test_property_3(self):
        dome = Dome()

        dome.shutterState = '5'
        dome.flapState = '5'
        dome.slew = 'e'
        dome.azimuth = 'e'

        self.assertEqual(dome.shutterState, None)
        self.assertEqual(dome.flapState, None)
        self.assertEqual(dome.slew, None)
        self.assertEqual(dome.azimuth, None)

    def test_property_4(self):
        dome = Dome()

        dome.shutterState = 'e'
        dome.flapState = 'e'

        self.assertEqual(dome.shutterState, None)
        self.assertEqual(dome.flapState, None)

    def test_Firmware_parse_1(self):
        dome = Dome()

        response = ['0', '0', '0', '1800']
        suc = dome.parse(response, 4)
        self.assertEqual(True, suc)
        self.assertEqual(dome.shutterState, 0)
        self.assertEqual(dome.flapState, 0)
        self.assertEqual(dome.slew, False)
        self.assertEqual(dome.azimuth, 180)

    def test_Firmware_parse_2(self):
        dome = Dome()

        response = ['1', '2', '1', '5400']
        suc = dome.parse(response, 4)
        self.assertEqual(True, suc)
        self.assertEqual(dome.shutterState, 1)
        self.assertEqual(dome.flapState, 2)
        self.assertEqual(dome.slew, True)
        self.assertEqual(dome.azimuth, 180)

    def test_Firmware_parse_3(self):
        dome = Dome()

        response = ['1', '2', '1']
        suc = dome.parse(response, 4)
        self.assertEqual(False, suc)

    def test_Firmware_parse_4(self):
        dome = Dome()

        response = ['e', 'e', 'e', 'e']
        suc = dome.parse(response, 4)
        self.assertEqual(True, suc)
        self.assertEqual(dome.shutterState, 1)
        self.assertEqual(dome.flapState, 2)
        self.assertEqual(dome.slew, True)
        self.assertEqual(dome.azimuth, 180)

    def test_Firmware_parse_4(self):
        dome = Dome()

        response = ['5', '-1', '1', '5400']
        suc = dome.parse(response, 4)
        self.assertEqual(True, suc)
        self.assertEqual(dome.shutterState, None)
        self.assertEqual(dome.flapState, None)
        self.assertEqual(dome.slew, True)

    def test_Firmware_poll_1(self):
        dome = Dome()
        response = ['0', '0', '0', '1800']

        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 4
            suc = dome.poll()
            self.assertEqual(False, suc)

    def test_Firmware_poll_2(self):
        dome = Dome()
        response = ['0', '0', '0', '1800']

        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 4
            suc = dome.poll()
            self.assertEqual(True, suc)

    def test_openShutter_1(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.openShutter()
            self.assertEqual(False, suc)

    def test_openShutter_2(self):
        dome = Dome()

        response = ['0']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.openShutter()
            self.assertEqual(False, suc)

    def test_openShutter_3(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.openShutter()
            self.assertEqual(True, suc)

    def test_closeShutter_1(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.closeShutter()
            self.assertEqual(False, suc)

    def test_closeShutter_2(self):
        dome = Dome()

        response = ['0']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.closeShutter()
            self.assertEqual(False, suc)

    def test_closeShutter_3(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.closeShutter()
            self.assertEqual(True, suc)

    def test_openFlap_1(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.openFlap()
            self.assertEqual(False, suc)

    def test_openFlap_2(self):
        dome = Dome()

        response = ['0']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.openFlap()
            self.assertEqual(False, suc)

    def test_openFlap_3(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.openFlap()
            self.assertEqual(True, suc)

    def test_closeFlap_1(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.closeFlap()
            self.assertEqual(False, suc)

    def test_closeFlap_2(self):
        dome = Dome()

        response = ['0']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.closeFlap()
            self.assertEqual(False, suc)

    def test_closeFlap_3(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.closeFlap()
            self.assertEqual(True, suc)

    def test_slewDome_1(self):
        dome = Dome()

        suc = dome.slewDome()
        self.assertEqual(False, suc)

    def test_slewDome_2(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 1
            suc = dome.slewDome(azimuth=Angle(degrees=100))
            self.assertEqual(False, suc)

    def test_slewDome_3(self):
        dome = Dome()

        response = ['0']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = dome.slewDome(azimuth=100)
            self.assertEqual(False, suc)

    def test_slewDome_4(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 1
            suc = dome.slewDome(azimuth=100)
            self.assertEqual(True, suc)

    def test_enableInternalDomeControl_1(self):
        dome = Dome()

        response = ['1']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = False, response, 0
            suc = dome.enableInternalDomeControl()
            self.assertEqual(False, suc)

    def test_enableInternalDomeControl_2(self):
        dome = Dome()

        response = ['0']
        with mock.patch('mountcontrol.dome.Connection') as mConn:
            mConn.return_value.communicate.return_value = True, response, 0
            suc = dome.enableInternalDomeControl()
            self.assertEqual(True, suc)
