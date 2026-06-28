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
import mw4.gui
import numpy as np
import pytest
from mw4.gui.mainWaddon.tabSat_Search import SatSearch, SatSearchSignals
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from pathlib import Path
from PySide6.QtCore import QRect
from PySide6.QtWidgets import QTableWidgetItem
from skyfield.api import EarthSatellite
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    class Test:
        objects = {}

    mainW = MWidget()
    mainW.app = App()
    mainW.satellites = Test()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    # Mock timeMgr methods
    mainW.app.timeMgr.convertTime = mock.MagicMock(return_value="12:00")
    mainW.app.timeMgr.timeZoneString = mock.MagicMock(return_value="(UTC)")
    window = SatSearch(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


@pytest.fixture(autouse=True)
def resetSatellites(function):
    # Provide a complete satellites baseline so tests don't inherit a partial
    # stub left behind by another test in this module-scoped fixture.
    sats = mock.MagicMock()
    sats.objects = {}
    sats.dataValid = False
    sats.dest = Path("tests/work/temp/satellites.tle")
    function.satellites = sats
    yield


def test_satSearchSignals_1(qapp):
    signals = SatSearchSignals()
    assert signals.setSatListItem is not None


def test_initConfig_1(function):
    with mock.patch.object(function.ui.satSourceList, "setCurrentIndex"):
        function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_prepareSatTable_1(function):
    function.prepareSatTable()


def test_processSatelliteSource(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    with mock.patch.object(function.app.mount.obsSite.loader, "tle_file", return_value=[sat]):
        function.processSatelliteSource()


def test_filterListSats_1(function):
    function.ui.satFilterGroup.setEnabled(True)
    function.ui.satIsSunlit.setChecked(True)
    function.ui.satRemoveSO.setChecked(True)
    function.ui.listSats.clear()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("1234")
    function.ui.listSats.setItem(0, 0, entry)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listSats.setItem(0, 1, entry)
    entry = QTableWidgetItem("1")
    function.ui.listSats.setItem(0, 8, entry)
    entry = QTableWidgetItem("1234")
    function.ui.listSats.setItem(0, 7, entry)
    with mock.patch.object(function.ui.satTwilight, "currentIndex", return_value=1):
        function.filterListSats()


def test_filterListSats_2(function):
    function.ui.satFilterGroup.setEnabled(True)
    function.ui.satRemoveK.setChecked(True)
    function.ui.listSats.clear()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("1234")
    function.ui.listSats.setItem(0, 0, entry)
    entry = QTableWidgetItem("KUIPER-123")
    function.ui.listSats.setItem(0, 1, entry)
    entry = QTableWidgetItem("1")
    function.ui.listSats.setItem(0, 8, entry)
    entry = QTableWidgetItem("1234")
    function.ui.listSats.setItem(0, 7, entry)
    with mock.patch.object(function.ui.satTwilight, "currentIndex", return_value=6):
        function.filterListSats()


def test_filterListSats_3(function):
    function.ui.satFilterGroup.setEnabled(True)
    function.ui.satRemoveDQ.setChecked(True)
    function.ui.listSats.clear()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("1234")
    function.ui.listSats.setItem(0, 0, entry)
    entry = QTableWidgetItem("QUIANFAN-1")
    function.ui.listSats.setItem(0, 1, entry)
    entry = QTableWidgetItem("1")
    function.ui.listSats.setItem(0, 8, entry)
    entry = QTableWidgetItem("1234")
    function.ui.listSats.setItem(0, 7, entry)
    with mock.patch.object(function.ui.satTwilight, "currentIndex", return_value=6):
        function.filterListSats()


def test_filterListSats_4(function):
    function.ui.satFilterGroup.setEnabled(True)
    function.ui.satRemoveDQ.setChecked(True)
    function.ui.listSats.clear()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("1234")
    function.ui.listSats.setItem(0, 0, entry)
    entry = QTableWidgetItem("DIGUI-2")
    function.ui.listSats.setItem(0, 1, entry)
    entry = QTableWidgetItem("1")
    function.ui.listSats.setItem(0, 8, entry)
    entry = QTableWidgetItem("1234")
    function.ui.listSats.setItem(0, 7, entry)
    with mock.patch.object(function.ui.satTwilight, "currentIndex", return_value=6):
        function.filterListSats()


def test_setListSatsEntry(function):
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("test")
    function.setListSatsEntry(0, 0, entry)


def test_updateListSats_1(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    isUp = [ts]
    with mock.patch.object(function.signals, "setSatListItem") as mock_signal:
        function.updateListSats(0, param, isUp, True, 5, 4)
        assert mock_signal.emit.called


def test_updateListSats_2(function):
    param = [1, 2, 3, 4]
    with mock.patch.object(function.signals, "setSatListItem") as mock_signal:
        function.updateListSats(0, param, None, False, None, None)
        # Should emit at least for the satParam values
        assert mock_signal.emit.called


def test_updateListSats_3(function):
    param = [1, 2, 3, 4]
    with mock.patch.object(function.signals, "setSatListItem") as mock_signal:
        function.updateListSats(0, param, [], False, 5.5, 2)
        assert mock_signal.emit.called


def test_updateListSats_4(function):
    param = [1, 2, 3, 4]
    ts = function.app.mount.obsSite.ts.now()
    with mock.patch.object(function.signals, "setSatListItem") as mock_signal:
        function.updateListSats(0, param, [ts], True, 3.2, 1)
        assert mock_signal.emit.called


def test_calcSatListDynamic_1(function):
    function.ui.satTabWidget.setCurrentIndex(1)
    function.ui.mainTabWidget.setCurrentIndex(1)
    function.calcSatListDynamic()


def test_calcSatListDynamic_2(function):
    function.ui.satTabWidget.setCurrentIndex(0)
    function.ui.mainTabWidget.setCurrentIndex(1)
    function.calcSatListDynamic()


def test_calcSatListDynamic_3(function):
    function.ui.mainTabWidget.setCurrentIndex(5)
    with mock.patch.object(function.ui.satTabWidget, "isVisible", return_value=True):
        function.calcSatListDynamic()


def test_calcSatListDynamic_4(function):
    function.satellites.dataValid = True
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.satellites.objects = {"NOAA 8": sat}

    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("test")
    function.ui.listSats.setItem(0, 0, entry)
    with (
        mock.patch.object(function.ui.satTabWidget, "isVisible", return_value=True),
        mock.patch.object(QRect, "intersects", return_value=False),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "calcAppMag", return_value=10),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSunlit", return_value=True),
    ):
        function.calcSatListDynamic()


def test_calcSatListDynamic_5(function):
    function.satellites.dataValid = True
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.satellites.objects = {"NOAA 8": sat}

    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("test")
    function.ui.listSats.setItem(0, 0, entry)
    function.ui.listSats.setRowHidden(0, True)
    with (
        mock.patch.object(function.ui.satTabWidget, "isVisible", return_value=True),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSunlit", return_value=True),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "calcAppMag", return_value=10),
        mock.patch.object(QRect, "intersects", return_value=True),
    ):
        function.calcSatListDynamic()


def test_calcSatListDynamic_6(function):
    function.satellites.dataValid = True
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.setRowHidden(0, False)
    function.satellites.objects = {"NOAA 8": sat}
    with (
        mock.patch.object(function.ui.satTabWidget, "isVisible", return_value=True),
        mock.patch.object(function, "updateListSats"),
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "findRangeRate", return_value=[1, 2, 3]
        ),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSunlit", return_value=False),
        mock.patch.object(QRect, "intersects", return_value=True),
    ):
        function.calcSatListDynamic()


def test_calcSatListDynamic_7(function):
    function.satellites.dataValid = True
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.setRowHidden(0, False)
    function.satellites.objects = {"NOAA 8": sat}
    with (
        mock.patch.object(function.ui.satTabWidget, "isVisible", return_value=True),
        mock.patch.object(function, "updateListSats"),
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "findRangeRate", return_value=[1, 2, 3]
        ),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSunlit", return_value=True),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "calcAppMag", return_value=10),
        mock.patch.object(QRect, "intersects", return_value=True),
    ):
        function.calcSatListDynamic()


def test_calcSatListDynamic_8(function):
    function.satellites.dataValid = True
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.ui.mainTabWidget.setCurrentIndex(5)
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.setRowHidden(0, False)
    function.satellites.objects = {"NOAA 8": sat}
    with (
        mock.patch.object(function.ui.satTabWidget, "isVisible", return_value=True),
        mock.patch.object(function, "updateListSats"),
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "findRangeRate", return_value=[np.nan, 2, 3]
        ),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSunlit", return_value=True),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "calcAppMag", return_value=10),
        mock.patch.object(QRect, "intersects", return_value=True),
    ):
        function.calcSatListDynamic()


def test_checkSatOk_1(function):
    tle = [
        "STARLINK-1914",
        "1 47180U 20088BL  21303.19708368  .16584525  12000-4  30219-2 0  9999",
        "2 47180  53.0402 223.8709 0008872 210.0671 150.2394 16.31518727 52528",
    ]
    ts = function.app.mount.obsSite.ts
    tEnd = ts.tt_jd(2459523.2430)
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    suc = function.checkSatOk(sat, tEnd)
    assert not suc


def test_checkSatOk_2(function):
    tle = [
        "CALSPHERE 1",
        "1 00900U 64063C   21307.74429300  .00000461  00000-0  48370-3 0  9996",
        "2 00900  90.1716  36.8626 0025754 343.8320 164.5583 13.73613883839670",
    ]
    ts = function.app.mount.obsSite.ts
    tEnd = ts.tt_jd(2459523.2430)
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    suc = function.checkSatOk(sat, tEnd)
    assert suc


def test_calcSat_1(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    with (
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "findRangeRate", return_value=(1, 1, 1, 1)
        ),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSunlit", return_value=False),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSatUp"),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "checkTwilight"),
        mock.patch.object(function, "updateListSats"),
    ):
        function.calcSat(sat, 0, 0, 0, 0, 0, 0)


def test_calcSat_2(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    with (
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "findRangeRate", return_value=(1, 1, 1, 1)
        ),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSunlit", return_value=True),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "findSatUp"),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "checkTwilight"),
        mock.patch.object(mw4.gui.mainWaddon.tabSat_Search, "calcAppMag", return_value=0),
        mock.patch.object(function, "updateListSats"),
    ):
        function.calcSat(sat, 0, 0, 0, 0, 0, 0)


def test_calcSat_3(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    with (
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "findRangeRate", return_value=(np.nan, 0, 0, 0)
        ),
        mock.patch.object(function, "updateListSats"),
    ):
        function.calcSat(sat, 0, 0, 0, 0, 0, 0)


def test_workerCalcSatList_1(function):
    function.ui.listSats.setRowCount(0)
    function.workerCalcSatList()


def test_workerCalcSatList_2(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    class Test:
        objects = {"sat1": sat}

    function.satellites = Test()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("sat1")
    function.ui.listSats.setItem(0, 1, entry)

    with mock.patch.object(function, "checkSatOk", return_value=False):
        function.workerCalcSatList()


def test_workerCalcSatList_3(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    class Test:
        objects = {"sat1": sat}

    function.satellites = Test()
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(9)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("sat1")
    function.ui.listSats.setItem(0, 1, entry)

    with (
        mock.patch.object(function, "checkSatOk", return_value=True),
        mock.patch.object(function, "calcSat"),
    ):
        function.workerCalcSatList()


def test_calcSatList_1(function):
    with mock.patch.object(function.app.threadPool, "start"):
        function.calcSatList()


def test_fillSatListName_1(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    function.satellites.objects = {"sat1": sat}
    with mock.patch.object(function, "calcSatList"):
        function.fillSatListName()
