############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries


# external packages
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QListView
from functools import partial

# local import
from gui.utilities.toolsQtWidget import changeStyleDynamic


class SettRelay(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = self.app.msg
        self.ui = mainW.ui

        # define lists for the entries
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
        self.relayDropDownKeys = [
            "relay0index",
            "relay1index",
            "relay2index",
            "relay3index",
            "relay4index",
            "relay5index",
            "relay6index",
            "relay7index",
        ]
        self.relayButtons = {
            0: self.ui.relayButton0,
            1: self.ui.relayButton1,
            2: self.ui.relayButton2,
            3: self.ui.relayButton3,
            4: self.ui.relayButton4,
            5: self.ui.relayButton5,
            6: self.ui.relayButton6,
            7: self.ui.relayButton7,
        }
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
        self.relayButtonTextKeys = [
            "relay0buttonText",
            "relay1buttonText",
            "relay2buttonText",
            "relay3buttonText",
            "relay4buttonText",
            "relay5buttonText",
            "relay6buttonText",
            "relay7buttonText",
        ]

        # dynamically generate the widgets
        self.setupRelayGui()
        self.app.relay.signals.statusReady.connect(self.updateRelayGui)

        # make the gui signals linked to slots
        for relayButtonText in self.relayButtonTexts:
            relayButtonText.editingFinished.connect(self.updateRelayButtonText)
        for button in self.relayButtons:
            self.relayButtons[button].clicked.connect(partial(self.relayButtonPressed, button))

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        for button, key in zip(self.relayButtonTexts, self.relayButtonTextKeys):
            button.setText(config.get(key, ""))
        for dropDown, key in zip(self.relayDropDowns, self.relayDropDownKeys):
            dropDown.setCurrentIndex(config.get(key, 0))
        self.updateRelayButtonText()

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        for button, key in zip(self.relayButtonTexts, self.relayButtonTextKeys):
            config[key] = button.text()
        for dropDown, key in zip(self.relayDropDowns, self.relayDropDownKeys):
            config[key] = dropDown.currentIndex()

    def setupRelayGui(self) -> None:
        """ " """
        for dropDown in self.relayDropDowns:
            dropDown.clear()
            dropDown.setView(QListView())
            dropDown.addItem("Switch - Toggle")
            dropDown.addItem("Pulse 0.5 sec")

    def updateRelayButtonText(self) -> None:
        """ """
        for button, textField in zip(self.relayButtons.values(), self.relayButtonTexts):
            button.setText(textField.text())

    def doRelayAction(self, relayIndex: int) -> bool:
        """ """
        action = self.relayDropDowns[relayIndex].currentIndex()
        if action == 0:
            return self.app.relay.switch(relayIndex)
        else:
            return self.app.relay.pulse(relayIndex)

    def relayButtonPressed(self, buttonIndex: int) -> None:
        """ """
        if not self.doRelayAction(buttonIndex):
            self.msg.emit(2, "System", "Relay", "Action cannot be done")

    def updateRelayGui(self) -> None:
        """ """
        for status, button in zip(self.app.relay.status, self.relayButtons.values()):
            if status:
                changeStyleDynamic(button, "running", True)
            else:
                changeStyleDynamic(button, "running", False)
