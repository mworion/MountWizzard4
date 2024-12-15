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
from PySide6.QtWidgets import QInputDialog, QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabImage_Manage import ImageManage
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = ImageManage(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_checkEnableCameraUI(function):
    function.checkEnableCameraUI()


def test_updateOffset_1(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = None
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = None
    function.updateOffset()


def test_updateOffset_2(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 0
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.updateOffset()


def test_updateOffset_3(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = []
    function.updateOffset()


def test_updateOffset_4(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = -1
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.updateOffset()


def test_updateOffset_5(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 2
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.updateOffset()


def test_updateGain_1(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = None
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = None
    function.updateGain()


def test_updateGain_2(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = 0
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.updateGain()


def test_updateGain_3(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = []
    function.updateGain()


def test_updateGain_4(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = -1
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.updateGain()


def test_updateGain_5(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = 2
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.updateGain()


def test_updateCooler_1(function):
    function.app.camera.data["CCD_COOLER.COOLER_ON"] = False
    function.updateCooler()


def test_updateCooler_2(function):
    function.app.camera.data["CCD_COOLER.COOLER_ON"] = True
    function.updateCooler()


def test_updateFilter(function):
    function.updateFilter()


def test_updateFocuser(function):
    function.updateFocuser()


def test_updateImagingParam_1(function):
    with mock.patch.object(function, "checkEnableCameraUI"):
        with mock.patch.object(function, "updateOffset"):
            with mock.patch.object(function, "updateGain"):
                with mock.patch.object(function, "updateCooler"):
                    with mock.patch.object(function, "updateFilter"):
                        with mock.patch.object(function, "updateFocuser"):
                            function.updateImagingParam()


def test_updateImagingParam_2(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 0
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.camera.data["CCD_GAIN.GAIN"] = 0
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_Y"] = 1
    function.app.camera.data["READOUT_QUALITY.QUALITY_LOW"] = True
    function.updateImagingParam()


def test_updateImagingParam_3(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 0
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.camera.data["CCD_GAIN.GAIN"] = 0
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_Y"] = 1
    function.app.camera.data["READOUT_QUALITY.QUALITY_LOW"] = True
    function.ui.automaticTelescope.setChecked(False)
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    function.updateImagingParam()


def test_updateImagingParam_4(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 0
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.camera.data["CCD_GAIN.GAIN"] = 0
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_X"] = 4000
    function.app.camera.data["CCD_INFO.CCD_MAX_Y"] = 4000
    function.app.camera.data["READOUT_QUALITY.QUALITY_LOW"] = True
    function.ui.automaticTelescope.setChecked(False)
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    function.updateImagingParam()
    assert function.ui.optimalBinning.text() == "2"


def test_updateImagingParam_5(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 0
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.camera.data["CCD_GAIN.GAIN"] = 0
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_X"] = 1000
    function.app.camera.data["CCD_INFO.CCD_MAX_Y"] = 4000
    function.app.camera.data["READOUT_QUALITY.QUALITY_LOW"] = True
    function.ui.automaticTelescope.setChecked(False)
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    function.updateImagingParam()
    assert function.ui.optimalBinning.text() == "1"


def test_updateImagingParam_6(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 0
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.camera.data["CCD_GAIN.GAIN"] = 0
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_X"] = 1
    function.app.camera.data["CCD_INFO.CCD_PIXEL_SIZE_Y"] = 1
    function.app.camera.data["CCD_INFO.CCD_MAX_X"] = 8000
    function.app.camera.data["CCD_INFO.CCD_MAX_Y"] = 6000
    function.app.camera.data["READOUT_QUALITY.QUALITY_LOW"] = True
    function.ui.automaticTelescope.setChecked(False)
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    function.updateImagingParam()
    assert function.ui.optimalBinning.text() == "3"


def test_setCoolerTemp_1(function):
    suc = function.setCoolerTemp()
    assert not suc


def test_setCoolerTemp_2(function):
    function.app.camera.data["CAN_SET_CCD_TEMPERATURE"] = False
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, False)):
        suc = function.setCoolerTemp()
        assert not suc


def test_setCoolerTemp_3(function):
    function.app.camera.data["CAN_SET_CCD_TEMPERATURE"] = True
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, True)):
        suc = function.setCoolerTemp()
        assert not suc


def test_setCoolerTemp_4(function):
    function.app.camera.data["CAN_SET_CCD_TEMPERATURE"] = True
    function.app.camera.data["CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"] = 10
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, True)):
        suc = function.setCoolerTemp()
        assert suc


def test_setCoolerTemp_5(function):
    function.app.camera.data["CAN_SET_CCD_TEMPERATURE"] = True
    function.app.camera.data["CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"] = 10
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, False)):
        suc = function.setCoolerTemp()
        assert not suc


def test_setOffset_1(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = None
    suc = function.setOffset()
    assert not suc


def test_setOffset_2(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_MIN"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_MAX"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    with mock.patch.object(QInputDialog, "getItem", return_value=("1", False)):
        suc = function.setOffset()
        assert not suc


def test_setOffset_3(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_MIN"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_MAX"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    with mock.patch.object(QInputDialog, "getItem", return_value=("1", True)):
        suc = function.setOffset()
        assert suc


def test_setOffset_4(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_MIN"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_MAX"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = None
    with mock.patch.object(QInputDialog, "getInt", return_value=("1", True)):
        suc = function.setOffset()
        assert suc


def test_setOffset_5(function):
    function.app.camera.data["CCD_OFFSET.OFFSET"] = 1
    function.app.camera.data["CCD_OFFSET.OFFSET_MIN"] = None
    function.app.camera.data["CCD_OFFSET.OFFSET_MAX"] = None
    function.app.camera.data["CCD_OFFSET.OFFSET_LIST"] = None
    with mock.patch.object(QInputDialog, "getInt", return_value=("1", True)):
        suc = function.setOffset()
        assert suc


def test_setGain_1(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = None
    suc = function.setGain()
    assert not suc


def test_setGain_2(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_MIN"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_MAX"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    with mock.patch.object(QInputDialog, "getItem", return_value=("1", False)):
        suc = function.setGain()
        assert not suc


def test_setGain_3(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_MIN"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_MAX"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    with mock.patch.object(QInputDialog, "getItem", return_value=("1", True)):
        suc = function.setGain()
        assert suc


def test_setGain_4(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_MIN"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_MAX"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = None
    with mock.patch.object(QInputDialog, "getInt", return_value=("1", True)):
        suc = function.setGain()
        assert suc


def test_setGain_5(function):
    function.app.camera.data["CCD_GAIN.GAIN"] = 1
    function.app.camera.data["CCD_GAIN.GAIN_MIN"] = None
    function.app.camera.data["CCD_GAIN.GAIN_MAX"] = None
    function.app.camera.data["CCD_GAIN.GAIN_LIST"] = None
    with mock.patch.object(QInputDialog, "getInt", return_value=("1", True)):
        suc = function.setGain()
        assert suc


def test_setFilterNumber_1(function):
    suc = function.setFilterNumber()
    assert not suc


def test_setFilterNumber_2(function):
    function.app.filter.data["FILTER_SLOT.FILTER_SLOT_VALUE"] = 10
    function.app.filter.data["FILTER_NAME.FILTER_SLOT_NAME_0"] = "test"
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, False)):
        suc = function.setFilterNumber()
        assert not suc


def test_setFilterNumber_3(function):
    function.app.filter.data = {"FILTER_SLOT.FILTER_SLOT_VALUE": 10}
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, True)):
        suc = function.setFilterNumber()
        assert suc


def test_setFilterName_1(function):
    function.app.filter.data["FILTER_SLOT.FILTER_SLOT_VALUE"] = None
    suc = function.setFilterName()
    assert not suc


def test_setFilterName_2(function):
    function.app.filter.data["FILTER_SLOT.FILTER_SLOT_VALUE"] = 1
    function.app.filter.data["FILTER_NAME.FILTER_SLOT_NAME_0"] = "test1"
    function.app.filter.data["FILTER_NAME.FILTER_SLOT_NAME_1"] = "test2"
    with mock.patch.object(QInputDialog, "getItem", return_value=(10, False)):
        suc = function.setFilterName()
        assert not suc


def test_setFilterName_3(function):
    function.app.filter.data["FILTER_SLOT.FILTER_SLOT_VALUE"] = 1
    function.app.filter.data["FILTER_NAME.FILTER_SLOT_NAME_0"] = "test1"
    function.app.filter.data["FILTER_NAME.FILTER_SLOT_NAME_1"] = "test2"
    with mock.patch.object(QInputDialog, "getItem", return_value=("test1", True)):
        suc = function.setFilterName()
        assert suc


def test_setFilterName_4(function):
    function.app.filter.data = {
        "FILTER_SLOT.FILTER_SLOT_VALUE": 1,
        "FILTER_NAME.FILTER_SLOT_NAME_1": "test1",
        "FILTER_NAME.FILTER_SLOT_NAME_2": "test2",
    }
    with mock.patch.object(QInputDialog, "getItem", return_value=("test1", True)):
        suc = function.setFilterName()
        assert suc


def test_setDownloadModeFast(function):
    function.setDownloadModeFast()


def test_setDownloadModeSlow(function):
    function.setDownloadModeSlow()


def test_setCoolerOn_1(function):
    function.setCoolerOn()


def test_setCoolerOff_1(function):
    function.setCoolerOff()


def test_updateCoverStatGui_1(function):
    function.app.cover.data["CAP_PARK.PARK"] = True
    function.updateCoverStatGui()


def test_updateCoverStatGui_2(function):
    function.app.cover.data["CAP_PARK.PARK"] = False
    function.updateCoverStatGui()


def test_updateCoverStatGui_3(function):
    function.app.cover.data["CAP_PARK.PARK"] = None
    function.updateCoverStatGui()


def test_updateCoverLightGui_1(function):
    function.app.cover.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] = True
    function.updateCoverLightGui()


def test_updateCoverLightGui_2(function):
    function.app.cover.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] = False
    function.updateCoverLightGui()


def test_updateCoverLightGui_3(function):
    function.app.cover.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] = None
    function.updateCoverLightGui()


def test_setCoverPark_1(function):
    with mock.patch.object(function.app.cover, "closeCover", return_value=False):
        suc = function.setCoverPark()
        assert not suc


def test_setCoverPark_2(function):
    with mock.patch.object(function.app.cover, "closeCover", return_value=True):
        suc = function.setCoverPark()
        assert suc


def test_setCoverUnpark_1(function):
    with mock.patch.object(function.app.cover, "openCover", return_value=False):
        suc = function.setCoverUnpark()
        assert not suc


def test_setCoverUnpark_2(function):
    with mock.patch.object(function.app.cover, "openCover", return_value=True):
        suc = function.setCoverUnpark()
        assert suc


def test_setCoverHalt_1(function):
    with mock.patch.object(function.app.cover, "haltCover", return_value=False):
        suc = function.setCoverHalt()
        assert not suc


def test_setCoverHalt_2(function):
    with mock.patch.object(function.app.cover, "haltCover", return_value=True):
        suc = function.setCoverHalt()
        assert suc


def test_moveFocuserIn_1(function):
    with mock.patch.object(function.app.focuser, "move", return_value=False):
        suc = function.moveFocuserIn()
        assert not suc


def test_moveFocuserIn_2(function):
    with mock.patch.object(function.app.focuser, "move", return_value=True):
        suc = function.moveFocuserIn()
        assert suc


def test_moveFocuserOut_1(function):
    with mock.patch.object(function.app.focuser, "move", return_value=False):
        suc = function.moveFocuserOut()
        assert not suc


def test_moveFocuserOut_2(function):
    with mock.patch.object(function.app.focuser, "move", return_value=True):
        suc = function.moveFocuserOut()
        assert suc


def test_haltFocuser_1(function):
    with mock.patch.object(function.app.focuser, "halt", return_value=False):
        suc = function.haltFocuser()
        assert not suc


def test_haltFocuser_2(function):
    with mock.patch.object(function.app.focuser, "halt", return_value=True):
        suc = function.haltFocuser()
        assert suc


def test_switchLightOn_1(function):
    with mock.patch.object(function.app.cover, "lightOn", return_value=False):
        suc = function.switchLightOn()
        assert not suc


def test_switchLightOn_2(function):
    with mock.patch.object(function.app.cover, "lightOn", return_value=True):
        suc = function.switchLightOn()
        assert suc


def test_switchLightOff_1(function):
    with mock.patch.object(function.app.cover, "lightOff", return_value=False):
        suc = function.switchLightOff()
        assert not suc


def test_switchLightOff_2(function):
    with mock.patch.object(function.app.cover, "lightOff", return_value=True):
        suc = function.switchLightOff()
        assert suc


def test_setLightIntensity_1(function):
    suc = function.setLightIntensity()
    assert not suc


def test_setLightIntensity_2(function):
    function.app.cover.data["FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"] = 10
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, False)):
        suc = function.setLightIntensity()
        assert not suc


def test_setLightIntensity_3(function):
    function.app.cover.data["FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"] = 10
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, True)):
        with mock.patch.object(function.app.cover, "lightIntensity", return_value=False):
            suc = function.setLightIntensity()
            assert not suc


def test_setLightIntensity_4(function):
    function.app.cover.data["FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"] = 10
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, True)):
        with mock.patch.object(function.app.cover, "lightIntensity", return_value=True):
            suc = function.setLightIntensity()
            assert suc


def test_updateDomeGui_1(function):
    function.app.dome.data["DOME_MOTION.DOME_CW"] = True
    function.app.dome.data["DOME_MOTION.DOME_CCW"] = True
    function.updateDomeGui()


def test_updateDomeGui_2(function):
    function.app.dome.data["DOME_MOTION.DOME_CW"] = False
    function.app.dome.data["DOME_MOTION.DOME_CCW"] = False
    function.updateDomeGui()


def test_updateShutterStatGui_1(function):
    function.app.dome.data["DOME_SHUTTER.SHUTTER_OPEN"] = True
    function.app.dome.data["Status.Shutter"] = "test"
    function.updateShutterStatGui()

    assert function.ui.domeShutterStatusText.text() == "test"


def test_updateShutterStatGui_2(function):
    function.app.dome.data["DOME_SHUTTER.SHUTTER_OPEN"] = False
    function.app.dome.data["Status.Shutter"] = "test"
    function.updateShutterStatGui()

    assert function.ui.domeShutterStatusText.text() == "test"


def test_updateShutterStatGui_3(function):
    function.app.dome.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
    function.app.dome.data["Status.Shutter"] = "test"
    function.updateShutterStatGui()

    assert function.ui.domeShutterStatusText.text() == "test"


def test_domeSlewCW_0(function):
    function.app.deviceStat["dome"] = False
    suc = function.domeSlewCW()
    assert not suc


def test_domeSlewCW_1(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "slewCW", return_value=False):
        suc = function.domeSlewCW()
        assert not suc


def test_domeSlewCW_2(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "slewCW", return_value=True):
        suc = function.domeSlewCW()
        assert suc


def test_domeSlewCCW_0(function):
    function.app.deviceStat["dome"] = False
    suc = function.domeSlewCCW()
    assert not suc


def test_domeSlewCCW_1(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "slewCCW", return_value=False):
        suc = function.domeSlewCCW()
        assert not suc


def test_domeSlewCCW_2(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "slewCCW", return_value=True):
        suc = function.domeSlewCCW()
        assert suc


def test_domeAbortSlew_0(function):
    function.app.deviceStat["dome"] = False
    suc = function.domeAbortSlew()
    assert not suc


def test_domeAbortSlew_1(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "abortSlew", return_value=False):
        suc = function.domeAbortSlew()
        assert not suc


def test_domeAbortSlew_2(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "abortSlew", return_value=True):
        suc = function.domeAbortSlew()
        assert suc


def test_domeOpenShutter_0(function):
    function.app.deviceStat["dome"] = False
    suc = function.domeOpenShutter()
    assert not suc


def test_domeOpenShutter_1(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "openShutter", return_value=False):
        suc = function.domeOpenShutter()
        assert not suc


def test_domeOpenShutter_2(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "openShutter", return_value=True):
        suc = function.domeOpenShutter()
        assert suc


def test_domeCloseShutter_0(function):
    function.app.deviceStat["dome"] = False
    suc = function.domeCloseShutter()
    assert not suc


def test_domeCloseShutter_1(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "closeShutter", return_value=False):
        suc = function.domeCloseShutter()
        assert not suc


def test_domeCloseShutter_2(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function.app.dome, "closeShutter", return_value=True):
        suc = function.domeCloseShutter()
        assert suc


def test_domeMoveGameController_0(function):
    function.app.deviceStat["dome"] = False
    suc = function.domeMoveGameController(128, 128)
    assert not suc


def test_domeMoveGameController_1(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function, "domeAbortSlew"):
        suc = function.domeMoveGameController(128, 128)
        assert suc


def test_domeMoveGameController_2(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function, "domeSlewCCW"):
        with mock.patch.object(function, "domeOpenShutter"):
            suc = function.domeMoveGameController(0, 0)
            assert suc


def test_domeMoveGameController_3(function):
    function.app.deviceStat["dome"] = True
    with mock.patch.object(function, "domeSlewCW"):
        with mock.patch.object(function, "domeCloseShutter"):
            suc = function.domeMoveGameController(255, 255)
            assert suc
