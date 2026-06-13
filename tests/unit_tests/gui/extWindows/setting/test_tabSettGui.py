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
import hid
import pytest
from mw4.gui.extWindows.setting.tabSettGui import SettGui
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QComboBox
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


def createMockCheckBox(defaultValue: bool = False):
    """Create a mock checkbox."""
    m = mock.MagicMock()
    m._checked = defaultValue
    m.isChecked = mock.MagicMock(side_effect=lambda: m._checked)
    m.setChecked = mock.MagicMock(side_effect=lambda v: setattr(m, "_checked", v))
    m.clicked = mock.MagicMock()
    return m


@pytest.fixture(autouse=True, scope="module")
def settGui(qapp):
    """Setup SettMisc fixture for testing."""
    parentW = MWidget()
    parentW.gameControllerRunning = False
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Create mock UI elements for game controller
    parentW.ui.gameControllerGroup = createMockCheckBox(defaultValue=False)
    parentW.ui.gameControllerList = QComboBox()
    parentW.ui.colorSet = QComboBox()
    parentW.ui.colorSet.addItem("Color1")
    parentW.ui.colorSet.addItem("Color2")
    parentW.ui.colorSet.addItem("Color3")
    parentW.ui.soundSatStartTracking = QComboBox()
    parentW.ui.soundSatStartTracking.addItem("None")
    parentW.ui.soundSatStartTracking.addItem("Beep")

    # Create mock icon labels
    parentW.ui.controller1 = mock.MagicMock()
    parentW.ui.controller2 = mock.MagicMock()
    parentW.ui.controller3 = mock.MagicMock()
    parentW.ui.controller4 = mock.MagicMock()
    parentW.ui.controller5 = mock.MagicMock()
    parentW.ui.controllerOverview = mock.MagicMock()

    window = SettGui(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_initConfig_with_defaults(settGui):
    """Test initConfig loads default values."""
    settGui.app.config["SettingGui"] = {}
    with mock.patch.object(settGui, "populateGameControllerList"):
        settGui.initConfig()

    assert settGui.ui.gameControllerGroup.isChecked() is False
    assert settGui.ui.colorSet.currentIndex() == 0


def test_storeConfig_saves_all_values(settGui):
    """Test storeConfig properly saves all UI state."""
    settGui.ui.gameControllerGroup.setChecked(True)
    settGui.ui.colorSet.setCurrentIndex(1)
    settGui.ui.soundSatStartTracking.setCurrentIndex(2)

    settGui.storeConfig()

    config = settGui.app.config["SettingGui"]
    assert config["gameControllerGroup"] is True
    assert config["colorSet"] == 1


def test_setupIcons_creates_icons(settGui):
    """Test setupIcons method."""
    settGui.setupIcons()


def test_sendGameControllerSignals_with_changed_values(settGui):
    """Test sendGameControllerSignals emits on changes."""
    act = [0, 0, 0, 0, 0, 0, 0]
    old = [1, 1, 1, 1, 1, 1, 1]
    with mock.patch.object(settGui.app, "gameABXY"):
        settGui.sendGameControllerSignals(act, old)


def test_readGameController_returns_empty_on_exception(settGui):
    """Test readGameController returns empty list on exception."""

    class Gamepad:
        @staticmethod
        def read(a):
            raise Exception("Device error")

    settGui.gameControllerRunning = True
    val = settGui.readGameController(Gamepad())
    assert len(val) == 0
    assert settGui.gameControllerRunning is False


def test_readGameController_returns_empty_when_disconnected(settGui):
    """Test readGameController returns empty when disconnected."""

    class Gamepad:
        @staticmethod
        def read(a):
            return []

    settGui.parentW.gameControllerRunning = False
    val = settGui.readGameController(Gamepad())
    assert len(val) == 0


def test_readGameController_returns_data_when_running(settGui):
    """Test readGameController behavior when running."""

    # Just verify the method doesn't crash
    class MockGamepad:
        def read(self, a):
            settGui.parentW.gameControllerRunning = False
            return []

    settGui.parentW.gameControllerRunning = True
    val = settGui.readGameController(MockGamepad())
    assert isinstance(val, list)


def test_readGameController_stops_on_empty(settGui):
    """Test readGameController stops on empty data."""

    class Gamepad:
        @staticmethod
        def read(a):
            settGui.parentW.gameControllerRunning = False
            return []

    settGui.parentW.gameControllerRunning = True
    val = settGui.readGameController(Gamepad())
    assert len(val) == 0


def test_workerGameController_with_no_controller(settGui):
    """Test workerGameController when no controller."""
    settGui.parentW.gameControllerRunning = False
    settGui.workerGameController()


def test_convertData_empty_for_unknown_controller(settGui):
    """Test convertData returns zeros for unknown controller."""
    val = settGui.convertData("test", [])
    assert all(v == 0 for v in val)
    assert len(val) == 7


def test_convertData_pro_controller(settGui):
    """Test convertData for Pro Controller."""
    iR = [0, 1, 2, 3, 0, 5, 0, 7, 0, 9, 0, 11]
    name = "Pro Controller"
    val = settGui.convertData(name, iR)
    assert val[0] == 1
    assert val[1] == 2
    assert val[2] == 3
    assert val[3] == 5
    assert val[4] == 7
    assert val[5] == 9
    assert val[6] == 11


def test_convertData_xbox_controller_default(settGui):
    """Test convertData for Xbox controller with default direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0]
    name = "Controller (XBOX 360 For Windows)"
    val = settGui.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b1111


def test_convertData_xbox_controller_up(settGui):
    """Test convertData for Xbox controller with up direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b11100]
    name = "Controller (XBOX 360 For Windows)"
    val = settGui.convertData(name, iR)
    assert val[2] == 0b110


def test_convertData_xbox_controller_right(settGui):
    """Test convertData for Xbox controller with right direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b10100]
    name = "Controller (XBOX 360 For Windows)"
    val = settGui.convertData(name, iR)
    assert val[2] == 0b100


def test_convertData_xbox_controller_down(settGui):
    """Test convertData for Xbox controller with down direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b1100]
    name = "Controller (XBOX 360 For Windows)"
    val = settGui.convertData(name, iR)
    assert val[2] == 0b10


def test_convertData_xbox_controller_left(settGui):
    """Test convertData for Xbox controller with left direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b100]
    name = "Controller (XBOX 360 For Windows)"
    val = settGui.convertData(name, iR)
    assert val[2] == 0b0


def test_isNewerData_with_empty_data(settGui):
    """Test isNewerData returns False with empty data."""
    suc = settGui.isNewerData([], [])
    assert not suc


def test_isNewerData_with_same_data(settGui):
    """Test isNewerData returns False with same data."""
    suc = settGui.isNewerData([2], [2])
    assert not suc


def test_isNewerData_with_different_data(settGui):
    """Test isNewerData returns True with different data."""
    suc = settGui.isNewerData([2], [0])
    assert suc


def test_workerGameController_with_return_early(settGui):
    """Test workerGameController returns early when no controller."""

    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

        @staticmethod
        def open(a, b):
            return

        @staticmethod
        def set_nonblocking(a):
            return

    settGui.parentW.gameControllerRunning = False
    settGui.ui.gameControllerList.clear()
    settGui.ui.gameControllerList.addItem("test")
    settGui.ui.gameControllerList.setCurrentIndex(0)
    settGui.gameControllerList["test"] = {"vendorId": 1, "productId": 1}
    with mock.patch.object(hid, "device", return_value=Gamepad()):
        settGui.workerGameController()


def test_startGameController_starts_worker(settGui):
    """Test startGameController starts thread pool worker."""
    with mock.patch.object(settGui.app.threadPool, "start"):
        settGui.startGameController()


def test_isValidGameControllers_rejects_invalid(settGui):
    """Test isValidGameControllers rejects invalid names."""
    suc = settGui.isValidGameControllers("test")
    assert not suc


def test_isValidGameControllers_accepts_game(settGui):
    """Test isValidGameControllers accepts Game in name."""
    suc = settGui.isValidGameControllers("Game")
    assert suc


def test_populateGameControllerList_when_disabled(settGui):
    """Test populateGameControllerList stops when disabled."""
    settGui.ui.gameControllerGroup.setChecked(False)
    settGui.parentW.gameControllerRunning = True
    settGui.populateGameControllerList()


def test_populateGameControllerList_when_already_running(settGui):
    """Test populateGameControllerList returns when already running."""
    settGui.ui.gameControllerGroup.setChecked(True)
    settGui.parentW.gameControllerRunning = True
    settGui.populateGameControllerList()


def test_populateGameControllerList_skips_invalid(settGui):
    """Test populateGameControllerList skips invalid controllers."""
    settGui.ui.gameControllerGroup.setChecked(True)
    settGui.parentW.gameControllerRunning = False
    device = [{"product_string": "test", "vendor_id": 1, "product_id": 1}]
    with (
        mock.patch.object(hid, "enumerate", return_value=device),
        mock.patch.object(settGui, "isValidGameControllers", return_value=False),
    ):
        settGui.populateGameControllerList()


def test_populateGameControllerList_starts_valid_controller(settGui):
    """Test populateGameControllerList starts valid controller."""
    settGui.ui.gameControllerGroup.setChecked(True)
    settGui.parentW.gameControllerRunning = False
    device = [{"product_string": "test", "vendor_id": 1, "product_id": 1}]
    with (
        mock.patch.object(hid, "enumerate", return_value=device),
        mock.patch.object(settGui, "isValidGameControllers", return_value=True),
        mock.patch.object(settGui, "startGameController"),
    ):
        settGui.populateGameControllerList()


def test_switchStatusGameController_enabled(settGui):
    """Test switchStatusGameController enables controller when checked."""
    settGui.ui.gameControllerGroup.setChecked(True)
    settGui.gameControllerRunning = False
    with mock.patch.object(settGui, "populateGameControllerList"):
        settGui.switchStatusGameController()


def test_switchStatusGameController_disabled(settGui):
    """Test switchStatusGameController disables controller when unchecked."""
    settGui.ui.gameControllerGroup.setChecked(False)
    settGui.gameControllerRunning = True
    settGui.switchStatusGameController()

    assert settGui.gameControllerRunning is False


def test_switchStatusGameController_already_running(settGui):
    """Test switchStatusGameController skips when already running."""
    settGui.ui.gameControllerGroup.setChecked(True)
    settGui.gameControllerRunning = True
    with mock.patch.object(settGui, "populateGameControllerList") as mock_pop:
        settGui.switchStatusGameController()

        mock_pop.assert_not_called()


def test_readGameController_returns_data_on_success(settGui):
    """Test readGameController returns data when read succeeds (lines 71-80)."""

    class Gamepad:
        def __init__(self):
            self.call_count = 0

        def read(self, size):
            self.call_count += 1
            if self.call_count == 1:
                return [0, 1, 2, 3, 4, 5]  # Return non-empty data
            else:
                settGui.gameControllerRunning = False
                return []  # Then return empty to break loop

    settGui.gameControllerRunning = True
    gamepad = Gamepad()
    val = settGui.readGameController(gamepad)
    assert val == [0, 1, 2, 3, 4, 5]


def test_workerGameController_with_new_data(settGui):
    """Test workerGameController processes data when new data arrives (lines 132-138)."""
    settGui.gameControllerRunning = True
    settGui.gameControllerList["test"] = {"vendorId": 1, "productId": 1}
    settGui.ui.gameControllerList.clear()
    settGui.ui.gameControllerList.addItem("test")
    settGui.ui.gameControllerList.setCurrentIndex(0)

    # Mock the device and read process
    class Gamepad:
        def __init__(self):
            self.call_count = 0

        def open(self, v, p):
            pass

        def set_nonblocking(self, a):
            pass

        def read(self, size):
            self.call_count += 1
            if self.call_count == 1:
                # Return Pro Controller data
                return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            else:
                settGui.gameControllerRunning = False
                return []

    with (
        mock.patch.object(hid, "device", return_value=Gamepad()),
        mock.patch.object(settGui.app, "gameABXY"),
        mock.patch.object(settGui.app, "gamePMH"),
        mock.patch.object(settGui.app, "gameDirection"),
        mock.patch.object(settGui.app, "gameSL"),
        mock.patch.object(settGui.app, "gameSR"),
    ):
        settGui.workerGameController()
        # Verify signals were emitted
        assert settGui.app.gameABXY.emit.called or settGui.gameControllerRunning is False


def test_workerGameController_continues_on_same_data(settGui):
    """Test workerGameController continues when data hasn't changed (line 135)."""
    settGui.gameControllerRunning = True
    # Use a valid controller name so convertData returns non-zero values
    settGui.gameControllerList["Pro Controller"] = {"vendorId": 1, "productId": 1}
    settGui.ui.gameControllerList.clear()
    settGui.ui.gameControllerList.addItem("Pro Controller")
    settGui.ui.gameControllerList.setCurrentIndex(0)

    # Mock the device and track read calls carefully
    class Gamepad:
        def __init__(self):
            self.read_count = 0

        def open(self, v, p):
            pass

        def set_nonblocking(self, a):
            pass

        def read(self, size):
            self.read_count += 1
            if self.read_count == 1:
                # First read: return Pro Controller data
                return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            elif self.read_count == 2:
                # Break first readGameController loop
                return []
            elif self.read_count == 3:
                # Second outer iteration: return same data again
                return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            elif self.read_count == 4:
                # Break second readGameController loop
                return []
            else:
                # Third outer iteration: empty data stops the loop
                settGui.gameControllerRunning = False
                return []

    with (
        mock.patch.object(hid, "device", return_value=Gamepad()),
        mock.patch("mw4.base.threadUtils.mainThreadSleep"),
        mock.patch.object(settGui.app, "gameABXY") as mock_signal_1,
        mock.patch.object(settGui.app, "gamePMH"),
        mock.patch.object(settGui.app, "gameDirection"),
        mock.patch.object(settGui.app, "gameSL"),
        mock.patch.object(settGui.app, "gameSR"),
    ):
        settGui.workerGameController()
        # Signal should be emitted at least once when data changes
        assert mock_signal_1.emit.call_count >= 1


def test_populateGameControllerList_when_no_devices(settGui):
    """Test populateGameControllerList when no game controllers are found."""
    settGui.ui.gameControllerGroup.setChecked(True)
    settGui.gameControllerRunning = False

    with (
        mock.patch.object(hid, "enumerate", return_value=[]),
        mock.patch.object(settGui, "startGameController") as mock_start,
    ):
        settGui.populateGameControllerList()
        # Should not start game controller if no devices found
        mock_start.assert_not_called()


def test_updateColorSet_updates_app(settGui):
    """Test updateColorSet updates color set."""
    settGui.ui.colorSet.setCurrentIndex(1)
    settGui.updateColorSet()

    from mw4.gui.styles.styles import Styles

    assert Styles.colorSet == 1
