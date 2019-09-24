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
        self.deviceNameDropDowns = [self.ui.imagingDeviceName,
                                    self.ui.domeDeviceName,
                                    self.ui.environDeviceName,
                                    self.ui.skymeterDeviceName,
                                    self.ui.coverDeviceName,
                                    self.ui.powerDeviceName,
                                    self.ui.telescopeDeviceName,
                                    ]
        self.deviceNameDropDownKeys = ['imagingDeviceName',
                                       'domeDeviceName',
                                       'environmentDeviceName',
                                       'skymeterDeviceName',
                                       'coverDeviceName',
                                       'powerDeviceName',
                                       'telescopeDeviceName',
                                       ]

        # all internal signal for handling
        sig = self.app.dome.client.signals
        sig.serverDisconnected.connect(self.showIndiDomeDisconnected)
        sig.deviceConnected.connect(self.showDomeDeviceConnected)
        sig.deviceDisconnected.connect(self.showDomeDeviceDisconnected)
        sig.newDevice.connect(self.showIndiNewDomeDevice)
        sig.removeDevice.connect(self.showIndiRemoveDomeDevice)
        sig.newMessage.connect(self.indiMessage)

        sig = self.app.imaging.client.signals
        sig.serverDisconnected.connect(self.showIndiImagingDisconnected)
        sig.deviceConnected.connect(self.showImagingDeviceConnected)
        sig.deviceDisconnected.connect(self.showImagingDeviceDisconnected)
        sig.newDevice.connect(self.showIndiNewImagingDevice)
        sig.removeDevice.connect(self.showIndiRemoveImagingDevice)
        sig.newMessage.connect(self.indiMessage)

        sig = self.app.environ.client.signals
        sig.serverDisconnected.connect(self.showIndiEnvironDisconnected)
        sig.deviceConnected.connect(self.showEnvironDeviceConnected)
        sig.deviceDisconnected.connect(self.showEnvironDeviceDisconnected)
        sig.newDevice.connect(self.showIndiNewEnvironDevice)
        sig.removeDevice.connect(self.showIndiRemoveEnvironDevice)
        sig.newMessage.connect(self.indiMessage)

        sig = self.app.cover.client.signals
        sig.serverDisconnected.connect(self.showIndiCoverDisconnected)
        sig.deviceConnected.connect(self.showCoverDeviceConnected)
        sig.deviceDisconnected.connect(self.showCoverDeviceDisconnected)
        sig.newDevice.connect(self.showIndiNewCoverDevice)
        sig.removeDevice.connect(self.showIndiRemoveCoverDevice)
        sig.newMessage.connect(self.indiMessage)

        sig = self.app.skymeter.client.signals
        sig.serverDisconnected.connect(self.showIndiSkymeterDisconnected)
        sig.deviceConnected.connect(self.showSkymeterDeviceConnected)
        sig.deviceDisconnected.connect(self.showSkymeterDeviceDisconnected)
        sig.newDevice.connect(self.showIndiNewSkymeterDevice)
        sig.removeDevice.connect(self.showIndiRemoveSkymeterDevice)
        sig.newMessage.connect(self.indiMessage)

        sig = self.app.telescope.client.signals
        sig.serverDisconnected.connect(self.showIndiTelescopeDisconnected)
        sig.deviceConnected.connect(self.showTelescopeDeviceConnected)
        sig.deviceDisconnected.connect(self.showTelescopeDeviceDisconnected)
        sig.newDevice.connect(self.showIndiNewTelescopeDevice)
        sig.removeDevice.connect(self.showIndiRemoveTelescopeDevice)
        sig.newMessage.connect(self.indiMessage)

        sig = self.app.power.client.signals
        sig.serverDisconnected.connect(self.showIndiPowerDisconnected)
        sig.deviceConnected.connect(self.showPowerDeviceConnected)
        sig.deviceDisconnected.connect(self.showPowerDeviceDisconnected)
        sig.newDevice.connect(self.showIndiNewPowerDevice)
        sig.removeDevice.connect(self.showIndiRemovePowerDevice)
        sig.newMessage.connect(self.indiMessage)

        self.setupDeviceNameGui()

        # signals from gui

        self.ui.domeDeviceName.currentIndexChanged.connect(self.domeDispatch)
        self.ui.imagingDeviceName.currentIndexChanged.connect(self.imagingDispatch)
        self.ui.environDeviceName.currentIndexChanged.connect(self.environDispatch)
        self.ui.coverDeviceName.currentIndexChanged.connect(self.coverDispatch)
        self.ui.telescopeDeviceName.currentIndexChanged.connect(self.telescopeDispatch)
        self.ui.skymeterDeviceName.currentIndexChanged.connect(self.skymeterDispatch)
        self.ui.powerDeviceName.currentIndexChanged.connect(self.powerDispatch)

        self.ui.environHost.editingFinished.connect(self.shareServerHost)
        self.ui.coverHost.editingFinished.connect(self.shareServerHost)
        self.ui.imagingHost.editingFinished.connect(self.shareServerHost)
        self.ui.domeHost.editingFinished.connect(self.shareServerHost)
        self.ui.telescopeHost.editingFinished.connect(self.shareServerHost)
        self.ui.skymeterHost.editingFinished.connect(self.shareServerHost)
        self.ui.powerHost.editingFinished.connect(self.shareServerHost)

        self.ui.environPort.editingFinished.connect(self.shareServerPort)
        self.ui.coverPort.editingFinished.connect(self.shareServerPort)
        self.ui.imagingPort.editingFinished.connect(self.shareServerPort)
        self.ui.domePort.editingFinished.connect(self.shareServerPort)
        self.ui.telescopePort.editingFinished.connect(self.shareServerPort)
        self.ui.skymeterPort.editingFinished.connect(self.shareServerPort)
        self.ui.powerPort.editingFinished.connect(self.shareServerPort)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for dropDown, key in zip(self.deviceNameDropDowns, self.deviceNameDropDownKeys):
            dropDown.setCurrentIndex(config.get(key, 0))

        self.ui.environHost.setText(config.get('environHost', ''))
        self.ui.environPort.setText(config.get('environPort', '7624'))
        self.ui.coverHost.setText(config.get('coverHost', ''))
        self.ui.coverPort.setText(config.get('coverPort', '7624'))
        self.ui.imagingHost.setText(config.get('imagingHost', ''))
        self.ui.imagingPort.setText(config.get('imagingPort', '7624'))
        self.ui.domeHost.setText(config.get('domeHost', ''))
        self.ui.domePort.setText(config.get('domePort', '7624'))
        self.ui.telescopeHost.setText(config.get('telescopeHost', ''))
        self.ui.telescopePort.setText(config.get('telescopePort', '7624'))
        self.ui.skymeterHost.setText(config.get('skymeterHost', ''))
        self.ui.skymeterPort.setText(config.get('skymeterPort', '7624'))
        self.ui.powerHost.setText(config.get('powerHost', ''))
        self.ui.powerPort.setText(config.get('powerPort', '7624'))

        self.ui.indiMessage.setChecked(config.get('indiMessage', False))
        self.ui.shareIndiServer.setChecked(config.get('shareIndiServer', False))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for dropDown, key in zip(self.deviceNameDropDowns, self.deviceNameDropDownKeys):
            config[key] = dropDown.currentIndex()
        config['environHost'] = self.ui.environHost.text()
        config['environPort'] = self.ui.environPort.text()
        config['coverHost'] = self.ui.coverHost.text()
        config['coverPort'] = self.ui.coverPort.text()
        config['imagingHost'] = self.ui.imagingHost.text()
        config['imagingPort'] = self.ui.imagingPort.text()
        config['domeHost'] = self.ui.domeHost.text()
        config['domePort'] = self.ui.domePort.text()
        config['skymeterHost'] = self.ui.skymeterHost.text()
        config['skymeterPort'] = self.ui.skymeterPort.text()
        config['telescopeHost'] = self.ui.telescopeHost.text()
        config['telescopePort'] = self.ui.telescopePort.text()
        config['powerHost'] = self.ui.powerHost.text()
        config['powerPort'] = self.ui.powerPort.text()

        config['indiMessage'] = self.ui.indiMessage.isChecked()
        config['shareIndiServer'] = self.ui.shareIndiServer.isChecked()

        return True

    def setupDeviceNameGui(self):
        """
        setupRelayGui handles the dropdown lists for all devices possible in mountwizzard.
        therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        for dropDown in self.deviceNameDropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device driver selected')
        # adding special items
        self.ui.imagingDeviceName.addItem('Altair')
        self.ui.imagingDeviceName.addItem('Apogee CCD')
        self.ui.imagingDeviceName.addItem('Atik CCD')
        self.ui.imagingDeviceName.addItem('CCD Simulator')
        self.ui.imagingDeviceName.addItem('Canon DSLR')
        self.ui.imagingDeviceName.addItem('DMK CCD')
        self.ui.imagingDeviceName.addItem('FLI CCD')
        self.ui.imagingDeviceName.addItem('FireFly MV')
        self.ui.imagingDeviceName.addItem('GPhoto CCD')
        self.ui.imagingDeviceName.addItem('Guide Simulator')
        self.ui.imagingDeviceName.addItem('MI CCD (ETH)')
        self.ui.imagingDeviceName.addItem('MI CCD (USB)')
        self.ui.imagingDeviceName.addItem('Meade Deep Sky Imager')
        self.ui.imagingDeviceName.addItem('Nightscape 8300 CCD')
        self.ui.imagingDeviceName.addItem('Nikon DSLR')
        self.ui.imagingDeviceName.addItem('Pentax DSLR')
        self.ui.imagingDeviceName.addItem('QHY CCD')
        self.ui.imagingDeviceName.addItem('QSI CCD')
        self.ui.imagingDeviceName.addItem('SBIG CCD')
        self.ui.imagingDeviceName.addItem('SBIG ST-I')
        self.ui.imagingDeviceName.addItem('SX CCD')
        self.ui.imagingDeviceName.addItem('Sony DSLR')
        self.ui.imagingDeviceName.addItem('Starfish CCD')
        self.ui.imagingDeviceName.addItem('ToupCam')
        self.ui.imagingDeviceName.addItem('V4L2 CCD')
        self.ui.imagingDeviceName.addItem('ZWO CCD')

        self.ui.domeDeviceName.addItem('Baader Dome')
        self.ui.domeDeviceName.addItem('Dome Scripting Gateway')
        self.ui.domeDeviceName.addItem('Dome Simulator')
        self.ui.domeDeviceName.addItem('MaxDome II')
        self.ui.domeDeviceName.addItem('NexDome')
        self.ui.domeDeviceName.addItem('RollOff Simulator')
        self.ui.domeDeviceName.addItem('ScopeDome Dome')

        self.ui.environDeviceName.addItem('AAG Cloud Watcher')
        self.ui.environDeviceName.addItem('Arduino MeteoStation')
        self.ui.environDeviceName.addItem('MBox')
        self.ui.environDeviceName.addItem('OpenWeatherMap')
        self.ui.environDeviceName.addItem('Vantage')
        self.ui.environDeviceName.addItem('Weather Meta')
        self.ui.environDeviceName.addItem('Weather Simulator')
        self.ui.environDeviceName.addItem('Weather Watcher')
        self.ui.environDeviceName.addItem('WonderGround')

        self.ui.skymeterDeviceName.addItem('SQM')
        self.ui.telescopeDeviceName.addItem('LX200 10micron')
        self.ui.powerDeviceName.addItem('Pegasus UPB')
        self.ui.coverDeviceName.addItem('Flip Flat')

        return True

    def shareServerHost(self):
        """
        shareServerHost is called whenever a indi server host is edited. if checkbox
        for sharing is set, the new entry will be copied to all other indi servers

        :return:
        """

        if not self.ui.shareIndiServer.isChecked():
            return False

        hosts = [self.ui.environHost,
                 self.ui.coverHost,
                 self.ui.imagingHost,
                 self.ui.domeHost,
                 self.ui.skymeterHost,
                 self.ui.telescopeHost,
                 self.ui.powerHost,
                 self.ui.skymeterHost,
                 ]

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

        ports = [self.ui.environPort,
                 self.ui.coverPort,
                 self.ui.imagingPort,
                 self.ui.domePort,
                 self.ui.skymeterPort,
                 self.ui.telescopePort,
                 self.ui.powerPort,
                 ]

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

    def indiMessage(self, device, text):
        """
        indiMessage take a message send by indi device and puts them in the user message
        window as well.

        :param device: device name
        :param text: message received
        :return: success
        """
        if self.ui.indiMessage.isChecked():
            if text.startswith('[WARNING]'):
                text = self.removePrefix(text, '[WARNING]')
                self.app.message.emit(device + ' -> ' + text, 0)
            elif text.startswith('[ERROR]'):
                text = self.removePrefix(text, '[ERROR]')
                self.app.message.emit(device + ' -> ' + text, 2)
            else:
                self.app.message.emit(device + ' -> ' + text, 0)
            return True
        return False

    def showIndiDomeDisconnected(self):
        """
        showIndiDomeDisconnected writes info to message window and recolors the status

        :return: true for test purpose
        """

        self.ui.domeDevice.setStyleSheet(self.BACK_NORM)
        return True

    def showIndiNewDomeDevice(self, deviceName):
        """
        showIndiNewDomeDevice writes info to message window

        :return: true for test purpose
        """

        if deviceName == self.app.dome.name:
            self.app.message.emit(f'INDI dome device [{deviceName}] found', 0)
        else:
            self.app.message.emit(f'INDI dome device snoops -> [{deviceName}]', 0)

        return True

    def showIndiRemoveDomeDevice(self, deviceName):
        """
        showIndiRemoveDomeDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI dome device [{deviceName}] removed', 0)
        return True

    def showDomeDeviceConnected(self):
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

    def showIndiNewImagingDevice(self, deviceName):
        """
        showIndiNewImagingDevice writes info to message window

        :return: true for test purpose
        """

        if deviceName == self.app.imaging.name:
            self.app.message.emit(f'INDI imaging device [{deviceName}] found', 0)
        else:
            self.app.message.emit(f'INDI imaging device snoops -> [{deviceName}]', 0)

        return True

    def showIndiRemoveImagingDevice(self, deviceName):
        """
        showIndiRemoveImagingDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI imaging device [{deviceName}] removed', 0)
        return True

    def showImagingDeviceConnected(self):
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

    def showIndiNewEnvironDevice(self, deviceName):
        """
        showIndiNewEnvironDevice writes info to message window

        :return: true for test purpose
        """

        if deviceName == self.app.environ.name:
            self.app.message.emit(f'INDI environment device [{deviceName}] found', 0)
        else:
            self.app.message.emit(f'INDI environment device snoops -> [{deviceName}]', 0)

        return True

    def showIndiRemoveEnvironDevice(self, deviceName):
        """
        showIndiRemoveEnvironDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI environment device [{deviceName}] removed', 0)
        return True

    def showEnvironDeviceConnected(self):
        """
        showEnvironDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.environDevice.setStyleSheet(self.BACK_GREEN)
        self.deviceStat['environment'] = True
        return True

    def showEnvironDeviceDisconnected(self):
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

    def showIndiNewSkymeterDevice(self, deviceName):
        """
        showIndiNewSkymeterDevice writes info to message window

        :return: true for test purpose
        """

        if deviceName == self.app.skymeter.name:
            self.app.message.emit(f'INDI skymeter device [{deviceName}] found', 0)
        else:
            self.app.message.emit(f'INDI skymeter device snoops -> [{deviceName}]', 0)
        return True

    def showIndiRemoveSkymeterDevice(self, deviceName):
        """
        showIndiRemoveSkymeterDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI skymeter device [{deviceName}] removed', 0)
        return True

    def showSkymeterDeviceConnected(self):
        """
        showSkymeterDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.skymeterDevice.setStyleSheet(self.BACK_GREEN)
        self.deviceStat['skymeter'] = True
        return True

    def showSkymeterDeviceDisconnected(self):
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

    def showIndiNewTelescopeDevice(self, deviceName):
        """
        showIndiNewTelescopeDevice writes info to message window

        :return: true for test purpose
        """

        if deviceName == self.app.telescope.name:
            self.app.message.emit(f'INDI telescope device [{deviceName}] found', 0)
        else:
            self.app.message.emit(f'INDI telescope device snoops -> [{deviceName}]', 0)
        return True

    def showIndiRemoveTelescopeDevice(self, deviceName):
        """
        showIndiRemoveTelescopeDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI telescope device [{deviceName}] removed', 0)
        return True

    def showTelescopeDeviceConnected(self):
        """
        showTelescopeDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.ui.telescopeDevice.setStyleSheet(self.BACK_GREEN)
        self.deviceStat['telescope'] = True
        return True

    def showTelescopeDeviceDisconnected(self):
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

    def showIndiNewPowerDevice(self, deviceName):
        """
        showIndiNewPowerDevice writes info to message window

        :return: true for test purpose
        """

        if deviceName == self.app.power.name:
            self.app.message.emit(f'INDI power device [{deviceName}] found', 0)
        else:
            self.app.message.emit(f'INDI power device snoops -> [{deviceName}]', 0)
        return True

    def showIndiRemovePowerDevice(self, deviceName):
        """
        showIndiRemovePowerDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI power device [{deviceName}] removed', 0)
        return True

    def showPowerDeviceConnected(self):
        """
        showPowerDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['power'] = True
        self.ui.powerDevice.setStyleSheet(self.BACK_GREEN)
        return True

    def showPowerDeviceDisconnected(self):
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

    def showIndiNewCoverDevice(self, deviceName):
        """
        showIndiNewCoverDevice writes info to message window

        :return: true for test purpose
        """

        if deviceName == self.app.cover.name:
            self.app.message.emit(f'INDI cover device [{deviceName}] found', 0)
        else:
            self.app.message.emit(f'INDI cover device snoops -> [{deviceName}]', 0)
        return True

    def showIndiRemoveCoverDevice(self, deviceName):
        """
        showIndiRemoveCoverDevice writes info to message window

        :return: true for test purpose
        """

        self.app.message.emit(f'INDI cover device [{deviceName}] removed', 0)
        return True

    def showCoverDeviceConnected(self):
        """
        showCoverDeviceConnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['cover'] = True
        self.ui.coverDevice.setStyleSheet(self.BACK_GREEN)
        return True

    def showCoverDeviceDisconnected(self):
        """
        showCoverDeviceDisconnected changes the style of related ui groups to make it clear
        to the user, which function is actually available

        :return: true for test purpose
        """

        self.deviceStat['cover'] = False
        self.ui.coverDevice.setStyleSheet(self.BACK_NORM)
        return True
