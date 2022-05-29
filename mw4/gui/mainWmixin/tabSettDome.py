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
#
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import


class SettDome(object):
    """
    """

    def __init__(self):
        self.ui.domeRadius.valueChanged.connect(self.setUseGeometry)
        self.ui.offGEM.valueChanged.connect(self.setUseGeometry)
        self.ui.offLAT.valueChanged.connect(self.setUseGeometry)
        self.ui.domeEastOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeNorthOffset.valueChanged.connect(self.setUseGeometry)
        self.ui.domeZoffGEM.valueChanged.connect(self.setZoffGEMInMount)
        self.ui.domeZoff10micron.valueChanged.connect(self.setZoff10micronInMount)
        self.ui.domeClearOpening.valueChanged.connect(self.setUseGeometry)
        self.ui.domeOpeningHysteresis.valueChanged.connect(self.setUseGeometry)
        self.ui.domeClearanceZenith.valueChanged.connect(self.setUseGeometry)
        self.ui.useOvershoot.clicked.connect(self.setUseGeometry)
        self.ui.settleTimeDome.valueChanged.connect(self.setDomeSettlingTime)
        self.ui.useDomeGeometry.clicked.connect(self.setUseGeometry)
        self.ui.useDynamicFollowing.clicked.connect(self.setUseGeometry)
        self.ui.copyFromDomeDriver.clicked.connect(self.updateDomeGeometryToGui)
        self.app.mount.signals.firmwareDone.connect(self.setUseGeometry)
        self.app.mount.signals.firmwareDone.connect(self.setZoffGEMInMount)

        self.ui.domeRadius.valueChanged.connect(self.tab1)
        self.ui.domeNorthOffset.valueChanged.connect(self.tab2)
        self.ui.domeEastOffset.valueChanged.connect(self.tab3)
        self.ui.domeZoffGEM.valueChanged.connect(self.tab4)
        self.ui.domeZoff10micron.valueChanged.connect(self.tab5)
        self.ui.offGEM.valueChanged.connect(self.tab6)
        self.ui.offLAT.valueChanged.connect(self.tab7)
        self.ui.domeClearOpening.valueChanged.connect(self.tab8)
        self.ui.domeOpeningHysteresis.valueChanged.connect(self.tab9)
        self.ui.domeClearanceZenith.valueChanged.connect(self.tab10)

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

    def tab10(self):
        self.ui.tabDomeExplain.setCurrentIndex(9)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.domeClearOpening.setValue(config.get('domeClearOpening', 0.4))
        self.ui.domeOpeningHysteresis.setValue(config.get('domeOpeningHysteresis',
                                                          0.0))
        self.ui.domeClearanceZenith.setValue(config.get('domeClearanceZenith', 0.2))
        self.ui.useOvershoot.setChecked(config.get('useOvershoot', False))
        self.ui.domeNorthOffset.setValue(config.get('domeNorthOffset', 0))
        self.ui.domeEastOffset.setValue(config.get('domeEastOffset', 0))
        self.ui.domeZoffGEM.setValue(config.get('domeZoffGEM', 0))
        self.ui.offGEM.setValue(config.get('offGEM', 0))
        self.ui.offLAT.setValue(config.get('offLAT', 0))
        self.ui.domeRadius.setValue(config.get('domeRadius', 1.5))
        self.ui.useDomeGeometry.setChecked(config.get('useDomeGeometry', False))
        self.ui.automaticDome.setChecked(config.get('automaticDome', False))
        self.ui.useDynamicFollowing.setChecked(config.get('useDynamicFollowing', False))
        self.ui.settleTimeDome.setValue(config.get('settleTimeDome', 0))
        self.setUseGeometry()
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['domeRadius'] = self.ui.domeRadius.value()
        config['domeClearOpening'] = self.ui.domeClearOpening.value()
        config['domeOpeningHysteresis'] = self.ui.domeOpeningHysteresis.value()
        config['domeClearanceZenith'] = self.ui.domeClearanceZenith.value()
        config['useOvershoot'] = self.ui.useOvershoot.isChecked()
        config['domeNorthOffset'] = self.ui.domeNorthOffset.value()
        config['domeEastOffset'] = self.ui.domeEastOffset.value()
        config['domeZoffGEM'] = self.ui.domeZoffGEM.value()
        config['offGEM'] = self.ui.offGEM.value()
        config['offLAT'] = self.ui.offLAT.value()
        config['useDomeGeometry'] = self.ui.useDomeGeometry.isChecked()
        config['automaticDome'] = self.ui.automaticDome.isChecked()
        config['useDynamicFollowing'] = self.ui.useDynamicFollowing.isChecked()
        config['settleTimeDome'] = self.ui.settleTimeDome.value()
        return True

    def setZoffGEMInMount(self):
        """
        :return:
        """
        self.app.mount.geometry.offVertGEM = self.ui.domeZoffGEM.value()
        self.ui.domeZoff10micron.setValue(self.app.mount.geometry.offVert)
        self.app.updateDomeSettings.emit()
        return True

    def setZoff10micronInMount(self):
        """
        :return:
        """
        self.app.mount.geometry.offVert = self.ui.domeZoff10micron.value()
        self.ui.domeZoffGEM.setValue(self.app.mount.geometry.offVertGEM)
        self.app.updateDomeSettings.emit()
        return True

    def setUseGeometry(self):
        """
        setUseGeometry updates the mount class with the new setting if use
        geometry for dome calculation should be used or not.

        :return: true for test purpose
        """
        if self.ui.automaticDome.isChecked():
            self.updateDomeGeometryToGui()

        self.app.mount.geometry.domeRadius = self.ui.domeRadius.value()
        self.app.dome.radius = self.ui.domeRadius.value()
        self.app.mount.geometry.offGEM = self.ui.offGEM.value()
        self.app.mount.geometry.offLAT = self.ui.offLAT.value()
        self.app.mount.geometry.offNorth = self.ui.domeNorthOffset.value()
        self.app.mount.geometry.offEast = self.ui.domeEastOffset.value()
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

    def updateDomeGeometryToGui(self):
        """
        :return: true for test purpose
        """
        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_OTA_OFFSET', 0))
        self.ui.offGEM.setValue(value)

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_DOME_RADIUS', 0))
        self.ui.domeRadius.setValue(value)

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_SHUTTER_WIDTH', 0))
        self.ui.domeClearOpening.setValue(value)

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_NORTH_DISPLACEMENT', 0))
        self.ui.domeNorthOffset.setValue(value)

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_EAST_DISPLACEMENT', 0))
        self.ui.domeEastOffset.setValue(value)

        value = float(self.app.dome.data.get('DOME_MEASUREMENTS.DM_UP_DISPLACEMENT', 0))
        self.ui.domeZoffGEM.setValue(value)
        return True

    def setDomeSettlingTime(self):
        """
        :return: true for test purpose
        """
        self.app.dome.settlingTime = self.ui.settleTimeDome.value()
        return True
