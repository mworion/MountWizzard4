# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from functools import partial
from mw4.gui.extWindows.analyseW import AnalyseWindow
from mw4.gui.extWindows.hemisphere.hemisphereW import HemisphereWindow
from mw4.gui.extWindows.image.imageW import ImageWindow
from mw4.gui.extWindows.keypadW import KeypadWindow
from mw4.gui.extWindows.measure.measureW import MeasureWindow
from mw4.gui.extWindows.messageW import MessageWindow
from mw4.gui.extWindows.satelliteHorW import SatelliteHorizonWindow
from mw4.gui.extWindows.satelliteMapW import SatelliteMapWindow
from mw4.gui.extWindows.setting.settingW import SettingWindow
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow
from mw4.gui.extWindows.video.videoW import VideoWindow
from mw4.gui.utilities.qtHelpers import changeStyleDynamic
from typing import Any


class ExternalWindows:
    def __init__(self, mainW) -> None:
        self.log = logging.getLogger("MW4")
        self.mainW = mainW
        self.app = mainW.app

        self.uiWindows: dict[str, dict[str, Any]] = self.createWindowTable()
        self.setupSignals()

    def createWindowTable(self) -> dict[str, dict[str, Any]]:
        ui = self.mainW.ui
        windowSpec: list[tuple[str, Any, str, type]] = [
            ("showMessageW", ui.openMessageW, "MessageDialog", MessageWindow),
            ("showHemisphereW", ui.openHemisphereW, "HemisphereDialog", HemisphereWindow),
            ("showImageW", ui.openImageW, "ImageDialog", ImageWindow),
            ("showMeasureW", ui.openMeasureW, "MeasureDialog", MeasureWindow),
            ("showSatelliteMapW", ui.openSatelliteMapW, "SatelliteMapDialog", SatelliteMapWindow),
            (
                "showSatelliteHorizonW",
                ui.openSatelliteHorizonW,
                "SatelliteHorizonDialog",
                SatelliteHorizonWindow,
            ),
            ("showAnalyseW", ui.openAnalyseW, "AnalyseDialog", AnalyseWindow),
            ("showVideoW1", ui.openV1, "Video1", VideoWindow),
            ("showVideoW2", ui.openV2, "Video2", VideoWindow),
            ("showVideoW3", ui.openV3, "Video3", VideoWindow),
            ("showVideoW4", ui.openV4, "Video4", VideoWindow),
            ("showKeypadW", ui.openKeypadW, "KeypadDialog", KeypadWindow),
            ("showSimulatorW", ui.mountConnected, "SimulatorDialog", SimulatorWindow),
            ("showSettingW", ui.setting, "SettingDialog", SettingWindow),
        ]
        return {
            key: {"button": button, "classObj": None, "name": name, "class": windowClass}
            for key, button, name, windowClass in windowSpec
        }

    def setupSignals(self) -> None:
        for window in self.uiWindows:
            self.uiWindows[window]["button"].clicked.connect(partial(self.toggleWindow, window))
        self.app.timeMgr.update1s.connect(self.updateWindowsStats)

    def updateWindowsStats(self) -> None:
        for win in self.uiWindows:
            winObj = self.uiWindows[win]

            if winObj["classObj"]:
                changeStyleDynamic(winObj["button"], "run", "true")
            else:
                changeStyleDynamic(winObj["button"], "run", "false")

    def storeConfigExtendedWindows(self) -> None:
        for window in self.uiWindows:
            self.app.config[window] = bool(self.uiWindows[window]["classObj"])
            if self.app.config[window]:
                self.uiWindows[window]["classObj"].storeConfig()

    def deleteWindowResource(self, window: str) -> None:
        self.uiWindows[window]["classObj"] = None

    def buildWindow(self, window: str) -> None:
        self.uiWindows[window]["classObj"] = self.uiWindows[window]["class"](
            self.app, self.uiWindows[window]["name"]
        )
        self.uiWindows[window]["classObj"].destroyed.connect(
            partial(self.deleteWindowResource, window)
        )
        self.uiWindows[window]["classObj"].initConfig()
        self.uiWindows[window]["classObj"].showWindow()

    def showExtendedWindows(self) -> None:
        for window in self.uiWindows:
            if not self.app.config.get(window, False):
                continue
            self.log.debug("Build window    : %s", window)
            self.buildWindow(window)

    def toggleWindow(self, windowName) -> None:
        if not self.uiWindows[windowName]["classObj"]:
            self.buildWindow(windowName)
        else:
            self.uiWindows[windowName]["classObj"].close()

    def closeExtendedWindows(self) -> None:
        for window in self.uiWindows:
            if not self.uiWindows[window]["classObj"]:
                continue
            self.log.debug("Close window    : %s", window)
            self.uiWindows[window]["classObj"].close()
