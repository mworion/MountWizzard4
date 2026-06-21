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
from collections.abc import Any


class SettUpdate:
    log = logging.getLogger("MW4")

    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.ui.loglevelInfo.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelTrace.clicked.connect(self.setLoggingLevel)
        self.ui.isOnline.clicked.connect(self.setOnlineMode)
        self.ui.isOnline.clicked.connect(self.storeConfig)
        self.ui.ageDatabases.valueChanged.connect(self.storeConfig)
        self.app.onlineModeChanged.connect(self.setupIERS)
        self.ui.unitTimeUTC.clicked.connect(self.setTimeBaseUTC)
        self.ui.unitTimeLocal.clicked.connect(self.setTimeBaseLocal)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingUpdate", {})
        self.ui.loglevelInfo.setChecked(config.get("loglevelInfo", False))
        self.ui.loglevelDebug.setChecked(config.get("loglevelDebug", True))
        self.ui.loglevelTrace.setChecked(config.get("loglevelTrace", False))
        self.ui.isOnline.setChecked(config.get("isOnline", False))
        self.ui.ageDatabases.setValue(config.get("ageDatabases", 1))
        self.ui.unitTimeUTC.setChecked(config.get("unitTimeUTC", True))
        self.ui.unitTimeLocal.setChecked(config.get("unitTimeLocal", False))
        self.setLoggingLevel()
        self.setOnlineMode()
        self.setupIERS()

    def storeConfig(self) -> None:
        self.app.config["SettingUpdate"] = {}
        config = self.app.config["SettingUpdate"]
        config["isOnline"] = self.ui.isOnline.isChecked()
        config["loglevelInfo"] = self.ui.loglevelInfo.isChecked()
        config["loglevelDebug"] = self.ui.loglevelDebug.isChecked()
        config["loglevelTrace"] = self.ui.loglevelTrace.isChecked()
        config["ageDatabases"] = self.ui.ageDatabases.value()
        config["unitTimeUTC"] = self.ui.unitTimeUTC.isChecked()
        config["unitTimeLocal"] = self.ui.unitTimeLocal.isChecked()

    def setupIERS(self) -> None:
        if self.app.isOnline:
            iers.conf.auto_download = True
            iers.conf.auto_max_age = 30
            data.conf.allow_internet = True
        else:
            iers.conf.auto_download = False
            iers.conf.auto_max_age = 99999
            data.conf.allow_internet = False

    def setOnlineMode(self) -> None:
        isOnline = self.ui.isOnline.isChecked()
        self.app.isOnline = isOnline
        if isOnline:
            self.msg.emit(0, "System", "Online", "Online mode activated")
        else:
            self.msg.emit(0, "System", "Online", "Online mode deactivated")
        self.app.onlineModeChanged.emit()

    def setLoggingLevel(self) -> None:
        if self.ui.loglevelInfo.isChecked():
            setCustomLoggingLevel(self.app, "INFO")
        elif self.ui.loglevelTrace.isChecked():
            setCustomLoggingLevel(self.app, "TRACE")
        else:
            setCustomLoggingLevel(self.app, "DEBUG")

    def setTimeBaseUTC(self) -> None:
        self.app.config["unitTimeUTC"] = True
        self.app.timebaseChanged.emit()

    def setTimeBaseLocal(self) -> None:
        self.app.config["unitTimeUTC"] = False
        self.app.timebaseChanged.emit()
