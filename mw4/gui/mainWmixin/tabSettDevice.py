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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import
from mw4.gui.devicePopupW import DevicePopup


class SettDevice(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadPool for managing async
    processing if needed.
    """

    def __init__(self):

        self.popupUi = None
        self.drivers = {
            'dome': {
                'uiDropDown': self.ui.domeDevice,
                'uiSetup': self.ui.domeSetup,
                'class': self.app.dome,
            },
            'camera': {
                'uiDropDown': self.ui.cameraDevice,
                'uiSetup': self.ui.cameraSetup,
                'class': self.app.camera,
            },
            'filter': {
                'uiDropDown': self.ui.filterDevice,
                'uiSetup': self.ui.filterSetup,
                'class': self.app.filter,
            },
            'focuser': {
                'uiDropDown': self.ui.focuserDevice,
                'uiSetup': self.ui.focuserSetup,
                'class': self.app.focuser,
            },
            'sensorWeather': {
                'uiDropDown': self.ui.sensorWeatherDevice,
                'uiSetup': self.ui.sensorWeatherSetup,
                'class': self.app.sensorWeather,
            },
            'directWeather': {
                'uiDropDown': self.ui.directWeatherDevice,
                'uiSetup': None,
                'class': self.app.directWeather,
            },
            'onlineWeather': {
                'uiDropDown': self.ui.onlineWeatherDevice,
                'uiSetup': None,
                'class': self.app.onlineWeather,
            },
            'cover': {
                'uiDropDown': self.ui.coverDevice,
                'uiSetup': self.ui.coverSetup,
                'class': self.app.cover,
            },
            'skymeter': {
                'uiDropDown': self.ui.skymeterDevice,
                'uiSetup': self.ui.skymeterSetup,
                'class': self.app.skymeter,
            },
            'telescope': {
                'uiDropDown': self.ui.telescopeDevice,
                'uiSetup': self.ui.telescopeSetup,
                'class': self.app.telescope,
            },
            'power': {
                'uiDropDown': self.ui.powerDevice,
                'uiSetup': self.ui.powerSetup,
                'class': self.app.power,
            },
            'relay': {
                'uiDropDown': self.ui.relayDevice,
                'uiSetup': None,
                'class': self.app.relay,
            },
            'astrometry': {
                'uiDropDown': self.ui.astrometryDevice,
                'uiSetup': None,
                'class': self.app.astrometry,
            },
            'remote': {
                'uiDropDown': self.ui.remoteDevice,
                'uiSetup': None,
                'class': self.app.remote,
            },
            'measure': {
                'uiDropDown': self.ui.measureDevice,
                'uiSetup': None,
                'class': self.app.measure,
            },
        }

        self.driversData = {}
        self.setupDeviceGui()

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].activated.connect(self.drivers[driver]['class'])
            if self.drivers[driver]['uiSetup'] is not None:
                self.drivers[driver]['uiSetup'].clicked.connect(self.setupPopUp)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config.get('mainW', {})
        configData = self.app.config.get('driversData', {})

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].setCurrentIndex(config.get(driver, 0))
            self.drivers[driver]['class']()

        for driver in self.drivers:
            self.driversData[driver] = configData.get(driver, {})

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config.get('mainW', {})
        configData = self.app.config.get('driversData', {})

        for driver in self.drivers:
            config[driver] = self.drivers[driver]['uiDropDown'].currentIndex()

        for driver in self.drivers:
            configData[driver] = self.driversData[driver]

        return True

    def setupDeviceGui(self):
        """
        setupRelayGui handles the dropdown lists for all devices possible in mountwizzard.
        therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        dropDowns = list(self.drivers[driver]['uiDropDown'] for driver in self.drivers)
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device selected')

        # adding special items
        self.drivers['dome']['uiDropDown'].addItem('INDI')
        self.drivers['camera']['uiDropDown'].addItem('INDI')
        self.drivers['filter']['uiDropDown'].addItem('INDI')
        self.drivers['focuser']['uiDropDown'].addItem('INDI')
        self.drivers['sensorWeather']['uiDropDown'].addItem('INDI')
        self.drivers['directWeather']['uiDropDown'].addItem('Built-In')
        self.drivers['onlineWeather']['uiDropDown'].addItem('Built-In')
        self.drivers['cover']['uiDropDown'].addItem('INDI')
        self.drivers['skymeter']['uiDropDown'].addItem('INDI')
        self.drivers['telescope']['uiDropDown'].addItem('INDI')
        self.drivers['power']['uiDropDown'].addItem('INDI')
        self.drivers['relay']['uiDropDown'].addItem('Built-In')
        for app in self.app.astrometry.solverAvailable:
            self.drivers['astrometry']['uiDropDown'].addItem(app)
        self.drivers['remote']['uiDropDown'].addItem('Built-In')
        self.drivers['measure']['uiDropDown'].addItem('Built-In')

        return True

    def setupPopUp(self):
        """

        """

        for driver in self.drivers:
            if self.sender() != self.drivers[driver]['uiSetup']:
                continue
            # calculate geometry
            posX = self.pos().x()
            posY = self.pos().y()
            height = self.height()
            width = self.width()
            geo = posX, posY, width, height

            self.popupUi = DevicePopup(geo=geo, device=driver, data=self.driversData)
            # todo: signal when Popup is finished

    def dispatch(self):
        """

        :return: true for test purpose
        """
        for driver in self.drivers:
            if self.sender() != self.drivers[driver]['uiDropDown']:
                continue

            if dropDown.currentText().startswith('Built-In'):
                self.app.message.emit(f'{driver} enabled', 0)
                self.deviceStat[driver] = False
                self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_GREEN)
                self.drivers['class'].startCommunication()

            elif dropDown.currentText().startswith('INDI'):
                self.app.message.emit(f'{driver} enabled', 0)
                self.deviceStat[driver] = False
                self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_GREEN)
                driverData = self.driversData.get('dome', {})
                self.app.dome.run['indi'].name = driverData.get('name', '')
                self.drivers['class'].startCommunication()

            else:
                self.app.message.emit(f'{driver} disabled', 0)
                self.deviceStat[driver] = None
                self.drivers['class'].stopCommunication()
                self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)
            return true

    def showIndiDisconnected(self, deviceList):
        """
        showIndiDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        if not deviceList:
            return False

        deviceName = list(deviceList.keys())[0]

        for driver in self.drivers:
            if self.drivers[driver].name != deviceName:
                continue
            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)
        return True

    def showDeviceConnected(self, deviceName):
        """
        showCoverDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        for driver in self.drivers:
            if self.drivers[driver]['class'].name != deviceName:
                continue
            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_GREEN)
            self.deviceStat[device] = True
        return True

    def showDeviceDisconnected(self, deviceName):
        """
        showCoverDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        for driver in self.drivers:
            if self.drivers[driver]['class'].name != deviceName:
                continue
            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)
            self.deviceStat[device] = False
        return True
