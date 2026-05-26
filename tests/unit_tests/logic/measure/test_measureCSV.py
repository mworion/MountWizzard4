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
import PySide6
import pytest
import unittest.mock as mock
from mw4.logic.measure.measureCSV import MeasureDataCSV
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="function")
def function():
    class Test1:
        CYCLE_UPDATE_TASK = 1000

        @staticmethod
        def setEmptyData():
            return

        @staticmethod
        def measureTask():
            return True

    with mock.patch.object(PySide6.QtCore.QTimer, "start"):
        func = MeasureDataCSV(app=App(), parent=Test1())
        yield func


def test_startCommunication(function):
    with (
        mock.patch.object(function.timerTask, "start"),
        mock.patch.object(function, "writeHeaderCSV"),
        mock.patch.object(
            function.app.mount.obsSite.timeJD,
            "utc_strftime",
            return_value="2022-01-01-00-00-00",
        ),
    ):
        function.startCommunication()


def test_stopCommunication(function):
    with mock.patch.object(function.timerTask, "stop"):
        function.stopCommunication()


def test_writeHeaderCSV(function):
    function.csvFilename = Path("tests/work/temp/test.csv")
    function.writeHeaderCSV()


def test_writeCSV_1(function):
    function.csvFilename = Path("tests/work/temp/test.csv")
    function.data = {}
    function.writeCSV()


def test_writeCSV_2(function):
    function.csvFilename = Path("tests/work/temp/test.csv")
    function.data = {"time": [1, 2]}
    function.writeCSV()


def test_measureTask(function):
    with mock.patch.object(function, "writeCSV"):
        function.measureTask()
