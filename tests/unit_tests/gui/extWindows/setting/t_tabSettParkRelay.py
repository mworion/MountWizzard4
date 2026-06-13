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
from mw4.gui.extWindows.setting.tabSettParkRelay import SettParkPos
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QDoubleSpinBox, QLineEdit
from skyfield.api import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


def createMockLineEdit() -> QLineEdit:
    """Create a mock line edit for park position names."""
    m = QLineEdit()
    m.editingFinished = mock.MagicMock()
    return m


def createMockSpinBox() -> QDoubleSpinBox:
    """Create a mock spin box for altitude/azimuth."""
    m = QDoubleSpinBox()
    m.setValue(0)
    return m


def createMockButton():
    """Create a mock button."""
    return mock.MagicMock()


@pytest.fixture(autouse=True, scope="module")
def settParkPos(qapp):
    """Setup SettParkPos fixture for testing."""
    parentW = MWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Create mock UI elements for park positions
    for i in range(0, 10):
        setattr(parentW.ui, f"posButton{i}", createMockButton())
        setattr(parentW.ui, f"posSave{i}", createMockButton())
        setattr(parentW.ui, f"posText{i}", createMockLineEdit())
        setattr(parentW.ui, f"posAlt{i}", createMockSpinBox())
        setattr(parentW.ui, f"posAz{i}", createMockSpinBox())

    # Create other UI elements
    parentW.ui.parkMountAfterSlew = mock.MagicMock()
    parentW.ui.parkMountAfterSlew._checked = False
    parentW.ui.parkMountAfterSlew.isChecked = mock.MagicMock(
        side_effect=lambda: parentW.ui.parkMountAfterSlew._checked
    )
    parentW.ui.parkMountAfterSlew.setChecked = mock.MagicMock(
        side_effect=lambda v: setattr(parentW.ui.parkMountAfterSlew, "_checked", v)
    )

    window = SettParkPos(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_initConfig_with_default_config(settParkPos):
    """Test initConfig loads defaults when config empty."""
    settParkPos.app.config["SettingParkPos"] = {}
    settParkPos.initConfig()


def test_initConfig_with_custom_values(settParkPos):
    """Test initConfig loads custom config values."""
    config = settParkPos.app.config.get("SettingParkPos", {})
    if not config:
        settParkPos.app.config["SettingParkPos"] = {}
        config = settParkPos.app.config["SettingParkPos"]

    for i in range(0, 10):
        config[f"posText{i:1d}"] = str(i)
        config[f"posAlt{i:1d}"] = i
        config[f"posAz{i:1d}"] = i

    settParkPos.initConfig()

    assert settParkPos.ui.posText0.text() == "0"
    assert settParkPos.ui.posAlt0.value() == 0
    assert settParkPos.ui.posAz0.value() == 0
    assert settParkPos.ui.posText4.text() == "4"
    assert settParkPos.ui.posAlt4.value() == 4
    assert settParkPos.ui.posAz4.value() == 4


def test_storeConfig_saves_all_values(settParkPos):
    """Test storeConfig properly saves state."""
    settParkPos.storeConfig()

    config = settParkPos.app.config["SettingParkPos"]
    assert "posText0" in config
    assert "posAlt0" in config
    assert "posAz0" in config


def test_setupIcons_creates_icons(settParkPos):
    """Test setupIcons method."""
    settParkPos.setupIcons()


def test_setup_creates_park_position_widgets(settParkPos):
    """Test setup creates 10 park position widgets."""
    # Check all the required attributes exist
    for i in range(0, 10):
        assert i in settParkPos.posTexts
        assert i in settParkPos.posAlt
        assert i in settParkPos.posAz
        assert i in settParkPos.posSaveButtons


def test_parkAtPos_when_park_fails(settParkPos):
    """Test parkAtPos when park fails."""
    settParkPos.app.dReg["mount"].signals.slewed.connect(settParkPos.parkAtPos)
    with mock.patch.object(
        settParkPos.app.dReg["mount"].obsSite, "parkOnActualPosition", return_value=False
    ):
        settParkPos.parkAtPos()


def test_parkAtPos_when_park_succeeds(settParkPos):
    """Test parkAtPos when park succeeds."""
    settParkPos.app.dReg["mount"].signals.slewed.connect(settParkPos.parkAtPos)
    with mock.patch.object(
        settParkPos.app.dReg["mount"].obsSite, "parkOnActualPosition", return_value=True
    ):
        settParkPos.parkAtPos()


def test_slewToParkPos_when_set_target_fails(settParkPos):
    """Test slewToParkPos when setTargetAltAz fails."""
    with mock.patch.object(
        settParkPos.app.dReg["mount"].obsSite, "setTargetAltAz", return_value=False
    ):
        settParkPos.slewToParkPos(0)


def test_slewToParkPos_when_slewing_fails(settParkPos):
    """Test slewToParkPos when startSlewing fails."""
    with (
        mock.patch.object(
            settParkPos.app.dReg["mount"].obsSite, "setTargetAltAz", return_value=True
        ),
        mock.patch.object(
            settParkPos.app.dReg["mount"].obsSite, "startSlewing", return_value=False
        ),
    ):
        settParkPos.slewToParkPos(0)


def test_slewToParkPos_with_park_after_slew_enabled(settParkPos):
    """Test slewToParkPos with parkMountAfterSlew enabled."""
    settParkPos.ui.parkMountAfterSlew.setChecked(True)
    with (
        mock.patch.object(
            settParkPos.app.dReg["mount"].obsSite, "setTargetAltAz", return_value=True
        ),
        mock.patch.object(
            settParkPos.app.dReg["mount"].obsSite, "startSlewing", return_value=True
        ),
    ):
        settParkPos.slewToParkPos(0)


def test_slewToParkPos_with_park_after_slew_disabled(settParkPos):
    """Test slewToParkPos with parkMountAfterSlew disabled."""
    settParkPos.ui.parkMountAfterSlew.setChecked(False)
    with (
        mock.patch.object(
            settParkPos.app.dReg["mount"].obsSite, "setTargetAltAz", return_value=True
        ),
        mock.patch.object(
            settParkPos.app.dReg["mount"].obsSite, "startSlewing", return_value=True
        ),
    ):
        settParkPos.slewToParkPos(0)


def test_saveActualPosition_saves_current_position(settParkPos):
    """Test saveActualPosition saves current mount position."""
    settParkPos.app.dReg["mount"].obsSite.Alt = Angle(degrees=10)
    settParkPos.app.dReg["mount"].obsSite.Az = Angle(degrees=10)
    settParkPos.saveActualPosition(0)

    assert settParkPos.ui.posAlt0.value() == 10
    assert settParkPos.ui.posAz0.value() == 10


def test_updateParkPosButtonText_updates_button(settParkPos):
    """Test updateParkPosButtonText updates button text."""
    settParkPos.ui.posText0.setText("Test Position")
    settParkPos.updateParkPosButtonText()



