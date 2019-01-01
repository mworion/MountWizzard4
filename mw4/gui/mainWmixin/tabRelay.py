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
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
import numpy as np
import matplotlib.pyplot
# local import
from mw4.gui import widget
from mw4.gui.widgets import main_ui
from mw4.base import transform


class Relay(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def local__init__(self):
        self.setupRelayGui()
        self.app.relay.statusReady.connect(self.updateRelayGui)
        self.enableRelay()

    def initConfig(self):
        if 'mainW' not in self.app.config:
            return False
        config = self.app.config['mainW']
        for button in self.relayButton:
            button.clicked.connect(self.toggleRelay)
        for i, button in enumerate(self.relayButton):
            key = 'relayText{0:1d}'.format(i)
            button.setText(config.get(key, 'Relay{0:1d}'.format(i)))
        for i, drop in enumerate(self.relayDropDown):
            key = 'relayFun{0:1d}'.format(i)
            drop.setCurrentIndex(config.get(key, 0))
        return True

    def storeConfig(self):
        if 'mainW' not in self.app.config:
            self.app.config['mainW'] = {}
        config = self.app.config['mainW']
        for i, line in enumerate(self.relayText):
            key = 'relayText{0:1d}'.format(i)
            config[key] = line.text()
        for i, drop in enumerate(self.relayDropDown):
            key = 'relayFun{0:1d}'.format(i)
            config[key] = drop.currentIndex()

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
