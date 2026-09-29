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
def function(qapp):
    try:
        function = ModelData(App())
    except (
        RuntimeError,
        ImportError,
        AttributeError,
        ConnectionError,
        OSError,
        ValueError,
    ) as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield function


@pytest.fixture(autouse=True)
def resetState(function):
    function.cancelBatch = False
    function.pauseBatch = False
    function.endBatch = False
    function.passActive = False
    function.modelBuildData = {}
    function.modelRunList = []
    function.modelRunKey = ""
    function.retries = 0
    function.numberRetries = 0
    function.waitTimeExposure = 0
    yield
    function.timerExposure.stop()
    function.passActive = False


def buildRunData(keys: list[str]) -> dict:
    return {
        key: {
            "imagePath": Path(f"{key}.fits"),
            "countSequence": i,
            "success": False,
            "processed": False,
            "message": "",
        }
        for i, key in enumerate(keys)
    }


def solveResult(key: str, success: bool = True, message: str = "Ok") -> dict:
    return {"success": success, "imagePath": Path(f"{key}.fits"), "message": message}


def test_setupAndResetSignals(function):
    function.modelTiming = function.PROGRESSIVE
    exposed = function.app.dReg["camera"].signals.exposed
    with mock.patch.object(function, "startSlew") as mockSlew:
        function.setupSignals()
        try:
            exposed.emit(Path("test.fits"))
            assert mockSlew.emit.call_count == 1
        finally:
            function.resetSignals()
        exposed.emit(Path("test.fits"))
        assert mockSlew.emit.call_count == 1
    function.modelTiming = function.CONSERVATIVE


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
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(function, "startExposureAfterSlew"):
        function.setMountSlewed()
        assert function.mountSlewed
        assert not function.domeSlewed


def test_setMountSlewed_2(function):
    function.domeSlewed = False
    function.mountSlewed = False
    function.app.dReg.d["dome"].stat = False
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
    function.modelRunKey = "im-02"
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
    assert function.modelRunKey == ""


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

    with mock.patch.object(
        function.app.dReg.d["mount"].instance.obsSite,
        "setTargetAltAz",
        return_value=False,
    ):
        function.startNewSlew()
        assert not function.mountSlewed
        assert not function.domeSlewed


def test_startNewSlew_4(function):
    function.domeSlewed = True
    function.mountSlewed = True
    function.cancelBatch = False
    function.endBatch = False
    function.app.dReg.d["dome"].stat = True
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

    with (
        mock.patch.object(
            function.app.dReg.d["mount"].instance.obsSite,
            "setTargetAltAz",
            return_value=True,
        ),
        mock.patch.object(function.app.dReg.d["dome"].instance, "slewDome"),
        mock.patch.object(function.app.dReg.d["mount"].instance.obsSite, "startSlewing"),
    ):
        function.startNewSlew()
        assert not function.mountSlewed
        assert not function.domeSlewed


def test_addMountModelToBuildModel_1(function):
    function.app.dReg.d["mount"].instance.model.starList = [1, 2, 3]
    function.modelSaveData = [1, 2, 3]
    with (
        mock.patch.object(
            mw4.logic.modelBuild.modelRun, "writeRetrofitData", return_value=[1, 2, 3]
        ),
        mock.patch.object(
            mw4.logic.modelBuild.modelRun, "convertAngleToFloat", return_value=[1, 2, 3]
        ),
    ):
        function.addMountModelToBuildModel()
    assert len(function.modelSaveData) == 3


def test_addMountModelToBuildModel_2(function):
    function.app.dReg.d["mount"].instance.model.starList = [1, 2]
    function.modelSaveData = [1, 2, 3]
    with (
        mock.patch.object(
            mw4.logic.modelBuild.modelRun, "writeRetrofitData", return_value=[1, 2, 3]
        ),
        mock.patch.object(
            mw4.logic.modelBuild.modelRun, "convertAngleToFloat", return_value=[1, 2, 3]
        ),
    ):
        function.addMountModelToBuildModel()

    assert len(function.modelSaveData) == 0


def test_collectBuildModelResults_1(function):
    function.modelSaveData = [1, 2, 3]
    function.modelBuildData = []

    function.collectBuildModelResults()
    assert function.modelSaveData == []


def test_collectBuildModelResults_2(function):
    jd = function.app.dReg.d["mount"].instance.obsSite.timeJD
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
    with (
        mock.patch.object(function, "collectBuildModelResults"),
        mock.patch.object(function, "addMountModelToBuildModel"),
    ):
        function.generateSaveData()


def test_saveModelData_1(function):
    function.modelSaveData = [1, 2, 3]
    with mock.patch.object(builtins, "open"), mock.patch.object(json, "dump"):
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


def test_startNewImageExposure_1(function):
    function.cancelBatch = True
    function.startNewImageExposure()
    assert not function.timerExposure.isActive()


def test_startNewImageExposure_2(function):
    function.waitTimeExposure = 2
    function.startNewImageExposure()
    assert function.timerExposure.isActive()
    assert function.timerExposure.interval() == 2000


def test_checkPauseAndExpose_1(function):
    function.endBatch = True
    with mock.patch.object(function, "exposeImage") as mockExpose:
        function.checkPauseAndExpose()
    mockExpose.assert_not_called()
    assert not function.timerExposure.isActive()


def test_checkPauseAndExpose_2(function):
    function.pauseBatch = True
    with mock.patch.object(function, "exposeImage") as mockExpose:
        function.checkPauseAndExpose()
    mockExpose.assert_not_called()
    assert function.timerExposure.isActive()
    assert function.timerExposure.interval() == function.PAUSE_POLL_MS


def test_checkPauseAndExpose_3(function):
    with mock.patch.object(function, "exposeImage") as mockExpose:
        function.checkPauseAndExpose()
    mockExpose.assert_called_once()


def test_startNewImageExposure_timerExposes(function, qtbot):
    with mock.patch.object(function, "exposeImage") as mockExpose:
        function.startNewImageExposure()
        qtbot.waitUntil(lambda: mockExpose.called, timeout=1000)


def test_exposeImage_1(function):
    function.modelBuildData = {"im-00": {"imagePath": Path("test")}}
    function.modelRunKey = "im-00"
    with (
        mock.patch.object(function, "addMountDataToModelBuildData"),
        mock.patch.object(function.app.dReg.d["camera"].instance, "expose") as mockExpose,
    ):
        function.exposeImage()
    mockExpose.assert_called_once()


def test_startNewPlateSolve_1(function):
    function.modelBuildData = [{"imagePath": "test"}]
    with mock.patch.object(function.app.dReg["plateSolve"].instance, "solve"):
        function.startNewPlateSolve(Path("image-000.fits"))


def test_sendModelProgress_1(function):
    function.modelBuildData = {
        "im-00": {"imagePath": Path("test"), "success": True, "processed": True}
    }
    function.sendModelProgress()


def test_collectPlateSolveResult_1(function):
    jd = function.app.dReg.d["mount"].instance.obsSite.timeJD
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
    with (
        mock.patch.object(function.app.data, "setStatusBuildP"),
        mock.patch.object(function, "sendModelProgress"),
    ):
        function.collectPlateSolveResult(result)


def test_collectPlateSolveResult_2(function):
    jd = function.app.dReg.d["mount"].instance.obsSite.timeJD
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
    with (
        mock.patch.object(function.app.data, "setStatusBuildP"),
        mock.patch.object(function, "sendModelProgress"),
    ):
        function.collectPlateSolveResult(result)


def test_collectPlateSolveResult_3(function):
    jd = function.app.dReg.d["mount"].instance.obsSite.timeJD
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
    with (
        mock.patch.object(function.app.data, "setStatusBuildP"),
        mock.patch.object(function, "sendModelProgress"),
    ):
        function.collectPlateSolveResult(result)


def test_collectPlateSolveResult_4(function):
    jd = function.app.dReg.d["mount"].instance.obsSite.timeJD
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
    with (
        mock.patch.object(function.app.data, "setStatusBuildP"),
        mock.patch.object(function, "sendModelProgress"),
    ):
        function.collectPlateSolveResult(result)


def test_prepareModelBuildData_1(function):
    function.modelInputData = [(5, 0, True), (20, 1, True)]
    function.app.dReg.d["mount"].instance.setting.horizonLimitLow = 10
    function.app.dReg.d["mount"].instance.setting.horizonLimitHigh = 90

    with (
        mock.patch.object(function, "sendModelProgress"),
        mock.patch.object(function.app.data, "setStatusBuildPUnprocessed"),
    ):
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
    function.modelRunList = list(function.modelBuildData)
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
    function.modelRunList = list(function.modelBuildData)
    assert function.checkRetryNeeded()


def test_checkModelFinished_1(function):
    function.modelBuildData = {
        "image-000": {"processed": True},
        "image-001": {"processed": True},
        "image0-02": {"processed": True},
    }
    function.modelRunList = list(function.modelBuildData)
    assert function.checkModelFinished()


def test_checkModelFinished_2(function):
    function.modelBuildData = {
        "image-000": {"processed": True},
        "image-001": {"processed": False},
        "image0-02": {"processed": True},
    }
    function.modelRunList = list(function.modelBuildData)
    assert not function.checkModelFinished()


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


def test_collectPlateSolveResult_finishesPass(function, qtbot):
    function.modelBuildData = buildRunData(["im-00"])
    function.modelRunList = ["im-00"]
    function.passActive = True
    with (
        mock.patch.object(function, "sendModelProgress"),
        mock.patch.object(function, "finishModel") as mockFinish,
    ):
        function.collectPlateSolveResult(solveResult("im-00"))
        mockFinish.assert_not_called()
        qtbot.waitUntil(lambda: mockFinish.called, timeout=1000)
    assert not function.passActive


def test_startPass_1(function):
    function.retries = 1
    function.cancelBatch = True
    retrySlot = mock.MagicMock()
    function.statusRetry.connect(retrySlot)
    try:
        with (
            mock.patch.object(function, "finishModel") as mockFinish,
            mock.patch.object(function, "generateRunIterator") as mockGen,
        ):
            function.startPass()
    finally:
        function.statusRetry.disconnect(retrySlot)
    retrySlot.assert_called_once_with(1)
    mockFinish.assert_called_once()
    mockGen.assert_not_called()


def test_startPass_2(function, qtbot):
    function.modelBuildData = buildRunData(["im-00"])
    function.modelRunList = []
    with (
        mock.patch.object(function, "startSlew") as mockSlew,
        mock.patch.object(function, "finishModel") as mockFinish,
    ):
        function.startPass()
        assert function.passActive
        qtbot.waitUntil(lambda: mockFinish.called, timeout=1000)
    mockSlew.emit.assert_not_called()


def test_startPass_3(function):
    function.modelBuildData = buildRunData(["im-00", "im-01"])
    function.modelBuildData["im-00"]["processed"] = True
    function.modelRunList = ["im-00", "im-01"]
    with mock.patch.object(function, "startSlew") as mockSlew:
        function.startPass()
    mockSlew.emit.assert_called_once()
    assert function.passActive
    assert not function.modelBuildData["im-00"]["processed"]


def test_finishPass_1(function):
    function.passActive = False
    with mock.patch.object(function, "finishModel") as mockFinish:
        function.finishPass()
    mockFinish.assert_not_called()


def test_finishPass_2(function):
    function.passActive = True
    function.numberRetries = 2
    with (
        mock.patch.object(function, "checkRetryNeeded", return_value=True),
        mock.patch.object(function, "startPass") as mockStart,
        mock.patch.object(function, "finishModel") as mockFinish,
    ):
        function.finishPass()
    assert function.retries == 1
    mockStart.assert_called_once()
    mockFinish.assert_not_called()


def test_finishPass_3(function):
    function.passActive = True
    function.numberRetries = 2
    function.retries = 2
    with (
        mock.patch.object(function, "checkRetryNeeded", return_value=True),
        mock.patch.object(function, "startPass") as mockStart,
        mock.patch.object(function, "finishModel") as mockFinish,
    ):
        function.finishPass()
    mockStart.assert_not_called()
    mockFinish.assert_called_once()


def test_finishPass_4(function):
    function.passActive = True
    function.numberRetries = 2
    function.endBatch = True
    with (
        mock.patch.object(function, "checkRetryNeeded", return_value=True),
        mock.patch.object(function, "startPass") as mockStart,
        mock.patch.object(function, "finishModel") as mockFinish,
    ):
        function.finishPass()
    mockStart.assert_not_called()
    mockFinish.assert_called_once()


def test_finishPass_5(function):
    function.passActive = True
    function.numberRetries = 2
    with (
        mock.patch.object(function, "checkRetryNeeded", return_value=False),
        mock.patch.object(function, "startPass") as mockStart,
        mock.patch.object(function, "finishModel") as mockFinish,
    ):
        function.finishPass()
    mockStart.assert_not_called()
    mockFinish.assert_called_once()


def test_finishModel_1(function, qtbot):
    function.cancelBatch = True
    function.timerExposure.start(10000)
    with (
        mock.patch.object(function, "resetSignals") as mockReset,
        mock.patch.object(function, "buildProgModel") as mockBuild,
        qtbot.waitSignal(function.finished) as blocker,
    ):
        function.finishModel()
    assert blocker.args == [True]
    assert not function.timerExposure.isActive()
    mockReset.assert_called_once()
    mockBuild.assert_not_called()


def test_finishModel_2(function, qtbot):
    def build():
        function.modelProgData = [1, 2]

    with (
        mock.patch.object(function, "resetSignals"),
        mock.patch.object(function, "buildProgModel", side_effect=build),
        qtbot.waitSignal(function.finished) as blocker,
    ):
        function.finishModel()
    assert blocker.args == [False]
    assert function.modelProgData == []


def test_finishModel_3(function, qtbot):
    def build():
        function.modelProgData = [1, 2, 3]

    with (
        mock.patch.object(function, "resetSignals"),
        mock.patch.object(function, "buildProgModel", side_effect=build),
        qtbot.waitSignal(function.finished) as blocker,
    ):
        function.finishModel()
    assert blocker.args == [False]
    assert function.modelProgData == [1, 2, 3]


def test_stopRun_1(function):
    function.timerExposure.start(10000)
    with mock.patch.object(function, "finishPass") as mockFinish:
        function.stopRun()
    assert not function.timerExposure.isActive()
    mockFinish.assert_not_called()


def test_stopRun_2(function, qtbot):
    function.passActive = True
    with mock.patch.object(function, "finishModel") as mockFinish:
        function.stopRun()
        mockFinish.assert_not_called()
        qtbot.waitUntil(lambda: mockFinish.called, timeout=1000)


def test_cancelRun(function):
    with mock.patch.object(function, "stopRun") as mockStop:
        function.cancelRun()
    assert function.cancelBatch
    mockStop.assert_called_once()


def test_endRun(function):
    with mock.patch.object(function, "stopRun") as mockStop:
        function.endRun()
    assert function.endBatch
    mockStop.assert_called_once()


def test_resetBatchFlags(function):
    function.cancelBatch = function.endBatch = function.pauseBatch = True
    function.passActive = True
    function.resetBatchFlags()
    assert not any(
        [function.cancelBatch, function.endBatch, function.pauseBatch, function.passActive]
    )


def test_runModel_1(function, qtbot):
    function.modelInputData = []
    with (
        mock.patch.object(function, "startPass") as mockStart,
        qtbot.waitSignal(function.finished) as blocker,
    ):
        function.runModel()
    assert blocker.args == [False]
    mockStart.assert_not_called()


def test_runModel_2(function):
    function.modelInputData = [(0, 0, True)]
    with (
        mock.patch.object(function, "setupSignals") as mockSetup,
        mock.patch.object(function, "prepareModelBuildData"),
        mock.patch.object(function, "startPass") as mockStart,
    ):
        function.runModel()
    mockSetup.assert_called_once()
    mockStart.assert_called_once()


def test_runModel_flowWithRetry(function, qtbot):
    keys = ["image-000", "image-001", "image-002"]
    function.numberRetries = 1
    passes = []

    def prepare():
        function.modelBuildData = buildRunData(keys)
        function.modelRunList = list(keys)

    def slew():
        passes.append(list(function.modelRunList))
        for key in function.modelRunList:
            success = len(passes) > 1 or key != "image-001"
            function.collectPlateSolveResult(solveResult(key, success=success))

    function.modelInputData = [(10, 0), (20, 90), (30, 180)]
    with (
        mock.patch.object(function, "setupSignals"),
        mock.patch.object(function, "resetSignals"),
        mock.patch.object(function, "prepareModelBuildData", side_effect=prepare),
        mock.patch.object(function, "startSlew") as mockSlew,
        mock.patch.object(function, "sendModelProgress"),
        mock.patch.object(function, "buildProgModel"),
        qtbot.waitSignal(function.finished, timeout=2000) as blocker,
    ):
        mockSlew.emit.side_effect = slew
        function.runModel()
    assert blocker.args == [False]
    assert passes == [keys, ["image-001"]]
    assert all(function.modelBuildData[key]["success"] for key in keys)
    assert function.retries == 1
