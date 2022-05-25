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
# written in python3, (c) 2019-2022 by mworion
#
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
def module_setup_teardown():
    class Test1:
        @staticmethod
        def setEmptyData():
            return

        @staticmethod
        def measureTask():
            return True

    global app
    with mock.patch.object(PyQt5.QtCore.QTimer,
                           'start'):
        app = MeasureDataCSV(app=App(), parent=Test1())
        yield


def test_startCommunication():
    with mock.patch.object(app.timerTask,
                           'start'):
        suc = app.startCommunication()
        assert suc


def test_stopCommunication():
    with mock.patch.object(app.timerTask,
                           'stop'):
        suc = app.stopCommunication()
        assert suc


def test_openCSV_1():
    suc = app.openCSV()
    assert suc


def test_writeCSV_1():
    suc = app.writeCSV()
    assert not suc


def test_writeCSV_2():
    app.csvFile = open('tests/workDir/temp/test.csv', 'w')
    suc = app.writeCSV()
    assert not suc


def test_writeCSV_3():
    app.csvFile = open('tests/workDir/temp/test.csv', 'w')
    app.csvWriter = csv.DictWriter(app.csvFile, ['test'])
    app.data = {'test': [1, 2]}
    suc = app.writeCSV()
    assert suc


def test_closeCSV_1():
    suc = app.closeCSV()
    assert not suc


def test_closeCSV_2():
    app.csvFile = open('tests/workDir/temp/test.csv', 'w')
    suc = app.closeCSV()
    assert not suc


def test_closeCSV_3():
    app.csvFile = open('tests/workDir/temp/test.csv', 'w')
    app.csvWriter = csv.DictWriter(app.csvFile, ['test'])
    suc = app.closeCSV()
    assert suc


def test_measureTask():
    suc = app.measureTask()
    assert suc