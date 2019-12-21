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
import copy
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
            'directWeather': {
                'uiDropDown': self.ui.directWeatherDevice,
                'uiSetup': None,
                'class': self.app.directWeather,
                'deviceType': None,
            },
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
                'deviceType': 'astrometry',
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
            signals.serverDisconnected.connect(self.serverDisconnected)
            signals.deviceConnected.connect(self.deviceConnected)
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

        return True

    def setupPopUp(self):
        """
        setupPopUp calculates the geometry data to place the popup centered on top of the
        parent window and call it with all necessary data. The popup is modal and we connect
        the signal of the destroyed window to update the dispatching value for all changes
        drivers

        """

        for driver in self.drivers:
            if self.sender() != self.drivers[driver]['uiSetup']:
                continue

            # calculate geometry
            geometry = self.pos().x(), self.pos().y(), self.height(), self.width()
            # get all available frameworks
            framework = self.drivers[driver]['class'].run.keys()
            # selecting the device type
            deviceType = self.drivers[driver]['deviceType']

            self.popupUi = DevicePopup(geometry=geometry,
                                       driver=driver,
                                       deviceType=deviceType,
                                       framework=framework,
                                       data=self.driversData)
            # memorizing the driver we have to update
            driverCall = driver

        # setting callback when the modal window is closed to update the configuration
        self.popupUi.destroyed.connect(lambda: self.dispatch(driverName=driverCall))

    def dispatchStopDriver(self, driver=None):
        """
        dispatchStopDriver stops the named driver.

        :return: returns status if we are finished
        """

        # if there is a change we first have to stop running drivers and reset gui
        # if it's the startup (which has no name set, we don't need to stop)
        if self.drivers[driver]['class'].name:
            self.drivers[driver]['class'].stopCommunication()
            self.app.message.emit(f'Disabled:            [{driver}]', 0)

        # stopped driver get gets neutral color
        self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)

        # disabling the driver for the overall app
        self.deviceStat[driver] = None

        # if new driver is disabled, we are finished
        if self.drivers[driver]['uiDropDown'].currentText() == 'device disabled':
            self.drivers[driver]['class'].name = ''
            return False

        return True

    def dispatchConfigDriver(self, driver=None):
        """
        dispatchConfigDriver

        :param driver:
        :return: success of start
        """

        driverData = self.driversData.get(driver, {})

        # without connection it is false, which leads to a red in gui
        self.deviceStat[driver] = False

        # now driver specific parameters will be set
        if self.drivers[driver]['uiDropDown'].currentText().startswith('indi'):
            name = driverData.get('indiName', '')
            host = (driverData.get('indiHost'),
                    int(driverData.get('indiPort')))
            showMessages = driverData.get('indiMessages', False)

            self.drivers[driver]['class'].showMessages = showMessages
            self.drivers[driver]['class'].host = host
            self.drivers[driver]['class'].framework = 'indi'

        elif self.drivers[driver]['uiDropDown'].currentText().startswith('alpaca'):
            name = driverData.get('alpacaName', '')
            host = (driverData.get('alpacaHost'),
                    int(driverData.get('alpacaPort')))

            self.drivers[driver]['class'].host = host
            self.drivers[driver]['class'].framework = 'alpaca'

        elif self.drivers[driver]['deviceType'] == 'astrometry':
            name = driver
            astrometryFramework = self.drivers[driver]['uiDropDown'].currentText()
            self.drivers[driver]['class'].framework = astrometryFramework

        else:
            name = driver

        # setting the new selected framework type and name, host
        self.drivers[driver]['class'].name = name

    def dispatchStartDriver(self, driver=None):
        """
        dispatchStartDriver

        :param driver:
        :return: success of start
        """

        # for built-in i actually not check their presence as the should function
        if self.drivers[driver]['uiDropDown'].currentText() == 'built-in':
            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_GREEN)

        # and finally start it
        self.app.message.emit(f'Enabled:             [{driver}]', 0)
        suc = self.drivers[driver]['class'].startCommunication()
        return suc

    def dispatch(self, driverName=''):
        """
        dispatch is the central method to start / stop the drivers, setting the parameters
        and managing the boot / shutdown.

        dispatch is called by signals if the user uses the dropdown to change a driver setting
        or could be called directly with a driverName to manually change the setting. this
        happens at the startup to initialize the drivers and after a popup is closed to update
        the settings for a driver.

        first dispatch will stop running drivers
        then changing the settings
        then starting the new ones

        :return: true for test purpose
        """

        for driver in self.drivers:
            # check if the call comes from gui or direct call. a call from gui has a list of
            # objects
            isGui = not isinstance(driverName, str)

            if not isGui and (driverName != driver):
                continue
            if isGui and (self.sender() != self.drivers[driver]['uiDropDown']):
                continue

            if not self.dispatchStopDriver(driver=driver):
                continue

            self.dispatchConfigDriver(driver=driver)

            suc = self.dispatchStartDriver(driver=driver)
            if not suc:
                self.app.message.emit(f'[{driver}] could not be started', 2)

        return True

    def scanValid(self, driver=None, deviceName=''):
        """
        scanValid checks if the calling device fits to the summary of all devices and gives
        back if it should be skipped

        :param deviceName:
        :param driver:
        :return:
        """

        if hasattr(self.drivers[driver]['class'], 'signals'):
            if self.sender() != self.drivers[driver]['class'].signals:
                return False
        else:
            if self.drivers[driver]['class'].name != deviceName:
                return False
        return True

    def serverDisconnected(self, deviceList):
        """
        serverDisconnected writes info to message window and recolors the status

        :param deviceList:
        :return: true for test purpose
        """

        if not deviceList:
            return False

        deviceName = list(deviceList.keys())[0]

        for driver in self.drivers:
            if not self.scanValid(driver=driver, deviceName=deviceName):
                continue

            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)
            # self.app.message.emit(f'Disconnected server: [{driver}] ', 0)
        return True

    def deviceConnected(self, deviceName):
        """
        showCoverDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :param deviceName:
        :return: true for test purpose
        """

        for driver in self.drivers:
            if not self.scanValid(driver=driver, deviceName=deviceName):
                continue

            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_GREEN)
            self.deviceStat[driver] = True
            # self.app.message.emit(f'{driver} connected', 0)
        return True

    def deviceDisconnected(self, deviceName):
        """
        showCoverDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :param deviceName:
        :return: true for test purpose
        """

        for driver in self.drivers:
            if not self.scanValid(driver=driver, deviceName=deviceName):
                continue

            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)
            self.deviceStat[driver] = False
            # self.app.message.emit(f'{driver} disconnected', 0)
        return True
