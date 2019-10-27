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
        self.deviceNames = [self.ui.imagingDeviceName,
                            self.ui.domeDeviceName,
                            self.ui.environDeviceName,
                            self.ui.skymeterDeviceName,
                            self.ui.coverDeviceName,
                            self.ui.powerDeviceName,
                            self.ui.telescopeDeviceName,
                            ]
        self.deviceNameKeys = ['imagingDeviceName',
                               'domeDeviceName',
                               'environmentDeviceName',
                               'skymeterDeviceName',
                               'coverDeviceName',
                               'powerDeviceName',
                               'telescopeDeviceName',
                               ]
        self.indiSignals = [self.app.dome.client.signals,
                            self.app.imaging.client.signals,
                            self.app.environ.client.signals,
                            self.app.cover.client.signals,
                            self.app.skymeter.client.signals,
                            self.app.telescope.client.signals,
                            self.app.power.client.signals,
                            ]

        self.indiDevices = {
            'dome':
                {'uiName': self.ui.domeDeviceName,
                 'dispatch': self.domeDispatch,
                 'signals': self.app.dome.client.signals,
                 'port': self.ui.domePort,
                 'host': self.ui.domeHost,
                 },
            'imaging':
                {'uiName': self.ui.imagingDeviceName,
                 'dispatch': self.imagingDispatch,
                 'signals': self.app.imaging.client.signals,
                 'port': self.ui.imagingPort,
                 'host': self.ui.imagingHost,
                 },
            'environ':
                {'uiName': self.ui.environDeviceName,
                 'dispatch': self.environDispatch,
                 'signals': self.app.environ.client.signals,
                 'port': self.ui.environPort,
                 'host': self.ui.environHost,
                 },
            'cover':
                {'uiName': self.ui.coverDeviceName,
                 'dispatch': self.coverDispatch,
                 'signals': self.app.cover.client.signals,
                 'port': self.ui.coverPort,
                 'host': self.ui.coverHost,
                 },
            'skymeter':
                {'uiName': self.ui.skymeterDeviceName,
                 'dispatch': self.skymeterDispatch,
                 'signals': self.app.skymeter.client.signals,
                 'port': self.ui.skymeterPort,
                 'host': self.ui.skymeterHost,
                 },
            'telescope':
                {'uiName': self.ui.telescopeDeviceName,
                 'dispatch': self.telescopeDispatch,
                 'signals': self.app.telescope.client.signals,
                 'port': self.ui.telescopePort,
                 'host': self.ui.telescopeHost,
                 },
            'power':
                {'uiName': self.ui.powerDeviceName,
                 'dispatch': self.powerDispatch,
                 'signals': self.app.power.client.signals,
                 'port': self.ui.powerPort,
                 'host': self.ui.powerHost,
                 },
            }

        self.setupDeviceNameGui()

        # all internal signal for handling
        sig = self.app.dome.client.signals
        sig.serverDisconnected.connect(self.showIndiDomeDisconnected)
        sig.deviceConnected.connect(self.showDomeDeviceConnected)
        sig.deviceDisconnected.connect(self.showDomeDeviceDisconnected)

        sig = self.app.imaging.client.signals
        sig.serverDisconnected.connect(self.showIndiImagingDisconnected)
        sig.deviceConnected.connect(self.showImagingDeviceConnected)
        sig.deviceDisconnected.connect(self.showImagingDeviceDisconnected)

        sig = self.app.environ.client.signals
        sig.serverDisconnected.connect(self.showIndiEnvironDisconnected)
        sig.deviceConnected.connect(self.showEnvironDeviceConnected)
        sig.deviceDisconnected.connect(self.showEnvironDeviceDisconnected)

        sig = self.app.cover.client.signals
        sig.serverDisconnected.connect(self.showIndiCoverDisconnected)
        sig.deviceConnected.connect(self.showCoverDeviceConnected)
        sig.deviceDisconnected.connect(self.showCoverDeviceDisconnected)

        sig = self.app.skymeter.client.signals
        sig.serverDisconnected.connect(self.showIndiSkymeterDisconnected)
        sig.deviceConnected.connect(self.showSkymeterDeviceConnected)
        sig.deviceDisconnected.connect(self.showSkymeterDeviceDisconnected)

        sig = self.app.telescope.client.signals
        sig.serverDisconnected.connect(self.showIndiTelescopeDisconnected)
        sig.deviceConnected.connect(self.showTelescopeDeviceConnected)
        sig.deviceDisconnected.connect(self.showTelescopeDeviceDisconnected)

        sig = self.app.power.client.signals
        sig.serverDisconnected.connect(self.showIndiPowerDisconnected)
        sig.deviceConnected.connect(self.showPowerDeviceConnected)
        sig.deviceDisconnected.connect(self.showPowerDeviceDisconnected)

        # signals from gui

        for name, item in self.indiDevices.items():
            item['uiName'].currentIndexChanged.connect(item['dispatch'])
            item['host'].editingFinished.connect(self.shareServerHost)
            item['port'].editingFinished.connect(self.shareServerPort)
            #item['signals'].serverDisconnected.connect(self.showIndiDisconnected)
            #item['signals'].deviceConnected.connect(self.showDeviceConnected)
            #item['signals'].deviceDisconnected.connect(self.showDeviceDisconnected)

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
            self.indiDevices[name]['port'].setText(config.get(f'{name}Port', '7624'))
            self.indiDevices[name]['host'].setText(config.get(f'{name}Host', ''))

        self.ui.checkMessageINDI.setChecked(config.get('checkMessageINDI', False))
        self.ui.shareIndiServer.setChecked(config.get('shareIndiServer', True))

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
            config[f'{name}Port'] = self.indiDevices[name]['port'].text()
            config[f'{name}Host'] = self.indiDevices[name]['host'].text()

        config['checkMessageINDI'] = self.ui.checkMessageINDI.isChecked()
        config['shareIndiServer'] = self.ui.shareIndiServer.isChecked()

        return True

    def setupDeviceNameGui(self):
        """
        setupRelayGui handles the dropdown lists for all devices possible in mountwizzard.
        therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        for dropDown in self.deviceNames:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device driver selected')
        # adding special items
        self.indiDevices['imaging']['uiName'].addItem('Altair')
        self.indiDevices['imaging']['uiName'].addItem('Apogee CCD')
        self.indiDevices['imaging']['uiName'].addItem('Atik CCD')
        self.indiDevices['imaging']['uiName'].addItem('CCD Simulator')
        self.indiDevices['imaging']['uiName'].addItem('Canon DSLR')
        self.indiDevices['imaging']['uiName'].addItem('DMK CCD')
        self.indiDevices['imaging']['uiName'].addItem('FLI CCD')
        self.indiDevices['imaging']['uiName'].addItem('FireFly MV')
        self.indiDevices['imaging']['uiName'].addItem('GPhoto CCD')
        self.indiDevices['imaging']['uiName'].addItem('Guide Simulator')
        self.indiDevices['imaging']['uiName'].addItem('MI CCD (ETH)')
        self.indiDevices['imaging']['uiName'].addItem('MI CCD (USB)')
        self.indiDevices['imaging']['uiName'].addItem('Meade Deep Sky Imager')
        self.indiDevices['imaging']['uiName'].addItem('Nightscape 8300 CCD')
        self.indiDevices['imaging']['uiName'].addItem('Nikon DSLR')
        self.indiDevices['imaging']['uiName'].addItem('Pentax DSLR')
        self.indiDevices['imaging']['uiName'].addItem('QHY CCD')
        self.indiDevices['imaging']['uiName'].addItem('QSI CCD')
        self.indiDevices['imaging']['uiName'].addItem('SBIG CCD')
        self.indiDevices['imaging']['uiName'].addItem('SBIG ST-I')
        self.indiDevices['imaging']['uiName'].addItem('SX CCD')
        self.indiDevices['imaging']['uiName'].addItem('Sony DSLR')
        self.indiDevices['imaging']['uiName'].addItem('Starfish CCD')
        self.indiDevices['imaging']['uiName'].addItem('ToupCam')
        self.indiDevices['imaging']['uiName'].addItem('V4L2 CCD')
        self.indiDevices['imaging']['uiName'].addItem('ZWO CCD')

        self.indiDevices['dome']['uiName'].addItem('Baader Dome')
        self.indiDevices['dome']['uiName'].addItem('Dome Scripting Gateway')
        self.indiDevices['dome']['uiName'].addItem('Dome Simulator')
        self.indiDevices['dome']['uiName'].addItem('MaxDome II')
        self.indiDevices['dome']['uiName'].addItem('NexDome')
        self.indiDevices['dome']['uiName'].addItem('RollOff Simulator')
        self.indiDevices['dome']['uiName'].addItem('ScopeDome Dome')

        self.indiDevices['environ']['uiName'].addItem('AAG Cloud Watcher')
        self.indiDevices['environ']['uiName'].addItem('Arduino MeteoStation')
        self.indiDevices['environ']['uiName'].addItem('MBox')
        self.indiDevices['environ']['uiName'].addItem('OpenWeatherMap')
        self.indiDevices['environ']['uiName'].addItem('Vantage')
        self.indiDevices['environ']['uiName'].addItem('Weather Meta')
        self.indiDevices['environ']['uiName'].addItem('Weather Simulator')
        self.indiDevices['environ']['uiName'].addItem('Weather Watcher')
        self.indiDevices['environ']['uiName'].addItem('WonderGround')

        self.indiDevices['skymeter']['uiName'].addItem('SQM')
        self.indiDevices['telescope']['uiName'].addItem('LX200 10micron')
        self.indiDevices['power']['uiName'].addItem('Pegasus UPB')
        self.indiDevices['cover']['uiName'].addItem('Flip Flat')

        return True

    def shareServerHost(self):
        """
        shareServerHost is called whenever a indi server host is edited. if checkbox
        for sharing is set, the new entry will be copied to all other indi servers

        :return:
        """

        if not self.ui.shareIndiServer.isChecked():
            return False

        hosts = list(self.indiDevices[name]['host'] for name in self.indiDevices)

        if self.sender() not in hosts:
            return False

        for host in hosts:
            if self.sender() == host:
                continue
            host.setText(self.sender().text())

        return True

    def shareServerPort(self):
        """
        shareServerPort is called whenever a indi server port is edited. if checkbox
        for sharing is set, the new entry will be copied to all other indi servers

        :return:
        """

        if not self.ui.shareIndiServer.isChecked():
            return False

        ports = list(self.indiDevices[name]['port'] for name in self.indiDevices)

        if self.sender() not in ports:
            return False

        for port in ports:
            if self.sender() == port:
                continue
            port.setText(self.sender().text())

        return True

    @staticmethod
    def removePrefix(text, prefix):
        """

        :param text:
        :param prefix:
        :return:
        """

        value = text[text.startswith(prefix) and len(prefix):]
        value = value.strip()
        return value

    def showIndiDomeDisconnected(self):
        """
        showIndiDomeDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.domeDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showDomeDeviceConnected(self, deviceName):
        """
        showDomeDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.domeDevice.setStyleSheet(self.BACK_GREEN)
        self.deviceStat['dome'] = True
        return True

    def showDomeDeviceDisconnected(self):
        """
        showDomeDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.domeDevice.setStyleSheet(self.BACK_NORM)
        self.deviceStat['dome'] = False
        return True

    def showIndiImagingDisconnected(self):
        """
        showIndiImagingDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.imagingDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showImagingDeviceConnected(self, deviceName):
        """
        showImagingDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.imagingDevice.setStyleSheet(self.BACK_GREEN)
        self.deviceStat['imaging'] = True
        return True

    def showImagingDeviceDisconnected(self):
        """
        showImagingDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.imagingDevice.setStyleSheet(self.BACK_NORM)
        self.deviceStat['imaging'] = False
        return True

    def showIndiEnvironDisconnected(self):
        """
        showIndiEnvironDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.environDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showEnvironDeviceConnected(self, deviceName):
        """
        showEnvironDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.environDevice.setStyleSheet(self.BACK_GREEN)
        self.deviceStat['environment'] = True
        return True

    def showEnvironDeviceDisconnected(self, deviceName):
        """
        showEnvironDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.environDevice.setStyleSheet(self.BACK_NORM)
        self.deviceStat['environment'] = False
        return True

    def showIndiSkymeterDisconnected(self):
        """
        showIndiSkymeterDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.skymeterDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showSkymeterDeviceConnected(self, deviceName):
        """
        showSkymeterDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.skymeterDevice.setStyleSheet(self.BACK_GREEN)
        self.deviceStat['skymeter'] = True
        return True

    def showSkymeterDeviceDisconnected(self, deviceName):
        """
        showSkymeterDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.skymeterDevice.setStyleSheet(self.BACK_NORM)
        self.deviceStat['skymeter'] = False
        return True

    def showIndiTelescopeDisconnected(self):
        """
        showIndiTelescopeDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.telescopeDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showTelescopeDeviceConnected(self, deviceName):
        """
        showTelescopeDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.telescopeDevice.setStyleSheet(self.BACK_GREEN)
        self.deviceStat['telescope'] = True
        return True

    def showTelescopeDeviceDisconnected(self, deviceName):
        """
        showTelescopeDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.telescopeDevice.setStyleSheet(self.BACK_NORM)
        self.deviceStat['telescope'] = False
        return True

    def showIndiPowerDisconnected(self):
        """
        showIndiPowerDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.powerDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showPowerDeviceConnected(self, deviceName):
        """
        showPowerDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['power'] = True
        self.ui.powerDevice.setStyleSheet(self.BACK_GREEN)
        return True

    def showPowerDeviceDisconnected(self, deviceName):
        """
        showPowerDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['power'] = False
        self.ui.powerDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showIndiCoverDisconnected(self):
        """
        showIndiCoverDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.coverDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showCoverDeviceConnected(self, deviceName):
        """
        showCoverDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['cover'] = True
        self.ui.coverDevice.setStyleSheet(self.BACK_GREEN)
        return True

    def showCoverDeviceDisconnected(self, deviceName):
        """
        showCoverDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['cover'] = False
        self.ui.coverDevice.setStyleSheet(self.BACK_NORM)
        return True


    def showIndiDisconnected(self):
        """
        showIndiDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """
        a = self.sender()
        print(a)

        self.ui.coverDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showDeviceConnected(self, deviceName):
        """
        showCoverDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['cover'] = True
        self.ui.coverDevice.setStyleSheet(self.BACK_GREEN)
        return True

    def showDeviceDisconnected(self, deviceName):
        """
        showCoverDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['cover'] = False
        self.ui.coverDevice.setStyleSheet(self.BACK_NORM)
        return True
