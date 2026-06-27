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
import unittest.mock as mock
from mw4.gui.mainWaddon.tabMount import Mount
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    class TestAddOns:
        def __init__(self):
            self.addons = {"MountSett": mock.Mock()}

    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    mainW.mainWindowAddons = TestAddOns()
    window = Mount(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.initConfig()


def test_initConfig_2(function):
    del function.app.config["WindowMain"]
    function.initConfig()


def test_storeConfig_1(function):
    function.app.config["WindowMain"] = {}
    function.storeConfig()


def test_changeTrackingHid_1(function):
    with mock.patch.object(function, "changeTracking"):
        function.changeTrackingHid(4)


def test_changeTracking_ok2(function, qtbot):
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function.app.mount.obsSite, "stopTracking", return_value=False):
        function.changeTracking()


def test_changeTracking_ok3(function, qtbot):
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function.app.mount.obsSite, "stopTracking", return_value=True):
        function.changeTracking()


def test_changeTracking_ok4(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite, "startTracking", return_value=True):
        function.changeTracking()


def test_changeTracking_ok5(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite, "startTracking", return_value=False):
        function.changeTracking()


def test_changeParkHid_1(function):
    with mock.patch.object(function, "changePark"):
        function.changeParkHid(1)


def test_changePark_ok1(function):
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.obsSite, "unpark", return_value=False):
        function.changePark()


def test_changePark_ok2(function):
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function.app.mount.obsSite, "unpark", return_value=True):
        function.changePark()


def test_changePark_ok3(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite, "park", return_value=False):
        function.changePark()


def test_changePark_ok4(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite, "park", return_value=True):
        function.changePark()


def test_changePark_notok(function, qtbot):
    with mock.patch.object(function.app.mount.obsSite, "park", return_value=True):
        function.changePark()


def test_setLunarTracking_1(function):
    with mock.patch.object(function.app.mount.setting, "setLunarTracking", return_value=True):
        function.setLunarTracking()


def test_setLunarTracking_2(function):
    with mock.patch.object(function.app.mount.setting, "setLunarTracking", return_value=False):
        function.setLunarTracking()


def test_setSiderealTracking_1(function):
    with mock.patch.object(
        function.app.mount.setting, "setSiderealTracking", return_value=False
    ):
        function.setSiderealTracking()


def test_setSiderealTracking_2(function):
    with mock.patch.object(
        function.app.mount.setting, "setSiderealTracking", return_value=True
    ):
        function.setSiderealTracking()


def test_setSolarTracking_1(function):
    with mock.patch.object(function.app.mount.setting, "setSolarTracking", return_value=False):
        suc = function.setSolarTracking()
        assert not suc


def test_setSolarTracking_2(function):
    with mock.patch.object(function.app.mount.setting, "setSolarTracking", return_value=True):
        function.setSolarTracking()


def test_flipMountHid_1(function):
    with mock.patch.object(function, "flipMount"):
        function.flipMountHid(2)


def test_flipMount_1(function):
    with mock.patch.object(function.app.mount.obsSite, "flip", return_value=False):
        function.flipMount()


def test_flipMount_2(function):
    with mock.patch.object(function.app.mount.obsSite, "flip", return_value=True):
        function.flipMount()


def test_stopHid_1(function):
    with mock.patch.object(function, "stop"):
        function.stopHid(8)


def test_stop_1(function):
    with mock.patch.object(function.app.mount.obsSite, "stop", return_value=True):
        function.stop()


def test_stop_2(function):
    with mock.patch.object(function.app.mount.obsSite, "stop", return_value=False):
        function.stop()


def test_setHidIcon_status0(function):
    ui = mock.Mock()
    function.setHidIcon(ui, status=0)
    ui.setPixmap.assert_called_once()


def test_setHidIcon_status1(function):
    ui = mock.Mock()
    function.setHidIcon(ui, status=1)
    ui.setPixmap.assert_called_once()


def test_setHidIcon_status2(function):
    ui = mock.Mock()
    function.setHidIcon(ui, status=2)
    ui.setPixmap.assert_called_once()


def test_setHidIcons_connectedWithFeatureDisabled(function):
    """Test setHidIcons when connected but feature disabled (status=1)."""
    with mock.patch.object(function, "setHidIcon") as mock_setHidIcon:
        # Set connected status
        function.app.dReg["hidController"].stat = True
        # Set one config flag to False (feature disabled)
        function.app.dReg["hidController"].instance.config.moveAltAz = False
        function.app.dReg["hidController"].instance.config.moveRaDec = True
        function.app.dReg["hidController"].instance.config.tracking = True
        function.app.dReg["hidController"].instance.config.parkStop = True
        function.app.dReg["hidController"].instance.config.dome = True

        function.setHidIcons()

        # Verify all 5 icons were updated
        assert mock_setHidIcon.call_count == 5
        # Verify first call (moveAltAz) got status=1 (connected but disabled)
        calls = mock_setHidIcon.call_args_list
        assert calls[0][0][1] == 1  # First icon should have status=1


def test_setHidIcons(function):
    with mock.patch.object(function, "setHidIcon") as mock_setHidIcon:
        function.setHidIcons()
        assert mock_setHidIcon.call_count == 5
