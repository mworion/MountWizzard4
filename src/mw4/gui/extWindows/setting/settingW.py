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

    def initConfig(self) -> None:
        config = self.app.config.get("WindowSetting", {})
        self.positionWindow(config)
        self.app.colorChange.connect(self.colorChange)

    def storeConfig(self) -> None:
        configMain = self.app.config
        configMain["WindowSetting"] = {}
        config = configMain["WindowSetting"]
        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()

    def closeEvent(self, closeEvent) -> None:
        self.storeConfig()
        super().closeEvent(closeEvent)

    def colorChange(self) -> None:
        self.setStyleSheet(self.mw4Style)

    def showWindow(self) -> None:
        self.show()
        self.setMinimumSize(self.FULL_WIDTH, 450)
        self.setMaximumSize(self.FULL_WIDTH, 450)
        self.titleBar.normButton.setVisible(False)
        self.titleBar.maxButton.setVisible(False)
        self.titleBar.windowFixed = True
