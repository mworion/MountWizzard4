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
from mw4.gui.utilities.qtHelpers import img2pixmap
from typing import Any


class SettDome():
    def __init__(self, parentW: Any) -> None:
        self.parentW = parentW
        self.app = parentW.app
        self.msg = parentW.app.msg
        self.ui = parentW.ui

        self.ui.domeRadius.valueChanged.connect(self.setUseGeometry)
        self.ui.offGEM.valueChanged.connect(self.setUseGeometry)
        self.ui.offLAT.valueChanged.connect(self.setUseGeometry)
        self.ui.domeEastOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeNorthOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeVerticalOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeClearOpening.valueChanged.connect(self.setUseGeometry)
        self.ui.domeOpeningHysteresis.valueChanged.connect(self.setUseGeometry)
        self.ui.domeClearanceZenith.valueChanged.connect(self.setUseGeometry)
        self.ui.useOvershoot.clicked.connect(self.setUseGeometry)
        self.ui.settleTimeDome.valueChanged.connect(self.setDomeSettlingTime)
        self.ui.useDomeGeometry.clicked.connect(self.setUseGeometry)
        self.ui.useDynamicFollowing.clicked.connect(self.setUseGeometry)
        self.ui.copyFromDomeDriver.clicked.connect(self.updateDomeGeometryToGui)
        self.app.dReg["mount"].signals.firmwareDone.connect(self.setUseGeometry)
        self.ui.domeRadius.valueChanged.connect(self.tab1)
        self.ui.domeNorthOffset.valueChanged.connect(self.tab2)
        self.ui.domeEastOffset.valueChanged.connect(self.tab3)
        self.ui.domeVerticalOffset.valueChanged.connect(self.tab4)
        self.ui.offGEM.valueChanged.connect(self.tab5)
        self.ui.offLAT.valueChanged.connect(self.tab6)
        self.ui.domeClearOpening.valueChanged.connect(self.tab7)
        self.ui.domeOpeningHysteresis.valueChanged.connect(self.tab8)
        self.ui.domeClearanceZenith.valueChanged.connect(self.tab9)
        self.ui.use10micronDef.clicked.connect(self.switchGeometryDefinition)
        self.ui.use10micronDef.clicked.connect(self.setupIcons)

    def tab1(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(0)

    def tab2(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(1)

    def tab3(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(2)

    def tab4(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(3)

    def tab5(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(4)

    def tab6(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(5)

    def tab7(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(6)

    def tab8(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(7)

    def tab9(self) -> None:
        self.ui.tabDomeExplain.setCurrentIndex(8)

    def initConfig(self) -> None:
        config = self.app.config.get("SettingDeviceDome", {})
        self.ui.domeClearOpening.setValue(config.get("domeClearOpening", 0.4))
        self.ui.domeOpeningHysteresis.setValue(config.get("domeOpeningHysteresis", 0.0))
        self.ui.domeClearanceZenith.setValue(config.get("domeClearanceZenith", 0.2))
        self.ui.useOvershoot.setChecked(config.get("useOvershoot", False))
        self.ui.domeNorthOffset.setValue(config.get("domeNorthOffset", 0))
        self.ui.domeEastOffset.setValue(config.get("domeEastOffset", 0))
        self.ui.domeVerticalOffset.setValue(config.get("domeVerticalOffset", 0))
        self.ui.use10micronDef.setChecked(config.get("use10micronDef", False))
        self.ui.offGEM.setValue(config.get("offGEM", 0))
        self.ui.offLAT.setValue(config.get("offLAT", 0))
        self.ui.domeRadius.setValue(config.get("domeRadius", 1.5))
        self.ui.useDomeGeometry.setChecked(config.get("useDomeGeometry", False))
        self.ui.automaticDome.setChecked(config.get("automaticDome", False))
        self.ui.useDynamicFollowing.setChecked(config.get("useDynamicFollowing", False))
        self.ui.settleTimeDome.setValue(config.get("settleTimeDome", 0))
        self.setUseGeometry()

    def storeConfig(self) -> None:
        self.app.config["SettingDeviceDome"] = {}
        config = self.app.config["SettingDeviceDome"]
        config["domeRadius"] = self.ui.domeRadius.value()
        config["domeClearOpening"] = self.ui.domeClearOpening.value()
        config["domeOpeningHysteresis"] = self.ui.domeOpeningHysteresis.value()
        config["domeClearanceZenith"] = self.ui.domeClearanceZenith.value()
        config["useOvershoot"] = self.ui.useOvershoot.isChecked()
        config["domeNorthOffset"] = self.ui.domeNorthOffset.value()
        config["domeEastOffset"] = self.ui.domeEastOffset.value()
        config["domeVerticalOffset"] = self.ui.domeVerticalOffset.value()
        config["use10micronDef"] = self.ui.use10micronDef.isChecked()
        config["offGEM"] = self.ui.offGEM.value()
        config["offLAT"] = self.ui.offLAT.value()
        config["useDomeGeometry"] = self.ui.useDomeGeometry.isChecked()
        config["automaticDome"] = self.ui.automaticDome.isChecked()
        config["useDynamicFollowing"] = self.ui.useDynamicFollowing.isChecked()
        config["settleTimeDome"] = self.ui.settleTimeDome.value()

    def setupIcons(self) -> None:
        pixmap = img2pixmap("assets/dome/radius.png")
        self.ui.picDome1.setPixmap(pixmap)

        is10Micron = self.ui.use10micronDef.isChecked()
        if is10Micron:
            pixmap = img2pixmap("assets/dome/north.png")
            self.ui.picDome2.setPixmap(pixmap)
            pixmap = img2pixmap("assets/dome/east.png")
            self.ui.picDome3.setPixmap(pixmap)
            pixmap = img2pixmap("assets/dome/vert.png")
            self.ui.picDome4.setPixmap(pixmap)
        else:
            pixmap = img2pixmap("assets/dome/northGEM.png")
            self.ui.picDome2.setPixmap(pixmap)
            pixmap = img2pixmap("assets/dome/eastGEM.png")
            self.ui.picDome3.setPixmap(pixmap)
            pixmap = img2pixmap("assets/dome/vertGEM.png")
            self.ui.picDome4.setPixmap(pixmap)

        pixmap = img2pixmap("assets/dome/gem.png")
        self.ui.picDome5.setPixmap(pixmap)
        pixmap = img2pixmap("assets/dome/lat.png")
        self.ui.picDome6.setPixmap(pixmap)
        pixmap = img2pixmap("assets/dome/shutter.png")
        self.ui.picDome7.setPixmap(pixmap)
        pixmap = img2pixmap("assets/dome/hysteresis.png")
        self.ui.picDome8.setPixmap(pixmap)
        pixmap = img2pixmap("assets/dome/zenith.png")
        self.ui.picDome9.setPixmap(pixmap)

        self.parentW.wIcon(self.ui.copyFromDomeDriver, "copy")

    def updateDomeGeometryToGui(self) -> None:
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

    def switchGeometryDefinition(self) -> None:
        self.ui.domeEastOffset.valueChanged.disconnect(self.setUseGeometry)
        self.ui.domeNorthOffset.valueChanged.disconnect(self.setUseGeometry)
        self.ui.domeVerticalOffset.valueChanged.disconnect(self.setUseGeometry)
        is10Micron = self.ui.use10micronDef.isChecked()
        if is10Micron:
            self.ui.domeNorthOffset.setValue(self.app.dReg["mount"].geometry.offNorth)
            self.ui.domeEastOffset.setValue(self.app.dReg["mount"].geometry.offEast)
            self.ui.domeVerticalOffset.setValue(self.app.dReg["mount"].geometry.offVert)
        else:
            self.ui.domeNorthOffset.setValue(self.app.dReg["mount"].geometry.offNorthGEM)
            self.ui.domeEastOffset.setValue(self.app.dReg["mount"].geometry.offEastGEM)
            self.ui.domeVerticalOffset.setValue(self.app.dReg["mount"].geometry.offVertGEM)
        self.ui.domeEastOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeNorthOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeVerticalOffset.valueChanged.connect(self.setUseGeometry)

    def setUseGeometry(self) -> None:
        if self.ui.automaticDome.isChecked():
            self.updateDomeGeometryToGui()

        mount = self.app.dReg["mount"].instance
        dome = self.app.dReg["dome"].instance

        mount.geometry.domeRadius = self.ui.domeRadius.value()
        dome.radius = self.ui.domeRadius.value()
        mount.geometry.offGEM = self.ui.offGEM.value()
        mount.geometry.offLAT = self.ui.offLAT.value()

        is10Micron = self.ui.use10micronDef.isChecked()
        if is10Micron:
            mount.geometry.offNorth = self.ui.domeNorthOffset.value()
            mount.geometry.offEast = self.ui.domeEastOffset.value()
            mount.geometry.offVert = self.ui.domeVerticalOffset.value()
        else:
            mount.geometry.offNorthGEM = self.ui.domeNorthOffset.value()
            mount.geometry.offEastGEM = self.ui.domeEastOffset.value()
            mount.geometry.offVertGEM = self.ui.domeVerticalOffset.value()

        clearOpening = self.ui.domeClearOpening.value()
        dome.clearOpening = clearOpening
        self.ui.domeOpeningHysteresis.setMaximum(clearOpening / 2.1)
        dome.openingHysteresis = self.ui.domeOpeningHysteresis.value()
        dome.clearanceZenith = self.ui.domeClearanceZenith.value()

        useGeometry = self.ui.useDomeGeometry.isChecked()
        dome.useGeometry = useGeometry

        useDynamicFollowing = self.ui.useDynamicFollowing.isChecked()
        dome.useDynamicFollowing = useDynamicFollowing
        dome.overshoot = self.ui.useOvershoot.isChecked()
        self.app.updateDomeSettings.emit()

    def setDomeSettlingTime(self) -> None:
        dome = self.app.dReg["dome"].instance
        dome.settlingTime = self.ui.settleTimeDome.value()
