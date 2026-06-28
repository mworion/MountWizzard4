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
from functools import partial
from mw4.base.threadUtils import mainThreadSleep
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
from pytestqt.qtbot import QWidget


class ExternalWindows:
    def __init__(self, mainW):
        self.mainW = mainW
        self.app = mainW.app

        self.uiWindows: dict[str, dict[str, QWidget]] = {
            "showMessageW": {
                "button": self.mainW.ui.openMessageW,
                "classObj": None,
                "name": "MessageDialog",
                "class": MessageWindow,
            },
            "showHemisphereW": {
                "button": self.mainW.ui.openHemisphereW,
                "classObj": None,
                "name": "HemisphereDialog",
                "class": HemisphereWindow,
            },
            "showImageW": {
                "button": self.mainW.ui.openImageW,
                "classObj": None,
                "name": "ImageDialog",
                "class": ImageWindow,
            },
            "showMeasureW": {
                "button": self.mainW.ui.openMeasureW,
                "classObj": None,
                "name": "MeasureDialog",
                "class": MeasureWindow,
            },
            "showSatelliteMapW": {
                "button": self.mainW.ui.openSatelliteMapW,
                "classObj": None,
                "name": "SatelliteMapDialog",
                "class": SatelliteMapWindow,
            },
            "showSatelliteHorizonW": {
                "button": self.mainW.ui.openSatelliteHorizonW,
                "classObj": None,
                "name": "SatelliteHorizonDialog",
                "class": SatelliteHorizonWindow,
            },
            "showAnalyseW": {
                "button": self.mainW.ui.openAnalyseW,
                "classObj": None,
                "name": "AnalyseDialog",
                "class": AnalyseWindow,
            },
            "showVideoW1": {
                "button": self.mainW.ui.openV1,
                "classObj": None,
                "name": "Video1",
                "class": VideoWindow,
            },
            "showVideoW2": {
                "button": self.mainW.ui.openV2,
                "classObj": None,
                "name": "Video2",
                "class": VideoWindow,
            },
            "showVideoW3": {
                "button": self.mainW.ui.openV3,
                "classObj": None,
                "name": "Video3",
                "class": VideoWindow,
            },
            "showVideoW4": {
                "button": self.mainW.ui.openV4,
                "classObj": None,
                "name": "Video4",
                "class": VideoWindow,
            },
            "showKeypadW": {
                "button": self.mainW.ui.openKeypadW,
                "classObj": None,
                "name": "KeypadDialog",
                "class": KeypadWindow,
            },
            "showSimulatorW": {
                "button": self.mainW.ui.mountConnected,
                "classObj": None,
                "name": "SimulatorDialog",
                "class": SimulatorWindow,
            },
            "showSettingW": {
                "button": self.mainW.ui.setting,
                "classObj": None,
                "name": "SettingDialog",
                "class": SettingWindow,
            },
        }

        for window in self.uiWindows:
            self.uiWindows[window]["button"].clicked.connect(
                partial(self.toggleWindow, window)
            )
        self.app.timeMgr.update1s.connect(self.updateWindowsStats)

    def updateWindowsStats(self) -> None:
        for win in self.uiWindows:
            winObj = self.uiWindows[win]

            if winObj["classObj"]:
                changeStyleDynamic(winObj["button"], "run", True)
            else:
                changeStyleDynamic(winObj["button"], "run", False)

    def storeConfigExtendedWindows(self):
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
            self.uiWindows[window]["classObj"].close()
            mainThreadSleep(50)
