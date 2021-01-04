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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import


class SettParkPos(object):
    """
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

        self.posButtons = list()
        self.posTexts = list()
        self.posAlt = list()
        self.posAz = list()
        self.posSaveButtons = list()

        self.setupParkPosGui()
        for posText in self.posTexts:
            posText.editingFinished.connect(self.updateParkPosButtonText)
        for button in self.posButtons:
            button.clicked.connect(self.slewToParkPos)
        for button in self.posSaveButtons:
            button.clicked.connect(self.saveActualPosition)

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
        self.ui.parkMountAfterSlew.setChecked(config.get('parkMountAfterSlew', False))

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
        config['parkMountAfterSlew'] = self.ui.parkMountAfterSlew.isChecked()

        return True

    def setupParkPosGui(self):
        """
        setupRelayGui handles the modeldata of list for relay handling. to keep many relay in
        order i collect them in the list for list handling afterwards.

        :return: True for test purpose
        """
        # generate the button list and text entry for later use
        for i in range(0, 10):
            self.posButtons.append(eval('self.ui.posButton{0:1d}'.format(i)))
            self.posTexts.append(eval('self.ui.posText{0:1d}'.format(i)))
            self.posAlt.append(eval('self.ui.posAlt{0:1d}'.format(i)))
            self.posAz.append(eval('self.ui.posAz{0:1d}'.format(i)))
            self.posSaveButtons.append(eval('self.ui.posSave{0:1d}'.format(i)))

        return True

    def updateParkPosButtonText(self):
        """
        updateParkPosButtonText updates the text in the gui button if we change texts in
        the gui.

        :return: true for test purpose
        """

        for button, textField in zip(self.posButtons, self.posTexts):
            button.setText(textField.text())

        return True

    def parkAtPos(self):
        """
        :return:
        """
        self.app.mount.signals.slewFinished.disconnect(self.parkAtPos)
        suc = self.app.mount.obsSite.parkOnActualPosition()

        if not suc:
            self.app.message.emit('Cannot park at current position', 2)

        return suc

    def slewToParkPos(self):
        """
        slewToParkPos takes the configured data from park positions menu and slews the mount
        to the targeted alt az coordinates and stops tracking. actually there is no chance to
        park the mount directly.

        :return: success
        """

        for button, posText, alt, az in zip(self.posButtons,
                                            self.posTexts,
                                            self.posAlt,
                                            self.posAz,
                                            ):

            if button != self.sender():
                continue

            try:
                altValue = float(alt.text())
                azValue = float(az.text())

            except Exception as e:
                self.log.critical(f'no usable values in data: error {e}')
                self.app.message.emit('Missing correct entries in settings', 2)
                return False

            posTextValue = posText.text()

            if altValue < -5:
                altValue = -5
            elif altValue > 90:
                altValue = 90
            azValue = azValue % 360

            suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=altValue,
                                                        az_degrees=azValue)

            if suc:
                suc = self.app.mount.obsSite.startSlewing(slewType='notrack')

            if not suc:
                self.app.message.emit(f'Cannot slew to [{posTextValue}]', 2)
                return False

            self.app.message.emit(f'Slew to [{posTextValue}]', 0)

            if not self.ui.parkMountAfterSlew.isChecked():
                return True

            self.app.mount.signals.slewFinished.connect(self.parkAtPos)

            return True

        return False

    def saveActualPosition(self):
        """
        saveActualPosition takes the actual mount position alt/az and stores it in the alt az
        fields in the gui for persistence.

        :return: success
        """

        obs = self.app.mount.obsSite

        if not obs.Alt:
            return False
        if not obs.Az:
            return False

        for button, alt, az in zip(self.posSaveButtons,
                                   self.posAlt,
                                   self.posAz,
                                   ):

            if button != self.sender():
                continue

            alt.setText(f'{obs.Alt.degrees:3.0f}')
            az.setText(f'{obs.Az.degrees:3.0f}')

        return True
