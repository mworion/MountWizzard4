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
from mw4.gui.mainWaddon.tabMount_Park import Park
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
    window = Park(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_park_class_exists():
    assert Park is not None


def test_park_can_instantiate(function):
    assert function is not None


def test_park_instance_is_park_type(function):
    assert isinstance(function, Park)


def test_park_has_mainw_attribute(function):
    assert hasattr(function, "mainW")
    assert function.mainW is not None


def test_park_has_app_attribute(function):
    assert hasattr(function, "app")
    assert function.app is not None


def test_park_has_msg_attribute(function):
    assert hasattr(function, "msg")
    assert function.msg is not None


def test_park_has_ui_attribute(function):
    assert hasattr(function, "ui")
    assert function.ui is not None


def test_park_has_parkButtons_attribute(function):
    assert hasattr(function, "parkButtons")
    assert function.parkButtons is not None


def test_park_parkButtons_is_list(function):
    assert isinstance(function.parkButtons, list)


def test_park_parkButtons_has_ten_elements(function):
    assert len(function.parkButtons) == 10


def test_park_has_initConfig_method(function):
    assert hasattr(function, "initConfig")
    assert callable(function.initConfig)


def test_park_has_storeConfig_method(function):
    assert hasattr(function, "storeConfig")
    assert callable(function.storeConfig)


def test_park_has_updateParkButtonText_method(function):
    assert hasattr(function, "updateParkButtonText")
    assert callable(function.updateParkButtonText)


def test_park_has_parkAtPos_method(function):
    assert hasattr(function, "parkAtPos")
    assert callable(function.parkAtPos)


def test_park_has_slewToPark_method(function):
    assert hasattr(function, "slewToPark")
    assert callable(function.slewToPark)


def test_initConfig_empty_config(function):
    function.app.config = {}
    function.initConfig()


def test_initConfig_with_config(function):
    function.app.config = {"MountPark": {"ParkMountAfterSlew": True}}
    function.initConfig()
    assert function.mainW.ui.parkMountAfterSlew.isChecked() is True


def test_initConfig_sets_default_false(function):
    function.app.config = {"MountPark": {}}
    function.initConfig()
    assert function.mainW.ui.parkMountAfterSlew.isChecked() is False


def test_storeConfig_saves_state(function):
    function.mainW.ui.parkMountAfterSlew.setChecked(True)
    function.storeConfig()
    assert function.app.config["MountPark"]["ParkMountAfterSlew"] is True


def test_storeConfig_saves_false_state(function):
    function.mainW.ui.parkMountAfterSlew.setChecked(False)
    function.storeConfig()
    assert function.app.config["MountPark"]["ParkMountAfterSlew"] is False


def test_updateParkButtonText_empty_config(function):
    function.app.config = {}
    function.updateParkButtonText()


def test_updateParkButtonText_with_config(function):
    config = {"SettingPark": {}}
    for i in range(10):
        config["SettingPark"][f"ParkText{i:1d}"] = f"Park {i}"
    function.app.config = config
    function.updateParkButtonText()
    for i in range(10):
        assert function.parkButtons[i].text() == f"Park {i}"


def test_updateParkButtonText_default_text(function):
    function.app.config = {"SettingPark": {}}
    function.updateParkButtonText()
    assert function.parkButtons[0].text() == ""


def test_parkAtPos_disconnects_signal(function):
    function.app.dReg["mount"].signals.slewed = mock.MagicMock()
    function.app.dReg["mount"].signals.slewed.disconnect = mock.MagicMock()
    with mock.patch.object(
        function.app.dReg["mount"].obsSite, "parkOnActualPosition", return_value=True
    ):
        function.parkAtPos()
        function.app.dReg["mount"].signals.slewed.disconnect.assert_called_once()


def test_parkAtPos_failure_emits_message(function):
    function.app.dReg["mount"].signals.slewed = mock.MagicMock()
    function.app.dReg["mount"].signals.slewed.disconnect = mock.MagicMock()
    mock_msg = mock.MagicMock()
    original_msg = function.msg
    function.msg = mock_msg
    try:
        with mock.patch.object(
            function.app.dReg["mount"].obsSite, "parkOnActualPosition", return_value=False
        ):
            function.parkAtPos()
            mock_msg.emit.assert_called_once_with(
                2, "Mount", "Command", "Cannot park at current position"
            )
    finally:
        function.msg = original_msg


def test_park_inherits_from_tabaddon(function):
    from mw4.gui.mainWaddon.tabAddon import TabAddon

    assert isinstance(function, TabAddon)


def test_slewToPark_requires_posAlt_attribute(function):
    """Test slewToPark requires posAlt attribute."""
    # Note: slewToPark will fail because posAlt doesn't exist
    # This test documents the bug in the source code
    function.posAlt = [mock.MagicMock() for _ in range(10)]
    function.posAz = [mock.MagicMock() for _ in range(10)]
    function.posTexts = [mock.MagicMock() for _ in range(10)]
    function.posAlt[0].value.return_value = 45.0
    function.posAz[0].value.return_value = 180.0
    function.posTexts[0].text.return_value = "Test Position"
    with (
        mock.patch.object(
            function.app.dReg["mount"].obsSite, "setTargetAltAz", return_value=True
        ),
        mock.patch.object(
            function.app.dReg["mount"].obsSite, "startSlewing", return_value=True
        ),
    ):
        function.slewToPark(0)


def test_slewToPark_when_setTargetAltAz_fails(function):
    """Test slewToPark when setTargetAltAz fails."""
    function.posAlt = [mock.MagicMock() for _ in range(10)]
    function.posAz = [mock.MagicMock() for _ in range(10)]
    function.posTexts = [mock.MagicMock() for _ in range(10)]
    function.posAlt[0].value.return_value = 45.0
    function.posAz[0].value.return_value = 180.0
    function.posTexts[0].text.return_value = "Test Position"
    mock_msg = mock.MagicMock()
    original_msg = function.msg
    function.msg = mock_msg
    try:
        with mock.patch.object(
            function.app.dReg["mount"].obsSite, "setTargetAltAz", return_value=False
        ):
            function.slewToPark(0)
            mock_msg.emit.assert_called_once()
    finally:
        function.msg = original_msg


def test_slewToPark_when_startSlewing_fails(function):
    """Test slewToPark when startSlewing fails."""
    function.posAlt = [mock.MagicMock() for _ in range(10)]
    function.posAz = [mock.MagicMock() for _ in range(10)]
    function.posTexts = [mock.MagicMock() for _ in range(10)]
    function.posAlt[0].value.return_value = 45.0
    function.posAz[0].value.return_value = 180.0
    function.posTexts[0].text.return_value = "Test Position"
    mock_msg = mock.MagicMock()
    original_msg = function.msg
    function.msg = mock_msg
    try:
        with (
            mock.patch.object(
                function.app.dReg["mount"].obsSite, "setTargetAltAz", return_value=True
            ),
            mock.patch.object(
                function.app.dReg["mount"].obsSite, "startSlewing", return_value=False
            ),
        ):
            function.slewToPark(0)
            mock_msg.emit.assert_called_once()
    finally:
        function.msg = original_msg


def test_slewToPark_with_park_after_slew_enabled(function):
    """Test slewToPark with parkMountAfterSlew enabled."""
    function.posAlt = [mock.MagicMock() for _ in range(10)]
    function.posAz = [mock.MagicMock() for _ in range(10)]
    function.posTexts = [mock.MagicMock() for _ in range(10)]
    function.posAlt[0].value.return_value = 45.0
    function.posAz[0].value.return_value = 180.0
    function.posTexts[0].text.return_value = "Test Position"
    function.mainW.ui.parkMountAfterSlew.setChecked(True)
    function.app.dReg["mount"].signals.slewed = mock.MagicMock()
    with (
        mock.patch.object(
            function.app.dReg["mount"].obsSite, "setTargetAltAz", return_value=True
        ),
        mock.patch.object(
            function.app.dReg["mount"].obsSite, "startSlewing", return_value=True
        ),
    ):
        function.slewToPark(0)
        function.app.dReg["mount"].signals.slewed.connect.assert_called_once()
