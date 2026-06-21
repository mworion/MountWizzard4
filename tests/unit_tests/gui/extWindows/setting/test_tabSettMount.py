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
import mw4.gui
import mw4.gui.extWindows.setting.tabSettMount
import pytest
import unittest.mock as mock
import wakeonlan
from mw4.gui.extWindows.setting.tabSettMount import SettMount
from mw4.gui.widgets.setting_ui import Ui_SettingDialog
from PySide6.QtWidgets import QWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_SettingDialog()
    mainW.ui.setupUi(mainW)

    # Mock the clicked signal for buttons that need it
    mainW.ui.mountOn.clicked = mock.MagicMock()
    mainW.ui.mountOff.clicked = mock.MagicMock()
    mainW.ui.bootRackComp.clicked = mock.MagicMock()

    # Add wIcon method to mainW for setupIcons
    mainW.wIcon = mock.MagicMock()

    window = SettMount(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["WindowMain"] = {"automaticWOL": True}
    with mock.patch.object(function, "mountBoot"):
        function.initConfig()


def test_storeConfig1(function):
    function.storeConfig()


def test_setMountCapabilities_1(function):
    function.setMountCapabilities(function.app.mount.firmware)


def test_mountBoot_1(function):
    with mock.patch.object(function.app.mount, "bootMount", return_value=False):
        function.mountBoot()


def test_mountBoot_2(function):
    with mock.patch.object(function.app.mount, "bootMount", return_value=True):
        function.mountBoot()


def test_mountShutdown_1(function):
    with mock.patch.object(function.app.mount, "shutdown", return_value=False):
        function.mountShutdown()


def test_mountShutdown_2(function):
    with mock.patch.object(function.app.mount, "shutdown", return_value=True):
        function.mountShutdown()


def test_bootRackComp_1(function):
    with (
        mock.patch.object(
            mw4.gui.extWindows.setting.tabSettMount, "checkFormatMAC", return_value=False
        ),
        mock.patch.object(wakeonlan, "send_magic_packet", return_value=False),
    ):
        function.bootRackComp()


def test_bootRackComp_2(function):
    function.ui.rackCompMAC.setText("00:00:00:00:00:xy")
    with (
        mock.patch.object(
            mw4.gui.extWindows.setting.tabSettMount, "checkFormatMAC", return_value=True
        ),
        mock.patch.object(wakeonlan, "send_magic_packet", return_value=True),
    ):
        function.bootRackComp()


def test_setMountMAC_1(function):
    function.setMountMAC()


def test_setMountMAC_2(function):
    class Test:
        addressLanMAC = None
        typeConnection = 0

    function.setMountMAC(sett=Test())


def test_setMountMAC_3(function):
    class Test:
        addressLanMAC = ""
        typeConnection = 0

    function.setMountMAC(sett=Test())


def test_setMountMAC_4(function):
    class Test:
        addressLanMAC = None
        typeConnection = 0

    function.app.mount.MAC = None
    function.setMountMAC(sett=Test())


def test_setMountMAC_5(function):
    class Test:
        addressLanMAC = "00:00:0xx:00:00:00"
        typeConnection = 3

    function.setMountMAC(sett=Test())


def test_setMountMAC_6(function):
    class Test:
        addressLanMAC = "00:00:00:00:00:00"
        typeConnection = 3

    function.app.mount.MAC = "00:00:00:00:00:00"
    function.setMountMAC(Test())


def test_updateFwGui_1(function):
    function.updateFwGui(function.app.mount.firmware)


def test_toggleClockSync_1(function):
    function.ui.clockSync.setChecked(True)
    function.toggleClockSync()


def test_toggleClockSync_2(function):
    function.ui.clockSync.setChecked(False)
    function.toggleClockSync()


def test_closeEvent(function):
    function.closeEvent()


def test_setupIcons(function):
    function.setupIcons()


def test_showMountStatus_1(function):
    function.showMountStatus(True)


def test_showMountStatus_2(function):
    function.showMountStatus(False)
