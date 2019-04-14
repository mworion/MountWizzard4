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
import PyQt5
# local import


class Tools(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        pass

    def initConfig(self):
        config = self.app.config['mainW']
        self.ui.renameInput.setText(config.get('renameInput', ''))
        self.ui.renameOutput.setText(config.get('renameOutput', ''))
        self.ui.renameProgress.setValue(0)
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['renameInput'] = self.ui.renameInput.text()
        config['renameOutput'] = self.ui.renameOutput.text()
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """

        self.wIcon(self.ui.renameStart, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.renameCancel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)

        return True

    def clearGUI(self):
        """
        clearGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        return True

