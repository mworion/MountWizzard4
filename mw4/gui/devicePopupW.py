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
        'skymeter': 'SQM',
        'power': 'Pegasus UPB',
    }

    def __init__(self,
                 app=None,
                 geometry=None,
                 driver='',
                 deviceType='',
                 availFramework={},
                 data=None):

        super().__init__()
        self.app = app
        self.data = data
        self.driver = driver
        self.deviceType = deviceType
        self.availFramework = availFramework
        self.returnValues = {'close': 'cancel'}

        self.ui = Ui_DevicePopup()
        self.ui.setupUi(self)
        self.initUI()
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
        x = geometry[0] + int((geometry[2] - self.width()) / 2)
        y = geometry[1] + int((geometry[3] - self.height()) / 2)
        self.move(x, y)

        """
        self.deviceFramework = {
            'indi': {'host': self.ui.indiHost,
                     'port': self.ui.indiPort,
                     'device': self.ui.indiDeviceList,
                     'messages': self.ui.indiMessages,
                     'loadConfig': self.ui.indiLoadConfig,
                     },
            'alpaca': {'host': self.ui.alpacaHost,
                       'port': self.ui.alpacaPort,
                       'device': self.ui.alpacaDevice,
                       'number': self.ui.alpacaNumber,
                       'user': self.ui.alpacaUser,
                       'password': self.ui.alpacaPassword,
                       'protocol': self.ui.alpacaProtocol,
                       },
            'ascom': {'device': self.ui.ascomDevice,
                      },
            'astrometry': {'device': self.ui.astrometryDeviceList,
                           'searchRadius': self.ui.astrometrySearchRadius,
                           'timeout': self.ui.astrometryTimeout,
                           'indexPath': self.ui.astrometryIndexPath,
                           },
            'astap': {'device': self.ui.astapDeviceList,
                      'searchRadius': self.ui.astapSearchRadius,
                      'timeout': self.ui.astapTimeout,
                      'indexPath': self.ui.astapIndexPath,
                      },
        }
        """

        self._indiClass = None
        self._indiSearchNameList = ()
        self._indiSearchType = None

        self.ui.cancel.clicked.connect(self.close)
        self.ui.ok.clicked.connect(self.storeConfig)
        self.ui.indiSearch.clicked.connect(self.searchDevices)
        self.ui.selectAstrometryIndexPath.clicked.connect(self.selectAstrometryIndexPath)
        self.ui.selectAstrometryAppPath.clicked.connect(self.selectAstrometryAppPath)
        self.ui.selectAstapIndexPath.clicked.connect(self.selectAstapIndexPath)
        self.ui.selectAstapAppPath.clicked.connect(self.selectAstapAppPath)
        self.ui.copyAlpaca.clicked.connect(self.copyAllAlpacaSettings)
        self.ui.copyIndi.clicked.connect(self.copyAllIndiSettings)
        self.ui.ascomSelector.clicked.connect(self.setupAscomDriver)

        self.initConfig()
        self.show()

    def initConfig(self):
        """

        :return: True for test purpose
        """

        # populate data
        deviceData = self.data.get(self.driver, {})
        selectedFramework = deviceData.get('framework', '')
        self._indiSearchType = self.indiTypes.get(self.deviceType, 0xff)

        self.setWindowTitle(f'Setup for: {self.driver}')

        # populating indi data
        self.ui.indiHost.setText(deviceData.get('indiHost', 'localhost'))
        self.ui.indiPort.setText(deviceData.get('indiPort', '7624'))
        self.ui.indiDeviceList.clear()
        self.ui.indiDeviceList.setView(PyQt5.QtWidgets.QListView())
        indiName = deviceData.get('indiName', '')
        nameList = deviceData.get('indiDeviceList', [])
        if not nameList:
            self.ui.indiDeviceList.addItem('-')
        for i, name in enumerate(nameList):
            self.ui.indiDeviceList.addItem(name)
            if indiName == name:
                self.ui.indiDeviceList.setCurrentIndex(i)
        self.ui.indiMessages.setChecked(deviceData.get('indiMessages', False))
        self.ui.indiLoadConfig.setChecked(deviceData.get('indiLoadConfig', False))

        # populating alpaca data
        self.ui.alpacaProtocol.setCurrentIndex(deviceData.get('alpacaProtocol', 0))
        self.ui.alpacaHost.setText(deviceData.get('alpacaHost', 'localhost'))
        self.ui.alpacaPort.setText(deviceData.get('alpacaPort', '11111'))
        device, number = deviceData.get('alpacaName', '"":0').split(':')
        self.ui.alpacaDevice.setText(device)
        self.ui.alpacaNumber.setValue(int(number))
        self.ui.alpacaUser.setText(deviceData.get('alpacaUser', ''))
        self.ui.alpacaPassword.setText(deviceData.get('alpacaPassword', ''))

        # populating astrometry
        astrometryName = deviceData.get('astrometryName', '')
        nameList = deviceData.get('astrometryDeviceList', [])
        if not nameList:
            self.ui.astrometryDeviceList.addItem('-')
        for i, name in enumerate(nameList):
            self.ui.astrometryDeviceList.addItem(name)
            if astrometryName == name:
                self.ui.astrometryDeviceList.setCurrentIndex(i)
        self.ui.astrometryIndexPath.setText(deviceData.get('astrometryIndexPath', '/'))
        self.ui.astrometryAppPath.setText(deviceData.get('astrometryAppPath', '/'))
        self.ui.astrometryTimeout.setValue(deviceData.get('astrometryTimeout', 30))
        self.ui.astrometrySearchRadius.setValue(deviceData.get('astrometrySearchRadius', 20))
        self.checkAvailability('astrometry')

        # populating astap
        astapName = deviceData.get('astapName', '')
        nameList = deviceData.get('astapDeviceList', [])
        if not nameList:
            self.ui.astapDeviceList.addItem('-')
        for i, name in enumerate(nameList):
            self.ui.astapDeviceList.addItem(name)
            if astapName == name:
                self.ui.astrometryDeviceList.setCurrentIndex(i)
        self.ui.astapIndexPath.setText(deviceData.get('astapIndexPath', '/'))
        self.ui.astapAppPath.setText(deviceData.get('astapAppPath', '/'))
        self.ui.astapTimeout.setValue(deviceData.get('astapTimeout', 30))
        self.ui.astapSearchRadius.setValue(deviceData.get('astapSearchRadius', 20))
        self.checkAvailability('astap')

        # populating ascom
        self.ui.ascomDevice.setText(deviceData.get('ascomName', ''))

        # for fw in self.framework:
        tabWidget = self.ui.tab.findChild(PyQt5.QtWidgets.QWidget, selectedFramework)
        tabIndex = self.ui.tab.indexOf(tabWidget)
        self.ui.tab.setCurrentIndex(tabIndex)

        for index in range(0, self.ui.tab.count()):
            if self.ui.tab.tabText(index).lower() in self.availFramework:
                self.ui.tab.setTabEnabled(index, True)
            else:
                self.ui.tab.setTabEnabled(index, False)
            self.ui.tab.setStyleSheet(self.getStyle())

        return True

    def storeConfig(self):
        """

        :return: true for test purpose
        """
        # collecting indi data
        self.data[self.driver]['indiHost'] = self.ui.indiHost.text()
        self.data[self.driver]['indiPort'] = self.ui.indiPort.text()
        self.data[self.driver]['indiName'] = self.ui.indiDeviceList.currentText()

        model = self.ui.indiDeviceList.model()
        nameList = []
        for index in range(model.rowCount()):
            nameList.append(model.item(index).text())
        self.data[self.driver]['indiDeviceList'] = nameList
        self.data[self.driver]['indiMessages'] = self.ui.indiMessages.isChecked()
        self.data[self.driver]['indiLoadConfig'] = self.ui.indiLoadConfig.isChecked()

        # collecting alpaca data
        self.data[self.driver]['alpacaProtocol'] = self.ui.alpacaProtocol.currentIndex()
        self.data[self.driver]['alpacaHost'] = self.ui.alpacaHost.text()
        self.data[self.driver]['alpacaPort'] = self.ui.alpacaPort.text()
        name = f'{self.deviceType}:{self.ui.alpacaNumber.value()}'
        self.data[self.driver]['alpacaName'] = name
        self.data[self.driver]['alpacaUser'] = self.ui.alpacaUser.text()
        self.data[self.driver]['alpacaPassword'] = self.ui.alpacaPassword.text()

        # collecting astrometry data
        self.data[self.driver]['astrometryName'] = self.ui.astrometryDeviceList.currentText()
        model = self.ui.astrometryDeviceList.model()
        nameList = []
        for index in range(model.rowCount()):
            nameList.append(model.item(index).text())
        self.data[self.driver]['astrometryDeviceList'] = nameList
        self.data[self.driver]['astrometryIndexPath'] = self.ui.astrometryIndexPath.text()
        self.data[self.driver]['astrometryAppPath'] = self.ui.astrometryAppPath.text()
        self.data[self.driver]['astrometrySearchRadius'] = self.ui.astrometrySearchRadius.value()
        self.data[self.driver]['astrometryTimeout'] = self.ui.astrometryTimeout.value()

        # collecting astap data
        self.data[self.driver]['astapName'] = self.ui.astapDeviceList.currentText()
        model = self.ui.astapDeviceList.model()
        nameList = []
        for index in range(model.rowCount()):
            nameList.append(model.item(index).text())
        self.data[self.driver]['astapDeviceList'] = nameList
        self.data[self.driver]['astapIndexPath'] = self.ui.astapIndexPath.text()
        self.data[self.driver]['astapAppPath'] = self.ui.astapAppPath.text()
        self.data[self.driver]['astapSearchRadius'] = self.ui.astapSearchRadius.value()
        self.data[self.driver]['astapTimeout'] = self.ui.astapTimeout.value()

        # collecting ascom data
        self.data[self.driver]['ascomName'] = self.ui.ascomDevice.text()

        # setting framework
        index = self.ui.tab.currentIndex()
        currentFramework = self.ui.tab.tabText(index).lower()
        self.data[self.driver]['framework'] = currentFramework

        # storing ok as closing
        self.returnValues['close'] = 'ok'

        # finally closing window
        self.close()

        return True

    def copyAllIndiSettings(self):
        """
        copyAllIndiSettings transfers all data from host, port, messages to all other
        driver settings

        :return: true for test purpose
        """
        for driver in self.data:
            self.data[driver]['indiHost'] = self.ui.indiHost.text()
            self.data[driver]['indiPort'] = self.ui.indiPort.text()
            self.data[driver]['indiMessages'] = self.ui.indiLoadConfig.isChecked()
            self.data[driver]['indiLoadConfig'] = self.ui.indiLoadConfig.isChecked()

        # memorizing that copy was done:
        self.returnValues['copyIndi'] = True

        return True

    def copyAllAlpacaSettings(self):
        """
        copyAllAlpacaSettings transfers all data from protocol, host, port, user, password to
        all other driver settings

        :return: true for test purpose
        """
        for driver in self.data:
            self.data[driver]['alpacaProtocol'] = self.ui.alpacaProtocol.currentIndex()
            self.data[driver]['alpacaHost'] = self.ui.alpacaHost.text()
            self.data[driver]['alpacaPort'] = self.ui.alpacaPort.text()
            self.data[driver]['alpacaNumber'] = self.ui.alpacaNumber.value()
            self.data[driver]['alpacaUser'] = self.ui.alpacaUser.text()
            self.data[driver]['alpacaPassword'] = self.ui.alpacaPassword.text()

        # memorizing that copy was done:
        self.returnValues['copyAlpaca'] = True

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
