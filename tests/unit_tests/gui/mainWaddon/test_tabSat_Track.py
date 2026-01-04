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
# Licence APL2.0
#
###########################################################

import mw4.gui
import numpy as np
import pytest
from mw4.gui.mainWaddon.astroObjects import AstroObjects
from mw4.gui.mainWaddon.tabSat_Track import SatTrack
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QComboBox, QGroupBox, QTableWidget, QTableWidgetItem
from sgp4.exporter import export_tle
from skyfield.api import Angle, EarthSatellite
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    def test():
        return

    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SatTrack(mainW)
    window.satellites = AstroObjects(
        mainW, "satellite", [""], QTableWidget(), QComboBox(), QGroupBox(), test, test
    )
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_enableGuiFunctions_1(function):
    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=None):
        function.enableGuiFunctions()


def test_enableGuiFunctions_2(function):
    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=True):
        function.enableGuiFunctions()


def test_signalSatelliteData_1(function):
    function.satOrbits = 1
    function.signalSatelliteData([], [])


def test_signalSatelliteData_2(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.satOrbits = 1
    function.signalSatelliteData([], [])


def test_clearTrackingParameters(function):
    function.clearTrackingParameters()


def test_calcTrajectoryData_1(function):
    alt, az = function.calcTrajectoryData(100, 100)
    assert len(alt) == 0
    assert len(az) == 0


def test_calcTrajectoryData_2(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]

    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    start = 2459215.0
    alt, az = function.calcTrajectoryData(start, start + 2 / 86400)
    assert len(alt)
    assert len(az)


def test_calcTrajectoryAndShow_1(function):
    function.app.deviceStat["mount"] = True
    function.ui.useInternalSatCalc.setChecked(True)
    with mock.patch.object(function, "selectStartEnd", return_value=(0, 0)):
        function.calcTrajectoryAndShow()


def test_calcTrajectoryAndShow_2(function):
    function.app.deviceStat["mount"] = True
    function.ui.useInternalSatCalc.setChecked(True)
    with mock.patch.object(function, "selectStartEnd", return_value=(1, 1)):
        with mock.patch.object(function, "calcTrajectoryData", return_value=(0, 0)):
            with mock.patch.object(function, "filterHorizon", return_value=(0, 0, 0, 0)):
                with mock.patch.object(function, "signalSatelliteData"):
                    function.calcTrajectoryAndShow()


def test_calcTrajectoryAndShow_3(function):
    function.app.deviceStat["mount"] = False
    function.ui.useInternalSatCalc.setChecked(False)
    with mock.patch.object(function, "selectStartEnd", return_value=(1, 1)):
        with mock.patch.object(function.app.mount, "calcTLE"):
            with mock.patch.object(function, "signalSatelliteData"):
                function.calcTrajectoryAndShow()


def test_calcTrajectoryAndShow_4(function):
    function.app.deviceStat["mount"] = True
    function.ui.useInternalSatCalc.setChecked(False)
    with mock.patch.object(function, "selectStartEnd", return_value=(1, 1)):
        with mock.patch.object(function.app.mount, "calcTLE"):
            with mock.patch.object(function, "signalSatelliteData"):
                function.calcTrajectoryAndShow()


def test_workerShowSatPasses_0(function):
    function.satellite = None
    function.workerShowSatPasses()


def test_showSatPasses_1(function):
    ts = function.app.mount.obsSite.ts
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "culminate": ts.tt_jd(2459215.6),
            "settle": ts.tt_jd(2459215.7),
        },
        {"rise": ts.tt_jd(2459216.5), "settle": ts.tt_jd(2459216.7)},
    ]
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Track, "calcSatPasses", return_value=satOrbits
        ):
            with mock.patch.object(function, "calcTrajectoryAndShow"):
                function.workerShowSatPasses()


def test_workerShowSatPasses_2(function):
    ts = function.app.mount.obsSite.ts
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "culminate": ts.tt_jd(2459215.6),
            "flip": ts.tt_jd(2459215.6),
            "settle": ts.tt_jd(2459215.7),
        },
        {"rise": ts.tt_jd(2459216.5), "settle": ts.tt_jd(2459216.7)},
    ]
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Track, "calcSatPasses", return_value=satOrbits
        ):
            with mock.patch.object(function, "calcTrajectoryAndShow"):
                function.workerShowSatPasses()


def test_workerShowSatPasses_3(function):
    ts = function.app.mount.obsSite.ts
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    satOrbits = [
        {
            "culminate": ts.tt_jd(2459215.6),
            "flip": ts.tt_jd(2459215.6),
        },
        {"rise": ts.tt_jd(2459216.5), "settle": ts.tt_jd(2459216.7)},
    ]
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(
            mw4.gui.mainWaddon.tabSat_Track, "calcSatPasses", return_value=satOrbits
        ):
            with mock.patch.object(function, "calcTrajectoryAndShow"):
                function.workerShowSatPasses()


def test_showSatPasses_1(function):
    with mock.patch.object(function.app.threadPool, "start"):
        function.showSatPasses()


def test_extractSatelliteData_0(function):
    function.satellites.objects = {"NOAA 8": "sat", "Test1": "sat"}

    function.satTableBaseValid = False
    function.extractSatelliteData(satName="Tjan")


def test_extractSatelliteData_1(function):
    function.satellites.objects = {"NOAA 8": "sat", "Test1": "sat"}

    function.satTableBaseValid = True
    function.extractSatelliteData(satName="Tjan")


def test_extractSatelliteData_2(function):
    function.ui.listSats.clear()
    function.satellites.objects = {"Test0": "", "Test1": ""}

    function.satTableBaseValid = True
    function.extractSatelliteData(satName="NOAA 8")


def test_extractSatelliteData_3(function):
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("Test1")
    function.ui.listSats.setItem(0, 1, entry)

    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    function.satellites.objects = {"NOAA 8": sat, "Test1": sat}
    function.satTableBaseValid = True
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(
        function.app.mount.obsSite.ts, "now", return_value=ts.tt_jd(2458925.404976551)
    ):
        with mock.patch.object(MWidget, "positionCursorInTable"):
            function.extractSatelliteData(satName="NOAA 8")


def test_extractSatelliteData_4(function):
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("Test1")
    function.ui.listSats.setItem(0, 1, entry)

    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    function.satellites.objects = {"NOAA 8": sat, "Test1": sat}
    function.satTableBaseValid = True
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(
        function.app.mount.obsSite.ts, "now", return_value=ts.tt_jd(2458930.404976551)
    ):
        with mock.patch.object(MWidget, "positionCursorInTable"):
            function.extractSatelliteData(satName="NOAA 8")


def test_extractSatelliteData_5(function):
    function.ui.listSats.setRowCount(0)
    function.ui.listSats.setColumnCount(2)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("NOAA 8")
    function.ui.listSats.setItem(0, 1, entry)
    function.ui.listSats.insertRow(0)
    entry = QTableWidgetItem("Test1")
    function.ui.listSats.setItem(0, 1, entry)

    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    sat = EarthSatellite(tle[1], tle[2], name=tle[0])

    function.satellites.objects = {"NOAA 8": sat, "Test1": sat}
    function.satTableBaseValid = True
    ts = function.app.mount.obsSite.ts
    with mock.patch.object(
        function.app.mount.obsSite.ts, "now", return_value=ts.tt_jd(2458950.404976551)
    ):
        with mock.patch.object(MWidget, "positionCursorInTable"):
            function.extractSatelliteData(satName="NOAA 8")


def test_programSatToMount_3(function):
    tle = [
        "TIANGONG 1",
        "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
        "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072",
    ]
    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.satellites.objects = {"TIANGONG 2": EarthSatellite(tle[1], tle[2], name=tle[0])}
    function.app.mount.satellite.tleParams.name = "TIANGONG 2"
    with mock.patch.object(function.app.mount.satellite, "setTLE", return_value=False):
        function.programSatToMount(satName="TIANGONG 2")


def test_programSatToMount_4(function):
    tle = [
        "TIANGONG 1",
        "1 37820U 11053A   14314.79851609  .00064249  00000-0  44961-3 0  5637",
        "2 37820  42.7687 147.7173 0010686 283.6368 148.1694 15.73279710179072",
    ]
    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.satellites.objects = {"TIANGONG 2": EarthSatellite(tle[1], tle[2], name=tle[0])}
    function.app.mount.satellite.tleParams.name = "TIANGONG 2"
    with mock.patch.object(function.app.mount.satellite, "setTLE", return_value=True):
        with mock.patch.object(function.app.mount, "getTLE"):
            function.programSatToMount(satName="TIANGONG 2")


def test_chooseSatellite_1(function):
    satTab = function.ui.listSats
    function.app.deviceStat["mount"] = True
    with mock.patch.object(satTab, "item"):
        with mock.patch.object(function, "programSatToMount"):
            function.chooseSatellite()


def test_chooseSatellite_2(function):
    function.ui.autoSwitchTrack.setChecked(True)
    satTab = function.ui.listSats
    function.app.deviceStat["mount"] = False
    with mock.patch.object(satTab, "item"):
        with mock.patch.object(function, "extractSatelliteData"):
            with mock.patch.object(function, "showSatPasses"):
                function.chooseSatellite()


def test_getSatelliteDataFromDatabase_2(function):
    class Name:
        name = ""

    tleParams = Name()
    with mock.patch.object(function, "extractSatelliteData"):
        with mock.patch.object(function, "showSatPasses"):
            function.getSatelliteDataFromDatabase(tleParams=tleParams)


def test_updateOrbit_1(function):
    function.satellite = None
    function.satSourceValid = False
    function.updateOrbit()


def test_updateOrbit_2(function):
    function.satellite = None
    function.satSourceValid = True
    function.updateOrbit()


def test_updateOrbit_4(function):
    function.satSourceValid = True
    function.satellite = "test"
    function.updateOrbit()


def test_selectStartEnd_1(function):
    function.satOrbits = []
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_2(function):
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_3(function):
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [{"test": ts.tt_jd(2459215.5), "test": ts.tt_jd(2459215.7)}]
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_4(function):
    function.app.deviceStat["mount"] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "test": ts.tt_jd(2459215.6),
            "test": ts.tt_jd(2459215.7),
        }
    ]
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_5(function):
    function.app.deviceStat["mount"] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "flip": ts.tt_jd(2459215.6),
            "settle": ts.tt_jd(2459215.7),
        }
    ]
    function.ui.satBeforeFlip.setChecked(False)
    function.ui.satAfterFlip.setChecked(False)
    s, e = function.selectStartEnd()
    assert s == 0
    assert e == 0


def test_selectStartEnd_6(function):
    function.app.deviceStat["mount"] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "flip": ts.tt_jd(2459215.6),
            "settle": ts.tt_jd(2459215.7),
        }
    ]
    function.ui.satBeforeFlip.setChecked(True)
    function.ui.satAfterFlip.setChecked(True)
    s, e = function.selectStartEnd()
    assert s == 2459215.5
    assert e == 2459215.7


def test_selectStartEnd_7(function):
    function.app.deviceStat["mount"] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "flipLate": ts.tt_jd(2459215.6),
            "settle": ts.tt_jd(2459215.7),
        }
    ]
    function.ui.satBeforeFlip.setChecked(True)
    function.ui.satAfterFlip.setChecked(False)
    s, e = function.selectStartEnd()
    assert s == 2459215.5
    assert e == 2459215.6


def test_selectStartEnd_8(function):
    function.app.deviceStat["mount"] = True
    ts = function.app.mount.obsSite.ts
    function.satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "flipEarly": ts.tt_jd(2459215.6),
            "settle": ts.tt_jd(2459215.7),
        }
    ]
    function.ui.satBeforeFlip.setChecked(False)
    function.ui.satAfterFlip.setChecked(True)
    s, e = function.selectStartEnd()
    assert s == 2459215.6
    assert e == 2459215.7


def test_filterHorizon_1(function):
    function.ui.avoidHorizon.setChecked(False)
    start = 100 / 86400
    end = 109 / 86400
    alt = [5, 6, 7, 45, 46, 47, 48, 7, 6, 5]
    az = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    function.app.data.horizonP = [(40, 40)]
    start, end, alt, az = function.filterHorizon(start, end, alt, az)
    assert alt == [5, 6, 7, 45, 46, 47, 48, 7, 6, 5]
    assert az == [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    assert start == 100 / 86400
    assert end == 109 / 86400


def test_filterHorizon_2(function):
    function.ui.avoidHorizon.setChecked(True)
    start = 100 / 86400
    end = 109 / 86400
    alt = [5, 6, 7, 45, 46, 47, 48, 7, 6, 5]
    az = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    function.app.data.horizonP = [(40, 40)]
    start, end, alt, az = function.filterHorizon(start, end, alt, az)
    assert np.array_equal(alt, [45, 46, 47, 48])
    assert np.array_equal(az, [40, 50, 60, 70])
    assert start == (100 + 3) / 86400
    assert end == (109 - 3) / 86400


def test_startProg_1(function):
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(function, "selectStartEnd", return_value=(1, 2)):
            with mock.patch.object(function, "calcTrajectoryData", return_value=(0, 0)):
                with mock.patch.object(
                    function, "filterHorizon", return_value=(0, 0, [1], [1])
                ):
                    with mock.patch.object(function.app.mount, "progTrajectory"):
                        function.startProg()


def test_startProg_2(function):
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(function, "selectStartEnd", return_value=(0, 0)):
            function.startProg()


def test_startProg_3(function):
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(function, "selectStartEnd", return_value=(1, 1)):
            with mock.patch.object(function, "calcTrajectoryData", return_value=(0, 0)):
                with mock.patch.object(function, "filterHorizon", return_value=(0, 0, [], [])):
                    function.startProg()


def test_changeUnitTimeUTC_1(function):
    with mock.patch.object(function, "showSatPasses"):
        with mock.patch.object(function, "updateSatelliteTrackGui"):
            function.changeUnitTimeUTC()


def test_updateSatelliteTrackGui_1(function):
    ts = function.app.mount.obsSite.ts

    class Test:
        jdStart = ts.tt_jd(2459215.5)
        jdEnd = ts.tt_jd(2459215.6)
        flip = True
        message = "e"
        altitude = 1

    function.satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "flip": ts.tt_jd(2459215.6),
            "culminate": ts.tt_jd(2459215.6),
            "settle": ts.tt_jd(2459215.7),
        }
    ]

    function.updateSatelliteTrackGui(Test())


def test_updateSatelliteTrackGui_2(function):
    ts = function.app.mount.obsSite.ts

    class Test:
        jdStart = ts.tt_jd(2459215.5)
        jdEnd = ts.tt_jd(2459215.6)
        flip = False
        message = "e"
        altitude = 1

    function.satOrbits = [
        {
            "rise": ts.tt_jd(2459215.5),
            "flip": ts.tt_jd(2459215.6),
            "culminate": ts.tt_jd(2459215.6),
            "settle": ts.tt_jd(2459215.7),
        }
    ]

    function.updateSatelliteTrackGui(Test())


def test_updateSatelliteTrackGui_3(function):
    ts = function.app.mount.obsSite.ts

    class Test:
        jdStart = ts.tt_jd(2459215.5)
        jdEnd = ts.tt_jd(2459215.6)
        flip = True
        message = "e"
        altitude = 1

    function.satOrbits = []

    function.updateSatelliteTrackGui(Test())


def test_tle_export_1(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]

    satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    line1, line2 = export_tle(satellite.model)

    assert tle[0] == satellite.name
    assert tle[1] == line1
    assert tle[2] == line2


def test_updateInternalTrackGui_1(function):
    with mock.patch.object(function, "updateSatelliteTrackGui"):
        function.updateInternalTrackGui([])


def test_startTrack_1(function):
    function.app.deviceStat["mount"] = False
    function.startTrack()


def test_startTrack_2(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(
        function.app.mount.satellite, "slewTLE", return_value=(False, "test")
    ):
        function.startTrack()


def test_startTrack_3(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(
        function.app.mount.satellite, "slewTLE", return_value=(False, "test")
    ):
        function.startTrack()


def test_startTrack_4(function):
    function.app.deviceStat["mount"] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(
        function.app.mount.satellite, "slewTLE", return_value=(False, "test")
    ):
        function.startTrack()


def test_startTrack_5(function):
    function.app.deviceStat["mount"] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(
        function.app.mount.satellite, "slewTLE", return_value=(True, "test")
    ):
        function.startTrack()


def test_startTrack_6(function):
    function.app.deviceStat["mount"] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(
        function.app.mount.satellite, "slewTLE", return_value=(True, "test")
    ):
        with mock.patch.object(function.app.mount.obsSite, "unpark", return_value=True):
            function.startTrack()


def test_startTrack_7(function):
    function.app.deviceStat["mount"] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(
        function.app.mount.satellite, "slewTLE", return_value=(True, "test")
    ):
        with mock.patch.object(function.app.mount.obsSite, "unpark", return_value=False):
            with mock.patch.object(
                function.app.mount.satellite, "clearTrackingOffsets", return_value=True
            ):
                function.startTrack()


def test_stopTrack_1(function):
    function.app.deviceStat["mount"] = False
    function.stopTrack()


def test_stopTrack_2(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function.app.mount.obsSite, "startTracking", return_value=False):
        function.stopTrack()


def test_stopTrack_3(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function.app.mount.obsSite, "startTracking", return_value=True):
        function.stopTrack()


def test_toggleTrackingOffset_1(function):
    class OBS:
        status = 10

    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=True):
        function.toggleTrackingOffset(obs=OBS())


def test_toggleTrackingOffset_2(function):
    class OBS:
        status = 1

    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=True):
        function.toggleTrackingOffset(obs=OBS())


def test_toggleTrackingOffset_3(function):
    class OBS:
        status = 1

    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=False):
        function.toggleTrackingOffset(obs=OBS())


def test_followMount_1(function):
    obs = function.app.mount.obsSite
    function.ui.domeAutoFollowSat.setChecked(False)
    obs.status = 1
    function.followMount(obs)


def test_followMount_2(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(False)
    function.followMount(obs)


def test_followMount_3(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(True)
    function.app.deviceStat["dome"] = False
    function.followMount(obs)


def test_followMount_4(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(True)
    function.app.deviceStat["dome"] = True
    obs.Az = Angle(degrees=1)
    obs.Alt = Angle(degrees=1)
    function.followMount(obs)


def test_setTrackingOffsets_1(function):
    with mock.patch.object(
        function.app.mount.satellite, "setTrackingOffsets", return_value=True
    ):
        function.setTrackingOffsets()


def test_setTrackingOffsets_2(function):
    with mock.patch.object(
        function.app.mount.satellite, "setTrackingOffsets", return_value=False
    ):
        function.setTrackingOffsets()
