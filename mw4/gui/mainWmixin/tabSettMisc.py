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
import logging
# external packages
# local import


class SettMisc(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelInfo.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelWarning.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelError.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebugIB.clicked.connect(self.setLoggingLevelIB)
        self.ui.loglevelInfoIB.clicked.connect(self.setLoggingLevelIB)
        self.ui.loglevelWarningIB.clicked.connect(self.setLoggingLevelIB)
        self.ui.loglevelErrorIB.clicked.connect(self.setLoggingLevelIB)
        self.ui.loglevelDebugMC.clicked.connect(self.setLoggingLevelMC)
        self.ui.loglevelInfoMC.clicked.connect(self.setLoggingLevelMC)
        self.ui.loglevelWarningMC.clicked.connect(self.setLoggingLevelMC)
        self.ui.loglevelErrorMC.clicked.connect(self.setLoggingLevelMC)

    def initConfig(self):
        config = self.app.config['mainW']
        self.ui.loglevelDebug.setChecked(config.get('loglevelDebug', True))
        self.ui.loglevelInfo.setChecked(config.get('loglevelInfo', False))
        self.ui.loglevelWarning.setChecked(config.get('loglevelWarning', False))
        self.ui.loglevelError.setChecked(config.get('loglevelError', False))

        self.ui.loglevelDebugIB.setChecked(config.get('loglevelDebugIB', True))
        self.ui.loglevelInfoIB.setChecked(config.get('loglevelInfoIB', False))
        self.ui.loglevelWarningIB.setChecked(config.get('loglevelWarningIB', False))
        self.ui.loglevelErrorIB.setChecked(config.get('loglevelErrorIB', False))

        self.ui.loglevelDebugMC.setChecked(config.get('loglevelDebugMC', True))
        self.ui.loglevelInfoMC.setChecked(config.get('loglevelInfoMC', False))
        self.ui.loglevelWarningMC.setChecked(config.get('loglevelWarningMC', False))
        self.ui.loglevelErrorMC.setChecked(config.get('loglevelErrorMC', False))

        self.ui.expiresYes.setChecked(config.get('expiresYes', True))
        self.ui.expiresNo.setChecked(config.get('expiresNo', False))

        self.setLoggingLevel()
        self.setLoggingLevelIB()
        self.setLoggingLevelMC()
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['loglevelDebug'] = self.ui.loglevelDebug.isChecked()
        config['loglevelInfo'] = self.ui.loglevelInfo.isChecked()
        config['loglevelWarning'] = self.ui.loglevelWarning.isChecked()
        config['loglevelError'] = self.ui.loglevelError.isChecked()

        config['loglevelDebugIB'] = self.ui.loglevelDebugIB.isChecked()
        config['loglevelInfoIB'] = self.ui.loglevelInfoIB.isChecked()
        config['loglevelWarningIB'] = self.ui.loglevelWarningIB.isChecked()
        config['loglevelErrorIB'] = self.ui.loglevelErrorIB.isChecked()

        config['loglevelDebugMC'] = self.ui.loglevelDebugMC.isChecked()
        config['loglevelInfoMC'] = self.ui.loglevelInfoMC.isChecked()
        config['loglevelWarningMC'] = self.ui.loglevelWarningMC.isChecked()
        config['loglevelErrorMC'] = self.ui.loglevelErrorMC.isChecked()

        config['expiresYes'] = self.ui.expiresYes.isChecked()
        config['expiresNo'] = self.ui.expiresNo.isChecked()
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

    def setLoggingLevel(self):
        """
        Setting the log level according to the setting in the gui.

        :return: nothing
        """

        if self.ui.loglevelDebug.isChecked():
            logging.getLogger().setLevel(logging.DEBUG)
        elif self.ui.loglevelInfo.isChecked():
            logging.getLogger().setLevel(logging.INFO)
        elif self.ui.loglevelWarning.isChecked():
            logging.getLogger().setLevel(logging.WARNING)
        elif self.ui.loglevelError.isChecked():
            logging.getLogger().setLevel(logging.ERROR)

    def setLoggingLevelIB(self):
        """
        Setting the log level according to the setting in the gui.

        :return: nothing
        """

        if self.ui.loglevelDebugIB.isChecked():
            logging.getLogger('indibase').setLevel(logging.DEBUG)
        elif self.ui.loglevelInfoIB.isChecked():
            logging.getLogger('indibase').setLevel(logging.INFO)
        elif self.ui.loglevelWarningIB.isChecked():
            logging.getLogger('indibase').setLevel(logging.WARNING)
        elif self.ui.loglevelErrorIB.isChecked():
            logging.getLogger('indibase').setLevel(logging.ERROR)

    def setLoggingLevelMC(self):
        """
        Setting the log level according to the setting in the gui.

        :return: nothing
        """

        if self.ui.loglevelDebugMC.isChecked():
            logging.getLogger('mountcontrol').setLevel(logging.DEBUG)
        elif self.ui.loglevelInfoMC.isChecked():
            logging.getLogger('mountcontrol').setLevel(logging.INFO)
        elif self.ui.loglevelWarningMC.isChecked():
            logging.getLogger('mountcontrol').setLevel(logging.WARNING)
        elif self.ui.loglevelErrorMC.isChecked():
            logging.getLogger('mountcontrol').setLevel(logging.ERROR)
