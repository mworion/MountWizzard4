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
import socket
import unittest.mock as mock
import wakeonlan
from mw4.gui.extWindows.setting.tabSettMount import SettMount
from mw4.gui.widgets.main_ui import Ui_MainWindow
from PySide6.QtWidgets import QWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)

    # Helper to create mock widgets that store values
    def create_mock_lineedit(default_value=""):
        m = mock.MagicMock()
        m._value = default_value
        m.text = mock.MagicMock(side_effect=lambda: m._value)
        m.setText = mock.MagicMock(side_effect=lambda v: setattr(m, "_value", v))
        return m

    def create_mock_checkbox(default_value=False):
        m = mock.MagicMock()
        m._checked = default_value
        m.isChecked = mock.MagicMock(side_effect=lambda: m._checked)
        m.setChecked = mock.MagicMock(side_effect=lambda v: setattr(m, "_checked", v))
        return m

    # Add mock UI elements needed by SettMount
    mainW.ui.mountOn = mock.MagicMock()
    mainW.ui.mountOff = mock.MagicMock()
    mainW.ui.mountHost = create_mock_lineedit()
    mainW.ui.port3492 = create_mock_checkbox(default_value=True)
    mainW.ui.port3490 = create_mock_checkbox(default_value=False)

    # Make port3492 and port3490 mutually exclusive
    def set_port3492(v):
        mainW.ui.port3492._checked = v
        if v:
            mainW.ui.port3490._checked = False

    def set_port3490(v):
        mainW.ui.port3490._checked = v
        if v:
            mainW.ui.port3492._checked = False

    mainW.ui.port3492.setChecked = mock.MagicMock(side_effect=set_port3492)
    mainW.ui.port3490.setChecked = mock.MagicMock(side_effect=set_port3490)

    mainW.ui.mountMAC = create_mock_lineedit()
    mainW.ui.bootRackComp = mock.MagicMock()
    mainW.ui.mountWolAddress = create_mock_lineedit(default_value="255.255.255.255")
    mainW.ui.mountWolPort = create_mock_lineedit(default_value="9")
    mainW.ui.rackCompMAC = create_mock_lineedit()
    mainW.ui.automaticWOL = create_mock_checkbox()
    mainW.ui.clockSync = create_mock_checkbox()
    mainW.ui.syncTimeNone = create_mock_checkbox(default_value=True)
    mainW.ui.syncTimeCont = create_mock_checkbox()
    mainW.ui.syncTimeNotTrack = create_mock_checkbox()
    mainW.ui.GroupWOL = mock.MagicMock()
    mainW.ui.product = mock.MagicMock()
    mainW.ui.vString = mock.MagicMock()
    mainW.ui.fwdate = mock.MagicMock()
    mainW.ui.fwtime = mock.MagicMock()
    mainW.ui.hardware = mock.MagicMock()
    mainW.ui.mount_productRAM = mock.MagicMock()
    mainW.ui.mount_productROM = mock.MagicMock()
    mainW.ui.mointAlt = mock.MagicMock()
    mainW.ui.mointAz = mock.MagicMock()
    mainW.ui.mointHA = mock.MagicMock()
    mainW.ui.mointDEC = mock.MagicMock()
    mainW.ui.mointRA = mock.MagicMock()
    mainW.ui.mount_time = mock.MagicMock()
    mainW.ui.mount_SID = mock.MagicMock()
    mainW.ui.mount_siteLat = mock.MagicMock()
    mainW.ui.mount_siteLon = mock.MagicMock()
    mainW.ui.mount_alignment = mock.MagicMock()
    mainW.ui.mount_tracking = mock.MagicMock()
    mainW.ui.mount_pierE = mock.MagicMock()
    mainW.ui.mount_pierW = mock.MagicMock()
    mainW.ui.use10micronDef = mock.MagicMock()

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


def test_mountHost_1(function):
    function.ui.port3492.setChecked(True)
    function.ui.mountHost.setText("")
    function.mountHost()


def test_mountHost_2(function):
    function.ui.port3490.setChecked(True)
    function.ui.mountHost.setText("192.168.2.1")
    with mock.patch.object(socket, "gethostbyname", return_value=True, side_effect=Exception):
        function.mountHost()


def test_mountHost_3(function):
    function.ui.port3490.setChecked(True)
    function.ui.mountHost.setText("192.168.2.1")
    function.mountHost()
    assert function.app.mount.host == ("192.168.2.1", 3490)


def test_mountMAC(function):
    function.ui.mountMAC.setText("00:00:00:00:00:00")
    function.mountMAC()

    assert function.app.mount.MAC == "00:00:00:00:00:00"


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


def test_syncClock_1(function):
    function.ui.syncTimeNone.setChecked(True)
    function.syncClock()


def test_syncClock_2(function):
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeNotTrack.setChecked(True)
     function.app.dReg.d["mount"].stat = False
     function.syncClock()


def test_syncClock_3(function):
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeNotTrack.setChecked(True)
     function.app.dReg.d["mount"].stat = True
     function.app.mount.obsSite.status = 0
     function.syncClock()


def test_syncClock_4(function):
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeCont.setChecked(True)
     function.app.dReg.d["mount"].stat = True
     function.app.mount.obsSite.status = 1
     function.app.mount.obsSite.timeDiff = 0
     function.syncClock()


def test_syncClock_5(function):
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeCont.setChecked(False)
     function.app.dReg.d["mount"].stat = True
     function.app.mount.obsSite.status = 1
     function.app.mount.obsSite.timeDiff = 1
     with mock.patch.object(function.app.mount.obsSite, "adjustClock", return_value=False):
         function.syncClock()


def test_syncClock_6(function):
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeCont.setChecked(True)
     function.app.dReg.d["mount"].stat = True
     function.app.mount.obsSite.status = 1
     function.app.mount.obsSite.timeDiff = 1
     with mock.patch.object(function.app.mount.obsSite, "adjustClock", return_value=True):
         function.syncClock()


def test_closeEvent(function):
    function.closeEvent()


def test_setupIcons(function):
    function.setupIcons()


def test_showMountStatus_1(function):
    function.showMountStatus(True)


def test_showMountStatus_2(function):
     function.showMountStatus(False)


def test_initConfig_with_automaticWOL_checked(function):
     """Test initConfig calls mountBoot when automaticWOL is checked."""
     function.app.config["SettingDeviceMount"] = {"automaticWOL": True}
     with mock.patch.object(function, "mountBoot"):
         function.initConfig()
         function.mountBoot.assert_called()


def test_syncClock_with_syncTimeNotTrack_and_tracking(function):
     """Test syncClock returns early when tracking and doSyncNotTrack is checked."""
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeNotTrack.setChecked(True)
     function.app.dReg.d["mount"].stat = True
     function.app.mount.obsSite.status = 10
     function.msg = mock.MagicMock()
     function.syncClock()


def test_syncClock_with_small_delta(function):
     """Test syncClock returns early when delta is below threshold."""
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeCont.setChecked(True)
     function.app.dReg.d["mount"].stat = True
     function.app.mount.obsSite.status = 1
     function.app.mount.obsSite.timeDiff = 0.005
     function.msg = mock.MagicMock()
     function.syncClock()
     function.msg.emit.assert_not_called()


def test_syncClock_with_large_positive_delta(function):
     """Test syncClock clamps large positive delta to 999."""
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeCont.setChecked(True)
     function.app.dReg.d["mount"].stat = True
     function.app.mount.obsSite.status = 1
     function.app.mount.obsSite.timeDiff = 2.0
     with mock.patch.object(
         function.app.mount.obsSite, "adjustClock", return_value=True
     ) as mock_adjust:
         function.msg = mock.MagicMock()
         function.syncClock()
         # Verify adjustClock was called
         assert mock_adjust.called
         call_args = mock_adjust.call_args[0]
         # Delta is 2000ms, clamped to 999
         assert call_args[0] == 999


def test_syncClock_with_large_negative_delta(function):
     """Test syncClock clamps large negative delta to -999."""
     function.ui.syncTimeNone.setChecked(False)
     function.ui.syncTimeCont.setChecked(True)
     function.app.dReg.d["mount"].stat = True
     function.app.mount.obsSite.status = 1
     function.app.mount.obsSite.timeDiff = -2.0
     with mock.patch.object(
         function.app.mount.obsSite, "adjustClock", return_value=True
     ) as mock_adjust:
         function.msg = mock.MagicMock()
         function.syncClock()
         # Verify adjustClock was called
         assert mock_adjust.called
         call_args = mock_adjust.call_args[0]
         # Delta is -2000ms, clamped to -999
         assert call_args[0] == -999
