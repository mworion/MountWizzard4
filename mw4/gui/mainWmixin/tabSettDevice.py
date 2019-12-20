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
                'deviceType': 'dome',
            },
            'camera': {
                'uiDropDown': self.ui.cameraDevice,
                'uiSetup': self.ui.cameraSetup,
                'class': self.app.camera,
                'deviceType': 'camera',
            },
            'filter': {
                'uiDropDown': self.ui.filterDevice,
                'uiSetup': self.ui.filterSetup,
                'class': self.app.filter,
                'deviceType': 'filter',
            },
            'focuser': {
                'uiDropDown': self.ui.focuserDevice,
                'uiSetup': self.ui.focuserSetup,
                'class': self.app.focuser,
                'deviceType': 'focuser',
            },
            'sensorWeather': {
                'uiDropDown': self.ui.sensorWeatherDevice,
                'uiSetup': self.ui.sensorWeatherSetup,
                'class': self.app.sensorWeather,
                'deviceType': 'weather',
            },
            #'directWeather': {
            #    'uiDropDown': self.ui.directWeatherDevice,
            #    'uiSetup': None,
            #    'class': None,
            #    'deviceType': None,
            #},
            'onlineWeather': {
                'uiDropDown': self.ui.onlineWeatherDevice,
                'uiSetup': None,
                'class': self.app.onlineWeather,
                'deviceType': None,
            },
            'cover': {
                'uiDropDown': self.ui.coverDevice,
                'uiSetup': self.ui.coverSetup,
                'class': self.app.cover,
                'deviceType': 'cover',
            },
            'skymeter': {
                'uiDropDown': self.ui.skymeterDevice,
                'uiSetup': self.ui.skymeterSetup,
                'class': self.app.skymeter,
                'deviceType': 'weather',
            },
            'telescope': {
                'uiDropDown': self.ui.telescopeDevice,
                'uiSetup': self.ui.telescopeSetup,
                'class': self.app.telescope,
                'deviceType': 'telescope',
            },
            'power': {
                'uiDropDown': self.ui.powerDevice,
                'uiSetup': self.ui.powerSetup,
                'class': self.app.power,
                'deviceType': None,
            },
            'relay': {
                'uiDropDown': self.ui.relayDevice,
                'uiSetup': None,
                'class': self.app.relay,
                'deviceType': None,
            },
            'astrometry': {
                'uiDropDown': self.ui.astrometryDevice,
                'uiSetup': None,
                'class': self.app.astrometry,
                'deviceType': None,
            },
            'remote': {
                'uiDropDown': self.ui.remoteDevice,
                'uiSetup': None,
                'class': self.app.remote,
                'deviceType': None,
            },
            'measure': {
                'uiDropDown': self.ui.measureDevice,
                'uiSetup': None,
                'class': self.app.measure,
                'deviceType': None,
            },
        }

        self.driversData = {}
        self.setupDeviceGui()

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].activated.connect(self.dispatch)
            if self.drivers[driver]['uiSetup'] is not None:
                self.drivers[driver]['uiSetup'].clicked.connect(self.setupPopUp)

            if not hasattr(self.drivers[driver]['class'], 'signals'):
                continue

            signals = self.drivers[driver]['class'].signals
            if hasattr(signals, 'serverDisconnected'):
                signals.serverDisconnected.connect(self.serverDisconnected)
            if hasattr(signals, 'deviceConnected'):
                signals.deviceConnected.connect(self.deviceConnected)
            if hasattr(signals, 'deviceDisconnected'):
                signals.deviceDisconnected.connect(self.deviceDisconnected)

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
            self.driversData[driver] = configData.get(driver, {})

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].setCurrentIndex(config.get(driver, 0))
            self.dispatch(driverName=driver)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        if 'driversData' not in self.app.config:
            self.app.config['driversData'] = {}
        configData = self.app.config['driversData']

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

        # all dropdown have disabled as capability
        dropDowns = list(self.drivers[driver]['uiDropDown'] for driver in self.drivers)
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('device disabled')

        # adding driver items with applicable framework
        for driver in self.drivers:
            if not hasattr(self.drivers[driver]['class'], 'run'):
                continue
            for framework in self.drivers[driver]['class'].run.keys():
                self.drivers[driver]['uiDropDown'].addItem(framework)

        # build-in drivers
        # self.drivers['directWeather']['uiDropDown'].addItem('built-in')
        self.drivers['onlineWeather']['uiDropDown'].addItem('built-in')
        self.drivers['relay']['uiDropDown'].addItem('built-in')
        self.drivers['remote']['uiDropDown'].addItem('built-in')
        self.drivers['measure']['uiDropDown'].addItem('built-in')
        for app in self.app.astrometry.solverAvailable:
            self.drivers['astrometry']['uiDropDown'].addItem(app)

        return True

    def setupPopUp(self):
        """
        setupPopUp calculates the geometry data to place the popup centered on top of the
        parent window and call it with all necessary data, n

        """

        for driver in self.drivers:
            if self.sender() != self.drivers[driver]['uiSetup']:
                continue

            # calculate geometry
            posX = self.pos().x()
            posY = self.pos().y()
            height = self.height()
            width = self.width()
            geometry = posX, posY, width, height

            # get framework
            # todo check if attribute checking is necessary
            if hasattr(self.drivers[driver]['class'], 'run'):
                framework = self.drivers[driver]['class'].run.keys()
            else:
                framework = {}
            deviceType = self.drivers[driver]['deviceType']

            self.popupUi = DevicePopup(geometry=geometry,
                                       driver=driver,
                                       deviceType=deviceType,
                                       framework=framework,
                                       data=self.driversData)
            # todo: signal when Popup is finished

    def dispatch(self, driverName=''):
        """

        :return: true for test purpose
        """

        for driver in self.drivers:

            driverObj = self.drivers[driver]

            # check if the call comes from gui or direct call
            isGui = not isinstance(driverName, str)
            if not isGui and (driverName != driver):
                continue
            if isGui and (self.sender() != driverObj['uiDropDown']):
                continue

            # if not driver is selected, we stop all running processes and stop
            impl = ['indi', 'buil', 'alpa']
            if driverObj['uiDropDown'].currentText()[:4] not in impl:
                self.app.message.emit(f'{driver} disabled', 0)
                self.deviceStat[driver] = None
                driverObj['uiDropDown'].setStyleSheet(self.BACK_NORM)
                if driverObj['class'] is not None:
                    driverObj['class'].stopCommunication()
                continue

            # setting processes to run
            self.app.message.emit(f'{driver} enabled', 0)
            # without connection it is first red
            self.deviceStat[driver] = False
            # driverObj['uiDropDown'].setStyleSheet(self.BACK_GREEN)

            # depending on the type different setups have to be made

            driverData = self.driversData.get(driver, {})
            dropDownText = driverObj['uiDropDown'].currentText()

            if dropDownText.startswith('indi'):
                framework = 'indi'
                name = driverData.get('indiName', '')
                driverObj['class'].showMessages = driverData.get('indiMessages', False)
                host = (driverData.get('indiHost'), int(driverData.get('indiPort')))

            elif dropDownText.startswith('alpaca'):
                framework = 'alpaca'
                name = driverData.get('alpacaName', 0)
                host = (driverData.get('alpacaHost'), int(driverData.get('alpacaPort')))

            else:
                name = driver

            driverObj['class'].framework = framework

            if framework in ['alpaca', 'indi']:
                driverObj['class'].name = name
                driverObj['class'].host = host

            # and finally start it
            if driverObj['class'] is not None:
                suc = driverObj['class'].startCommunication()
                if not suc:
                    self.app.message.emit(f'{driver} could not be started', 2)

            return True

    def serverDisconnected(self, deviceList):
        """
        serverDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        if not deviceList:
            return False

        deviceName = list(deviceList.keys())[0]

        for driver in self.drivers:
            if self.drivers[driver]['class'].name != deviceName:
                continue

            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)
            self.app.message.emit(f'server {driver} disconnected', 0)
        return True

    def deviceConnected(self, deviceName):
        """
        showCoverDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        for driver in self.drivers:
            if self.drivers[driver]['class'].name != deviceName:
                continue

            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_GREEN)
            self.deviceStat[driver] = True
            self.app.message.emit(f'{driver} connected', 0)
        return True

    def deviceDisconnected(self, deviceName):
        """
        showCoverDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        for driver in self.drivers:
            if self.drivers[driver]['class'].name != deviceName:
                continue

            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)
            self.deviceStat[driver] = False
            self.app.message.emit(f'{driver} disconnected', 0)
        return True
