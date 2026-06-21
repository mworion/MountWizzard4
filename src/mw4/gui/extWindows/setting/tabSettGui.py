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
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.qtHelpers import svg2pixmap
from typing import Any


class SettGui:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.ui.colorSet.currentIndexChanged.connect(self.updateColorSet)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingGui", {})
        colSet = config.get("colorSet", 0)
        self.ui.colorSet.setCurrentIndex(colSet)

    def storeConfig(self) -> None:
        self.app.config["SettingGui"] = {}
        config = self.app.config["SettingGui"]
        config["colorSet"] = self.ui.colorSet.currentIndex()

    def setupIcons(self) -> None:
        pixmap = svg2pixmap("assets/icon/controllerNew.svg", self.parentW.M_PRIM)
        self.ui.controllerOverview.setPixmap(pixmap)

    def updateColorSet(self) -> None:
        Styles.colorSet = self.ui.colorSet.currentIndex()
        self.parentW.setStyleSheet(self.parentW.mw4Style)
        self.setupIcons()
        self.app.colorChange.emit()
