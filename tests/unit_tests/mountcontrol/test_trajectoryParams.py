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

    def testFlipFalse(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.flip = False
        assert not trajectoryParams.flip

    def testFlipTrue(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.flip = True
        assert trajectoryParams.flip

    def testMessage(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.message = "test"
        assert trajectoryParams.message == "test"

    def testOffsetRA(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.offsetRA = 1.5
        assert trajectoryParams.offsetRA == 1.5

    def testOffsetDEC(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.offsetDEC = 2.5
        assert trajectoryParams.offsetDEC == 2.5

    def testOffsetDECcorr(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.offsetDECcorr = 3.5
        assert trajectoryParams.offsetDECcorr == 3.5

    def testOffsetTime(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.offsetTime = 4.5
        assert trajectoryParams.offsetTime == 4.5

    def testJdStartDefault(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        result = trajectoryParams.jdStart
        assert result is not None

    def testJdStartZero(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.jdStart = 0
        assert trajectoryParams.jdStart.tt == 69

    def testJdStartValue(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.jdStart = 100
        assert trajectoryParams.jdStart.tt == 169

    def testJdEndDefault(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        result = trajectoryParams.jdEnd
        assert result is not None

    def testJdEndZero(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.jdEnd = 0
        assert trajectoryParams.jdEnd.tt == 69

    def testJdEndValue(self):
        trajectoryParams = TrajectoryParams(ObsSite())
        trajectoryParams.jdEnd = 100
        assert trajectoryParams.jdEnd.tt == 169
