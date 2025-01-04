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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock

# external packages
from PySide6.QtWidgets import QTableWidgetItem, QTableWidget, QComboBox
from PySide6.QtWidgets import QGroupBox
from skyfield.api import EarthSatellite
from skyfield.api import Angle
from sgp4.exporter import export_tle
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import gui
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabSat_Track import SatTrack
from gui.mainWaddon.astroObjects import AstroObjects
from gui.utilities.toolsQtWidget import MWidget


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
        suc = function.enableGuiFunctions()
        assert not suc


def test_enableGuiFunctions_2(function):
    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=True):
        suc = function.enableGuiFunctions()
        assert suc


def test_clearTrackingParameters(function):
    function.clearTrackingParameters()


def test_updatePasses_1(function):
    function.app.mount.setting.meridianLimitTrack = 10
    function.lastMeridianLimit = 5
    with mock.patch.object(function, "showSatPasses"):
        suc = function.updatePasses()
        assert suc
        assert function.lastMeridianLimit == 10


def test_updatePasses_2(function):
    function.app.mount.setting.meridianLimitTrack = None
    function.lastMeridianLimit = 5
    with mock.patch.object(function, "showSatPasses"):
        suc = function.updatePasses()
        assert not suc
        assert function.lastMeridianLimit == 5


def test_sendSatelliteData_1(function):
    function.satellite = None
    suc = function.signalSatelliteData()
    assert not suc


def test_sendSatelliteData_3(function):
    tle = [
        "NOAA 8",
        "1 13923U 83022A   20076.90417581  .00000005  00000-0  19448-4 0  9998",
        "2 13923  98.6122  63.2579 0016304  96.9736 263.3301 14.28696485924954",
    ]
    function.satellite = EarthSatellite(tle[1], tle[2], name=tle[0])
    function.satOrbits = 1
    suc = function.signalSatelliteData()
    assert suc


def test_showSatPasses_0(function):
    function.satellite = None
    suc = function.showSatPasses()
    assert not suc


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
            gui.mainWaddon.tabSat_Track, "calcSatPasses", return_value=satOrbits
        ):
            with mock.patch.object(function, "progTrajectoryToMount"):
                suc = function.showSatPasses()
                assert suc


def test_showSatPasses_2(function):
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
            gui.mainWaddon.tabSat_Track, "calcSatPasses", return_value=satOrbits
        ):
            with mock.patch.object(function, "progTrajectoryToMount"):
                suc = function.showSatPasses()
                assert suc


def test_showSatPasses_3(function):
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
            gui.mainWaddon.tabSat_Track, "calcSatPasses", return_value=satOrbits
        ):
            with mock.patch.object(function, "progTrajectoryToMount"):
                suc = function.showSatPasses()
                assert suc


def test_extractSatelliteData_0(function):
    function.satellites.objects = {"NOAA 8": "sat", "Test1": "sat"}

    function.satTableBaseValid = False
    suc = function.extractSatelliteData(satName="Tjan")
    assert not suc


def test_extractSatelliteData_1(function):
    function.satellites.objects = {"NOAA 8": "sat", "Test1": "sat"}

    function.satTableBaseValid = True
    suc = function.extractSatelliteData(satName="Tjan")
    assert not suc


def test_extractSatelliteData_2(function):
    function.ui.listSats.clear()
    function.satellites.objects = {"Test0": "", "Test1": ""}

    function.satTableBaseValid = True
    suc = function.extractSatelliteData(satName="NOAA 8")
    assert not suc


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
            suc = function.extractSatelliteData(satName="NOAA 8")
            assert suc


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
            suc = function.extractSatelliteData(satName="NOAA 8")
            assert suc


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
            suc = function.extractSatelliteData(satName="NOAA 8")
            assert suc


def test_programSatToMount_1(function):
    suc = function.programSatToMount()
    assert not suc


def test_programSatToMount_2(function):
    suc = function.programSatToMount(satName="test")
    assert not suc


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
        suc = function.programSatToMount(satName="TIANGONG 2")
        assert not suc


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
            suc = function.programSatToMount(satName="TIANGONG 2")
            assert suc


def test_chooseSatellite_1(function):
    satTab = function.ui.listSats
    function.app.deviceStat["mount"] = True
    with mock.patch.object(satTab, "item"):
        with mock.patch.object(function, "extractSatelliteData"):
            with mock.patch.object(function, "showSatPasses"):
                function.chooseSatellite()


def test_chooseSatellite_2(function):
    function.ui.autoSwitchTrack.setChecked(True)
    satTab = function.ui.listSats
    function.app.deviceStat["mount"] = False
    with mock.patch.object(satTab, "item"):
        with mock.patch.object(function, "extractSatelliteData"):
            with mock.patch.object(function, "showSatPasses"):
                function.chooseSatellite()


def test_getSatelliteDataFromDatabase_1(function):
    class Name:
        name = ""
        jdStart = 1
        jdEnd = 1
        flip = False
        message = ""
        altitude = None
        azimuth = None

    function.app.mount.satellite.tleParams = Name()
    suc = function.getSatelliteDataFromDatabase()
    assert not suc


def test_getSatelliteDataFromDatabase_2(function):
    class Name:
        name = ""

    tleParams = Name()
    with mock.patch.object(function, "extractSatelliteData"):
        with mock.patch.object(function, "showSatPasses"):
            suc = function.getSatelliteDataFromDatabase(tleParams=tleParams)
            assert suc


def test_updateOrbit_1(function):
    function.satellite = None
    function.satSourceValid = False
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_2(function):
    function.satellite = None
    function.satSourceValid = True
    suc = function.updateOrbit()
    assert not suc


def test_updateOrbit_4(function):
    function.satSourceValid = True
    function.satellite = "test"
    suc = function.updateOrbit()
    assert suc


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


def test_progTrajectoryToMount_1(function):
    function.app.deviceStat["mount"] = True
    function.ui.useInternalSatCalc.setChecked(True)
    with mock.patch.object(function, "selectStartEnd", return_value=(0, 0)):
        suc = function.progTrajectoryToMount()
        assert not suc


def test_progTrajectoryToMount_2(function):
    function.app.deviceStat["mount"] = True
    function.ui.useInternalSatCalc.setChecked(True)
    with mock.patch.object(function, "selectStartEnd", return_value=(1, 1)):
        with mock.patch.object(function, "calcTrajectoryData", return_value=(0, 0)):
            with mock.patch.object(function, "filterHorizon", return_value=(0, 0, 0, 0)):
                with mock.patch.object(function, "signalSatelliteData"):
                    suc = function.progTrajectoryToMount()
                    assert suc


def test_progTrajectoryToMount_3(function):
    function.app.deviceStat["mount"] = False
    function.ui.useInternalSatCalc.setChecked(False)
    with mock.patch.object(function, "selectStartEnd", return_value=(1, 1)):
        with mock.patch.object(function.app.mount, "calcTLE"):
            with mock.patch.object(function, "signalSatelliteData"):
                suc = function.progTrajectoryToMount()
                assert suc


def test_progTrajectoryToMount_4(function):
    function.app.deviceStat["mount"] = True
    function.ui.useInternalSatCalc.setChecked(False)
    with mock.patch.object(function, "selectStartEnd", return_value=(1, 1)):
        with mock.patch.object(function.app.mount, "calcTLE"):
            with mock.patch.object(function, "signalSatelliteData"):
                suc = function.progTrajectoryToMount()
                assert suc


def test_startProg_1(function):
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(function, "selectStartEnd", return_value=(1, 2)):
            with mock.patch.object(function, "calcTrajectoryData", return_value=(0, 0)):
                with mock.patch.object(function, "filterHorizon", return_value=(0, 0, [1], [1])):
                    with mock.patch.object(function.app.mount, "progTrajectory"):
                        suc = function.startProg()
                        assert suc


def test_startProg_2(function):
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(function, "selectStartEnd", return_value=(0, 0)):
            suc = function.startProg()
            assert not suc


def test_startProg_3(function):
    with mock.patch.object(function, "clearTrackingParameters"):
        with mock.patch.object(function, "selectStartEnd", return_value=(1, 1)):
            with mock.patch.object(function, "calcTrajectoryData", return_value=(0, 0)):
                with mock.patch.object(function, "filterHorizon", return_value=(0, 0, [], [])):
                    suc = function.startProg()
                    assert not suc


def test_updateSatelliteTrackGui_1(function):
    suc = function.updateSatelliteTrackGui()
    assert not suc


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

    suc = function.updateSatelliteTrackGui(Test())
    assert suc


def test_updateSatelliteTrackGui_3(function):
    ts = function.app.mount.obsSite.ts

    class Test:
        jdStart = None
        jdEnd = None
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

    suc = function.updateSatelliteTrackGui(Test())
    assert suc


def test_updateInternalTrackGui_1(function):
    with mock.patch.object(function, "updateSatelliteTrackGui"):
        function.updateInternalTrackGui()


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


def test_startTrack_1(function):
    function.app.deviceStat["mount"] = False
    suc = function.startTrack()
    assert not suc


def test_startTrack_2(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function.app.mount.satellite, "slewTLE", return_value=(False, "test")):
        suc = function.startTrack()
        assert not suc


def test_startTrack_3(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function.app.mount.satellite, "slewTLE", return_value=(False, "test")):
        suc = function.startTrack()
        assert not suc


def test_startTrack_4(function):
    function.app.deviceStat["mount"] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite, "slewTLE", return_value=(False, "test")):
        suc = function.startTrack()
        assert not suc


def test_startTrack_5(function):
    function.app.deviceStat["mount"] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite, "slewTLE", return_value=(True, "test")):
        suc = function.startTrack()
        assert suc


def test_startTrack_6(function):
    function.app.deviceStat["mount"] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite, "slewTLE", return_value=(True, "test")):
        with mock.patch.object(function.app.mount.obsSite, "unpark", return_value=True):
            suc = function.startTrack()
            assert suc


def test_startTrack_7(function):
    function.app.deviceStat["mount"] = True
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.satellite, "slewTLE", return_value=(True, "test")):
        with mock.patch.object(function.app.mount.obsSite, "unpark", return_value=False):
            with mock.patch.object(
                function.app.mount.satellite, "clearTrackingOffsets", return_value=True
            ):
                suc = function.startTrack()
                assert suc


def test_stopTrack_1(function):
    function.app.deviceStat["mount"] = False
    suc = function.stopTrack()
    assert not suc


def test_stopTrack_2(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function.app.mount.obsSite, "startTracking", return_value=False):
        suc = function.stopTrack()
        assert not suc


def test_stopTrack_3(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function.app.mount.obsSite, "startTracking", return_value=True):
        suc = function.stopTrack()
        assert suc


def test_toggleTrackingOffset_1(function):
    class OBS:
        status = 10

    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=True):
        suc = function.toggleTrackingOffset(obs=OBS())
        assert suc


def test_toggleTrackingOffset_2(function):
    class OBS:
        status = 1

    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=True):
        suc = function.toggleTrackingOffset(obs=OBS())
        assert suc


def test_toggleTrackingOffset_3(function):
    class OBS:
        status = 1

    with mock.patch.object(function.app.mount.firmware, "checkNewer", return_value=False):
        suc = function.toggleTrackingOffset(obs=OBS())
        assert not suc


def test_followMount_1(function):
    obs = function.app.mount.obsSite
    function.ui.domeAutoFollowSat.setChecked(False)
    obs.status = 1
    suc = function.followMount(obs)
    assert not suc


def test_followMount_2(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(False)
    suc = function.followMount(obs)
    assert not suc


def test_followMount_3(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(True)
    function.app.deviceStat["dome"] = False
    suc = function.followMount(obs)
    assert not suc


def test_followMount_4(function):
    obs = function.app.mount.obsSite
    obs.status = 10
    function.ui.domeAutoFollowSat.setChecked(True)
    function.app.deviceStat["dome"] = True
    obs.Az = Angle(degrees=1)
    obs.Alt = Angle(degrees=1)
    suc = function.followMount(obs)
    assert suc


def test_setTrackingOffsets_1(function):
    with mock.patch.object(function.app.mount.satellite, "setTrackingOffsets", return_value=True):
        suc = function.setTrackingOffsets()
        assert suc


def test_setTrackingOffsets_2(function):
    with mock.patch.object(function.app.mount.satellite, "setTrackingOffsets", return_value=False):
        suc = function.setTrackingOffsets()
        assert not suc
