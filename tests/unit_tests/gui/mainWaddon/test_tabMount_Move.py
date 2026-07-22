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
from mw4.gui.mainWaddon.tabMount_Move import MountMove, StepSize
from mw4.gui.utilities.nativeQt.qtInputDialog import MWInputDialog
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QWidget
from skyfield.api import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = MountMove(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.initConfig()


def test_initConfig_2(function):
    del function.app.config["WindowMain"]
    function.initConfig()


def test_storeConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.storeConfig()


def test_setupGuiMount_1(function):
    function.setupGuiMount()


def test_stopMoveAll(function):
    with mock.patch.object(function.app.mount.obsSite, "stopMoveAll", return_value=True):
        function.stopMoveAll()


def test_countDuration_1(function):
    """Test startDurationTimer initialization."""
    function.ui.moveDuration.setCurrentIndex(1)
    with mock.patch.object(function, "onDurationTick"):
        function.startDurationTimer()
        assert function.durationTimer is not None


def test_countDuration_2(function):
    """Test startDurationTimer stops existing timer."""
    function.ui.moveDuration.setCurrentIndex(1)
    with mock.patch.object(function, "onDurationTick"):
        function.startDurationTimer()
        existing_timer = function.durationTimer
        assert existing_timer is not None
        function.startDurationTimer()
        # A new timer should be created
        assert function.durationTimer is not existing_timer


def test_onDurationTick_1(function):
    """Test onDurationTick with remaining countdown."""
    function.countdownRemaining = 5
    function.ui.stopMoveAll.setText("STOP")
    with mock.patch.object(function.ui.stopMoveAll, "setText"):
        function.onDurationTick()
        assert function.countdownRemaining == 4


def test_onDurationTick_2(function):
    """Test onDurationTick when countdown reaches zero."""
    function.countdownRemaining = 0
    with (
        mock.patch.object(function, "stopMoveAll"),
        mock.patch.object(function.ui.stopMoveAll, "setText"),
    ):
        function.durationTimer = mock.MagicMock()
        function.onDurationTick()
        assert function.ui.stopMoveAll.text() == "STOP"


def test_moveDuration_1(function):
    """Test moveDuration with index 1."""
    function.ui.moveDuration.setCurrentIndex(1)
    with mock.patch.object(function, "startDurationTimer"):
        function.moveDuration()
        function.startDurationTimer.assert_called_once()


def test_moveDuration_2(function):
    """Test moveDuration with index 2."""
    function.ui.moveDuration.setCurrentIndex(2)
    with mock.patch.object(function, "startDurationTimer"):
        function.moveDuration()


def test_moveDuration_3(function):
    """Test moveDuration with index 3."""
    function.ui.moveDuration.setCurrentIndex(3)
    with mock.patch.object(function, "startDurationTimer"):
        function.moveDuration()


def test_moveDuration_4(function):
    """Test moveDuration with index 4."""
    function.ui.moveDuration.setCurrentIndex(4)
    with mock.patch.object(function, "startDurationTimer"):
        function.moveDuration()


def test_moveDuration_5(function):
    """Test moveDuration with index 0 (no-op)."""
    function.ui.moveDuration.setCurrentIndex(0)
    with mock.patch.object(function, "startDurationTimer") as mock_timer:
        function.moveDuration()
        mock_timer.assert_not_called()


def test_moveRaDecHid_1(function):
    with mock.patch.object(function, "stopMoveAll"):
        function.moveRaDecHid(128, 128)


def test_moveRaDecHid_2(function):
    with mock.patch.object(function, "moveRaDec"):
        function.moveRaDecHid(0, 0)


def test_moveRaDecHid_3(function):
    with mock.patch.object(function, "moveRaDec"):
        function.moveRaDecHid(255, 255)


def test_moveRaDec_1(function):
    with mock.patch.object(function, "moveDuration"):
        function.moveRaDec("NE")


def test_moveRaDec_2(function):
    with mock.patch.object(function, "moveDuration"):
        function.moveRaDec("SW")


def test_moveRaDec_3(function):
    with mock.patch.object(function, "moveDuration"):
        function.moveRaDec("STOP")


def test_convertDirection_1(function):
    assert function.convertDirection([1, 0]) == "N"


def test_convertDirection_2(function):
    assert function.convertDirection([2, 2]) == "STOP"


def test_setSlewSpeed_1(function):
    function.setSlewSpeed("max")


def test_moveAltAzDefault(function):
    function.moveAltAzDefault()


def test_moveAltAzHid_1(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzHid(0)


def test_moveAltAzHid_2(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzHid(2)


def test_moveAltAzHid_3(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzHid(4)


def test_moveAltAzHid_4(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzHid(6)


def test_moveAltAzHid_5(function):
    with mock.patch.object(function, "moveAltAz"):
        function.moveAltAzHid(99)


def test_moveAltAz_3(function):
    function.targetAlt = Angle(degrees=10)
    function.targetAz = Angle(degrees=10)
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function.slewInterface, "slewTargetAltAz", return_value=True):
        function.moveAltAz("NE")


def test_stepsize_enum_value_degrees(function):
    """Test StepSize enum valueDegrees property."""
    assert StepSize.Step025.valueDegrees == 0.25
    assert StepSize.Step05.valueDegrees == 0.5
    assert StepSize.Step10.valueDegrees == 1.0
    assert StepSize.Step20.valueDegrees == 2.0
    assert StepSize.Step50.valueDegrees == 5.0
    assert StepSize.Step100.valueDegrees == 10.0
    assert StepSize.Step200.valueDegrees == 20.0


def test_stepsize_enum_display_text(function):
    """Test StepSize enum displayText property."""
    assert StepSize.Step025.displayText == "Stepsize 0.25°"
    assert StepSize.Step05.displayText == "Stepsize 0.5°"
    assert StepSize.Step10.displayText == "Stepsize 1.0°"
    assert StepSize.Step20.displayText == "Stepsize 2.0°"
    assert StepSize.Step50.displayText == "Stepsize 5.0°"
    assert StepSize.Step100.displayText == "Stepsize 10°"
    assert StepSize.Step200.displayText == "Stepsize 20°"


def test_direction_by_vector_reverse_lookup(function):
    """Test directionByVector reverse lookup dictionary."""
    assert function.directionByVector[(1, 0)] == "N"
    assert function.directionByVector[(0, 1)] == "E"
    assert function.directionByVector[(-1, 0)] == "S"
    assert function.directionByVector[(0, -1)] == "W"
    assert function.directionByVector[(1, 1)] == "NE"
    assert function.directionByVector[(1, -1)] == "NW"
    assert function.directionByVector[(-1, 1)] == "SE"
    assert function.directionByVector[(-1, -1)] == "SW"
    assert function.directionByVector[(0, 0)] == "STOP"


def test_setRA_1(function):
    with mock.patch.object(MWInputDialog, "getText", return_value=("", False)):
        function.setRA()


def test_setRA_2(function):
    with mock.patch.object(MWInputDialog, "getText", return_value=("", True)):
        function.setRA()


def test_setRA_3(function):
    with mock.patch.object(MWInputDialog, "getText", return_value=("12H", True)):
        function.setRA()


def test_setDEC_1(function):
    with mock.patch.object(MWInputDialog, "getText", return_value=("", False)):
        function.setDEC()


def test_setDEC_2(function):
    with mock.patch.object(MWInputDialog, "getText", return_value=("", True)):
        function.setDEC()


def test_setDEC_3(function):
    with mock.patch.object(MWInputDialog, "getText", return_value=("12", True)):
        function.setDEC()


def test_checkAltAzInputs_1(function):
    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=True):
        function.checkAltAzInputs()
        assert function.ui.moveAltAzAbsolute.isEnabled()


def test_checkAltAzInputs_2(function):
    with mock.patch.object(function.app.mount.obsSite, "setTargetAltAz", return_value=False):
        function.checkAltAzInputs()
        assert not function.ui.moveAltAzAbsolute.isEnabled()


def test_setAz_1(function):
    with mock.patch.object(function, "checkAltAzInputs"):
        function.setAz()


def test_setAlt_1(function):
    with mock.patch.object(function, "checkAltAzInputs"):
        function.setAlt()


def test_moveAltAzAbsolute_1(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    function.ui.moveCoordinateAlt.setText("50h")
    function.ui.moveCoordinateAz.setText("50h")
    with mock.patch.object(function.slewInterface, "slewTargetAltAz"):
        function.moveAltAzAbsolute()


def test_moveAltAzAbsolute_2(function):
    function.app.mount.obsSite.AltTarget = Angle(degrees=0)
    function.app.mount.obsSite.AzTarget = Angle(degrees=0)
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50h")
    with mock.patch.object(function.slewInterface, "slewTargetAltAz"):
        function.moveAltAzAbsolute()


def test_moveAltAzAbsolute_3(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50")
    with mock.patch.object(function.slewInterface, "slewTargetAltAz"):
        function.moveAltAzAbsolute()


def test_moveAltAzAbsolute_4(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText("50")
    function.ui.moveCoordinateAz.setText("50")
    with mock.patch.object(function.slewInterface, "slewTargetAltAz"):
        function.moveAltAzAbsolute()


def test_moveRaDecAbsolute_1(function):
    function.app.mount.obsSite.haJNowTarget = Angle(degrees=0)
    function.app.mount.obsSite.decJNowTarget = Angle(degrees=0)
    function.ui.moveCoordinateRa.setText("asd")
    function.ui.moveCoordinateDec.setText("asd")
    with mock.patch.object(function.slewInterface, "slewTargetRaDec"):
        function.moveRaDecAbsolute()


def test_moveRaDecAbsolute_2(function):
    function.app.mount.obsSite.haJNowTarget = Angle(degrees=0)
    function.app.mount.obsSite.decJNowTarget = Angle(degrees=0)
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("asd")
    with mock.patch.object(function.slewInterface, "slewTargetRaDec"):
        function.moveRaDecAbsolute()


def test_moveRaDecAbsolute_3(function):
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("30 30")
    with mock.patch.object(function.slewInterface, "slewTargetRaDec"):
        function.moveRaDecAbsolute()


def test_moveRaDecAbsolute_4(function):
    function.ui.moveCoordinateRa.setText("12H")
    function.ui.moveCoordinateDec.setText("30 30")
    with mock.patch.object(function.slewInterface, "slewTargetRaDec"):
        function.moveRaDecAbsolute()
