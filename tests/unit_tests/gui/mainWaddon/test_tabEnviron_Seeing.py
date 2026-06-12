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

import platform
import pytest
import shutil
import webbrowser
from mw4.gui.mainWaddon.tabEnviron_Seeing import EnvironSeeing
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QTableWidgetItem
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

HOURLY = {
    "hour": [10] * 96,
    "date": ["2022-01-01"] * 96,
    "high_clouds": [50] * 96,
    "mid_clouds": [50] * 96,
    "low_clouds": [50] * 96,
    "seeing_arcsec": [1.5] * 96,
    "seeing1": [1] * 96,
    "seeing1_color": ["#404040"] * 96,
    "seeing2": [1] * 96,
    "seeing2_color": ["#404040"] * 96,
    "temperature": [15] * 96,
    "relative_humidity": [60] * 96,
    "badlayer_top": ["1500"] * 96,
    "badlayer_bottom": ["500"] * 96,
    "badlayer_gradient": ["1"] * 96,
    "jetstream": [20] * 96,
}

META = {"last_model_update": "2022-01-01"}


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    shutil.copy("tests/testData/meteoblue.data", "tests/work/data/meteoblue.data")

    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    # Mock timeMgr methods
    mainW.app.timeMgr.convertTime = mock.MagicMock(return_value="12:00")
    mainW.app.timeMgr.timeZoneString = mock.MagicMock(return_value="(UTC)")
    window = EnvironSeeing(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_setupIcons(function):
    function.setupIcons()


def test_addSkyfieldTimeObject(function):
    data = {"hour": [10, 11], "date": ["2022-01-01", "2022-01-01"]}

    function.addSkyfieldTimeObject(data)
    assert "time" in data


def test_applyColumnStyle_j0(function):
    data = dict(HOURLY)
    function.addSkyfieldTimeObject(data)
    item = QTableWidgetItem()
    t = function.applyColumnStyle(item, 0, "time", data, 0, "#111", "#222", "#333")
    assert len(t) > 0


def test_applyColumnStyle_j1(function):
    data = dict(HOURLY)
    function.addSkyfieldTimeObject(data)
    item = QTableWidgetItem()
    t = function.applyColumnStyle(item, 1, "time", data, 0, "#111", "#222", "#333")
    assert ":" in t


def test_applyColumnStyle_j2(function):
    data = dict(HOURLY)
    item = QTableWidgetItem()
    t = function.applyColumnStyle(item, 2, "high_clouds", data, 0, "#404040", "#222", "#333")
    assert t == "50"


def test_applyColumnStyle_j6(function):
    data = dict(HOURLY)
    item = QTableWidgetItem()
    t = function.applyColumnStyle(item, 6, "seeing1", data, 0, "#111", "#404040", "#333")
    assert t == "1"


def test_applyColumnStyle_j7(function):
    data = dict(HOURLY)
    item = QTableWidgetItem()
    t = function.applyColumnStyle(item, 7, "seeing2", data, 0, "#111", "#404040", "#333")
    assert t == "1"


def test_applyColumnStyle_j10(function):
    data = dict(HOURLY)
    item = QTableWidgetItem()
    t = function.applyColumnStyle(item, 10, "badlayer_top", data, 0, "#111", "#222", "#333")
    assert t == "1.5"


def test_applyColumnStyle_j11(function):
    data = dict(HOURLY)
    item = QTableWidgetItem()
    t = function.applyColumnStyle(item, 11, "badlayer_bottom", data, 0, "#111", "#222", "#333")
    assert t == "0.5"


def test_applyColumnStyle_default(function):
    data = dict(HOURLY)
    item = QTableWidgetItem()
    t = function.applyColumnStyle(item, 5, "seeing_arcsec", data, 0, "#111", "#222", "#333")
    assert t == "1.5"


def test_buildSeeingItem(function):
    data = dict(HOURLY)
    function.addSkyfieldTimeObject(data)
    item = function.buildSeeingItem(
        5, "seeing_arcsec", data, 0, "#404040", "#404040", "#404040"
    )
    assert item.text() == "1.5"


def test_markActualColumn(function):
    function.app.dReg.d["seeingWeather"].instance.data = {
        "meta": META,
        "hourly": dict(HOURLY),
    }
    data = dict(HOURLY)
    item = QTableWidgetItem()
    result = function.markActualColumn(item, data, 3)
    assert result == 3
    assert function.ui.limitForecast.text() == "1.5"
    assert function.ui.limitForecastDate.text() == "2022-01-01"


def test_updateSeeingEntries_1(function):
    function.app.dReg.d["seeingWeather"].instance.data = {
        "test": {"hour": [10, 11], "date": ["2022-01-01", "2022-01-01"]}
    }
    function.updateSeeingEntries()


def test_updateSeeingEntries_2(function):
    function.app.dReg.d["seeingWeather"].instance.data = {
        "meta": META,
        "hourly": dict(HOURLY),
    }
    t = function.app.mount.obsSite.ts.utc(2022, 1, 1, 10, 0, 0)
    with mock.patch.object(function.app.mount.obsSite.ts, "now", return_value=t):
        function.updateSeeingEntries()


def test_updateSeeingEntries_3(function):
    function.app.dReg.d["seeingWeather"].instance.data = {
        "meta": META,
        "hourly": dict(HOURLY),
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


def test_openWeb_1(function):
    with mock.patch.object(webbrowser, "open", return_value=True):
        function.openWeb()


def test_openWeb_2(function):
    with mock.patch.object(webbrowser, "open", return_value=False):
        function.openWeb()
