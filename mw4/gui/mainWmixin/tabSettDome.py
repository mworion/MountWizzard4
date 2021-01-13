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
# written in python3, (c) 2019-2021 by mworion
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
        self.ui.domeRadius.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.offGEM.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.offLAT.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.domeEastOffset.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.domeNorthOffset.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.domeZoffGEM.valueChanged.connect(self.setZoffGEMInMount)
        self.ui.domeZoff10micron.valueChanged.connect(self.setZoff10micronInMount)
        self.ui.domeShutterWidth.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.settleTimeDome.valueChanged.connect(self.setDomeSettlingTime)
        self.ui.checkUseDomeGeometry.clicked.connect(self.setUseDomeGeometry)
        self.ui.copyFromDomeDriver.clicked.connect(self.updateDomeGeometryToGui)
        self.app.mount.signals.firmwareDone.connect(self.setUseGeometryInMount)
        self.app.mount.signals.firmwareDone.connect(self.setZoffGEMInMount)

        self.ui.domeRadius.valueChanged.connect(self.tab1)
        self.ui.domeNorthOffset.valueChanged.connect(self.tab2)
        self.ui.domeEastOffset.valueChanged.connect(self.tab3)
        self.ui.domeZoffGEM.valueChanged.connect(self.tab4)
        self.ui.domeZoff10micron.valueChanged.connect(self.tab5)
        self.ui.offGEM.valueChanged.connect(self.tab6)
        self.ui.offLAT.valueChanged.connect(self.tab7)
        self.ui.domeShutterWidth.valueChanged.connect(self.tab8)
        self.app.update1s.connect(self.updateShutterStatGui)
        self.ui.domeAbortSlew.clicked.connect(self.domeAbortSlew)
        self.ui.domeOpenShutter.clicked.connect(self.domeOpenShutter)
        self.ui.domeCloseShutter.clicked.connect(self.domeCloseShutter)

    def tab1(self):
        self.ui.tabDomeExplain.setCurrentIndex(0)
        self.ui.tabDomeExplain.setStyleSheet(self.getStyle())

    def tab2(self):
        self.ui.tabDomeExplain.setCurrentIndex(1)
        self.ui.tabDomeExplain.setStyleSheet(self.getStyle())

    def tab3(self):
        self.ui.tabDomeExplain.setCurrentIndex(2)
        self.ui.tabDomeExplain.setStyleSheet(self.getStyle())

    def tab4(self):
        self.ui.tabDomeExplain.setCurrentIndex(3)
        self.ui.tabDomeExplain.setStyleSheet(self.getStyle())

    def tab5(self):
        self.ui.tabDomeExplain.setCurrentIndex(4)
        self.ui.tabDomeExplain.setStyleSheet(self.getStyle())

    def tab6(self):
        self.ui.tabDomeExplain.setCurrentIndex(5)
        self.ui.tabDomeExplain.setStyleSheet(self.getStyle())

    def tab7(self):
        self.ui.tabDomeExplain.setCurrentIndex(6)
        self.ui.tabDomeExplain.setStyleSheet(self.getStyle())

    def tab8(self):
        self.ui.tabDomeExplain.setCurrentIndex(7)
        self.ui.tabDomeExplain.setStyleSheet(self.getStyle())

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.domeShutterWidth.setValue(config.get('domeShutterWidth', 0.2))
        self.ui.domeNorthOffset.setValue(config.get('domeNorthOffset', 0))
        self.ui.domeEastOffset.setValue(config.get('domeEastOffset', 0))
        self.ui.domeZoffGEM.setValue(config.get('domeZoffGEM', 0))
        self.ui.offGEM.setValue(config.get('offGEM', 0))
        self.ui.offLAT.setValue(config.get('offLAT', 0))
        self.ui.domeRadius.setValue(config.get('domeRadius', 1.5))
        self.ui.checkUseDomeGeometry.setChecked(config.get('checkUseDomeGeometry', False))
        self.ui.checkAutomaticDome.setChecked(config.get('checkAutomaticDome', False))
        self.ui.settleTimeDome.setValue(config.get('settleTimeDome', 0))
        self.setUseDomeGeometry()
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
        config['domeShutterWidth'] = self.ui.domeShutterWidth.value()
        config['domeNorthOffset'] = self.ui.domeNorthOffset.value()
        config['domeEastOffset'] = self.ui.domeEastOffset.value()
        config['domeZoffGEM'] = self.ui.domeZoffGEM.value()
        config['offGEM'] = self.ui.offGEM.value()
        config['offLAT'] = self.ui.offLAT.value()
        config['checkUseDomeGeometry'] = self.ui.checkUseDomeGeometry.isChecked()
        config['checkAutomaticDome'] = self.ui.checkAutomaticDome.isChecked()
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

    def setUseGeometryInMount(self):
        """
        setUseGeometryInMount updates the mount class with the new setting if use
        geometry for dome calculation should be used or not.

        :return: true for test purpose
        """
        if self.ui.checkAutomaticDome.isChecked():
            self.updateDomeGeometryToGui()

        self.app.mount.geometry.domeRadius = self.ui.domeRadius.value()
        self.app.mount.geometry.offGEM = self.ui.offGEM.value()
        self.app.mount.geometry.offLAT = self.ui.offLAT.value()
        self.app.mount.geometry.offNorth = self.ui.domeNorthOffset.value()
        self.app.mount.geometry.offEast = self.ui.domeEastOffset.value()
        self.app.dome.domeShutterWidth = self.ui.domeShutterWidth.value()
        self.app.updateDomeSettings.emit()
        return True

    def setUseDomeGeometry(self):
        """
        :return: True for test purpose
        """
        useGeometry = self.ui.checkUseDomeGeometry.isChecked()
        self.app.dome.useGeometry = useGeometry
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
        self.ui.domeShutterWidth.setValue(value)

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

    def updateShutterStatGui(self):
        """
        :return: True for test purpose
        """
        value = self.app.dome.data.get('DOME_SHUTTER.SHUTTER_OPEN', None)
        if value is True:
            self.changeStyleDynamic(self.ui.domeOpenShutter, 'running', True)
            self.changeStyleDynamic(self.ui.domeCloseShutter, 'running', False)
        elif value is False:
            self.changeStyleDynamic(self.ui.domeOpenShutter, 'running', False)
            self.changeStyleDynamic(self.ui.domeCloseShutter, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.domeOpenShutter, 'running', False)
            self.changeStyleDynamic(self.ui.domeCloseShutter, 'running', False)

        value = self.app.dome.data.get('Status.Shutter', None)
        if value:
            self.ui.domeShutterStatusText.setText(value)
        return True

    def domeAbortSlew(self):
        """
        :return:
        """
        suc = self.app.dome.abortSlew()
        if not suc:
            self.app.message.emit('Dome slew abort could not be executed', 2)

        return suc

    def domeOpenShutter(self):
        """
        :return:
        """
        suc = self.app.dome.openShutter()
        if not suc:
            self.app.message.emit('Dome open shutter could not be executed', 2)

        return suc

    def domeCloseShutter(self):
        """
        :return:
        """
        suc = self.app.dome.closeShutter()
        if not suc:
            self.app.message.emit('Dome close shutter could not be executed', 2)

        return suc
