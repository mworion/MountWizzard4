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
# Python  v3.7.4
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


class SettIndi(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):

        self.indiDevices = {
            'dome':
                {'uiName': self.ui.domeDeviceName,
                 'uiDevice': self.ui.domeDevice,
                 'uiMessage': self.ui.domeDeviceMessage,
                 'class': self.app.dome,
                 'dispatch': self.domeDispatch,
                 'signals': self.app.dome.client.signals,
                 'port': self.ui.domePort,
                 'host': self.ui.domeHost,
                 },
            'imaging':
                {'uiName': self.ui.imagingDeviceName,
                 'uiDevice': self.ui.imagingDevice,
                 'uiMessage': self.ui.imagingDeviceMessage,
                 'class': self.app.imaging,
                 'dispatch': self.imagingDispatch,
                 'signals': self.app.imaging.client.signals,
                 'port': self.ui.imagingPort,
                 'host': self.ui.imagingHost,
                 },
            'sensorWeather':
                {'uiName': self.ui.sensorWeatherDeviceName,
                 'uiDevice': self.ui.sensorWeatherDevice,
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

        # adding special items
        self.indiDevices['imaging']['uiName'].addItem('Apogee CCD')
        self.indiDevices['imaging']['uiName'].addItem('Atik GP')
        self.indiDevices['imaging']['uiName'].addItem('CCD Simulator')
        self.indiDevices['imaging']['uiName'].addItem('Canon DSLR')
        self.indiDevices['imaging']['uiName'].addItem('FLI CCD')
        self.indiDevices['imaging']['uiName'].addItem('FireFly MV')
        self.indiDevices['imaging']['uiName'].addItem('GPhoto CCD')
        self.indiDevices['imaging']['uiName'].addItem('Guide Simulator')
        self.indiDevices['imaging']['uiName'].addItem('Meade Deep Sky Imager')
        self.indiDevices['imaging']['uiName'].addItem('Nikon DSLR')
        self.indiDevices['imaging']['uiName'].addItem('QHY CCD')
        self.indiDevices['imaging']['uiName'].addItem('QSI CCD')
        self.indiDevices['imaging']['uiName'].addItem('SBIG CCD')
        self.indiDevices['imaging']['uiName'].addItem('SBIG ST-I')
        self.indiDevices['imaging']['uiName'].addItem('SX CCD')
        self.indiDevices['imaging']['uiName'].addItem('Sony DSLR')
        self.indiDevices['imaging']['uiName'].addItem('Starfish CCD')
        self.indiDevices['imaging']['uiName'].addItem('V4L2 CCD')
        self.indiDevices['imaging']['uiName'].addItem('ZWO CCD ASI120MC')
        self.indiDevices['imaging']['uiName'].addItem('ZWO CCD ASI1600MC')
        self.indiDevices['imaging']['uiName'].addItem('ZWO CCD ASI290MM Mini')
        self.indiDevices['imaging']['uiName'].addItem('ZWO CCD ASI1600MM Pro')
        self.indiDevices['imaging']['uiName'].addItem('ZWO CCD ASI1600MM-Cool')

        self.indiDevices['dome']['uiName'].addItem('Baader Dome')
        self.indiDevices['dome']['uiName'].addItem('Dome Scripting Gateway')
        self.indiDevices['dome']['uiName'].addItem('Dome Simulator')
        self.indiDevices['dome']['uiName'].addItem('MaxDome II')
        self.indiDevices['dome']['uiName'].addItem('NexDome')
        self.indiDevices['dome']['uiName'].addItem('RollOff Simulator')
        self.indiDevices['dome']['uiName'].addItem('ScopeDome Dome')

        self.indiDevices['sensorWeather']['uiName'].addItem('AAG Cloud Watcher')
        self.indiDevices['sensorWeather']['uiName'].addItem('Arduino MeteoStation')
        self.indiDevices['sensorWeather']['uiName'].addItem('MBox')
        self.indiDevices['sensorWeather']['uiName'].addItem('OpenWeatherMap')
        self.indiDevices['sensorWeather']['uiName'].addItem('Vantage')
        self.indiDevices['sensorWeather']['uiName'].addItem('Weather Meta')
        self.indiDevices['sensorWeather']['uiName'].addItem('Weather Simulator')
        self.indiDevices['sensorWeather']['uiName'].addItem('Weather Watcher')

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
                if self.sender() == host:
                    continue
                elif self.sender() == port:
                    continue
                elif self.sender() in ports:
                    port.setText(self.sender().text())
                elif self.sender() in hosts:
                    host.setText(self.sender().text())

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
                if self.sender() == message:
                    continue
                elif self.sender() not in messages:
                    continue
                else:
                    message.setChecked(self.sender().isChecked())

            baseClass.showMessage = message.isChecked()

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
