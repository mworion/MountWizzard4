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


def test_tab1(function):
    function.tab1()


def test_tab2(function):
    function.tab2()


def test_tab3(function):
    function.tab3()


def test_tab4(function):
    function.tab4()


def test_tab5(function):
    function.tab5()


def test_tab6(function):
    function.tab6()


def test_tab7(function):
    function.tab7()


def test_tab8(function):
    function.tab8()


def test_tab9(function):
    function.tab9()


def test_initConfig_1(function):
    function.app.config["WindowMain"] = {}
    with mock.patch.object(function, "setUseGeometry"):
        function.initConfig()


def test_initConfig_2(function):
    with mock.patch.object(function, "setUseGeometry"):
        function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.ui.use10micronDef.setChecked(True)
    function.setupIcons()


def test_setupIcons_2(function):
    function.ui.use10micronDef.setChecked(False)
    function.setupIcons()


def test_switchGeometryDefinition_1(function):
    function.ui.use10micronDef.setChecked(True)
    function.switchGeometryDefinition()


def test_switchGeometryDefinition_2(function):
    function.ui.use10micronDef.setChecked(False)
    function.switchGeometryDefinition()


def test_setUseGeometry_1(function):
    function.ui.use10micronDef.setChecked(False)
    function.ui.automaticDome.setChecked(False)
    function.setUseGeometry()


def test_setUseGeometry_2(function):
    function.ui.use10micronDef.setChecked(True)
    function.ui.automaticDome.setChecked(True)
    with mock.patch.object(function, "updateDomeGeometryToGui"):
        function.setUseGeometry()


def test_updateDomeGeometry_1(function):
    function.updateDomeGeometryToGui()


def test_setDomeSettlingTime_1(function):
    function.setDomeSettlingTime()
