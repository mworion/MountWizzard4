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
import json

# external packages
import skyfield.api
from skyfield.api import Angle
from mountcontrol.modelStar import ModelStar
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabModel import Model
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
    suc = function.updateModelProgress(mPoint)
    assert not suc


def test_updateModelProgress_2(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 3, "countSequence": 2}
    suc = function.updateModelProgress(mPoint)
    assert suc


def test_updateModelProgress_3(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 2, "countSequence": 3}
    suc = function.updateModelProgress(mPoint)
    assert not suc


def test_updateModelProgress_4(function):
    mPoint = {"lenSequence": 0, "countSequence": 2}
    suc = function.updateModelProgress(mPoint)
    function.timeStartModeling = time.time()
    assert not suc


def test_updateModelProgress_5(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 3, "countSequence": 1}
    suc = function.updateModelProgress(mPoint)
    assert suc


def test_updateModelProgress_6(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 3, "countSequence": -1}
    suc = function.updateModelProgress(mPoint)
    assert not suc


def test_updateModelProgress_7(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 3, "countSequence": 2}
    suc = function.updateModelProgress(mPoint)
    assert suc


def test_updateModelProgress_8(function):
    function.timeStartModeling = time.time()
    mPoint = {"lenSequence": 0, "countSequence": -1}
    suc = function.updateModelProgress(mPoint)
    assert not suc


def test_setupModelRunContextAndGuiStatus_1(function):
    function.app.uiWindows = {"showImageW": {"classObj": None}}
    suc = function.setupModelRunContextAndGuiStatus()
    assert suc


def test_pauseBuild_1(function):
    function.ui.pauseModel.setProperty("pause", True)
    suc = function.pauseBuild()
    assert suc
    assert not function.ui.pauseModel.property("pause")


def test_pauseBuild_2(function):
    function.ui.pauseModel.setProperty("pause", False)
    suc = function.pauseBuild()
    assert suc
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
        suc = function.retrofitModel()
        assert suc


def test_saveModelFinish_1(function):
    def test():
        return

    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")
    function.modelName = "test"
    function.generateSaveData = test
    function.app.mount.signals.alignDone.connect(function.saveModelFinish)
    suc = function.saveModelFinish()
    assert suc


def test_generateBuildData_1(function):
    build = function.generateBuildData()
    assert build == []


def test_generateBuildData_2(function):
    function.model = [
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

    build = function.generateBuildData()
    assert build[0].sCoord.dec.degrees == 64.3246


def test_programModelToMount_1(function):
    function.model = []
    with mock.patch.object(function, "generateBuildData", return_value=[]):
        with mock.patch.object(
            function.app.mount.model, "programAlign", return_value=False
        ):
            suc = function.programModelToMount()
            assert not suc


def test_programModelToMount_2(function):
    function.model = []
    with mock.patch.object(function, "generateBuildData", return_value=[1, 2, 3]):
        with mock.patch.object(
            function.app.mount.model, "programAlign", return_value=False
        ):
            suc = function.programModelToMount()
            assert not suc


def test_programModelToMount_3(function):
    with mock.patch.object(function, "generateBuildData", return_value=[1, 2, 3]):
        with mock.patch.object(
            function.app.mount.model, "programAlign", return_value=True
        ):
            suc = function.programModelToMount()
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
    with mock.patch.object(function.app.mount.model, "clearAlign", return_value=False):
        suc = function.clearAlignAndBackup()
        assert not suc


def test_clearAlignAndBackup_2(function):
    with mock.patch.object(function.app.mount.model, "clearAlign", return_value=True):
        with mock.patch.object(
            function.app.mount.model, "deleteName", return_value=False
        ):
            with mock.patch.object(gui.mainWaddon.tabModel, "sleepAndEvents"):
                suc = function.clearAlignAndBackup()
                assert suc


def test_clearAlignAndBackup_3(function):
    with mock.patch.object(function.app.mount.model, "clearAlign", return_value=True):
        with mock.patch.object(
            function.app.mount.model, "deleteName", return_value=True
        ):
            with mock.patch.object(
                function.app.mount.model, "storeName", return_value=False
            ):
                with mock.patch.object(gui.mainWaddon.tabModel, "sleepAndEvents"):
                    suc = function.clearAlignAndBackup()
                    assert suc


def test_clearAlignAndBackup_4(function):
    with mock.patch.object(function.app.mount.model, "clearAlign", return_value=True):
        with mock.patch.object(
            function.app.mount.model, "deleteName", return_value=True
        ):
            with mock.patch.object(
                function.app.mount.model, "storeName", return_value=True
            ):
                with mock.patch.object(gui.mainWaddon.tabModel, "sleepAndEvents"):
                    suc = function.clearAlignAndBackup()
                    assert suc


def test_loadProgramModel_1(function):
    def openFile(a, b, c, d, multiple=False):
        return ([], [], [])

    function.openFile = openFile

    suc = function.loadProgramModel()
    assert not suc


def test_loadProgramModel_2(function):
    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")

    def openFile(a, b, c, d, multiple=False):
        return ("tests/workDir/model/test.model", "test", ".model")

    function.openFile = openFile

    with mock.patch.object(function, "clearAlignAndBackup", return_value=False):
        suc = function.loadProgramModel()
        assert not suc


def test_loadProgramModel_3(function):
    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")

    def openFile(a, b, c, d, multiple=False):
        return (["tests/workDir/model/test.model"], ["test"], [".model"])

    function.openFile = openFile

    with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
        with mock.patch.object(function, "programModelToMount", return_value=False):
            suc = function.loadProgramModel()
            assert not suc


def test_loadProgramModel_4(function):
    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")

    def openFile(a, b, c, d, multiple=False):
        return (["tests/workDir/model/test.model"], ["test"], [".model"])

    function.openFile = openFile

    with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
        with mock.patch.object(function, "programModelToMount", return_value=True):
            suc = function.loadProgramModel()
            assert suc


def test_loadProgramModel_5(function):
    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")

    def openFile(a, b, c, d, multiple=False):
        return (["tests/workDir/model/test.model"], ["test"], [".model"])

    function.openFile = openFile

    with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
        with mock.patch.object(function, "programModelToMount", return_value=True):
            with mock.patch.object(
                json, "load", return_value={}, side_effect=Exception
            ):
                suc = function.loadProgramModel()
                assert suc


def test_loadProgramModel_6(function):
    shutil.copy("tests/testData/test.model", "tests/workDir/model/test.model")
    shutil.copy("tests/testData/test1.model", "tests/workDir/model/test1.model")

    def openFile(a, b, c, d, multiple=False):
        return (
            ["tests/workDir/model/test.model", "tests/workDir/model/test1.model"],
            ["test", "test1"],
            [".model", ".model"],
        )

    function.openFile = openFile

    with mock.patch.object(function, "clearAlignAndBackup", return_value=True):
        suc = function.loadProgramModel()
        assert not suc
