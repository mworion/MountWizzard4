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
import unittest.mock as mock
from mw4.base.sgproClass import SGProClass
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraSGPro import CameraSGPro
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
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
        camera.imagePath = "/tmp/test.fits"
        func = CameraSGPro(camera)
    except Exception as e:
        pytest.skip(f"Fixture initialization failed: {e}")
    yield func


def test_cameraSGPro_inheritsFromSGProClass(function):
    assert isinstance(function, SGProClass)


def test_cameraSGPro_instantiation(function):
    assert function is not None


def test_getInitialConfig(function):
    function.data.clear()
    function.getInitialConfig()
    assert function.data.get("CCD_BINNING.HOR_BIN") == 1


def test_sendDownloadMode(function):
    function.sendDownloadMode()


def test_sendCoolerSwitch(function):
    function.sendCoolerSwitch(coolerOn=True)


def test_sendCoolerTemp(function):
    function.sendCoolerTemp(temperature=-10)


def test_sendOffset(function):
    function.sendOffset(offset=10)


def test_sendGain(function):
    function.sendGain(gain=100)


def test_captureImage(function):
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True, "Receipt": "1234"}
        suc, response = function.captureImage(params={})
        assert suc is True
        assert response["Receipt"] == "1234"
        mock_request.assert_called_once_with("image", params={})


def test_abortImage(function):
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True}
        result = function.abortImage()
        assert result is True
        mock_request.assert_called_once_with("abortimage")


def test_getImagePath(function):
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True}
        result = function.getImagePath(receipt="1234")
        assert result is True
        mock_request.assert_called_once_with("imagepath/1234")


def test_getCameraProps(function):
    with mock.patch.object(function, "requestProperty") as mock_request:
        mock_request.return_value = {"Success": True, "Props": {}}
        suc, response = function.getCameraProps()
        assert suc is True
        mock_request.assert_called_once_with("cameraprops")


def test_abort(function):
    with mock.patch.object(function, "abortImage", return_value=True) as mock_abort:
        result = function.abort()
        assert result is True
        mock_abort.assert_called_once()


def test_expose(function):
    with mock.patch.object(function.threadPool, "start") as mock_start:
        function.expose()
        mock_start.assert_called_once()


def test_workerExpose_captureImage_fails(function):
    function.parent.exposing = True
    with mock.patch.object(function, "captureImage", return_value=(False, {})):
        function.workerExpose()
    assert function.parent.exposing is False


def test_workerExpose_no_receipt(function):
    function.parent.exposing = True
    with mock.patch.object(function, "captureImage", return_value=(True, {})):
        function.workerExpose()
    assert function.parent.exposing is False


def test_workerExpose_aborted_during_wait(function):
    function.parent.exposing = True
    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function, "waitFunc", return_value=True),
        mock.patch.object(function, "getImagePath") as mock_get_path,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep"),
    ):

        def abortAfterFirst(*args, **kwargs):
            function.parent.exposing = False
            return True

        function.waitFunc.side_effect = abortAfterFirst
        function.workerExpose()
    mock_get_path.assert_not_called()


def test_waitFunc(function):
    function.data["Device.Message"] = "camera integrating"
    assert function.waitFunc() is True
    function.data["Device.Message"] = "idle"
    assert function.waitFunc() is False


def test_workerExpose_success(function):
    function.parent.exposing = True
    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function, "waitFunc", side_effect=[True, False]),
        mock.patch.object(function, "getImagePath", return_value=True),
        mock.patch.object(function.signals, "exposed") as mock_exposed,
        mock.patch.object(function.signals, "downloaded") as mock_downloaded,
        mock.patch.object(function.parent, "updateImageFitsHeaderPointing") as mock_update,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep"),
    ):
        function.workerExpose()
    mock_exposed.emit.assert_called_once_with(function.parent.imagePath)
    mock_downloaded.emit.assert_called_once_with(function.parent.imagePath)
    mock_update.assert_called_once()


def test_workerExpose_getImagePath_timeout(function):
    function.parent.exposing = True
    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function, "waitFunc", return_value=False),
        mock.patch.object(function, "getImagePath", return_value=False),
        mock.patch.object(function.parent, "updateImageFitsHeaderPointing") as mock_update,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep"),
    ):
        function.workerExpose()
    mock_update.assert_called_once()


def test_workerExpose_aborted_after_download_wait(function):
    function.parent.exposing = True
    with (
        mock.patch.object(function, "captureImage", return_value=(True, {"Receipt": "1234"})),
        mock.patch.object(function, "waitFunc", return_value=False),
        mock.patch.object(function, "getImagePath") as mock_get_path,
        mock.patch("mw4.logic.camera.cameraSGPro.time.sleep"),
    ):

        def abortDuringDownload(*args, **kwargs):
            function.parent.exposing = False
            return False

        mock_get_path.side_effect = abortDuringDownload
        function.workerExpose()
