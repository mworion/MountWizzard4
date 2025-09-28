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
from unittest import mock
import json
import os

# external packages
from PySide6.QtWidgets import QTableWidgetItem

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabComet import Comet
from gui.mainWaddon.tabComet import MWidget


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Comet(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.initConfig()


def test_initConfigDelayedComet_1(function):
    with mock.patch.object(function.ui.cometSourceList, "setCurrentIndex"):
        function.initConfigDelayedComet()


def test_storeConfig_1(function):
    function.storeConfig()


def test_prepareCometTable_1(function):
    function.prepareCometTable()


def test_generateName_1(function):
    val = function.generateName({})
    assert val == ""


def test_generateName_2(function):
    mp = {"Designation_and_name": "test"}
    val = function.generateName(mp)
    assert val == "test"


def test_generateName_3(function):
    mp = {"Name": "test", "Number": "123", "Principal_desig": "base"}
    val = function.generateName(mp)
    assert val == "base - test 123"


def test_generateName_4(function):
    mp = {"Principal_desig": "base"}
    val = function.generateName(mp)
    assert val == "base"


def test_generateName_5(function):
    mp = {"Name": "test", "Number": "123"}
    val = function.generateName(mp)
    assert val == "test 123"


def test_processCometSource_1(function):
    function.comets.dest = "tests/testData/mpc_comet_test.json"
    with mock.patch.object(json, "load", return_value="", side_effect=Exception):
        with mock.patch.object(os, "remove"):
            function.processCometSource()
            assert function.comets.objects == {}


def test_processCometSource_2(function):
    function.comets.dest = "tests/testData/mpc_comet_test.json"
    with mock.patch.object(json, "load", return_value={"test": "test"}):
        with mock.patch.object(function, "generateName", return_value=""):
            function.processCometSource()
            assert function.comets.objects == {}


def test_processCometSource_3(function):
    function.comets.dest = "tests/testData/mpc_comet_test.json"
    with mock.patch.object(json, "load", return_value={"test": "test"}):
        with mock.patch.object(function, "generateName", return_value="albert"):
            function.processCometSource()
            assert function.comets.objects == {"albert": "test"}


def test_filterListComets_1(function):
    function.ui.listComets.clear()
    function.ui.listComets.setRowCount(0)
    function.ui.listComets.setColumnCount(9)
    function.ui.listComets.insertRow(0)
    entry = QTableWidgetItem("1234")
    function.ui.listComets.setItem(0, 0, entry)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listComets.setItem(0, 1, entry)
    function.filterListComets()


def test_fillCometListNames_1(function):
    function.ui.listComets.clear()
    function.comets.objects = {
        "test": {
            "Orbit_type": "C",
            "Provisional_packed_desig": "J71E010",
            "Year_of_perihelion": 1971,
            "Month_of_perihelion": 4,
            "Day_of_perihelion": 8.4027,
            "Perihelion_dist": 1.261019,
            "e": 1.000557,
            "Peri": 152.2158,
            "Node": 103.2844,
            "i": 110.5572,
            "Epoch_year": 2020,
            "Epoch_month": 10,
            "Epoch_day": 10,
            "H": 9.0,
            "G": 4.0,
            "Designation_and_name": "C/1971 E1 (Toba)",
            "Ref": "83,   64",
        }
    }
    function.fillCometListName()
    assert function.ui.listComets.rowCount() == 1
