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

import mw4.gui.mainWaddon
import mw4.gui.mainWaddon.tabModel
import os
import pytest
import time
from mw4.gui.mainWaddon.tabModel import Model
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.nativeQt.qtMessageDialog import MWMessageDialog
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.logic.modelBuild.modelRun import ModelData
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
    mainW.ui.plateSolveDevice = mock.MagicMock()
    mainW.ui.plateSolveDevice.currentText.return_value = "Astrometry.net"
    window = Model(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_setWaitTimeFlip_1(function):
    function.setWaitTimeFlip()


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


def test_pauseBuild_1(function):
    function.ui.pauseModel.setProperty("pause", True)
    function.pauseBuild()
    assert function.ui.pauseModel.property("pause") == "false"


def test_pauseBuild_2(function):
    function.ui.pauseModel.setProperty("pause", False)
    function.pauseBuild()
    assert function.ui.pauseModel.property("pause")


def test_programModelToMountFinish_1(function):
    function.modelData = ModelData(App)
    function.modelData.modelName = "Test"
    function.app.mount.signals.getModelDone.connect(function.programModelToMountFinish)
    with (
        mock.patch.object(function.modelData, "generateSaveData"),
        mock.patch.object(function.modelData, "saveModelData"),
    ):
        function.programModelToMountFinish()


def test_programModelToMount_1(function):
    function.modelData = ModelData(App)
    function.modelData.modelName = "Test"
    function.modelData.modelProgData = []
    with mock.patch.object(
        function.app.mount.model, "programModelFromStarList", return_value=False
    ):
        function.programModelToMount()


def test_programModelToMount_2(function):
    function.modelData = ModelData(App)
    function.modelData.modelName = "Test"
    function.modelData.modelProgData = [1, 2, 3]
    with mock.patch.object(
        function.app.mount.model, "programModelFromStarList", return_value=False
    ):
        function.programModelToMount()


def test_programModelToMount_3(function):
    function.modelData = ModelData(App)
    function.modelData.modelName = "Test"

    function.modelData.modelProgData = [1, 2, 3]
    with (
        mock.patch.object(
            function.app.mount.model, "programModelFromStarList", return_value=True
        ),
        mock.patch.object(function.app.mount.model, "storeName"),
    ):
        function.programModelToMount()


def test_checkMountTimeSync_1(function):
    function.app.dReg["mount"].config.syncTimeNone = True
    result = function.checkMountTimeSync()
    assert result


def test_checkMountTimeSync_2(function):
    function.app.dReg["mount"].config.syncTimeNone = False
    with mock.patch.object(MWMessageDialog, "question", return_value=1):
        result = function.checkMountTimeSync()
        assert result


def test_checkMountTimeSync_3(function):
    function.app.dReg["mount"].config.syncTimeNone = False
    with mock.patch.object(MWMessageDialog, "question", return_value=0):
        result = function.checkMountTimeSync()
        assert not result


def test_checkModelRunConditions_1(function):
    function.app.buildPoint.buildP = [(0, 0, 1)]
    suc = function.checkModelRunConditions()
    assert not suc


def test_checkModelRunConditions_2(function):
    function.app.buildPoint.buildP = [[0, 0, 1]] * 100
    suc = function.checkModelRunConditions()
    assert not suc


def test_checkModelRunConditions_4(function):
    function.app.buildPoint.buildP = [[0, 0, 1], [0, 0, 1], [0, 0, 1]]
    suc = function.checkModelRunConditions()
    assert suc


def test_clearAlignAndBackup_1(function):
    continuation = mock.MagicMock()
    with mock.patch.object(function.app.mount.model, "clearModel", return_value=False):
        suc = function.clearAlignAndBackup(continuation)
    assert not suc
    continuation.assert_not_called()


def test_clearAlignAndBackup_2(function, qtbot):
    continuation = mock.MagicMock()
    with (
        mock.patch.object(function.app.mount.model, "clearModel", return_value=True),
        mock.patch.object(function, "CLEAR_WAIT_MS", 0),
        mock.patch.object(function, "backupAfterClear") as mockBackup,
    ):
        suc = function.clearAlignAndBackup(continuation)
        assert suc
        mockBackup.assert_not_called()
        qtbot.waitUntil(lambda: mockBackup.called, timeout=1000)
    mockBackup.assert_called_once_with(continuation)


def test_backupAfterClear_1(function):
    continuation = mock.MagicMock()
    with (
        mock.patch.object(function.app.mount.model, "storeName", return_value=False),
        mock.patch.object(function, "msg") as mockMsg,
    ):
        function.backupAfterClear(continuation)
    continuation.assert_called_once()
    assert mockMsg.emit.call_args_list[-1][0][0] == 2


def test_backupAfterClear_2(function):
    continuation = mock.MagicMock()
    with (
        mock.patch.object(function.app.mount.model, "storeName", return_value=True),
        mock.patch.object(function, "msg") as mockMsg,
    ):
        function.backupAfterClear(continuation)
    continuation.assert_called_once()
    assert mockMsg.emit.call_count == 1


def test_setupFilenamesAndDirectories_1(function):
    with mock.patch.object(Path, "is_dir", return_value=False), mock.patch.object(os, "mkdir"):
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


def test_showStatusExposure(function):
    status = ["test", 5, 1]
    function.showStatusExposure(status)


def test_showStatusSlew(function):
    status = ["test", 5, 1, ""]
    function.showStatusSlew(status)


def test_showStatusRetry(function):
    status = 3
    function.showStatusRetry(status)


def test_showStatusSolve_1(function):
    status = {"imagePath": Path("test"), "success": False, "message": "Error"}
    function.showStatusSolve(status)


def test_showStatusSolve_2(function):
    status = {
        "imagePath": Path("test"),
        "success": True,
        "angleS": Angle(degrees=2.5),
        "errorRMS_S": 1,
        "scaleS": 1.25,
    }
    function.showStatusSolve(status)


def test_setupModelInputData_1(function):
    function.modelData = ModelData(function.app)
    function.app.buildPoint.buildP = [[0, 0, 1], [0, 0, 1], [0, 0, 1]]
    function.setupModelInputData()


def test_setupBatchData_1(function):
    function.modelData = ModelData(App)
    with mock.patch.object(function, "setupFilenamesAndDirectories", return_value=(Path(""))):
        function.setupBatchData()


def test_setModelTiming_1(function):
    function.modelData = ModelData(App())
    function.ui.progressiveTiming.setChecked(True)
    function.setModelTiming()
    assert function.modelData.modelTiming == function.modelData.PROGRESSIVE


def test_setModelTiming_2(function):
    function.modelData = ModelData(App())
    function.ui.normalTiming.setChecked(True)
    function.setModelTiming()
    assert function.modelData.modelTiming == function.modelData.NORMAL


def test_setModelTiming_3(function):
    function.modelData = ModelData(App())
    function.ui.conservativeTiming.setChecked(True)
    function.setModelTiming()
    assert function.modelData.modelTiming == function.modelData.CONSERVATIVE


def test_runBatch_1(function):
    with mock.patch.object(function, "checkModelRunConditions", return_value=False):
        function.runBatch()


def test_runBatch_2(function):
    with (
        mock.patch.object(function, "checkModelRunConditions", return_value=True),
        mock.patch.object(function, "checkMountTimeSync", return_value=False),
    ):
        function.runBatch()


def test_runBatch_3(function):
    function.modelData = ModelData(function.app)
    with (
        mock.patch.object(function, "checkModelRunConditions", return_value=True),
        mock.patch.object(function, "checkMountTimeSync", return_value=True),
        mock.patch.object(function, "clearAlignAndBackup", return_value=False),
        mock.patch.object(function.app, "operationRunning") as mockOp,
    ):
        function.runBatch()
    assert mockOp.emit.call_args_list[-1][0][0] == function.STATUS_IDLE


def test_runBatch_4(function):
    function.modelData = ModelData(function.app)
    function.modelData.cancelBatch = True
    with (
        mock.patch.object(function, "checkModelRunConditions", return_value=True),
        mock.patch.object(function, "checkMountTimeSync", return_value=True),
        mock.patch.object(function, "clearAlignAndBackup", return_value=True) as mockClear,
        mock.patch.object(function.modelData, "runModel") as mockRun,
    ):
        function.runBatch()
    assert not function.modelData.cancelBatch
    mockClear.assert_called_once_with(function.startBatch)
    mockRun.assert_not_called()


def test_startBatch_1(function):
    function.modelData = ModelData(function.app)
    with (
        mock.patch.object(function, "setModelTiming"),
        mock.patch.object(function, "setupBatchData"),
        mock.patch.object(function, "setupModelInputData"),
        mock.patch.object(function.modelData, "runModel") as mockRun,
    ):
        function.startBatch()
    mockRun.assert_called_once()


def test_finishBatch_1(function):
    function.ui.parkMountAfterModel.setChecked(False)
    with (
        mock.patch.object(function, "programModelToMount") as mockProgram,
        mock.patch.object(function.app.dReg["mount"].obsSite, "park") as mockPark,
        mock.patch.object(function, "msg") as mockMsg,
    ):
        function.finishBatch(True)
    mockProgram.assert_not_called()
    mockPark.assert_not_called()
    assert "cancelled" in mockMsg.emit.call_args_list[0][0][3]


def test_finishBatch_2(function):
    function.ui.parkMountAfterModel.setChecked(True)
    with (
        mock.patch.object(function, "programModelToMount") as mockProgram,
        mock.patch.object(function.app.dReg["mount"].obsSite, "park") as mockPark,
        mock.patch.object(function.app, "operationRunning") as mockOp,
    ):
        function.finishBatch(False)
    mockProgram.assert_called_once()
    mockPark.assert_called_once()
    mockOp.emit.assert_called_once_with(function.STATUS_IDLE)
    function.ui.parkMountAfterModel.setChecked(False)


def test_finishBatch_connectedToModelData(function):
    function.modelData = ModelData(function.app)
    function.modelData.finished.connect(function.finishBatch)
    with mock.patch.object(function, "programModelToMount") as mockProgram:
        function.modelData.finished.emit(False)
    mockProgram.assert_called_once()


def test_runFileModel_1(function):
    with mock.patch.object(MWFileDialog, "getOpenFileNames", return_value=[]):
        function.runFileModel()


def test_runFileModel_2(function):
    function.modelData = ModelData(App)
    with (
        mock.patch.object(MWFileDialog, "getOpenFileNames", return_value=[Path("test.model")]),
        mock.patch.object(function, "clearAlignAndBackup", return_value=True) as mockClear,
        mock.patch.object(function, "programFileModel") as mockProgram,
    ):
        function.runFileModel()
    assert function.modelData.modelName == "test"
    mockClear.assert_called_once()
    mockProgram.assert_not_called()
    continuation = mockClear.call_args[0][0]
    continuation()
    mockProgram.assert_called_once_with([Path("test.model")])


def test_runFileModel_3(function):
    function.modelData = ModelData(App)
    function.modelData.modelName = "Test"
    files = [Path("test1.model"), Path("test2.model")]
    with (
        mock.patch.object(function, "clearAlignAndBackup", return_value=True),
        mock.patch.object(MWFileDialog, "getOpenFileNames", return_value=files),
        mock.patch.object(
            function, "setupFilenamesAndDirectories", return_value=Path("m-test1-add")
        ),
    ):
        function.runFileModel()
    assert function.modelData.modelName == "m-test1-add"


def test_runFileModel_4(function):
    function.modelData = ModelData(App)
    function.modelData.modelName = "Test"
    files = [Path("test1.model"), Path("test2.model")]
    with (
        mock.patch.object(function, "clearAlignAndBackup", return_value=False),
        mock.patch.object(MWFileDialog, "getOpenFileNames", return_value=files),
        mock.patch.object(
            function, "setupFilenamesAndDirectories", return_value=Path("m-test1-add")
        ),
        mock.patch.object(function.app, "operationRunning") as mockOp,
    ):
        function.runFileModel()
    assert mockOp.emit.call_args_list[-1][0][0] == function.STATUS_IDLE


def test_programFileModel_1(function):
    model = [{"success": True}]
    function.modelData = ModelData(App)
    with (
        mock.patch.object(
            mw4.gui.mainWaddon.tabModel, "loadModelsFromFile", return_value=(model, "")
        ),
        mock.patch.object(function.modelData, "buildProgModel"),
        mock.patch.object(function, "programModelToMount") as mockProgram,
    ):
        function.programFileModel([Path("test.model")])
    mockProgram.assert_called_once()


def test_programFileModel_2(function):
    function.modelData = ModelData(App)
    with (
        mock.patch.object(
            mw4.gui.mainWaddon.tabModel, "loadModelsFromFile", return_value=([], "Error")
        ),
        mock.patch.object(function.modelData, "buildProgModel"),
        mock.patch.object(function, "programModelToMount") as mockProgram,
        mock.patch.object(function, "msg") as mockMsg,
    ):
        function.programFileModel([Path("test.model")])
    mockProgram.assert_not_called()
    mockMsg.emit.assert_called_once_with(3, "Model", "Run error", "Error")
