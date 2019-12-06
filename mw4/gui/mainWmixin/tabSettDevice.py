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


class SettDevice(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadPool for managing async
    processing if needed.
    """

    def __init__(self):
        self.drivers = {
            'dome': {
                'uiDriver': self.ui.domeDevice,
                'dispatch': self.domeDispatch,
            },
            'camera': {
                'uiDriver': self.ui.cameraDevice,
                'dispatch': self.cameraDispatch,
            },
            'filterwheel': {
                'uiDriver': self.ui.filterwheelDevice,
                'dispatch': self.filterwheelDispatch,
            },
            'sensorWeather': {
                'uiDriver': self.ui.sensorWeatherDevice,
                'dispatch': self.sensorWeatherDispatch,
            },
            'directWeather': {
                'uiDriver': self.ui.directWeatherDevice,
                'dispatch': self.directWeatherDispatch,
            },
            'onlineWeather': {
                'uiDriver': self.ui.onlineWeatherDevice,
                'dispatch': self.onlineWeatherDispatch,
            },
            'cover': {
                'uiDriver': self.ui.coverDevice,
                'dispatch': self.coverDispatch,
            },
            'skymeter': {
                'uiDriver': self.ui.skymeterDevice,
                'dispatch': self.skymeterDispatch,
            },
            'telescope': {
                'uiDriver': self.ui.telescopeDevice,
                'dispatch': self.telescopeDispatch,
            },
            'power': {
                'uiDriver': self.ui.powerDevice,
                'dispatch': self.powerDispatch,
            },
            'relay': {
                'uiDriver': self.ui.relayDevice,
                'dispatch': self.relayDispatch,
            },
            'astrometry': {
                'uiDriver': self.ui.astrometryDevice,
                'dispatch': self.astrometryDispatch,
            },
            'remote': {
                'uiDriver': self.ui.remoteDevice,
                'dispatch': self.remoteDispatch,
            },
            'measure': {
                'uiDriver': self.ui.measureDevice,
                'dispatch': self.measureDispatch,
            },
        }

        self.setupDeviceGui()

        for driver in self.drivers:
            self.drivers[driver]['uiDriver'].activated.connect(self.drivers[driver]['dispatch'])

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']

        for driver in self.drivers:
            self.drivers[driver]['uiDriver'].setCurrentIndex(config.get(driver, 0))
            self.drivers[driver]['dispatch']()

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
            config[driver] = self.drivers[driver]['uiDriver'].currentIndex()

        return True

    def setupDeviceGui(self):
        """
        setupRelayGui handles the dropdown lists for all devices possible in mountwizzard.
        therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        dropDowns = list(self.drivers[driver]['uiDriver'] for driver in self.drivers)
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device selected')

        # adding special items
        self.drivers['dome']['uiDriver'].addItem('INDI')
        self.drivers['camera']['uiDriver'].addItem('INDI')
        self.drivers['sensorWeather']['uiDriver'].addItem('INDI')
        self.drivers['directWeather']['uiDriver'].addItem('Built-In')
        self.drivers['onlineWeather']['uiDriver'].addItem('Built-In')
        self.drivers['cover']['uiDriver'].addItem('INDI')
        self.drivers['skymeter']['uiDriver'].addItem('INDI')
        self.drivers['telescope']['uiDriver'].addItem('INDI')
        self.drivers['power']['uiDriver'].addItem('INDI')
        self.drivers['relay']['uiDriver'].addItem('Built-In')
        for app in self.app.astrometry.solverAvailable:
            self.drivers['astrometry']['uiDriver'].addItem(app)
        self.drivers['remote']['uiDriver'].addItem('Built-In')
        self.drivers['measure']['uiDriver'].addItem('Built-In')

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
            self.app.dome.name = self.ui.domeDeviceName.currentText()
            self.app.message.emit('Dome enabled', 0)
            self.deviceStat['dome'] = False
        else:
            self.app.dome.name = ''
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
            self.app.camera.name = self.ui.cameraDeviceName.currentText()
            self.app.message.emit('Camera enabled', 0)
            self.deviceStat['camera'] = False
        else:
            self.app.camera.name = ''
            self.app.message.emit('Camera disabled', 0)
            self.deviceStat['camera'] = None

        return True

    def filterwheelDispatch(self):
        pass

    def sensorWeatherDispatch(self):
        """
        sensorWeatherDispatch selects the type of device for weather measures and
        start / stop them. in addition this function enables and disables other gui
        functions, which rely on the presence of a running driver

        :return: true for test purpose
        """

        if self.ui.sensorWeatherDevice.currentText().startswith('INDI'):
            self.app.sensorWeather.name = self.ui.sensorWeatherDeviceName.currentText()
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
            self.app.skymeter.name = self.ui.skymeterDeviceName.currentText()
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
            self.app.cover.name = self.ui.coverDeviceName.currentText()
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
            self.app.telescope.name = self.ui.telescopeDeviceName.currentText()
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
            self.app.power.name = self.ui.powerDeviceName.currentText()
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
