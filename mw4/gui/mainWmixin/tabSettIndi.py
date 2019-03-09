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

        host = config.get('environHost', '')
        self.app.environ.client.host = host
        self.ui.environHost.setText(host)

        name = config.get('environName', '')
        self.app.environ.name = name
        self.ui.environName.setText(name)
        self.ui.environMessage.setChecked(config.get('environMessage', False))

        host = config.get('imagingHost', '')
        self.ui.imagingHost.setText(host)

        name = config.get('imagingName', '')
        self.ui.imagingName.setText(name)
        self.ui.imagingMessage.setChecked(config.get('imagingMessage', False))

        host = config.get('domeHost', '')
        self.ui.domeHost.setText(host)

        name = config.get('domeName', '')
        self.ui.domeName.setText(name)
        self.ui.domeMessage.setChecked(config.get('domeMessage', False))

        return True

    def storeConfig(self):
        config = self.app.config['mainW']

        config['environHost'] = self.ui.environHost.text()
        config['environName'] = self.ui.environName.text()
        config['environMessage'] = self.ui.environMessage.isChecked()

        config['imagingHost'] = self.ui.imagingHost.text()
        config['imagingName'] = self.ui.imagingName.text()
        config['imagingMessage'] = self.ui.imagingMessage.isChecked()

        config['domeHost'] = self.ui.domeHost.text()
        config['domeName'] = self.ui.domeName.text()
        config['domeMessage'] = self.ui.domeMessage.isChecked()

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
    def _remove_prefix(text, prefix):
        return text[text.startswith(prefix) and len(prefix):]

    def indiMessage(self, device, text):
        """

        :param device:
        :param text:
        :return:
        """
        if self.ui.environMessage.isChecked():
            if text.startswith('[WARNING]'):
                text = self._remove_prefix(text, '[WARNING]')
                self.app.message.emit(device + ' -> ' + text, 0)
            elif text.startswith('[ERROR]'):
                text = self._remove_prefix(text, '[ERROR]')
                self.app.message.emit(device + ' -> ' + text, 2)
            else:
                self.app.message.emit(device + ' -> ' + text, 0)
