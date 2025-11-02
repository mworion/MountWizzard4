############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide !

#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import time
import unittest.mock as mock
from pathlib import Path

import pytest

# external packages
from skyfield.api import Angle

import mw4.gui.mainWaddon
import mw4.gui.mainWaddon.tabModel
from mw4.gui.mainWaddon.tabModel import Model
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.logic.modelBuild.modelData import ModelData

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Model(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["mainW"] = {}
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_cancelBatch_1(function):
    function.modelData = None
    function.cancelBatch()


def test_cancelBatch_2(function):
    function.modelData = ModelData(App)
    function.cancelBatch()
    assert function.modelData.cancelBatch


def test_pauseBatch_1(function):
    function.modelData = None
    function.pauseBatch()


def test_pauseBatch_2(function):
    function.modelData = ModelData(App)
    function.pauseBatch()
    assert function.modelData.pauseBatch


def test_endBatch_1(function):
    function.modelData = None
    function.endBatch()


def test_endBatch_2(function):
    function.modelData = ModelData(App)
    function.endBatch()
    assert function.modelData.endBatch


def test_setModelOperationMode_1(function):
    function.setModelOperationMode(1)


def test_setModelOperationMode_2(function):
    function.setModelOperationMode(2)


def test_setModelOperationMode_3(function):
    function.setModelOperationMode(3)


def test_setModelOperationMode_4(function):
    function.setModelOperationMode(0)


def test_setModelOperationMode_5(function):
    function.setModelOperationMode(4)


def test_setupModelRunContextAndGuiStatus_1(function):
    function.app.uiWindows = {"showImageW": {"classObj": None}}
    function.setupModelRunContextAndGuiStatus()


def test_pauseBuild_1(function):
    function.ui.pauseModel.setProperty("pause", True)
    function.pauseBuild()
    assert not function.ui.pauseModel.property("pause")


def test_pauseBuild_2(function):
    function.ui.pauseModel.setProperty("pause", False)
    function.pauseBuild()
    assert function.ui.pauseModel.property("pause")


def test_programModelToMountFinish_1(function):
    function.modelData = ModelData(App)
    function.modelData.name = "Test"
    function.app.mount.signals.getModelDone.connect(function.programModelToMountFinish)
    with mock.patch.object(function.modelData, "generateSaveData"):
        with mock.patch.object(function.modelData, "saveModelData"):
            function.programModelToMountFinish()


def test_programModelToMount_1(function):
    function.modelData = ModelData(App)
    function.modelData.name = "Test"
    function.modelData.modelProgData = []
    with mock.patch.object(
        function.app.mount.model, "programModelFromStarList", return_value=False
    ):
        function.programModelToMount()


def test_programModelToMount_2(function):
    function.modelData = ModelData(App)
    function.modelData.name = "Test"
    function.modelData.modelProgData = [1, 2, 3]
    with mock.patch.object(
        function.app.mount.model, "programModelFromStarList", return_value=False
    ):
        function.programModelToMount()


def test_programModelToMount_3(function):
    function.modelData = ModelData(App)
    function.modelData.name = "Test"

    function.modelData.modelProgData = [1, 2, 3]
    with mock.patch.object(
        function.app.mount.model, "programModelFromStarList", return_value=True
    ):
        with mock.patch.object(function.app.mount.model, "storeName"):
            function.programModelToMount()


def test_checkModelRunConditions_1(function):
    function.app.data.buildP = [(0, 0, True)]
    suc = function.checkModelRunConditions(False)
    assert not suc


def test_checkModelRunConditions_2(function):
    function.app.data.buildP = [(0, 0, True)] * 100
    suc = function.checkModelRunConditions(False)
    assert not suc


def test_checkModelRunConditions_3(function):
    function.app.data.buildP = [(0, 0, True), (0, 0, True), (0, 0, False)]
    function.ui.excludeDonePoints.setChecked(True)
    suc = function.checkModelRunConditions(True)
    assert not suc


def test_checkModelRunConditions_4(function):
    function.app.data.buildP = [(0, 0, True), (0, 0, True), (0, 0, True)]
    suc = function.checkModelRunConditions(True)
    assert suc


def test_clearAlignAndBackup_1(function):
    with mock.patch.object(function.app.mount.model, "clearModel", return_value=False):
        suc = function.clearAlignAndBackup()
        assert not suc


def test_clearAlignAndBackup_2(function):
    with mock.patch.object(function.app.mount.model, "clearModel", return_value=True):
        with mock.patch.object(function.app.mount.model, "deleteName", return_value=False):
            with mock.patch.object(mw4.gui.mainWaddon.tabModel, "sleepAndEvents"):
                suc = function.clearAlignAndBackup()
                assert suc


def test_clearAlignAndBackup_3(function):
    with mock.patch.object(function.app.mount.model, "clearModel", return_value=True):
        with mock.patch.object(function.app.mount.model, "deleteName", return_value=True):
            with mock.patch.object(function.app.mount.model, "storeName", return_value=False):
                with mock.patch.object(mw4.gui.mainWaddon.tabModel, "sleepAndEvents"):
                    suc = function.clearAlignAndBackup()
                    assert suc


def test_clearAlignAndBackup_4(function):
    with mock.patch.object(function.app.mount.model, "clearModel", return_value=True):
        with mock.patch.object(function.app.mount.model, "deleteName", return_value=True):
            with mock.patch.object(function.app.mount.model, "storeName", return_value=True):
                with mock.patch.object(mw4.gui.mainWaddon.tabModel, "sleepAndEvents"):
                    suc = function.clearAlignAndBackup()
                    assert suc


def test_setupFilenamesAndDirectories_1(function):
    with mock.patch.object(Path, "is_dir", return_value=False):
        with mock.patch.object(os, "mkdir"):
            function.setupFilenamesAndDirectories()


def test_setupFilenamesAndDirectories_2(function):
    with mock.patch.object(Path, "is_dir", return_value=True):
        function.setupFilenamesAndDirectories()


def test_showProgress_1(function):
    function.showProgress(
        {
            "count": 10,
            "number": 1,
            "modelPercent": 10,
            "secondsElapsed": time.time(),
            "secondsEstimated": time.time(),
        }
    )


def test_setupModelInputData_1(function):
    function.app.data.buildP = [(0, 0, True), (0, 0, False), (0, 0, True)]
    function.setupModelInputData(True)


def test_setupBatchData_1(function):
    function.modelData = ModelData(App)
    with mock.patch.object(
        function, "setupFilenamesAndDirectories", return_value=(Path(""))
    ):
        function.setupBatchData()


def test_setModelTiming_1(function):
    function.modelData = ModelData(App())
    function.ui.progressiveTiming.setChecked(True)
    function.setModelTiming()
    assert function.modelData.timing == function.modelData.PROGRESSIVE


def test_setModelTiming_2(function):
    function.modelData = ModelData(App())
    function.ui.normalTiming.setChecked(True)
    function.setModelTiming()
    assert function.modelData.timing == function.modelData.NORMAL


def test_setModelTiming_3(function):
    function.modelData = ModelData(App())
    function.ui.conservativeTiming.setChecked(True)
    function.setModelTiming()
    assert function.modelData.timing == function.modelData.CONSERVATIVE


def test_runBatch_1(function):
    with mock.patch.object(function, "checkModelRunConditions", return_value=False):
        function.runBatch()


def test_runBatch_2(function):
    with mock.patch.object(function, "checkModelRunConditions", return_value=True):
        with mock.patch.object(function, "clearAlignAndBackup", return_value=False):
            function.runBatch()


def test_runBatch_3(function):
    with mock.patch.object(function, "checkModelRunConditions", return_value=True):
        with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
            with mock.patch.object(function, "setupModelInputData"):
                with mock.patch.object(function.modelData, "runModel"):
                    with mock.patch.object(function, "programModelToMount"):
                        function.runBatch()


def test_runFileModel_1(function):
    with mock.patch.object(MWidget, "openFile", return_value=[]):
        function.runFileModel()


def test_runFileModel_2(function):
    model = [
        {
            "altitude": 44.556745182012854,
            "azimuth": 37.194805194805184,
            "binning": 1.0,
            "countSequence": 0,
            "decJNowS": Angle(degrees=64.3246),
            "decJNowM": Angle(degrees=64.32841185357267),
            "errorDEC": -229.0210134131381,
            "errorRMS": 237.1,
            "errorRA": -61.36599559380768,
            "exposureTime": 3.0,
            "fastReadout": True,
            "julianDate": "2019-06-08T08:57:57Z",
            "name": "m-file-2019-06-08-08-57-44",
            "lenSequence": 3,
            "imagePath": "/Users/mw/PycharmProjects/MountWizzard4/image/m-file-2019-06-08-08"
            "-57-44/image-000.fits",
            "pierside": "W",
            "raJNowS": Angle(hours=8.42882),
            "raJNowM": Angle(hours=8.427692953132278),
            "siderealTime": Angle(hours=12.5),
            "subFrame": 100.0,
        },
    ]

    val = (model, "Error")
    function.modelData = ModelData(App)
    with mock.patch.object(MWidget, "openFile", return_value=[Path("test.model")]):
        with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
            with mock.patch.object(function.modelData, "buildProgModel"):
                with mock.patch.object(
                    mw4.gui.mainWaddon.tabModel, "loadModelsFromFile", return_value=val
                ):
                    with mock.patch.object(function.modelData, "buildProgModel"):
                        with mock.patch.object(function, "programModelToMount"):
                            function.runFileModel()
                            assert function.modelData.name == "test"


def test_runFileModel_3(function):
    function.modelData = ModelData(App)
    function.modelData.name = "Test"

    with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
        with mock.patch.object(
            MWidget, "openFile", return_value=[Path("test1.model"), Path("test2.model")]
        ):
            with mock.patch.object(
                function, "setupFilenamesAndDirectories", return_value=(Path("m-test1-add"))
            ):
                with mock.patch.object(
                    mw4.gui.mainWaddon.tabModel, "loadModelsFromFile", return_value=([], "")
                ):
                    with mock.patch.object(function.modelData, "buildProgModel"):
                        with mock.patch.object(function, "programModelToMount"):
                            function.runFileModel()
                            assert function.modelData.name == Path("m-test1-add")


def test_runFileModel_4(function):
    function.modelData = ModelData(App)
    function.modelData.name = "Test"
    with mock.patch.object(function, "clearAlignAndBackup", return_value=False):
        with mock.patch.object(
            MWidget, "openFile", return_value=[Path("test1.model"), Path("test2.model")]
        ):
            with mock.patch.object(
                function, "setupFilenamesAndDirectories", return_value=(Path("m-test1-add"))
            ):
                function.runFileModel()
