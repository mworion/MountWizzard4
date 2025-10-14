############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest

# external packages
from skyfield.api import load

from mw4.base.loggerMW import setupLogging

# local imports
from mw4.mountcontrol.trajectoryParams import TrajectoryParams

setupLogging()


class TestConfigData(unittest.TestCase):
    def setUp(self):
        pass

    def test_TP_flip_1(self):
        trajectoryParams = TrajectoryParams()
        trajectoryParams.flip = None
        assert trajectoryParams.flip is None

    def test_TP_flip_2(self):
        trajectoryParams = TrajectoryParams()
        trajectoryParams.flip = "F"
        assert trajectoryParams.flip

    def test_TP_flip_3(self):
        trajectoryParams = TrajectoryParams()
        trajectoryParams.flip = "x"
        assert not trajectoryParams.flip

    def test_TP_flip_4(self):
        trajectoryParams = TrajectoryParams()
        trajectoryParams.flip = False
        assert not trajectoryParams.flip

    def test_TP_jdStart_1(self):
        trajectoryParams = TrajectoryParams()
        trajectoryParams.jdStart = None
        assert trajectoryParams.jdStart is None

    def test_TP_jdStart_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        trajectoryParams = TrajectoryParams(obsSite=ObsSite())
        trajectoryParams.jdStart = "100"
        assert trajectoryParams.jdStart.tt == 169

    def test_TP_jdEnd_1(self):
        trajectoryParams = TrajectoryParams()
        trajectoryParams.jdEnd = None
        assert trajectoryParams.jdEnd is None

    def test_TP_jdEnd_2(self):
        class ObsSite:
            UTC2TT = 69
            ts = load.timescale()

        trajectoryParams = TrajectoryParams(obsSite=ObsSite())
        trajectoryParams.jdEnd = "100"
        assert trajectoryParams.jdEnd.tt == 169

    def test_TR_message_1(self):
        trajectoryParams = TrajectoryParams()
        trajectoryParams.message = None
        assert trajectoryParams.message is None

    def test_TR_message_2(self):
        trajectoryParams = TrajectoryParams()
        trajectoryParams.message = "test"
        assert trajectoryParams.message == "test"
