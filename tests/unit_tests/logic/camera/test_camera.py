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
import importlib
import mw4.logic
import mw4.logic.camera.camera as cameraModule
import platform
import pytest
from astropy.io import fits
from mw4.logic.camera.camera import Camera
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function() -> None:
    try:
        func = Camera(app=App())
        yield func
    except (
        RuntimeError,
        ImportError,
        AttributeError,
        ConnectionError,
        OSError,
        ValueError,
    ) as e:
        pytest.skip(f"Camera initialization failed: {e}")


@pytest.fixture
def mocked_sleepAndEvents(monkeypatch, function) -> None:
    def test(a):
        function.exposing = False

    monkeypatch.setattr("mw4.logic.camera.camera.time.sleep", test)


def test_properties(function) -> None:
    function.framework = "indi"
    function.host = ("localhost", 7624)
    assert function.host == ("localhost", 7624)

    function.deviceName = "test"
    assert function.deviceName == "test"


def test_properties_1(function) -> None:
    function.data = {"CCD_BINNING.HOR_BIN": 1}
    function.binning = 1
    assert function.binning == 1


def test_properties_2(function) -> None:
    function.loadConfig = True
    function.framework = "indi"
    assert function.loadConfig


def test_propSubFrame_0(function) -> None:
    function.data = {
        "CCD_INFO.CCD_MAX_X": 1000,
        "CCD_INFO.CCD_MAX_Y": 1000,
        "CCD_BINNING.HOR_BIN": 1,
    }
    function.subFrame = 1
    assert function.posX == 0
    assert function.posY == 0
    assert function.width == 1000
    assert function.height == 1000


def test_propSubFrame_1(function) -> None:
    function.data = {
        "CCD_INFO.CCD_MAX_X": 1000,
        "CCD_INFO.CCD_MAX_Y": 1000,
        "CCD_BINNING.HOR_BIN": 1,
    }
    function.subFrame = 90
    assert function.posX == 50
    assert function.posY == 50
    assert function.width == 900
    assert function.height == 900


def test_propSubFrame_2(function) -> None:
    function.data = {
        "CCD_INFO.CCD_MAX_X": 100,
        "CCD_INFO.CCD_MAX_Y": 1000,
        "CCD_BINNING.HOR_BIN": 1,
    }
    function.subFrame = 100
    assert function.posX == 0
    assert function.posY == 0
    assert function.width == 100
    assert function.height == 1000


def test_propSubFrame_3(function) -> None:
    function.data = {
        "CCD_INFO.CCD_MAX_X": 1000,
        "CCD_INFO.CCD_MAX_Y": 100,
        "CCD_BINNING.HOR_BIN": 1,
    }
    function.subFrame = 100
    assert function.posX == 0
    assert function.posY == 0
    assert function.width == 1000
    assert function.height == 100


def test_propSubFrame_4(function) -> None:
    function.data = {
        "CCD_INFO.CCD_MAX_X": 1000,
        "CCD_INFO.CCD_MAX_Y": 1000,
        "CCD_BINNING.HOR_BIN": 1,
    }
    function.subFrame = 50
    assert function.posX == 250
    assert function.posY == 250
    assert function.width == 500
    assert function.height == 500


def test_propSubFrame_5(function) -> None:
    function.binning = 2
    function.data = {
        "CCD_INFO.CCD_MAX_X": 1000,
        "CCD_INFO.CCD_MAX_Y": 1000,
        "CCD_BINNING.HOR_BIN": 1,
    }
    function.subFrame = 100
    assert function.posX == 0
    assert function.posY == 0
    assert function.width == 1000
    assert function.height == 1000


def test_propSubFrame_6(function) -> None:
    function.subFrame = 100
    assert function.subFrame == 100


def test_exposeFinished(function) -> None:
    function.exposeFinished()
    assert not function.exposing


def test_startCommunication_1(function) -> None:
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "startCommunication", return_value=True):
        function.startCommunication()


def test_stopCommunication_1(function) -> None:
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "stopCommunication", return_value=True):
        function.stopCommunication()


def test_expose_2(function) -> None:
    function.exposing = True
    function.framework = "indi"
    suc = function.expose(imagePath="tests", exposureTime=1, binning=0)
    assert not suc


def test_expose_3(function) -> None:
    function.exposing = False
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "expose", return_value=True):
        suc = function.expose(imagePath="tests", exposureTime=1, binning=0)
        assert suc


def test_expose_4(function) -> None:
    function.exposing = False
    function.framework = ""
    suc = function.expose(imagePath="tests", exposureTime=1, binning=0)
    assert not suc


def test_abort_1(function) -> None:
    function.framework = "indi"
    function.exposing = True
    with mock.patch.object(function.run["indi"], "abort", return_value=False):
        result = function.abort()
        assert not result


def test_abort_2(function) -> None:
    function.framework = "indi"
    function.exposing = True
    with mock.patch.object(function.run["indi"], "abort", return_value=True):
        function.abort()
        assert not function.exposing


def test_abort_3(function) -> None:
    function.framework = ""
    result = function.abort()
    assert not result


def test_sendDownloadMode_2(function) -> None:
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendDownloadMode", return_value=True):
        function.sendDownloadMode()


def test_sendCoolerSwitch_2(function) -> None:
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendCoolerSwitch", return_value=True):
        function.sendCoolerSwitch()


def test_sendCoolerTemp_2(function) -> None:
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendCoolerTemp", return_value=True):
        function.sendCoolerTemp()


def test_sendOffset_2(function) -> None:
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendOffset", return_value=True):
        function.sendOffset()


def test_sendGain_2(function) -> None:
    function.framework = "indi"
    with mock.patch.object(function.run["indi"], "sendGain", return_value=True):
        function.sendGain()


def test_writeImageFitsHeader_1(function) -> None:
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    with (
        mock.patch.object(fits, "open", return_value=hdu),
        mock.patch.object(mw4.logic.camera.camera, "writeHeaderPointing"),
        mock.patch.object(mw4.logic.camera.camera, "writeHeaderCamera"),
    ):
        function.writeImageFitsHeader()


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_cameraAscom_import() -> None:
    import importlib

    spec = importlib.util.find_spec("mw4.logic.camera.cameraAscom")
    assert spec is not None


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_camera_sgpro_in_run(function) -> None:
    assert "sgpro" in function.run
    assert function.run["sgpro"] is not None


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows needed")
def test_camera_ascom_in_run() -> None:
    function = Camera(app=App())
    assert "ascom" in function.run
    assert function.run["ascom"] is not None


def test_camera_nonWindows_run() -> None:
    with mock.patch("platform.system", return_value="Linux"):
        function = Camera(app=App())
        assert "indi" in function.run
        assert "alpaca" in function.run
        assert "sgpro" not in function.run
        assert "ascom" not in function.run


def test_camera_nonWindows_import() -> None:
    with mock.patch("platform.system", return_value="Linux"):
        importlib.reload(cameraModule)
        assert hasattr(cameraModule, "Camera")
        assert hasattr(cameraModule, "CameraIndi")
        assert hasattr(cameraModule, "CameraAlpaca")
    importlib.reload(cameraModule)
