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
from mw4.gui.extWindows.setting.tabSettGui import SettGui
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QCheckBox, QComboBox
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def settGui(qapp):
    """Setup SettGui fixture for testing."""
    parentW = MWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    parentW.ui.colorSet = QComboBox()
    parentW.ui.colorSet.addItem("Color1")
    parentW.ui.colorSet.addItem("Color2")
    parentW.ui.colorSet.addItem("Color3")
    parentW.ui.soundSatStartTracking = QComboBox()
    parentW.ui.soundSatStartTracking.addItem("None")
    parentW.ui.soundSatStartTracking.addItem("Beep")
    parentW.ui.controllerOverview = mock.MagicMock()
    parentW.ui.hidDome = QCheckBox()
    parentW.ui.hidAltAz = QCheckBox()
    parentW.ui.hidRaDec = QCheckBox()
    parentW.ui.hidTracking = QCheckBox()
    parentW.ui.hidParkStop = QCheckBox()
    parentW.ui.transparency = mock.MagicMock()
    parentW.ui.transparency.value = mock.MagicMock(return_value=1)
    parentW.ui.transparency.setValue = mock.MagicMock()
    parentW.ui.transparency.valueChanged = mock.MagicMock()
    parentW.ui.transparency.valueChanged.connect = mock.MagicMock()

    window = SettGui(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_initConfig_with_defaults(settGui):
    """Test initConfig loads default values."""
    settGui.app.config["SettingGui"] = {}
    settGui.initConfig()
    assert settGui.ui.colorSet.currentIndex() == 0
    assert settGui.ui.hidParkStop.isChecked() is True


def test_storeConfig_saves_color(settGui):
    """Test storeConfig saves colorSet."""
    settGui.ui.colorSet.setCurrentIndex(1)
    settGui.storeConfig()
    config = settGui.app.config["SettingGui"]
    assert config["colorSet"] == 1


def test_storeConfig_saves_hidParkStop(settGui):
    """Test storeConfig saves hidParkStop."""
    settGui.ui.hidParkStop.setChecked(False)
    settGui.storeConfig()
    cfg = settGui.app.dReg["hidController"].instance.config
    assert cfg.parkStop is False


def test_initConfig_hidParkStop_unchecked(settGui):
    """Test initConfig with hidParkStop unchecked."""
    settGui.app.dReg["hidController"].instance.config.parkStop = False
    settGui.ui.hidParkStop.setChecked(True)
    settGui.initConfig()
    assert settGui.ui.hidParkStop.isChecked() is False


def test_setupIcons_creates_icons(settGui):
    """Test setupIcons method."""
    settGui.setupIcons()


def test_updateColorSet_updates_app(settGui):
    """Test updateColorSet updates color set."""
    settGui.ui.colorSet.setCurrentIndex(1)
    settGui.updateColorSet()

    from mw4.gui.styles.styles import Styles

    assert Styles.colorSet == 1
