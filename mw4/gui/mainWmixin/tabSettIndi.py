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


class SettIndi(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    # INDI device types
    GENERAL_INTERFACE = 0
    TELESCOPE_INTERFACE = (1 << 0)
    CCD_INTERFACE = (1 << 1)
    GUIDER_INTERFACE = (1 << 2)
    FOCUSER_INTERFACE = (1 << 3)
    FILTER_INTERFACE = (1 << 4)
    DOME_INTERFACE = (1 << 5)
    GPS_INTERFACE = (1 << 6)
    WEATHER_INTERFACE = (1 << 7)
    AO_INTERFACE = (1 << 8)
    DUSTCAP_INTERFACE = (1 << 9)
    LIGHTBOX_INTERFACE = (1 << 10)
    DETECTOR_INTERFACE = (1 << 11)
    AUX_INTERFACE = (1 << 15)

    def __init__(self):

        self.indiClass = None
        self.indiDeviceList = list()
        self.indiSearchType = None

        self.indiDevices = {
            'dome':
                {'uiName': self.ui.domeDeviceName,
                 'uiDevice': self.ui.domeDevice,
                 'uiSearch': self.ui.searchDomeDevices,
                 'searchType': self.DOME_INTERFACE,
                 'uiMessage': self.ui.domeDeviceMessage,
                 'class': self.app.dome,
                 'dispatch': self.domeDispatch,
                 'signals': self.app.dome.signals,
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
        for name, item in self.indiDevices.items():
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
            uiList = self.indiDevices[device]['uiName']
            deviceList = config.get(f'{device}Devices', [])
            for deviceItem in deviceList:
                if deviceItem == 'No device driver selected':
                    continue
                uiList.addItem(deviceItem)

        for name, item in self.indiDevices.items():
            self.indiDevices[name]['uiName'].setCurrentIndex(config.get(f'{name}Name', 0))
            self.indiDevices[name]['uiMessage'].setChecked(config.get(f'{name}Message', False))
            self.indiDevices[name]['port'].setText(config.get(f'{name}Port', '7624'))
            self.indiDevices[name]['host'].setText(config.get(f'{name}Host', ''))

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
            model = self.indiDevices[device]['uiName'].model()
            deviceList = []
            for index in range(model.rowCount()):
                if model.item(index).text() == 'No device driver selected':
                    continue
                deviceList.append(model.item(index).text())
            config[f'{device}Devices'] = deviceList

        for name, item in self.indiDevices.items():
            config[f'{name}Name'] = self.indiDevices[name]['uiName'].currentIndex()
            config[f'{name}Message'] = self.indiDevices[name]['uiMessage'].isChecked()
            config[f'{name}Port'] = self.indiDevices[name]['port'].text()
            config[f'{name}Host'] = self.indiDevices[name]['host'].text()

        config['shareIndiServer'] = self.ui.shareIndiServer.isChecked()

        return True

    def setupDeviceNameGui(self):
        """
        setupRelayGui handles the dropdown lists for all devices possible in mountwizzard.
        therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        dropDowns = list(self.indiDevices[device]['uiName'] for device in self.indiDevices)
        for dropDown in dropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device driver selected')

        self.indiDevices['skymeter']['uiName'].addItem('SQM')
        self.indiDevices['telescope']['uiName'].addItem('LX200 10micron')
        self.indiDevices['power']['uiName'].addItem('Pegasus UPB')
        self.indiDevices['cover']['uiName'].addItem('Flip Flat')

        return True

    def shareServer(self):
        """
        shareServer is called whenever a indi server host is edited. if checkbox
        for sharing is set, the new entry will be copied to all other indi servers

        :return:
        """

        ports = list(self.indiDevices[device]['port'] for device in self.indiDevices)
        hosts = list(self.indiDevices[device]['host'] for device in self.indiDevices)
        baseClasses = list(self.indiDevices[device]['class'] for device in self.indiDevices)

        for baseClass, host, port in zip(baseClasses, hosts, ports):

            if self.ui.shareIndiServer.isChecked():
                if self.sender() != host and self.sender() in hosts:
                    host.setText(self.sender().text())
                if self.sender() != port and self.sender() in ports:
                    port.setText(self.sender().text())

            if baseClass == self.app.dome:
                baseClass.host = (host.text(), int(port.text()))
            else:
                baseClass.client.host = (host.text(), int(port.text()))

        return True

    def shareMessage(self):
        """
        shareMessage is called whenever a indi message checkbox is edited. if checkbox
        for sharing is set, the new entry will be copied to all other indi servers

        :return: true for test purpose
        """

        messages = list(self.indiDevices[device]['uiMessage'] for device in self.indiDevices)
        baseClasses = list(self.indiDevices[device]['class'] for device in self.indiDevices)

        for baseClass, message in zip(baseClasses, messages):

            if self.ui.shareIndiServer.isChecked():
                if self.sender() != message and self.sender() in messages:
                    message.setChecked(self.sender().isChecked())

            baseClass.showMessages = message.isChecked()

        return True

    def showIndiDisconnected(self, deviceList):
        """
        showIndiDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        if not deviceList:
            return False

        deviceName = list(deviceList.keys())[0]

        for device in self.indiDevices:
            if self.indiDevices[device]['class'].name != deviceName:
                continue
            self.indiDevices[device]['uiDevice'].setStyleSheet(self.BACK_NORM)
        return True

    def showDeviceConnected(self, deviceName):
        """
        showCoverDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        for device in self.indiDevices:
            if self.indiDevices[device]['class'].name != deviceName:
                continue
            self.indiDevices[device]['uiDevice'].setStyleSheet(self.BACK_GREEN)
            self.deviceStat[device] = True
        return True

    def showDeviceDisconnected(self, deviceName):
        """
        showCoverDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        for device in self.indiDevices:
            if self.indiDevices[device]['class'].name != deviceName:
                continue
            self.indiDevices[device]['uiDevice'].setStyleSheet(self.BACK_NORM)
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

        self.indiDeviceList = list()

        for device in self.indiDevices:
            # simplify
            devObj = self.indiDevices[device]

            if devObj['uiSearch'] != self.sender():
                continue
            if not devObj['class'].client.connected:
                continue

            host = (devObj['host'].text(),
                    int(devObj['port'].text()),
                    )
            self.indiClass = IndiClass(host=host)
            self.indiSearchType = devObj['searchType']
            self.indiClass.client.signals.defText.connect(self.addDevicesWithType)
            self.indiClass.client.connectServer()
            self.indiClass.client.watchDevice()
            msg = PyQt5.QtWidgets.QMessageBox
            msg.information(self,
                            'Searching Devices',
                            f'Search for {device} could take some seconds!')
            self.indiClass.client.disconnectServer()
            self.indiClass = None
            self.indiSearchType = None

            devObj['uiName'].clear()
            devObj['uiName'].setView(PyQt5.QtWidgets.QListView())
            devObj['uiName'].addItem('No device driver selected')
            for deviceName in self.indiDeviceList:
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

        device = self.indiClass.client.devices[deviceName]
        interface = device.getText(propertyName).get('DRIVER_INTERFACE', None)

        if interface is None:
            return False

        if self.indiSearchType is None:
            return False

        interface = int(interface)
        if interface & self.indiSearchType:
            self.indiDeviceList.append(deviceName)

        return True
