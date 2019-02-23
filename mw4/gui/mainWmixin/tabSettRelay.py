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
        # define lists for the entries
        self.relayDropDownIndex = list()
        self.relayTexts = list()
        self.relayButtons = list()

        # dynamically generate the widgets
        self.setupRelayGui()

        # make the gui signals linked to slots
        self.ui.checkEnableRelay.clicked.connect(self.enableRelay)
        self.ui.relayHost.editingFinished.connect(self.relayHost)
        self.ui.relayUser.editingFinished.connect(self.relayUser)
        self.ui.relayPassword.editingFinished.connect(self.relayPassword)
        for relayText in self.relayTexts:
            relayText.editingFinished.connect(self.updateRelayButtonText)
        for button in self.relayButtons:
            button.clicked.connect(self.relayButtonPressed)

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
        for i, textField in enumerate(self.relayTexts):
            keyConfig = 'relay{0:1d}buttonText'.format(i)
            textField.setText(config.get(keyConfig, 'Relay {0:1d}'.format(i)))
        for i, index in enumerate(self.relayDropDownIndex):
            keyConfig = 'relay{0:1d}index'.format(i)
            index.setCurrentIndex(config.get(keyConfig, 0))
        self.updateRelayButtonText()
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['checkEnableRelay'] = self.ui.checkEnableRelay.isChecked()
        config['relayHost'] = self.ui.relayHost.text()
        config['relayUser'] = self.ui.relayUser.text()
        config['relayPassword'] = self.ui.relayPassword.text()
        for i, textField in enumerate(self.relayTexts):
            keyConfig = 'relay{0:1d}buttonText'.format(i)
            config[keyConfig] = textField.text()
        for i, index in enumerate(self.relayDropDownIndex):
            keyConfig = 'relay{0:1d}index'.format(i)
            config[keyConfig] = index.currentIndex()
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

        # generate the button list and text entry for later use
        for i in range(0, 8):
            self.relayButtons.append(eval('self.ui.relayButton{0:1d}'.format(i)))
            self.relayTexts.append(eval('self.ui.relayText{0:1d}'.format(i)))

        # dynamically generate the drop down menus and set the index
        for i in range(0, 8):
            self.relayDropDownIndex.append(eval('self.ui.relayFun{0:1d}'.format(i)))

        # and setting the entries of the drop down menus
        for dropDown in self.relayDropDownIndex:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('Switch - Toggle')
            dropDown.addItem('Pulse 0.5 sec')
        return True

    def updateRelayButtonText(self):
        """

        :return:
        """
        for button, textField in zip(self.relayButtons, self.relayTexts):
            button.setText(textField.text())

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

    def doRelayAction(self, relayIndex=0):
        """

        :param relayIndex: relayIndex according to pressed button
        :return: success
        """

        action = self.relayDropDownIndex[relayIndex].currentIndex()
        if action == 0:
            suc = self.app.relay.switch(relayIndex)
        elif action == 1:
            suc = self.app.relay.pulse(relayIndex)
        else:
            suc = False
        return suc

    def relayButtonPressed(self):
        """
        relayButtonPressed reads the button and starts the relay action on the box.

        :return: success for test
        """

        if not self.ui.checkEnableRelay.isChecked():
            self.app.message.emit('Relay box off', 2)
            return False
        suc = False
        for i, button in enumerate(self.relayButtons):
            if button != self.sender():
                continue
            self.doRelayAction(i)
        if not suc:
            self.app.message.emit('Relay action cannot be performed', 2)
            return False
        return True

    def relayHost(self):
        self.app.relay.host = self.ui.relayHost.text()

    def relayUser(self):
        self.app.relay.user = self.ui.relayUser.text()

    def relayPassword(self):
        self.app.relay.password = self.ui.relayPassword.text()
