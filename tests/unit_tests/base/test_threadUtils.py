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

import time
import unittest.mock as mock
from mw4.base.threadUtils import mainThreadSleep


def test_mainThreadSleepCallsTimeSleep():
    with mock.patch.object(time, "sleep") as mocked:
        mainThreadSleep(1000)
        mocked.assert_called_once_with(1.0)


def test_mainThreadSleepConverts500ms():
    with mock.patch.object(time, "sleep") as mocked:
        mainThreadSleep(500)
        mocked.assert_called_once_with(0.5)


def test_mainThreadSleepConverts250ms():
    with mock.patch.object(time, "sleep") as mocked:
        mainThreadSleep(250)
        mocked.assert_called_once_with(0.25)


def test_mainThreadSleepZero():
    with mock.patch.object(time, "sleep") as mocked:
        mainThreadSleep(0)
        mocked.assert_called_once_with(0.0)


def test_mainThreadSleepReturnsNone():
    with mock.patch.object(time, "sleep"):
        result = mainThreadSleep(100)
        assert result is None


def test_mainThreadSleepActuallySleeps():
    start = time.monotonic()
    mainThreadSleep(50)
    elapsed = time.monotonic() - start
    assert elapsed >= 0.04
