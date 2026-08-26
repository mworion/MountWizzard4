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
"""Unit tests for SatSearch GUI module."""

import json
import mw4.gui
import numpy as np
import pytest
from mw4.gui.mainWaddon.tabSat_Search import SatSearch, SatSearchSignals
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from pathlib import Path
from PySide6.QtWidgets import QTableWidgetItem
from skyfield.api import EarthSatellite
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from typing import ClassVar
from unittest import mock


@pytest.fixture(scope="module")
def function(qapp: object) -> SatSearch:
    """Create SatSearch instance with mocked dependencies for testing."""

    class Test:
        objects: ClassVar = {}

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


@pytest.fixture(autouse=True, scope="module")
def resetSatellites(function: SatSearch) -> None:
    """Reset satellites state before each test module."""
    # Provide a complete satellites baseline so tests don't inherit a partial
    # stub left behind by another test in this module-scoped fixture.
    sats = mock.MagicMock()
    sats.objects = {}
    sats.dataValid = False
    sats.dest = Path("tests/work/temp/satellites.tle")
    function.satellites = sats
    yield


def test_satSearchSignals_1(qapp: object) -> None:
    signals = SatSearchSignals()
    assert signals.setSatListItem is not None
    assert signals.setSatListRowHidden is not None
    assert signals.setSatGroupTitle is not None


def test_initConfig_1(function: SatSearch) -> None:
    with mock.patch.object(function.ui.satSourceList, "setCurrentIndex"):
        function.initConfig()


def test_storeConfig_1(function: SatSearch) -> None:
    function.storeConfig()


def test_prepareSatTable_1(function: SatSearch) -> None:
    function.prepareSatTable()


def test_processSatelliteSource_tle(function: SatSearch) -> None:
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.satellites.dest = Path("test.tle")

    loader = function.app.dReg["mount"].obsSite.loader
    with mock.patch.object(loader, "tle_file", return_value=[sat]):
        function.processSatelliteSource()
        assert "NOAA 8" in function.satellites.objects


def test_processSatelliteSource_json(function: SatSearch) -> None:
    """Test processSatelliteSource with JSON OMM file."""
    function.satellites.dest = Path("test.json")
    omm_record = {"OBJECT_NAME": "SAT1", "OBJECT_ID": "2020-001A"}

    with (
        mock.patch("builtins.open", mock.mock_open(read_data='[{"OBJECT_NAME": "SAT1"}]')),
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "EarthSatellite"
        ) as mock_sat_class,
        mock.patch("json.load", return_value=[omm_record]),
    ):
        mock_sat = mock.MagicMock()
        mock_sat.name = "SAT1"
        mock_sat_class.from_omm.return_value = mock_sat

        function.processSatelliteSource()
        assert "SAT1" in function.satellites.objects


def test_processSatelliteSource_unsupported_format(function: SatSearch) -> None:
    """Test processSatelliteSource with unsupported file format."""
    function.satellites.dest = Path("test.txt")
    function.processSatelliteSource()


def test_processLoadTLE(function: SatSearch) -> None:
    """Test processLoadTLE loads TLE file correctly."""
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.satellites.dest = Path("test.tle")

    loader = function.app.dReg["mount"].obsSite.loader
    with mock.patch.object(loader, "tle_file", return_value=[sat]):
        function.processLoadTLE()
        assert "NOAA 8" in function.satellites.objects


def test_processLoadJsonOMM_success(function: SatSearch) -> None:
    """Test processLoadJsonOMM successfully loads OMM records."""
    function.satellites.dest = Path("test.json")
    omm_record = {"OBJECT_NAME": "SAT1"}

    with (
        mock.patch("builtins.open", mock.mock_open(read_data='[{"OBJECT_NAME": "SAT1"}]')),
        mock.patch("json.load", return_value=[omm_record]),
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "EarthSatellite"
        ) as mock_sat_class,
    ):
        mock_sat = mock.MagicMock()
        mock_sat.name = "SAT1"
        mock_sat_class.from_omm.return_value = mock_sat

        function.processLoadJsonOMM()
        assert "SAT1" in function.satellites.objects


def test_processLoadJsonOMM_json_error(function: SatSearch) -> None:
    """Test processLoadJsonOMM handles JSON decode error."""
    function.satellites.dest = Path("test.json")

    json_error = json.JSONDecodeError("test", "doc", 0)
    with (
        mock.patch("builtins.open", mock.mock_open(read_data="invalid json")),
        mock.patch("json.load", side_effect=json_error),
        mock.patch.object(function.mainW.log, "error"),
    ):
        function.processLoadJsonOMM()


def test_setListSatsEntry(function: SatSearch) -> None:
    function.ui.listSats.setRowCount(1)
    function.calcGeneration = 3
    entry = QTableWidgetItem("test")
    function.setListSatsEntry(0, 0, entry, 3)
    assert function.ui.listSats.item(0, 0).text() == "test"


def test_setListSatsEntry_stale(function: SatSearch) -> None:
    function.ui.listSats.setRowCount(1)
    function.ui.listSats.setItem(0, 0, QTableWidgetItem("keep"))
    function.calcGeneration = 5
    entry = QTableWidgetItem("dropped")
    function.setListSatsEntry(0, 0, entry, 4)
    assert function.ui.listSats.item(0, 0).text() == "keep"


def test_updateVisibilityRow(function: SatSearch) -> None:
    function.ui.listSats.setRowCount(1)
    function.calcGeneration = 2
    function.updateVisibilityRow(0, True, 2)
    assert function.ui.listSats.isRowHidden(0)
    function.updateVisibilityRow(0, False, 2)
    assert not function.ui.listSats.isRowHidden(0)


def test_updateVisibilityRow_stale(function: SatSearch) -> None:
    function.ui.listSats.setRowCount(1)
    function.ui.listSats.setRowHidden(0, False)
    function.calcGeneration = 7
    function.updateVisibilityRow(0, True, 6)
    assert not function.ui.listSats.isRowHidden(0)


def test_updateTitleRunning(function: SatSearch) -> None:
    function.calcGeneration = 1
    with (
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "changeStyleDynamic"
        ) as mockChangeStyle,
        mock.patch.object(function.ui.satFilterGroup, "setTitle") as mockSetTitle,
    ):
        function.updateTitleRunning("Test Title", True, 1)
        mockChangeStyle.assert_called_once_with(function.ui.satFilterGroup, "run", "true")
        mockSetTitle.assert_called_once_with("Test Title")


def test_updateTitleRunning_stale(function: SatSearch) -> None:
    function.calcGeneration = 9
    with (
        mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Search, "changeStyleDynamic"
        ) as mockChangeStyle,
        mock.patch.object(function.ui.satFilterGroup, "setTitle") as mockSetTitle,
    ):
        function.updateTitleRunning("Test Title", False, 8)
        mockChangeStyle.assert_not_called()
        mockSetTitle.assert_not_called()


def test_updateListSats_1(function: SatSearch) -> None:
    param = [1, 2, 3, 4]
    ts = function.app.dReg["mount"].obsSite.ts.now()
    isUp = [ts]
    with mock.patch.object(function.signals, "setSatListItem") as mock_signal:
        function.updateListSats(0, param, isUp, True, 5, 4)
        assert mock_signal.emit.called


def test_updateListSats_2(function: SatSearch) -> None:
    param = [1, 2, 3, 4]
    with mock.patch.object(function.signals, "setSatListItem") as mock_signal:
        function.updateListSats(0, param, [], False)
        # Should emit for the satParam values
        assert mock_signal.emit.called


def test_updateListSats_3(function: SatSearch) -> None:
    param = [1, 2, 3, 4]
    with mock.patch.object(function.signals, "setSatListItem") as mock_signal:
        function.updateListSats(0, param, [], False, 5.5, 2)
        assert mock_signal.emit.called


def test_updateListSats_4(function: SatSearch) -> None:
    param = [1, 2, 3, 4]
    ts = function.app.dReg["mount"].obsSite.ts.now()
    with mock.patch.object(function.signals, "setSatListItem") as mock_signal:
        function.updateListSats(0, param, [ts], True, 3.2, 1)
        assert mock_signal.emit.called


def test_satOkSGP4_1(function: SatSearch) -> None:
    tle = [
        "STARLINK-1914",
        "1 47180U 20088BL  21303.19708368  .16584525  12000-4  30219-2 0  9999",
        "2 47180  53.0402 223.8709 0008872 210.0671 150.2394 16.31518727 52528",
    ]
    ts = function.app.dReg["mount"].obsSite.ts
    tEnd = ts.tt_jd(2459523.2430)
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    suc = function.satOkSGP4(sat, tEnd)
    assert not suc


def test_satOkSGP4_2(function: SatSearch) -> None:
    tle = [
        "CALSPHERE 1",
        "1 00900U 64063C   21307.74429300  .00000461  00000-0  48370-3 0  9996",
        "2 00900  90.1716  36.8626 0025754 343.8320 164.5583 13.73613883839670",
    ]
    ts = function.app.dReg["mount"].obsSite.ts
    tEnd = ts.tt_jd(2459523.2430)
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    suc = function.satOkSGP4(sat, tEnd)
    assert suc


def test_calcSat_1(function: SatSearch) -> None:
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
        result = function.calcSat(sat, 0, 0, 0, 0, 0, 0, 0)
        assert isinstance(result, tuple)
        assert len(result) == 2


def test_calcSat_2(function: SatSearch) -> None:
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
        result = function.calcSat(sat, 0, 0, 0, 0, 0, 0, 0)
        assert isinstance(result, tuple)
        assert result[0] is True


def test_calcSat_3(function: SatSearch) -> None:
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
        result = function.calcSat(sat, 0, 0, 0, 0, 0, 0, 0)
        assert isinstance(result, tuple)
        assert result == (False, 5)


def test_runnerCalcSatList_1(function: SatSearch) -> None:
    function.calcGeneration = 1
    function.mutexCalc.lock()
    with mock.patch.object(function.signals, "setSatGroupTitle"):
        function.runnerCalcSatList([], 1, False, 5, 30)


def test_runnerCalcSatList_2(function: SatSearch) -> None:
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.calcGeneration = 1
    function.mutexCalc.lock()
    snapshot = [(0, "sat1", sat, False)]
    with (
        mock.patch.object(function, "satOkSGP4", return_value=False),
        mock.patch.object(function.signals, "setSatGroupTitle"),
    ):
        function.runnerCalcSatList(snapshot, 1, False, 5, 30)


def test_runnerCalcSatList_3(function: SatSearch) -> None:
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.calcGeneration = 1
    function.mutexCalc.lock()
    snapshot = [(0, "sat1", sat, False)]
    with (
        mock.patch.object(function, "satOkSGP4", return_value=True),
        mock.patch.object(function, "calcSat", return_value=(True, 2)),
        mock.patch.object(function.signals, "setSatGroupTitle"),
        mock.patch.object(function.signals, "setSatListRowHidden"),
    ):
        function.runnerCalcSatList(snapshot, 1, False, 5, 30)


def test_runnerCalcSatList_4(function: SatSearch) -> None:
    """Test runnerCalcSatList with hidden row."""
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.calcGeneration = 1
    function.mutexCalc.lock()
    snapshot = [(0, "sat1", sat, True)]
    with (
        mock.patch.object(function, "satOkSGP4", return_value=True),
        mock.patch.object(function, "calcSat"),
        mock.patch.object(function.signals, "setSatGroupTitle"),
    ):
        function.runnerCalcSatList(snapshot, 1, False, 5, 30)


def test_runnerCalcSatList_generation_break(function: SatSearch) -> None:
    """Test runnerCalcSatList breaks early on generation change."""
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.calcGeneration = 2
    function.mutexCalc.lock()
    snapshot = [(0, "sat1", sat, False)]
    with (
        mock.patch.object(function.signals, "setSatGroupTitle"),
        mock.patch.object(function, "calcSat") as mockCalcSat,
    ):
        function.runnerCalcSatList(snapshot, 1, False, 5, 30)
        mockCalcSat.assert_not_called()


def test_runnerCalcSatList_check_sunlit_true(function: SatSearch) -> None:
    """Test runnerCalcSatList with checkIsSunlit True and satellite sunlit."""
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.calcGeneration = 1
    function.mutexCalc.lock()
    snapshot = [(0, "sat1", sat, False)]
    with (
        mock.patch.object(function, "satOkSGP4", return_value=True),
        mock.patch.object(function, "calcSat", return_value=(True, 2)),
        mock.patch.object(function.signals, "setSatGroupTitle"),
        mock.patch.object(function.signals, "setSatListRowHidden"),
    ):
        function.runnerCalcSatList(snapshot, 1, True, 5, 30)


def test_calcSatList_empty(function: SatSearch) -> None:
    function.calcGeneration = 1
    with (
        mock.patch.object(function.signals, "setSatGroupTitle") as mockTitle,
        mock.patch.object(function.app.threadPool, "start") as mockStart,
    ):
        function.calcSatList([], 1)
        mockTitle.emit.assert_called_once()
        mockStart.assert_not_called()


def test_calcSatList_starts_worker(function: SatSearch) -> None:
    snapshot = [(0, "sat1", mock.MagicMock(), False)]
    with (
        mock.patch.object(function.mutexCalc, "tryLock", return_value=True),
        mock.patch.object(function.app.threadPool, "start") as mockStart,
    ):
        function.calcSatList(snapshot, 1)
        mockStart.assert_called_once()


def test_calcSatList_mutex_locked(function: SatSearch) -> None:
    snapshot = [(0, "sat1", mock.MagicMock(), False)]
    with (
        mock.patch.object(function.mutexCalc, "tryLock", return_value=False),
        mock.patch.object(function.app.threadPool, "start") as mockStart,
    ):
        function.calcSatList(snapshot, 1)
        mockStart.assert_not_called()


def test_fillSatListName_1(function: SatSearch) -> None:
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    function.satellites.objects = {"sat1": sat}
    function.calcGeneration = 0
    with mock.patch.object(function, "calcSatList") as mockCalc:
        function.fillSatListName()
        assert function.calcGeneration == 1
        mockCalc.assert_called_once()
        snapshot = mockCalc.call_args[0][0]
        assert snapshot[0][1] == "sat1"


def test_checkSatNameOk_with_filter(function: SatSearch) -> None:
    """Test checkSatNameOk applies satellite name filters."""
    function.filterStr = "starlink"
    function.ui.satRemoveStarlink.setChecked(True)
    function.ui.satRemoveCosmos.setChecked(False)
    result = function.checkSatNameOk("STARLINK-1234", 1234)
    assert not result


def test_checkSatNameOk_pass_filter(function: SatSearch) -> None:
    """Test checkSatNameOk passes when filter not applied."""
    function.filterStr = "cosmos"
    function.ui.satRemoveStarlink.setChecked(False)
    function.ui.satRemoveCosmos.setChecked(True)
    result = function.checkSatNameOk("COSMOS-2234", 2234)
    assert not result


def test_checkSatNameOk_no_filters(function: SatSearch) -> None:
    """Test checkSatNameOk with no filters applied."""
    function.filterStr = "test"
    for satFilter in function.SATFILTERS:
        ui = getattr(function.ui, f"satRemove{satFilter}")
        ui.setChecked(False)
    result = function.checkSatNameOk("TEST-SAT", 1234)
    assert result
