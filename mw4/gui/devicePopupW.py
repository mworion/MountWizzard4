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
import PyQt5.QtCore
# import .NET / COM Handling

if platform.system() == 'Windows':
    import win32com.client

# local import
from mw4.base.indiClass import IndiClass
from mw4.gui import widget
from mw4.gui.widgets.devicePopup_ui import Ui_DevicePopup


class DevicePopup(PyQt5.QtWidgets.QDialog, widget.MWidget):
    """
    the DevicePopup window class handles

    """

    __all__ = ['DevicePopup',
               ]

    # INDI device types
    indiTypes = {
        'telescope': (1 << 0),
        'camera': (1 << 1),
        'guider': (1 << 2),
        'focuser': (1 << 3),
        'filterwheel': (1 << 4),
        'dome': (1 << 5),
        'observingconditions': (1 << 7),
        'skymeter': 0,
        'cover': (1 << 9) | (1 << 10),
        'power': (1 << 7) | (1 << 3)
    }

    indiDefaults = {
        'telescope': 'LX200 10micron',
    }

    framework2tabs = {
        'indi': 'INDI',
        'ascom': 'ASCOM',
        'alpaca': 'ALPACA',
        'astrometry': 'ASTROMETRY',
        'astap': 'ASTAP',
    }

    def __init__(self,
                 app=None,
                 geometry=None,
                 driver=None,
                 data=None):

        super().__init__()
        self.app = app
        self.data = data
        self.driver = driver
        self.returnValues = {'close': 'cancel'}

        self.ui = Ui_DevicePopup()
        self.ui.setupUi(self)
        self.initUI()

        self.setWindowModality(Qt.ApplicationModal)
        x = geometry[0] + int((geometry[2] - self.width()) / 2)
        y = geometry[1] + int((geometry[3] - self.height()) / 2)
        self.move(x, y)

        self.framework2gui = {
            'indi': {
                'host': self.ui.indiHost,
                'port': self.ui.indiPort,
                'deviceList': self.ui.indiDeviceList,
                'messages': self.ui.indiMessages,
                'loadConfig': self.ui.indiLoadConfig,
                'copyConfig': self.ui.indiCopyConfig,
            },
            'alpaca': {
                'host': self.ui.alpacaHost,
                'port': self.ui.alpacaPort,
                'deviceList': self.ui.alpacaDeviceList,
                'protocolList': self.ui.alpacaProtocolList,
                'user': self.ui.alpacaUser,
                'password': self.ui.alpacaPassword,
                'copyConfig': self.ui.alpacaCopyConfig,
            },
            'ascom': {
                'device': self.ui.ascomDevice,
            },
            'astrometry': {
                'deviceList': self.ui.astrometryDeviceList,
                'searchRadius': self.ui.astrometrySearchRadius,
                'timeout': self.ui.astrometryTimeout,
                'indexPath': self.ui.astrometryIndexPath,
            },
            'astap': {
                'deviceList': self.ui.astapDeviceList,
                'searchRadius': self.ui.astapSearchRadius,
                'timeout': self.ui.astapTimeout,
                'indexPath': self.ui.astapIndexPath,
            },
        }

        self.ui.cancel.clicked.connect(self.close)
        self.ui.ok.clicked.connect(self.storeConfig)
        self.ui.indiSearch.clicked.connect(self.searchDevices)
        self.ui.selectAstrometryIndexPath.clicked.connect(self.selectAstrometryIndexPath)
        self.ui.selectAstrometryAppPath.clicked.connect(self.selectAstrometryAppPath)
        self.ui.selectAstapIndexPath.clicked.connect(self.selectAstapIndexPath)
        self.ui.selectAstapAppPath.clicked.connect(self.selectAstapAppPath)
        self.ui.ascomSelector.clicked.connect(self.setupAscomDriver)

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

        framework = self.data['framework']
        frameworkTabText = self.framework2tabs[framework]
        frameworkTabList = [self.framework2tabs[x] for x in self.data['frameworks']]

        tabWidget = self.ui.tab.findChild(PyQt5.QtWidgets.QWidget, frameworkTabText)
        tabIndex = self.ui.tab.indexOf(tabWidget)
        self.ui.tab.setCurrentIndex(tabIndex)

        for index in range(0, self.ui.tab.count()):
            if self.ui.tab.tabText(index).lower() in self.availFramework:
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
                        if frameworks[fw][prop[:-4]] == device:
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

        frameworks = self.data['frameworks']

        for fw in frameworks:
            for prop in frameworks[fw]:
                if prop not in self.framework2gui[fw]:
                    continue

                ui = self.framework2gui[fw][prop]

                if isinstance(ui, QComboBox):
                    frameworks[fw][prop[:-4]] = ui.currentText()
                    frameworks[fw][prop].clear()
                    for index in range(ui.model().rowCount()):
                        frameworks[fw][prop].append(ui.model().item(index).text())

                elif isinstance(ui, QLineEdit):
                    if isinstance(frameworks[fw][prop], str):
                        frameworks[fw][prop] = ui.text()
                    elif isinstance(frameworks[fw][prop], int):
                        frameworks[fw][prop] = int(ui.text())
                    else:
                        frameworks[fw][prop] = float(ui.text())

                elif isinstance(ui, QCheckBox):
                    frameworks[fw][prop] = ui.isChecked()

                elif isinstance(ui, QDoubleSpinBox):
                    frameworks[fw][prop] = ui.value()

                else:
                    self.log.info(f'Property {prop} in gui for framework {fw} not found')

        return True

    def readFramework(self):
        """
        readFramework determines, which tab was selected when leaving and writes the
        adequate selection into the property. as the headline might be different from the
        keywords, a translation table (self.framework2gui) is used.

        :return: True for test purpose
        """

        index = self.ui.tab.currentIndex()
        currentSelection = self.ui.tab.tabText(index)
        for fw in self.data['frameworks']:
            if currentSelection == self.framework2gui[fw]:
                break
        self.data['framework'] = fw

        return True

    def storeConfig(self):
        """
        storeConfig collects all the data changed

        :return: true for test purpose
        """

        self.readTabs()
        self.readFramework()
        self.returnValues['close'] = 'ok'
        self.close()

        return True

    def addDevicesWithType(self, deviceName, propertyName):
        """
        addDevicesWithType gety called whenever a new device send out text messages. than it
        checks, if the device type fits to the search type desired. if they match, the
        device name is added to the list.

        :param deviceName:
        :param propertyName:
        :return: success
        """

        device = self._indiClass.client.devices.get(deviceName)
        if not device:
            return False

        interface = device.getText(propertyName).get('DRIVER_INTERFACE', None)

        if interface is None:
            return False

        if self._indiSearchType is None:
            return False

        interface = int(interface)

        if interface & self._indiSearchType:
            self._indiSearchNameList.append(deviceName)

        return True

    def searchDevices(self):
        """
        searchDevices implements a search for devices of a certain device type. it is called
        from a button press and checks which button it was. after that for the right device
        it collects all necessary data for host value, instantiates an INDI client and
        watches for all devices connected to this server. Than it connects a subroutine for
        collecting the right device names and opens a model dialog. the data collection
        takes place as long as the model dialog is open. when the user closes this dialog, the
        collected data is written to the drop down list.

        :return:  success finding
        """

        self._indiSearchNameList = list()

        if self.driver in self.indiDefaults:
            self._indiSearchNameList.append(self.indiDefaults[self.driver])

        else:
            host = (self.ui.indiHost.text(), int(self.ui.indiPort.text()))
            self._indiClass = IndiClass()
            self._indiClass.host = host

            self._indiClass.client.signals.defText.connect(self.addDevicesWithType)
            self._indiClass.client.connectServer()
            self._indiClass.client.watchDevice()
            msg = PyQt5.QtWidgets.QMessageBox
            msg.information(self,
                            'Searching Devices',
                            f'Search for [{self.driver}] could take some seconds!')
            self._indiClass.client.disconnectServer()

        self.ui.indiDeviceList.clear()
        self.ui.indiDeviceList.setView(PyQt5.QtWidgets.QListView())

        for name in self._indiSearchNameList:
            self.log.info(f'Indi search found: {name}')

        for deviceName in self._indiSearchNameList:
            self.ui.indiDeviceList.addItem(deviceName)

        return True

    def checkAvailability(self, framework):
        """

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

        if self.checkAvailability('astrometry'):
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

        if self.checkAvailability('astrometry'):
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

        if self.checkAvailability('astap'):
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

        if self.checkAvailability('astap'):
            self.ui.astapIndexPath.setText(saveFilePath)

        return True

    def setupAscomDriver(self):
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
