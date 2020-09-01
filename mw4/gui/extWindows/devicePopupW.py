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
import platform

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QWidget, QListView, QComboBox, QLineEdit
from PyQt5.QtWidgets import QCheckBox, QDoubleSpinBox

if platform.system() == 'Windows':
    import win32com.client

# local import
from base.indiClass import IndiClass
from gui.utilities import widget
from gui.widgets.devicePopup_ui import Ui_DevicePopup


class DevicePopup(QDialog, widget.MWidget):
    """
    the DevicePopup window class handles

    """

    __all__ = ['DevicePopup',
               ]

    framework2tabs = {
        'indi': 'INDI / INDIGO',
        'ascom': 'ASCOM',
        'alpaca': 'ALPACA',
        'astrometry': 'ASTROMETRY',
        'astap': 'ASTAP',
    }

    def __init__(self,
                 app=None,
                 geometry=None,
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
        self.initUI()
        self.setWindowModality(Qt.ApplicationModal)
        x = geometry[0] + int((geometry[2] - self.width()) / 2)
        y = geometry[1] + int((geometry[3] - self.height()) / 2)
        self.move(x, y)

        self.returnValues = {'close': 'cancel'}
        self.framework2gui = {
            'indi': {
                'host': self.ui.indiHost,
                'port': self.ui.indiPort,
                'deviceList': self.ui.indiDeviceList,
                'messages': self.ui.indiMessages,
                'loadConfig': self.ui.indiLoadConfig,
            },
            'alpaca': {
                'host': self.ui.alpacaHost,
                'port': self.ui.alpacaPort,
                'deviceList': self.ui.alpacaDeviceList,
                'protocolList': self.ui.alpacaProtocolList,
                'user': self.ui.alpacaUser,
                'password': self.ui.alpacaPassword,
            },
            'ascom': {
                'device': self.ui.ascomDevice,
            },
            'astrometry': {
                'deviceList': self.ui.astrometryDeviceList,
                'searchRadius': self.ui.astrometrySearchRadius,
                'timeout': self.ui.astrometryTimeout,
                'appPath': self.ui.astrometryIndexPath,
                'indexPath': self.ui.astrometryAppPath,
            },
            'astap': {
                'deviceList': self.ui.astapDeviceList,
                'searchRadius': self.ui.astapSearchRadius,
                'timeout': self.ui.astapTimeout,
                'appPath': self.ui.astapIndexPath,
                'indexPath': self.ui.astapAppPath,
            },
        }

        self.ui.cancel.clicked.connect(self.close)
        self.ui.ok.clicked.connect(self.storeConfig)

        # todo: naming equally to indiSelector, astapIndexPathSelector etc.
        self.ui.indiSearch.clicked.connect(self.discoverIndiDevices)
        self.ui.selectAstrometryIndexPath.clicked.connect(self.selectAstrometryIndexPath)
        self.ui.selectAstrometryAppPath.clicked.connect(self.selectAstrometryAppPath)
        self.ui.selectAstapIndexPath.clicked.connect(self.selectAstapIndexPath)
        self.ui.selectAstapAppPath.clicked.connect(self.selectAstapAppPath)
        self.ui.ascomSelector.clicked.connect(self.selectAscomDriver)

        self.initConfig()
        self.show()

    def selectTabs(self):
        """
        show only the tabs needed for available frameworks and properties to be entered
        as there might be differences in tab text and framework name internally there is a
        translation table (self.framework2tabs) in between.
        - it selects the tab for the actual framework
        - it hides all tabs, which are not relevant for the available frameworks

        :return: True for test purpose
        """

        firstFramework = next(iter(self.data['frameworks']))
        framework = self.data.get('framework')

        if not framework:
            framework = firstFramework

        frameworkTabText = self.framework2tabs[framework]
        frameworkTabList = [self.framework2tabs[x] for x in self.data['frameworks']]

        tabWidget = self.ui.tab.findChild(QWidget, frameworkTabText)
        tabIndex = self.ui.tab.indexOf(tabWidget)
        self.ui.tab.setCurrentIndex(tabIndex)

        for index in range(0, self.ui.tab.count()):
            if self.ui.tab.tabText(index) in frameworkTabList:
                self.ui.tab.setTabEnabled(index, True)
            else:
                self.ui.tab.setTabEnabled(index, False)
            self.ui.tab.setStyleSheet(self.getStyle())

        return True

    def populateTabs(self):
        """
        populateTabs takes all the data coming from driver data dict and puts it onto the
        corresponding gui elements in the tabs. as we need to have unique names in the gui,
        there is a translation table (self.framework2gui) for all framework entries to be
        used.

        :return: True for test purpose
        """

        frameworks = self.data['frameworks']

        for fw in frameworks:
            for prop in frameworks[fw]:
                if prop not in self.framework2gui[fw]:
                    continue

                ui = self.framework2gui[fw][prop]

                if isinstance(ui, QComboBox):
                    ui.clear()
                    ui.setView(QListView())
                    for i, device in enumerate(frameworks[fw][prop]):
                        ui.addItem(device)
                        if frameworks[fw]['deviceName'] == device:
                            ui.setCurrentIndex(i)

                elif isinstance(ui, QLineEdit):
                    ui.setText(f'{frameworks[fw][prop]}')

                elif isinstance(ui, QCheckBox):
                    ui.setChecked(frameworks[fw][prop])

                elif isinstance(ui, QDoubleSpinBox):
                    ui.setValue(frameworks[fw][prop])

                else:
                    self.log.info(f'Property {prop} in gui for framework {fw} not found')

        return True

    def initConfig(self):
        """

        :return: True for test purpose
        """

        self.setWindowTitle(f'Setup for: {self.driver}')
        self.selectTabs()
        self.populateTabs()

        return True

    def readTabs(self):
        """
        readTabs takes all the gui information and puts it onto the data dictionary and
        properties as we need to have unique names in the gui, there is a translation table
        (self.framework2gui) for all framework entries to be used.

        :return: True for test purpose
        """

        framework = self.data['framework']
        frameworkData = self.data['frameworks'][framework]

        for prop in list(frameworkData):
            if prop not in self.framework2gui[framework]:
                continue

            ui = self.framework2gui[framework][prop]

            if isinstance(ui, QComboBox):
                frameworkData['deviceName'] = ui.currentText()
                frameworkData[prop].clear()
                for index in range(ui.model().rowCount()):
                    frameworkData[prop].append(ui.model().item(index).text())

            elif isinstance(ui, QLineEdit):
                if isinstance(frameworkData[prop], str):
                    frameworkData[prop] = ui.text()

                elif isinstance(frameworkData[prop], int):
                    frameworkData[prop] = int(ui.text())

                else:
                    frameworkData[prop] = float(ui.text())

            elif isinstance(ui, QCheckBox):
                frameworkData[prop] = ui.isChecked()

            elif isinstance(ui, QDoubleSpinBox):
                frameworkData[prop] = ui.value()

            else:
                self.log.info(f'Property {prop} in gui for framework {framework} not found')

        return True

    def readFramework(self):
        """
        readFramework determines, which tab was selected when leaving and writes the
        adequate selection into the property. as the headline might be different from the
        keywords, a translation table (self.framework2gui) in a reverse index is used.

        :return: True for test purpose
        """

        index = self.ui.tab.currentIndex()
        currentSelection = self.ui.tab.tabText(index)

        searchD = dict([(value, key) for key, value in self.framework2tabs.items()])
        self.data['framework'] = searchD[currentSelection]

        return True

    def storeConfig(self):
        """
        storeConfig collects all the data changed

        :return: true for test purpose
        """

        self.readFramework()
        self.readTabs()
        self.returnValues['indiCopyConfig'] = self.ui.indiCopyConfig.isChecked()
        self.returnValues['alpacaCopyConfig'] = self.ui.alpacaCopyConfig.isChecked()
        self.returnValues['close'] = 'ok'
        self.close()

        return True

    def updateIndiDeviceNameList(self, deviceNames=[]):
        """
        updateIndiDeviceNameList updates the indi device name selectors combobox with the
        discovered entries. therefore it deletes the old list and rebuild it new.

        :return: True for test purpose
        """

        self.ui.indiDeviceList.clear()
        self.ui.indiDeviceList.setView(QListView())

        for deviceName in deviceNames:
            self.ui.indiDeviceList.addItem(deviceName)

        return True

    def discoverIndiDevices(self):
        """
        discoverIndiDevices looks all possible indi devices up from the actual server and
        the selected device type. The search time is defined in indi class and should be
        about 2-3 seconds. if the search was successful, the gui and the device list will
         be updated

        :return: success
        """

        host = (self.ui.indiHost.text(), int(self.ui.indiPort.text()))
        indi = IndiClass()
        indi.host = host

        deviceNames = indi.discoverDevices(deviceType=self.deviceType)

        if not deviceNames:
            self.message.emit('Indi search found no devices', 2)
            return False

        for deviceName in deviceNames:
            self.message.emit(f'Indi search found device: [{deviceName}]', 0)

        self.updateIndiDeviceNameList(deviceNames=deviceNames)

        return True

    def checkAstrometryAvailability(self, framework):
        """
        checkAvailability looks the presence of the binaries and indexes up and reports the
        result back to the gui.

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
