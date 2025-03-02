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
from PySide6.QtCore import QObject

# local import


class SettDome(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

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
        self.app.mount.signals.firmwareDone.connect(self.setUseGeometry)
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

    def tab1(self):
        self.ui.tabDomeExplain.setCurrentIndex(0)

    def tab2(self):
        self.ui.tabDomeExplain.setCurrentIndex(1)

    def tab3(self):
        self.ui.tabDomeExplain.setCurrentIndex(2)

    def tab4(self):
        self.ui.tabDomeExplain.setCurrentIndex(3)

    def tab5(self):
        self.ui.tabDomeExplain.setCurrentIndex(4)

    def tab6(self):
        self.ui.tabDomeExplain.setCurrentIndex(5)

    def tab7(self):
        self.ui.tabDomeExplain.setCurrentIndex(6)

    def tab8(self):
        self.ui.tabDomeExplain.setCurrentIndex(7)

    def tab9(self):
        self.ui.tabDomeExplain.setCurrentIndex(8)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config["mainW"]
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
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config["mainW"]
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
        return True

    def setupIcons(self):
        """
        :return:
        """
        pixmap = self.mainW.img2pixmap(":/dome/radius.png")
        self.ui.picDome1.setPixmap(pixmap)

        is10Micron = self.ui.use10micronDef.isChecked()
        if is10Micron:
            pixmap = self.mainW.img2pixmap(":/dome/north.png")
            self.ui.picDome2.setPixmap(pixmap)
            pixmap = self.mainW.img2pixmap(":/dome/east.png")
            self.ui.picDome3.setPixmap(pixmap)
            pixmap = self.mainW.img2pixmap(":/dome/vert.png")
            self.ui.picDome4.setPixmap(pixmap)
        else:
            pixmap = self.mainW.img2pixmap(":/dome/northGEM.png")
            self.ui.picDome2.setPixmap(pixmap)
            pixmap = self.mainW.img2pixmap(":/dome/eastGEM.png")
            self.ui.picDome3.setPixmap(pixmap)
            pixmap = self.mainW.img2pixmap(":/dome/vertGEM.png")
            self.ui.picDome4.setPixmap(pixmap)

        pixmap = self.mainW.img2pixmap(":/dome/gem.png")
        self.ui.picDome5.setPixmap(pixmap)
        pixmap = self.mainW.img2pixmap(":/dome/lat.png")
        self.ui.picDome6.setPixmap(pixmap)
        pixmap = self.mainW.img2pixmap(":/dome/shutter.png")
        self.ui.picDome7.setPixmap(pixmap)
        pixmap = self.mainW.img2pixmap(":/dome/hysteresis.png")
        self.ui.picDome8.setPixmap(pixmap)
        pixmap = self.mainW.img2pixmap(":/dome/zenith.png")
        self.ui.picDome9.setPixmap(pixmap)

        self.mainW.wIcon(self.ui.copyFromDomeDriver, "copy")
        self.mainW.wIcon(self.ui.domeCloseShutter, "exit-down")
        self.mainW.wIcon(self.ui.domeOpenShutter, "exit-up")
        self.mainW.wIcon(self.ui.domeAbortSlew, "bolt-alt")
        return True

    def updateDomeGeometryToGui(self):
        """
        :return: true for test purpose
        """
        value = float(self.app.dome.data.get("DOME_MEASUREMENTS.DM_OTA_OFFSET", 0))
        self.ui.offGEM.setValue(value)

        value = float(self.app.dome.data.get("DOME_MEASUREMENTS.DM_DOME_RADIUS", 0))
        self.ui.domeRadius.setValue(value)

        value = float(self.app.dome.data.get("DOME_MEASUREMENTS.DM_SHUTTER_WIDTH", 0))
        self.ui.domeClearOpening.setValue(value)

        value = float(self.app.dome.data.get("DOME_MEASUREMENTS.DM_NORTH_DISPLACEMENT", 0))
        self.ui.domeNorthOffset.setValue(value)

        value = float(self.app.dome.data.get("DOME_MEASUREMENTS.DM_EAST_DISPLACEMENT", 0))
        self.ui.domeEastOffset.setValue(value)

        value = float(self.app.dome.data.get("DOME_MEASUREMENTS.DM_UP_DISPLACEMENT", 0))
        self.ui.domeVerticalOffset.setValue(value)
        return True

    def switchGeometryDefinition(self):
        """
        :return:
        """
        self.ui.domeEastOffset.valueChanged.disconnect(self.setUseGeometry)
        self.ui.domeNorthOffset.valueChanged.disconnect(self.setUseGeometry)
        self.ui.domeVerticalOffset.valueChanged.disconnect(self.setUseGeometry)
        is10Micron = self.ui.use10micronDef.isChecked()
        if is10Micron:
            self.ui.domeNorthOffset.setValue(self.app.mount.geometry.offNorth)
            self.ui.domeEastOffset.setValue(self.app.mount.geometry.offEast)
            self.ui.domeVerticalOffset.setValue(self.app.mount.geometry.offVert)
        else:
            self.ui.domeNorthOffset.setValue(self.app.mount.geometry.offNorthGEM)
            self.ui.domeEastOffset.setValue(self.app.mount.geometry.offEastGEM)
            self.ui.domeVerticalOffset.setValue(self.app.mount.geometry.offVertGEM)
        self.ui.domeEastOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeNorthOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeVerticalOffset.valueChanged.connect(self.setUseGeometry)
        return True

    def setUseGeometry(self):
        """
        :return: true for test purpose
        """
        if self.ui.automaticDome.isChecked():
            self.updateDomeGeometryToGui()

        self.app.mount.geometry.domeRadius = self.ui.domeRadius.value()
        self.app.dome.radius = self.ui.domeRadius.value()
        self.app.mount.geometry.offGEM = self.ui.offGEM.value()
        self.app.mount.geometry.offLAT = self.ui.offLAT.value()

        is10Micron = self.ui.use10micronDef.isChecked()
        if is10Micron:
            self.app.mount.geometry.offNorth = self.ui.domeNorthOffset.value()
            self.app.mount.geometry.offEast = self.ui.domeEastOffset.value()
            self.app.mount.geometry.offVert = self.ui.domeVerticalOffset.value()
        else:
            self.app.mount.geometry.offNorthGEM = self.ui.domeNorthOffset.value()
            self.app.mount.geometry.offEastGEM = self.ui.domeEastOffset.value()
            self.app.mount.geometry.offVertGEM = self.ui.domeVerticalOffset.value()

        clearOpening = self.ui.domeClearOpening.value()
        self.app.dome.clearOpening = clearOpening
        self.ui.domeOpeningHysteresis.setMaximum(clearOpening / 2.1)
        self.app.dome.openingHysteresis = self.ui.domeOpeningHysteresis.value()
        self.app.dome.clearanceZenith = self.ui.domeClearanceZenith.value()

        useGeometry = self.ui.useDomeGeometry.isChecked()
        self.app.dome.useGeometry = useGeometry

        useDynamicFollowing = self.ui.useDynamicFollowing.isChecked()
        self.app.dome.useDynamicFollowing = useDynamicFollowing
        self.app.dome.overshoot = self.ui.useOvershoot.isChecked()
        self.app.updateDomeSettings.emit()
        return True

    def setDomeSettlingTime(self):
        """
        :return: true for test purpose
        """
        self.app.dome.settlingTime = self.ui.settleTimeDome.value()
        return True
