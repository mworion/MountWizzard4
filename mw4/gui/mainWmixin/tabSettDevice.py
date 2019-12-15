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
                'dispatch': self.domeDispatch,
            },
            'camera': {
                'uiDropDown': self.ui.cameraDevice,
                'uiSetup': self.ui.cameraSetup,
                'dispatch': self.cameraDispatch,
            },
            'filter': {
                'uiDropDown': self.ui.filterDevice,
                'uiSetup': self.ui.filterSetup,
                'dispatch': self.filterDispatch,
            },
            'focuser': {
                'uiDropDown': self.ui.focuserDevice,
                'uiSetup': self.ui.focuserSetup,
                'dispatch': self.focuserDispatch,
            },
            'sensorWeather': {
                'uiDropDown': self.ui.sensorWeatherDevice,
                'uiSetup': self.ui.sensorWeatherSetup,
                'dispatch': self.sensorWeatherDispatch,
            },
            'directWeather': {
                'uiDropDown': self.ui.directWeatherDevice,
                'uiSetup': None,
                'dispatch': self.directWeatherDispatch,
            },
            'onlineWeather': {
                'uiDropDown': self.ui.onlineWeatherDevice,
                'uiSetup': None,
                'dispatch': self.onlineWeatherDispatch,
            },
            'cover': {
                'uiDropDown': self.ui.coverDevice,
                'uiSetup': self.ui.coverSetup,
                'dispatch': self.coverDispatch,
            },
            'skymeter': {
                'uiDropDown': self.ui.skymeterDevice,
                'uiSetup': self.ui.skymeterSetup,
                'dispatch': self.skymeterDispatch,
            },
            'telescope': {
                'uiDropDown': self.ui.telescopeDevice,
                'uiSetup': self.ui.telescopeSetup,
                'dispatch': self.telescopeDispatch,
            },
            'power': {
                'uiDropDown': self.ui.powerDevice,
                'uiSetup': self.ui.powerSetup,
                'dispatch': self.powerDispatch,
            },
            'relay': {
                'uiDropDown': self.ui.relayDevice,
                'uiSetup': None,
                'dispatch': self.relayDispatch,
            },
            'astrometry': {
                'uiDropDown': self.ui.astrometryDevice,
                'uiSetup': None,
                'dispatch': self.astrometryDispatch,
            },
            'remote': {
                'uiDropDown': self.ui.remoteDevice,
                'uiSetup': None,
                'dispatch': self.remoteDispatch,
            },
            'measure': {
                'uiDropDown': self.ui.measureDevice,
                'uiSetup': None,
                'dispatch': self.measureDispatch,
            },
        }

        self.driversData = {
            'sensorWeather': {
                'indiHost': 'astro-comp.fritz.box',
                'indiPort': '7624',
                'indiName': '-',
                'indiNameList': ['indi 1', 'indi 2'],
            }
        }

        self.setupDeviceGui()

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].activated.connect(self.drivers[driver]['dispatch'])
            if self.drivers[driver]['uiSetup'] is not None:
                self.drivers[driver]['uiSetup'].clicked.connect(self.setupPopUp)

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
            self.driversData[driver]['driverType'] = self.drivers[driver]['type']

            self.popupUi = DevicePopup(geo=geo, device=driver, data=self.driversData)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].setCurrentIndex(config.get(driver, 0))
            self.drivers[driver]['dispatch']()

        for driver in self.driverData:
            self.driverData[driver] = config.get(driver, {})

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for driver in self.drivers:
            config[driver] = self.drivers[driver]['uiDropDown'].currentIndex()
        for driver in self.driverData:
            config[driver] = self.driverData[driver]

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

    def relayDispatch(self):
        """
        relayDispatch allows to run the relay box.

        :return: success for test
        """

        if self.ui.relayDevice.currentText().startswith('Built-In'):
            self.app.message.emit('Relay enabled', 0)
            self.deviceStat['relay'] = True
            self.app.relay.startTimers()
            self.ui.relayDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.message.emit('Relay disabled', 0)
            self.deviceStat['relay'] = False
            self.app.relay.stopTimers()
            self.ui.relayDevice.setStyleSheet(self.BACK_NORM)

        return True

    def remoteDispatch(self):
        """
        remoteAccess enables or disables the remote access

        :return: true for test purpose
        """

        if self.ui.remoteDevice.currentText() == 'Built-In':
            self.app.remote.startRemote()
            self.app.message.emit('Remote enabled', 0)
            self.deviceStat['remote'] = True
            self.ui.remoteDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.remote.stopRemote()
            self.app.message.emit('Remote disabled', 0)
            self.deviceStat['remote'] = None
            self.ui.remoteDevice.setStyleSheet(self.BACK_NORM)

        return True

    def measureDispatch(self):
        """
        measureDispatch enables or disables the on board measurement process

        :return: true for test purpose
        """

        if self.ui.measureDevice.currentText().startswith('Built-In'):
            self.app.measure.startMeasurement()
            self.app.message.emit('Measurement enabled', 0)
            self.deviceStat['measure'] = True
            self.ui.measureDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.measure.stopMeasurement()
            self.app.message.emit('Measurement disabled', 0)
            self.deviceStat['measure'] = None
            self.ui.measureDevice.setStyleSheet(self.BACK_NORM)

        return True

    def domeDispatch(self):
        """
        domeDispatch selects the type of device for dome measures and start / stop
        them.
        in addition this function enables and disables other gui functions, which rely on
        the presence of a running driver

        :return: true for test purpose
        """

        if self.ui.domeDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('dome', {})
            self.app.dome.run['indi'].name = driverData.get('name', '')
            self.app.message.emit('Dome enabled', 0)
            self.deviceStat['dome'] = False
        else:
            self.app.dome.run['indi'].name = ''
            self.app.message.emit('Dome disabled', 0)
            self.deviceStat['dome'] = None

        return True

    def cameraDispatch(self):
        """
        cameraDispatch selects the type of device for camera and start / stop them.
        in addition this function enables and disables other gui functions, which rely on
        the presence of a running driver

        :return: true for test purpose
        """

        if self.ui.cameraDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('camera', {})
            self.app.camera.name = driverData.get('name', '')
            self.app.message.emit('Camera enabled', 0)
            self.deviceStat['camera'] = False
        else:
            self.app.camera.name = ''
            self.app.message.emit('Camera disabled', 0)
            self.deviceStat['camera'] = None

        return True

    def filterDispatch(self):
        """
        filterDispatch selects the type of device for filterwheel settings.

        :return: true for test purpose
        """

        if self.ui.filterDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('filter', {})
            self.app.filter.name = driverData.get('name', '')
            self.app.message.emit('Filter enabled', 0)
            self.deviceStat['filter'] = False
        else:
            self.app.filter.name = ''
            self.app.message.emit('Filter disabled', 0)
            self.deviceStat['filter'] = None

    def focuserDispatch(self):
        """
        focuserDispatch selects the type of device for focuser settings.

        :return: true for test purpose
        """

        if self.ui.focuserDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('focuser', {})
            self.app.focuser.name = driverData.get('name', '')
            self.app.message.emit('Focuser enabled', 0)
            self.deviceStat['focuser'] = False
        else:
            self.app.focuser.name = ''
            self.app.message.emit('Focuser disabled', 0)
            self.deviceStat['focuser'] = None

    def sensorWeatherDispatch(self):
        """
        sensorWeatherDispatch selects the type of device for weather measures and
        start / stop them. in addition this function enables and disables other gui
        functions, which rely on the presence of a running driver

        :return: true for test purpose
        """

        if self.ui.sensorWeatherDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('sensorWeather', {})
            self.app.sensorWeather.name = driverData.get('name', '')
            self.app.message.emit('Sensor Weather enabled', 0)
            self.deviceStat['sensorWeather'] = False
        else:
            self.app.sensorWeather.name = ''
            self.app.message.emit('Sensor Weather disabled', 0)
            self.deviceStat['sensorWeather'] = None

        return True

    def onlineWeatherDispatch(self):
        """

        :return:
        """

        if self.ui.onlineWeatherDevice.currentText().startswith('Built-In'):
            self.app.onlineWeather.startCommunication()
            self.app.message.emit('Weather enabled', 0)
            self.deviceStat['onlineWeather'] = True
            self.ui.onlineWeatherDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.onlineWeather.stopCommunication()
            self.app.message.emit('Weather disabled', 0)
            self.deviceStat['onlineWeather'] = None
            self.ui.onlineWeatherDevice.setStyleSheet(self.BACK_NORM)

        return True

    def directWeatherDispatch(self):
        """

        :return:
        """

        if self.ui.directWeatherDevice.currentText().startswith('Built-In'):
            self.app.message.emit('Direct Weather enabled', 0)
            self.deviceStat['directWeather'] = True
            self.ui.directWeatherDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.message.emit('Direct Weather disabled', 0)
            self.deviceStat['directWeather'] = None
            self.ui.directWeatherDevice.setStyleSheet(self.BACK_NORM)

        return True

    def skymeterDispatch(self):
        """
        skymeterDispatch selects the type of device for skymeter measures and
        start / stop them.

        :return: true for test purpose
        """

        if self.ui.skymeterDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('skymeter', {})
            self.app.skymeter.name = driverData.get('name', '')
            self.app.message.emit('Skymeter enabled', 0)
            self.deviceStat['skymeter'] = False
        else:
            self.app.skymeter.name = ''
            self.app.message.emit('Skymeter disabled', 0)
            self.deviceStat['skymeter'] = None

        return True

    def coverDispatch(self):
        """
        coverDispatch selects the type of device for cover status and start / stop
        them.

        :return: true for test purpose
        """

        if self.ui.coverDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('cover', {})
            self.app.cover.name = driverData.get('name', '')
            self.app.message.emit('Cover enabled', 0)
            self.deviceStat['cover'] = False
        else:
            self.app.cover.name = ''
            self.app.message.emit('Cover disabled', 0)
            self.deviceStat['cover'] = None

        return True

    def telescopeDispatch(self):
        """
        telescopeDispatch selects the type of device for telescope settings.

        :return: true for test purpose
        """

        if self.ui.telescopeDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('telescope', {})
            self.app.telescope.name = driverData.get('name', '')
            self.app.message.emit('Telescope enabled', 0)
            self.deviceStat['telescope'] = False
        else:
            self.app.telescope.name = ''
            self.app.message.emit('Telescope disabled', 0)
            self.deviceStat['telescope'] = None

        return True

    def powerDispatch(self):
        """
        powerDispatch selects the type of device for power measures and start / stop
        them.

        :return: true for test purpose
        """

        if self.ui.powerDevice.currentText().startswith('INDI'):
            driverData = self.driversData.get('power', {})
            self.app.power.name = driverData.get('name', '')
            self.app.message.emit('Power enabled', 0)
            self.deviceStat['power'] = False
        else:
            self.app.power.name = ''
            self.app.message.emit('Power disabled', 0)
            self.deviceStat['power'] = None

        return True

    def astrometryDispatch(self):
        """
        astrometryDispatch selects the type of device for astrometry.

        :return: true for test purpose
        """

        if self.ui.astrometryDevice.currentText() in self.app.astrometry.solverAvailable:
            self.app.astrometry.solverSelected = self.ui.astrometryDevice.currentText()
            self.ui.astrometryDevice.setStyleSheet(self.BACK_GREEN)
            self.deviceStat['astrometry'] = True
            self.app.message.emit('Astrometry enabled', 0)
        else:
            self.app.message.emit('Astrometry disabled', 0)
            self.deviceStat['astrometry'] = None
            self.ui.astrometryDevice.setStyleSheet(self.BACK_NORM)

        return True
