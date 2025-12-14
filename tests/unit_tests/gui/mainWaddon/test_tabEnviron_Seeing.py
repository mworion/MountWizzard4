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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import platform
import pytest
import shutil
import webbrowser
from mw4.base.loggerMW import setupLogging
from mw4.gui.mainWaddon.tabEnviron_Seeing import EnvironSeeing
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

setupLogging()


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    shutil.copy("tests/testData/meteoblue.data", "tests/work/data/meteoblue.data")

    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = EnvironSeeing(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_setupIcons(function):
    function.setupIcons()


def test_addSkyfieldTimeObject(function):
    data = {"hour": [10, 11], "date": ["2022-01-01", "2022-01-01"]}

    function.addSkyfieldTimeObject(data)
    assert "time" in data


def test_updateSeeingEntries_1(function):
    function.app.seeingWeather.data = {
        "test": {"hour": [10, 11], "date": ["2022-01-01", "2022-01-01"]}
    }
    function.updateSeeingEntries()


def test_updateSeeingEntries_2(function):
    function.app.seeingWeather.data = {
        "meta": {
            "last_model_update": "2022-01-01",
        },
        "hourly": {
            "hour": [10] * 96,
            "date": ["2022-01-01"] * 96,
            "high_clouds": [1] * 96,
            "mid_clouds": [1] * 96,
            "low_clouds": [1] * 96,
            "seeing_arcsec": [1] * 96,
            "seeing1": [1] * 96,
            "seeing1_color": ["#404040"] * 96,
            "seeing2": [1] * 96,
            "seeing2_color": ["#404040"] * 96,
            "temperature": [1] * 96,
            "relative_humidity": [1] * 96,
            "badlayer_top": ["1"] * 96,
            "badlayer_bottom": ["1"] * 96,
            "badlayer_gradient": ["1"] * 96,
            "jetstream": [1] * 96,
        },
    }
    t = function.app.mount.obsSite.ts.utc(2022, 1, 1, 10, 0, 0)
    with mock.patch.object(function.app.mount.obsSite.ts, "now", return_value=t):
        function.updateSeeingEntries()


def test_updateSeeingEntries_3(function):
    function.app.seeingWeather.data = {
        "meta": {
            "last_model_update": "2022-01-01",
        },
        "hourly": {
            "hour": [10] * 96,
            "date": ["2022-01-01"] * 96,
            "high_clouds": [1] * 96,
            "mid_clouds": [1] * 96,
            "low_clouds": [1] * 96,
            "seeing_arcsec": [1] * 96,
            "seeing1": [1] * 96,
            "seeing1_color": ["#404040"] * 96,
            "seeing2": [1] * 96,
            "seeing2_color": ["#404040"] * 96,
            "temperature": [1] * 96,
            "relative_humidity": [1] * 96,
            "badlayer_top": ["1"] * 96,
            "badlayer_bottom": ["1"] * 96,
            "badlayer_gradient": ["1"] * 96,
            "jetstream": [1] * 96,
        },
    }
    t = function.app.mount.obsSite.ts.utc(2023, 1, 1, 10, 0, 0)
    with mock.patch.object(function.app.mount.obsSite.ts, "now", return_value=t):
        function.updateSeeingEntries()


def test_clearSeeingEntries(function):
    function.clearSeeingEntries()


def test_enableSeeingEntries_1(function):
    function.seeingEnabled = False
    function.enableSeeingEntries()


def test_prepareSeeingTable_1(function):
    with mock.patch.object(platform, "system", return_value="Darwin"):
        function.prepareSeeingTable()


def test_prepareSeeingTable_2(function):
    with mock.patch.object(platform, "system", return_value="Windows"):
        function.prepareSeeingTable()


def test_openMeteoblue_1(function):
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openMeteoblue()


def test_openMeteoblue_2(function):
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openMeteoblue()
