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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.bigPopup_ui import Ui_BigPopup
from gui.utilities.toolsQtWidget import changeStyleDynamic


class BigPopup(MWidget):
    """ """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = Ui_BigPopup()
        self.ui.setupUi(self)
        self.parent = app.mainW
        self.msg = app.msg
        self.setWindowTitle("Big buttons")

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("bigPopupW", {})
        self.positionWindow(config)

    def storeConfig(self) -> None:
        """ """
        configMain = self.app.config
        configMain["bigPopupW"] = {}
        config = configMain["bigPopupW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.storeConfig()
        super().closeEvent(closeEvent)

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)

    def showWindow(self) -> None:
        """ """
        self.wIcon(self.ui.mountOn, "power-on")
        self.wIcon(self.ui.mountOff, "power-off")
        self.wIcon(self.ui.stop, "hand")

        self.app.colorChange.connect(self.colorChange)
        self.app.update1s.connect(self.updateDeviceStats)
        self.app.mount.signals.pointDone.connect(self.updateStatus)
        self.ui.stop.clicked.connect(lambda: self.app.virtualStop.emit())
        self.ui.mountOn.clicked.connect(lambda: self.app.mountOn.emit())
        self.ui.mountOff.clicked.connect(lambda: self.app.mountOff.emit())
        self.show()

    def updateDeviceStats(self) -> None:
        """ """
        isMount = self.app.deviceStat.get("mount", False)
        changeStyleDynamic(self.ui.mountOn, "running", isMount)
        changeStyleDynamic(self.ui.mountOff, "running", not isMount)

    def updateStatus(self) -> None:
        """ """
        running = self.app.mount.obsSite.status == 1
        changeStyleDynamic(self.ui.stop, "running", running)
