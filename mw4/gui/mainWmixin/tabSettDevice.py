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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
from deepdiff import DeepDiff

# local import
from gui.extWindows.devicePopupW import DevicePopup


class SettDevice:
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

    def __init__(self):
        self.popupUi = None
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
            'sensorWeather': {
                'uiDropDown': self.ui.sensorWeatherDevice,
                'uiSetup': self.ui.sensorWeatherSetup,
                'class': self.app.sensorWeather,
                'deviceType': 'observingconditions',
            },
            'directWeather': {
                'uiDropDown': self.ui.directWeatherDevice,
                'uiSetup': None,
                'class': self.app.directWeather,
                'deviceType': None,
            },
            'onlineWeather': {
                'uiDropDown': self.ui.onlineWeatherDevice,
                'uiSetup': self.ui.onlineWeatherSetup,
                'class': self.app.onlineWeather,
                'deviceType': 'observingconditions',
            },
            'seeingWeather': {
                'uiDropDown': self.ui.seeingWeatherDevice,
                'uiSetup': self.ui.seeingWeatherSetup,
                'class': self.app.seeingWeather,
                'deviceType': 'observingconditions',
            },
            'skymeter': {
                'uiDropDown': self.ui.skymeterDevice,
                'uiSetup': self.ui.skymeterSetup,
                'class': self.app.skymeter,
                'deviceType': 'observingconditions',
            },
            'powerWeather': {
                'uiDropDown': self.ui.powerWeatherDevice,
                'uiSetup': self.ui.powerWeatherSetup,
                'class': self.app.powerWeather,
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
            self.drivers[driver]['uiDropDown'].activated.connect(self.dispatchDriverDropdown)
            if self.drivers[driver]['uiSetup'] is not None:
                ui = self.drivers[driver]['uiSetup']
                ui.clicked.connect(self.dispatchPopup)

            if hasattr(self.drivers[driver]['class'], 'signals'):
                signals = self.drivers[driver]['class'].signals
                signals.serverDisconnected.connect(self.serverDisconnected)
                signals.deviceConnected.connect(self.deviceConnected)
                signals.deviceDisconnected.connect(self.deviceDisconnected)

        self.ui.ascomConnect.clicked.connect(self.manualStartAllAscomDrivers)
        self.ui.ascomDisconnect.clicked.connect(self.manualStopAllAscomDrivers)

    def checkStructureDriversData(self, driver, config):
        """
        checkStructureDriversData
        :param driver:
        :param config:
        :return:
        """
        defaultConfig = self.drivers[driver]['class'].defaultConfig
        res = DeepDiff(defaultConfig, config['driversData'][driver])

        if 'dictionary_item_added' in res or 'dictionary_item_removed' in res:
            config['driversData'][driver] = defaultConfig
            self.log.info(f'Config for {[driver]} updated to default')
            return False

        return True

    def setDefaultData(self, driver, config):
        """
        :param driver:
        :param config:
        :return:
        """
        config['driversData'][driver] = {}
        defaultConfig = self.drivers[driver]['class'].defaultConfig
        config['driversData'][driver].update(defaultConfig)
        return True

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        configD = self.app.config
        if 'driversData' not in configD:
            configD['driversData'] = {}

        # adding default for missing drivers
        for driver in self.drivers:
            if driver not in configD['driversData']:
                self.setDefaultData(driver, configD)

        # remove unknown drivers from data
        for driver in list(configD['driversData'].keys()):
            if driver not in self.drivers:
                del configD['driversData'][driver]

        self.driversData.clear()
        self.driversData.update(configD.get('driversData', {}))
        self.ui.autoConnectASCOM.setChecked(config.get('autoConnectASCOM', False))
        self.setupDeviceGui()
        self.startDrivers()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        configD = self.app.config
        configD['driversData'] = self.driversData
        config['autoConnectASCOM'] = self.ui.autoConnectASCOM.isChecked()
        return True

    def setupDeviceGui(self):
        """
        setupDeviceGui handles the dropdown lists for all devices possible. it reads the
        information out of the config dict and populated the entries where necessary

        :return: success for test
        """
        dropDowns = list(self.drivers[driver]['uiDropDown'] for driver in self.drivers)
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('device disabled')

        for driver in self.driversData:
            frameworks = self.driversData[driver]['frameworks']

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
        self.popupUi.ui.ok.clicked.disconnect(self.processPopupResults)
        driver = self.popupUi.returnValues.get('driver')

        if not driver:
            return False
        if self.popupUi.returnValues.get('indiCopyConfig', False):
            self.copyConfig(driver=driver, framework='indi')
        if self.popupUi.returnValues.get('alpacaCopyConfig', False):
            self.copyConfig(driver=driver, framework='alpaca')

        selectedFramework = self.driversData[driver]['framework']
        index = self.findIndexValue(self.drivers[driver]['uiDropDown'], selectedFramework)
        name = self.driversData[driver]['frameworks'][selectedFramework]['deviceName']

        if not name:
            return False

        itemText = f'{selectedFramework} - {name}'
        self.drivers[driver]['uiDropDown'].setCurrentIndex(index)
        self.drivers[driver]['uiDropDown'].setItemText(index, itemText)
        self.drivers[driver]['uiDropDown'].update()

        self.stopDriver(driver=driver)
        self.startDriver(driver=driver)
        return True

    def copyConfig(self, driver='', framework=''):
        """
        copyConfig transfers all information of the actual driver to all other
        drivers of the same framework. if done so, all other drivers running on
        the same framework have to be stopped, copied parameters, initialized and
        started, too.

        :param driver:
        :param framework:
        :return: True for test purpose
        """
        for driverLoop in self.drivers:
            if driverLoop == driver:
                # not copy on the same driver
                continue

            driverClass = self.drivers[driverLoop]['class']

            if driverClass.framework == framework:
                self.stopDriver(driver=driver)
            if driverLoop not in self.driversData:
                continue
            if framework not in self.driversData[driverLoop]['frameworks']:
                continue
            for param in self.driversData[driverLoop]['frameworks'][framework]:
                # no local information should be copied
                if param in ['deviceList', 'deviceName']:
                    continue

                source = self.driversData[driver]['frameworks'][framework][param]
                self.driversData[driverLoop]['frameworks'][framework][param] = source
        return True

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

        self.popupUi = DevicePopup(self,
                                   app=self.app,
                                   driver=driver,
                                   deviceType=deviceType,
                                   data=data)

        self.popupUi.ui.ok.clicked.connect(self.processPopupResults)
        return True

    def dispatchPopup(self):
        """
        :return: True for test purpose
        """
        sender = self.sender()
        driver = self.returnDriver(sender, self.drivers, addKey='uiSetup')

        if driver:
            self.callPopup(driver=driver)
        return True

    def stopDriver(self, driver=None):
        """
        :param driver:
        :return: returns status if we are finished
        """
        if not driver:
            return False

        self.deviceStat[driver] = None
        framework = self.drivers[driver]['class'].framework
        if not framework:
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
        self.deviceStat[driver] = None

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

        self.deviceStat[driver] = False
        framework = self.driversData[driver]['framework']
        if not framework:
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
        connection, but for internal driver this has to be done separately.

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
        if not framework:
            return False

        driverClass = self.drivers[driver]['class']

        loadConfig = data['frameworks'][framework].get('loadConfig', False)
        updateRate = data['frameworks'][framework].get('updateRate', 1000)
        driverClass.updateRate = updateRate
        driverClass.loadConfig = loadConfig

        driverClass.framework = framework
        isInternal = framework == 'internal'
        if isInternal:
            self.changeStyleDynamic(self.drivers[driver]['uiDropDown'],
                                    'active', True)

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

    def dispatchDriverDropdown(self):
        """
        dispatchDriverDropdown maps the gui event received from signals to the
        methods doing the real stuff. this splits function and gui reaction into
        two separate tasks. if a dropDown action is taken, this means and new
        driver has been selected, so the old one has to be stopped, the new
        configured and started.

        :return: true for test purpose
        """
        sender = self.sender()
        isDisabled = sender.currentText() == 'device disabled'
        driver = self.returnDriver(sender, self.drivers, addKey='uiDropDown')

        if driver:
            if isDisabled:
                framework = ''
            else:
                framework = sender.currentText().split('-')[0].rstrip()

            self.driversData[driver]['framework'] = framework
            self.stopDriver(driver=driver)
            if framework:
                self.startDriver(driver=driver)
        return True

    def scanValid(self, driver=None, deviceName=''):
        """
        scanValid checks if the calling device fits to the summary of all
        devices and gives back if it should be skipped

        :param deviceName:
        :param driver:
        :return:
        """
        if not driver:
            return False
        if not deviceName:
            return False

        if hasattr(self.drivers[driver]['class'], 'signals'):
            if self.sender() != self.drivers[driver]['class'].signals:
                return False
        else:
            driverClass = self.drivers[driver]['class']
            if not driverClass.framework:
                return False
            if driverClass.run[driverClass.framework].deviceName != deviceName:
                return False

        return True

    def serverDisconnected(self, deviceList):
        """
        :param deviceList:
        :return: true for test purpose
        """
        if not deviceList:
            return False

        deviceName = list(deviceList.keys())[0]

        for driver in self.drivers:
            if not self.scanValid(driver=driver, deviceName=deviceName):
                continue

            self.msg.emit(0, 'Driver', 'Server disconnected', f'{driver}')
        return True

    def deviceConnected(self, deviceName):
        """
        :param deviceName:
        :return: true for test purpose
        """
        if not deviceName:
            return False

        for driver in self.drivers:
            if not self.scanValid(driver=driver, deviceName=deviceName):
                continue

            self.changeStyleDynamic(self.drivers[driver]['uiDropDown'],
                                    'active', True)
            self.deviceStat[driver] = True
            self.msg.emit(0, 'Driver', 'Device connected', f'{driver}')

            data = self.driversData[driver]
            framework = data['framework']
            if data['frameworks'][framework].get('loadConfig', False):
                self.msg.emit(0, 'Driver', 'Config loaded', f'{driver}')
        return True

    def deviceDisconnected(self, deviceName):
        """
        :param deviceName:
        :return: true for test purpose
        """
        for driver in self.drivers:
            if not self.scanValid(driver=driver, deviceName=deviceName):
                continue

            self.changeStyleDynamic(self.drivers[driver]['uiDropDown'],
                                    'active', False)
            self.deviceStat[driver] = False
            self.msg.emit(0, 'Driver', 'Device disconnected', f'{driver}')
        return True
