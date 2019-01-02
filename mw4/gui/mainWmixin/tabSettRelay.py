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
# local import


class SettRelay(object):
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
        self.ui.checkEnableRelay.clicked.connect(self.enableRelay)
        self.ui.relayHost.editingFinished.connect(self.relayHost)
        self.ui.relayUser.editingFinished.connect(self.relayUser)
        self.ui.relayPassword.editingFinished.connect(self.relayPassword)
        for button in self.relayButton:
            button.clicked.connect(self.toggleRelay)

    def initConfig(self):
        config = self.app.config['mainW']
        self.ui.checkEnableRelay.setChecked(config.get('checkEnableRelay', False))
        self.enableRelay()
        self.ui.relayHost.setText(config.get('relayHost', ''))
        self.relayHost()
        self.ui.relayUser.setText(config.get('relayUser', ''))
        self.relayUser()
        self.ui.relayPassword.setText(config.get('relayPassword', ''))
        self.relayPassword()
        for i, line in enumerate(self.relayText):
            key = 'relayText{0:1d}'.format(i)
            line.setText(config.get(key, 'Relay{0:1d}'.format(i)))
        for i, button in enumerate(self.relayButton):
            key = 'relayText{0:1d}'.format(i)
            button.setText(config.get(key, 'Relay{0:1d}'.format(i)))
        for i, drop in enumerate(self.relayDropDown):
            key = 'relayFun{0:1d}'.format(i)
            drop.setCurrentIndex(config.get(key, 0))
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['checkEnableRelay'] = self.ui.checkEnableRelay.isChecked()
        config['relayHost'] = self.ui.relayHost.text()
        config['relayUser'] = self.ui.relayUser.text()
        config['relayPassword'] = self.ui.relayPassword.text()
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

    def setupRelayGui(self):
        """
        setupRelayGui handles the modeldata of list for relay handling. to keep many relay in
        order i collect them in the list for list handling afterwards.

        :return: success for test
        """

        print('setupRelaisGui')
        for i in range(0, 8):
            self.relayDropDown.append(eval('self.ui.relayFun{0:1d}'.format(i)))
            self.relayButton.append(eval('self.ui.relayButton{0:1d}'.format(i)))
            self.relayText.append(eval('self.ui.relayText{0:1d}'.format(i)))
        # and setting the entries of the drop down menus
        for dropDown in self.relayDropDown:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('Switch - Toggle')
            dropDown.addItem('Pulse 0.5 sec')
        return True

    def enableRelay(self):
        """
        enableRelay allows to run the relay box.

        :return: success for test
        """

        # get index for relay tab
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Relay')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)

        if self.ui.checkEnableRelay.isChecked():
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            self.app.message.emit('Relay enabled', 0)
            self.app.relay.startTimers()
        else:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            self.app.message.emit('Relay disabled', 0)
            self.app.relay.stopTimers()
        # update the style for showing the Relay tab
        self.ui.mainTabWidget.style().unpolish(self.ui.mainTabWidget)
        self.ui.mainTabWidget.style().polish(self.ui.mainTabWidget)
        return True

    def relayHost(self):
        self.app.relay.host = self.ui.relayHost.text()

    def relayUser(self):
        self.app.relay.user = self.ui.relayUser.text()

    def relayPassword(self):
        self.app.relay.password = self.ui.relayPassword.text()
