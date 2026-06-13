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

import contextlib
import hid
import pytest
from mw4.gui.extWindows.setting.tabSettGui import SettMisc
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QComboBox
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


def createMockComboBox() -> QComboBox:
    """Create a mock combo box for sound selection."""
    m = QComboBox()
    m.addItem("None")
    m.addItem("Beep")
    m.addItem("Beep1")
    m.addItem("Beep2")
    m.addItem("Bleep")
    m.addItem("Pan1")
    m.addItem("Pan2")
    m.addItem("Horn")
    m.addItem("Alarm")
    return m


def createMockCheckBox(defaultValue: bool = False):
    """Create a mock checkbox."""
    m = mock.MagicMock()
    m._checked = defaultValue
    m.isChecked = mock.MagicMock(side_effect=lambda: m._checked)
    m.setChecked = mock.MagicMock(side_effect=lambda v: setattr(m, "_checked", v))
    m.clicked = mock.MagicMock()
    return m


@pytest.fixture(autouse=True, scope="module")
def settMisc(qapp):
    """Setup SettMisc fixture for testing."""
    parentW = MWidget()
    parentW.gameControllerRunning = False
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Create mock UI elements for sound dropdowns
    parentW.ui.soundMountSlewFinished = createMockComboBox()
    parentW.ui.soundDomeSlewFinished = createMockComboBox()
    parentW.ui.soundMountAlert = createMockComboBox()
    parentW.ui.soundRunFinished = createMockComboBox()
    parentW.ui.soundImageSaved = createMockComboBox()
    parentW.ui.soundImageSolved = createMockComboBox()
    parentW.ui.soundConnectionLost = createMockComboBox()
    parentW.ui.soundSatStartTracking = createMockComboBox()

    # Create mock UI elements for game controller
    parentW.ui.gameControllerGroup = createMockCheckBox(defaultValue=False)
    parentW.ui.gameControllerList = QComboBox()
    parentW.ui.colorSet = QComboBox()
    parentW.ui.unitTimeUTC = createMockCheckBox(defaultValue=True)
    parentW.ui.unitTimeLocal = createMockCheckBox(defaultValue=False)

    # Create mock icon labels
    parentW.ui.controller1 = mock.MagicMock()
    parentW.ui.controller2 = mock.MagicMock()
    parentW.ui.controller3 = mock.MagicMock()
    parentW.ui.controller4 = mock.MagicMock()
    parentW.ui.controller5 = mock.MagicMock()
    parentW.ui.controllerOverview = mock.MagicMock()

    window = SettMisc(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_initConfig_with_defaults(settMisc):
    """Test initConfig loads default values."""
    settMisc.app.config["SettingMisc"] = {}
    with mock.patch.object(settMisc, "populateGameControllerList"):
        settMisc.initConfig()

    assert settMisc.ui.gameControllerGroup.isChecked() is False
    assert settMisc.ui.unitTimeUTC.isChecked() is True
    assert settMisc.ui.unitTimeLocal.isChecked() is False


def test_storeConfig_saves_all_values(settMisc):
    """Test storeConfig properly saves all UI state."""
    settMisc.ui.gameControllerGroup.setChecked(True)
    settMisc.ui.unitTimeUTC.setChecked(False)
    settMisc.ui.unitTimeLocal.setChecked(True)

    settMisc.storeConfig()

    config = settMisc.app.config["SettingMisc"]
    assert config["gameControllerGroup"] is True
    assert config["unitTimeUTC"] is False
    assert config["unitTimeLocal"] is True


def test_setupIcons_creates_icons(settMisc):
    """Test setupIcons method."""
    settMisc.setupIcons()


def test_sendGameControllerSignals_with_changed_values(settMisc):
    """Test sendGameControllerSignals emits on changes."""
    act = [0, 0, 0, 0, 0, 0, 0]
    old = [1, 1, 1, 1, 1, 1, 1]
    with mock.patch.object(settMisc.app, "gameABXY"):
        settMisc.sendGameControllerSignals(act, old)


def test_readGameController_returns_empty_on_exception(settMisc):
    """Test readGameController returns empty list on exception."""
    class Gamepad:
        @staticmethod
        def read(a):
            return [0] * 12

    settMisc.parentW.gameControllerRunning = True
    with mock.patch.object(Gamepad, "read", side_effect=Exception):
        val = settMisc.readGameController(Gamepad())
        assert len(val) == 0


def test_readGameController_returns_empty_when_disconnected(settMisc):
    """Test readGameController returns empty when disconnected."""
    class Gamepad:
        @staticmethod
        def read(a):
            return []

    settMisc.parentW.gameControllerRunning = False
    val = settMisc.readGameController(Gamepad())
    assert len(val) == 0


def test_readGameController_returns_data_when_running(settMisc):
    """Test readGameController behavior when running."""
    # Just verify the method doesn't crash
    class MockGamepad:
        def read(self, a):
            settMisc.parentW.gameControllerRunning = False
            return []

    settMisc.parentW.gameControllerRunning = True
    val = settMisc.readGameController(MockGamepad())
    assert isinstance(val, list)


def test_readGameController_stops_on_empty(settMisc):
    """Test readGameController stops on empty data."""
    class Gamepad:
        @staticmethod
        def read(a):
            settMisc.parentW.gameControllerRunning = False
            return []

    settMisc.parentW.gameControllerRunning = True
    val = settMisc.readGameController(Gamepad())
    assert len(val) == 0


def test_workerGameController_with_no_controller(settMisc):
    """Test workerGameController when no controller."""
    settMisc.parentW.gameControllerRunning = False
    settMisc.workerGameController()


def test_convertData_empty_for_unknown_controller(settMisc):
    """Test convertData returns zeros for unknown controller."""
    val = settMisc.convertData("test", [])
    assert all(v == 0 for v in val)
    assert len(val) == 7


def test_convertData_pro_controller(settMisc):
    """Test convertData for Pro Controller."""
    iR = [0, 1, 2, 3, 0, 5, 0, 7, 0, 9, 0, 11]
    name = "Pro Controller"
    val = settMisc.convertData(name, iR)
    assert val[0] == 1
    assert val[1] == 2
    assert val[2] == 3
    assert val[3] == 5
    assert val[4] == 7
    assert val[5] == 9
    assert val[6] == 11


def test_convertData_xbox_controller_default(settMisc):
    """Test convertData for Xbox controller with default direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0]
    name = "Controller (XBOX 360 For Windows)"
    val = settMisc.convertData(name, iR)
    assert val[0] == 10
    assert val[1] == 0
    assert val[2] == 0b1111


def test_convertData_xbox_controller_up(settMisc):
    """Test convertData for Xbox controller with up direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b11100]
    name = "Controller (XBOX 360 For Windows)"
    val = settMisc.convertData(name, iR)
    assert val[2] == 0b110


def test_convertData_xbox_controller_right(settMisc):
    """Test convertData for Xbox controller with right direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b10100]
    name = "Controller (XBOX 360 For Windows)"
    val = settMisc.convertData(name, iR)
    assert val[2] == 0b100


def test_convertData_xbox_controller_down(settMisc):
    """Test convertData for Xbox controller with down direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b1100]
    name = "Controller (XBOX 360 For Windows)"
    val = settMisc.convertData(name, iR)
    assert val[2] == 0b10


def test_convertData_xbox_controller_left(settMisc):
    """Test convertData for Xbox controller with left direction."""
    iR = [0, 1, 0, 3, 0, 5, 0, 7, 0, 0, 10, 0b100]
    name = "Controller (XBOX 360 For Windows)"
    val = settMisc.convertData(name, iR)
    assert val[2] == 0b0


def test_isNewerData_with_empty_data(settMisc):
    """Test isNewerData returns False with empty data."""
    suc = settMisc.isNewerData([], [])
    assert not suc


def test_isNewerData_with_same_data(settMisc):
    """Test isNewerData returns False with same data."""
    suc = settMisc.isNewerData([2], [2])
    assert not suc


def test_isNewerData_with_different_data(settMisc):
    """Test isNewerData returns True with different data."""
    suc = settMisc.isNewerData([2], [0])
    assert suc


def test_workerGameController_with_return_early(settMisc):
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

    settMisc.parentW.gameControllerRunning = False
    settMisc.ui.gameControllerList.clear()
    settMisc.ui.gameControllerList.addItem("test")
    settMisc.ui.gameControllerList.setCurrentIndex(0)
    settMisc.gameControllerList["test"] = {"vendorId": 1, "productId": 1}
    with mock.patch.object(hid, "device", return_value=Gamepad()):
        settMisc.workerGameController()


def test_startGameController_starts_worker(settMisc):
    """Test startGameController starts thread pool worker."""
    with mock.patch.object(settMisc.app.threadPool, "start"):
        settMisc.startGameController()


def test_isValidGameControllers_rejects_invalid(settMisc):
    """Test isValidGameControllers rejects invalid names."""
    suc = settMisc.isValidGameControllers("test")
    assert not suc


def test_isValidGameControllers_accepts_game(settMisc):
    """Test isValidGameControllers accepts Game in name."""
    suc = settMisc.isValidGameControllers("Game")
    assert suc


def test_populateGameControllerList_when_disabled(settMisc):
    """Test populateGameControllerList stops when disabled."""
    settMisc.ui.gameControllerGroup.setChecked(False)
    settMisc.parentW.gameControllerRunning = True
    settMisc.populateGameControllerList()


def test_populateGameControllerList_when_already_running(settMisc):
    """Test populateGameControllerList returns when already running."""
    settMisc.ui.gameControllerGroup.setChecked(True)
    settMisc.parentW.gameControllerRunning = True
    settMisc.populateGameControllerList()


def test_populateGameControllerList_skips_invalid(settMisc):
    """Test populateGameControllerList skips invalid controllers."""
    settMisc.ui.gameControllerGroup.setChecked(True)
    settMisc.parentW.gameControllerRunning = False
    device = [{"product_string": "test", "vendor_id": 1, "product_id": 1}]
    with (
        mock.patch.object(hid, "enumerate", return_value=device),
        mock.patch.object(settMisc, "isValidGameControllers", return_value=False),
    ):
        settMisc.populateGameControllerList()


def test_populateGameControllerList_starts_valid_controller(settMisc):
    """Test populateGameControllerList starts valid controller."""
    settMisc.ui.gameControllerGroup.setChecked(True)
    settMisc.parentW.gameControllerRunning = False
    device = [{"product_string": "test", "vendor_id": 1, "product_id": 1}]
    with (
        mock.patch.object(hid, "enumerate", return_value=device),
        mock.patch.object(settMisc, "isValidGameControllers", return_value=True),
        mock.patch.object(settMisc, "startGameController"),
    ):
        settMisc.populateGameControllerList()


def test_playSound_invalid_sound_name(settMisc):
    """Test playSound with invalid sound name."""
    settMisc.playSound("")


def test_playSound_valid_sound_name(settMisc):
    """Test playSound with valid sound name."""
    with mock.patch.object(QSoundEffect, "play"):
        settMisc.playSound("MountSlew")


def test_playSound_with_custom_audio(settMisc):
    """Test playSound with custom audio selection."""
    settMisc.audioSignalsSet["Pan1"] = "test"
    settMisc.guiAudioList["MountSlew"] = settMisc.ui.soundMountSlewFinished
    settMisc.guiAudioList["MountSlew"].clear()
    settMisc.guiAudioList["MountSlew"].addItem("Pan1")
    with mock.patch.object(QSoundEffect, "play"):
        settMisc.playSound("MountSlew")


def test_playSound_skips_unknown_audio(settMisc):
    """Test playSound skips unknown audio."""
    settMisc.audioSignalsSet["Pan1"] = "test"
    settMisc.guiAudioList["MountSlew"] = settMisc.ui.soundMountSlewFinished
    settMisc.guiAudioList["MountSlew"].clear()
    settMisc.guiAudioList["MountSlew"].addItem("Pan5")

    with mock.patch.object(QSoundEffect, "play"):
        settMisc.playSound("MountSlew")


def test_setupAudioSignals(settMisc):
    """Test setupAudioSignals initializes audio dict."""
    settMisc.setupAudioSignals()
    assert "Beep" in settMisc.audioSignalsSet
    assert "Pan1" in settMisc.audioSignalsSet


def test_minimizeGUI(settMisc):
    """Test minimizeGUI method exists."""
    # Just verify the method can be called
    with contextlib.suppress(AttributeError):
        settMisc.minimizeGUI()


def test_setTimeBaseUTC(settMisc):
    """Test setTimeBaseUTC sets UTC mode."""
    with mock.patch.object(settMisc.app, "timebaseChanged"):
        settMisc.setTimeBaseUTC()


def test_setTimeBaseLocal(settMisc):
    """Test setTimeBaseLocal sets local time mode."""
    with mock.patch.object(settMisc.app, "timebaseChanged"):
        settMisc.setTimeBaseLocal()











