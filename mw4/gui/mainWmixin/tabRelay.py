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
# GUI with PyQT5 for python
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
# local import


class Relay(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.relayDropDown = list()
        self.relayButton = list()
        self.relayText = list()
        self.setupRelayGui()

        ms = self.app.mount.signals
        ms.namesDone.connect(self.setNameList)
        self.app.relay.statusReady.connect(self.updateRelayGui)

    def initConfig(self):
        config = self.app.config['mainW']
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        return True

    def clearMountGUI(self):
        """
        clearMountGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        return True

    def toggleRelay(self):
        """
        toggleRelay reads the button and toggles the relay on the box.

        :return: success for test
        """

        if not self.ui.checkEnableRelay.isChecked():
            self.app.message.emit('Relay box off', 2)
            return False
        suc = False
        for i, button in enumerate(self.relayButton):
            if button != self.sender():
                continue
            suc = self.app.relay.switch(i)
        if not suc:
            self.app.message.emit('Relay cannot be switched', 2)
            return False
        self.app.relay.cyclePolling()
        return True

    def updateRelayGui(self):
        """
        updateRelayGui changes the style of the button related to the state of the relay

        :return: success for test
        """

        status = self.app.relay.status
        for i, button in enumerate(self.relayButton):
            if status[i]:
                self.changeStyleDynamic(button, 'running', 'true')
            else:
                self.changeStyleDynamic(button, 'running', 'false')
        return True
