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
from PySide6.QtWidgets import QListView
from typing import Any


class SettRelay:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.relayDropDowns: list = []
        self.relayButtonTexts: list = []
        for i in range(8):
            self.relayDropDowns.append(getattr(self.ui, f"relayFun{i:1d}"))
            self.relayButtonTexts.append(getattr(self.ui, f"relayButtonText{i:1d}"))
        self.setupRelayGui()

    def initConfig(self) -> None:
        config = self.app.config.get("SettingRelay", {})
        for i in range(8):
            self.relayButtonTexts[i].setText(config.get(f"RelayText{i:1d}", "-"))
            self.relayDropDowns[i].setCurrentIndex(config.get(f"Action{i:1d}", 0))
            self.relayButtonTexts[i].textChanged.connect(self.storeConfig)
            self.relayDropDowns[i].currentIndexChanged.connect(self.storeConfig)
        self.app.relayChanged.emit()

    def storeConfig(self) -> None:
        self.app.config["SettingRelay"] = {}
        config = self.app.config["SettingRelay"]
        for i in range(8):
            config[f"RelayText{i:1d}"] = self.relayButtonTexts[i].text()
            config[f"Action{i:1d}"] = self.relayDropDowns[i].currentIndex()
        self.app.relayChanged.emit()

    def setupRelayGui(self) -> None:
        for dropDown in self.relayDropDowns:
            dropDown.clear()
            dropDown.setView(QListView())
            dropDown.addItem("Switch - Toggle")
            dropDown.addItem("Pulse 0.5 sec")
