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
        self.ui.relayDevice.currentIndexChanged.connect(self.enableRelay)
        self.ui.remoteDevice.currentIndexChanged.connect(self.enableRemote)

        self.ui.environDevice.currentIndexChanged.connect(self.environDispatch)

        signals = self.app.environ.client.signals
        signals.serverConnected.connect(self.indiEnvironConnected)
        signals.serverDisconnected.connect(self.indiEnvironDisconnected)
        signals.newDevice.connect(self.newEnvironDevice)
        signals.removeDevice.connect(self.removeEnvironDevice)

    def initConfig(self):
        config = self.app.config['mainW']
        for dropDown, key in zip(self.deviceDropDowns, self.deviceDropDownKeys):
            dropDown.setCurrentIndex(config.get(key, 0))

        self.enableRelay()
        self.enableRemote()
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

    def updateGUI(self):
        """
        updateGUI update gui elements on regular bases (actually 1 second) for items,
        which are not events based.

        :return: success
        """

        if self.app.environ.device is not None:
            if self.app.environ.device.getSwitch('CONNECTION'):
                print('connected')
            else:
                print('not connected')
        return True

    def setupDeviceGui(self):
        """
        setupRelayGui handles the modeldata of list for relay handling.

        :return: success for test
        """

        for dropDown in self.deviceDropDowns:
            dropDown.clear()
            dropDown.setView(PyQt5.QtWidgets.QListView())
            dropDown.addItem('No device selected - Off')

        # adding special items
        self.ui.measureDevice.addItem('Built-In Measurement - On')
        self.ui.remoteDevice.addItem('Built-In Remote - On')
        self.ui.relayDevice.addItem('Built-In Relay - On')

        self.ui.environDevice.addItem('Indi Driver - On')

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
            self.app.message.emit('Relay enabled', 2)
            self.app.relay.startTimers()
        else:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            self.app.message.emit('Relay disabled', 2)
            self.app.relay.stopTimers()
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
            self.app.message.emit('Remote enabled', 2)
        else:
            self.app.remote.stopRemote()
            self.app.message.emit('Remote disabled', 2)

        return True

    def environDispatch(self):
        index = self.ui.environDevice.currentIndex()
        if index == 1:
            self.app.environ.startCommunication()
        else:
            self.app.environ.stopCommunication()

    def indiEnvironConnected(self):
        self.app.message.emit('INDI server environment connected', 0)

    def indiEnvironDisconnected(self):
        self.app.message.emit('INDI server environment disconnected', 0)

    def newEnvironDevice(self, deviceName):
        self.app.message.emit(f'INDI environment device [{deviceName}] found', 0)

    def removeEnvironDevice(self, deviceName):
        self.app.message.emit(f'INDI environment device [{deviceName}] removed', 0)
