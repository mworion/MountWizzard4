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

import unittest
from mw4.base.loggerMW import setupLogging
from mw4.mountcontrol.trajectoryParams import TrajectoryParams
from skyfield.api import load

setupLogging()


class ObsSite:
    UTC2TT = 69
    ts = load.timescale()


class TestConfigData(unittest.TestCase):
    def setUp(self):
        pass

    def test_TP_flip_4(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.flip = False
        assert not trajectoryParams.flip

    def test_TP_jdStart_2(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.jdStart = 100
        assert trajectoryParams.jdStart.tt == 169

    def test_TP_jdEnd_2(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.jdEnd = 100
        assert trajectoryParams.jdEnd.tt == 169

    def test_TR_message_2(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.message = "test"
        assert trajectoryParams.message == "test"
