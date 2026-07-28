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
from mw4.gui.utilities.qtHelpers import img2pixmap, setPixmapAlpha
from typing import Any


class SettDome:
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui

        self.valueConfigWidgets = [
            self.ui.domeRadius,
            self.ui.offGEM,
            self.ui.offLAT,
            self.ui.domeEastOffset,
            self.ui.domeNorthOffset,
            self.ui.domeVerticalOffset,
            self.ui.domeClearOpening,
            self.ui.domeOpeningHysteresis,
            self.ui.domeClearanceZenith,
            self.ui.settleTimeDome,
        ]
        for widget in self.valueConfigWidgets:
            widget.valueChanged.connect(self.storeConfig)

        self.clickConfigWidgets = [
            self.ui.useOvershoot,
            self.ui.useDomeGeometry,
            self.ui.useDynamicFollowing,
            self.ui.use10micronDef,
        ]
        for widget in self.clickConfigWidgets:
            widget.clicked.connect(self.storeConfig)

        self.ui.use10micronDef.clicked.connect(self.setupIcons)
        self.ui.copyFromDomeDriver.clicked.connect(self.updateGeometryFromDriver)
        self.app.dReg["mount"].signals.firmwareDone.connect(self.storeConfig)

        self.domeExplainTabs = [
            (self.ui.domeRadius, 0),
            (self.ui.domeNorthOffset, 1),
            (self.ui.domeEastOffset, 2),
            (self.ui.domeVerticalOffset, 3),
            (self.ui.offGEM, 4),
            (self.ui.offLAT, 5),
            (self.ui.domeClearOpening, 6),
            (self.ui.domeOpeningHysteresis, 7),
            (self.ui.domeClearanceZenith, 8),
        ]
        for widget, index in self.domeExplainTabs:
            widget.valueChanged.connect(
                lambda checked, idx=index: self.showDomeExplainTab(idx)
            )

    def showDomeExplainTab(self, index: int) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(index)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingDome", {})
        self.ui.domeClearOpening.setValue(config.get("clearOpening", 0.4))
        self.ui.domeOpeningHysteresis.setValue(config.get("openingHysteresis", 0.0))
        self.ui.domeClearanceZenith.setValue(config.get("clearanceZenith", 0.2))
        self.ui.useOvershoot.setChecked(config.get("useOvershoot", False))
        self.ui.domeNorthOffset.setValue(config.get("northOffset", 0))
        self.ui.domeEastOffset.setValue(config.get("eastOffset", 0))
        self.ui.domeVerticalOffset.setValue(config.get("verticalOffset", 0))
        self.ui.use10micronDef.setChecked(config.get("use10micronDef", False))
        self.ui.offGEM.setValue(config.get("offGEM", 0))
        self.ui.offLAT.setValue(config.get("offLAT", 0))
        self.ui.domeRadius.setValue(config.get("radius", 1.5))
        self.ui.useDomeGeometry.setChecked(config.get("useGeometry", False))
        self.ui.automaticDome.setChecked(config.get("automaticDome", False))
        self.ui.useDynamicFollowing.setChecked(config.get("useDynamicFollowing", False))
        self.ui.settleTimeDome.setValue(config.get("settleTime", 0))

    def storeConfig(self) -> None:
        config = self.app.config["SettingDome"]
        config["radius"] = self.ui.domeRadius.value()
        config["clearOpening"] = self.ui.domeClearOpening.value()
        config["openingHysteresis"] = self.ui.domeOpeningHysteresis.value()
        config["clearanceZenith"] = self.ui.domeClearanceZenith.value()
        config["useOvershoot"] = self.ui.useOvershoot.isChecked()
        config["northOffset"] = self.ui.domeNorthOffset.value()
        config["eastOffset"] = self.ui.domeEastOffset.value()
        config["verticalOffset"] = self.ui.domeVerticalOffset.value()
        config["use10micronDef"] = self.ui.use10micronDef.isChecked()
        config["offGEM"] = self.ui.offGEM.value()
        config["offLAT"] = self.ui.offLAT.value()
        config["useGeometry"] = self.ui.useDomeGeometry.isChecked()
        config["automaticDome"] = self.ui.automaticDome.isChecked()
        config["useDynamicFollowing"] = self.ui.useDynamicFollowing.isChecked()
        config["settleTime"] = self.ui.settleTimeDome.value()
        self.ui.domeOpeningHysteresis.setMaximum(self.ui.domeClearOpening.value() / 2.1)
        self.app.updateDomeSettings.emit()

    def setupIcons(self) -> None:
        is10Micron = self.ui.use10micronDef.isChecked()
        images = [
            ("radius", 1, False),
            ("north", 2, True),
            ("east", 3, True),
            ("vert", 4, True),
            ("gem", 5, False),
            ("lat", 6, False),
            ("shutter", 7, False),
            ("hysteresis", 8, False),
            ("zenith", 9, False),
        ]
        for image, pic_index, has_gem_variant in images:
            ext = "" if (is10Micron or not has_gem_variant) else "GEM"
            pixmap = img2pixmap(f"assets/dome/{image}{ext}.png")
            pixmap = setPixmapAlpha(pixmap, Styles.transparency)
            getattr(self.ui, f"picDome{pic_index}").setPixmap(pixmap)

        self.parentW.wIcon(self.ui.copyFromDomeDriver, "copy")

    def closeEvent(self) -> None:
        self.app.dReg["mount"].signals.firmwareDone.disconnect(self.storeConfig)

    def updateGeometryFromDriver(self) -> None:
        value = float(self.app.dReg["dome"].data.get("DOME_MEASUREMENTS.DM_OTA_OFFSET", 0))
        self.ui.offGEM.setValue(value)
        value = float(self.app.dReg["dome"].data.get("DOME_MEASUREMENTS.DM_DOME_RADIUS", 0))
        self.ui.domeRadius.setValue(value)
        value = float(self.app.dReg["dome"].data.get("DOME_MEASUREMENTS.DM_SHUTTER_WIDTH", 0))
        self.ui.domeClearOpening.setValue(value)
        value = float(
            self.app.dReg["dome"].data.get("DOME_MEASUREMENTS.DM_NORTH_DISPLACEMENT", 0)
        )
        self.ui.domeNorthOffset.setValue(value)
        value = float(
            self.app.dReg["dome"].data.get("DOME_MEASUREMENTS.DM_EAST_DISPLACEMENT", 0)
        )
        self.ui.domeEastOffset.setValue(value)
        value = float(
            self.app.dReg["dome"].data.get("DOME_MEASUREMENTS.DM_UP_DISPLACEMENT", 0)
        )
        self.ui.domeVerticalOffset.setValue(value)
        self.storeConfig()
