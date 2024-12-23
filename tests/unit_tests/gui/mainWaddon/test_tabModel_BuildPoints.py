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
from pathlib import Path

# external packages
from astroquery.simbad import Simbad
from PySide6.QtWidgets import QWidget
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabModel_BuildPoints import BuildPoints


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = BuildPoints(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


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
        suc = function.genBuildGrid()
        assert suc


def test_genBuildGrid_2(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(9)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)
    with mock.patch.object(function.app.data, "genGrid", return_value=True):
        suc = function.genBuildGrid()
        assert suc


def test_genBuildGrid_3(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(9)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)

    with mock.patch.object(function.app.data, "genGrid", return_value=False):
        suc = function.genBuildGrid()
        assert not suc


def test_genBuildAlign_1(function):
    with mock.patch.object(function.app.data, "genAlign", return_value=False):
        suc = function.genBuildAlign()
        assert not suc


def test_genBuildAlign_2(function):
    with mock.patch.object(function.app.data, "genAlign", return_value=True):
        suc = function.genBuildAlign()
        assert suc


def test_genBuildMax_1(function):
    function.ui.autoDeleteHorizon.setChecked(False)
    function.genBuildMax()


def test_genBuildMax_2(function):
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=False):
        function.genBuildMax()


def test_genBuildMax_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=True):
        function.genBuildMax()


def test_genBuildMed_1(function):
    function.genBuildMed()


def test_genBuildMed_2(function):
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=False):
        function.genBuildMed()


def test_genBuildMed_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=True):
        function.genBuildMed()


def test_genBuildNorm_1(function):
    function.genBuildNorm()


def test_genBuildNorm_2(function):
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=False):
        function.genBuildNorm()


def test_genBuildNorm_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=True):
        function.genBuildNorm()


def test_genBuildMin_1(function):
    function.ui.autoDeleteHorizon.setChecked(True)
    function.genBuildMin()


def test_genBuildMin_1b(function):
    function.ui.autoDeleteHorizon.setChecked(False)
    function.genBuildMin()


def test_genBuildMin_2(function):
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=False):
        function.genBuildMin()


def test_genBuildMin_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data, "genGreaterCircle", return_value=True):
        function.genBuildMin()


def test_genBuildDSO_1(function):
    function.app.mount.obsSite.raJNow = None
    function.app.mount.obsSite.decJNow = None
    suc = function.genBuildDSO()
    assert not suc


def test_genBuildDSO_2(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    with mock.patch.object(function.app.data, "generateDSOPath", return_value=False):
        suc = function.genBuildDSO()
        assert not suc


def test_genBuildDSO_3(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = None
    function.simbadDec = None
    with mock.patch.object(function.app.data, "generateDSOPath", return_value=False):
        suc = function.genBuildDSO()
        assert not suc


def test_genBuildDSO_4(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = None
    function.simbadDec = None
    with mock.patch.object(function.app.data, "generateDSOPath", return_value=False):
        suc = function.genBuildDSO()
        assert not suc


def test_genBuildDSO_5(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    with mock.patch.object(function.app.data, "generateDSOPath", return_value=True):
        suc = function.genBuildDSO()
        assert suc


def test_genBuildDSO_6(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.ui.ditherBuildPoints.setChecked(True)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    with mock.patch.object(function.app.data, "generateDSOPath", return_value=True):
        with mock.patch.object(function.app.data, "ditherPoints"):
            suc = function.genBuildDSO()
            assert suc


def test_genBuildGoldenSpiral_1(function):
    def test():
        function.app.data.buildP = [1] * 20

    function.ui.numberSpiral.setValue(15)
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(function.app.data, "generateGoldenSpiral", return_value=True):
        function.genBuildGoldenSpiral()
    function.autoDeletePoints = t


def test_genBuildGoldenSpiral_2(function):
    function.ui.numberSpiral.setValue(2)
    with mock.patch.object(function.app.data, "generateGoldenSpiral", return_value=False):
        function.genBuildGoldenSpiral()


def test_genModel_1(function):
    class Star:
        alt = Angle(degrees=10)
        az = Angle(degrees=10)

    function.app.mount.model.starList.append(Star())
    with mock.patch.object(function.app.data, "addBuildP"):
        function.genModel()


def test_loadBuildFile_1(function):
    with mock.patch.object(Path, "is_file", return_value=False):
        with mock.patch.object(function, "openFile", return_value=Path("test.bpts")):
            with mock.patch.object(function.app.data, "loadBuildP", return_value=True):
                function.loadBuildFile()


def test_loadBuildFile_2(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function.app.data, "loadBuildP", return_value=True):
            with mock.patch.object(function, "openFile", return_value=Path("")):
                function.loadBuildFile()


def test_loadBuildFile_3(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function, "openFile", return_value=Path("test.bpts")):
            with mock.patch.object(function.app.data, "loadBuildP", return_value=False):
                function.loadBuildFile()


def test_saveBuildFile_1(function):
    function.ui.buildPFileName.setText("test")
    with mock.patch.object(function, "saveFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveBuildP", return_value=True):
            function.saveBuildFile()


def test_saveBuildFile_2(function):
    function.ui.buildPFileName.setText("")
    suc = function.saveBuildFile()
    assert not suc


def test_saveBuildFile_3(function):
    function.ui.buildPFileName.setText("test")
    with mock.patch.object(function, "saveFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveBuildP", return_value=False):
            function.saveBuildFile()


def test_saveBuildFileAs_1(function):
    with mock.patch.object(function, "saveFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveBuildP", return_value=True):
            function.saveBuildFileAs()


def test_saveBuildFileAs_2(function):
    with mock.patch.object(function, "saveFile", return_value=Path("")):
        function.saveBuildFileAs()


def test_saveBuildFileAs_3(function):
    with mock.patch.object(function, "saveFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveBuildP", return_value=False):
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
    function.ui.autoDeleteHorizon.setChecked(True)
    function.ui.autoDeleteMeridian.setChecked(True)
    function.ui.useSafetyMargin.setChecked(True)
    function.autoDeletePoints()


def test_doSortDomeAzData_1(function):
    function.sortRunning.lock()
    with mock.patch.object(function.app.data, "sort"):
        function.doSortDomeAzData((0, 1))


def test_sortDomeAzWorker_1(function):
    with mock.patch.object(
        function.app.mount,
        "calcMountAltAzToDomeAltAz",
        return_value=(0, Angle(degrees=10)),
    ):
        suc = function.sortDomeAzWorker([(10, 10, True)])
        assert suc


def test_sortDomeAzWorker_2(function):
    with mock.patch.object(
        function.app.mount, "calcMountAltAzToDomeAltAz", return_value=(None, None)
    ):
        suc = function.sortDomeAzWorker([(10, 10, True)])
        assert suc


def test_sortDomeAz_1(function):
    with mock.patch.object(function.app.threadPool, "start"):
        function.sortDomeAz([])
        function.sortRunning.unlock()


def test_sortDomeAz_2(function):
    function.sortRunning.lock()
    with mock.patch.object(function.app.threadPool, "start"):
        function.sortDomeAz([])


def test_sortMountAz(function):
    with mock.patch.object(function.app.data, "sort"):
        function.sortMountAz([])


def test_autoSortPoints_1(function):
    function.ui.sortEW.setChecked(False)
    function.ui.sortHL.setChecked(False)
    function.ui.avoidFlip.setChecked(False)
    function.ui.useDomeAz.setChecked(False)
    function.ui.useDomeAz.setEnabled(False)
    function.autoSortPoints()


def test_autoSortPoints_2(function):
    function.ui.sortEW.setChecked(True)
    function.ui.sortHL.setChecked(False)
    function.ui.avoidFlip.setChecked(False)
    function.ui.useDomeAz.setChecked(True)
    function.ui.useDomeAz.setEnabled(True)
    with mock.patch.object(function, "sortDomeAz"):
        function.autoSortPoints()


def test_autoSortPoints_3(function):
    function.ui.sortEW.setChecked(False)
    function.ui.sortHL.setChecked(False)
    function.ui.avoidFlip.setChecked(True)
    function.ui.useDomeAz.setChecked(False)
    function.ui.useDomeAz.setEnabled(False)
    with mock.patch.object(function, "sortMountAz"):
        function.autoSortPoints()


def test_buildPointsChanged(function):
    function.lastGenerator = "test"
    function.buildPointsChanged()
    assert function.lastGenerator == "none"


def test_rebuildPoints_1(function):
    function.lastGenerator = "align"
    with mock.patch.object(function, "processPoints"):
        function.rebuildPoints()


def test_processPoints(function):
    with mock.patch.object(function, "autoDeletePoints"):
        with mock.patch.object(function, "autoSortPoints"):
            function.processPoints()


def test_setupDsoGui(function):
    function.setupDsoGui()


def test_querySimbad_1(function):
    function.ui.isOnline.setChecked(False)
    function.querySimbad()


def test_querySimbad_2(function):
    function.ui.isOnline.setChecked(True)
    function.ui.generateQuery.setText("")
    function.querySimbad()


def test_querySimbad_3(function):
    function.ui.isOnline.setChecked(True)
    function.ui.generateQuery.setText("m31")
    with mock.patch.object(Simbad, "query_object", return_value=None):
        function.querySimbad()


def test_querySimbad_4(function):
    class Data2:
        data = ["10 00 00"]

    class Data:
        value = Data2()

    result = {"RA": Data(), "DEC": Data()}

    function.ui.isOnline.setChecked(True)
    function.ui.generateQuery.setText("m31")
    with mock.patch.object(Simbad, "query_object", return_value=result):
        function.querySimbad()
