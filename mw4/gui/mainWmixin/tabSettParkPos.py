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
# Python  v3.7.4
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
    """

    def __init__(self):
        # define lists for the entries
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
        self.ui.offOTA.valueChanged.connect(self.adjustGEMOffset)
        self.ui.offGEM.valueChanged.connect(self.adjustOTAOffset)
        self.ui.domeDiameter.valueChanged.connect(self.setDomeDiameter)
        self.ui.domeNorthOffset.valueChanged.connect(self.setDomeNorthOffset)
        self.ui.domeEastOffset.valueChanged.connect(self.setDomeEastOffset)
        self.ui.domeVerticalOffset.valueChanged.connect(self.setDomeVerticalOffset)

        # signals from functions
        self.app.mount.signals.firmwareDone.connect(self.adjustOTAOffset)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.checkDomeGeometry.setChecked(config.get('checkDomeGeometry', False))
        self.ui.domeDiameter.setValue(config.get('domeDiameter', 3))
        self.ui.domeNorthOffset.setValue(config.get('domeNorthOffset', 0))
        self.ui.domeEastOffset.setValue(config.get('domeEastOffset', 0))
        self.ui.domeVerticalOffset.setValue(config.get('domeVerticalOffset', 0))
        self.ui.offOTA.setValue(config.get('offOTA', 0))
        self.ui.offGEM.setValue(config.get('offGEM', 0))

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
        config['domeDiameter'] = self.ui.domeDiameter.value()
        config['domeNorthOffset'] = self.ui.domeNorthOffset.value()
        config['domeEastOffset'] = self.ui.domeEastOffset.value()
        config['domeVerticalOffset'] = self.ui.domeVerticalOffset.value()
        config['offOTA'] = self.ui.offOTA.value()
        config['offGEM'] = self.ui.offGEM.value()

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

        :return: success for test
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
        updateParkPosButtonText updates the text in the gui button

        :return: true for test purpose
        """

        for button, textField in zip(self.posButtons, self.posTexts):
            button.setText(textField.text())

        return True

    def slewToParkPos(self):
        """
        slewToParkPos takes the configured data from menu and slews the mount to the
        targeted alt az coordinates.

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
                posTextValue = posText.text()
            except Exception as e:
                self.logger.error(f'no usable values in data: error {e}')
                self.app.message.emit('Missing correct entries in settings', 2)
            else:
                suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=altValue,
                                                            az_degrees=azValue)
                if suc:
                    suc = self.app.mount.obsSite.startSlewing()
                if suc:
                    self.app.message.emit(f'Slew to [{posTextValue}]', 0)
                else:
                    self.app.message.emit(f'Cannot slew to [{posTextValue}]', 2)
                return suc

        return False

    def saveActualPosition(self):
        """
        saveActualPosition takes the actual mount position and stores it in the alt az fields

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

    def adjustGEMOffset(self):
        """

        :return: true for test purpose
        """

        self.app.mount.geometry.offPlateOTA = self.ui.offOTA.value()
        self.ui.offGEM.setValue(self.app.mount.geometry.offGEM)
        return True

    def adjustOTAOffset(self):
        """

        :return: true for test purpose
        """

        value = self.ui.offGEM.value()
        value = max(value, self.app.mount.geometry.offGemPlate)
        self.ui.offGEM.setValue(value)
        self.app.mount.geometry.offGEM = value
        self.ui.offOTA.setValue(self.app.mount.geometry.offPlateOTA)
        return True

    def setDomeDiameter(self):
        """

        :return: true for test purpose
        """

        self.app.mount.geometry.domeRadius = self.ui.domeDiameter.value() / 2
        return True

    def setDomeNorthOffset(self):
        """

        :return: true for test purpose
        """

        self.app.mount.geometry.offNorth = self.ui.domeNorthOffset.value()
        return True

    def setDomeEastOffset(self):
        """

        :return: true for test purpose
        """

        self.app.mount.geometry.offEast = self.ui.domeEastOffset.value()
        return True

    def setDomeVerticalOffset(self):
        """

        :return: true for test purpose
        """

        self.app.mount.geometry.offVert = self.ui.domeVerticalOffset.value()
        return True
