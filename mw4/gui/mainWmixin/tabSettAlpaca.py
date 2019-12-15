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
# external packages
import PyQt5
# local import
from mw4.base.indiClass import IndiClass


class SettAlpaca(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):

        self.alpacaClass = None
        self.alpacaDeviceList = list()
        self.alpacaSearchType = None

        self.alpacaDevices = {
            'dome':
                {'uiName': self.ui.domeDeviceName,
                 'uiDevice': self.ui.domeDevice,
                 'uiSearch': self.ui.searchDomeDevices,
                 'searchType': self.DOME_INTERFACE,
                 'uiMessage': self.ui.domeDeviceMessage,
                 'class': self.app.dome,
                 'dispatch': self.domeDispatch,
                 'signals': self.app.dome.client.signals,
                 'port': self.ui.domePort,
                 'host': self.ui.domeHost,
                 },
            'camera':
                {'uiName': self.ui.cameraDeviceName,
                 'uiDevice': self.ui.cameraDevice,
                 'uiSearch': self.ui.searchCameraDevices,
                 'searchType': self.CCD_INTERFACE,
                 'uiMessage': self.ui.cameraDeviceMessage,
                 'class': self.app.camera,
                 'dispatch': self.cameraDispatch,
                 'signals': self.app.camera.client.signals,
                 'port': self.ui.cameraPort,
                 'host': self.ui.cameraHost,
                 },
            'filterwheel':
                {'uiName': self.ui.filterwheelDeviceName,
                 'uiDevice': self.ui.filterwheelDevice,
                 'uiSearch': self.ui.searchFilterwheelDevices,
                 'searchType': self.FILTER_INTERFACE,
                 'uiMessage': self.ui.filterwheelDeviceMessage,
                 'class': self.app.filterwheel,
                 'dispatch': self.filterwheelDispatch,
                 'signals': self.app.filterwheel.client.signals,
                 'port': self.ui.filterwheelPort,
                 'host': self.ui.filterwheelHost,
                 },
            'focuser':
                {'uiName': self.ui.focuserDeviceName,
                 'uiDevice': self.ui.focuserDevice,
                 'uiSearch': self.ui.searchFocuserDevices,
                 'searchType': self.FOCUSER_INTERFACE,
                 'uiMessage': self.ui.focuserDeviceMessage,
                 'class': self.app.focuser,
                 'dispatch': self.focuserDispatch,
                 'signals': self.app.focuser.client.signals,
                 'port': self.ui.focuserPort,
                 'host': self.ui.focuserHost,
                 },
            'sensorWeather':
                {'uiName': self.ui.sensorWeatherDeviceName,
                 'uiDevice': self.ui.sensorWeatherDevice,
                 'uiSearch': self.ui.searchSensorWeatherDevices,
                 'searchType': self.WEATHER_INTERFACE,
                 'uiMessage': self.ui.sensorWeatherDeviceMessage,
                 'class': self.app.sensorWeather,
                 'dispatch': self.sensorWeatherDispatch,
                 'signals': self.app.sensorWeather.client.signals,
                 'port': self.ui.sensorWeatherPort,
                 'host': self.ui.sensorWeatherHost,
                 },
            'cover':
                {'uiName': self.ui.coverDeviceName,
                 'uiDevice': self.ui.coverDevice,
                 'uiSearch': None,
                 'searchType': None,
                 'uiMessage': self.ui.coverDeviceMessage,
                 'class': self.app.cover,
                 'dispatch': self.coverDispatch,
                 'signals': self.app.cover.client.signals,
                 'port': self.ui.coverPort,
                 'host': self.ui.coverHost,
                 },
            'skymeter':
                {'uiName': self.ui.skymeterDeviceName,
                 'uiDevice': self.ui.skymeterDevice,
                 'uiSearch': None,
                 'searchType': None,
                 'uiMessage': self.ui.skymeterDeviceMessage,
                 'class': self.app.skymeter,
                 'dispatch': self.skymeterDispatch,
                 'signals': self.app.skymeter.client.signals,
                 'port': self.ui.skymeterPort,
                 'host': self.ui.skymeterHost,
                 },
            'telescope':
                {'uiName': self.ui.telescopeDeviceName,
                 'uiDevice': self.ui.telescopeDevice,
                 'uiSearch': None,
                 'searchType': None,
                 'uiMessage': self.ui.telescopeDeviceMessage,
                 'class': self.app.telescope,
                 'dispatch': self.telescopeDispatch,
                 'signals': self.app.telescope.client.signals,
                 'port': self.ui.telescopePort,
                 'host': self.ui.telescopeHost,
                 },
            'power':
                {'uiName': self.ui.powerDeviceName,
                 'uiDevice': self.ui.powerDevice,
                 'uiSearch': None,
                 'searchType': None,
                 'uiMessage': self.ui.powerDeviceMessage,
                 'class': self.app.power,
                 'dispatch': self.powerDispatch,
                 'signals': self.app.power.client.signals,
                 'port': self.ui.powerPort,
                 'host': self.ui.powerHost,
                 },
        }

        # signals from functions
        for name, item in self.alpacaDevices.items():
            item['uiName'].currentIndexChanged.connect(item['dispatch'])
            item['host'].editingFinished.connect(self.shareServer)
            item['port'].editingFinished.connect(self.shareServer)
            if item['uiSearch'] is not None:
                item['uiSearch'].clicked.connect(self.searchDevices)
            item['uiMessage'].clicked.connect(self.shareMessage)
            item['signals'].serverDisconnected.connect(self.showIndiDisconnected)
            item['signals'].deviceConnected.connect(self.showDeviceConnected)
            item['signals'].deviceDisconnected.connect(self.showDeviceDisconnected)

        self.setupDeviceNameGui()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']

        for device in ['camera', 'filterwheel', 'focuser', 'dome', 'sensorWeather']:
            uiList = self.alpacaDevices[device]['uiName']
            deviceList = config.get(f'{device}Devices', [])
            for deviceItem in deviceList:
                if deviceItem == 'No device driver selected':
                    continue
                uiList.addItem(deviceItem)

        for name, item in self.alpacaDevices.items():
            self.alpacaDevices[name]['uiName'].setCurrentIndex(config.get(f'{name}Name', 0))
            self.alpacaDevices[name]['uiMessage'].setChecked(config.get(f'{name}Message', False))
            self.alpacaDevices[name]['port'].setText(config.get(f'{name}Port', '7624'))
            self.alpacaDevices[name]['host'].setText(config.get(f'{name}Host', ''))

        self.ui.shareIndiServer.setChecked(config.get('shareIndiServer', True))
        self.shareServer()
        self.shareMessage()

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']

        for device in ['camera', 'filterwheel', 'focuser', 'dome', 'sensorWeather']:
            model = self.alpacaDevices[device]['uiName'].model()
            deviceList = []
            for index in range(model.rowCount()):
                if model.item(index).text() == 'No device driver selected':
                    continue
                deviceList.append(model.item(index).text())
            config[f'{device}Devices'] = deviceList

        for name, item in self.alpacaDevices.items():
            config[f'{name}Name'] = self.alpacaDevices[name]['uiName'].currentIndex()
            config[f'{name}Message'] = self.alpacaDevices[name]['uiMessage'].isChecked()
            config[f'{name}Port'] = self.alpacaDevices[name]['port'].text()
            config[f'{name}Host'] = self.alpacaDevices[name]['host'].text()

        config['shareIndiServer'] = self.ui.shareIndiServer.isChecked()

        return True

    def setupDeviceNameGui(self):
        """
        setupRelayGui handles the dropdown lists for all devices possible in mountwizzard.
        therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        dropDowns = list(self.alpacaDevices[device]['uiName'] for device in self.alpacaDevices)
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device driver selected')

        self.alpacaDevices['skymeter']['uiName'].addItem('SQM')
        self.alpacaDevices['telescope']['uiName'].addItem('LX200 10micron')
        self.alpacaDevices['power']['uiName'].addItem('Pegasus UPB')
        self.alpacaDevices['cover']['uiName'].addItem('Flip Flat')

        return True

    def shareServer(self):
        """
        shareServer is called whenever a indi server host is edited. if checkbox
        for sharing is set, the new entry will be copied to all other indi servers

        :return:
        """

        ports = list(self.alpacaDevices[device]['port'] for device in self.alpacaDevices)
        hosts = list(self.alpacaDevices[device]['host'] for device in self.alpacaDevices)
        baseClasses = list(self.alpacaDevices[device]['class'] for device in self.alpacaDevices)

        for baseClass, host, port in zip(baseClasses, hosts, ports):

            if self.ui.shareIndiServer.isChecked():
                if self.sender() != host and self.sender() in hosts:
                    host.setText(self.sender().text())
                if self.sender() != port and self.sender() in ports:
                    port.setText(self.sender().text())

            baseClass.client.host = (host.text(), int(port.text()))

        return True

    def shareMessage(self):
        """
        shareMessage is called whenever a indi message checkbox is edited. if checkbox
        for sharing is set, the new entry will be copied to all other indi servers

        :return: true for test purpose
        """

        messages = list(self.alpacaDevices[device]['uiMessage'] for device in self.alpacaDevices)
        baseClasses = list(self.alpacaDevices[device]['class'] for device in self.alpacaDevices)

        for baseClass, message in zip(baseClasses, messages):

            if self.ui.shareIndiServer.isChecked():
                if self.sender() != message and self.sender() in messages:
                    message.setChecked(self.sender().isChecked())

            baseClass.showMessages = message.isChecked()

        return True

    def showIndiDisconnected(self, deviceList):
        """
        deviceDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        if not deviceList:
            return False

        deviceName = list(deviceList.keys())[0]

        for device in self.alpacaDevices:
            if self.alpacaDevices[device]['class'].name != deviceName:
                continue
            self.alpacaDevices[device]['uiDevice'].setStyleSheet(self.BACK_NORM)
        return True

    def showDeviceConnected(self, deviceName):
        """
        showCoverDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        for device in self.alpacaDevices:
            if self.alpacaDevices[device]['class'].name != deviceName:
                continue
            self.alpacaDevices[device]['uiDevice'].setStyleSheet(self.BACK_GREEN)
            self.deviceStat[device] = True
        return True

    def showDeviceDisconnected(self, deviceName):
        """
        showCoverDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        for device in self.alpacaDevices:
            if self.alpacaDevices[device]['class'].name != deviceName:
                continue
            self.alpacaDevices[device]['uiDevice'].setStyleSheet(self.BACK_NORM)
            self.deviceStat[device] = False
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

        self.alpacaDeviceList = list()

        for device in self.alpacaDevices:
            # simplify
            devObj = self.alpacaDevices[device]

            if devObj['uiSearch'] != self.sender():
                continue
            if not devObj['class'].client.connected:
                continue

            host = (devObj['host'].text(),
                    int(devObj['port'].text()),
                    )
            self.alpacaClass = IndiClass(host=host)
            self.alpacaSearchType = devObj['searchType']
            self.alpacaClass.client.signals.defText.connect(self.addDevicesWithType)
            self.alpacaClass.client.connectServer()
            self.alpacaClass.client.watchDevice()
            msg = PyQt5.QtWidgets.QMessageBox
            msg.information(self,
                            'Searching Devices',
                            f'Search for {device} could take some seconds!')
            self.alpacaClass.client.disconnectServer()
            self.alpacaClass = None
            self.alpacaSearchType = None

            devObj['uiName'].clear()
            devObj['uiName'].setView(PyQt5.QtWidgets.QListView())
            devObj['uiName'].addItem('No device driver selected')
            for deviceName in self.alpacaDeviceList:
                devObj['uiName'].addItem(deviceName)

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

        device = self.alpacaClass.client.devices[deviceName]
        interface = device.getText(propertyName).get('DRIVER_INTERFACE', None)

        if interface is None:
            return False

        if self.alpacaSearchType is None:
            return False

        interface = int(interface)
        if interface & self.alpacaSearchType:
            self.alpacaDeviceList.append(deviceName)

        return True
