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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
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

    as the mainW class is very big i have chosen to use mixins to extend the readability
    of the code and extend the mainW class by additional parent classes.

    SettParkPos handles all topics around setting und handling park positions for the mount
    and cover.
    """

    def __init__(self):
        # define lists for the gui entries
        self.posButtons = list()
        self.posTexts = list()
        self.posAlt = list()
        self.posAz = list()
        self.posSaveButtons = list()

        # dynamically generate the widgets
        self.setupParkPosGui()
        for posText in self.posTexts:
            posText.editingFinished.connect(self.updateParkPosButtonText)
        for button in self.posButtons:
            button.clicked.connect(self.slewToParkPos)
        for button in self.posSaveButtons:
            button.clicked.connect(self.saveActualPosition)

        # signals on gui
        self.ui.coverPark.clicked.connect(self.setCoverPark)
        self.ui.coverUnpark.clicked.connect(self.setCoverUnpark)
        self.ui.checkDomeGeometry.clicked.connect(self.toggleUseGeometry)

        # signals from functions
        self.app.update1s.connect(self.updateCoverStatGui)
        self.app.update1s.connect(self.updateDomeGeometry)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        self.ui.checkDomeGeometry.setChecked(config.get('checkDomeGeometry', False))
        self.toggleUseGeometry()

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
        config['checkDomeGeometry'] = self.ui.checkDomeGeometry.isChecked()

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
            else:
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
                if suc:
                    self.app.message.emit(f'Slew to [{posTextValue}]', 0)
                else:
                    self.app.message.emit(f'Cannot slew to [{posTextValue}]', 2)
                return suc

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

    def toggleUseGeometry(self):
        """
        toggleUseGeometry updates the mount class with the new setting if use geometry for
        dome calculation should be used or not.

        :return: true for test purpose
        """

        self.app.dome.isGeometry = self.ui.checkDomeGeometry.isChecked()
        return True

    def updateDomeGeometry(self):
        """
        updateDomeGeometry takes the information gathered from the driver and programs them
        into the mount class and gui for later use.

        :return: true for test purpose
        """

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_OTA_OFFSET', 0))
        self.app.mount.geometry.offPlateOTA = value
        self.ui.offOTA.setText(f'{value:3.2f}')

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_DOME_RADIUS', 0))
        self.app.mount.geometry.domeRadius = value
        self.ui.domeRadius.setText(f'{value:3.2f}')

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_NORTH_DISPLACEMENT', 0))
        self.app.mount.geometry.offNorth = value
        self.ui.domeNorthOffset.setText(f'{value:3.2f}')

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_EAST_DISPLACEMENT', 0))
        self.app.mount.geometry.offEast = value
        self.ui.domeEastOffset.setText(f'{value:3.2f}')

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_UP_DISPLACEMENT', 0))
        self.app.mount.geometry.offVert = value
        self.ui.domeVerticalOffset.setText(f'{value:3.2f}')

        return True

    def updateCoverStatGui(self):
        """
        updateCoverStatGui changes the style of the button related to the state of the
        FlipFlat cover

        :return: True for test purpose
        """

        value = self.app.cover.data.get('Status.Cover', '-').strip().upper()
        if value == 'OPEN':
            self.changeStyleDynamic(self.ui.coverUnpark, 'running', True)
        elif value == 'CLOSED':
            self.changeStyleDynamic(self.ui.coverPark, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.coverPark, 'running', False)
            self.changeStyleDynamic(self.ui.coverUnpark, 'running', False)

        value = self.app.cover.data.get('Status.Cover', '-')
        self.ui.coverStatusText.setText(value)

        value = self.app.cover.data.get('Status.Motor', '-')
        self.ui.coverMotorText.setText(value)

        return True

    def setCoverPark(self):
        """
        setCoverPark closes the cover

        :return: success
        """

        self.app.cover.sendCoverPark(park=True)
        return True

    def setCoverUnpark(self):
        """
        setCoverPark opens the cover

        :return: success
        """

        self.app.cover.sendCoverPark(park=False)
        return True
