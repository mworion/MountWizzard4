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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import platform

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QListView, QComboBox, QLineEdit
from PyQt5.QtWidgets import QCheckBox, QDoubleSpinBox

if platform.system() == 'Windows':
    import win32com.client

# local import
from base.indiClass import IndiClass
from base.alpacaClass import AlpacaClass
from gui.utilities import toolsQtWidget
from gui.widgets.devicePopup_ui import Ui_DevicePopup


class DevicePopup(toolsQtWidget.MWidget):
    """
    """

    __all__ = ['DevicePopup',
               ]

    framework2tabs = {
        'indi': 'INDI / INDIGO',
        'ascom': 'ASCOM',
        'alpaca': 'ALPACA',
        'astrometry': 'ASTROMETRY',
        'astap': 'ASTAP',
        'onlineWeather': 'Online Weather',
        'relay': 'Relay',
    }

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
        self.message = app.message

        self.ui = Ui_DevicePopup()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        x = parentWidget.x() + int((parentWidget.width() - self.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - self.height()) / 2)
        self.move(x, y)
        pixmap = QPixmap(':/icon/cogs.svg')
        self.ui.iconPixmap.setPixmap(pixmap)

        self.returnValues = {'close': 'cancel'}
        self.framework2gui = {
            'indi': {
                'hostaddress': self.ui.indiHostAddress,
                'port': self.ui.indiPort,
                'deviceList': self.ui.indiDeviceList,
                'messages': self.ui.indiMessages,
                'loadConfig': self.ui.indiLoadConfig,
            },
            'alpaca': {
                'hostaddress': self.ui.alpacaHostAddress,
                'port': self.ui.alpacaPort,
                'deviceList': self.ui.alpacaDeviceList,
                'user': self.ui.alpacaUser,
                'password': self.ui.alpacaPassword,
            },
            'ascom': {
                'deviceName': self.ui.ascomDevice,
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
            'onlineWeather': {
                'apiKey': self.ui.onlineWeatherApiKey,
                'hostaddress': self.ui.onlineWeatherHostAddress,
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
        self.ui.selectAstrometryIndexPath.clicked.connect(self.selectAstrometryIndexPath)
        self.ui.selectAstrometryAppPath.clicked.connect(self.selectAstrometryAppPath)
        self.ui.selectAstapIndexPath.clicked.connect(self.selectAstapIndexPath)
        self.ui.selectAstapAppPath.clicked.connect(self.selectAstapAppPath)
        self.ui.ascomSelector.clicked.connect(self.selectAscomDriver)

        self.initConfig()
        self.show()

    def selectTabs(self):
        """
        show only the tabs needed for available frameworks and properties to be
        entered as there might be differences in tab text and framework name
        internally there is a translation table (self.framework2tabs) in between.
        - it selects the tab for the actual framework
        - it hides all tabs, which are not relevant for the available frameworks

        :return: True for test purpose
        """
        firstFramework = next(iter(self.data['frameworks']))
        framework = self.data.get('framework')

        if not framework:
            framework = firstFramework

        frameworkTabText = self.framework2tabs[framework]
        frameworkTabTextList = [self.framework2tabs[x] for x in self.data['frameworks']]

        tabWidget = self.ui.tab.findChild(QWidget, frameworkTabText)
        tabIndex = self.ui.tab.indexOf(tabWidget)
        self.ui.tab.setCurrentIndex(tabIndex)

        for index in range(0, self.ui.tab.count()):
            if self.ui.tab.tabText(index) in frameworkTabTextList:
                self.ui.tab.setTabEnabled(index, True)

            else:
                self.ui.tab.setTabEnabled(index, False)

            self.ui.tab.setStyleSheet(self.getStyle())
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
        self.setWindowTitle(f'Setup for: {self.deviceType}')
        self.selectTabs()
        self.populateTabs()
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

            else:
                self.log.debug(f'Element {element} in gui for framework {framework} not found')
        return True

    def readFramework(self):
        """
        readFramework determines, which tab was selected when leaving and writes
        the adequate selection into the dict. as the headline might be different
        from the keywords, a translation table (self.framework2gui) in a reverse
        index is used.

        :return: True for test purpose
        """
        reversedDict = dict([(value, key) for key, value in self.framework2tabs.items()])
        index = self.ui.tab.currentIndex()
        currentSelectionText = self.ui.tab.tabText(index)
        self.data['framework'] = reversedDict[currentSelectionText]
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

    def updateIndiDeviceNameList(self, deviceNames=[]):
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
        indi = IndiClass()
        indi.hostaddress = self.ui.indiHostAddress.text()
        indi.port = self.ui.indiPort.text()

        self.changeStyleDynamic(self.ui.indiDiscover, 'running', True)
        deviceNames = indi.discoverDevices(deviceType=self.deviceType)
        self.changeStyleDynamic(self.ui.indiDiscover, 'running', False)

        if not deviceNames:
            self.message.emit('Indi no devices found', 2)
            return False

        for deviceName in deviceNames:
            self.message.emit(f'Indi discovered:     [{deviceName}]', 0)

        self.updateIndiDeviceNameList(deviceNames=deviceNames)
        return True

    def updateAlpacaDeviceNameList(self, deviceNames=[]):
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
        alpaca = AlpacaClass()
        alpaca.hostaddress = self.ui.alpacaHostAddress.text()
        alpaca.port = self.ui.alpacaPort.text()
        alpaca.apiVersion = 1

        self.changeStyleDynamic(self.ui.alpacaDiscover, 'running', True)
        deviceNames = alpaca.discoverDevices(deviceType=self.deviceType)
        self.changeStyleDynamic(self.ui.alpacaDiscover, 'running', False)

        if not deviceNames:
            self.message.emit('Alpaca no devices found', 2)
            return False

        for deviceName in deviceNames:
            self.message.emit(f'Alpaca discovered:   [{deviceName}]', 0)

        self.updateAlpacaDeviceNameList(deviceNames=deviceNames)
        return True

    def checkAstrometryAvailability(self, framework):
        """
        checkAvailability looks the presence of the binaries and indexes up and
        reports the result back to the gui.

        :return: success
        """
        sucApp, sucIndex = self.app.astrometry.run[framework].checkAvailability()
        if framework == 'astap':
            color = 'green' if sucApp else 'red'
            self.changeStyleDynamic(self.ui.astapAppPath, 'color', color)
            color = 'green' if sucIndex else 'red'
            self.changeStyleDynamic(self.ui.astapIndexPath, 'color', color)

        else:
            color = 'green' if sucApp else 'red'
            self.changeStyleDynamic(self.ui.astrometryAppPath, 'color', color)
            color = 'green' if sucIndex else 'red'
            self.changeStyleDynamic(self.ui.astrometryIndexPath, 'color', color)
        return True

    def selectAstrometryAppPath(self):
        """
        :return:
        """
        folder = self.ui.astrometryAppPath.text()
        saveFilePath, name, ext = self.openDir(self,
                                               'Select Astrometry App Path',
                                               folder,
                                               )
        if not name:
            return False

        if platform.system() == 'Darwin' and ext == '.app':
            if 'Astrometry.app' in saveFilePath:
                saveFilePath += '/Contents/MacOS/'

            else:
                saveFilePath += '/Contents/MacOS/astrometry/bin'

        if self.checkAstrometryAvailability('astrometry'):
            self.ui.astrometryAppPath.setText(saveFilePath)
        return True

    def selectAstrometryIndexPath(self):
        """
        :return:
        """
        folder = self.ui.astrometryIndexPath.text()
        saveFilePath, name, ext = self.openDir(self,
                                               'Select Astrometry Index Path',
                                               folder,
                                               )
        if not name:
            return False

        if self.checkAstrometryAvailability('astrometry'):
            self.ui.astrometryIndexPath.setText(saveFilePath)
        return True

    def selectAstapAppPath(self):
        """
        :return:
        """
        folder = self.ui.astapAppPath.text()
        saveFilePath, name, ext = self.openDir(self,
                                               'Select ASTAP App Path',
                                               folder,
                                               )
        if not name:
            return False

        if platform.system() == 'Darwin' and ext == '.app':
            saveFilePath += '/Contents/MacOS'

        if self.checkAstrometryAvailability('astap'):
            self.ui.astapAppPath.setText(saveFilePath)
        return True

    def selectAstapIndexPath(self):
        """
        :return:
        """
        folder = self.ui.astapIndexPath.text()
        saveFilePath, name, ext = self.openDir(self,
                                               'Select ASTAP Index Path',
                                               folder,
                                               )
        if not name:
            return False

        if self.checkAstrometryAvailability('astap'):
            self.ui.astapIndexPath.setText(saveFilePath)
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
