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
import pytest
import unittest.mock as mock
import csv

# external packages
import PyQt5

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.measure.measureCSV import MeasureDataCSV


@pytest.fixture(autouse=True, scope='function')
def function():
    class Test1:
        @staticmethod
        def setEmptyData():
            return

        @staticmethod
        def measureTask():
            return True

    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        func = MeasureDataCSV(app=App(), parent=Test1())
        yield func


def test_startCommunication(function):
    with mock.patch.object(function.timerTask,
                           'start'):
        suc = function.startCommunication()
        assert suc


def test_stopCommunication(function):
    with mock.patch.object(function.timerTask,
                           'stop'):
        suc = function.stopCommunication()
        assert suc


def test_openCSV_1(function):
    suc = function.openCSV()
    assert suc


def test_writeCSV_1(function):
    suc = function.writeCSV()
    assert not suc


def test_writeCSV_2(function):
    function.csvFile = open('tests/workDir/temp/test.csv', 'w')
    suc = function.writeCSV()
    assert not suc


def test_writeCSV_3(function):
    function.csvFile = open('tests/workDir/temp/test.csv', 'w')
    function.csvWriter = csv.DictWriter(function.csvFile, ['test'])
    function.data = {'test': [1, 2]}
    suc = function.writeCSV()
    assert suc


def test_closeCSV_1(function):
    suc = function.closeCSV()
    assert not suc


def test_closeCSV_2(function):
    function.csvFile = open('tests/workDir/temp/test.csv', 'w')
    suc = function.closeCSV()
    assert not suc


def test_closeCSV_3(function):
    function.csvFile = open('tests/workDir/temp/test.csv', 'w')
    function.csvWriter = csv.DictWriter(function.csvFile, ['test'])
    suc = function.closeCSV()
    assert suc


def test_measureTask(function):
    suc = function.measureTask()
    assert suc