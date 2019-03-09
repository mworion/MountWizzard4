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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
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
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.deviceDropDowns = [self.ui.ccdDevice,
                                self.ui.astrometryDevice,
                                self.ui.domeDevice,
                                self.ui.environDevice,
                                self.ui.skymeterDevice,
                                self.ui.powerDevice,
                                self.ui.relayDevice,
                                self.ui.measureDevice,
                                self.ui.remoteDevice,
                                ]
        self.deviceDropDownKeys = ['ccdDevice',
                                   'astrometryDevice',
                                   'domeDevice',
                                   'environmentDevice',
                                   'skymeterDevice',
                                   'powerDevice',
                                   'relayDevice',
                                   'measureDevice',
                                   'remoteDevice',
                                   ]
        self.setupDeviceGui()
        self.ui.relayDevice.activated.connect(self.enableRelay)
        self.ui.remoteDevice.activated.connect(self.enableRemote)
        self.ui.measureDevice.activated.connect(self.enableMeasure)
        self.ui.environDevice.activated.connect(self.environDispatch)

        signals = self.app.environ.client.signals
        signals.serverConnected.connect(self.indiEnvironConnected)
        signals.serverDisconnected.connect(self.indiEnvironDisconnected)
        signals.deviceConnected.connect(self.indiEnvironDeviceConnected)
        signals.deviceDisconnected.connect(self.indiEnvironDeviceDisconnected)
        signals.newDevice.connect(self.newEnvironDevice)
        signals.removeDevice.connect(self.removeEnvironDevice)

    def initConfig(self):
        config = self.app.config['mainW']
        for dropDown, key in zip(self.deviceDropDowns, self.deviceDropDownKeys):
            dropDown.setCurrentIndex(config.get(key, 0))

        self.enableRelay()
        self.enableRemote()
        self.enableMeasure()
        self.environDispatch()
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        for dropDown, key in zip(self.deviceDropDowns, self.deviceDropDownKeys):
            config[key] = dropDown.currentIndex()

        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        return True

    def clearMountGUI(self):
        """
        clearMountGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        return True

    def setupDeviceGui(self):
        """
        setupRelayGui handles the modeldata of list for relay handling.

        :return: success for test
        """

        for dropDown in self.deviceDropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device selected')

        # adding special items
        self.ui.measureDevice.addItem('Built-In Measurement')
        self.ui.remoteDevice.addItem('Built-In Remote')
        self.ui.relayDevice.addItem('Built-In Relay KMTronic')

        self.ui.environDevice.addItem('Indi Driver')

        return True

    def enableRelay(self):
        """
        enableRelay allows to run the relay box.

        :return: success for test
        """

        # get index for relay tab
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Relay')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)

        if self.ui.relayDevice.currentIndex() == 1:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            self.app.message.emit('Relay enabled', 0)
            self.app.relay.startTimers()
            self.ui.relayDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            self.app.message.emit('Relay disabled', 0)
            self.app.relay.stopTimers()
            self.ui.relayDevice.setStyleSheet(self.BACK_NORM)

        # update the style for showing the Relay tab
        self.ui.mainTabWidget.style().unpolish(self.ui.mainTabWidget)
        self.ui.mainTabWidget.style().polish(self.ui.mainTabWidget)
        return True

    def enableRemote(self):
        """
        remoteAccess enables or disables the remote access

        :return: true for test purpose
        """

        if self.ui.remoteDevice.currentIndex() == 1:
            self.app.remote.startRemote()
            self.app.message.emit('Remote enabled', 0)
            self.ui.remoteDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.remote.stopRemote()
            self.app.message.emit('Remote disabled', 0)
            self.ui.remoteDevice.setStyleSheet(self.BACK_NORM)

        return True

    def enableMeasure(self):
        """
        enableMeasure enables or disables the remote access

        :return: true for test purpose
        """

        if self.ui.measureDevice.currentIndex() == 1:
            self.app.measure.startMeasurement()
            self.app.message.emit('Measurement enabled', 0)
            self.ui.measureDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.app.measure.stopMeasurement()
            self.app.message.emit('Measurement disabled', 0)
            self.ui.measureDevice.setStyleSheet(self.BACK_NORM)

        return True

    def environDispatch(self):
        index = self.ui.environDevice.currentIndex()
        if index == 1:
            self.app.environ.client.host = self.ui.environHost.text()
            self.app.environ.name = self.ui.environName.text()
            self.app.environ.startCommunication()
            self.changeStyleDynamic(self.ui.environConnected, 'color', 'red')
        else:
            self.app.environ.stopCommunication()
            self.changeStyleDynamic(self.ui.environConnected, 'color', 'gray')

    def indiEnvironConnected(self):
        self.app.message.emit('INDI server environment connected', 0)

    def indiEnvironDisconnected(self):
        self.ui.environDevice.setStyleSheet(self.BACK_NORM)
        self.app.message.emit('INDI server environment disconnected', 0)

    def newEnvironDevice(self, deviceName):
        self.app.message.emit(f'INDI environment device [{deviceName}] found', 0)

    def removeEnvironDevice(self, deviceName):
        self.app.message.emit(f'INDI environment device [{deviceName}] removed', 0)

    def indiEnvironDeviceConnected(self):
        self.ui.environDevice.setStyleSheet(self.BACK_GREEN)
        self.changeStyleDynamic(self.ui.environConnected, 'color', 'green')

    def indiEnvironDeviceDisconnected(self):
        self.ui.environDevice.setStyleSheet(self.BACK_NORM)
        self.changeStyleDynamic(self.ui.environConnected, 'color', 'red')
