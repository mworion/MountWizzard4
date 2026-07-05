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
from mw4.gui.styles.styles import Styles
from mw4.gui.utilities.qtHelpers import svg2pixmap
from typing import Any


class SettGui:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui
        self.ui.colorSet.currentIndexChanged.connect(self.updateColorSet)
        self.ui.transparency.valueChanged.connect(self.updateColorSet)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingGui", {})
        colSet = config.get("colorSet", 0)
        self.ui.colorSet.setCurrentIndex(colSet)
        self.ui.transparency.setValue(config.get("transparency", 1))
        cfg = self.app.dReg["hidController"].instance.config
        self.ui.hidDome.setChecked(cfg.dome)
        self.ui.hidAltAz.setChecked(cfg.moveAltAz)
        self.ui.hidRaDec.setChecked(cfg.moveRaDec)
        self.ui.hidTracking.setChecked(cfg.tracking)
        self.ui.hidParkStop.setChecked(cfg.parkStop)
        self.ui.hidDome.clicked.connect(self.storeConfig)
        self.ui.hidParkStop.clicked.connect(self.storeConfig)
        self.ui.hidAltAz.clicked.connect(self.storeConfig)
        self.ui.hidRaDec.clicked.connect(self.storeConfig)
        self.ui.hidTracking.clicked.connect(self.storeConfig)

    def storeConfig(self) -> None:
        self.app.config["SettingGui"] = {}
        config = self.app.config["SettingGui"]
        config["colorSet"] = self.ui.colorSet.currentIndex()
        config["transparency"] = self.ui.transparency.value()
        cfg = self.app.dReg["hidController"].instance.config
        cfg.dome = self.ui.hidDome.isChecked()
        cfg.moveAltAz = self.ui.hidAltAz.isChecked()
        cfg.moveRaDec = self.ui.hidRaDec.isChecked()
        cfg.parkStop = self.ui.hidParkStop.isChecked()
        cfg.tracking = self.ui.hidTracking.isChecked()
        self.app.hidModeChanged.emit()

    def setupIcons(self) -> None:
        pixmap = svg2pixmap("assets/icon/controllerNew.svg", self.parentW.M_PRIM)
        self.ui.controllerOverview.setPixmap(pixmap)

    def updateColorSet(self) -> None:
        Styles.colorSet = self.ui.colorSet.currentIndex()
        Styles.transparency = self.ui.transparency.value()
        self.parentW.setStyleSheet(self.parentW.mw4Style)
        self.setupIcons()
        self.app.colorChange.emit()
