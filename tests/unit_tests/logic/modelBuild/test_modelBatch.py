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
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import logic.modelBuild.modelBatch
from logic.modelBuild.modelBatch import ModelBatch


@pytest.fixture(autouse=True, scope="module")
def function():
    function = ModelBatch(App())
    yield function


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        function.pauseBatch = False

    monkeypatch.setattr("logic.modelBuild.modelBatch.sleepAndEvents", test)


@pytest.fixture
def mocked_sleepAndEvents_2(monkeypatch, function):
    def test(a):
        function.cancelBatch = True

    monkeypatch.setattr("logic.modelBuild.modelBatch.sleepAndEvents", test)


def test_setImageExposed(function):
    function.modelBuildData = [{"imagePath": "test"}]
    function.pointerImage = 0
    function.modelTiming = 2
    with mock.patch.object(function, "startNewSlew"):
        function.setImageExposed()


def test_setImageDownloaded(function):
    function.modelTiming = 1
    with mock.patch.object(function, "startNewSlew"):
        function.setImageDownloaded()


def test_setImageSaved(function):
    function.modelTiming = 0
    with mock.patch.object(function, "startNewSlew"):
        function.setImageSaved()


def test_setMountSlewed_1(function):
    function.mountSlewed = False
    function.app.deviceStat["dome"] = False
    with mock.patch.object(function, "startNewImageExposure"):
        function.setMountSlewed()
        assert function.mountSlewed


def test_setMountSlewed_2(function):
    function.mountSlewed = False
    function.domeSlewed = True
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function, "startNewImageExposure"):
        function.setMountSlewed()
        assert function.mountSlewed


def test_setDomeSlewed_1(function):
    function.domeSlewed = False
    function.mountSlewed = True
    with mock.patch.object(function, "startNewImageExposure"):
        function.setDomeSlewed()
        assert function.domeSlewed


def test_startNewSlew_1(function):
    function.domeSlewed = True
    function.mountSlewed = True
    function.cancelBatch = False
    function.endBatch = False
    function.pointerSlew = 0
    function.modelBuildData = [{"altitude": 0, "azimuth": 0}]

    function.startNewSlew()
    assert function.mountSlewed
    assert function.domeSlewed


def test_startNewSlew_2(function):
    function.domeSlewed = True
    function.mountSlewed = True
    function.cancelBatch = True
    function.endBatch = True
    function.pointerSlew = -1
    function.modelBuildData = [{"altitude": 0, "azimuth": 0}]

    function.startNewSlew()
    assert function.mountSlewed
    assert function.domeSlewed


def test_startNewSlew_3(function):
    function.domeSlewed = True
    function.mountSlewed = True
    function.cancelBatch = False
    function.endBatch = False
    function.pointerSlew = -1
    function.modelBuildData = [{"altitude": 0, "azimuth": 0}]

    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=False):
        function.startNewSlew()
        assert not function.mountSlewed
        assert not function.domeSlewed


def test_startNewSlew_4(function):
    function.domeSlewed = True
    function.mountSlewed = True
    function.cancelBatch = False
    function.endBatch = False
    function.pointerSlew = -1
    function.app.deviceStat["dome"] = True
    function.modelBuildData = [{"altitude": 0, "azimuth": 0}]

    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=True):
        with mock.patch.object(function.app.dome, "slewDome"):
            with mock.patch.object(function.app.mount.obsSite, "startSlewing"):
                function.startNewSlew()
                assert not function.mountSlewed
                assert not function.domeSlewed


def test_addMountModelToBuildModel_1(function):
    function.app.mount.model.starList = [1, 2, 3]
    function.modelSaveData = [1, 2, 3]
    with mock.patch.object(
        logic.modelBuild.modelBatch, "writeRetrofitData", return_value=[1, 2, 3]
    ):
        with mock.patch.object(
            logic.modelBuild.modelBatch, "convertAngleToFloat", return_value=[1, 2, 3]
        ):
            function.addMountModelToBuildModel()
    assert len(function.modelSaveData) == 3


def test_addMountModelToBuildModel_2(function):
    function.app.mount.model.starList = [1, 2]
    function.modelSaveData = [1, 2, 3]
    with mock.patch.object(
        logic.modelBuild.modelBatch, "writeRetrofitData", return_value=[1, 2, 3]
    ):
        with mock.patch.object(
            logic.modelBuild.modelBatch, "convertAngleToFloat", return_value=[1, 2, 3]
        ):
            function.addMountModelToBuildModel()

    assert len(function.modelSaveData) == 0


def test_collectBuildModelResults_1(function):
    function.modelSaveData = [1, 2, 3]
    function.modelBuildData = []

    function.collectBuildModelResults()
    assert function.modelSaveData == []


def test_collectBuildModelResults_2(function):
    jd = function.app.mount.obsSite.timeJD
    function.modelBuildData = [
        {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "julianDate": jd,
            "success": True,
        },
        {
            "altitude": Angle(degrees=1),
            "azimuth": Angle(degrees=1),
            "julianDate": jd,
            "success": False,
        },
        {
            "dec": Angle(degrees=0),
            "ra": Angle(hours=0),
            "julianDate": jd,
            "success": True,
        },
    ]
    function.modelSaveData = [1, 2, 3]

    function.collectBuildModelResults()
    assert len(function.modelSaveData) == 2
    assert "version" in function.modelSaveData[0]
    assert "profile" in function.modelSaveData[0]
    assert "firmware" in function.modelSaveData[0]
    assert "latitude" in function.modelSaveData[0]


def test_generateSaveData_1(function):
    with mock.patch.object(function, "collectBuildModelResults"):
        with mock.patch.object(function, "addMountModelToBuildModel"):
            function.generateSaveData()


def test_addMountDataToModelBuildData_1(function):
    function.pointerImage = 0
    function.modelBuildData = [{"altitude": 0, "azimuth": 0}]
    function.addMountDataToModelBuildData()
    assert "raJ2000M" in function.modelBuildData[0]
    assert "decJ2000M" in function.modelBuildData[0]
    assert "raJNowM" in function.modelBuildData[0]
    assert "decJNowM" in function.modelBuildData[0]


def test_startNewImageExposure_1(function, mocked_sleepAndEvents):
    function.cancelBatch = True
    function.startNewImageExposure()


def test_startNewImageExposure_2(function, mocked_sleepAndEvents):
    function.pauseBatch = True
    function.cancelBatch = False
    function.exposureWaitTime = 1
    function.pointerImage = -1
    function.modelBuildData = [{"imagePath": "test"}]
    with mock.patch.object(function, "addMountDataToModelBuildData"):
        with mock.patch.object(function.app.camera, "expose"):
            function.startNewImageExposure()


def test_startNewPlateSolve_1(function):
    function.pointerPlateSolve = -1
    function.modelBuildData = [{"imagePath": "test"}]
    with mock.patch.object(function.app.plateSolve, "solve"):
        function.startNewPlateSolve()


def test_sendModelProgress_1(function):
    function.modelBuildData = [{"success": True}]
    function.pointerResult = 0
    function.sendModelProgress()


def test_collectPlateSolveResult_1(function):
    jd = function.app.mount.obsSite.timeJD
    function.modelBuildData = [
        {"julianDate": jd, "raJ2000S": Angle(hours=0), "decJ2000S": Angle(degrees=0)}
    ]
    function.pointerResult = -1
    result = {"success": True, "raJNow": 0, "decJNow": 0}
    with mock.patch.object(function.app.data, "setStatusBuildP"):
        with mock.patch.object(function, "sendModelProgress"):
            function.collectPlateSolveResult(result)
            assert function.pointerResult == 0


def test_prepareModelBuildData_1(function):
    function.modelInputData = [(0, 0, True), (1, 1, True)]
    function.pointerResult = -1
    with mock.patch.object(function, "sendModelProgress"):
        function.prepareModelBuildData()
        assert len(function.modelBuildData) == 2
        assert function.modelBuildData[0]["altitude"].degrees == 0
        assert function.modelBuildData[0]["azimuth"].degrees == 0


def test_processModelBuildData_1(function):
    function.processModelBuildData()


def test_run_1(function):
    function.modelInputData = []
    function.run()


def test_run_2(function, mocked_sleepAndEvents_2):
    function.modelInputData = [(0, 0, True)]
    with mock.patch.object(function, "prepareModelBuildData"):
        with mock.patch.object(function, "startNewSlew"):
            with mock.patch.object(function, "generateSaveData"):
                function.run()
