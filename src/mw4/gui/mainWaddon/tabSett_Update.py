############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import logging
from astropy.utils import data, iers
from mw4.base.loggerMW import setCustomLoggingLevel
from PySide6.QtCore import QObject


class SettUpdate(QObject):
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.ui.loglevelTrace.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelStandard.clicked.connect(self.setLoggingLevel)
        self.ui.isOnline.clicked.connect(self.setOnlineMode)
        self.ui.isOnline.clicked.connect(self.setupIERS)

    def initConfig(self):
        """ """
        config = self.app.config["mainW"]
        loglevel = logging.getLevelName(self.log.level)
        self.ui.loglevelTrace.setChecked(loglevel == "TRACE")
        self.ui.loglevelDebug.setChecked(loglevel == "DEBUG")
        self.ui.loglevelStandard.setChecked(loglevel == "INFO")
        self.ui.isOnline.setChecked(config.get("isOnline", False))
        self.ui.ageDatabases.setValue(config.get("ageDatabases", 1))
        self.setOnlineMode()
        self.setupIERS()

    def storeConfig(self):
        """ """
        config = self.app.config["mainW"]
        config["isOnline"] = self.ui.isOnline.isChecked()
        config["ageDatabases"] = self.ui.ageDatabases.value()

    def setOnlineMode(self):
        """ """
        isOnline = self.ui.isOnline.isChecked()
        self.app.onlineMode = isOnline
        if isOnline:
            self.msg.emit(0, "System", "Online", "Online mode activated")
        else:
            self.msg.emit(0, "System", "Online", "Online mode deactivated")

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
