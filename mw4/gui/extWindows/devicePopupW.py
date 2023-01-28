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
import platform

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListView, QComboBox, QLineEdit
from PyQt5.QtWidgets import QCheckBox, QDoubleSpinBox

if platform.system() == 'Windows':
    import win32com.client

# local import
from base.indiClass import IndiClass
from base.alpacaClass import AlpacaClass
from base.sgproClass import SGProClass
from base.ninaClass import NINAClass
from gui.utilities import toolsQtWidget
from gui.widgets.devicePopup_ui import Ui_DevicePopup


class DevicePopup(toolsQtWidget.MWidget):
    """
    """

    __all__ = ['DevicePopup']

    def __init__(self,
                 parentWidget,
                 app=None,
                 driver=None,
                 deviceType=None,
                 data=None):

        super().__init__()
        self.app = app
        self.data = data
        self.driver = driver
        self.deviceType = deviceType
        self.msg = app.msg

        self.ui = Ui_DevicePopup()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)
        pixmap = self.svg2pixmap(':/icon/cogs.svg', self.M_BLUE)
        self.ui.iconPixmap.setPixmap(pixmap)

        self.returnValues = {'close': 'cancel'}
        self.framework2gui = {
            'indi': {
                'hostaddress': self.ui.indiHostAddress,
                'port': self.ui.indiPort,
                'deviceList': self.ui.indiDeviceList,
                'messages': self.ui.indiMessages,
                'loadConfig': self.ui.indiLoadConfig,
                'updateRate': self.ui.indiUpdateRate,
            },
            'alpaca': {
                'hostaddress': self.ui.alpacaHostAddress,
                'port': self.ui.alpacaPort,
                'user': self.ui.alpacaUser,
                'password': self.ui.alpacaPassword,
                'deviceList': self.ui.alpacaDeviceList,
                'updateRate': self.ui.alpacaUpdateRate,
            },
            'ascom': {
                'deviceName': self.ui.ascomDevice,
            },
            'sgpro': {
                'deviceList': self.ui.sgproDeviceList,
            },
            'nina': {
                'deviceList': self.ui.ninaDeviceList,
            },
            'astrometry': {
                'deviceList': self.ui.astrometryDeviceList,
                'searchRadius': self.ui.astrometrySearchRadius,
                'timeout': self.ui.astrometryTimeout,
                'appPath': self.ui.astrometryAppPath,
                'indexPath': self.ui.astrometryIndexPath,
            },
            'astap': {
                'deviceList': self.ui.astapDeviceList,
                'searchRadius': self.ui.astapSearchRadius,
                'timeout': self.ui.astapTimeout,
                'appPath': self.ui.astapAppPath,
                'indexPath': self.ui.astapIndexPath,
            },
            'watney': {
                'deviceList': self.ui.watneyDeviceList,
                'searchRadius': self.ui.watneySearchRadius,
                'timeout': self.ui.watneyTimeout,
                'appPath': self.ui.watneyAppPath,
                'indexPath': self.ui.watneyIndexPath,
            },
            'onlineWeather': {
                'apiKey': self.ui.onlineWeatherApiKey,
                'hostaddress': self.ui.onlineWeatherHostAddress,
            },
            'seeing': {
                'apiKey': self.ui.seeingWeatherApiKey,
                'hostaddress': self.ui.seeingWeatherHostAddress,
            },
            'relay': {
                'hostaddress': self.ui.relayHostAddress,
                'user': self.ui.relayUser,
                'password': self.ui.relayPassword,
            },
        }

        self.ui.cancel.clicked.connect(self.close)
        self.ui.ok.clicked.connect(self.storeConfig)
        self.ui.indiDiscover.clicked.connect(self.discoverIndiDevices)
        self.ui.alpacaDiscover.clicked.connect(self.discoverAlpacaDevices)
        self.ui.sgproDiscover.clicked.connect(self.discoverSGProDevices)
        self.ui.ninaDiscover.clicked.connect(self.discoverNINADevices)
        self.ui.selectAstrometryIndexPath.clicked.connect(self.selectAstrometryIndexPath)
        self.ui.selectAstrometryAppPath.clicked.connect(self.selectAstrometryAppPath)
        self.ui.selectAstapIndexPath.clicked.connect(self.selectAstapIndexPath)
        self.ui.selectAstapAppPath.clicked.connect(self.selectAstapAppPath)
        self.ui.selectWatneyIndexPath.clicked.connect(self.selectWatneyIndexPath)
        self.ui.selectWatneyAppPath.clicked.connect(self.selectWatneyAppPath)
        self.ui.ascomSelector.clicked.connect(self.selectAscomDriver)
        self.initConfig()
        self.show()

    def selectTabs(self):
        """
        show only the tabs needed for available frameworks and properties to be
        - it selects the tab for the actual framework
        - it hides all tabs, which are not relevant for the available frameworks

        :return: True for test purpose
        """
        firstFramework = next(iter(self.data['frameworks']))
        framework = self.data.get('framework')
        if not framework:
            framework = firstFramework

        tabIndex = self.getTabIndex(self.ui.tab, framework)
        self.ui.tab.setCurrentIndex(tabIndex)

        for index in range(0, self.ui.tab.count()):
            isVisible = self.ui.tab.widget(index).objectName() in self.data['frameworks']
            self.ui.tab.setTabVisible(index, isVisible)
        return True

    def populateTabs(self):
        """
        populateTabs takes all the data coming from driver data dict and puts
        it onto the corresponding gui elements in the tabs. as we need to have
        unique names in the gui, there is a translation table (self.framework2gui)
        for all framework entries to be used.

        :return: True for test purpose
        """
        frameworks = self.data['frameworks']
        for fw in frameworks:
            frameworkElements = frameworks[fw]
            for element in frameworkElements:

                ui = self.framework2gui[fw].get(element)

                if isinstance(ui, QComboBox):
                    ui.clear()
                    ui.setView(QListView())
                    for i, deviceName in enumerate(frameworks[fw][element]):
                        ui.addItem(deviceName)
                        if frameworks[fw]['deviceName'] == deviceName:
                            ui.setCurrentIndex(i)

                elif isinstance(ui, QLineEdit):
                    ui.setText(f'{frameworks[fw][element]}')

                elif isinstance(ui, QCheckBox):
                    ui.setChecked(frameworks[fw][element])

                elif isinstance(ui, QDoubleSpinBox):
                    ui.setValue(frameworks[fw][element])
        return True

    def initConfig(self):
        """
        :return: True for test purpose
        """
        self.setWindowTitle(f'Setup driver for {self.deviceType}')
        self.populateTabs()
        self.selectTabs()
        if self.data.get('framework') in ['astrometry', 'watney', 'astap']:
            self.updatePlateSolverStatus()
        return True

    def readTabs(self):
        """
        readTabs takes all the gui information and puts it onto the data
        dictionary and properties as we need to have unique names in the gui,
        there is a translation table (self.framework2gui) for all framework
        entries to be used.

        :return: True for test purpose
        """
        framework = self.data['framework']
        frameworkData = self.data['frameworks'][framework]

        for element in list(frameworkData):
            ui = self.framework2gui[framework].get(element)
            if isinstance(ui, QComboBox):
                frameworkData['deviceName'] = ui.currentText()
                frameworkData[element].clear()
                for index in range(ui.model().rowCount()):
                    frameworkData[element].append(ui.model().item(index).text())

            elif isinstance(ui, QLineEdit):
                if isinstance(frameworkData[element], str):
                    frameworkData[element] = ui.text()
                elif isinstance(frameworkData[element], int):
                    frameworkData[element] = int(ui.text())
                else:
                    frameworkData[element] = float(ui.text())

            elif isinstance(ui, QCheckBox):
                frameworkData[element] = ui.isChecked()
            elif isinstance(ui, QDoubleSpinBox):
                frameworkData[element] = ui.value()
        return True

    def readFramework(self):
        """
        readFramework determines, which tab was selected when leaving and writes
        the adequate selection into the dict. as the headline might be different
        from the keywords, a translation table (self.framework2gui) in a reverse
        index is used.

        :return: True for test purpose
        """
        index = self.ui.tab.currentIndex()
        framework = self.ui.tab.widget(index).objectName()
        self.data['framework'] = framework
        return True

    def storeConfig(self):
        """
        :return: true for test purpose
        """
        self.readFramework()
        self.readTabs()
        self.returnValues['indiCopyConfig'] = self.ui.indiCopyConfig.isChecked()
        self.returnValues['alpacaCopyConfig'] = self.ui.alpacaCopyConfig.isChecked()
        self.returnValues['close'] = 'ok'
        self.returnValues['driver'] = self.driver
        self.close()
        return True

    def updateIndiDeviceNameList(self, deviceNames):
        """
        updateIndiDeviceNameList updates the indi device name selectors combobox
        with the discovered entries. therefore it deletes the old list and
        rebuild it new.

        :return: True for test purpose
        """
        self.ui.indiDeviceList.clear()
        self.ui.indiDeviceList.setView(QListView())
        for deviceName in deviceNames:
            self.ui.indiDeviceList.addItem(deviceName)
        return True

    def discoverIndiDevices(self):
        """
        discoverIndiDevices looks all possible indi devices up from the actual
        server and the selected device type. The search time is defined in indi
        class and should be about 2-3 seconds. if the search was successful,
        the gui and the device list will be updated

        :return: success
        """
        indi = IndiClass(app=self.app)
        indi.hostaddress = self.ui.indiHostAddress.text()
        indi.port = self.ui.indiPort.text()

        self.changeStyleDynamic(self.ui.indiDiscover, 'running', True)
        deviceNames = indi.discoverDevices(deviceType=self.deviceType)
        self.changeStyleDynamic(self.ui.indiDiscover, 'running', False)

        if not deviceNames:
            self.msg.emit(2, 'INDI', 'Device', 'No devices found')
            return False

        for deviceName in deviceNames:
            self.msg.emit(0, 'INDI', 'Device discovered', f'{deviceName}')

        self.updateIndiDeviceNameList(deviceNames=deviceNames)
        return True

    def updateAlpacaDeviceNameList(self, deviceNames):
        """
        updateAlpacaDeviceNameList updates the indi device name selectors
        combobox with the discovered entries. therefore it deletes the old list
        and rebuild it new.

        :return: True for test purpose
        """
        self.ui.alpacaDeviceList.clear()
        self.ui.alpacaDeviceList.setView(QListView())
        for deviceName in deviceNames:
            self.ui.alpacaDeviceList.addItem(deviceName)
        return True

    def discoverAlpacaDevices(self):
        """
        discoverAlpacaDevices looks all possible alpaca devices up from the
        actual server and the selected device type.

        :return: success
        """
        alpaca = AlpacaClass(app=self.app)
        alpaca.hostaddress = self.ui.alpacaHostAddress.text()
        alpaca.port = self.ui.alpacaPort.text()
        alpaca.apiVersion = 1

        self.changeStyleDynamic(self.ui.alpacaDiscover, 'running', True)
        deviceNames = alpaca.discoverDevices(deviceType=self.deviceType)
        self.changeStyleDynamic(self.ui.alpacaDiscover, 'running', False)

        if not deviceNames:
            self.msg.emit(2, 'ALPACA', 'Device', 'No devices found')
            return False

        for deviceName in deviceNames:
            self.msg.emit(0, 'ALPACA', 'Device discovered', f'{deviceName}')

        self.updateAlpacaDeviceNameList(deviceNames=deviceNames)
        return True

    def updateSGProDeviceNameList(self, deviceNames):
        """
        updateSGProDeviceNameList updates the indi device name selectors
        combobox with the discovered entries. therefore it deletes the old list
        and rebuild it new.

        :return: True for test purpose
        """
        self.ui.sgproDeviceList.clear()
        self.ui.sgproDeviceList.setView(QListView())
        for deviceName in deviceNames:
            self.ui.sgproDeviceList.addItem(deviceName)
        return True

    def discoverSGProDevices(self):
        """
        discoverSGProDevices looks all possible alpaca devices up from the
        actual server and the selected device type.

        :return: success
        """
        sgpro = SGProClass(app=self.app)
        sgpro.DEVICE_TYPE = 'Camera'

        self.changeStyleDynamic(self.ui.sgproDiscover, 'running', True)
        deviceNames = sgpro.discoverDevices()
        if not deviceNames:
            self.msg.emit(2, 'SGPRO', 'Device', 'No devices found')

        deviceNames.insert(0, 'SGPro controlled')
        self.changeStyleDynamic(self.ui.sgproDiscover, 'running', False)

        for deviceName in deviceNames:
            self.msg.emit(0, 'SGPRO', 'Device discovered', f'{deviceName}')

        self.updateSGProDeviceNameList(deviceNames=deviceNames)
        return True

    def updateNINADeviceNameList(self, deviceNames):
        """
        updateSGProDeviceNameList updates the indi device name selectors
        combobox with the discovered entries. therefore it deletes the old list
        and rebuild it new.

        :return: True for test purpose
        """
        self.ui.ninaDeviceList.clear()
        self.ui.ninaDeviceList.setView(QListView())
        for deviceName in deviceNames:
            self.ui.ninaDeviceList.addItem(deviceName)
        return True

    def discoverNINADevices(self):
        """
        discoverSGProDevices looks all possible alpaca devices up from the
        actual server and the selected device type.

        :return: success
        """
        nina = NINAClass(app=self.app)
        nina.DEVICE_TYPE = 'Camera'

        self.changeStyleDynamic(self.ui.ninaDiscover, 'running', True)
        deviceNames = nina.discoverDevices()
        if not deviceNames:
            self.msg.emit(2, 'N.I.N.A.', 'Device', 'No devices found')

        deviceNames.insert(0, 'N.I.N.A. controlled')
        self.changeStyleDynamic(self.ui.ninaDiscover, 'running', False)

        for deviceName in deviceNames:
            self.msg.emit(0, 'N.I.N.A.', 'Device discovered', f'{deviceName}')

        self.updateNINADeviceNameList(deviceNames=deviceNames)
        return True

    def checkPlateSolveAvailability(self, framework, appPath, indexPath):
        """
        checkAvailability looks the presence of the binaries and indexes up and
        reports the result back to the gui.

        :return: success
        """
        sucApp, sucIndex = self.app.plateSolve.run[framework].checkAvailability(
            appPath=appPath, indexPath=indexPath)

        if framework == 'astap':
            color = 'green' if sucApp else 'red'
            self.changeStyleDynamic(self.ui.astapAppPath, 'color', color)
            color = 'green' if sucIndex else 'red'
            self.changeStyleDynamic(self.ui.astapIndexPath, 'color', color)

        elif framework == 'watney':
            color = 'green' if sucApp else 'red'
            self.changeStyleDynamic(self.ui.watneyAppPath, 'color', color)
            color = 'green' if sucIndex else 'red'
            self.changeStyleDynamic(self.ui.watneyIndexPath, 'color', color)

        elif framework == 'astrometry':
            color = 'green' if sucApp else 'red'
            self.changeStyleDynamic(self.ui.astrometryAppPath, 'color', color)
            color = 'green' if sucIndex else 'red'
            self.changeStyleDynamic(self.ui.astrometryIndexPath, 'color', color)
        return True

    def updatePlateSolverStatus(self):
        """
        :return:
        """
        self.checkPlateSolveAvailability('astrometry',
                                         self.ui.astrometryAppPath.text(),
                                         self.ui.astrometryIndexPath.text())
        self.checkPlateSolveAvailability('watney',
                                         self.ui.watneyAppPath.text(),
                                         self.ui.watneyIndexPath.text())
        self.checkPlateSolveAvailability('astap',
                                         self.ui.astapAppPath.text(),
                                         self.ui.astapIndexPath.text())
        return True

    def selectAstrometryAppPath(self):
        """
        :return:
        """
        folder = self.ui.astrometryAppPath.text()
        folder = folder if folder else '/'
        saveFilePath, name, ext = self.openDir(self,
                                               'Select Astrometry App Path',
                                               folder)
        if not name:
            return False

        if platform.system() == 'Darwin' and ext == '.app':
            if 'Astrometry.app' in saveFilePath:
                saveFilePath += '/Contents/MacOS/'

            else:
                saveFilePath += '/Contents/MacOS/astrometry/bin'

        self.checkPlateSolveAvailability('astrometry',
                                         saveFilePath,
                                         self.ui.astrometryIndexPath.text())
        self.ui.astrometryAppPath.setText(saveFilePath)
        return True

    def selectAstrometryIndexPath(self):
        """
        :return:
        """
        folder = self.ui.astrometryIndexPath.text()
        folder = folder if folder else '/'
        saveFilePath, name, ext = self.openDir(self,
                                               'Select Astrometry Index Path',
                                               folder)
        if not name:
            return False

        self.checkPlateSolveAvailability('astrometry',
                                         self.ui.astrometryAppPath.text(),
                                         saveFilePath)
        self.ui.astrometryIndexPath.setText(saveFilePath)
        return True

    def selectAstapAppPath(self):
        """
        :return:
        """
        folder = self.ui.astapAppPath.text()
        folder = folder if folder else '/'
        saveFilePath, name, ext = self.openDir(self,
                                               'Select ASTAP App Path',
                                               folder)
        if not name:
            return False

        if platform.system() == 'Darwin' and ext == '.app':
            saveFilePath += '/Contents/MacOS'

        self.checkPlateSolveAvailability('astap',
                                         saveFilePath,
                                         self.ui.astapIndexPath.text())
        self.ui.astapAppPath.setText(saveFilePath)
        return True

    def selectAstapIndexPath(self):
        """
        :return:
        """
        folder = self.ui.astapIndexPath.text()
        folder = folder if folder else '/'
        saveFilePath, name, ext = self.openDir(self,
                                               'Select ASTAP Index Path',
                                               folder)
        if not name:
            return False

        self.checkPlateSolveAvailability('astap',
                                         self.ui.astapAppPath.text(),
                                         saveFilePath)
        self.ui.astapIndexPath.setText(saveFilePath)
        return True

    def selectWatneyAppPath(self):
        """
        :return:
        """
        folder = self.ui.watneyAppPath.text()
        folder = folder if folder else '/'
        saveFilePath, name, ext = self.openDir(self,
                                               'Select Watney App Path',
                                               folder)
        if not name:
            return False

        self.checkPlateSolveAvailability('watney',
                                         saveFilePath,
                                         self.ui.watneyIndexPath.text())
        self.ui.watneyAppPath.setText(saveFilePath)
        return True

    def selectWatneyIndexPath(self):
        """
        :return:
        """
        folder = self.ui.watneyIndexPath.text()
        folder = folder if folder else '/'
        saveFilePath, name, ext = self.openDir(self,
                                               'Select Watney Index Path',
                                               folder)
        if not name:
            return False

        self.checkPlateSolveAvailability('watney',
                                         self.ui.watneyAppPath.text(),
                                         saveFilePath)
        self.ui.watneyIndexPath.setText(saveFilePath)
        return True

    def selectAscomDriver(self):
        """
        :return: success
        """
        deviceName = self.ui.ascomDevice.text()
        try:
            chooser = win32com.client.Dispatch('ASCOM.Utilities.Chooser')
            chooser.DeviceType = self.deviceType
            deviceName = chooser.Choose(deviceName)

        except Exception as e:
            self.log.critical(f'Error: {e}')
            return False

        finally:
            self.ui.ascomDevice.setText(deviceName)
        return True
