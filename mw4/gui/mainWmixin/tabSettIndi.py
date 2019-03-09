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

    def initConfig(self):
        config = self.app.config['mainW']

        self.ui.environHost.setText(config.get('environHost', ''))
        self.ui.environName.setText(config.get('environName', ''))
        self.ui.imagingHost.setText(config.get('imagingHost', ''))
        self.ui.imagingName.setText(config.get('imagingName', ''))
        self.ui.domeHost.setText(config.get('domeHost', ''))
        self.ui.domeName.setText(config.get('domeName', ''))
        self.ui.indiMessage.setChecked(config.get('indiMessage', False))

        return True

    def storeConfig(self):
        config = self.app.config['mainW']

        config['environHost'] = self.ui.environHost.text()
        config['environName'] = self.ui.environName.text()
        config['imagingHost'] = self.ui.imagingHost.text()
        config['imagingName'] = self.ui.imagingName.text()
        config['domeHost'] = self.ui.domeHost.text()
        config['domeName'] = self.ui.domeName.text()
        config['indiMessage'] = self.ui.indiMessage.isChecked()

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
