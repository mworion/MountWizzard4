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
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import


class SettDevice(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadPool for managing async
    processing if needed.
    """

    def __init__(self):
        self.deviceDropDowns = [self.ui.imagingDevice,
                                self.ui.astrometryDevice,
                                self.ui.domeDevice,
                                self.ui.environDevice,
                                self.ui.skymeterDevice,
                                self.ui.coverDevice,
                                self.ui.telescopeDevice,
                                self.ui.powerDevice,
                                self.ui.relayDevice,
                                self.ui.measureDevice,
                                self.ui.remoteDevice,
                                ]
        self.deviceDropDownKeys = ['imagingDevice',
                                   'astrometryDevice',
                                   'domeDevice',
                                   'environmentDevice',
                                   'skymeterDevice',
                                   'coverDevice',
                                   'telescopeDevice',
                                   'powerDevice',
                                   'relayDevice',
                                   'measureDevice',
                                   'remoteDevice',
                                   ]
        self.setupDeviceGui()
        self.ui.imagingDevice.activated.connect(self.imagingDispatch)
        self.ui.relayDevice.activated.connect(self.relayDispatch)
        self.ui.remoteDevice.activated.connect(self.remoteDispatch)
        self.ui.measureDevice.activated.connect(self.measureDispatch)
        self.ui.domeDevice.activated.connect(self.domeDispatch)
        self.ui.environDevice.activated.connect(self.environDispatch)
        self.ui.skymeterDevice.activated.connect(self.skymeterDispatch)
        self.ui.coverDevice.activated.connect(self.coverDispatch)
        self.ui.telescopeDevice.activated.connect(self.telescopeDispatch)
        self.ui.powerDevice.activated.connect(self.powerDispatch)
        self.ui.astrometryDevice.activated.connect(self.astrometryDispatch)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for dropDown, key in zip(self.deviceDropDowns, self.deviceDropDownKeys):
            dropDown.setCurrentIndex(config.get(key, 0))

        self.telescopeDispatch()
        self.relayDispatch()
        self.remoteDispatch()
        self.measureDispatch()
        self.domeDispatch()
        self.imagingDispatch()
        self.environDispatch()
        self.skymeterDispatch()
        self.coverDispatch()
        self.powerDispatch()
        self.astrometryDispatch()
        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        for dropDown, key in zip(self.deviceDropDowns, self.deviceDropDownKeys):
            config[key] = dropDown.currentIndex()

        return True

    def setupDeviceGui(self):
        """
        setupRelayGui handles the dropdown lists for all devices possible in mountwizzard.
        therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        for dropDown in self.deviceDropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device selected')

        # adding special items
        self.ui.measureDevice.addItem('Built-In')
        self.ui.remoteDevice.addItem('Built-In')
        self.ui.relayDevice.addItem('Built-In')
        self.ui.environDevice.addItem('INDI')
        self.ui.domeDevice.addItem('INDI')
        self.ui.imagingDevice.addItem('INDI')
        self.ui.skymeterDevice.addItem('INDI')
        self.ui.coverDevice.addItem('INDI')
        self.ui.telescopeDevice.addItem('INDI')
        self.ui.powerDevice.addItem('INDI')
        for app in self.app.astrometry.solverAvailable:
            self.ui.astrometryDevice.addItem(app)

        return True

    def relayDispatch(self):
        """
        relayDispatch allows to run the relay box.

        :return: success for test
        """

        if self.ui.relayDevice.currentText().startswith('Built-In'):
            self.app.message.emit('Relay enabled', 0)
            self.deviceStat['relay'] = True
            self.app.relay.startTimers()
            self.ui.relayDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.message.emit('Relay disabled', 0)
            self.deviceStat['relay'] = False
            self.app.relay.stopTimers()
            self.ui.relayDevice.setStyleSheet(self.BACK_NORM)

        return True

    def remoteDispatch(self):
        """
        remoteAccess enables or disables the remote access

        :return: true for test purpose
        """

        if self.ui.remoteDevice.currentText() == 'Built-In':
            self.app.remote.startRemote()
            self.app.message.emit('Remote enabled', 0)
            self.ui.remoteDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.remote.stopRemote()
            self.app.message.emit('Remote disabled', 0)
            self.ui.remoteDevice.setStyleSheet(self.BACK_NORM)

        return True

    def measureDispatch(self):
        """
        measureDispatch enables or disables the on board measurement process

        :return: true for test purpose
        """

        if self.ui.measureDevice.currentText().startswith('Built-In'):
            self.app.measure.startMeasurement()
            self.app.message.emit('Measurement enabled', 0)
            self.ui.measureDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.measure.stopMeasurement()
            self.app.message.emit('Measurement disabled', 0)
            self.ui.measureDevice.setStyleSheet(self.BACK_NORM)

        return True

    def domeDispatch(self):
        """
        domeDispatch selects the type of device for dome measures and start / stop
        them.
        in addition this function enables and disables other gui functions, which rely on
        the presence of a running driver

        :return: true for test purpose
        """

        if self.ui.domeDevice.currentText().startswith('INDI'):
            self.app.dome.client.host = self.ui.domeHost.text()
            if self.app.dome.name != self.ui.domeDeviceName.currentText():
                self.app.dome.stopCommunication()
            self.app.dome.name = self.ui.domeDeviceName.currentText()
            self.app.dome.startCommunication()
            self.app.message.emit('Dome enabled', 0)
        else:
            self.app.dome.stopCommunication()
            self.app.dome.name = ''
            self.app.message.emit('Dome disabled', 0)
            self.deviceStat['dome'] = None

        return True

    def imagingDispatch(self):
        """
        imagingDispatch selects the type of device for imaging and start / stop them.
        in addition this function enables and disables other gui functions, which rely on
        the presence of a running driver

        :return: true for test purpose
        """

        if self.ui.imagingDevice.currentText().startswith('INDI'):
            self.app.imaging.client.host = self.ui.imagingHost.text()
            if self.app.imaging.name != self.ui.imagingDeviceName.currentText():
                self.app.imaging.stopCommunication()
            self.app.imaging.name = self.ui.imagingDeviceName.currentText()
            self.app.imaging.startCommunication()
            self.app.message.emit('Imaging enabled', 0)
        else:
            self.app.imaging.stopCommunication()
            self.app.imaging.name = ''
            self.deviceStat['imaging'] = None
            self.app.message.emit('Imaging disabled', 0)

        return True

    def environDispatch(self):
        """
        environDispatch selects the type of device for environment measures and start / stop
        them.
        in addition this function enables and disables other gui functions, which rely on
        the presence of a running driver

        :return: true for test purpose
        """

        if self.ui.environDevice.currentText().startswith('INDI'):
            self.app.environ.client.host = self.ui.environHost.text()
            if self.app.environ.name != self.ui.environDeviceName.currentText():
                self.app.environ.stopCommunication()
            self.app.environ.name = self.ui.environDeviceName.currentText()
            self.app.environ.startCommunication()
            self.app.message.emit('Environment enabled', 0)
        else:
            self.app.environ.stopCommunication()
            self.app.environ.name = ''
            self.deviceStat['environ'] = None
            self.app.message.emit('Environment disabled', 0)

        return True

    def skymeterDispatch(self):
        """
        skymeterDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        if self.ui.skymeterDevice.currentText().startswith('INDI'):
            self.app.skymeter.client.host = self.ui.skymeterHost.text()
            if self.app.skymeter.name != self.ui.skymeterDeviceName.currentText():
                self.app.skymeter.stopCommunication()
            self.app.skymeter.name = self.ui.skymeterDeviceName.currentText()
            self.app.skymeter.startCommunication()
            self.app.message.emit('Skymeter enabled', 0)
        else:
            self.app.skymeter.stopCommunication()
            self.app.skymeter.name = ''
            self.app.message.emit('Skymeter disabled', 0)
            self.deviceStat['skymeter'] = None

        return True

    def coverDispatch(self):
        """
        coverDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        if self.ui.coverDevice.currentText().startswith('INDI'):
            self.app.cover.client.host = self.ui.coverHost.text()
            if self.app.cover.name != self.ui.coverDeviceName.currentText():
                self.app.cover.stopCommunication()
            self.app.cover.name = self.ui.coverDeviceName.currentText()
            self.app.cover.startCommunication()
            self.app.message.emit('Cover enabled', 0)
        else:
            self.app.cover.stopCommunication()
            self.app.cover.name = ''
            self.app.message.emit('Cover disabled', 0)
            self.deviceStat['cover'] = None

        return True

    def telescopeDispatch(self):
        """
        telescopeDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        if self.ui.telescopeDevice.currentText().startswith('INDI'):
            self.app.telescope.client.host = self.ui.telescopeHost.text()
            if self.app.telescope.name != self.ui.telescopeDeviceName.currentText():
                self.app.telescope.stopCommunication()
            self.app.telescope.name = self.ui.telescopeDeviceName.currentText()
            self.app.telescope.startCommunication()
            self.app.message.emit('Telescope enabled', 0)
        else:
            self.app.telescope.stopCommunication()
            self.app.telescope.name = ''
            self.app.message.emit('Telescope disabled', 0)
            self.deviceStat['telescope'] = None

        return True

    def powerDispatch(self):
        """
        powerDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        if self.ui.powerDevice.currentText().startswith('INDI'):
            self.app.power.client.host = self.ui.powerHost.text()
            if self.app.power.name != self.ui.powerDeviceName.currentText():
                self.app.power.stopCommunication()
            self.app.power.name = self.ui.powerDeviceName.currentText()
            self.app.power.startCommunication()
            self.app.message.emit('Power enabled', 0)
        else:
            self.app.power.stopCommunication()
            self.app.power.name = ''
            self.app.message.emit('Power disabled', 0)
            self.deviceStat['power'] = None

        return True

    def astrometryDispatch(self):
        """
        astrometryDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        if self.ui.astrometryDevice.currentText() in self.app.astrometry.solverAvailable:
            self.app.astrometry.solverSelected = self.ui.astrometryDevice.currentText()
            self.ui.astrometryDevice.setStyleSheet(self.BACK_GREEN)
            self.deviceStat['astrometry'] = True
            self.app.message.emit('Astrometry enabled', 0)
        else:
            self.app.message.emit('Astrometry disabled', 0)
            self.deviceStat['astrometry'] = None
            self.ui.astrometryDevice.setStyleSheet(self.BACK_NORM)

        return True
