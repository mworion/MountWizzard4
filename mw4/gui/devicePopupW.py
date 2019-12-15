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
from mw4.gui import widget
from mw4.gui.widgets.devicePopup_ui import Ui_DevicePopup
from mw4.base.indiClass import IndiClass


class DevicePopup(widget.MWidget):
    """
    the message window class handles

    """

    __all__ = ['DevicePopup',
               ]

    logger = logging.getLogger(__name__)

    # INDI device types
    indiTypes = {
        'telescope': (1 << 0),
        'camera': (1 << 1),
        'guider': (1 << 2),
        'focuser': (1 << 3),
        'filter': (1 << 4),
        'dome': (1 << 5),
        'weather': (1 << 7),
        'cover': (1 << 9),
    }

    def __init__(self, geo=None, device='', data=None):
        super().__init__()
        self.ui = Ui_DevicePopup()
        self.ui.setupUi(self)
        self.initUI()
        self.setWindowModality(PyQt5.QtCore.Qt.ApplicationModal)
        self.data = data
        self.device = device
        self.indiClass = None
        self.indiSearchNameList = ()
        self.indiSearchType = None

        # setting to center of parent image
        x = geo[0] + (geo[2] - self.width()) / 2
        y = geo[1] + (geo[3] - self.height()) / 2
        self.move(x, y)

        self.ui.cancel.clicked.connect(self.close)
        self.ui.ok.clicked.connect(self.saveData)
        self.ui.indiSearch.clicked.connect(self.searchDevices)
        self.showWindow()

    def showWindow(self):
        """

        """

        # populate data
        deviceData = self.data.get(self.device, {})
        framework = deviceData.get('framework', 'indi')
        self.setWindowTitle(f'Setup for: {self.device}')

        # populating indi data
        self.ui.indiHost.setText(deviceData.get('indiHost', 'localhost'))
        self.ui.indiPort.setText(deviceData.get('indiPort', '7624'))

        self.ui.indiNameList.clear()
        self.ui.indiNameList.setView(PyQt5.QtWidgets.QListView())
        indiName = deviceData.get('indiName', 'test2')
        nameList = deviceData.get('indiNameList', ['test1', 'test2'])
        self.ui.indiNameList.addItem('-')
        for i, name in enumerate(nameList):
            self.ui.indiNameList.addItem(name)
            if indiName == name:
                self.ui.indiNameList.setCurrentIndex(i + 1)

        self.ui.indiMessages.setChecked(deviceData.get('indiMessages', False))
        self.ui.indiLoadConfig.setChecked(deviceData.get('indiLoadConfig', False))

        # populating alpaca data
        self.ui.alpacaProtocol.setCurrentIndex(deviceData.get('alpacaProtocol', 0))
        self.ui.alpacaHost.setText(deviceData.get('alpacaHost', 'localhost'))
        self.ui.alpacaPort.setText(deviceData.get('alpacaPort', '11111'))
        self.ui.alpacaNumber.setValue(deviceData.get('alpacaNumber', 0))
        self.ui.alpacaUser.setText(deviceData.get('alpacaUser', 'user'))
        self.ui.alpacaPassword.setText(deviceData.get('alpacaPassword', 'password'))

        # selecting the right tab
        if framework == 'indi':
            self.ui.tab.setCurrentIndex(0)
        elif framework == 'alpaca':
            self.ui.tab.setCurrentIndex(1)

        # finally showing the window
        self.show()

    def saveData(self):
        """

        """
        # collecting indi data
        self.data[self.device]['indiHost'] = self.ui.indiHost.text()
        self.data[self.device]['indiPort'] = self.ui.indiPort.text()
        self.data[self.device]['indiName'] = self.ui.indiNameList.currentText()

        model = self.ui.indiNameList.model()
        nameList = []
        for index in range(model.rowCount()):
            if model.item(index).text() == '-':
                continue
            nameList.append(model.item(index).text())
        self.data[self.device]['indiNameList'] = nameList

        self.data[self.device]['indiMessages'] = self.ui.indiMessages.isChecked()
        self.data[self.device]['indiLoadConfig'] = self.ui.indiLoadConfig.isChecked()

        # collecting alpaca data

        # finally closing window
        self.close()

    def copyAllIndiSettings(self):
        """

        """
        return True

    def copyAllAlpacaSettings(self):
        """

        """
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

        device = self.indiClass.client.devices[deviceName]
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

        :return:  true for test purpose
        """

        self.indiSearchNameList = list()
        host = (self.ui.indiHost.text(), int(self.ui.indiPort.text()))
        self.indiSearchType = self.indiTypes[self.device]
        self.indiClass = IndiClass()
        self.indiClass.host = host

        self.indiClass.client.signals.defText.connect(self.addDevicesWithType)
        self.indiClass.client.connectServer()
        self.indiClass.client.watchDevice()
        msg = PyQt5.QtWidgets.QMessageBox
        msg.information(self,
                        'Searching Devices',
                        f'Search for {self.device} could take some seconds!')
        self.indiClass.client.disconnectServer()

        self.ui.indiNameList.clear()
        self.ui.indiNameList.setView(PyQt5.QtWidgets.QListView())
        self.ui.indiNameList.addItem('-')
        for deviceName in self.indiSearchNameList:
            self.ui.indiNameList.addItem(deviceName)

        return True


