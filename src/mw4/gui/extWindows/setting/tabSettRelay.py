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
        self.relayDropDowns = [
            self.ui.relayFun0,
            self.ui.relayFun1,
            self.ui.relayFun2,
            self.ui.relayFun3,
            self.ui.relayFun4,
            self.ui.relayFun5,
            self.ui.relayFun6,
            self.ui.relayFun7,
        ]
        self.relayButtonTexts = [
            self.ui.relayButtonText0,
            self.ui.relayButtonText1,
            self.ui.relayButtonText2,
            self.ui.relayButtonText3,
            self.ui.relayButtonText4,
            self.ui.relayButtonText5,
            self.ui.relayButtonText6,
            self.ui.relayButtonText7,
        ]
        self.setupRelayGui()

    def initConfig(self) -> None:
        config = self.app.config.get("SettingRelay", {})
        for i, button in enumerate(self.relayButtonTexts):
            button.setText(config.get(f"RelayText{i:1d}", "-"))
        for i, dropDown in enumerate(self.relayDropDowns):
            dropDown.setCurrentIndex(config.get(f"Action{i:1d}", 0))
        for button in self.relayButtonTexts:
            button.textChanged.connect(self.storeConfig)
        for dropdown in self.relayDropDowns:
            dropdown.currentIndexChanged.connect(self.storeConfig)
        self.app.relayChanged.emit()

    def storeConfig(self) -> None:
        self.app.config["SettingRelay"] = {}
        config = self.app.config["SettingRelay"]
        for i, button in enumerate(self.relayButtonTexts):
            config[f"RelayText{i:1d}"] = button.text()
        for i, dropDown in enumerate(self.relayDropDowns):
            config[f"Action{i:1d}"] = dropDown.currentIndex()
        self.app.relayChanged.emit()

    def setupRelayGui(self) -> None:
        for dropDown in self.relayDropDowns:
            dropDown.clear()
            dropDown.setView(QListView())
            dropDown.addItem("Switch - Toggle")
            dropDown.addItem("Pulse 0.5 sec")
