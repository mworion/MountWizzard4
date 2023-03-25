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
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets

# local import


class SettRelay(object):
    """
    """

    def __init__(self):
        # define lists for the entries
        self.relayDropDowns = [self.ui.relayFun0,
                               self.ui.relayFun1,
                               self.ui.relayFun2,
                               self.ui.relayFun3,
                               self.ui.relayFun4,
                               self.ui.relayFun5,
                               self.ui.relayFun6,
                               self.ui.relayFun7,
                               ]
        self.relayDropDownKeys = ['relay0index',
                                  'relay1index',
                                  'relay2index',
                                  'relay3index',
                                  'relay4index',
                                  'relay5index',
                                  'relay6index',
                                  'relay7index',
                                  ]
        self.relayButtons = [self.ui.relayButton0,
                             self.ui.relayButton1,
                             self.ui.relayButton2,
                             self.ui.relayButton3,
                             self.ui.relayButton4,
                             self.ui.relayButton5,
                             self.ui.relayButton6,
                             self.ui.relayButton7,
                             ]
        self.relayButtonTexts = [self.ui.relayButtonText0,
                                 self.ui.relayButtonText1,
                                 self.ui.relayButtonText2,
                                 self.ui.relayButtonText3,
                                 self.ui.relayButtonText4,
                                 self.ui.relayButtonText5,
                                 self.ui.relayButtonText6,
                                 self.ui.relayButtonText7,
                                 ]
        self.relayButtonTextKeys = ['relay0buttonText',
                                    'relay1buttonText',
                                    'relay2buttonText',
                                    'relay3buttonText',
                                    'relay4buttonText',
                                    'relay5buttonText',
                                    'relay6buttonText',
                                    'relay7buttonText',
                                    ]

        # dynamically generate the widgets
        self.setupRelayGui()

        # make the gui signals linked to slots
        for relayButtonText in self.relayButtonTexts:
            relayButtonText.editingFinished.connect(self.updateRelayButtonText)
        for button in self.relayButtons:
            button.clicked.connect(self.relayButtonPressed)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for button, key in zip(self.relayButtonTexts, self.relayButtonTextKeys):
            button.setText(config.get(key, ''))
        for dropDown, key in zip(self.relayDropDowns, self.relayDropDownKeys):
            dropDown.setCurrentIndex(config.get(key, 0))
        self.updateRelayButtonText()
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for button, key in zip(self.relayButtonTexts, self.relayButtonTextKeys):
            config[key] = button.text()
        for dropDown, key in zip(self.relayDropDowns, self.relayDropDownKeys):
            config[key] = dropDown.currentIndex()
        return True

    def setupRelayGui(self):
        """
        setupRelayGui handles the modeldata of list for relay handling.

        :return: success for test
        """

        for dropDown in self.relayDropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('Switch - Toggle')
            dropDown.addItem('Pulse 0.5 sec')
        return True

    def updateRelayButtonText(self):
        """

        :return:
        """
        for button, textField in zip(self.relayButtons, self.relayButtonTexts):
            button.setText(textField.text())

    def doRelayAction(self, relayIndex=0):
        """

        :param relayIndex: relayIndex according to pressed button
        :return: success
        """

        action = self.relayDropDowns[relayIndex].currentIndex()
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

        suc = False
        for i, button in enumerate(self.relayButtons):
            if button != self.sender():
                continue
            suc = self.doRelayAction(i)
        if not suc:
            self.msg.emit(2, 'System', 'Relay', 'Action cannot be done')
            return False
        return True
