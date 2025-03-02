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
# GUI with PySide for python
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
from gui.mainWaddon.tabAsteroid import Asteroid
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Asteroid(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.initConfig()


def test_initConfigDelayedAsteroid_1(function):
    with mock.patch.object(function.ui.asteroidSourceList, "setCurrentIndex"):
        function.initConfigDelayedAsteroid()


def test_storeConfig_1(function):
    function.storeConfig()


def test_prepareAsteroidTable_1(function):
    function.prepareAsteroidTable()


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


def test_processAsteroidSource_1(function):
    function.asteroids.dest = "tests/testData/mpc_asteroid_test.json"
    with mock.patch.object(json, "load", return_value="", side_effect=Exception):
        with mock.patch.object(os, "remove"):
            function.processAsteroidSource()
            assert function.asteroids.objects == {}


def test_processAsteroidSource_2(function):
    function.asteroids.dest = "tests/testData/mpc_asteroid_test.json"
    with mock.patch.object(json, "load", return_value={"test": "test"}):
        with mock.patch.object(function, "generateName", return_value=""):
            function.processAsteroidSource()
            assert function.asteroids.objects == {}


def test_processAsteroidSource_3(function):
    function.asteroids.dest = "tests/testData/mpc_asteroid_test.json"
    with mock.patch.object(json, "load", return_value={"test": "test"}):
        with mock.patch.object(function, "generateName", return_value="albert"):
            function.processAsteroidSource()
            assert function.asteroids.objects == {"albert": "test"}


def test_filterListAsteroids_1(function):
    function.ui.listAsteroids.clear()
    function.ui.listAsteroids.setRowCount(0)
    function.ui.listAsteroids.setColumnCount(9)
    function.ui.listAsteroids.insertRow(0)
    entry = QTableWidgetItem("1234")
    function.ui.listAsteroids.setItem(0, 0, entry)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listAsteroids.setItem(0, 1, entry)
    function.filterListAsteroids()


def test_fillAsteroidListNames_1(function):
    function.ui.listAsteroids.clear()
    function.asteroids.objects = {
        "test": {
            "H": 18.9,
            "G": 0.15,
            "Num_obs": 103,
            "rms": 0.41,
            "U": "1",
            "Arc_years": "1994-2019",
            "Perturbers": "M-v",
            "Perturbers_2": "38h",
            "Principal_desig": "1994 WY1",
            "Epoch": 2458600.5,
            "M": 298.5756,
            "Peri": 155.25303,
            "Node": 232.63124,
            "i": 5.79199,
            "e": 0.3747765,
            "n": 0.2341911,
            "a": 2.6066884,
            "Ref": "E2019-P40",
            "Num_opps": 3,
            "Computer": "MPCLINUX",
            "Hex_flags": "0005",
            "Last_obs": "2019-08-04",
            "Tp": 2458862.78324,
            "Orbital_period": 4.2085615,
            "Perihelion_dist": 1.6297628,
            "Aphelion_dist": 3.583614,
            "Semilatus_rectum": 1.1202798,
            "Synodic_period": 1.3116661,
            "Orbit_type": "Object with perihelion distance < 1.665 AU",
        }
    }
    function.fillAsteroidListName()
    assert function.ui.listAsteroids.rowCount() == 1
