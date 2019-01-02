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


class INDI(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.ui.indiHost.editingFinished.connect(self.indiHost)
        self.ui.localWeatherName.editingFinished.connect(self.localWeatherName)
        self.ui.globalWeatherName.editingFinished.connect(self.globalWeatherName)
        self.ui.sqmName.editingFinished.connect(self.sqmName)
        self.ui.reconnectIndiServer.clicked.connect(self.app.environment.reconnectIndiServer)

    def initConfig(self):
        config = self.app.config['mainW']
        environ = self.app.environment
        self.ui.indiHost.setText(config.get('indiHost', ''))
        environ.client.host = config.get('indiHost', '')
        self.ui.globalWeatherName.setText(config.get('globalWeatherName', ''))
        environ.globalWeatherName = config.get('globalWeatherName', '')
        self.ui.localWeatherName.setText(config.get('localWeatherName', ''))
        environ.localWeatherName = config.get('localWeatherName', '')
        self.ui.sqmName.setText(config.get('sqmName', ''))
        environ.sqmName = config.get('sqmName', '')
        self.ui.ccdName.setText(config.get('ccdName', ''))
        self.ui.domeName.setText(config.get('domeName', ''))

        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['indiHost'] = self.ui.indiHost.text()
        config['localWeatherName'] = self.ui.localWeatherName.text()
        config['globalWeatherName'] = self.ui.globalWeatherName.text()
        config['sqmName'] = self.ui.sqmName.text()
        config['domeName'] = self.ui.domeName.text()
        config['ccdName'] = self.ui.ccdName.text()

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

    def indiHost(self):
        host = self.ui.indiHost.text()
        self.app.environment.client.host = host

    def localWeatherName(self):
        environ = self.app.environment
        environ.localWeatherName = self.ui.localWeatherName.text()

    def globalWeatherName(self):
        environ = self.app.environment
        environ.globalWeatherName = self.ui.globalWeatherName.text()

    def sqmName(self):
        environ = self.app.environment
        environ.sqmName = self.ui.sqmName.text()
