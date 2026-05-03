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
from mw4.base.loggerMW import setupLogging
from mw4.mountcontrol.trajectoryParams import TrajectoryParams
from skyfield.api import load

setupLogging()


class ObsSite:
    UTC2TT = 69
    ts = load.timescale()


def testFlipFalse():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.flip = False
    assert not trajectoryParams.flip


def testFlipTrue():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.flip = True
    assert trajectoryParams.flip


def testMessage():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.message = "test"
    assert trajectoryParams.message == "test"


def testOffsetRA():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.offsetRA = 1.5
    assert trajectoryParams.offsetRA == 1.5


def testOffsetDEC():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.offsetDEC = 2.5
    assert trajectoryParams.offsetDEC == 2.5


def testOffsetDECcorr():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.offsetDECcorr = 3.5
    assert trajectoryParams.offsetDECcorr == 3.5


def testOffsetTime():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.offsetTime = 4.5
    assert trajectoryParams.offsetTime == 4.5


def testJdStartDefault():
    trajectoryParams = TrajectoryParams(ObsSite())
    result = trajectoryParams.jdStart
    assert result is not None


def testJdStartZero():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.jdStart = 0
    assert trajectoryParams.jdStart.tt == 69


def testJdStartValue():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.jdStart = 100
    assert trajectoryParams.jdStart.tt == 169


def testJdEndDefault():
    trajectoryParams = TrajectoryParams(ObsSite())
    result = trajectoryParams.jdEnd
    assert result is not None


def testJdEndZero():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.jdEnd = 0
    assert trajectoryParams.jdEnd.tt == 69


def testJdEndValue():
    trajectoryParams = TrajectoryParams(ObsSite())
    trajectoryParams.jdEnd = 100
    assert trajectoryParams.jdEnd.tt == 169
