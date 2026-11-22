# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from astroquery.simbad import Simbad
from mw4.gui.mainWaddon.tabModel_BuildPoints import BuildPoints
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.logic.controllers.model.buildpointsSupport import MAX_ITERATIONS
from pathlib import Path
from skyfield.api import Angle
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    mainW = MWidget()
    mainW.app = makeApp()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = BuildPoints(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


@pytest.fixture(autouse=True)
def resetBuildPointState(function, qapp):
    waitForDSOWorker(function, qapp)
    function.app.buildPoint.buildP = []
    function.app.dReg.d["dome"].stat = False
    for checkbox in (
        function.ui.autoDeleteHorizon,
        function.ui.autoDeleteMeridian,
        function.ui.useSafetyMargin,
        function.ui.avoidFlip,
        function.ui.sortAZ,
        function.ui.sortALT,
        function.ui.sortDomeAZ,
        function.ui.ditherBuildPoints,
        function.ui.keepGeneratedPoints,
    ):
        checkbox.setChecked(False)
    yield
    waitForDSOWorker(function, qapp)


def waitForDSOWorker(function, qapp):
    for _ in range(MAX_ITERATIONS + 5):
        qapp.processEvents()
        if function.dsoGenerationParams is None:
            return
        function.app.threadPool.waitForDone(1000)
    qapp.processEvents()
    assert function.dsoGenerationParams is None


def test_initConfig_1(function):
    with mock.patch.object(function, "setupDsoGui"):
        function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_genBuildGrid_1(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(10)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)
    with mock.patch.object(function.app.data, "genGrid", return_value=True):
        function.genBuildGrid()


def test_genBuildGrid_2(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(9)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)
    with mock.patch.object(function.app.data, "genGrid", return_value=True):
        function.genBuildGrid()


def test_genBuildGrid_3(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(9)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)

    with mock.patch.object(function.app.data, "genGrid", return_value=False):
        function.genBuildGrid()


def test_genBuildAlign_1(function):
    with mock.patch.object(function.app.data, "genAlign", return_value=False):
        function.genBuildAlign()


def test_genBuildAlign_2(function):
    with mock.patch.object(function.app.data, "genAlign", return_value=True):
        function.genBuildAlign()


def test_genBuildCelestial_1(function):
    function.genBuildCelestial()


def test_genBuildCelestial_2(function):
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=False):
        function.genBuildCelestial()


def test_genBuildCelestial_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=True):
        function.genBuildCelestial()


def test_genBuildDSO_1(function):
    function.app.mount.obsSite.raJNow = None
    function.app.mount.obsSite.decJNow = None
    function.genBuildDSO()


def test_genBuildDSO_2(function, qapp):
    def test():
        function.app.data.buildP = [1] * 20

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(
        function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 20
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)
    function.autoDeletePoints = t


def test_genBuildDSO_3(function, qapp):
    def test():
        function.app.data.buildP = [1] * 20

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = None
    function.simbadDec = None
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(
        function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 20
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)
    function.autoDeletePoints = t


def test_genBuildDSO_4(function, qapp):
    def test():
        function.app.data.buildP = [1] * 20

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = None
    function.simbadDec = None
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(
        function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 20
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)
    function.autoDeletePoints = t


def test_genBuildDSO_5(function, qapp):
    def test():
        function.app.data.buildP = [1] * 20

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(
        function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 20
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)
    function.autoDeletePoints = t


def test_genBuildDSO_6(function, qapp):
    def test():
        function.app.data.buildP = []
        function.iteration = 0

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.ui.ditherBuildPoints.setChecked(True)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with (
        mock.patch.object(
            function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 20
        ),
        mock.patch.object(function.app.buildPoint, "ditherPoints"),
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)
    function.autoDeletePoints = t


def test_genBuildDSO_7(function, qapp):
    def test():
        function.app.data.buildP = [1]
        function.iteration = 0

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.ui.ditherBuildPoints.setChecked(True)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with (
        mock.patch.object(
            function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 20
        ),
        mock.patch.object(function.app.buildPoint, "ditherPoints"),
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)
    function.autoDeletePoints = t


def test_genBuildDSO_incomplete_generation_restores_controls(function, qapp):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.app.buildPoint.buildP = [[20, 30, 0]]
    function.ui.keepGeneratedPoints.setChecked(True)
    with (
        mock.patch.object(function.app.buildPoint, "generateDSOPath", return_value=None),
        mock.patch.object(function, "processPoints"),
        mock.patch.object(function, "msg") as message,
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)

    assert function.app.buildPoint.buildP == [[20, 30, 0]]
    assert function.ui.genBuildDSO.isEnabled()
    assert function.ui.numberDSOPoints.isEnabled()
    assert any("Could not generate enough" in call.args[3] for call in message.emit.call_args_list)


def test_genBuildDSO_worker_error_restores_controls(function, qapp):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    with (
        mock.patch.object(
            function.app.buildPoint,
            "generateDSOPath",
            side_effect=RuntimeError("test generation failure"),
        ),
        mock.patch.object(function, "msg") as message,
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)

    assert function.ui.genBuildDSO.isEnabled()
    assert function.ui.numberDSOPoints.isEnabled()
    assert any("DSO path generation failed" in call.args[3] for call in message.emit.call_args_list)


def test_genBuildDSO_retries_after_filtering(function, qapp):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.ui.numberDSOPoints.blockSignals(True)
    function.ui.numberDSOPoints.setValue(5)
    function.ui.numberDSOPoints.blockSignals(False)
    filteringCalls = 0

    def filterPoints():
        nonlocal filteringCalls
        filteringCalls += 1
        if filteringCalls == 1:
            function.app.buildPoint.buildP = [[10, 20, 0]]

    with (
        mock.patch.object(
            function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 5
        ) as generate,
        mock.patch.object(function, "autoDeletePoints", side_effect=filterPoints),
        mock.patch.object(function, "processPoints"),
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)

    assert generate.call_count == 2
    assert [call.args[4] for call in generate.call_args_list] == [5, 9]
    assert function.ui.genBuildDSO.isEnabled()
    assert function.ui.numberDSOPoints.isEnabled()


def test_genBuildDSO_stops_after_maximum_passes(function, qapp):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.ui.numberDSOPoints.blockSignals(True)
    function.ui.numberDSOPoints.setValue(2)
    function.ui.numberDSOPoints.blockSignals(False)
    with (
        mock.patch.object(
            function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]]
        ) as generate,
        mock.patch.object(
            function, "autoDeletePoints", side_effect=function.app.buildPoint.clearBuildP
        ),
        mock.patch.object(function, "processPoints"),
        mock.patch.object(function, "msg") as message,
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)

    assert generate.call_count == MAX_ITERATIONS - 1
    assert function.ui.genBuildDSO.isEnabled()
    assert function.ui.numberDSOPoints.isEnabled()
    assert any(
        "Could not generate the requested number" in call.args[3]
        for call in message.emit.call_args_list
    )


def test_genBuildGoldenSpiral_1(function):
    function.ui.numberSpiral.setValue(15)
    with mock.patch.object(function.app.data, "generateGoldenSpiral"):
        function.genBuildGoldenSpiral()


def test_genModel_1(function):
    class Star:
        alt = Angle(degrees=10)
        az = Angle(degrees=10)

    function.app.mount.model.starList.append(Star())
    with mock.patch.object(function.app.data, "addBuildP"):
        function.genModel()


def test_loadBuildFile_1(function):
    with (
        mock.patch.object(Path, "is_file", return_value=False),
        mock.patch.object(MWFileDialog, "getOpenFileName", return_value=Path("test.bpts")),
        mock.patch.object(function.app.data, "loadBuildP", return_value=True),
    ):
        function.loadBuildFile()


def test_loadBuildFile_2(function):
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(function.app.data, "loadBuildP", return_value=True),
        mock.patch.object(MWFileDialog, "getOpenFileName", return_value=Path("")),
    ):
        function.loadBuildFile()


def test_loadBuildFile_3(function):
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(MWFileDialog, "getOpenFileName", return_value=Path("test.bpts")),
        mock.patch.object(function.app.buildPoint, "loadBuildP", return_value=False),
    ):
        function.loadBuildFile()


def test_saveBuildFile_1(function):
    function.ui.buildPFileName.setText("test")
    with (
        mock.patch.object(MWFileDialog, "getSaveFileName", return_value=Path("test.bpts")),
        mock.patch.object(function.app.data, "saveBuildP", return_value=True),
    ):
        function.saveBuildFile()


def test_saveBuildFile_2(function):
    function.ui.buildPFileName.setText("")
    function.saveBuildFile()


def test_saveBuildFile_3(function):
    function.ui.buildPFileName.setText("test")
    with (
        mock.patch.object(MWFileDialog, "getSaveFileName", return_value=Path("test.bpts")),
        mock.patch.object(function.app.data, "saveBuildP", return_value=False),
    ):
        function.saveBuildFile()


def test_saveBuildFileAs_1(function):
    with (
        mock.patch.object(MWFileDialog, "getSaveFileName", return_value=Path("test.bpts")),
        mock.patch.object(function.app.data, "saveBuildP", return_value=True),
    ):
        function.saveBuildFileAs()


def test_saveBuildFileAs_2(function):
    with mock.patch.object(MWFileDialog, "getSaveFileName", return_value=Path("")):
        function.saveBuildFileAs()


def test_saveBuildFileAs_3(function):
    with (
        mock.patch.object(MWFileDialog, "getSaveFileName", return_value=Path("test.bpts")),
        mock.patch.object(function.app.data, "saveBuildP", return_value=False),
    ):
        function.saveBuildFileAs()


def test_genBuildFile_1(function):
    function.ui.buildPFileName.setText("")
    function.ui.autoDeleteHorizon.setChecked(True)
    function.genBuildFile()


def test_genBuildFile_2(function):
    function.ui.buildPFileName.setText("test")
    function.ui.autoDeleteHorizon.setChecked(True)
    with mock.patch.object(function.app.data, "loadBuildP", return_value=False):
        function.genBuildFile()


def test_genBuildFile_3(function):
    function.ui.buildPFileName.setText("test")
    function.ui.autoDeleteHorizon.setChecked(True)
    with mock.patch.object(function.app.data, "loadBuildP", return_value=True):
        function.genBuildFile()


def test_genBuildFile_4(function):
    function.ui.buildPFileName.setText("test")
    function.ui.autoDeleteHorizon.setChecked(False)
    with mock.patch.object(function.app.data, "loadBuildP", return_value=True):
        function.genBuildFile()


def test_clearBuildP_1(function):
    with mock.patch.object(function.app.data, "clearBuildP"):
        function.clearBuildP()


def test_autoDeletePoints(function):
    function.app.buildPoint.buildP = [[10, 20, 1]]
    function.ui.autoDeleteHorizon.setChecked(True)
    function.ui.autoDeleteMeridian.setChecked(True)
    function.ui.useSafetyMargin.setChecked(True)
    function.autoDeletePoints()


def test_autoSortPoints_1(function):
    function.ui.avoidFlip.setChecked(True)
    function.autoSortPoints()


def test_autoSortPoints_2(function):
    function.ui.sortAZ.setChecked(True)
    function.autoSortPoints()


def test_autoSortPoints_3(function):
    function.ui.sortALT.setChecked(True)
    function.autoSortPoints()


def test_autoSortPoints_4(function):
    function.app.dReg.d["dome"].stat = True
    function.app.buildPoint.buildP = [[10, 20, 1]]
    function.ui.sortDomeAZ.setChecked(True)
    with mock.patch.object(function.app.buildPoint, "sortDomeAz") as mockSort:
        function.autoSortPoints()
        mockSort.assert_called_once()


def test_buildPointsChanged(function):
    function.lastGenerator = "test"
    function.buildPointsChanged()
    assert function.lastGenerator == "none"


def test_rebuildPoints_1(function):
    function.lastGenerator = "align"
    with mock.patch.object(function, "processPoints"):
        function.rebuildPoints()


def test_rebuildPoints_2(function):
    function.lastGenerator = "none"
    with mock.patch.object(function, "processPoints") as m:
        function.rebuildPoints()
        m.assert_called_once()


def test_processPoints(function):
    with (
        mock.patch.object(function, "autoDeletePoints"),
        mock.patch.object(function, "autoSortPoints"),
    ):
        function.processPoints()


def test_setupDsoGui(function):
    function.setupDsoGui()


def test_querySimbad_1(function):
    function.app.isOnline = False
    function.querySimbad()


def test_querySimbad_2(function):
    function.app.isOnline = True
    function.ui.generateQuery.setText("")
    function.querySimbad()


def test_querySimbad_3(function):
    function.app.isOnline = True
    function.ui.generateQuery.setText("m31")
    with mock.patch.object(Simbad, "query_object", return_value=None):
        function.querySimbad()


def test_querySimbad_4(function):
    result = {"ra": 1.0, "dec": 2.5}

    function.app.isOnline = True
    function.ui.generateQuery.setText("m31")
    with mock.patch.object(Simbad, "query_object", return_value=result):
        function.querySimbad()


def test_genBuildGrid_fail(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(10)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)
    with (
        mock.patch.object(function.app.buildPoint, "genGrid", return_value=False),
        mock.patch.object(function, "msg") as mock_msg,
    ):
        function.genBuildGrid()
        mock_msg.emit.assert_called_once()


def test_genBuildAlign_fail(function):
    with (
        mock.patch.object(function.app.buildPoint, "genAlign", return_value=False),
        mock.patch.object(function, "msg") as mock_msg,
    ):
        function.genBuildAlign()
        mock_msg.emit.assert_called_once()


def test_genBuildCelestial_fail(function):
    with (
        mock.patch.object(function.app.buildPoint, "genGreaterCircle", return_value=False),
        mock.patch.object(function, "msg") as mock_msg,
    ):
        function.genBuildCelestial()
        mock_msg.emit.assert_called_once()


def test_genBuildCelestial_success_with_dither(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with (
        mock.patch.object(function.app.buildPoint, "genGreaterCircle", return_value=True),
        mock.patch.object(function.app.buildPoint, "ditherPoints"),
        mock.patch.object(function, "processPoints"),
    ):
        function.genBuildCelestial()


def test_genBuildGrid_success(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(10)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)
    with (
        mock.patch.object(function.app.buildPoint, "genGrid", return_value=True),
        mock.patch.object(function, "processPoints") as mockProc,
    ):
        function.genBuildGrid()
        mockProc.assert_called_once()


def test_genBuildDSO_iteration_zero(function, qapp):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = None
    function.simbadDec = None
    function.app.buildPoint.buildP = []
    with (
        mock.patch.object(
            function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 20
        ),
        mock.patch.object(function, "autoDeletePoints"),
        mock.patch.object(function, "processPoints"),
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)


def test_genBuildFile_loadFails(function):
    function.ui.buildPFileName.setText("nonexistent_file")
    with (
        mock.patch.object(function.app.buildPoint, "loadBuildP", return_value=False),
        mock.patch.object(function, "msg") as mockMsg,
    ):
        function.genBuildFile()
        mockMsg.emit.assert_called_once()


def test_autoSortPoints_dome_active(function):
    function.app.dReg.d["dome"].stat = True
    function.ui.sortDomeAZ.setChecked(True)
    with mock.patch.object(function.app.buildPoint, "sortDomeAz") as mockSort:
        function.autoSortPoints()
        mockSort.assert_called_once()
    function.app.dReg.d["dome"].stat = None
    function.ui.sortDomeAZ.setChecked(False)


def test_genBuildDSO_iteration_exhausted(function, qapp):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = None
    function.simbadDec = None
    function.ui.ditherBuildPoints.setChecked(False)
    function.ui.numberDSOPoints.blockSignals(True)
    function.ui.numberDSOPoints.setValue(50)
    function.ui.numberDSOPoints.blockSignals(False)

    def autoDelStub():
        function.app.buildPoint.buildP = [(10, 20, 1)]

    t = function.autoDeletePoints
    function.autoDeletePoints = autoDelStub
    with mock.patch.object(
        function.app.buildPoint, "generateDSOPath", return_value=[[10, 20, 0]] * 20
    ):
        function.genBuildDSO()
        waitForDSOWorker(function, qapp)
    function.autoDeletePoints = t


def test_genBuildGoldenSpiral_iteration_exhausted(function):
    function.ui.numberSpiral.blockSignals(True)
    function.ui.numberSpiral.setValue(100)
    function.ui.numberSpiral.blockSignals(False)

    def keepBuildP(**kwargs):
        function.app.buildPoint.buildP = [1]

    with (
        mock.patch.object(function.app.buildPoint, "generateGoldenSpiral", side_effect=keepBuildP),
        mock.patch.object(function, "autoDeletePoints"),
        mock.patch.object(function, "processPoints"),
    ):
        function.genBuildGoldenSpiral()
