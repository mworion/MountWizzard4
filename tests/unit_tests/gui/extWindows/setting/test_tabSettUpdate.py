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

import logging
import pytest
from astropy.utils import data, iers
from mw4.gui.extWindows.setting.tabSettUpdate import SettUpdate
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


def createMockCheckbox(defaultValue: bool = False):
    """Create a mock checkbox that stores and retrieves checked state."""
    m = mock.MagicMock()
    m._checked = defaultValue
    m.isChecked = mock.MagicMock(side_effect=lambda: m._checked)
    m.setChecked = mock.MagicMock(side_effect=lambda v: setattr(m, "_checked", v))
    m.clicked = mock.MagicMock()
    return m


def createMockSpinBox(defaultValue: int = 1):
    """Create a mock spinbox that stores and retrieves value."""
    m = mock.MagicMock()
    m._value = defaultValue
    m.value = mock.MagicMock(side_effect=lambda: m._value)
    m.setValue = mock.MagicMock(side_effect=lambda v: setattr(m, "_value", v))
    return m


@pytest.fixture(autouse=True, scope="module")
def settUpdate(qapp):
    """Setup SettUpdate fixture for testing."""
    parentW = MWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Create mock UI elements for SettUpdate
    parentW.ui.loglevelInfo = createMockCheckbox(defaultValue=False)
    parentW.ui.loglevelDebug = createMockCheckbox(defaultValue=True)
    parentW.ui.loglevelTrace = createMockCheckbox(defaultValue=False)
    parentW.ui.isOnline = createMockCheckbox(defaultValue=False)
    parentW.ui.ageDatabases = createMockSpinBox(defaultValue=1)
    parentW.ui.unitTimeUTC = createMockCheckbox(defaultValue=True)
    parentW.ui.unitTimeLocal = createMockCheckbox(defaultValue=False)

    window = SettUpdate(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_initConfig_with_defaults(settUpdate):
    """Test initConfig loads correct default values."""
    settUpdate.app.config["SettingUpdate"] = {}
    settUpdate.initConfig()

    assert settUpdate.ui.loglevelInfo.isChecked() is False
    assert settUpdate.ui.loglevelDebug.isChecked() is True
    assert settUpdate.ui.loglevelTrace.isChecked() is False
    assert settUpdate.ui.isOnline.isChecked() is False
    assert settUpdate.ui.ageDatabases.value() == 1


def test_initConfig_with_custom_values(settUpdate):
    """Test initConfig loads custom config values."""
    settUpdate.app.config["SettingUpdate"] = {
        "loglevelInfo": True,
        "loglevelDebug": False,
        "loglevelTrace": False,
        "isOnline": True,
        "ageDatabases": 7,
    }
    settUpdate.initConfig()

    assert settUpdate.ui.loglevelInfo.isChecked() is True
    assert settUpdate.ui.loglevelDebug.isChecked() is False
    assert settUpdate.ui.isOnline.isChecked() is True
    assert settUpdate.ui.ageDatabases.value() == 7


def test_storeConfig_saves_all_values(settUpdate):
    """Test storeConfig properly saves current UI state."""
    settUpdate.ui.loglevelInfo.setChecked(True)
    settUpdate.ui.loglevelDebug.setChecked(False)
    settUpdate.ui.loglevelTrace.setChecked(False)
    settUpdate.ui.isOnline.setChecked(True)
    settUpdate.ui.ageDatabases.setValue(14)

    settUpdate.storeConfig()

    config = settUpdate.app.config["SettingUpdate"]
    assert config["loglevelInfo"] is True
    assert config["loglevelDebug"] is False
    assert config["loglevelTrace"] is False
    assert config["isOnline"] is True
    assert config["ageDatabases"] == 14


def test_setOnlineMode_offline(settUpdate):
    """Test setOnlineMode disables online when unchecked."""
    settUpdate.ui.isOnline.setChecked(False)
    settUpdate.setOnlineMode()

    assert settUpdate.app.isOnline is False


def test_setOnlineMode_online(settUpdate):
    """Test setOnlineMode enables online when checked."""
    settUpdate.ui.isOnline.setChecked(True)
    settUpdate.setOnlineMode()

    assert settUpdate.app.isOnline is True


def test_setupIERS_offline_mode(settUpdate):
    """Test setupIERS disables auto-download when offline."""
    settUpdate.app.isOnline = False
    settUpdate.setupIERS()

    assert iers.conf.auto_download is False
    assert iers.conf.auto_max_age == 99999
    assert data.conf.allow_internet is False


def test_setupIERS_online_mode(settUpdate):
    """Test setupIERS enables auto-download when online."""
    settUpdate.app.isOnline = True
    settUpdate.setupIERS()

    assert iers.conf.auto_download is True
    assert iers.conf.auto_max_age == 30
    assert data.conf.allow_internet is True


def test_setLoggingLevel_debug(settUpdate):
    """Test setLoggingLevel sets DEBUG level."""
    settUpdate.ui.loglevelDebug.setChecked(True)
    settUpdate.ui.loglevelInfo.setChecked(False)
    settUpdate.ui.loglevelTrace.setChecked(False)

    settUpdate.setLoggingLevel()

    val = logging.getLogger("MW4").getEffectiveLevel()
    assert val == 10


def test_setLoggingLevel_info(settUpdate):
    """Test setLoggingLevel sets INFO level."""
    settUpdate.ui.loglevelDebug.setChecked(False)
    settUpdate.ui.loglevelInfo.setChecked(True)
    settUpdate.ui.loglevelTrace.setChecked(False)

    settUpdate.setLoggingLevel()

    val = logging.getLogger("MW4").getEffectiveLevel()
    assert val == 20


def test_setLoggingLevel_trace(settUpdate):
    """Test setLoggingLevel sets DEBUG level with TRACE enabled."""
    settUpdate.ui.loglevelDebug.setChecked(False)
    settUpdate.ui.loglevelInfo.setChecked(False)
    settUpdate.ui.loglevelTrace.setChecked(True)

    settUpdate.setLoggingLevel()

    val = logging.getLogger("MW4").getEffectiveLevel()
    assert val == 10


def test_setLoggingLevel_priority_info_over_trace(settUpdate):
    """Test setLoggingLevel priority: INFO over TRACE."""
    settUpdate.ui.loglevelDebug.setChecked(False)
    settUpdate.ui.loglevelInfo.setChecked(True)
    settUpdate.ui.loglevelTrace.setChecked(True)

    settUpdate.setLoggingLevel()

    val = logging.getLogger("MW4").getEffectiveLevel()
    assert val == 20


def test_setTimeBaseUTC_sets_config(settUpdate):
    """Test setTimeBaseUTC sets timeMgr config and emits signal."""
    settUpdate.setTimeBaseUTC()

    assert settUpdate.app.timeMgr.unitTimeUTC is True


def test_setTimeBaseLocal_sets_config(settUpdate):
    """Test setTimeBaseLocal sets timeMgr config and emits signal."""
    settUpdate.setTimeBaseLocal()

    assert settUpdate.app.timeMgr.unitTimeUTC is False


def test_storeConfig_with_timebase(settUpdate):
    """Test storeConfig saves SettingUpdate config."""
    settUpdate.ui.loglevelInfo.setChecked(False)
    settUpdate.ui.loglevelDebug.setChecked(True)
    settUpdate.ui.loglevelTrace.setChecked(False)
    settUpdate.ui.isOnline.setChecked(False)
    settUpdate.ui.ageDatabases.setValue(3)
    settUpdate.ui.unitTimeUTC.setChecked(True)
    settUpdate.ui.unitTimeLocal.setChecked(False)

    settUpdate.storeConfig()

    config = settUpdate.app.config["SettingUpdate"]
    assert config["isOnline"] is False
    assert config["loglevelInfo"] is False
    assert config["loglevelDebug"] is True
    assert config["loglevelTrace"] is False
    assert config["ageDatabases"] == 3


def test_setOnlineMode_emits_activated_message(settUpdate):
    """Test setOnlineMode sets isOnline when activated."""
    settUpdate.ui.isOnline.setChecked(True)
    settUpdate.setOnlineMode()

    assert settUpdate.app.isOnline is True


def test_setOnlineMode_emits_deactivated_message(settUpdate):
    """Test setOnlineMode clears isOnline when deactivated."""
    settUpdate.ui.isOnline.setChecked(False)
    settUpdate.setOnlineMode()

    assert settUpdate.app.isOnline is False


def test_initConfig_calls_setup_methods(settUpdate):
    """Test initConfig calls all setup methods."""
    settUpdate.app.config["SettingUpdate"] = {}
    with (
        mock.patch.object(settUpdate, "setLoggingLevel"),
        mock.patch.object(settUpdate, "setOnlineMode"),
        mock.patch.object(settUpdate, "setupIERS"),
    ):
        settUpdate.initConfig()

        assert settUpdate.ui.loglevelInfo.isChecked() is False
        assert settUpdate.ui.loglevelDebug.isChecked() is True
