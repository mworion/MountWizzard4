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
from mw4.gui.extWindows.setting.tabSettAudio import SettAudio
from mw4.gui.extWindows.setting.tabSettDevice import SettDevice
from mw4.gui.extWindows.setting.tabSettDome import SettDome
from mw4.gui.extWindows.setting.tabSettGui import SettGui
from mw4.gui.extWindows.setting.tabSettMount import SettMount
from mw4.gui.extWindows.setting.tabSettParkRelay import SettParkRelay
from mw4.gui.extWindows.setting.tabSettUpdate import SettUpdate
from mw4.gui.utilities.qtHelpers import getTabAndIndex, setTabAndIndex
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets import setting_ui
from typing import Any


class SettingWindow(MWidget):
    log = logging.getLogger("MW4")

    def __init__(self, app: Any, title: str) -> None:
        super().__init__()
        self.app = app
        self.ui = setting_ui.Ui_SettingDialog()
        self.ui.setupUi(self.ws)
        self.setWindowTitle("Setting")
        self.tabSettDevice = SettDevice(self)
        self.tabSettMount = SettMount(self)
        self.tabSettDome = SettDome(self)
        self.tabSettUpdate = SettUpdate(self)
        self.tabSettGui = SettGui(self)
        self.tabSettAudio = SettAudio(self)
        #self.tabSettParkPos = SettParkRelay(self)
        self.app.colorChange.connect(self.colorChange)
        self.setupIcons()

    def initConfig(self) -> None:
        config = self.app.config.get("WindowSetting", {})
        self.positionWindow(config)
        setTabAndIndex(self.ui.tabWidget, config, "TabOrder")
        self.tabSettMount.initConfig()
        self.tabSettDome.initConfig()
        self.tabSettUpdate.initConfig()
        self.tabSettGui.initConfig()
        self.tabSettAudio.initConfig()
        #self.tabSettParkRelay.initConfig()

    def storeConfig(self) -> None:
        configMain = self.app.config
        configMain["WindowSetting"] = {}
        config = configMain["WindowSetting"]
        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        getTabAndIndex(self.ui.tabWidget, config, "TabOrder")
        self.tabSettMount.storeConfig()
        self.tabSettDome.storeConfig()
        self.tabSettGui.storeConfig()
        self.tabSettAudio.storeConfig()
        self.tabSettUpdate.storeConfig()
        #self.tabSettParkRelay.storeConfig()

    def setupIcons(self) -> None:
        self.tabSettDevice.setupIcons()
        self.tabSettMount.setupIcons()
        self.tabSettDome.setupIcons()
        self.tabSettGui.setupIcons()
        #self.tabSettParkRelay.setupIcons()

    def closeEvent(self, closeEvent) -> None:
        self.storeConfig()
        self.tabSettDevice.closeEvent()
        self.tabSettMount.closeEvent()
        super().closeEvent(closeEvent)

    def colorChange(self) -> None:
        self.setStyleSheet(self.mw4Style)
        self.setupIcons()

    def showWindow(self) -> None:
        self.show()
        self.setMinimumSize(self.FULL_WIDTH, 450)
        self.setMaximumSize(self.FULL_WIDTH, 450)
        self.titleBar.normButton.setVisible(False)
        self.titleBar.maxButton.setVisible(False)
        self.titleBar.windowFixed = True
