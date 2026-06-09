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
from mw4.gui.mainWaddon.tabImage_Manage import ImageManage
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QInputDialog
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
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
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = None
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = None
    function.updateOffset()


def test_updateOffset_2(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.updateOffset()


def test_updateOffset_3(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = []
    function.updateOffset()


def test_updateOffset_4(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = -1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.updateOffset()


def test_updateOffset_5(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 2
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.updateOffset()


def test_updateGain_1(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = None
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = None
    function.updateGain()


def test_updateGain_2(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.updateGain()


def test_updateGain_3(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = []
    function.updateGain()


def test_updateGain_4(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = -1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.updateGain()


def test_updateGain_5(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 2
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.updateGain()


def test_updateCooler_1(function):
    function.app.dReg.d["camera"].instance.data["CCD_COOLER.COOLER_ON"] = False
    function.updateCooler()


def test_updateCooler_2(function):
    function.app.dReg.d["camera"].instance.data["CCD_COOLER.COOLER_ON"] = True
    function.updateCooler()


def test_updateFilter(function):
    function.updateFilter()


def test_updateFocuser(function):
    function.updateFocuser()


def test_updateImagingParam_1(function):
    with (
        mock.patch.object(function, "checkEnableCameraUI"),
        mock.patch.object(function, "updateOffset"),
        mock.patch.object(function, "updateGain"),
        mock.patch.object(function, "updateCooler"),
        mock.patch.object(function, "updateFilter"),
        mock.patch.object(function, "updateFocuser"),
    ):
        function.updateImagingParam()


def test_updateImagingParam_2(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_X"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_Y"] = 1
    function.updateImagingParam()


def test_updateImagingParam_3(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_X"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_Y"] = 1
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    function.updateImagingParam()


def test_updateImagingParam_4(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_X"] = 4000
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_Y"] = 4000
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    function.updateImagingParam()
    assert function.ui.optimalBinning.text() == "2"


def test_updateImagingParam_5(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_X"] = 1000
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_Y"] = 4000
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    function.updateImagingParam()
    assert function.ui.optimalBinning.text() == "1"


def test_updateImagingParam_6(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 0
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_X"] = 8000
    function.app.dReg.d["camera"].instance.data["CCD_INFO.CCD_MAX_Y"] = 6000
    function.ui.aperture.setValue(0)
    function.ui.focalLength.setValue(0)
    function.updateImagingParam()
    assert function.ui.optimalBinning.text() == "3"


def test_setCoolerTemp_1(function):
    function.setCoolerTemp()


def test_setCoolerTemp_2(function):
    function.app.dReg.d["camera"].instance.data["CAN_SET_CCD_TEMPERATURE"] = False
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, False)):
        function.setCoolerTemp()


def test_setCoolerTemp_3(function):
    function.app.dReg.d["camera"].instance.data["CAN_SET_CCD_TEMPERATURE"] = True
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, True)):
        function.setCoolerTemp()


def test_setCoolerTemp_4(function):
    function.app.dReg.d["camera"].instance.data["CAN_SET_CCD_TEMPERATURE"] = True
    function.app.dReg.d["camera"].instance.data["CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"] = 10
    with (
        mock.patch.object(QInputDialog, "getInt", return_value=(10, True)),
        mock.patch.object(
            function.app.dReg.d["camera"].instance,
            "sendCoolerTemp",
            return_value=None,
        ),
    ):
        function.setCoolerTemp()


def test_setCoolerTemp_5(function):
    function.app.dReg.d["camera"].instance.data["CAN_SET_CCD_TEMPERATURE"] = True
    function.app.dReg.d["camera"].instance.data["CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE"] = 10
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, False)):
        function.setCoolerTemp()


def test_setOffset_1(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = None
    function.setOffset()


def test_setOffset_2(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_MIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_MAX"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    with mock.patch.object(QInputDialog, "getItem", return_value=("1", False)):
        function.setOffset()


def test_setOffset_3(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_MIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_MAX"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = ["1"]
    with (
        mock.patch.object(QInputDialog, "getItem", return_value=("1", True)),
        mock.patch.object(
            function.app.dReg.d["camera"].instance,
            "sendOffset",
            return_value=None,
        ),
    ):
        function.setOffset()


def test_setOffset_4(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_MIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_MAX"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = None
    with (
        mock.patch.object(QInputDialog, "getInt", return_value=("1", True)),
        mock.patch.object(
            function.app.dReg.d["camera"].instance,
            "sendOffset",
            return_value=None,
        ),
    ):
        function.setOffset()


def test_setOffset_5(function):
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_MIN"] = None
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_MAX"] = None
    function.app.dReg.d["camera"].instance.data["CCD_OFFSET.OFFSET_LIST"] = None
    with (
        mock.patch.object(QInputDialog, "getInt", return_value=("1", True)),
        mock.patch.object(
            function.app.dReg.d["camera"].instance,
            "sendOffset",
            return_value=None,
        ),
    ):
        function.setOffset()


def test_setGain_1(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = None
    function.setGain()


def test_setGain_2(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_MIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_MAX"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    with mock.patch.object(QInputDialog, "getItem", return_value=("1", False)):
        function.setGain()


def test_setGain_3(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_MIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_MAX"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = ["1"]
    with (
        mock.patch.object(QInputDialog, "getItem", return_value=("1", True)),
        mock.patch.object(
            function.app.dReg.d["camera"].instance,
            "sendGain",
            return_value=None,
        ),
    ):
        function.setGain()


def test_setGain_4(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_MIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_MAX"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = None
    with (
        mock.patch.object(QInputDialog, "getInt", return_value=("1", True)),
        mock.patch.object(
            function.app.dReg.d["camera"].instance,
            "sendGain",
            return_value=None,
        ),
    ):
        function.setGain()


def test_setGain_5(function):
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN"] = 1
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_MIN"] = None
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_MAX"] = None
    function.app.dReg.d["camera"].instance.data["CCD_GAIN.GAIN_LIST"] = None
    with (
        mock.patch.object(QInputDialog, "getInt", return_value=("1", True)),
        mock.patch.object(
            function.app.dReg.d["camera"].instance,
            "sendGain",
            return_value=None,
        ),
    ):
        function.setGain()


def test_setFilterNumber_1(function):
    function.setFilterNumber()


def test_setFilterNumber_2(function):
    function.app.dReg.d["filter"].instance.data["FILTER_SLOT.FILTER_SLOT_VALUE"] = 10
    function.app.dReg.d["filter"].instance.data["FILTER_NAME.FILTER_SLOT_NAME_0"] = "test"
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, False)):
        function.setFilterNumber()


def test_setFilterNumber_3(function):
    function.app.dReg.d["filter"].instance.data = {"FILTER_SLOT.FILTER_SLOT_VALUE": 10}
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, True)):
        function.setFilterNumber()


def test_setFilterName_1(function):
    function.app.dReg.d["filter"].instance.data["FILTER_SLOT.FILTER_SLOT_VALUE"] = None
    function.setFilterName()


def test_setFilterName_2(function):
    function.app.dReg.d["filter"].instance.data["FILTER_SLOT.FILTER_SLOT_VALUE"] = 1
    function.app.dReg.d["filter"].instance.data["FILTER_NAME.FILTER_SLOT_NAME_0"] = "test1"
    function.app.dReg.d["filter"].instance.data["FILTER_NAME.FILTER_SLOT_NAME_1"] = "test2"
    with mock.patch.object(QInputDialog, "getItem", return_value=(10, False)):
        function.setFilterName()


def test_setFilterName_3(function):
    function.app.dReg.d["filter"].instance.data["FILTER_SLOT.FILTER_SLOT_VALUE"] = 1
    function.app.dReg.d["filter"].instance.data["FILTER_NAME.FILTER_SLOT_NAME_0"] = "test1"
    function.app.dReg.d["filter"].instance.data["FILTER_NAME.FILTER_SLOT_NAME_1"] = "test2"
    with mock.patch.object(QInputDialog, "getItem", return_value=("test1", True)):
        function.setFilterName()


def test_setFilterName_4(function):
    function.app.dReg.d["filter"].instance.data = {
        "FILTER_SLOT.FILTER_SLOT_VALUE": 1,
        "FILTER_NAME.FILTER_SLOT_NAME_1": "test1",
        "FILTER_NAME.FILTER_SLOT_NAME_2": "test2",
    }
    with mock.patch.object(QInputDialog, "getItem", return_value=("test1", True)):
        function.setFilterName()


def test_setCoolerOn_1(function):
    with mock.patch.object(
        function.app.dReg.d["camera"].instance,
        "sendCoolerSwitch",
        return_value=None,
    ):
        function.setCoolerOn()


def test_setCoolerOff_1(function):
    with mock.patch.object(
        function.app.dReg.d["camera"].instance,
        "sendCoolerSwitch",
        return_value=None,
    ):
        function.setCoolerOff()


def test_updateCoverStatGui_1(function):
    function.app.dReg.d["cover"].instance.data["CAP_PARK.PARK"] = True
    function.updateCoverStatGui()


def test_updateCoverStatGui_2(function):
    function.app.dReg.d["cover"].instance.data["CAP_PARK.PARK"] = False
    function.updateCoverStatGui()


def test_updateCoverStatGui_3(function):
    function.app.dReg.d["cover"].instance.data["CAP_PARK.PARK"] = None
    function.updateCoverStatGui()


def test_updateLightPanelGui_1(function):
    function.app.dReg.d["lightPanel"].instance.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] = True
    function.updateLightPanelGui()


def test_updateLightPanelGui_2(function):
    function.app.dReg.d["lightPanel"].instance.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] = False
    function.updateLightPanelGui()


def test_updateLightPanelGui_3(function):
    function.app.dReg.d["lightPanel"].instance.data["FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON"] = None
    function.updateLightPanelGui()


def test_setCoverPark_1(function):
    with mock.patch.object(
        function.app.dReg.d["cover"].instance, "closeCover", return_value=False
    ):
        function.setCoverPark()


def test_setCoverPark_2(function):
    with mock.patch.object(
        function.app.dReg.d["cover"].instance, "closeCover", return_value=True
    ):
        function.setCoverPark()


def test_setCoverUnpark_1(function):
    with mock.patch.object(
        function.app.dReg.d["cover"].instance, "openCover", return_value=False
    ):
        function.setCoverUnpark()


def test_setCoverUnpark_2(function):
    with mock.patch.object(
        function.app.dReg.d["cover"].instance, "openCover", return_value=True
    ):
        function.setCoverUnpark()


def test_setCoverHalt_1(function):
    with mock.patch.object(
        function.app.dReg.d["cover"].instance, "haltCover", return_value=False
    ):
        function.setCoverHalt()


def test_setCoverHalt_2(function):
    with mock.patch.object(
        function.app.dReg.d["cover"].instance, "haltCover", return_value=True
    ):
        function.setCoverHalt()


def test_moveFocuserIn_1(function):
    with mock.patch.object(
        function.app.dReg.d["focuser"].instance,
        "move",
        return_value=False,
    ):
        function.moveFocuserIn()


def test_moveFocuserIn_2(function):
    with mock.patch.object(
        function.app.dReg.d["focuser"].instance,
        "move",
        return_value=True,
    ):
        function.moveFocuserIn()


def test_moveFocuserOut_1(function):
    with mock.patch.object(
        function.app.dReg.d["focuser"].instance,
        "move",
        return_value=False,
    ):
        function.moveFocuserOut()


def test_moveFocuserOut_2(function):
    with mock.patch.object(
        function.app.dReg.d["focuser"].instance,
        "move",
        return_value=True,
    ):
        function.moveFocuserOut()


def test_haltFocuser_1(function):
    with mock.patch.object(
        function.app.dReg.d["focuser"].instance,
        "halt",
        return_value=False,
    ):
        function.haltFocuser()


def test_haltFocuser_2(function):
    with mock.patch.object(
        function.app.dReg.d["focuser"].instance,
        "halt",
        return_value=True,
    ):
        function.haltFocuser()


def test_switchLightOn_1(function):
    with mock.patch.object(
        function.app.dReg.d["lightPanel"].instance, "lightOn", return_value=False
    ):
        function.switchLightPanelOn()


def test_switchLightOn_2(function):
    with mock.patch.object(
        function.app.dReg.d["lightPanel"].instance, "lightOn", return_value=True
    ):
        function.switchLightPanelOn()


def test_switchLightOff_1(function):
    with mock.patch.object(
        function.app.dReg.d["lightPanel"].instance, "lightOff", return_value=False
    ):
        function.switchLightPanelOff()


def test_switchLightOff_2(function):
    with mock.patch.object(
        function.app.dReg.d["lightPanel"].instance, "lightOff", return_value=True
    ):
        function.switchLightPanelOff()


def test_setLightPanelIntensity_2(function):
    function.app.dReg.d["cover"].instance.data[
        "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"
    ] = 10
    with mock.patch.object(QInputDialog, "getInt", return_value=(10, False)):
        function.setLightPanelIntensity()


def test_setLightPanelIntensity_3(function):
    function.app.dReg.d["cover"].instance.data[
        "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"
    ] = 10
    with (
        mock.patch.object(QInputDialog, "getInt", return_value=(10, True)),
        mock.patch.object(
            function.app.dReg.d["lightPanel"].instance,
            "lightIntensity",
            return_value=False,
        ),
    ):
        function.setLightPanelIntensity()


def test_setLightPanelIntensity_4(function):
    function.app.dReg.d["cover"].instance.data[
        "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"
    ] = 10
    with (
        mock.patch.object(QInputDialog, "getInt", return_value=(10, True)),
        mock.patch.object(
            function.app.dReg.d["lightPanel"].instance,
            "lightIntensity",
            return_value=True,
        ),
    ):
        function.setLightPanelIntensity()


def test_updateDomeGui_1(function):
    function.app.dReg.d["dome"].instance.data["DOME_MOTION.DOME_CW"] = True
    function.app.dReg.d["dome"].instance.data["DOME_MOTION.DOME_CCW"] = True
    function.updateDomeGui()


def test_updateDomeGui_2(function):
    function.app.dReg.d["dome"].instance.data["DOME_MOTION.DOME_CW"] = False
    function.app.dReg.d["dome"].instance.data["DOME_MOTION.DOME_CCW"] = False
    function.updateDomeGui()


def test_updateShutterStatGui_1(function):
    function.app.dReg.d["dome"].instance.data["DOME_SHUTTER.SHUTTER_OPEN"] = True
    function.app.dReg.d["dome"].instance.data["Status.Shutter"] = "test"
    function.updateShutterStatGui()

    assert function.ui.domeShutterStatusText.text() == "test"


def test_updateShutterStatGui_2(function):
    function.app.dReg.d["dome"].instance.data["DOME_SHUTTER.SHUTTER_OPEN"] = False
    function.app.dReg.d["dome"].instance.data["Status.Shutter"] = "test"
    function.updateShutterStatGui()

    assert function.ui.domeShutterStatusText.text() == "test"


def test_updateShutterStatGui_3(function):
    function.app.dReg.d["dome"].instance.data["DOME_SHUTTER.SHUTTER_OPEN"] = None
    function.app.dReg.d["dome"].instance.data["Status.Shutter"] = "test"
    function.updateShutterStatGui()

    assert function.ui.domeShutterStatusText.text() == "test"


def test_domeSlewCW_0(function):
    function.app.dReg.d["dome"].stat = False
    function.domeSlewCW()


def test_domeSlewCW_1(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(function.app.dReg.d["dome"].instance, "slewCW", return_value=False):
        function.domeSlewCW()


def test_domeSlewCW_2(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(function.app.dReg.d["dome"].instance, "slewCW", return_value=True):
        function.domeSlewCW()


def test_domeSlewCCW_0(function):
    function.app.dReg.d["dome"].stat = False
    function.domeSlewCCW()


def test_domeSlewCCW_1(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(
        function.app.dReg.d["dome"].instance, "slewCCW", return_value=False
    ):
        function.domeSlewCCW()


def test_domeSlewCCW_2(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(function.app.dReg.d["dome"].instance, "slewCCW", return_value=True):
        function.domeSlewCCW()


def test_domeAbortSlew_0(function):
    function.app.dReg.d["dome"].stat = False
    function.domeAbortSlew()


def test_domeAbortSlew_1(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(
        function.app.dReg.d["dome"].instance, "abortSlew", return_value=False
    ):
        function.domeAbortSlew()


def test_domeAbortSlew_2(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(
        function.app.dReg.d["dome"].instance, "abortSlew", return_value=True
    ):
        function.domeAbortSlew()


def test_domeOpenShutter_0(function):
    function.app.dReg.d["dome"].stat = False
    function.domeOpenShutter()


def test_domeOpenShutter_1(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(
        function.app.dReg.d["dome"].instance, "openShutter", return_value=False
    ):
        function.domeOpenShutter()


def test_domeOpenShutter_2(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(
        function.app.dReg.d["dome"].instance, "openShutter", return_value=True
    ):
        function.domeOpenShutter()


def test_domeCloseShutter_0(function):
    function.app.dReg.d["dome"].stat = False
    function.domeCloseShutter()


def test_domeCloseShutter_1(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(
        function.app.dReg.d["dome"].instance, "closeShutter", return_value=False
    ):
        function.domeCloseShutter()


def test_domeCloseShutter_2(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(
        function.app.dReg.d["dome"].instance, "closeShutter", return_value=True
    ):
        function.domeCloseShutter()


def test_domeMoveGameController_0(function):
    function.app.dReg.d["dome"].stat = False
    function.domeMoveGameController(128, 128)


def test_domeMoveGameController_1(function):
    function.app.dReg.d["dome"].stat = True
    with mock.patch.object(function, "domeAbortSlew"):
        function.domeMoveGameController(128, 128)


def test_domeMoveGameController_2(function):
    function.app.dReg.d["dome"].stat = True
    with (
        mock.patch.object(function, "domeSlewCCW"),
        mock.patch.object(function, "domeOpenShutter"),
    ):
        function.domeMoveGameController(0, 0)


def test_domeMoveGameController_3(function):
    function.app.dReg.d["dome"].stat = True
    with (
        mock.patch.object(function, "domeSlewCW"),
        mock.patch.object(function, "domeCloseShutter"),
    ):
        function.domeMoveGameController(255, 255)
