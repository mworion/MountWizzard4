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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
# local import


class SettDome(object):
    """
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

        self.ui.domeRadius.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.offGEM.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.offLAT.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.domeEastOffset.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.domeNorthOffset.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.domeVerticalOffset.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.domeShutterWidth.valueChanged.connect(self.setUseGeometryInMount)
        self.ui.settleTimeDome.valueChanged.connect(self.setDomeSettlingTime)
        self.ui.checkUseDomeGeometry.clicked.connect(self.setUseDomeGeometry)
        self.ui.copyFromDomeDriver.clicked.connect(self.updateDomeGeometryToGui)
        self.app.mount.signals.firmwareDone.connect(self.setUseGeometryInMount)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']

        self.ui.domeRadius.setValue(config.get('domeRadius', 1.5))
        self.ui.domeShutterWidth.setValue(config.get('domeShutterWidth', 0.2))
        self.ui.domeNorthOffset.setValue(config.get('domeNorthOffset', 0))
        self.ui.domeEastOffset.setValue(config.get('domeEastOffset', 0))
        self.ui.domeVerticalOffset.setValue(config.get('domeVerticalOffset', 0))
        self.ui.offGEM.setValue(config.get('offGEM', 0))
        self.ui.offLAT.setValue(config.get('offLAT', 0))
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
        config['domeVerticalOffset'] = self.ui.domeVerticalOffset.value()
        config['offGEM'] = self.ui.offGEM.value()
        config['offLAT'] = self.ui.offLAT.value()
        config['checkUseDomeGeometry'] = self.ui.checkUseDomeGeometry.isChecked()
        config['checkAutomaticDome'] = self.ui.checkAutomaticDome.isChecked()
        config['settleTimeDome'] = self.ui.settleTimeDome.value()

        return True

    def setUseGeometryInMount(self):
        """
        setUseGeometryInMount updates the mount class with the new setting if use geometry for
        dome calculation should be used or not.

        :return: true for test purpose
        """

        if self.ui.checkAutomaticDome.isChecked():
            self.updateDomeGeometryToGui()

        value = self.ui.domeRadius.value()
        self.app.mount.geometry.domeRadius = value

        if value < 0.5:
            self.app.message.emit('Critical dome radius, please check', 2)

        self.app.mount.geometry.offGEM = self.ui.offGEM.value()
        self.app.mount.geometry.offLAT = self.ui.offLAT.value()
        self.app.mount.geometry.offNorth = self.ui.domeNorthOffset.value()
        self.app.mount.geometry.offEast = self.ui.domeEastOffset.value()
        self.app.mount.geometry.offVert = self.ui.domeVerticalOffset.value()
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
        updateDomeGeometryToGui takes the information gathered from the driver and programs
        them into the mount class and gui for later use.

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
        self.ui.domeVerticalOffset.setValue(value)

        return True

    def setDomeSettlingTime(self):
        """

        :return: true for test purpose
        """

        self.app.dome.settlingTime = self.ui.settleTimeDome.value()

        return True
