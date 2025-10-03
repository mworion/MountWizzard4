############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import shutil
import unittest.mock as mock
from pathlib import Path

import gui.utilities.toolsQtWidget
import pytest
from base import packageConfig
from gui.mainWindow.mainWindow import MainWindow

# external packages
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget
from skyfield.api import wgs84

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App

resources.qInitResources()


@pytest.fixture(autouse=True, scope="module")
def window(qapp):
    packageConfig.isAvailable = True
    with mock.patch.object(MainWindow, "show"):
        window = MainWindow(app=App())
        yield window
        window.app.threadPool.waitForDone(10000)


def test_initConfig_1(window):
    del window.app.config["mainW"]
    with mock.patch.object(window.mainWindowAddons, "initConfig"):
        with mock.patch.object(window, "smartTabGui"):
            with mock.patch.object(window, "enableTabsMovable"):
                with mock.patch.object(window, "setupIcons"):
                    window.initConfig()


def test_storeConfig_1(window):
    with mock.patch.object(window.mainWindowAddons, "storeConfig"):
        with mock.patch.object(window.externalWindows, "storeConfigExtendedWindows"):
            window.storeConfig()


def test_storeConfig_2(window):
    del window.app.config["mainW"]
    with mock.patch.object(window.mainWindowAddons, "storeConfig"):
        with mock.patch.object(window.externalWindows, "storeConfigExtendedWindows"):
            window.storeConfig()


def test_setupIcons_1(window):
    with mock.patch.object(window.mainWindowAddons, "setupIcons"):
        window.setupIcons()


def test_updateColorSet_1(window):
    with mock.patch.object(window, "setStyleSheet"):
        with mock.patch.object(window, "setupIcons"):
            with mock.patch.object(window.mainWindowAddons, "updateColorSet"):
                window.updateColorSet()


def test_enableTabsMovable(window):
    window.enableTabsMovable()


def test_closeEvent_1(window):
    with mock.patch.object(window.externalWindows, "closeExtendedWindows"):
        with mock.patch.object(window.mainWindowAddons.addons["SettDevice"], "stopDrivers"):
            with mock.patch.object(window.threadPool, "waitForDone"):
                window.closeEvent(QCloseEvent())


def test_quitSave_1(window):
    window.ui.profile.setText("test")
    with mock.patch.object(window, "saveProfile"):
        with mock.patch.object(gui.mainWindow.mainWindow, "saveProfile"):
            with mock.patch.object(window, "close"):
                window.quitSave()


def test_smartFunctionGui_0(window):
    window.app.deviceStat["mount"] = True
    window.app.deviceStat["camera"] = True
    window.app.deviceStat["plateSolve"] = True
    window.app.data.buildP = []
    window.ui.pauseModel.setProperty("pause", False)
    window.smartFunctionGui()


def test_smartFunctionGui_1(window):
    window.app.deviceStat["mount"] = True
    window.app.deviceStat["camera"] = True
    window.app.deviceStat["plateSolve"] = True
    window.app.data.buildP = [(0, 0)]
    window.smartFunctionGui()
    assert window.ui.runModel.isEnabled()
    assert window.ui.runFlexure.isEnabled()
    assert window.ui.runHysteresis.isEnabled()


def test_smartFunctionGui_2(window):
    window.app.deviceStat["mount"] = True
    window.app.deviceStat["camera"] = False
    window.app.deviceStat["plateSolve"] = True
    window.app.data.buildP = [(0, 0)]
    window.smartFunctionGui()
    assert not window.ui.runModel.isEnabled()
    assert not window.ui.runFlexure.isEnabled()
    assert not window.ui.runHysteresis.isEnabled()


def test_smartFunctionGui_3(window):
    window.app.deviceStat["mount"] = True
    window.smartFunctionGui()
    assert window.ui.refractionGroup.isEnabled()
    assert window.ui.dsoGroup.isEnabled()
    assert window.ui.mountCommandTable.isEnabled()


def test_smartFunctionGui_4(window):
    window.app.deviceStat["mount"] = False
    window.smartFunctionGui()
    assert not window.ui.refractionGroup.isEnabled()
    assert not window.ui.dsoGroup.isEnabled()
    assert not window.ui.mountCommandTable.isEnabled()


def test_smartFunctionGui_5(window):
    window.app.deviceStat["dome"] = True
    window.app.deviceStat["mount"] = True
    window.smartFunctionGui()
    assert window.ui.useDomeAz.isEnabled()


def test_smartFunctionGui_6(window):
    window.app.deviceStat["dome"] = False
    window.app.deviceStat["mount"] = False
    window.smartFunctionGui()
    assert not window.ui.useDomeAz.isEnabled()


def test_smartTabGui_1(window):
    window.smartTabGui()


def test_smartTabGui_2(window):
    window.app.deviceStat["power"] = True
    window.smartTabGui()


def test_setEnvironDeviceStats_1(window):
    window.ui.showTabEnviron.setChecked(True)
    window.app.mount.setting.statusRefraction = 0

    window.setEnvironDeviceStats()
    assert window.app.deviceStat["refraction"] is None


def test_setEnvironDeviceStats_2(window):
    window.ui.showTabEnviron.setChecked(True)
    window.ui.refracManual.setChecked(True)
    window.app.mount.setting.statusRefraction = 1

    window.setEnvironDeviceStats()
    assert window.app.deviceStat["refraction"]


def test_setEnvironDeviceStats_3(window):
    window.ui.showTabEnviron.setChecked(True)
    window.ui.refracCont.setChecked(True)
    window.app.mount.setting.statusRefraction = 1
    window.mainWindowAddons.addons["EnvironWeather"].refractionSource = "onlineWeather"
    window.app.deviceStat["onlineWeather"] = False

    window.setEnvironDeviceStats()
    assert not window.app.deviceStat["refraction"]


def test_updateDeviceStats_1(window):
    window.deviceStatGui = {"onlineWeather": QWidget()}
    window.app.deviceStat = {"onlineWeather": True}
    window.updateDeviceStats()


def test_updateDeviceStats_2(window):
    window.deviceStatGui = {"onlineWeather": QWidget()}
    window.app.deviceStat = {"onlineWeather": False}
    window.updateDeviceStats()


def test_updateDeviceStats_3(window):
    window.deviceStatGui = {"onlineWeather": QWidget()}
    window.app.deviceStat = {"onlineWeather": None}
    window.updateDeviceStats()


def test_updatePlateSolveStatus_1(window):
    window.updatePlateSolveStatus("")


def test_updateMountConnStat_1(window):
    window.updateMountConnStat(True)
    assert window.app.deviceStat["mount"]


def test_updatePlateSolveStatus(window):
    window.updatePlateSolveStatus("test")
    assert window.ui.plateSolveText.text() == "test"


def test_updateDomeStatus(window):
    window.updateDomeStatus("test")
    assert window.ui.domeText.text() == "test"


def test_updateCameraStatus(window):
    window.updateCameraStatus("test")
    assert window.ui.cameraText.text() == "test"
    window.updateControllerStatus()


def test_updateThreadAndOnlineStatus_1(window):
    window.app.mwGlob["workDir"] = "tests/work"
    window.ui.isOnline.setChecked(True)
    with mock.patch.object(shutil, "disk_usage", return_value=(100, 100, 100)):
        window.updateThreadAndOnlineStatus()


def test_updateThreadAndOnlineStatus_2(window):
    window.app.mwGlob["workDir"] = "tests/work"
    window.ui.isOnline.setChecked(False)
    with mock.patch.object(shutil, "disk_usage", return_value=(100, 100, 100)):
        window.updateThreadAndOnlineStatus()


def test_updateTime_1(window):
    window.updateTime()


def test_updateStatusGUI_1(window):
    class OB:
        @staticmethod
        def statusText():
            return None

    window.app.mount.obsSite.status = 0
    window.updateStatusGUI(OB)


def test_updateStatusGUI_2(window):
    class OB:
        @staticmethod
        def statusText():
            return "test"

    window.app.mount.obsSite.status = 0
    window.updateStatusGUI(OB)
    assert window.ui.statusText.text() == "test"


def test_updateStatusGUI_3(window):
    class OB:
        @staticmethod
        def statusText():
            return None

    window.app.mount.obsSite.status = 5
    window.updateStatusGUI(OB)


def test_updateStatusGUI_4(window):
    class OB:
        @staticmethod
        def statusText():
            return None

    window.app.mount.obsSite.status = 1
    window.updateStatusGUI(OB)


def test_updateStatusGUI_5(window):
    class OB:
        @staticmethod
        def statusText():
            return None

    window.app.mount.obsSite.status = 10
    window.satStatus = False
    window.updateStatusGUI(OB)


def test_switchProfile_1(window):
    loc = wgs84.latlon(latitude_degrees=10, longitude_degrees=10)
    with mock.patch.object(window.externalWindows, "closeExtendedWindows"):
        with mock.patch.object(window.externalWindows, "showExtendedWindows"):
            with mock.patch.object(window, "initConfig"):
                with mock.patch.object(window.app, "initConfig", return_value=loc):
                    with mock.patch.object(
                        window.mainWindowAddons.addons["SettDevice"], "stopDrivers"
                    ):
                        window.switchProfile({"test": 1})


def test_loadProfileGUI_1(window):
    with mock.patch.object(window, "openFile", return_value=Path("")):
        with mock.patch.object(Path, "is_file", return_value=False):
            window.loadProfileGUI()


def test_loadProfileGUI2(window):
    with mock.patch.object(window, "openFile", return_value=Path("config.cfg")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(gui.mainWindow.mainWindow, "loadProfile", return_value={}):
                with mock.patch.object(window, "switchProfile"):
                    window.loadProfileGUI()


def test_loadProfileGUI_3(window):
    with mock.patch.object(window, "openFile", return_value=Path("test.cfg")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(
                gui.mainWindow.mainWindow, "loadProfile", return_value={"test": 1}
            ):
                with mock.patch.object(window, "switchProfile"):
                    window.loadProfileGUI()


def test_addProfileGUI_1(window):
    with mock.patch.object(window, "openFile", return_value=Path("cfg")):
        suc = window.addProfileGUI()
        assert not suc


def test_addProfileGUI_2(window):
    with mock.patch.object(window, "openFile", return_value=Path("test.cfg")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(
                gui.mainWindow.mainWindow, "loadProfile", return_value=None
            ):
                with mock.patch.object(window, "storeConfig"):
                    with mock.patch.object(window.app, "storeConfig"):
                        with mock.patch.object(window, "switchProfile"):
                            with mock.patch.object(gui.mainWindow.mainWindow, "blendProfile"):
                                suc = window.addProfileGUI()
                                assert not suc


def test_addProfileGUI_3(window):
    with mock.patch.object(window, "openFile", return_value=Path("test.cfg")):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(
                gui.mainWindow.mainWindow, "loadProfile", return_value={"test": 1}
            ):
                with mock.patch.object(window, "storeConfig"):
                    with mock.patch.object(window.app, "storeConfig"):
                        with mock.patch.object(window, "switchProfile"):
                            with mock.patch.object(gui.mainWindow.mainWindow, "blendProfile"):
                                window.addProfileGUI()


def test_saveConfigAs1(window):
    with mock.patch.object(window, "saveFile", return_value=Path("test.cfg")):
        with mock.patch.object(gui.mainWindow.mainWindow, "saveProfile", return_value=True):
            with mock.patch.object(window.app, "storeConfig"):
                with mock.patch.object(window, "storeConfig"):
                    window.saveProfileAs()


def test_saveConfigAs2(window):
    with mock.patch.object(window, "saveFile", return_value=Path("test.cfg")):
        with mock.patch.object(gui.mainWindow.mainWindow, "saveProfile", return_value=False):
            with mock.patch.object(window.app, "storeConfig"):
                with mock.patch.object(window, "storeConfig"):
                    window.saveProfileAs()


def test_saveConfigAs3(window):
    with mock.patch.object(window, "saveFile", return_value=Path("")):
        window.saveProfileAs()


def test_saveConfig1(window):
    with mock.patch.object(window, "storeConfig"):
        with mock.patch.object(window.app, "storeConfig"):
            with mock.patch.object(
                gui.mainWindow.mainWindow, "saveProfile", return_value=True
            ):
                window.saveProfile()


def test_saveConfig2(window):
    with mock.patch.object(window, "storeConfig"):
        with mock.patch.object(window.app, "storeConfig"):
            with mock.patch.object(
                gui.mainWindow.mainWindow, "saveProfile", return_value=False
            ):
                window.saveProfile()


def test_remoteCommand_1(window):
    window.remoteCommand("")


def test_remoteCommand_2(window):
    with mock.patch.object(window, "quitSave"):
        window.remoteCommand("shutdown")


def test_remoteCommand_3(window):
    with mock.patch.object(window.mainWindowAddons.addons["SettMount"], "mountShutdown"):
        window.remoteCommand("shutdown mount")


def test_remoteCommand_4(window):
    with mock.patch.object(window.mainWindowAddons.addons["SettMount"], "mountBoot"):
        window.remoteCommand("boot mount")
