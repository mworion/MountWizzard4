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
import pytest
import unittest.mock as mock
from pathlib import Path
from queue import Queue

from mw4.base.indiClass import IndiClass
from mw4.logic.camera.camera import Camera
from mw4.logic.camera.cameraIndi import CameraIndi
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function():
    camera = Camera(App())
    camera.exposureTime = 1
    camera.focalLength = 1
    func = CameraIndi(parent=camera)
    yield func
    func.app.threadPool.waitForDone(5000)


# ---------------------------------------------------------------------------
# setUpdateConfig
# ---------------------------------------------------------------------------


def test_setUpdateConfig(function):
    function.txQ = Queue()
    function.setUpdateConfig("test_device")
    assert function.txQ.qsize() == 4
    assert function.txQ.get() == ("test_device", "FITS_HEADER", {"FITS_OBJECT": "Skymodel"})
    assert function.txQ.get() == (
        "test_device",
        "FITS_HEADER",
        {"FITS_OBSERVER": "MountWizzard4"},
    )
    assert function.txQ.get() == (
        "test_device",
        "ACTIVE_DEVICES",
        {"ACTIVE_TELESCOPE": "LX200 10micron"},
    )
    assert function.txQ.get() == ("test_device", "TELESCOPE_TYPE", {"TELESCOPE_PRIMARY": "On"})


# ---------------------------------------------------------------------------
# setExposureState
# ---------------------------------------------------------------------------


def test_setExposureState_no_ccd_exposure(function):
    """No 'CCD_EXPOSURE' key → early return, no signals emitted."""
    slot = mock.MagicMock()
    function.signals.message.connect(slot)
    function.setExposureState({})
    slot.assert_not_called()
    function.signals.message.disconnect(slot)


def test_setExposureState_busy_value_gt_0(function):
    """State 'Busy' and value > 0 → message signal with remaining time."""
    vectors = {
        "CCD_EXPOSURE": {
            "state": "Busy",
            "members": {"CCD_EXPOSURE_VALUE": {"floatvalue": 5.0}},
        }
    }
    slot = mock.MagicMock()
    function.signals.message.connect(slot)
    function.setExposureState(vectors)
    slot.assert_called_once_with("expose  5 s")
    function.signals.message.disconnect(slot)


def test_setExposureState_busy_value_zero(function):
    """State 'Busy' and value == 0 → exposed signal with imagePath."""
    vectors = {
        "CCD_EXPOSURE": {
            "state": "Busy",
            "members": {"CCD_EXPOSURE_VALUE": {"floatvalue": 0.0}},
        }
    }
    slot = mock.MagicMock()
    function.signals.exposed.connect(slot)
    function.setExposureState(vectors)
    slot.assert_called_once_with(function.parent.imagePath)
    function.signals.exposed.disconnect(slot)


def test_setExposureState_ok_value_zero(function):
    """State 'Ok' and value == 0 → downloaded signal + empty message."""
    vectors = {
        "CCD_EXPOSURE": {
            "state": "Ok",
            "members": {"CCD_EXPOSURE_VALUE": {"floatvalue": 0.0}},
        }
    }
    dl_slot = mock.MagicMock()
    msg_slot = mock.MagicMock()
    function.signals.downloaded.connect(dl_slot)
    function.signals.message.connect(msg_slot)
    function.setExposureState(vectors)
    dl_slot.assert_called_once_with(function.parent.imagePath)
    msg_slot.assert_called_once_with("")
    function.signals.downloaded.disconnect(dl_slot)
    function.signals.message.disconnect(msg_slot)


def test_setExposureState_alert(function):
    """State 'Alert' → exposed(Path()), downloaded(Path()), exposeFinished and abort called."""
    vectors = {
        "CCD_EXPOSURE": {
            "state": "Alert",
            "members": {"CCD_EXPOSURE_VALUE": {"floatvalue": 0.0}},
        }
    }
    with mock.patch.object(function.parent, "exposeFinished") as mock_finished:
        with mock.patch.object(function, "abort") as mock_abort:
            function.setExposureState(vectors)
            mock_finished.assert_called_once()
            mock_abort.assert_called_once()


def test_setExposureState_unknown_state(function):
    """Unrecognised state → no branch taken, no side effects."""
    vectors = {
        "CCD_EXPOSURE": {
            "state": "Idle",
            "members": {"CCD_EXPOSURE_VALUE": {"floatvalue": 5.0}},
        }
    }
    slot = mock.MagicMock()
    function.signals.message.connect(slot)
    function.setExposureState(vectors)
    slot.assert_not_called()
    function.signals.message.disconnect(slot)


# ---------------------------------------------------------------------------
# setCanTemperature
# ---------------------------------------------------------------------------


def test_setCanTemperature_absent(function):
    """No 'CCD_TEMPERATURE' in vectors → data key not set."""
    function.data.pop("CAN_SET_CCD_TEMPERATURE", None)
    function.setCanTemperature({})
    assert "CAN_SET_CCD_TEMPERATURE" not in function.data


def test_setCanTemperature_present(function):
    """'CCD_TEMPERATURE' present → data['CAN_SET_CCD_TEMPERATURE'] = True."""
    function.data.pop("CAN_SET_CCD_TEMPERATURE", None)
    function.setCanTemperature({"CCD_TEMPERATURE": {"state": "Ok", "members": {}}})
    assert function.data["CAN_SET_CCD_TEMPERATURE"] is True


# ---------------------------------------------------------------------------
# addGainLimits
# ---------------------------------------------------------------------------


def test_addGainLimits_absent(function):
    """No 'CCD_GAIN' → data unchanged."""
    function.data.pop("CCD_GAIN.GAIN_MIN", None)
    function.data.pop("CCD_GAIN.GAIN_MAX", None)
    function.addGainLimits({})
    assert "CCD_GAIN.GAIN_MIN" not in function.data
    assert "CCD_GAIN.GAIN_MAX" not in function.data


def test_addGainLimits_with_limits(function):
    """'CCD_GAIN' with min/max → data populated."""
    vectors = {"CCD_GAIN": {"state": "Ok", "members": {"min": 0, "max": 255}}}
    function.addGainLimits(vectors)
    assert function.data["CCD_GAIN.GAIN_MIN"] == 0
    assert function.data["CCD_GAIN.GAIN_MAX"] == 255


def test_addGainLimits_without_min_max(function):
    """'CCD_GAIN' without min/max keys → default values applied."""
    vectors = {"CCD_GAIN": {"state": "Ok", "members": {}}}
    function.addGainLimits(vectors)
    assert function.data["CCD_GAIN.GAIN_MIN"] == 0
    assert function.data["CCD_GAIN.GAIN_MAX"] == 1


# ---------------------------------------------------------------------------
# addOffsetLimits
# ---------------------------------------------------------------------------


def test_addOffsetLimits_absent(function):
    """No 'CCD_OFFSET' → data unchanged."""
    function.data.pop("CCD_OFFSET.OFFSET_MIN", None)
    function.data.pop("CCD_OFFSET.OFFSET_MAX", None)
    function.addOffsetLimits({})
    assert "CCD_OFFSET.OFFSET_MIN" not in function.data
    assert "CCD_OFFSET.OFFSET_MAX" not in function.data


def test_addOffsetLimits_with_limits(function):
    """'CCD_OFFSET' with min/max → data populated."""
    vectors = {"CCD_OFFSET": {"state": "Ok", "members": {"min": 10, "max": 100}}}
    function.addOffsetLimits(vectors)
    assert function.data["CCD_OFFSET.OFFSET_MIN"] == 10
    assert function.data["CCD_OFFSET.OFFSET_MAX"] == 100


def test_addOffsetLimits_without_min_max(function):
    """'CCD_OFFSET' without min/max keys → default values applied."""
    vectors = {"CCD_OFFSET": {"state": "Ok", "members": {}}}
    function.addOffsetLimits(vectors)
    assert function.data["CCD_OFFSET.OFFSET_MIN"] == 0
    assert function.data["CCD_OFFSET.OFFSET_MAX"] == 1


# ---------------------------------------------------------------------------
# saveImageBLOB
# ---------------------------------------------------------------------------


def test_saveImageBLOB_absent(function):
    """No 'CCD1' in vectors → exposeFinished not called."""
    item = mock.MagicMock()
    item.eventtype = "SetBLOB"
    with mock.patch.object(function.parent, "exposeFinished") as mock_fin:
        function.saveImageBLOB(item, {})
        mock_fin.assert_not_called()


def test_saveImageBLOB_not_setblob(function):
    """'CCD1' present but item.eventtype != 'SetBLOB' → exposeFinished not called."""
    item = mock.MagicMock()
    item.eventtype = "DefBLOB"
    vectors = {
        "CCD1": {
            "members": {
                "CCD1": {"filename": "test.fits", "blobformat": ".fits", "blobsize": 100}
            }
        }
    }
    with mock.patch.object(function.parent, "exposeFinished") as mock_fin:
        function.saveImageBLOB(item, vectors)
        mock_fin.assert_not_called()


def test_saveImageBLOB_no_filename(function):
    """'CCD1' present, SetBLOB, but filename is empty → exposeFinished not called."""
    item = mock.MagicMock()
    item.eventtype = "SetBLOB"
    vectors = {
        "CCD1": {"members": {"CCD1": {"filename": "", "blobformat": ".fits", "blobsize": 0}}}
    }
    with mock.patch.object(function.parent, "exposeFinished") as mock_fin:
        function.saveImageBLOB(item, vectors)
        mock_fin.assert_not_called()


def test_saveImageBLOB_fits(function):
    """SetBLOB with .fits format → imagePath suffix updated, rename called, writeImageFitsHeader called."""
    item = mock.MagicMock()
    item.eventtype = "SetBLOB"
    vectors = {
        "CCD1": {
            "members": {
                "CCD1": {"filename": "image.fits", "blobformat": ".fits", "blobsize": 1024}
            }
        }
    }
    mock_blob_file = mock.MagicMock()
    mock_temp_dir = mock.MagicMock()
    mock_temp_dir.__truediv__ = mock.MagicMock(return_value=mock_blob_file)
    function.app.mwGlob["tempDir"] = mock_temp_dir
    function.parent.imagePath = Path("tests/work/temp/capture.fits")
    with mock.patch.object(function.parent, "writeImageFitsHeader") as mock_fits:
        with mock.patch.object(function.parent, "exposeFinished") as mock_fin:
            function.saveImageBLOB(item, vectors)
            assert function.parent.imagePath == Path("tests/work/temp/capture.fits")
            mock_blob_file.rename.assert_called_once_with(function.parent.imagePath)
            mock_fits.assert_called_once()
            mock_fin.assert_called_once()


def test_saveImageBLOB_xisf(function):
    """SetBLOB with .xisf format → imagePath suffix updated, rename called, writeImageXisfHeader called."""
    item = mock.MagicMock()
    item.eventtype = "SetBLOB"
    vectors = {
        "CCD1": {
            "members": {
                "CCD1": {"filename": "image.xisf", "blobformat": ".xisf", "blobsize": 2048}
            }
        }
    }
    mock_blob_file = mock.MagicMock()
    mock_temp_dir = mock.MagicMock()
    mock_temp_dir.__truediv__ = mock.MagicMock(return_value=mock_blob_file)
    function.app.mwGlob["tempDir"] = mock_temp_dir
    function.parent.imagePath = Path("tests/work/temp/capture.fits")
    with mock.patch.object(function, "writeImageXisfHeader") as mock_xisf:
        with mock.patch.object(function.parent, "exposeFinished") as mock_fin:
            function.saveImageBLOB(item, vectors)
            assert function.parent.imagePath == Path("tests/work/temp/capture.xisf")
            mock_blob_file.rename.assert_called_once_with(function.parent.imagePath)
            mock_xisf.assert_called_once()
            mock_fin.assert_called_once()


# ---------------------------------------------------------------------------
# writeVectorsToData
# ---------------------------------------------------------------------------


def test_writeVectorsToData(function):
    """All delegate methods and super() are called with item and/or vectors."""
    item = mock.MagicMock()
    vectors = {}
    with mock.patch.object(IndiClass, "writeVectorsToData") as mock_super:
        with mock.patch.object(function, "addGainLimits") as mock_gain:
            with mock.patch.object(function, "addOffsetLimits") as mock_offset:
                with mock.patch.object(function, "setCanTemperature") as mock_temp:
                    with mock.patch.object(function, "setExposureState") as mock_exp:
                        with mock.patch.object(function, "saveImageBLOB") as mock_blob:
                            function.writeVectorsToData(item, vectors)
                            mock_super.assert_called_once_with(item, vectors)
                            mock_gain.assert_called_once_with(vectors)
                            mock_offset.assert_called_once_with(vectors)
                            mock_temp.assert_called_once_with(vectors)
                            mock_exp.assert_called_once_with(vectors)
                            mock_blob.assert_called_once_with(item, vectors)


# ---------------------------------------------------------------------------
# sendDownloadMode
# ---------------------------------------------------------------------------


def test_sendDownloadMode(function):
    """sendDownloadMode() puts 2 items into the txQ: READOUT_QUALITY and CCD_COMPRESSION."""
    function.txQ = Queue()
    function.deviceName = "test_cam"
    function.sendDownloadMode()
    assert function.txQ.qsize() == 2
    assert function.txQ.get() == ("test_cam", "READOUT_QUALITY", {"QUALITY_LOW": "On"})
    assert function.txQ.get() == ("test_cam", "CCD_COMPRESSION", {"INDI_DISABLED": "On"})


# ---------------------------------------------------------------------------
# expose
# ---------------------------------------------------------------------------


def test_expose(function):
    """expose() puts 6 correctly structured items into the txQ."""
    function.txQ = Queue()
    function.deviceName = "test_cam"
    function.parent._binning = 2
    function.parent.posX = 10
    function.parent.posY = 20
    function.parent.width = 800
    function.parent.height = 600
    function.parent.exposureTime = 3.0
    function.expose()
    assert function.txQ.qsize() == 6
    assert function.txQ.get() == ("test_cam", "READOUT_QUALITY", {"QUALITY_LOW": "On"})
    assert function.txQ.get() == ("test_cam", "CCD_COMPRESSION", {"INDI_DISABLED": "On"})
    assert function.txQ.get() == ("test_cam", "READOUT_QUALITY", {"QUALITY_LOW": "On"})
    assert function.txQ.get() == ("test_cam", "CCD_BINNING", {"HOR_BIN": 2, "VER_BIN": 2})
    assert function.txQ.get() == (
        "test_cam",
        "CCD_FRAME",
        {"X": 10, "Y": 20, "WIDTH": 800, "HEIGHT": 600},
    )
    assert function.txQ.get() == ("test_cam", "CCD_EXPOSURE", {"CCD_EXPOSURE_VALUE": 3.0})


# ---------------------------------------------------------------------------
# abort
# ---------------------------------------------------------------------------


def test_abort(function):
    """abort() puts one abort command into the txQ."""
    function.txQ = Queue()
    function.deviceName = "test_cam"
    function.abort()
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cam", "CCD_ABORT_EXPOSURE", {"ABORT": "On"})


# ---------------------------------------------------------------------------
# sendCoolerSwitch
# ---------------------------------------------------------------------------


def test_sendCoolerSwitch_off(function):
    """sendCoolerSwitch(False) → queues COOLER_ON='Off'."""
    function.txQ = Queue()
    function.deviceName = "test_cam"
    function.sendCoolerSwitch(coolerOn=False)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cam", "CCD_COOLER", {"COOLER_ON": "Off"})


def test_sendCoolerSwitch_on(function):
    """sendCoolerSwitch(True) → queues COOLER_ON='On'."""
    function.txQ = Queue()
    function.deviceName = "test_cam"
    function.sendCoolerSwitch(coolerOn=True)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cam", "CCD_COOLER", {"COOLER_ON": "On"})


# ---------------------------------------------------------------------------
# sendCoolerTemp
# ---------------------------------------------------------------------------


def test_sendCoolerTemp(function):
    """sendCoolerTemp() queues the target CCD temperature."""
    function.txQ = Queue()
    function.deviceName = "test_cam"
    function.sendCoolerTemp(temperature=-10.5)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == (
        "test_cam",
        "CCD_TEMPERATURE",
        {"CCD_TEMPERATURE_VALUE": -10.5},
    )


# ---------------------------------------------------------------------------
# sendOffset
# ---------------------------------------------------------------------------


def test_sendOffset(function):
    """sendOffset() queues the offset value."""
    function.txQ = Queue()
    function.deviceName = "test_cam"
    function.sendOffset(offset=50)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cam", "CCD_OFFSET", {"OFFSET": 50})


# ---------------------------------------------------------------------------
# sendGain
# ---------------------------------------------------------------------------


def test_sendGain(function):
    """sendGain() queues the gain value."""
    function.txQ = Queue()
    function.deviceName = "test_cam"
    function.sendGain(gain=200)
    assert function.txQ.qsize() == 1
    assert function.txQ.get() == ("test_cam", "CCD_GAIN", {"GAIN": 200})
