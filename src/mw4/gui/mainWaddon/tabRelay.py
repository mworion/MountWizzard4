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
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.qtHelpers import changeStyleDynamic
from typing import Any


class Relay(TabAddon):
    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.relayButtons = [
            self.ui.relayButton0,
            self.ui.relayButton1,
            self.ui.relayButton2,
            self.ui.relayButton3,
            self.ui.relayButton4,
            self.ui.relayButton5,
            self.ui.relayButton6,
            self.ui.relayButton7,
        ]
        self.app.dReg["relay"].signals.statusReady.connect(self.updateRelayGui)
        self.app.relayChanged.connect(self.updateRelayButtonText)

    def updateRelayButtonText(self) -> None:
        config = self.app.config.get("SettingRelay", {})
        for i, button in enumerate(self.relayButtons):
            button.setText(config.get(f"RelayText{i:1d}", "-"))
            action = config.get(f"Action{i:1d}", 0)
            icon = "cogs" if action else "flip"
            self.mainW.wIcon(button, icon)

    def doRelayAction(self, relayIndex: int) -> bool:
        cfg = self.app.config.get("SettingRelay", {})
        action = cfg.get(f"Action{relayIndex:1d}", 0)
        if action == 0:
            return self.app.relay.switch(relayIndex)
        else:
            return self.app.relay.pulse(relayIndex)

    def relayButtonPressed(self, buttonIndex: int) -> None:
        if not self.doRelayAction(buttonIndex):
            self.msg.emit(2, "System", "Relay", "Action cannot be done")

    def updateRelayGui(self) -> None:
        for status, button in zip(self.app.relay.status, self.relayButtons):
            if status:
                changeStyleDynamic(button, "run", True)
            else:
                changeStyleDynamic(button, "run", False)
