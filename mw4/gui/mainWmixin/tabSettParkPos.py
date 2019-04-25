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


class SettParkPos(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        # define lists for the entries
        self.posButtons = list()
        self.posTexts = list()
        self.posAlt = list()
        self.posAz = list()

        # dynamically generate the widgets
        self.setupParkPosGui()
        for posText in self.posTexts:
            posText.editingFinished.connect(self.updateParkPosButtonText)
        for button in self.posButtons:
            button.clicked.connect(self.slewToParkPos)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for i, textField in enumerate(self.posTexts):
            keyConfig = 'posText{0:1d}'.format(i)
            textField.setText(config.get(keyConfig, 'Park Pos {0:1d}'.format(i)))
        for i, textField in enumerate(self.posAlt):
            keyConfig = 'posAlt{0:1d}'.format(i)
            textField.setText(config.get(keyConfig, '-'))
        for i, textField in enumerate(self.posAz):
            keyConfig = 'posAz{0:1d}'.format(i)
            textField.setText(config.get(keyConfig, '-'))
        self.updateParkPosButtonText()
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for i, textField in enumerate(self.posTexts):
            keyConfig = 'posText{0:1d}'.format(i)
            config[keyConfig] = textField.text()
        for i, textField in enumerate(self.posAlt):
            keyConfig = 'posAlt{0:1d}'.format(i)
            config[keyConfig] = textField.text()
        for i, textField in enumerate(self.posAz):
            keyConfig = 'posAz{0:1d}'.format(i)
            config[keyConfig] = textField.text()
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        return True

    def setupParkPosGui(self):
        """
        setupRelayGui handles the modeldata of list for relay handling. to keep many relay in
        order i collect them in the list for list handling afterwards.

        :return: success for test
        """

        # generate the button list and text entry for later use
        for i in range(0, 8):
            self.posButtons.append(eval('self.ui.posButton{0:1d}'.format(i)))
            self.posTexts.append(eval('self.ui.posText{0:1d}'.format(i)))
            self.posAlt.append(eval('self.ui.posAlt{0:1d}'.format(i)))
            self.posAz.append(eval('self.ui.posAz{0:1d}'.format(i)))
        return True

    def updateParkPosButtonText(self):
        for button, textField in zip(self.posButtons, self.posTexts):
            button.setText(textField.text())

    def slewToParkPos(self):
        for button, posText, alt, az in zip(self.posButtons,
                                            self.posTexts,
                                            self.posAlt,
                                            self.posAz,
                                            ):
            if button == self.sender():
                altValue = float(alt.text())
                azValue = float(az.text())
                posTextValue = posText.text()
                suc = self.app.mount.obsSite.slewAltAz(alt_degrees=altValue,
                                                       az_degrees=azValue,
                                                       slewType='normal')
                if suc:
                    self.app.message.emit('Slew to [{0}]'.format(posTextValue), 0)
                else:
                    self.app.message.emit('Cannot slew to [{0}]'.format(posTextValue), 2)
                return suc
        return False
