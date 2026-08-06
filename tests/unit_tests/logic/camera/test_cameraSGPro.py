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
import pytest
from mw4.base.sgproClass import SGProClass
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraSGPro import CameraSGPro
from pathlib import Path
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function() -> None:
    try:
        app = App()
        camera = Camera(app)
        camera.exposureTime = 1
        camera.binning = 1
        camera.focalLength = 1
        camera.posXASCOM = 0
        camera.posYASCOM = 0
        camera.widthASCOM = 100
        camera.heightASCOM = 100
        camera.fastReadout = False
        camera.imagePath = Path("/tmp/test.fits")
        func = CameraSGPro(camera)
        func.parent = camera
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_cameraSGPro_inheritsFromSGProClass(function) -> None:
    assert isinstance(function, SGProClass)


def test_cameraSGPro_instantiation(function) -> None:
    assert function is not None


def test_getInitialConfig(function) -> None:
    function.data.clear()
    function.getInitialConfig()
    assert function.data.get("CCD_BINNING.HOR_BIN") == 1


def test_sendDownloadMode(function) -> None:
    function.sendDownloadMode()


def test_sendCoolerSwitch(function) -> None:
    function.sendCoolerSwitch(coolerOn=True)


def test_sendCoolerTemp(function) -> None:
    function.sendCoolerTemp(temperature=-10)


def test_sendOffset(function) -> None:
    function.sendOffset(offset=10)


def test_sendGain(function) -> None:
    function.sendGain(gain=100)


def test_captureImage(function) -> None:
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True, "Receipt": "1234"}
        suc, response = function.captureImage(params={})
        assert suc is True
        assert response["Receipt"] == "1234"
        mock_request.assert_called_once_with("image", params={})


def test_abortImage(function) -> None:
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True}
        result = function.abortImage()
        assert result is True
        mock_request.assert_called_once_with("abortimage")


def test_getImagePath(function) -> None:
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True, "Message": "/tmp/image.fits"}
        suc, imagePath = function.getImagePath(receipt="1234")
        assert suc is True
        assert imagePath == "/tmp/image.fits"
        mock_request.assert_called_once_with("imagepath/1234")


def test_getCameraProps(function) -> None:
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True, "Props": {}}
        suc, _response = function.getCameraProps()
        assert suc is True
        mock_request.assert_called_once_with("cameraprops")


def test_abort(function) -> None:
    with mock.patch.object(function, "abortImage", return_value=True) as mock_abort:
        result = function.abort()
        assert result is True
        mock_abort.assert_called_once()


def test_expose(function) -> None:
    with mock.patch.object(function.threadPool, "start") as mock_start:
        function.expose()
        mock_start.assert_called_once()
        assert function.workerExpose is not None


def test_startExpose_captureImage_fails(function) -> None:
    function.parent.exposing = True
    with mock.patch.object(function, "captureImage", return_value=(False, {})):
        receipt = function.startExpose()
    assert receipt == ""


def test_startExpose_no_receipt(function) -> None:
    function.parent.exposing = True
    with mock.patch.object(function, "captureImage", return_value=(True, {})):
        receipt = function.startExpose()
    assert receipt == ""


def test_startExpose_success(function) -> None:
    function.parent.exposing = True
    function.data["Device.Message"] = "integrating"
    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function.signals, "message") as mock_message,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep"),
    ):
        receipt = function.startExpose()
    assert receipt == "1234"
    mock_message.emit.assert_called_once_with("expose   1 s")


def test_startExpose_waits_for_integrating(function) -> None:
    function.parent.exposing = True
    function.data["Device.Message"] = "waiting"
    callCount = 0

    def sleepSideEffect(*args, **kwargs):
        nonlocal callCount
        callCount += 1
        if callCount == 1:
            function.data["Device.Message"] = "integrating"

    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function.signals, "message") as mock_message,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep", side_effect=sleepSideEffect),
    ):
        receipt = function.startExpose()
    assert receipt == "1234"
    assert mock_message.emit.call_count == 1


def test_runExpose(function) -> None:
    function.parent.exposing = True
    function.data["Device.Message"] = "integrating"
    callCount = 0

    def sleepSideEffect(*args, **kwargs):
        nonlocal callCount
        callCount += 1
        if callCount == 1:
            function.data["Device.Message"] = "idle"

    with (
        mock.patch.object(function.signals, "message") as mock_message,
        mock.patch.object(function.signals, "exposed") as mock_exposed,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep", side_effect=sleepSideEffect),
    ):
        function.runExpose()
    mock_exposed.emit.assert_called_once_with(function.parent.imagePath)
    assert mock_message.emit.call_count == 1


def test_runDownload(function) -> None:
    function.parent.exposing = True
    function.data["Device.Message"] = "downloading"
    callCount = 0

    def sleepSideEffect(*args, **kwargs):
        nonlocal callCount
        callCount += 1
        if callCount == 1:
            function.data["Device.Message"] = "idle"

    with (
        mock.patch.object(function.signals, "message") as mock_message,
        mock.patch.object(function.signals, "downloaded") as mock_downloaded,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep", side_effect=sleepSideEffect),
    ):
        function.runDownload()
    mock_downloaded.emit.assert_called_once_with(function.parent.imagePath)
    assert mock_message.emit.call_count == 1


def test_runSave_success(function) -> None:
    function.parent.exposing = True
    function.data["Device.Message"] = "saving"
    callCount = 0

    def sleepSideEffect(*args, **kwargs):
        nonlocal callCount
        callCount += 1
        if callCount == 1:
            function.data["Device.Message"] = "idle"

    with (
        mock.patch.object(function, "getImagePath", return_value=(True, "/tmp/new.fits")),
        mock.patch.object(function.signals, "message") as mock_message,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep", side_effect=sleepSideEffect),
    ):
        suc = function.runSave(receipt="1234")
    assert suc is True
    assert function.parent.imagePath == Path("/tmp/new.fits")
    mock_message.emit.assert_called_once_with("save")


def test_runSave_fails(function) -> None:
    function.parent.imagePath = Path("/tmp/test.fits")
    function.parent.exposing = True
    function.data["Device.Message"] = "saving"
    callCount = 0

    def sleepSideEffect(*args, **kwargs):
        nonlocal callCount
        callCount += 1
        if callCount == 1:
            function.data["Device.Message"] = "idle"

    with (
        mock.patch.object(function, "getImagePath", return_value=(False, "")),
        mock.patch.object(function.signals, "message") as mock_message,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep", side_effect=sleepSideEffect),
    ):
        suc = function.runSave(receipt="1234")
    assert suc is False
    mock_message.emit.assert_called_once_with("save")


def test_runnerExpose_captureImage_fails(function) -> None:
    function.parent.exposing = True
    with mock.patch.object(function, "captureImage", return_value=(False, {})):
        function.runnerExpose()
    assert function.parent.exposing is False


def test_runnerExpose_no_receipt(function) -> None:
    function.parent.exposing = True
    with mock.patch.object(function, "captureImage", return_value=(True, {})):
        function.runnerExpose()
    assert function.parent.exposing is False


def test_runnerExpose_aborted_before_integrating(function) -> None:
    function.parent.exposing = False
    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function, "getImagePath", return_value=(True, "/tmp/new.fits")),
        mock.patch.object(function.parent, "writeImageFitsHeader") as mock_write,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep"),
    ):
        function.runnerExpose()
    mock_write.assert_called_once()


def _cycleMessage(function) -> None:
    """Helper to advance Device.Message through the SGPro exposure states."""
    callCount = 0

    def sleepSideEffect(*args, **kwargs):
        nonlocal callCount
        callCount += 1
        if callCount == 1:
            function.data["Device.Message"] = "integrating"
        elif callCount == 2:
            function.data["Device.Message"] = "downloading"
        elif callCount == 3:
            function.data["Device.Message"] = "saving"
        elif callCount == 4:
            function.data["Device.Message"] = "idle"

    return sleepSideEffect


def test_runnerExpose_success(function) -> None:
    function.parent.exposing = True
    function.data["Device.Message"] = "waiting"
    sleepSideEffect = _cycleMessage(function)
    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function, "getImagePath", return_value=(True, "/tmp/new.fits")),
        mock.patch.object(function.signals, "exposed") as mock_exposed,
        mock.patch.object(function.signals, "downloaded") as mock_downloaded,
        mock.patch.object(function.parent, "writeImageFitsHeader") as mock_write,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep", side_effect=sleepSideEffect),
    ):
        function.runnerExpose()
    assert function.parent.imagePath == Path("/tmp/new.fits")
    mock_exposed.emit.assert_called_once_with(function.parent.imagePath)
    mock_downloaded.emit.assert_called_once_with(function.parent.imagePath)
    mock_write.assert_called_once()


def test_runnerExpose_runSave_fails(function) -> None:
    function.parent.exposing = True
    function.data["Device.Message"] = "waiting"
    sleepSideEffect = _cycleMessage(function)
    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function, "getImagePath", return_value=(False, "")),
        mock.patch.object(function.parent, "writeImageFitsHeader") as mock_write,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep", side_effect=sleepSideEffect),
    ):
        function.runnerExpose()
    mock_write.assert_not_called()


def test_runnerExpose_aborted_during_integration(function) -> None:
    function.parent.exposing = True
    function.data["Device.Message"] = "integrating"

    def abortOnFirstSleep(*args, **kwargs):
        function.parent.exposing = False

    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function, "getImagePath", return_value=(True, "/tmp/new.fits")),
        mock.patch.object(function.parent, "writeImageFitsHeader") as mock_write,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep", side_effect=abortOnFirstSleep),
    ):
        function.runnerExpose()
    mock_write.assert_called_once()
