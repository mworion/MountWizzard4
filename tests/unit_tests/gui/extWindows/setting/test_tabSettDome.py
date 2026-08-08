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
from mw4.gui.extWindows.setting.tabSettDome import SettDome
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    parentW = MWidget()
    parentW.app = App()
    parentW.ui = Ui_MainWindow()
    parentW.ui.setupUi(parentW)

    # Helper to create mock widgets
    def create_mock_spinbox(default_value=0):
        m = mock.MagicMock()
        m._value = default_value
        m.value = mock.MagicMock(side_effect=lambda: m._value)
        m.setValue = mock.MagicMock(side_effect=lambda v: setattr(m, "_value", v))
        return m

    def create_mock_checkbox(default_value=False):
        m = mock.MagicMock()
        m._checked = default_value
        m.isChecked = mock.MagicMock(side_effect=lambda: m._checked)
        m.setChecked = mock.MagicMock(side_effect=lambda v: setattr(m, "_checked", v))
        return m

    # Add mock UI elements needed by SettDome
    parentW.ui.domeRadius = create_mock_spinbox()
    parentW.ui.offGEM = create_mock_spinbox()
    parentW.ui.offLAT = create_mock_spinbox()
    parentW.ui.domeEastOffset = create_mock_spinbox()
    parentW.ui.domeNorthOffset = create_mock_spinbox()
    parentW.ui.domeVerticalOffset = create_mock_spinbox()
    parentW.ui.domeClearOpening = create_mock_spinbox()
    parentW.ui.domeOpeningHysteresis = create_mock_spinbox()
    parentW.ui.domeClearanceZenith = create_mock_spinbox()
    parentW.ui.useOvershoot = create_mock_checkbox()
    parentW.ui.settleTimeDome = create_mock_spinbox()
    parentW.ui.useDomeGeometry = create_mock_checkbox()
    parentW.ui.useDynamicFollowing = create_mock_checkbox()
    parentW.ui.copyFromDomeDriver = mock.MagicMock()
    parentW.ui.use10micronDef = create_mock_checkbox()
    parentW.ui.automaticDome = create_mock_checkbox()
    parentW.ui.tabDomeExplain = mock.MagicMock()

    # Add picture UI elements for setupIcons
    parentW.ui.picDome1 = mock.MagicMock()
    parentW.ui.picDome2 = mock.MagicMock()
    parentW.ui.picDome3 = mock.MagicMock()
    parentW.ui.picDome4 = mock.MagicMock()
    parentW.ui.picDome5 = mock.MagicMock()
    parentW.ui.picDome6 = mock.MagicMock()
    parentW.ui.picDome7 = mock.MagicMock()
    parentW.ui.picDome8 = mock.MagicMock()
    parentW.ui.picDome9 = mock.MagicMock()

    window = SettDome(parentW)
    yield window
    parentW.app.threadPool.waitForDone(1000)


def test_showDomeExplainTab(function):
    function.showDomeExplainTab(0)
    function.ui.tabDomeExplain.setCurrentIndex.assert_called_with(0)


def test_domeExplainTabsConnections(function):
    for widget, index in function.domeExplainTabs:
        callback = widget.valueChanged.connect.call_args[0][0]
        callback(None)
        function.ui.tabDomeExplain.setCurrentIndex.assert_called_with(index)


def test_initConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.initConfig()


def test_initConfig_2(function):
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.ui.use10micronDef.setChecked(True)
    function.setupIcons()


def test_setupIcons_2(function):
    function.ui.use10micronDef.setChecked(False)
    function.setupIcons()


def test_updateGeometryFromDriver_1(function):
    function.updateGeometryFromDriver()


def test_closeEvent_1(function):
    function.closeEvent()
