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
import collections

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

    frameworks = {
        'alpaca': {
            'device': '',
            'deviceList': [],
            'host': 'localhost',
            'port': 11111,
            'protocol': '',
            'protocolList': ['https', 'http'],
            'user': '',
            'password': '',
            'copyConfig': False,
        },
        'ascom': {
            'device': 'test',
        },
        'indi': {
            'device': '',
            'deviceList': [],
            'host': 'localhost',
            'port': 7624,
            'loadConfig': False,
            'messages': False,
            'copyConfig': False,
        },
        'astrometry': {
            'searchRadius': 10,
            'timeout': 30,
            'appPath': '',
            'indexPath': '',
        },
        'astap': {
            'searchRadius': 10,
            'timeout': 30,
            'appPath': '',
            'indexPath': '',
        },
    }

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
                'deviceType': 'skymeter',
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
                'deviceType': 'power',
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

        self.ui.ascomConnect.clicked.connect(self.manualStartAllAscomDrivers)
        self.ui.ascomDisconnect.clicked.connect(self.manualStopAllAscomDrivers)

        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].activated.connect(self.dispatch)
            if self.drivers[driver]['uiSetup'] is not None:
                ui = self.drivers[driver]['uiSetup']
                ui.clicked.connect(self.setupPopup)

            if not hasattr(self.drivers[driver]['class'], 'signals'):
                continue

            signals = self.drivers[driver]['class'].signals
            signals.serverDisconnected.connect(self.serverDisconnected)
            signals.deviceConnected.connect(self.deviceConnected)
            signals.deviceDisconnected.connect(self.deviceDisconnected)

    def dictMerge(self, dct, merge_dct):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dictMerge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], dict)
                    and isinstance(merge_dct[k], collections.Mapping)):
                self.dictMerge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    def cleanData(self, data, driver):
        """

        :param data:
        :param driver:
        :return: cleaned data
        """

        if not data or 'frameworks' not in data:
            data = {
                'framework': '',
                'deviceType': driver,
                'defaultDevice': '',
                'frameworks': {},
            }

        return data

        if 'frameworks' not in data:
            data['frameworks'] = {}

        for fw in self.drivers[driver]['class'].run:
            self.dictMerge(data['frameworks'][fw], self.frameworks.get(fw, {}))

        return data

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config.get('mainW', {})
        driversData = self.app.config.get('driversData', {})

        for driver in self.drivers:
            data = driversData.get(driver, {})
            self.driversData[driver] = self.cleanData(data, driver)

        self.setupDeviceGui()
        for driver in self.drivers:
            self.drivers[driver]['uiDropDown'].setCurrentIndex(config.get(driver, 0))
        self.ui.checkASCOMAutoConnect.setChecked(config.get('checkASCOMAutoConnect', False))
        self.dispatch(driver='all')

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
        driversData = self.app.config['driversData']

        for driver in self.drivers:
            config[driver] = self.drivers[driver]['uiDropDown'].currentIndex()

        for driver in self.drivers:
            if driver not in self.driversData:
                continue
            driversData[driver] = self.driversData[driver]

        config['checkASCOMAutoConnect'] = self.ui.checkASCOMAutoConnect.isChecked()

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

    def processPopupResults(self, driver=None):
        """
        processPopupResults takes sets the actual drop down in the device settings lists to
        the choice of the popup window. after that it reinitialises the selected driver with
        the new data.

        :return: True for test purpose
        """

        selectedFramework = self.driversData[driver]['framework']

        index = self.findIndexValue(self.drivers[driver]['uiDropDown'], selectedFramework)
        self.drivers[driver]['uiDropDown'].setCurrentIndex(index)

        self.dispatch(driver=driver)

        return True

    def callPopup(self, driver, geometry):
        """
        callPopup prepares the data and calls and processes the returned data.

        there is one definition when using selection lists for offering QComboBoxes:
        the list name for a property to be set through this lists is the property name
        with an postfix 'List' like 'protocol' and 'protocolList'

        :param driver:
        :param geometry:
        :return: True if OK and false if cancel
        """

        data = self.driversData[driver]
        self.popupUi = DevicePopup(app=self.app,
                                   geometry=geometry,
                                   driver=driver,
                                   data=data)
        self.popupUi.exec_()
        print(self.driversData)
        if self.popupUi.returnValues.get('close', 'cancel') == 'cancel':
            return False
        else:
            return True

    def setupPopup(self):
        """
        setupPopup calculates the geometry data to place the popup centered on top of the
        parent window and call it with all necessary data. The popup is modal and we connect
        the signal of the destroyed window to update the dispatching value for all changes
        drivers

        :return: True for test purpose
        """

        geometry = self.pos().x(), self.pos().y(), self.width(), self.height()
        suc = False

        for driver in self.drivers:
            if self.sender() != self.drivers[driver]['uiSetup']:
                continue
            suc = self.callPopup(driver, geometry)
            break

        if suc:
            self.processPopupResults(driver=driver)

        return True

    def dispatchStopDriver(self, driver=None, autoASCOM=True, onlyASCOM=False):
        """
        dispatchStopDriver stops the named driver.

        :param driver:
        :param autoASCOM: flag if ascom driver should be started, too
        :param onlyASCOM: flag if only ascom driver should be affected
        :return: returns status if we are finished
        """

        if not driver:
            return False

        if not self.drivers[driver]['uiDropDown'].currentText().startswith('ascom'):
            if onlyASCOM:
                return False

        if self.drivers[driver]['uiDropDown'].currentText().startswith('ascom'):
            if not (autoASCOM or onlyASCOM):
                return True

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

    def manualStopAllAscomDrivers(self):
        """

        :return: True for test purpose
        """
        for driver in self.drivers:
            self.dispatchStopDriver(driver=driver, onlyASCOM=True)

        return True

    def dispatchConfigDriver(self, driver=None, onlyASCOM=False):
        """
        dispatchConfigDriver

        :param driver:
        :param onlyASCOM: flag if only ascom driver should be affected
        :return: True for test purpose
        """

        if not driver:
            return False

        if not self.drivers[driver]['uiDropDown'].currentText().startswith('ascom'):
            if onlyASCOM:
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

    def manualStartAllAscomDrivers(self):
        """

        :return: True for test purpose
        """
        for driver in self.drivers:
            self.dispatchConfigDriver(driver=driver, onlyASCOM=True)
            self.dispatchStartDriver(driver=driver, onlyASCOM=True)

        return True

    def dispatchStartDriver(self, driver=None, autoASCOM=True, onlyASCOM=False):
        """
        dispatchStartDriver

        :param driver:
        :param autoASCOM: flag if ascom driver should be started, too
        :param onlyASCOM: flag if only ascom driver should be affected
        :return success of start
        """

        if not driver:
            return False

        if not self.drivers[driver]['uiDropDown'].currentText().startswith('ascom'):
            if onlyASCOM:
                return False

        if self.drivers[driver]['uiDropDown'].currentText().startswith('ascom'):
            if not (autoASCOM or onlyASCOM):
                return False

        if self.drivers[driver]['uiDropDown'].currentText().startswith('internal'):
            self.drivers[driver]['uiDropDown'].setStyleSheet(self.BACK_GREEN)
            self.deviceStat[driver] = True

        # and finally start it
        self.app.message.emit(f'Enabled device:      [{driver}]', 0)

        driverData = self.driversData.get(driver, {})
        loadConfig = driverData.get('indiLoadConfig', False)
        suc = self.drivers[driver]['class'].startCommunication(loadConfig=loadConfig)

        return suc

    def dispatch(self, driver=None):
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

        :param driver:
        :return: true for test purpose
        """

        isGui = not isinstance(driver, str)
        isAll = not isGui and driver == 'all'
        autoASCOM = self.ui.checkASCOMAutoConnect.isChecked()

        for d in self.drivers:
            if not isGui and (driver != d) and not isAll:
                continue

            if isGui and (self.sender() != self.drivers[d]['uiDropDown']):
                continue

            if not self.dispatchStopDriver(driver=d, autoASCOM=autoASCOM):
                continue

            self.dispatchConfigDriver(driver=d)
            self.dispatchStartDriver(driver=d, autoASCOM=autoASCOM)

        return True

    def scanValid(self, driver=None, device=''):
        """
        scanValid checks if the calling device fits to the summary of all devices and gives
        back if it should be skipped

        :param device:
        :param driver:
        :return:
        """

        if not driver:
            return False
        if not device:
            return False

        if hasattr(self.drivers[driver]['class'], 'signals'):
            if self.sender() != self.drivers[driver]['class'].signals:
                return False
        else:
            if self.drivers[driver]['class'].name != device:
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
