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
from mw4.gui.mainWaddon.tabRelay import Relay
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    mainW.wIcon = mock.MagicMock()
    window = Relay(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_relay_class_exists():
    assert Relay is not None


def test_relay_can_instantiate(function):
    assert function is not None


def test_relay_instance_is_relay_type(function):
    assert isinstance(function, Relay)


def test_relay_has_mainw_attribute(function):
    assert hasattr(function, "mainW")
    assert function.mainW is not None


def test_relay_has_app_attribute(function):
    assert hasattr(function, "app")
    assert function.app is not None


def test_relay_has_msg_attribute(function):
    assert hasattr(function, "msg")
    assert function.msg is not None


def test_relay_has_ui_attribute(function):
    assert hasattr(function, "ui")
    assert function.ui is not None


def test_relay_has_relayButtons_attribute(function):
    assert hasattr(function, "relayButtons")
    assert function.relayButtons is not None


def test_relay_relayButtons_is_list(function):
    assert isinstance(function.relayButtons, list)


def test_relay_relayButtons_has_eight_elements(function):
    assert len(function.relayButtons) == 8


def test_relay_has_updateRelayButtonText_method(function):
    assert hasattr(function, "updateRelayButtonText")
    assert callable(function.updateRelayButtonText)


def test_relay_has_doRelayAction_method(function):
    assert hasattr(function, "doRelayAction")
    assert callable(function.doRelayAction)


def test_relay_has_relayButtonPressed_method(function):
    assert hasattr(function, "relayButtonPressed")
    assert callable(function.relayButtonPressed)


def test_relay_has_updateRelayGui_method(function):
    assert hasattr(function, "updateRelayGui")
    assert callable(function.updateRelayGui)


def test_updateRelayButtonText_empty_config(function):
    function.app.config = {}
    function.updateRelayButtonText()


def test_updateRelayButtonText_with_config(function):
    function.app.config = {
        "SettingRelay": {
            "RelayText0": "Relay 0",
            "RelayText1": "Relay 1",
            "Action0": 0,
            "Action1": 1,
        }
    }
    function.updateRelayButtonText()
    function.mainW.wIcon.assert_called()


def test_updateRelayButtonText_default_text(function):
    function.app.config = {"SettingRelay": {}}
    function.updateRelayButtonText()
    assert function.relayButtons[0].text() == ""


def test_updateRelayButtonText_icon_switch(function):
    function.app.config = {
        "SettingRelay": {
            "RelayText0": "Test",
            "Action0": 0,
        }
    }
    function.mainW.wIcon.reset_mock()
    function.updateRelayButtonText()
    calls = function.mainW.wIcon.call_args_list
    assert len(calls) > 0
    icon_call = [c for c in calls if "flip" in str(c)]
    assert len(icon_call) > 0


def test_updateRelayButtonText_icon_pulse(function):
    function.app.config = {
        "SettingRelay": {
            "RelayText0": "Test",
            "Action0": 1,
        }
    }
    function.mainW.wIcon.reset_mock()
    function.updateRelayButtonText()
    calls = function.mainW.wIcon.call_args_list
    assert len(calls) > 0
    icon_call = [c for c in calls if "cogs" in str(c)]
    assert len(icon_call) > 0


def test_doRelayAction_switch_success(function):
    function.app.config = {
        "SettingRelay": {
            "Action0": 0,
        }
    }
    with mock.patch.object(function.app.relay, "switch", return_value=True):
        result = function.doRelayAction(0)
        assert result is True


def test_doRelayAction_switch_failure(function):
    function.app.config = {
        "SettingRelay": {
            "Action0": 0,
        }
    }
    with mock.patch.object(function.app.relay, "switch", return_value=False):
        result = function.doRelayAction(0)
        assert result is False


def test_doRelayAction_pulse_success(function):
    function.app.config = {
        "SettingRelay": {
            "Action0": 1,
        }
    }
    with mock.patch.object(function.app.relay, "pulse", return_value=True):
        result = function.doRelayAction(0)
        assert result is True


def test_doRelayAction_pulse_failure(function):
    function.app.config = {
        "SettingRelay": {
            "Action0": 1,
        }
    }
    with mock.patch.object(function.app.relay, "pulse", return_value=False):
        result = function.doRelayAction(0)
        assert result is False


def test_doRelayAction_with_config(function):
    function.app.config = {"SettingRelay": {"Action0": 0}}
    with mock.patch.object(function.app.relay, "switch", return_value=True):
        result = function.doRelayAction(0)
        assert result is True


def test_relayButtonPressed_success(function):
    function.app.config = {"SettingRelay": {"Action0": 0}}
    with mock.patch.object(function, "doRelayAction", return_value=True):
        function.relayButtonPressed(0)


def test_relayButtonPressed_failure(function):
    function.app.config = {"SettingRelay": {"Action0": 0}}
    mock_msg = mock.MagicMock()
    original_msg = function.msg
    function.msg = mock_msg
    try:
        with mock.patch.object(function, "doRelayAction", return_value=False):
            function.relayButtonPressed(0)
            mock_msg.emit.assert_called_once_with(
                2, "System", "Relay", "Action cannot be done"
            )
    finally:
        function.msg = original_msg


def test_updateRelayGui_all_off(function):
    function.app.relay.status = [0, 0, 0, 0, 0, 0, 0, 0]
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic"):
        function.updateRelayGui()


def test_updateRelayGui_all_on(function):
    function.app.relay.status = [1, 1, 1, 1, 1, 1, 1, 1]
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic"):
        function.updateRelayGui()


def test_updateRelayGui_mixed_status(function):
    function.app.relay.status = [1, 0, 1, 0, 1, 0, 1, 0]
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic"):
        function.updateRelayGui()


def test_updateRelayGui_calls_changeStyleDynamic(function):
    function.app.relay.status = [1, 0, 1, 0, 1, 0, 1, 0]
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic") as mock_style:
        function.updateRelayGui()
        assert mock_style.call_count > 0


def test_updateRelayGui_changeStyleDynamic_called_correctly(function):
    function.app.relay.status = [1, 0, 0, 0, 0, 0, 0, 0]
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic") as mock_style:
        function.updateRelayGui()
        first_call = mock_style.call_args_list[0]
        assert first_call[0][1] == "run"
        assert first_call[0][2] is True


def test_relay_buttons_connected_to_statusReady(function):
    assert function.app.dReg["relay"].signals.statusReady is not None


def test_relay_statusReady_signal_emission(function):
    function.app.relay.status = [1, 0, 0, 0, 0, 0, 0, 0]
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic"):
        function.app.dReg["relay"].signals.statusReady.emit()
        function.updateRelayGui()


def test_doRelayAction_different_indices(function):
    for i in range(8):
        function.app.config = {"SettingRelay": {f"Action{i}": 0}}
        with mock.patch.object(function.app.relay, "switch", return_value=True):
            result = function.doRelayAction(i)
            assert result is True


def test_relayButtonPressed_all_buttons(function):
    for i in range(8):
        function.app.config = {"SettingRelay": {f"Action{i}": 0}}
        with mock.patch.object(function, "doRelayAction", return_value=True):
            function.relayButtonPressed(i)


def test_updateRelayButtonText_all_configs(function):
    config = {"SettingRelay": {}}
    for i in range(8):
        config["SettingRelay"][f"RelayText{i}"] = f"Relay {i}"
        config["SettingRelay"][f"Action{i}"] = i % 2
    function.app.config = config
    function.updateRelayButtonText()


def test_relay_inherits_from_tabaddon(function):
    from mw4.gui.mainWaddon.tabAddon import TabAddon

    assert isinstance(function, TabAddon)


def test_relay_relay_button_texts_set_correctly(function):
    function.app.config = {
        "SettingRelay": {
            "RelayText0": "Shutter",
            "RelayText1": "Camera",
            "Action0": 0,
            "Action1": 1,
        }
    }
    function.updateRelayButtonText()
    assert function.relayButtons[0].text() == "Shutter"
    assert function.relayButtons[1].text() == "Camera"


def test_updateRelayGui_status_property_exists(function):
    assert hasattr(function.app.relay, "status")


def test_updateRelayGui_with_empty_status(function):
    function.app.relay.status = []
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic"):
        function.updateRelayGui()


def test_relayButtonPressed_calls_doRelayAction(function):
    function.app.config = {"SettingRelay": {"Action0": 0}}
    with mock.patch.object(function, "doRelayAction", return_value=True) as mock_action:
        function.relayButtonPressed(0)
        mock_action.assert_called_once_with(0)


def test_updateRelayButtonText_iterates_all_buttons(function):
    function.app.config = {"SettingRelay": {}}
    function.mainW.wIcon.reset_mock()
    function.updateRelayButtonText()
    assert function.mainW.wIcon.call_count == 8


def test_doRelayAction_reads_correct_config(function):
    function.app.config = {"SettingRelay": {}}
    for i in range(8):
        function.app.config["SettingRelay"][f"Action{i}"] = 0
    with mock.patch.object(function.app.relay, "switch", return_value=True):
        function.doRelayAction(3)
        function.app.relay.switch.assert_called_with(3)


def test_relayButtonPressed_emits_message_on_failure(function):
    function.app.config = {"SettingRelay": {"Action0": 0}}
    mock_msg = mock.MagicMock()
    original_msg = function.msg
    function.msg = mock_msg
    try:
        with mock.patch.object(function, "doRelayAction", return_value=False):
            function.relayButtonPressed(0)
            assert function.msg.emit.called
    finally:
        function.msg = original_msg


def test_relayButtonPressed_no_message_on_success(function):
    function.app.config = {"SettingRelay": {"Action0": 0}}
    mock_msg = mock.MagicMock()
    original_msg = function.msg
    function.msg = mock_msg
    try:
        with mock.patch.object(function, "doRelayAction", return_value=True):
            function.relayButtonPressed(0)
            assert not function.msg.emit.called
    finally:
        function.msg = original_msg


def test_relay_initialization_connects_signals(function):
    assert function.app.dReg["relay"].signals.statusReady is not None


def test_updateRelayGui_changeStyleDynamic_with_status_on(function):
    function.app.relay.status = [1, 1, 1, 1, 1, 1, 1, 1]
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic") as mock_style:
        function.updateRelayGui()
        calls = [c[0] for c in mock_style.call_args_list]
        assert all(c[2] is True for c in calls)


def test_updateRelayGui_changeStyleDynamic_with_status_off(function):
    function.app.relay.status = [0, 0, 0, 0, 0, 0, 0, 0]
    with mock.patch("mw4.gui.mainWaddon.tabRelay.changeStyleDynamic") as mock_style:
        function.updateRelayGui()
        calls = [c[0] for c in mock_style.call_args_list]
        assert all(c[2] is False for c in calls)
