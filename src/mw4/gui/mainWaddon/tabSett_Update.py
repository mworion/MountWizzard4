############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import platform
import sys
import webbrowser

import importlib_metadata

# external packages
import requests
from astropy.utils import data, iers
from packaging.utils import Version
from PySide6.QtCore import QObject

# local import
from mw4.base.loggerMW import setCustomLoggingLevel


class SettUpdate(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.ui.loglevelTrace.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelStandard.clicked.connect(self.setLoggingLevel)
        self.ui.isOnline.clicked.connect(self.setWeatherOnline)
        self.ui.isOnline.clicked.connect(self.setSeeingOnline)
        self.ui.isOnline.clicked.connect(self.setupIERS)

    def initConfig(self):
        """ """
        config = self.app.config["mainW"]
        self.ui.loglevelTrace.setChecked(config.get("loglevelTrace", False))
        self.ui.loglevelDebug.setChecked(config.get("loglevelDebug", True))
        self.ui.loglevelStandard.setChecked(config.get("loglevelStandard", False))
        self.ui.isOnline.setChecked(config.get("isOnline", False))
        self.ui.ageDatabases.setValue(config.get("ageDatabases", 1))

        self.setWeatherOnline()
        self.setSeeingOnline()
        self.setupIERS()

    def storeConfig(self):
        """ """
        config = self.app.config["mainW"]
        config["loglevelTrace"] = self.ui.loglevelTrace.isChecked()
        config["loglevelDebug"] = self.ui.loglevelDebug.isChecked()
        config["loglevelStandard"] = self.ui.loglevelStandard.isChecked()
        config["isOnline"] = self.ui.isOnline.isChecked()
        config["ageDatabases"] = self.ui.ageDatabases.value()

    def setWeatherOnline(self):
        """ """
        weather = self.app.onlineWeather
        if not weather:
            return False
        weather.online = self.ui.isOnline.isChecked()
        return True

    def setSeeingOnline(self):
        """ """
        seeing = self.app.seeingWeather
        if not seeing:
            return False
        seeing.online = self.ui.isOnline.isChecked()
        return True

    def setupIERS(self):
        """ """
        isOnline = self.ui.isOnline.isChecked()
        if isOnline:
            iers.conf.auto_download = True
            iers.conf.auto_max_age = 30
            data.conf.allow_internet = True

        else:
            iers.conf.auto_download = False
            iers.conf.auto_max_age = 99999
            data.conf.allow_internet = False

    def setLoggingLevel(self):
        """ """
        if self.ui.loglevelTrace.isChecked():
            setCustomLoggingLevel("TRACE")
        elif self.ui.loglevelDebug.isChecked():
            setCustomLoggingLevel("DEBUG")
        elif self.ui.loglevelStandard.isChecked():
            setCustomLoggingLevel("INFO")
