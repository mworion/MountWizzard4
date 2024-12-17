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
# GUI with PySide for python !

#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import time
import shutil
import os
from pathlib import Path

# external packages
import skyfield.api
from mountcontrol.modelStar import ModelStar
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from logic.modelBuild.modelBatch import ModelBatch
from gui.mainWaddon.tabModel import Model
import gui.mainWaddon.tabModel
import gui.mainWaddon
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
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
    function.modelBatch = None
    function.cancelBatch()


def test_cancelBatch_2(function):
    function.modelBatch = ModelBatch(App)
    function.cancelBatch()
    assert function.modelBatch.cancelBatch


def test_pauseBatch_1(function):
    function.modelBatch = None
    function.pauseBatch()


def test_pauseBatch_2(function):
    function.modelBatch = ModelBatch(App)
    function.pauseBatch()
    assert function.modelBatch.pauseBatch


def test_endBatch_1(function):
    function.modelBatch = None
    function.endBatch()


def test_endBatch_2(function):
    function.modelBatch = ModelBatch(App)
    function.endBatch()
    assert function.modelBatch.endBatch


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


def test_updateModelProgress_1(function):
    function.timeStartModeling = time.time()
    mPoint = {}
    function.updateModelProgress(mPoint)


def test_updateModelProgress_2(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 3, "countSequence": 2}
    function.updateModelProgress(mPoint)


def test_updateModelProgress_3(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 2, "countSequence": 3}
    function.updateModelProgress(mPoint)


def test_updateModelProgress_4(function):
    mPoint = {"lenSequence": 0, "countSequence": 2}
    function.updateModelProgress(mPoint)
    function.timeStartModeling = time.time()


def test_updateModelProgress_5(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 3, "countSequence": 1}
    function.updateModelProgress(mPoint)


def test_updateModelProgress_6(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 3, "countSequence": -1}
    function.updateModelProgress(mPoint)


def test_updateModelProgress_7(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 3, "countSequence": 2}
    function.updateModelProgress(mPoint)


def test_updateModelProgress_8(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 0, "countSequence": -1}
    function.updateModelProgress(mPoint)


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


def test_retrofitModel_1(function):
    function.app.mount.model.starList = list()

    point = ModelStar(
        coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
        number=1,
        errorRMS=10,
        errorAngle=skyfield.api.Angle(degrees=0),
        obsSite=function.app.mount.obsSite,
    )
    stars = list()
    stars.append(point)
    mPoint = {}
    function.model = list()
    function.model.append(mPoint)
    with mock.patch.object(gui.mainWaddon.tabModel, "writeRetrofitData"):
        function.retrofitModel()


def test_saveModelFinish_1(function):
    def test():
        return

    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")
    function.modelName = "test"
    function.generateSaveData = test
    function.app.mount.signals.getModelDone.connect(function.saveModelFinish)
    function.saveModelFinish()


def test_programModelToMount_1(function):
    function.model = []
    with mock.patch.object(gui.mainWaddon.tabModel, "buildProgModel", return_value=[]):
        with mock.patch.object(
            function.app.mount.model, "programModelFromStarList", return_value=False
        ):
            suc = function.programModelToMount([])
            assert not suc


def test_programModelToMount_2(function):
    function.model = []
    with mock.patch.object(gui.mainWaddon.tabModel, "buildProgModel", return_value=[1, 2, 3]):
        with mock.patch.object(
            function.app.mount.model, "programModelFromStarList", return_value=False
        ):
            suc = function.programModelToMount([])
            assert not suc


def test_programModelToMount_3(function):
    with mock.patch.object(gui.mainWaddon.tabModel, "buildProgModel", return_value=[1, 2, 3]):
        with mock.patch.object(
            function.app.mount.model, "programModelFromStarList", return_value=True
        ):
            suc = function.programModelToMount([])
            assert suc


def test_processModelData_1(function):
    with mock.patch.object(function, "programModelToMount", return_value=False):
        function.processModelData()


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
            with mock.patch.object(gui.mainWaddon.tabModel, "sleepAndEvents"):
                suc = function.clearAlignAndBackup()
                assert suc


def test_clearAlignAndBackup_3(function):
    with mock.patch.object(function.app.mount.model, "clearModel", return_value=True):
        with mock.patch.object(function.app.mount.model, "deleteName", return_value=True):
            with mock.patch.object(function.app.mount.model, "storeName", return_value=False):
                with mock.patch.object(gui.mainWaddon.tabModel, "sleepAndEvents"):
                    suc = function.clearAlignAndBackup()
                    assert suc


def test_clearAlignAndBackup_4(function):
    with mock.patch.object(function.app.mount.model, "clearModel", return_value=True):
        with mock.patch.object(function.app.mount.model, "deleteName", return_value=True):
            with mock.patch.object(function.app.mount.model, "storeName", return_value=True):
                with mock.patch.object(gui.mainWaddon.tabModel, "sleepAndEvents"):
                    suc = function.clearAlignAndBackup()
                    assert suc


def test_loadProgramModel_1(function):
    val = ([], "Error")
    with mock.patch.object(function, "openFile", return_value=[]):
        with mock.patch.object(gui.mainWaddon.tabModel, "loadModelsFromFile", return_value=val):
            function.loadProgramModel()


def test_loadProgramModel_2(function):
    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")
    val = ([{}, {}], "OK")
    with mock.patch.object(function, "openFile", return_value=[Path(""), Path("")]):
        with mock.patch.object(gui.mainWaddon.tabModel, "loadModelsFromFile", return_value=val):
            with mock.patch.object(function, "clearAlignAndBackup", return_value=False):
                function.loadProgramModel()


def test_loadProgramModel_3(function):
    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")
    val = ([{}, {}], "OK")
    with mock.patch.object(function, "openFile", return_value=[Path(""), Path("")]):
        with mock.patch.object(gui.mainWaddon.tabModel, "loadModelsFromFile", return_value=val):
            with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
                with mock.patch.object(function, "programModelToMount", return_value=False):
                    function.loadProgramModel()


def test_loadProgramModel_4(function):
    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")
    val = ([{}, {}], "OK")
    with mock.patch.object(function, "openFile", return_value=[Path(""), Path("")]):
        with mock.patch.object(gui.mainWaddon.tabModel, "loadModelsFromFile", return_value=val):
            with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
                with mock.patch.object(function, "programModelToMount", return_value=True):
                    function.loadProgramModel()


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
    function.modelBatch = ModelBatch(App)
    with mock.patch.object(
        function, "setupFilenamesAndDirectories", return_value=(Path(""), "test")
    ):
        function.setupBatchData()


def test_processModelData_1(function):
    with mock.patch.object(function, "programModelToMount", return_value=True):
        function.processModelData()


def test_communicateModelBatchRun_1(function):
    function.modelBatch = ModelBatch(App)
    function.modelBatch.modelBuildData = []
    function.communicateModelBatchRun()


def test_communicateModelBatchRun_2(function):
    function.modelBatch = ModelBatch(App)
    function.modelBatch.modelBuildData = [1, 2, 3]
    function.communicateModelBatchRun()


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
                with mock.patch.object(function, "setupModelInputData"):
                    with mock.patch.object(function, "setupBatchData"):
                        with mock.patch.object(function.modelBatch, "run"):
                            with mock.patch.object(function, "processModelData"):
                                with mock.patch.object(function, "communicateModelBatchRun"):
                                    function.runBatch()
