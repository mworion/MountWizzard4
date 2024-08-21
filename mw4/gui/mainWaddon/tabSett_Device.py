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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
from functools import partial

# external packages
import PySide6.QtCore
import PySide6.QtWidgets

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.devicePopupW import DevicePopup


class SettDevice(MWidget):
    """
    devices types in self.drivers are name related to ascom definitions

    architecture:
    - all properties are stored in the config dict as main source.
    - when starting, all gui elements will be populated based on the entries of config
    - all drivers were initialised with the content of config dict
    - if we setup a new device, data of device is gathered for the popup from config
    - when closing the popup, result data will be stored in config
    - if there is no default data for a driver in config dict, it will be retrieved from the
      driver

    sequence standard:
        loading config dict
        load driver default setup from driver if not present in config
        initialize gui
        initialize driver
        start drivers

    sequence popup:
        initialize popup data
        call popup modal
        popup close
        if cancel -> finished
        store data in config
        stop changed driver
        start new driver

    sequence dropdown:
        search driver
        if no driver -> finished
        stop changed driver
        if driver = "device disabled" -> finished
        start new driver
    """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.devicePopup = None

        self.drivers = {
            'dome': {
                'uiDropDown': self.ui.domeDevice,
                'uiSetup': self.ui.domeSetup,
                'class': self.app.dome,
                'deviceType': 'dome',
            },
            'cover': {
                'uiDropDown': self.ui.coverDevice,
                'uiSetup': self.ui.coverSetup,
                'class': self.app.cover,
                'deviceType': 'covercalibrator',
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
                'deviceType': 'filterwheel',
            },
            'focuser': {
                'uiDropDown': self.ui.focuserDevice,
                'uiSetup': self.ui.focuserSetup,
                'class': self.app.focuser,
                'deviceType': 'focuser',
            },
            'sensor1Weather': {
                'uiDropDown': self.ui.sensor1WeatherDevice,
                'uiSetup': self.ui.sensor1WeatherSetup,
                'class': self.app.sensor1Weather,
                'deviceType': 'observingconditions',
            },
            'sensor2Weather': {
                'uiDropDown': self.ui.sensor2WeatherDevice,
                'uiSetup': self.ui.sensor2WeatherSetup,
                'class': self.app.sensor2Weather,
                'deviceType': 'observingconditions',
            },
            'sensor3Weather': {
                'uiDropDown': self.ui.sensor3WeatherDevice,
                'uiSetup': self.ui.sensor3WeatherSetup,
                'class': self.app.sensor3Weather,
                'deviceType': 'observingconditions',
            },
            'onlineWeather': {
                'uiDropDown': self.ui.onlineWeatherDevice,
                'uiSetup': self.ui.onlineWeatherSetup,
                'class': self.app.onlineWeather,
                'deviceType': 'observingconditions',
            },
            'directWeather': {
                'uiDropDown': self.ui.directWeatherDevice,
                'uiSetup': None,
                'class': self.app.directWeather,
                'deviceType': None,
            },
            'seeingWeather': {
                'uiDropDown': self.ui.seeingWeatherDevice,
                'uiSetup': self.ui.seeingWeatherSetup,
                'class': self.app.seeingWeather,
                'deviceType': 'observingconditions',
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
                'deviceType': 'switch',
            },
            'relay': {
                'uiDropDown': self.ui.relayDevice,
                'uiSetup': self.ui.relaySetup,
                'class': self.app.relay,
                'deviceType': None,
            },
            'plateSolve': {
                'uiDropDown': self.ui.plateSolveDevice,
                'uiSetup': self.ui.plateSolveSetup,
                'class': self.app.plateSolve,
                'deviceType': 'plateSolve',
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

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].activated.connect(
                partial(self.dispatchDriverDropdown, driver))
            if self.drivers[driver]['uiSetup'] is not None:
                ui = self.drivers[driver]['uiSetup']
                ui.clicked.connect(partial(self.callPopup, driver))

            if hasattr(self.drivers[driver]['class'], 'signals'):
                signals = self.drivers[driver]['class'].signals
                signals.serverDisconnected.connect(
                    partial(self.serverDisconnected, driver))
                signals.deviceConnected.connect(
                    partial(self.deviceConnected, driver))
                signals.deviceDisconnected.connect(
                    partial(self.deviceDisconnected, driver))

        self.ui.ascomConnect.clicked.connect(self.manualStartAllAscomDrivers)
        self.ui.ascomDisconnect.clicked.connect(self.manualStopAllAscomDrivers)

    def setDefaultData(self, driver, config):
        """
        """
        config[driver] = {}
        defaultConfig = self.drivers[driver]['class'].defaultConfig
        config[driver].update(defaultConfig)

    def loadDriversDataFromConfig(self, config):
        """
        """
        config = config.get('driversData', {})
        self.driversData.clear()

        # adding default for missing drivers
        for driver in self.drivers:
            if driver not in config:
                self.setDefaultData(driver, config)

        # remove unknown drivers from data
        for driver in list(config):
            if driver not in self.drivers:
                del config[driver]

        self.driversData.update(config)

    def initConfig(self):
        """
        """
        config = self.app.config
        self.loadDriversDataFromConfig(config)
        self.ui.autoConnectASCOM.setChecked(config.get('autoConnectASCOM', False))
        self.setupDeviceGui()
        self.startDrivers()

    def storeConfig(self):
        """
        """
        config = self.app.config['mainW']
        configD = self.app.config
        configD['driversData'] = self.driversData
        config['autoConnectASCOM'] = self.ui.autoConnectASCOM.isChecked()

    def setupIcons(self):
        """
        """
        for driver in self.drivers:
            if self.drivers[driver]['uiSetup'] is not None:
                ui = self.drivers[driver]['uiSetup']
                self.wIcon(ui, 'cogs')

        self.wIcon(self.ui.ascomConnect, 'link')
        self.wIcon(self.ui.ascomDisconnect, 'unlink')

    def setupDeviceGui(self):
        """
        setupDeviceGui handles the dropdown lists for all devices possible. it reads the
        information out of the config dict and populated the entries where necessary

        :return: success for test
        """
        dropDowns = [self.drivers[driver]['uiDropDown'] for driver in self.drivers]
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(PySide6.QtWidgets.QListView())
            dropDown.addItem('device disabled')

        for driver in self.driversData:
            frameworks = self.driversData[driver].get('frameworks')

            if driver not in self.drivers:
                self.log.critical(f'Missing driver: [{driver}]')
                continue

            for fw in frameworks:
                name = frameworks[fw]['deviceName']
                itemText = f'{fw} - {name}'
                self.drivers[driver]['uiDropDown'].addItem(itemText)

            framework = self.driversData[driver]['framework']
            index = self.findIndexValue(self.drivers[driver]['uiDropDown'], framework)
            self.drivers[driver]['uiDropDown'].setCurrentIndex(index)
        return True

    def processPopupResults(self):
        """
        processPopupResults takes sets the actual drop down in the device settings
        lists to the choice of the popup window. after that it starts the driver
        again.

        :return: success if new device could be selected
        """
        self.devicePopup.ui.ok.clicked.disconnect(self.processPopupResults)
        driver = self.devicePopup.returnValues.get('driver')

        if not driver:
            return False
        if self.devicePopup.returnValues.get('indiCopyConfig', False):
            self.copyConfig(driverOrig=driver, framework='indi')
        if self.devicePopup.returnValues.get('alpacaCopyConfig', False):
            self.copyConfig(driverOrig=driver, framework='alpaca')

        selectedFramework = self.driversData[driver]['framework']
        index = self.findIndexValue(self.drivers[driver]['uiDropDown'], selectedFramework)
        name = self.driversData[driver]['frameworks'][selectedFramework]['deviceName']

        if not name:
            return False

        itemText = f'{selectedFramework} - {name}'
        self.drivers[driver]['uiDropDown'].setCurrentIndex(index)
        self.drivers[driver]['uiDropDown'].setItemText(index, itemText)

        self.stopDriver(driver=driver)
        self.startDriver(driver=driver)
        return True

    def copyConfig(self, driverOrig='', framework=''):
        """
        copyConfig transfers all information of the actual driver to all other
        drivers of the same framework. if done so, all other drivers running on
        the same framework have to be stopped, copied parameters, initialized and
        started, too.

        :param driverOrig:
        :param framework:
        :return: True for test purpose
        """
        for driverDest in self.drivers:
            if driverDest == driverOrig:
                continue

            driverClass = self.drivers[driverDest]['class']

            if driverClass.framework == framework:
                self.stopDriver(driver=driverOrig)
            if driverDest not in self.driversData:
                continue
            if framework not in self.driversData[driverDest]['frameworks']:
                continue
            for param in self.driversData[driverDest]['frameworks'][framework]:
                if param in ['deviceList', 'deviceName']:
                    continue

                source = self.driversData[driverOrig]['frameworks'][framework][param]
                self.driversData[driverDest]['frameworks'][framework][param] = source

    def callPopup(self, driver):
        """
        callPopup prepares the data and calls and processes the returned data for
        the given driver.
        if copy flags for some frameworks are given, the properties of the actual
        driver will be copied to all other drivers with the same framework.

        :param driver:
        :return: True for test purpose
        """
        data = self.driversData[driver]
        deviceType = self.drivers[driver]['deviceType']

        self.devicePopup = DevicePopup(self,
                                       app=self.app,
                                       driver=driver,
                                       deviceType=deviceType,
                                       data=data)

        self.devicePopup.ui.ok.clicked.connect(self.processPopupResults)

    def stopDriver(self, driver=None):
        """
        :param driver:
        :return: returns status if we are finished
        """
        if not driver:
            return False

        self.app.deviceStat[driver] = None
        framework = self.drivers[driver]['class'].framework
        if framework not in self.drivers[driver]['class'].run:
            return False

        driverClass = self.drivers[driver]['class']
        isRunning = driverClass.run[framework].deviceName != ''

        if isRunning:
            driverClass.stopCommunication()
            driverClass.data.clear()
            driverClass.run[framework].deviceName = ''
            self.msg.emit(0, 'Driver',
                          f'{framework.upper()} disabled',
                          f'{driver}')

        self.changeStyleDynamic(self.drivers[driver]['uiDropDown'],
                                'active', False)
        self.app.deviceStat[driver] = None
        return True

    def stopDrivers(self):
        """
        :return: True for test purpose
        """
        for driver in self.drivers:
            self.stopDriver(driver=driver)
        return True

    def configDriver(self, driver=None):
        """
        :param driver:
        :return: success of config
        """
        if not driver:
            return False

        self.app.deviceStat[driver] = False
        framework = self.driversData[driver]['framework']
        if framework not in self.drivers[driver]['class'].run:
            return False

        frameworkConfig = self.driversData[driver]['frameworks'][framework]
        driverClass = self.drivers[driver]['class'].run[framework]
        for attribute in frameworkConfig:
            setattr(driverClass, attribute, frameworkConfig[attribute])
        return True

    def startDriver(self, driver=None, autoStart=True):
        """
        startDriver checks if a framework has been set and starts the driver with
        its startCommunication method. Normally the driver would report it's
        connection.

        as the configuration is stored in the config, start also stores the
        selected framework in the framework attribute of the driver's class. this
        is needed as when stopping the driver the config dict already has the new
        framework set, and we have to remember it.

        :param driver:
        :param autoStart:
        :return: success if a driver has been started
        """
        if not driver:
            return False

        data = self.driversData[driver]
        framework = data['framework']
        if framework not in self.drivers[driver]['class'].run:
            return False

        driverClass = self.drivers[driver]['class']

        loadConfig = data['frameworks'][framework].get('loadConfig', False)
        updateRate = data['frameworks'][framework].get('updateRate', 1000)
        driverClass.updateRate = updateRate
        driverClass.loadConfig = loadConfig
        driverClass.framework = framework

        self.configDriver(driver=driver)
        if autoStart:
            driverClass.startCommunication()

        self.msg.emit(0, 'Driver',
                      f'{framework.upper()} enabled',
                      f'{driver}')
        return True

    def startDrivers(self):
        """
        startDrivers starts all drivers
        and managing the boot / shutdown.

        :return: true for test purpose
        """
        isAscomAutoConnect = self.ui.autoConnectASCOM.isChecked()
        for driver in self.drivers:
            if driver not in self.driversData:
                continue

            invalid = self.driversData[driver]['framework'] == ''
            if invalid:
                continue

            isAscom = self.driversData[driver]['framework'] in ['ascom', 'alpaca']
            if isAscom and not isAscomAutoConnect:
                autoStart = False
            else:
                autoStart = True

            self.startDriver(driver=driver, autoStart=autoStart)
        return True

    def manualStopAllAscomDrivers(self):
        """
        :return: True for test purpose
        """
        for driver in self.drivers:
            if driver not in self.driversData:
                continue

            isAscom = self.driversData[driver]['framework'] in ['ascom', 'alpaca']
            if isAscom:
                self.stopDriver(driver=driver)
        return True

    def manualStartAllAscomDrivers(self):
        """
        :return: True for test purpose
        """
        for driver in self.drivers:
            if driver not in self.driversData:
                continue

            isAscom = self.driversData[driver]['framework'] in ['ascom', 'alpaca']
            if isAscom:
                self.startDriver(driver=driver, autoStart=True)
        return True

    def dispatchDriverDropdown(self, driver, position):
        """
        dispatchDriverDropdown maps the gui event received from signals to the
        methods doing the real stuff. this splits function and gui reaction into
        two separate tasks. if a dropDown action is taken, this means and new
        driver has been selected, so the old one has to be stopped, the new
        configured and started.
        """
        dropDownEntry = self.drivers[driver]['uiDropDown'].currentText()
        isDisabled = position == 0

        if isDisabled:
            framework = ''
        else:
            framework = dropDownEntry.split('-')[0].rstrip()

        self.driversData[driver]['framework'] = framework
        self.stopDriver(driver=driver)
        if framework:
            self.startDriver(driver=driver)

    def serverDisconnected(self, driver, deviceList):
        """
        """
        if not deviceList:
            return False

        self.msg.emit(0, 'Driver', 'Server disconnected', f'{driver}')
        return True

    def deviceConnected(self, driver, deviceName):
        """
        """
        if not deviceName:
            return False

        self.changeStyleDynamic(self.drivers[driver]['uiDropDown'], 'active', True)
        self.app.deviceStat[driver] = True
        self.msg.emit(0, 'Driver', 'Device connected', f'{driver}')

        data = self.driversData[driver]
        framework = data['framework']
        if data['frameworks'][framework].get('loadConfig', False):
            self.msg.emit(0, 'Driver', 'Config loaded', f'{driver}')
        return True

    def deviceDisconnected(self, driver, deviceName):
        """
        """
        self.changeStyleDynamic(self.drivers[driver]['uiDropDown'], 'active', False)
        self.app.deviceStat[driver] = False
        self.msg.emit(0, 'Driver', 'Device disconnected', f'{driver}')
