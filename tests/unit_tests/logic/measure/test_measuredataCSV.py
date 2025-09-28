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
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import csv

# external packages
import PySide6

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.measure.measureCSV import MeasureDataCSV


@pytest.fixture(autouse=True, scope="function")
def function():
    class Test1:
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
    with mock.patch.object(function.timerTask, "start"):
        function.startCommunication()


def test_stopCommunication(function):
    with mock.patch.object(function.timerTask, "stop"):
        function.stopCommunication()


def test_openCSV_1(function):
    function.openCSV()


def test_writeCSV_1(function):
    function.writeCSV()


def test_writeCSV_2(function):
    function.csvFile = open("tests/work/temp/test.csv", "w")
    function.writeCSV()


def test_writeCSV_3(function):
    function.csvFile = open("tests/work/temp/test.csv", "w")
    function.csvWriter = csv.DictWriter(function.csvFile, ["test"])
    function.data = {"test": [1, 2]}
    function.writeCSV()


def test_closeCSV_1(function):
    function.closeCSV()


def test_closeCSV_2(function):
    function.csvFile = open("tests/work/temp/test.csv", "w")
    function.closeCSV()


def test_closeCSV_3(function):
    function.csvFile = open("tests/work/temp/test.csv", "w")
    function.csvWriter = csv.DictWriter(function.csvFile, ["test"])
    function.closeCSV()


def test_measureTask(function):
    function.measureTask()
