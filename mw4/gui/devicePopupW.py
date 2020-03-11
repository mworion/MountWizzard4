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
import logging
# external packages
import PyQt5.QtCore
# local import
from mw4.base.loggerMW import CustomLogger
from mw4.gui import widget
from mw4.gui.widgets.devicePopup_ui import Ui_DevicePopup
from mw4.base.indiClass import IndiClass


class DevicePopup(PyQt5.QtWidgets.QDialog, widget.MWidget):
    """
    the DevicePopup window class handles

    """

    __all__ = ['DevicePopup',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    # INDI device types
    indiTypes = {
        'telescope': (1 << 0),
        'camera': (1 << 1),
        'guider': (1 << 2),
        'focuser': (1 << 3),
        'filter': (1 << 4),
        'dome': (1 << 5),
        'weather': (1 << 7),
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
                 geometry=None,
                 driver='',
                 deviceType='',
                 framework={},
                 data=None):

        super().__init__()
        self.ui = Ui_DevicePopup()
        self.ui.setupUi(self)
        self.initUI()
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
        self.data = data
        self.driver = driver
        self.deviceType = deviceType
        self.framework = framework
        self.indiClass = None
        self.indiSearchNameList = ()
        self.indiSearchType = None
        self.returnValues = {'close': 'cancel'}

        # setting to center of parent image
        x = geometry[0] + (geometry[2] - self.width()) / 2
        y = geometry[1] + (geometry[3] - self.height()) / 2
        self.move(x, y)

        self.ui.cancel.clicked.connect(self.close)
        self.ui.ok.clicked.connect(self.storeConfig)
        self.ui.indiSearch.clicked.connect(self.searchDevices)
        self.ui.copyAlpaca.clicked.connect(self.copyAllAlpacaSettings)
        self.ui.copyIndi.clicked.connect(self.copyAllIndiSettings)
        self.initConfig()

    def initConfig(self):
        """

        :return: True for test purpose
        """

        # populate data
        deviceData = self.data.get(self.driver, {})
        selectedFramework = deviceData.get('framework', 'indi')
        self.indiSearchType = self.indiTypes.get(self.deviceType, 0xff)
        self.setWindowTitle(f'Setup for: {self.driver}')

        # populating indi data
        self.ui.indiHost.setText(deviceData.get('indiHost', 'localhost'))
        self.ui.indiPort.setText(deviceData.get('indiPort', '7624'))
        self.ui.indiNameList.clear()
        self.ui.indiNameList.setView(PyQt5.QtWidgets.QListView())
        indiName = deviceData.get('indiName', '')
        nameList = deviceData.get('indiNameList', [])
        if not nameList:
            self.ui.indiNameList.addItem('-')
        for i, name in enumerate(nameList):
            self.ui.indiNameList.addItem(name)
            if indiName == name:
                self.ui.indiNameList.setCurrentIndex(i)
        self.ui.indiMessages.setChecked(deviceData.get('indiMessages', False))
        self.ui.indiLoadConfig.setChecked(deviceData.get('indiLoadConfig', False))

        # populating alpaca data
        self.ui.alpacaProtocol.setCurrentIndex(deviceData.get('alpacaProtocol', 0))
        self.ui.alpacaHost.setText(deviceData.get('alpacaHost', 'localhost'))
        self.ui.alpacaPort.setText(deviceData.get('alpacaPort', '11111'))
        number = int(deviceData.get('alpacaName', '"":0').split(':')[1])
        self.ui.alpacaNumber.setValue(number)
        self.ui.alpacaUser.setText(deviceData.get('alpacaUser', 'user'))
        self.ui.alpacaPassword.setText(deviceData.get('alpacaPassword', 'password'))

        # for fw in self.framework:
        tabWidget = self.ui.tab.findChild(PyQt5.QtWidgets.QWidget, selectedFramework)
        tabIndex = self.ui.tab.indexOf(tabWidget)
        self.ui.tab.setCurrentIndex(tabIndex)

        for index in range(0, self.ui.tab.count()):
            if self.ui.tab.tabText(index).lower() in self.framework:
                continue
            self.ui.tab.setTabEnabled(index, False)
        self.show()

        return True

    def storeConfig(self):
        """

        :return: true for test purpose
        """
        # collecting indi data
        self.data[self.driver]['indiHost'] = self.ui.indiHost.text()
        self.data[self.driver]['indiPort'] = self.ui.indiPort.text()
        self.data[self.driver]['indiName'] = self.ui.indiNameList.currentText()

        model = self.ui.indiNameList.model()
        nameList = []
        for index in range(model.rowCount()):
            nameList.append(model.item(index).text())
        self.data[self.driver]['indiNameList'] = nameList
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

        # storing ok as closing
        self.returnValues['close'] = 'ok'

        # finally closing window
        self.close()

        return True

    def closeEvent(self, event):
        """
        closeEvent collects all data necessary for the following process

        :param event:
        :return:
        """
        # getting last setting:
        self.returnValues['framework'] = self.ui.tab.tabText(self.ui.tab.currentIndex()).lower()
        super().closeEvent(event)

        return

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

        device = self.indiClass.client.devices.get(deviceName)
        if not device:
            return False

        interface = device.getText(propertyName).get('DRIVER_INTERFACE', None)

        if interface is None:
            return False

        if self.indiSearchType is None:
            return False

        interface = int(interface)

        if interface & self.indiSearchType:
            self.indiSearchNameList.append(deviceName)

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

        self.indiSearchNameList = list()

        if self.driver in self.indiDefaults:
            self.indiSearchNameList.append(self.indiDefaults[self.driver])

        else:
            host = (self.ui.indiHost.text(), int(self.ui.indiPort.text()))
            self.indiClass = IndiClass()
            self.indiClass.host = host

            self.indiClass.client.signals.defText.connect(self.addDevicesWithType)
            self.indiClass.client.connectServer()
            self.indiClass.client.watchDevice()
            msg = PyQt5.QtWidgets.QMessageBox
            msg.information(self,
                            'Searching Devices',
                            f'Search for [{self.driver}] could take some seconds!')
            self.indiClass.client.disconnectServer()

        self.ui.indiNameList.clear()
        self.ui.indiNameList.setView(PyQt5.QtWidgets.QListView())

        for name in self.indiSearchNameList:
            self.log.info(f'Indi search found: {name}')

        for deviceName in self.indiSearchNameList:
            self.ui.indiNameList.addItem(deviceName)

        return True
