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

# local import
from mountcontrol.convert import valueToFloat


class SettParkPos(object):
    """
    """

    def __init__(self):
        self.posButtons = list()
        self.posTexts = list()
        self.posAlt = list()
        self.posAz = list()
        self.posSaveButtons = list()

        for i in range(0, 10):
            self.posButtons.append(eval('self.ui.posButton{0:1d}'.format(i)))
            self.posTexts.append(eval('self.ui.posText{0:1d}'.format(i)))
            self.posAlt.append(eval('self.ui.posAlt{0:1d}'.format(i)))
            self.posAz.append(eval('self.ui.posAz{0:1d}'.format(i)))
            self.posSaveButtons.append(eval('self.ui.posSave{0:1d}'.format(i)))

        for posText in self.posTexts:
            posText.editingFinished.connect(self.updateParkPosButtonText)
        for button in self.posButtons:
            button.clicked.connect(self.slewToParkPos)
        for button in self.posSaveButtons:
            button.clicked.connect(self.saveActualPosition)

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for i, textField in enumerate(self.posTexts):
            keyConfig = f'posText{i:1d}'
            textField.setText(config.get(keyConfig, f'Park Pos {i:1d}'))
        for i, textField in enumerate(self.posAlt):
            keyConfig = f'posAlt{i:1d}'
            val = valueToFloat(config.get(keyConfig))
            if val:
                textField.setValue(val)
        for i, textField in enumerate(self.posAz):
            keyConfig = f'posAz{i:1d}'
            val = valueToFloat(config.get(keyConfig))
            if val:
                textField.setValue(val)
        self.updateParkPosButtonText()
        self.ui.parkMountAfterSlew.setChecked(config.get('parkMountAfterSlew', False))
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for i, textField in enumerate(self.posTexts):
            keyConfig = f'posText{i:1d}'
            config[keyConfig] = textField.text()
        for i, textField in enumerate(self.posAlt):
            keyConfig = f'posAlt{i:1d}'
            config[keyConfig] = textField.value()
        for i, textField in enumerate(self.posAz):
            keyConfig = f'posAz{i:1d}'
            config[keyConfig] = textField.value()
        config['parkMountAfterSlew'] = self.ui.parkMountAfterSlew.isChecked()
        return True

    def updateParkPosButtonText(self):
        """
        updateParkPosButtonText updates the text in the gui button if we change
        texts in the gui.

        :return: true for test purpose
        """
        for button, textField in zip(self.posButtons, self.posTexts):
            text = textField.text()
            button.setText(text)
            button.setEnabled(text.strip() != '')
        return True

    def parkAtPos(self):
        """
        :return:
        """
        self.app.mount.signals.slewFinished.disconnect(self.parkAtPos)
        suc = self.app.mount.obsSite.parkOnActualPosition()
        if not suc:
            self.msg.emit(2, 'Mount', 'Command',
                          'Cannot park at current position')
        return suc

    def slewToParkPos(self):
        """
        slewToParkPos takes the configured data from park positions menu and
        slews the mount to the targeted alt az coordinates and stops tracking.
        actually there is no chance to park the mount directly.

        :return: success
        """
        if self.sender() not in self.posButtons:
            return False

        index = self.posButtons.index(self.sender())
        altValue = self.posAlt[index].value()
        azValue = self.posAz[index].value()
        posTextValue = self.posTexts[index].text()

        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=altValue,
                                                    az_degrees=azValue)
        if not suc:
            self.msg.emit(2, 'Mount', 'Command error',
                          f'Cannot slew to [{posTextValue}]')
            return False

        suc = self.app.mount.obsSite.startSlewing(slewType='notrack')
        if not suc:
            self.msg.emit(2, 'Mount', 'Command error',
                          f'Cannot slew to [{posTextValue}]')
            return False

        self.msg.emit(0, 'Mount', 'Command', f'Slew to [{posTextValue}]')
        if not self.ui.parkMountAfterSlew.isChecked():
            return True

        self.app.mount.signals.slewFinished.connect(self.parkAtPos)
        return False

    def saveActualPosition(self):
        """
        saveActualPosition takes the actual mount position alt/az and stores it
        in the alt az fields in the gui for persistence.

        :return: success
        """
        obs = self.app.mount.obsSite
        if not obs.Alt:
            return False
        if not obs.Az:
            return False
        if self.sender() not in self.posSaveButtons:
            return False
        index = self.posSaveButtons.index(self.sender())
        self.posAlt[index].setValue(obs.Alt.degrees)
        self.posAz[index].setValue(obs.Az.degrees)
        return True
