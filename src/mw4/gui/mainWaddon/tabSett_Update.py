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
# License APL2.0
#
###########################################################
import logging
from astropy.utils import data, iers
from mw4.base.loggerMW import setCustomLoggingLevel
from mw4.gui.mainWaddon.tabAddon import TabAddon
from typing import Any


class SettUpdate(TabAddon):
    log = logging.getLogger("MW4")

    def __init__(self, mainW: Any) -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.ui.loglevelInfo.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelTrace.clicked.connect(self.setLoggingLevel)
        self.ui.isOnline.clicked.connect(self.setOnlineMode)
        self.ui.isOnline.clicked.connect(self.setupIERS)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.ui.loglevelInfo.setChecked(config.get("loglevelInfo", False))
        self.ui.loglevelDebug.setChecked(config.get("loglevelDebug", True))
        self.ui.loglevelTrace.setChecked(config.get("loglevelTrace", False))
        self.ui.isOnline.setChecked(config.get("isOnline", False))
        self.ui.ageDatabases.setValue(config.get("ageDatabases", 1))
        self.setLoggingLevel()
        self.setOnlineMode()
        self.setupIERS()

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["isOnline"] = self.ui.isOnline.isChecked()
        config["loglevelInfo"] = self.ui.loglevelInfo.isChecked()
        config["loglevelDebug"] = self.ui.loglevelDebug.isChecked()
        config["loglevelTrace"] = self.ui.loglevelTrace.isChecked()
        config["ageDatabases"] = self.ui.ageDatabases.value()

    def setOnlineMode(self) -> None:
        isOnline = self.ui.isOnline.isChecked()
        self.app.onlineMode = isOnline
        if isOnline:
            self.msg.emit(0, "System", "Online", "Online mode activated")
        else:
            self.msg.emit(0, "System", "Online", "Online mode deactivated")

    def setupIERS(self) -> None:
        isOnline = self.ui.isOnline.isChecked()
        if isOnline:
            iers.conf.auto_download = True
            iers.conf.auto_max_age = 30
            data.conf.allow_internet = True

        else:
            iers.conf.auto_download = False
            iers.conf.auto_max_age = 99999
            data.conf.allow_internet = False

    def setLoggingLevel(self) -> None:
        if self.ui.loglevelInfo.isChecked():
            setCustomLoggingLevel(self.app, "INFO")
        elif self.ui.loglevelTrace.isChecked():
            setCustomLoggingLevel(self.app, "TRACE")
        else:
            setCustomLoggingLevel(self.app, "DEBUG")
