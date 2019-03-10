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


class SettIndi(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.app.environ.client.signals.newMessage.connect(self.indiMessage)

        sig = self.app.environ.client.signals
        sig.serverConnected.connect(self.showIndiEnvironConnected)
        sig.serverDisconnected.connect(self.showIndiEnvironDisconnected)
        sig.deviceConnected.connect(self.showEnvironDeviceConnected)
        sig.deviceDisconnected.connect(self.showEnvironDeviceDisconnected)
        sig.newDevice.connect(self.showIndiNewEnvironDevice)
        sig.removeDevice.connect(self.showIndiRemoveEnvironDevice)

    def initConfig(self):
        config = self.app.config['mainW']

        self.ui.environHost.setText(config.get('environHost', ''))
        self.ui.environPort.setText(config.get('environPort', '7624'))
        self.ui.environName.setText(config.get('environName', ''))
        self.ui.imagingHost.setText(config.get('imagingHost', ''))
        self.ui.imagingPort.setText(config.get('imagingPort', '7624'))
        self.ui.imagingName.setText(config.get('imagingName', ''))
        self.ui.domeHost.setText(config.get('domeHost', ''))
        self.ui.domePort.setText(config.get('domePort', '7624'))
        self.ui.domeName.setText(config.get('domeName', ''))
        self.ui.skymeterHost.setText(config.get('skymeterHost', ''))
        self.ui.skymeterPort.setText(config.get('skymeterPort', '7624'))
        self.ui.skymeterName.setText(config.get('skymeterName', ''))
        self.ui.indiMessage.setChecked(config.get('indiMessage', False))

        return True

    def storeConfig(self):
        config = self.app.config['mainW']

        config['environHost'] = self.ui.environHost.text()
        config['environPort'] = self.ui.environPort.text()
        config['environName'] = self.ui.environName.text()
        config['imagingHost'] = self.ui.imagingHost.text()
        config['imagingPort'] = self.ui.imagingPort.text()
        config['imagingName'] = self.ui.imagingName.text()
        config['domeHost'] = self.ui.domeHost.text()
        config['domePort'] = self.ui.domePort.text()
        config['domeName'] = self.ui.domeName.text()
        config['skymeterHost'] = self.ui.skymeterHost.text()
        config['skymeterPort'] = self.ui.skymeterPort.text()
        config['skymeterName'] = self.ui.skymeterName.text()
        config['indiMessage'] = self.ui.indiMessage.isChecked()

        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        return True

    def clearGUI(self):
        """
        clearGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        return True

    @staticmethod
    def _removePrefix(text, prefix):
        value = text[text.startswith(prefix) and len(prefix):]
        value = value.strip()
        return value

    def indiMessage(self, device, text):
        """
        indiMessage take a message send by indi device and puts them in the user message
        window as well.

        :param device: device name
        :param text: message received
        :return: success
        """
        if self.ui.indiMessage.isChecked():
            if text.startswith('[WARNING]'):
                text = self._removePrefix(text, '[WARNING]')
                self.app.message.emit(device + ' -> ' + text, 0)
            elif text.startswith('[ERROR]'):
                text = self._removePrefix(text, '[ERROR]')
                self.app.message.emit(device + ' -> ' + text, 2)
            else:
                self.app.message.emit(device + ' -> ' + text, 0)
            return True
        return False

    def showIndiEnvironConnected(self):
        """
        showIndiEnvironConnected writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit('INDI server environment connected', 0)
        return True

    def showIndiEnvironDisconnected(self):
        """
        showIndiEnvironDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.environDevice.setStyleSheet(self.BACK_NORM)
        self.app.message.emit('INDI server environment disconnected', 0)
        return True

    def showIndiNewEnvironDevice(self, deviceName):
        """
        showIndiNewEnvironDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI environment device [{deviceName}] found', 0)
        return True

    def showIndiRemoveEnvironDevice(self, deviceName):
        """
        showIndiRemoveEnvironDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI environment device [{deviceName}] removed', 0)
        return True

    def showEnvironDeviceConnected(self):
        """
        showEnvironDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.environDevice.setStyleSheet(self.BACK_GREEN)
        self.changeStyleDynamic(self.ui.environConnected, 'color', 'green')
        self.ui.environGroup.setEnabled(True)
        self.ui.refractionGroup.setEnabled(True)
        self.ui.setRefractionManual.setEnabled(True)
        return True

    def showEnvironDeviceDisconnected(self):
        """
        showEnvironDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.environDevice.setStyleSheet(self.BACK_NORM)
        self.changeStyleDynamic(self.ui.environConnected, 'color', 'red')
        self.ui.environGroup.setEnabled(False)
        self.ui.refractionGroup.setEnabled(False)
        self.ui.setRefractionManual.setEnabled(False)
        return True
