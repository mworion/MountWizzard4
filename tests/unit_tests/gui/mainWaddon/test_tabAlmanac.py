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

import numpy as np
import pytest
import threading
from mw4.gui.mainWaddon.tabAlmanac import Almanac, MoonPhaseData
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtGui import QPixmap
from skyfield.api import wgs84
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def almanac(qapp):
    """Setup Almanac fixture for testing."""
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    # Mock timeMgr methods
    mainW.app.timeMgr.convertTime = mock.MagicMock(return_value="12:00:00")
    mainW.app.timeMgr.timeZoneString = mock.MagicMock(return_value="(UTC)")
    # Avoid kicking off the heavy full-year twilight worker during construction;
    # it is covered explicitly by the showTwilightDataPlot tests.
    with mock.patch.object(Almanac, "showTwilightDataPlot"):
        window = Almanac(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_loads_config(almanac):
    """Test initConfig loads configuration."""
    with mock.patch.object(almanac, "showTwilightDataPlot"):
        almanac.initConfig()


def test_storeConfig_when_no_thread(almanac):
    """Test storeConfig when thread is None."""
    almanac.thread = None
    almanac.storeConfig()


def test_storeConfig_when_thread_running(almanac):
    """Test storeConfig when thread is running."""
    almanac.thread = threading.Thread()
    with mock.patch.object(threading.Thread, "join"):
        almanac.storeConfig()


def test_setColors_updates_colors(almanac):
    """Test setColors updates color scheme."""
    almanac.setColors()


def test_updateColorSet_refreshes_displays(almanac):
    """Test updateColorSet refreshes all displays."""
    with (
        mock.patch.object(almanac, "showTwilightDataPlot"),
        mock.patch.object(almanac, "showTwilightDataList"),
        mock.patch.object(almanac, "showMoonPhase"),
    ):
        almanac.updateColorSet()


def test_plotTwilightData_when_not_closing(almanac):
    """Test plotTwilightData when not closing."""
    almanac.closing = False
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    result = (ts, t, e)
    almanac.plotTwilightData(result)


def test_plotTwilightData_when_closing(almanac):
    """Test plotTwilightData when closing."""
    almanac.closing = True
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    result = (ts, t, e)
    almanac.plotTwilightData(result)


def test_listTwilightData_displays_data(almanac):
    """Test listTwilightData displays twilight data."""
    tsNow = almanac.app.mount.obsSite.ts.now()
    t = [tsNow, tsNow]
    e = [1, 1]
    almanac.listTwilightData(t, e)


def test_calcTwilightData_calculates_values(almanac):
    """Test calcTwilightData calculates twilight values."""
    ts = almanac.app.mount.obsSite.ts
    location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
    val = almanac.calcTwilightData(ts, location, tWinL=0, tWinH=0)
    assert val


def test_runnerCalcTwilightDataPlot_processes_data(almanac):
    """Test runnerCalcTwilightDataPlot processes twilight plot data."""
    location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    with mock.patch.object(almanac, "calcTwilightData", return_value=(t, e)):
        suc = almanac.runnerCalcTwilightDataPlot(ts, location, timeWindow=0)
        assert suc


def test_showTwilightDataPlot_without_location(almanac):
    """Test showTwilightDataPlot when location is None."""
    almanac.app.mount.obsSite.location = None
    with mock.patch.object(threading.Thread, "start"):
        almanac.showTwilightDataPlot()


def test_showTwilightDataPlot_with_location(almanac):
    """Test showTwilightDataPlot when location is set."""
    almanac.app.mount.obsSite.location = wgs84.latlon(
        latitude_degrees=0, longitude_degrees=0, elevation_m=0
    )
    with mock.patch.object(almanac.app.threadPool, "start"):
        almanac.showTwilightDataPlot()


def test_showTwilightDataList_without_location(almanac):
    """Test showTwilightDataList when location is None."""
    almanac.app.mount.obsSite.location = None
    with mock.patch.object(threading.Thread, "start"):
        almanac.showTwilightDataList()


def test_showTwilightDataList_with_location(almanac):
    """Test showTwilightDataList when location is set."""
    almanac.app.mount.obsSite.location = wgs84.latlon(
        latitude_degrees=0, longitude_degrees=0, elevation_m=0
    )
    with mock.patch.object(almanac, "listTwilightData"):
        almanac.showTwilightDataList()


def test_calcMoonPhase_returns_moon_phase_data(almanac):
    """Test calcMoonPhase returns MoonPhaseData with all fields."""
    val = almanac.calcMoonPhase()
    assert isinstance(val, MoonPhaseData)
    assert val.illumination is not None
    assert val.degree is not None
    assert val.percent is not None
    assert val.angle is not None
    assert val.moonTimes is not None
    assert val.moonEvents is not None
    assert val.nodeTimes is not None
    assert val.nodeEvents is not None


def test_generateMoonMask_45_degrees(almanac):
    """Test generateMoonMask with 45 degree angle (waxing, add terminator)."""
    q = QPixmap(64, 64)
    result = almanac.generateMoonMask(q, 45)
    assert not result.isNull()
    assert result.width() == 64
    assert result.height() == 64


def test_generateMoonMask_90_degrees(almanac):
    """Test generateMoonMask with 90 degree angle (first quarter, r=0)."""
    q = QPixmap(64, 64)
    result = almanac.generateMoonMask(q, 90)
    assert not result.isNull()
    assert result.width() == 64
    assert result.height() == 64


def test_generateMoonMask_135_degrees(almanac):
    """Test generateMoonMask with 135 degree angle (waxing gibbous, clear)."""
    q = QPixmap(64, 64)
    result = almanac.generateMoonMask(q, 135)
    assert not result.isNull()
    assert result.width() == 64
    assert result.height() == 64


def test_generateMoonMask_180_degrees(almanac):
    """Test generateMoonMask with 180 degree angle (full moon, r=-1)."""
    q = QPixmap(64, 64)
    result = almanac.generateMoonMask(q, 180)
    assert not result.isNull()
    assert result.width() == 64
    assert result.height() == 64


def test_generateMoonMask_225_degrees(almanac):
    """Test generateMoonMask with 225 degree angle (waning gibbous, clear)."""
    q = QPixmap(64, 64)
    result = almanac.generateMoonMask(q, 225)
    assert not result.isNull()
    assert result.width() == 64
    assert result.height() == 64


def test_generateMoonMask_270_degrees(almanac):
    """Test generateMoonMask with 270 degree angle (third quarter, r=0)."""
    q = QPixmap(64, 64)
    result = almanac.generateMoonMask(q, 270)
    assert not result.isNull()
    assert result.width() == 64
    assert result.height() == 64


def test_generateMoonMask_315_degrees(almanac):
    """Test generateMoonMask with 315 degree angle (waning, add terminator)."""
    q = QPixmap(64, 64)
    result = almanac.generateMoonMask(q, 315)
    assert not result.isNull()
    assert result.width() == 64
    assert result.height() == 64


def test_showMoonPhase_displays_phase(almanac):
    """Test showMoonPhase displays moon phase."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    val = MoonPhaseData(20, 45, 0.20, 0, t, [0, 1], t, [0, 1])
    with mock.patch.object(almanac, "calcMoonPhase", return_value=val):
        almanac.showMoonPhase()


def test_showMoonPhase_handles_data(almanac):
    """Test showMoonPhase handles moon phase data."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    val = MoonPhaseData(20, 45, 0.20, 0, t, [0, 1], t, [0, 1])
    with mock.patch.object(almanac, "calcMoonPhase", return_value=val):
        almanac.showMoonPhase()


def test_renderEventList_with_data(almanac):
    """Test renderEventList renders event list correctly."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    times = [tsNow, tsNow]
    events = [0, 1]
    labels = ["rise", "set"]
    almanac.renderEventList(almanac.ui.riseSetEventsMoon, times, events, labels, "%H:%M:%S")


def test_renderEventList_single_event(almanac):
    """Test renderEventList with single event."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    times = [tsNow]
    events = [0]
    labels = ["event"]
    almanac.renderEventList(almanac.ui.twilightEvents, times, events, labels, "%H:%M:%S")


def test_showMoonNumbers_updates_labels(almanac):
    """Test showMoonNumbers updates moon phase labels."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt])
    data = MoonPhaseData(0.75, 135, 37.5, 0, t, [0], t, [0])
    almanac.showMoonNumbers(data)


def test_showMoonRiseSet_renders_events(almanac):
    """Test showMoonRiseSet renders rise/set events."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    data = MoonPhaseData(0.5, 90, 25, 0, t, [0, 1], t, [0, 1])
    almanac.showMoonRiseSet(data)


def test_showMoonNodes_renders_events(almanac):
    """Test showMoonNodes renders lunar node events."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    data = MoonPhaseData(0.25, 45, 12.5, 0, t, [0], t, [0, 1])
    almanac.showMoonNodes(data)


def test_renderMoonImage_creates_pixmap(almanac):
    """Test renderMoonImage creates and sets moon pixmap."""
    almanac.renderMoonImage(45)


def test_plotTwilightData_with_low_hour_values(almanac):
    """Test plotTwilightData with diverse data to exercise all branches."""
    from datetime import datetime
    from dateutil.tz import tzlocal

    almanac.closing = False
    ts = almanac.app.mount.obsSite.ts
    # Create time entries spread across the day to potentially trigger both branches
    t_early = ts.from_datetime(
        datetime.now(tz=tzlocal()).replace(hour=3, minute=0, second=0, microsecond=0)
    )
    t_late = ts.from_datetime(
        datetime.now(tz=tzlocal()).replace(hour=15, minute=0, second=0, microsecond=0)
    )
    t = ts.tt_jd([t_early.tt, t_late.tt])
    e = np.array([1, 1])
    result = (ts, t, e)
    # Just call the method - it will exercise the code paths
    almanac.plotTwilightData(result)
