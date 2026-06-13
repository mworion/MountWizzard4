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
from mw4.gui.mainWaddon.tabAlmanac import Almanac
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


def test_workerCalcTwilightDataPlot_processes_data(almanac):
    """Test workerCalcTwilightDataPlot processes twilight plot data."""
    location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    e = np.array([1, 1])
    with mock.patch.object(almanac, "calcTwilightData", return_value=(t, e)):
        suc = almanac.workerCalcTwilightDataPlot(ts, location, timeWindow=0)
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


def test_calcMoonPhase_returns_8_values(almanac):
    """Test calcMoonPhase returns 8 values."""
    val = almanac.calcMoonPhase()
    assert len(val) == 8


def test_generateMoonMask_45_degrees(almanac):
    """Test generateMoonMask with 45 degree angle."""
    q = QPixmap(64, 64)
    almanac.generateMoonMask(q, 45)


def test_generateMoonMask_135_degrees(almanac):
    """Test generateMoonMask with 135 degree angle."""
    q = QPixmap(64, 64)
    almanac.generateMoonMask(q, 135)


def test_generateMoonMask_225_degrees(almanac):
    """Test generateMoonMask with 225 degree angle."""
    q = QPixmap(64, 64)
    almanac.generateMoonMask(q, 225)


def test_generateMoonMask_315_degrees(almanac):
    """Test generateMoonMask with 315 degree angle."""
    q = QPixmap(64, 64)
    almanac.generateMoonMask(q, 315)


def test_showMoonPhase_displays_phase(almanac):
    """Test showMoonPhase displays moon phase."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    val = (20, 45, 0.20, 0, t, [0, 1], t, [0, 1])
    with mock.patch.object(almanac, "calcMoonPhase", return_value=val):
        almanac.showMoonPhase()


def test_showMoonPhase_handles_data(almanac):
    """Test showMoonPhase handles moon phase data."""
    ts = almanac.app.mount.obsSite.ts
    tsNow = ts.now()
    t = ts.tt_jd([tsNow.tt, tsNow.tt])
    val = (20, 45, 0.20, 0, t, [0, 1], t, [0, 1])
    with mock.patch.object(almanac, "calcMoonPhase", return_value=val):
        almanac.showMoonPhase()


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


