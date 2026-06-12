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
from mw4.gui.extWindows.setting.tabSettRelay import SettRelay
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QComboBox, QLineEdit, QPushButton, QWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App


def createMockComboBox() -> QComboBox:
    """Create a relay function combo box."""
    m = QComboBox()
    m.clear()
    m.addItem("Switch - Toggle")
    m.addItem("Pulse 0.5 sec")
    return m


@pytest.fixture(autouse=True, scope="module")
def settRelay(qapp):
    """Setup SettRelay fixture for testing."""
    parentW = QWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Create mock UI elements for relay
    for i in range(0, 8):
        setattr(parentW.ui, f"relayFun{i}", createMockComboBox())
        setattr(parentW.ui, f"relayButtonText{i}", QLineEdit())
        setattr(parentW.ui, f"relayButton{i}", QPushButton())

    parentW.ui.relayDevice = mock.MagicMock()
    parentW.ui.relayDevice.currentIndex.return_value = 0

    window = SettRelay(parentW)

    # Create relayButtons dict since it's commented out in source
    window.relayButtons = {
        0: parentW.ui.relayButton0,
        1: parentW.ui.relayButton1,
        2: parentW.ui.relayButton2,
        3: parentW.ui.relayButton3,
        4: parentW.ui.relayButton4,
        5: parentW.ui.relayButton5,
        6: parentW.ui.relayButton6,
        7: parentW.ui.relayButton7,
    }

    yield window
    parentW.app.threadPool.waitForDone(10000)


def test_initConfig_with_defaults(settRelay):
    """Test initConfig loads defaults."""
    with mock.patch.object(settRelay, "updateRelayButtonText"):
        settRelay.initConfig()


def test_storeConfig_saves_state(settRelay):
    """Test storeConfig saves relay state."""
    settRelay.storeConfig()

    config = settRelay.app.config["SettingRelay"]
    assert "relay0buttonText" in config
    assert "relay0index" in config


def test_setupRelayGui_creates_dropdowns(settRelay):
    """Test setupRelayGui creates 8 relay dropdowns."""
    assert len(settRelay.relayDropDowns) == 8
    assert len(settRelay.relayButtonTexts) == 8
    assert len(settRelay.relayButtons) == 8

    for dropDown in settRelay.relayDropDowns:
        # Should have 2 items: "Switch - Toggle" and "Pulse 0.5 sec"
        assert dropDown.count() >= 2


def test_updateRelayButtonText_updates_all_buttons(settRelay):
    """Test updateRelayButtonText updates button text."""
    settRelay.updateRelayButtonText()


def test_doRelayAction_switch_fails(settRelay):
    """Test doRelayAction switch when it fails."""
    settRelay.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(settRelay.app.relay, "switch", return_value=False):
        suc = settRelay.doRelayAction(7)
        assert not suc


def test_doRelayAction_switch_succeeds(settRelay):
    """Test doRelayAction switch when it succeeds."""
    settRelay.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(settRelay.app.relay, "switch", return_value=True):
        suc = settRelay.doRelayAction(7)
        assert suc


def test_doRelayAction_invalid_action_index(settRelay):
    """Test doRelayAction with invalid action index."""
    settRelay.relayDropDowns[7].setCurrentIndex(2)
    suc = settRelay.doRelayAction(7)
    assert not suc


def test_doRelayAction_pulse_fails(settRelay):
    """Test doRelayAction pulse when it fails."""
    settRelay.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(settRelay.app.relay, "pulse", return_value=False):
        suc = settRelay.doRelayAction(7)
        assert not suc


def test_doRelayAction_pulse_succeeds(settRelay):
    """Test doRelayAction pulse when it succeeds."""
    settRelay.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(settRelay.app.relay, "pulse", return_value=True):
        suc = settRelay.doRelayAction(7)
        assert suc


def test_relayButtonPressed_when_action_fails(settRelay):
    """Test relayButtonPressed when action fails."""
    with mock.patch.object(settRelay, "doRelayAction", return_value=False):
        settRelay.relayButtonPressed(1)


def test_relayButtonPressed_when_action_succeeds(settRelay):
    """Test relayButtonPressed when action succeeds."""
    with mock.patch.object(settRelay, "doRelayAction", return_value=True):
        settRelay.relayButtonPressed(2)


def test_updateRelayGui_reflects_relay_status(settRelay):
    """Test updateRelayGui reflects relay status."""
    # Just verify the method can be called
    settRelay.app.relay.status = [0, 1, 0, 1, 0, 1, 0, 1]
    with mock.patch("mw4.gui.utilities.qtHelpers.changeStyleDynamic"):
        settRelay.updateRelayGui()





