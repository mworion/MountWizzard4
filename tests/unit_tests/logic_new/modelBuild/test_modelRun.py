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

import builtins
import json
import mw4.logic.modelBuild.modelRun
import pytest
from mw4.logic.modelBuild.modelRun import ModelData
from pathlib import Path
from skyfield.api import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function():
    function = ModelData(App())
    yield function


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function):
    def test(a):
        function.pauseBatch = False

    monkeypatch.setattr("mw4.logic.modelBuild.modelRun.sleepAndEvents", test)


@pytest.fixture
def mocked_sleepAndEvents_2(monkeypatch, function):
    def test(a):
        function.cancelBatch = True

    monkeypatch.setattr("mw4.logic.modelBuild.modelRun.sleepAndEvents", test)


def test_setImageExposed(function):
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


def test_startExposureAfterSlew_1(function):
    function.mountSlewed = True
    function.domeSlewed = True
    with mock.patch.object(function, "startNewImageExposure"):
        function.setMountSlewed()


def test_setMountSlewed_1(function):
    function.mountSlewed = False
    function.domeSlewed = False
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function, "startExposureAfterSlew"):
        function.setMountSlewed()
        assert function.mountSlewed
        assert not function.domeSlewed


def test_setMountSlewed_2(function):
    function.domeSlewed = False
    function.mountSlewed = False
    function.app.deviceStat["dome"] = False
    with mock.patch.object(function, "startExposureAfterSlew"):
        function.setMountSlewed()
        assert function.mountSlewed
        assert function.domeSlewed


def test_setDomeSlewed_1(function):
    function.domeSlewed = False
    with mock.patch.object(function, "startExposureAfterSlew"):
        function.setDomeSlewed()
        assert function.domeSlewed


def test_startNewSlew_1(function):
    function.domeSlewed = True
    function.mountSlewed = True
    function.cancelBatch = False
    function.endBatch = False
    function.modelRunKey = ""
    function.modelRunIterator = iter([])
    function.modelBuildData = {
        "im-00": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
        "im-01": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
        "im-02": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
    }
    function.startNewSlew()
    assert function.mountSlewed
    assert function.domeSlewed


def test_startNewSlew_3(function):
    function.domeSlewed = True
    function.mountSlewed = True
    function.cancelBatch = False
    function.endBatch = False
    function.modelRunIterator = iter(["im-00", "im-01", "im-02"])
    function.modelBuildData = {
        "im-00": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
        "im-01": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
        "im-02": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
    }

    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=False):
        function.startNewSlew()
        assert not function.mountSlewed
        assert not function.domeSlewed


def test_startNewSlew_4(function):
    function.domeSlewed = True
    function.mountSlewed = True
    function.cancelBatch = False
    function.endBatch = False
    function.app.deviceStat["dome"] = True
    function.modelRunIterator = iter(["im-00", "im-01", "im-02"])
    function.modelBuildData = {
        "im-00": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
        "im-01": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
        "im-02": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "success": True,
            "imagePath": Path("test"),
        },
    }

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
        mw4.logic.modelBuild.modelRun, "writeRetrofitData", return_value=[1, 2, 3]
    ):
        with mock.patch.object(
            mw4.logic.modelBuild.modelRun, "convertAngleToFloat", return_value=[1, 2, 3]
        ):
            function.addMountModelToBuildModel()
    assert len(function.modelSaveData) == 3


def test_addMountModelToBuildModel_2(function):
    function.app.mount.model.starList = [1, 2]
    function.modelSaveData = [1, 2, 3]
    with mock.patch.object(
        mw4.logic.modelBuild.modelRun, "writeRetrofitData", return_value=[1, 2, 3]
    ):
        with mock.patch.object(
            mw4.logic.modelBuild.modelRun, "convertAngleToFloat", return_value=[1, 2, 3]
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
    function.modelBuildData = {
        "im-00": {
            "altitude": Angle(degrees=0),
            "azimuth": Angle(degrees=0),
            "julianDate": jd,
            "success": True,
        },
        "im-01": {
            "altitude": Angle(degrees=1),
            "azimuth": Angle(degrees=1),
            "julianDate": jd,
            "success": False,
        },
        "im-02": {
            "dec": Angle(degrees=0),
            "ra": Angle(hours=0),
            "julianDate": jd,
            "success": True,
        },
    }
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


def test_saveModelData_1(function):
    function.modelSaveData = [1, 2, 3]
    with mock.patch.object(builtins, "open"):
        with mock.patch.object(json, "dump"):
            function.saveModelData(Path(""))


def test_buildProgModel_1(function):
    function.modelBuildData = []
    function.buildProgModel()


def test_buildProgModel_2(function):
    model = {
        "im-01": {
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
            "success": True,
        },
    }

    function.modelData = ModelData(App())
    function.modelBuildData = model
    function.buildProgModel()
    assert function.modelProgData[0].sCoord.dec.degrees == 64.3246


def test_buildProgModel_3(function):
    model = {
        "im-01": {
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
            "success": False,
        },
    }

    function.modelData = ModelData(App())
    function.modelBuildData = model
    function.buildProgModel()


def test_addMountDataToModelBuildData_1(function):
    function.modelRunKey = "im-00"
    function.modelBuildData = {"im-00": {"altitude": 0, "azimuth": 0}}
    function.addMountDataToModelBuildData()
    assert "raJ2000M" in function.modelBuildData["im-00"]
    assert "decJ2000M" in function.modelBuildData["im-00"]
    assert "raJNowM" in function.modelBuildData["im-00"]
    assert "decJNowM" in function.modelBuildData["im-00"]


def test_startNewImageExposure_1(function, mocked_sleepAndEvents):
    function.cancelBatch = True
    function.startNewImageExposure()


def test_startNewImageExposure_2(function, mocked_sleepAndEvents):
    function.pauseBatch = True
    function.cancelBatch = False
    function.exposureWaitTime = 1
    function.modelBuildData = {"im-00": {"imagePath": Path("test")}}
    with mock.patch.object(function, "addMountDataToModelBuildData"):
        with mock.patch.object(function.app.camera, "expose"):
            function.startNewImageExposure()


def test_startNewPlateSolve_1(function):
    function.modelBuildData = [{"imagePath": "test"}]
    with mock.patch.object(function.app.plateSolve, "solve"):
        function.startNewPlateSolve(Path("image-000.fits"))


def test_sendModelProgress_1(function):
    function.modelBuildData = {
        "im-00": {"imagePath": Path("test"), "success": True, "processed": True}
    }
    function.sendModelProgress()


def test_collectPlateSolveResult_1(function):
    jd = function.app.mount.obsSite.timeJD
    function.modelBuildData = {
        "im-00": {
            "julianDate": jd,
            "raJ2000S": Angle(hours=0),
            "decJ2000S": Angle(degrees=0),
            "imagePath": Path("test"),
            "angleS": Angle(degrees=0),
            "errorRMS_S": 1,
            "countSequence": 0,
            "processed": False,
        },
    }
    result = {
        "success": True,
        "raJNow": 0,
        "decJNow": 0,
        "imagePath": Path("im-00.fits"),
        "message": "Ok",
    }
    with mock.patch.object(function.app.data, "setStatusBuildP"):
        with mock.patch.object(function, "sendModelProgress"):
            function.collectPlateSolveResult(result)


def test_collectPlateSolveResult_2(function):
    jd = function.app.mount.obsSite.timeJD
    function.modelBuildData = {
        "im-00": {
            "julianDate": jd,
            "raJ2000S": Angle(hours=0),
            "decJ2000S": Angle(degrees=0),
            "imagePath": Path("test"),
            "angleS": Angle(degrees=0),
            "errorRMS_S": 1,
            "countSequence": 0,
            "processed": False,
        },
    }
    result = {
        "success": False,
        "raJNow": 0,
        "decJNow": 0,
        "imagePath": Path("im-00.fits"),
        "message": "Ok",
    }
    with mock.patch.object(function.app.data, "setStatusBuildP"):
        with mock.patch.object(function, "sendModelProgress"):
            function.collectPlateSolveResult(result)


def test_collectPlateSolveResult_3(function):
    jd = function.app.mount.obsSite.timeJD
    function.modelBuildData = {
        "im-00": {
            "julianDate": jd,
            "raJ2000S": Angle(hours=0),
            "decJ2000S": Angle(degrees=0),
            "imagePath": Path("test"),
            "angleS": Angle(degrees=0),
            "errorRMS_S": 1,
            "countSequence": 0,
            "processed": True,
        },
    }
    result = {
        "success": False,
        "raJNow": 0,
        "decJNow": 0,
        "imagePath": Path("im-00.fits"),
        "message": "Ok",
    }
    with mock.patch.object(function.app.data, "setStatusBuildP"):
        with mock.patch.object(function, "sendModelProgress"):
            function.collectPlateSolveResult(result)


def test_collectPlateSolveResult_4(function):
    jd = function.app.mount.obsSite.timeJD
    function.modelBuildData = {
        "im-00": {
            "julianDate": jd,
            "raJ2000S": Angle(hours=0),
            "decJ2000S": Angle(degrees=0),
            "imagePath": Path("test"),
            "angleS": Angle(degrees=0),
            "errorRMS_S": 1,
            "countSequence": 0,
            "processed": True,
        },
    }
    result = {
        "success": False,
        "raJNow": 0,
        "decJNow": 0,
        "imagePath": Path("im-00.fits"),
        "message": "Skipped",
    }
    with mock.patch.object(function.app.data, "setStatusBuildP"):
        with mock.patch.object(function, "sendModelProgress"):
            function.collectPlateSolveResult(result)


def test_prepareModelBuildData_1(function):
    function.modelInputData = [(5, 0, True), (20, 1, True)]
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 90

    with mock.patch.object(function, "sendModelProgress"):
        with mock.patch.object(function.app.data, "setStatusBuildPUnprocessed"):
            function.prepareModelBuildData()
            assert len(function.modelBuildData) == 2
            assert function.modelBuildData["image-000"]["altitude"].degrees == 5
            assert function.modelBuildData["image-000"]["azimuth"].degrees == 0


def test_checkRetryNeeded_1(function):
    function.modelBuildData = {
        "image-000": {"success": True, "imagePath": Path("test"), "message": ""},
        "image-001": {"success": True, "imagePath": Path("test"), "message": ""},
        "image0-02": {"success": True, "imagePath": Path("test"), "message": ""},
    }
    assert not function.checkRetryNeeded()


def test_checkRetryNeeded_2(function):
    function.modelBuildData = {
        "image-000": {
            "success": True,
            "imagePath": Path("test"),
            "message": "Slew not possible",
        },
        "image-001": {
            "success": False,
            "imagePath": Path("test"),
            "message": "Slew not possible",
        },
        "image0-02": {"success": False, "imagePath": Path("test"), "message": ""},
    }
    assert function.checkRetryNeeded()


def test_checkModelFinished_1(function):
    function.modelBuildData = {
        "image-000": {"processed": True},
        "image-001": {"processed": True},
        "image0-02": {"processed": True},
    }
    assert function.checkModelFinished()


def test_checkModelFinished_2(function):
    function.modelBuildData = {
        "image-000": {"processed": True},
        "image-001": {"processed": False},
        "image0-02": {"processed": True},
    }
    assert not function.checkModelFinished()


def test_runThroughModelBuildData_1(function, mocked_sleepAndEvents_2):
    function.cancelBatch = False
    function.endBatch = False
    with mock.patch.object(function, "startNewSlew"):
        with mock.patch.object(function, "checkModelFinished", return_value=False):
            function.runThroughModelBuildData()


def test_generateRunIterator_1(function):
    function.retriesReverse = False
    function.retries = 1
    function.modelRunList = ["image-000", "image-001", "image-002", "image-003"]
    function.modelBuildData = {
        "image-000": {"success": False, "imagePath": Path("test"), "message": ""},
        "image-001": {"success": False, "imagePath": Path("test"), "message": ""},
        "image-002": {"success": True, "imagePath": Path("test"), "message": ""},
        "image-003": {
            "success": False,
            "imagePath": Path("test"),
            "message": "Slew not possible",
        },
    }
    function.generateRunIterator()
    assert list(function.modelRunIterator) == ["image-000", "image-001"]


def test_generateRunIterator_2(function):
    function.retriesReverse = True
    function.retries = 1
    function.modelRunList = ["image-000", "image-001", "image-002", "image-003"]
    function.modelBuildData = {
        "image-000": {"success": False, "imagePath": Path("test"), "message": ""},
        "image-001": {"success": False, "imagePath": Path("test"), "message": ""},
        "image-002": {"success": True, "imagePath": Path("test"), "message": ""},
        "image-003": {
            "success": False,
            "imagePath": Path("test"),
            "message": "Slew not possible",
        },
    }
    function.generateRunIterator()
    assert list(function.modelRunIterator) == ["image-001", "image-000"]


def test_runThroughModelBuildDataRetries_1(function):
    function.cancelBatch = False
    function.endBatch = False
    function.retries = 1
    function.numberRetries = 2
    with mock.patch.object(function, "generateRunIterator"):
        with mock.patch.object(function, "runThroughModelBuildData"):
            with mock.patch.object(function, "checkRetryNeeded", return_value=False):
                function.runThroughModelBuildDataRetries()


def test_runThroughModelBuildDataRetries_2(function):
    function.cancelBatch = True
    function.endBatch = True
    function.retries = 1
    function.numberRetries = 2
    with mock.patch.object(function, "generateRunIterator"):
        with mock.patch.object(function, "runThroughModelBuildData"):
            with mock.patch.object(function, "checkRetryNeeded", return_value=True):
                function.runThroughModelBuildDataRetries()


def test_runThroughModelBuildDataRetries_3(function):
    function.cancelBatch = False
    function.endBatch = False
    function.retries = 1
    function.numberRetries = 2
    with mock.patch.object(function, "generateRunIterator"):
        with mock.patch.object(function, "runThroughModelBuildData"):
            with mock.patch.object(function, "checkRetryNeeded", return_value=True):
                function.runThroughModelBuildDataRetries()


def test_runModel_1(function):
    function.modelInputData = []
    function.runModel()


def test_runModel_2(function):
    function.modelInputData = [(0, 0, True)]
    function.cancelBatch = False
    with mock.patch.object(function, "prepareModelBuildData"):
        with mock.patch.object(function, "runThroughModelBuildData"):
            with mock.patch.object(function, "buildProgModel"):
                function.runModel()


def test_runModel_3(function):
    function.modelInputData = [(0, 0, True)]
    function.cancelBatch = True
    with mock.patch.object(function, "prepareModelBuildData"):
        with mock.patch.object(function, "runThroughModelBuildData"):
            function.runModel()
