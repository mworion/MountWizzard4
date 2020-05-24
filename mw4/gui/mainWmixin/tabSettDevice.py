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

    devices types in self.drivers are name related to ascom definitions
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

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
                'uiSetup': self.ui.astrometrySetup,
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
            d = self.driversData[driver] = configData.get(driver, {})

            if driver != 'astrometry':
                continue

            nameASTROMETRY = self.app.astrometry.run['astrometry'].name
            d['astrometryDeviceList'] = [nameASTROMETRY]
            if not d['astrometryAppPath']:
                d['astrometryAppPath'] = self.app.astrometry.run['astrometry'].appPath
            if not d['astrometryIndexPath']:
                d['astrometryIndexPath'] = self.app.astrometry.run['astrometry'].indexPath

            nameASTAP = self.app.astrometry.run['astap'].name
            d['astapDeviceList'] = [nameASTAP]
            if not d['astapAppPath']:
                d['astapAppPath'] = self.app.astrometry.run['astap'].appPath
            if not d['astapIndexPath']:
                d['astapIndexPath'] = self.app.astrometry.run['astap'].indexPath

        self.setupDeviceGui()

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].setCurrentIndex(config.get(driver, 0))

        self.dispatch(driverName='all')

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
            if driver not in self.driversData:
                continue
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
                if driver not in self.driversData:
                    self.driversData[driver] = {}
                if framework == 'indi':
                    name = ' - ' + self.driversData[driver].get('indiName', '')
                elif framework == 'alpaca':
                    name = ' - ' + self.driversData[driver].get('alpacaName', '')
                elif framework == 'ascom':
                    name = ' - ' + self.driversData[driver].get('ascomName', '')
                elif framework == 'astrometry':
                    name = ' - ' + self.driversData[driver].get('astrometryName', '')
                elif framework == 'astap':
                    name = ' - ' + self.driversData[driver].get('astapName', '')
                else:
                    name = ''
                itemText = f'{framework}{name}'
                self.drivers[driver]['uiDropDown'].addItem(itemText)

        return True

    def processPopupResults(self, driverSelected=None, returnValues=None):
        """

        :return: True for test purpose
        """

        # check if copy are made. if so, than restart all drivers related
        if returnValues.get('copyIndi', False):
            for driver in self.drivers:
                if not self.drivers[driver]['class'].framework == 'indi':
                    continue
                self.dispatch(driverName=driver)

        elif returnValues.get('copyAlpaca', False):
            for driver in self.drivers:
                if not self.drivers[driver]['class'].framework == 'alpaca':
                    continue
                self.dispatch(driverName=driver)

        # if we choose a framework and it's available, we select it from drop down
        selectedFramework = self.driversData[driverSelected].get('framework', '')
        index = self.findIndexValue(self.drivers[driverSelected]['uiDropDown'], selectedFramework)
        self.drivers[driverSelected]['uiDropDown'].setCurrentIndex(index)

        self.dispatch(driverName=driverSelected)

        return True

    def setupPopUp(self):
        """
        setupPopUp calculates the geometry data to place the popup centered on top of the
        parent window and call it with all necessary data. The popup is modal and we connect
        the signal of the destroyed window to update the dispatching value for all changes
        drivers

        :return: True for test purpose
        """

        for driver in self.drivers:
            if self.sender() != self.drivers[driver]['uiSetup']:
                continue

            # calculate geometry of parent window to center the popup
            geometry = self.pos().x(), self.pos().y(), self.width(), self.height()

            # collect all available frameworks
            availFramework = list(self.drivers[driver]['class'].run.keys())

            # selecting the device type
            deviceType = self.drivers[driver]['deviceType']

            self.popupUi = DevicePopup(geometry=geometry,
                                       driver=driver,
                                       deviceType=deviceType,
                                       availFramework=availFramework,
                                       data=self.driversData)

            # memorizing the driver we have to update
            self.popupUi.exec_()
            if self.popupUi.returnValues.get('close', 'cancel') == 'cancel':
                return False
            else:
                break

        self.processPopupResults(driverSelected=driver,
                                 returnValues=self.popupUi.returnValues)

        return True

    def dispatchStopDriver(self, driver=None):
        """
        dispatchStopDriver stops the named driver.

        :return: returns status if we are finished
        """

        # if there is a change we first have to stop running drivers and reset gui
        # if it's the startup (which has no name set, we don't need to stop)
        if self.drivers[driver]['class'].name:
            self.drivers[driver]['class'].stopCommunication()
            self.drivers[driver]['class'].data.clear()
            self.app.message.emit(f'Disabled device:     [{driver}]', 0)

        # stopped driver get gets neutral color
        self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_NORM)

        # disabling the driver for the overall app
        self.deviceStat[driver] = None

        # if new driver is disabled, we are finished
        if self.drivers[driver]['uiDropDown'].currentText() == 'device disabled':
            self.drivers[driver]['class'].name = ''
            return False

        return True

    def stopAllDrivers(self):
        """

        :return: True for test purpose
        """
        for driver in self.drivers:
            self.dispatchStopDriver(driver=driver)

        return True

    def dispatchConfigDriver(self, driver=None):
        """
        dispatchConfigDriver

        :param driver:
        :return: True for test purpose
        """

        if not driver:
            return False

        driverData = self.driversData.get(driver, {})
        driverClass = self.drivers[driver]['class']

        # without connection it is false, which leads to a red in gui
        self.deviceStat[driver] = False

        # now driver specific parameters will be set
        if self.drivers[driver]['uiDropDown'].currentText().startswith('indi'):
            framework = 'indi'
            driverClass.framework = framework
            driverData['framework'] = framework
            name = driverData.get('indiName', '')
            driverClass.name = name

            address = driverData.get('indiHost', 'localhost')
            port = int(driverData.get('indiPort', 7624))
            host = (address, port)
            showMessages = driverData.get('indiMessages', False)
            driverClass.run[framework].showMessages = showMessages
            driverClass.host = host
            index = self.drivers[driver]['uiDropDown'].currentIndex()
            self.drivers[driver]['uiDropDown'].setItemText(index, f'indi - {name}')

        elif self.drivers[driver]['uiDropDown'].currentText().startswith('alpaca'):
            framework = 'alpaca'
            driverClass.framework = framework
            driverData['framework'] = framework
            name = driverData.get('alpacaName', '')
            driverClass.name = name

            address = driverData.get('alpacaHost', 'localhost')
            port = int(driverData.get('alpacaPort', 11111))
            host = (address, port)
            driverClass.host = host
            index = self.drivers[driver]['uiDropDown'].currentIndex()
            self.drivers[driver]['uiDropDown'].setItemText(index, f'alpaca - {name}')

        elif self.drivers[driver]['uiDropDown'].currentText().startswith('ascom'):
            framework = 'ascom'
            driverClass.framework = framework
            driverData['framework'] = framework
            name = driverData.get('ascomName', '')
            driverClass.name = name
            index = self.drivers[driver]['uiDropDown'].currentIndex()
            self.drivers[driver]['uiDropDown'].setItemText(index, f'ascom - {name}')

        elif self.drivers[driver]['uiDropDown'].currentText().startswith('astrometry'):
            framework = 'astrometry'
            driverClass.framework = framework
            driverData['framework'] = framework
            name = driverData.get('astrometryName', '')
            driverClass.name = name

            driverClass.timeout = driverData.get('astrometryTimeout', 30)
            driverClass.searchRadius = driverData.get('astrometrySearchRadius', 20)
            indexPath = driverData.get('astrometryIndexPath', '')
            driverClass.indexPath = indexPath
            appPath = driverData.get('astrometryAppPath', '')
            driverClass.appPath = appPath
            index = self.drivers[driver]['uiDropDown'].currentIndex()
            self.drivers[driver]['uiDropDown'].setItemText(index, f'astrometry - {name}')

        elif self.drivers[driver]['uiDropDown'].currentText().startswith('astap'):
            framework = 'astap'
            driverClass.framework = framework
            driverData['framework'] = framework
            name = driverData.get('astapName', '')
            driverClass.name = name

            driverClass.timeout = driverData.get('astapTimeout', 30)
            driverClass.searchRadius = driverData.get('astapSearchRadius', 20)
            indexPath = driverData.get('astapIndexPath', '')
            driverClass.indexPath = indexPath
            appPath = driverData.get('astapAppPath', '')
            driverClass.appPath = appPath
            index = self.drivers[driver]['uiDropDown'].currentIndex()
            self.drivers[driver]['uiDropDown'].setItemText(index, f'astap - {name}')

        elif self.drivers[driver]['uiDropDown'].currentText().startswith('internal'):
            text = self.drivers[driver]['uiDropDown'].currentText()
            driverClass.framework = text
            driverClass.name = text

        return True

    def dispatchStartDriver(self, driver=None):
        """
        dispatchStartDriver

        :param driver:
        :return success of start
        """

        if not driver:
            return False

        # for built-in i actually not check their presence as the should function
        if self.drivers[driver]['uiDropDown'].currentText().startswith('internal'):
            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_GREEN)
            self.deviceStat[driver] = True

        # and finally start it
        self.app.message.emit(f'Enabled device:      [{driver}]', 0)

        driverData = self.driversData.get(driver, {})
        loadConfig = driverData.get('indiLoadConfig', False)
        suc = self.drivers[driver]['class'].startCommunication(loadConfig=loadConfig)

        return suc

    def dispatch(self, driverName=None):
        """
        dispatch is the central method to start / stop the drivers, setting the parameters
        and managing the boot / shutdown.

        dispatch is called by signals if the user uses the dropdown to change a driver setting
        or could be called directly with a driverName to manually change the setting. this
        happens at the startup to initialize the drivers and after a popup is closed to update
        the settings for a driver.

        if driver=='all' is set, dispatch will handler all drivers in a row.

        first dispatch will stop running drivers
        then changing the settings
        then starting the new ones

        :param driverName:
        :return: true for test purpose
        """

        isGui = not isinstance(driverName, str)
        isAll = not isGui and driverName == 'all'

        for driver in self.drivers:
            if not isGui and (driverName != driver) and not isAll:
                continue

            if isGui and (self.sender() != self.drivers[driver]['uiDropDown']):
                continue

            if not self.dispatchStopDriver(driver=driver):
                continue

            self.dispatchConfigDriver(driver=driver)
            self.dispatchStartDriver(driver=driver)

        return True

    def scanValid(self, driver=None, deviceName=''):
        """
        scanValid checks if the calling device fits to the summary of all devices and gives
        back if it should be skipped

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
        if not deviceName:
            return False

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
