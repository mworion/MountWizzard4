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

import pytest
from astroquery.simbad import Simbad
from mw4.gui.mainWaddon.tabModel_BuildPoints import BuildPoints
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from pathlib import Path
from skyfield.api import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
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


def test_genBuildDSO_2(function):
    def test():
        function.app.data.buildP = [1] * 20

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(function.app.data, "generateDSOPath"):
        function.genBuildDSO()
    function.autoDeletePoints = t


def test_genBuildDSO_3(function):
    def test():
        function.app.data.buildP = [1] * 20

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = None
    function.simbadDec = None
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(function.app.data, "generateDSOPath"):
        function.genBuildDSO()
    function.autoDeletePoints = t


def test_genBuildDSO_4(function):
    def test():
        function.app.data.buildP = [1] * 20

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = None
    function.simbadDec = None
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(function.app.data, "generateDSOPath"):
        function.genBuildDSO()
    function.autoDeletePoints = t


def test_genBuildDSO_5(function):
    def test():
        function.app.data.buildP = [1] * 20

    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    t = function.autoDeletePoints
    function.autoDeletePoints = test
    with mock.patch.object(function.app.data, "generateDSOPath"):
        function.genBuildDSO()
    function.autoDeletePoints = t


def test_genBuildDSO_6(function):
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
    with mock.patch.object(function.app.data, "generateDSOPath"):
        with mock.patch.object(function.app.data, "ditherPoints"):
            function.genBuildDSO()
    function.autoDeletePoints = t


def test_genBuildDSO_7(function):
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
    with mock.patch.object(function.app.data, "generateDSOPath"):
        with mock.patch.object(function.app.data, "ditherPoints"):
            function.genBuildDSO()
    function.autoDeletePoints = t


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
    with mock.patch.object(Path, "is_file", return_value=False):
        with mock.patch.object(MWidget, "openFile", return_value=Path("test.bpts")):
            with mock.patch.object(function.app.data, "loadBuildP", return_value=True):
                function.loadBuildFile()


def test_loadBuildFile_2(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function.app.data, "loadBuildP", return_value=True):
            with mock.patch.object(MWidget, "openFile", return_value=Path("")):
                function.loadBuildFile()


def test_loadBuildFile_3(function):
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(MWidget, "openFile", return_value=Path("test.bpts")):
            with mock.patch.object(function.app.data, "loadBuildP", return_value=False):
                function.loadBuildFile()


def test_saveBuildFile_1(function):
    function.ui.buildPFileName.setText("test")
    with mock.patch.object(MWidget, "saveFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveBuildP", return_value=True):
            function.saveBuildFile()


def test_saveBuildFile_2(function):
    function.ui.buildPFileName.setText("")
    function.saveBuildFile()


def test_saveBuildFile_3(function):
    function.ui.buildPFileName.setText("test")
    with mock.patch.object(MWidget, "saveFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveBuildP", return_value=False):
            function.saveBuildFile()


def test_saveBuildFileAs_1(function):
    with mock.patch.object(MWidget, "saveFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveBuildP", return_value=True):
            function.saveBuildFileAs()


def test_saveBuildFileAs_2(function):
    with mock.patch.object(MWidget, "saveFile", return_value=Path("")):
        function.saveBuildFileAs()


def test_saveBuildFileAs_3(function):
    with mock.patch.object(MWidget, "saveFile", return_value=Path("test.bpts")):
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


def test_autoSortPoints_1(function):
    function.ui.noSort.setChecked(True)
    function.autoSortPoints()


def test_autoSortPoints_2(function):
    function.ui.sortAZ.setChecked(True)
    function.autoSortPoints()


def test_autoSortPoints_3(function):
    function.ui.sortALT.setChecked(True)
    function.autoSortPoints()


def test_autoSortPoints_4(function):
    function.ui.sortDomeAZ.setChecked(True)
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
    result = {"ra": 1.0, "dec": 2.5}

    function.ui.isOnline.setChecked(True)
    function.ui.generateQuery.setText("m31")
    with mock.patch.object(Simbad, "query_object", return_value=result):
        function.querySimbad()
