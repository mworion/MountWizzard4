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
# Python  v3.7.3
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
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.deviceDropDowns = [self.ui.imagingDevice,
                                self.ui.astrometryDevice,
                                self.ui.domeDevice,
                                self.ui.environDevice,
                                self.ui.skymeterDevice,
                                self.ui.weatherDevice,
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
                                   'weatherDevice',
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
        self.ui.weatherDevice.activated.connect(self.weatherDispatch)
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

        self.relayDispatch()
        self.remoteDispatch()
        self.measureDispatch()
        self.domeDispatch()
        self.imagingDispatch()
        self.environDispatch()
        self.skymeterDispatch()
        self.weatherDispatch()
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

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
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
        self.ui.weatherDevice.addItem('INDI')
        self.ui.powerDevice.addItem('INDI')
        for app in self.app.astrometry.available:
            self.ui.astrometryDevice.addItem(app)

        return True

    def relayDispatch(self):
        """
        relayDispatch allows to run the relay box.

        :return: success for test
        """

        # get index for relay tab
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Relay')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)

        if self.ui.relayDevice.currentText().startswith('Built-In'):
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            self.ui.mainTabWidget.setStyleSheet(self.getStyle())
            self.app.message.emit('Relay enabled', 0)
            self.app.relay.startTimers()
            self.ui.relayDevice.setStyleSheet(self.BACK_GREEN)
        else:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            self.ui.mainTabWidget.setStyleSheet(self.getStyle())
            self.app.message.emit('Relay disabled', 0)
            self.app.relay.stopTimers()
            self.ui.relayDevice.setStyleSheet(self.BACK_NORM)

        # update the style for showing the Relay tab
        self.ui.mainTabWidget.style().unpolish(self.ui.mainTabWidget)
        self.ui.mainTabWidget.style().polish(self.ui.mainTabWidget)
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

        self.app.dome.stopCommunication()
        if self.ui.domeDevice.currentText().startswith('INDI'):
            self.app.dome.client.host = self.ui.domeHost.text()
            self.app.dome.name = self.ui.domeDeviceName.currentText()
            self.app.dome.startCommunication()
            self.changeStyleDynamic(self.ui.domeConnected, 'color', 'red')
            self.app.message.emit('Dome enabled', 0)
        else:
            self.changeStyleDynamic(self.ui.domeConnected, 'color', 'gray')
            self.app.message.emit('Dome disabled', 0)

        return True

    def imagingDispatch(self):
        """
        imagingDispatch selects the type of device for imaging and start / stop them.
        in addition this function enables and disables other gui functions, which rely on
        the presence of a running driver

        :return: true for test purpose
        """

        self.app.imaging.stopCommunication()
        if self.ui.imagingDevice.currentText().startswith('INDI'):
            self.app.imaging.client.host = self.ui.imagingHost.text()
            self.app.imaging.name = self.ui.imagingDeviceName.currentText()
            self.app.imaging.startCommunication()
            self.changeStyleDynamic(self.ui.imagingConnected, 'color', 'red')
            self.app.message.emit('Imaging enabled', 0)
        else:
            self.changeStyleDynamic(self.ui.imagingConnected, 'color', 'gray')
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

        self.ui.environGroup.setEnabled(False)
        self.ui.refractionGroup.setEnabled(False)
        self.ui.setRefractionManual.setEnabled(False)

        self.app.environ.stopCommunication()
        if self.ui.environDevice.currentText().startswith('INDI'):
            self.app.environ.client.host = self.ui.environHost.text()
            self.app.environ.name = self.ui.environDeviceName.currentText()
            self.app.environ.startCommunication()
            self.changeStyleDynamic(self.ui.environConnected, 'color', 'red')
            self.app.message.emit('Environment enabled', 0)
        else:
            self.changeStyleDynamic(self.ui.environConnected, 'color', 'gray')
            self.app.message.emit('Environment disabled', 0)

        return True

    def skymeterDispatch(self):
        """
        skymeterDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        self.ui.skymeterGroup.setEnabled(False)

        self.app.skymeter.stopCommunication()
        if self.ui.skymeterDevice.currentText().startswith('INDI'):
            self.app.skymeter.client.host = self.ui.skymeterHost.text()
            self.app.skymeter.name = self.ui.skymeterDeviceName.currentText()
            self.app.skymeter.startCommunication()
            self.app.message.emit('Skymeter enabled', 0)
        else:
            self.app.message.emit('Skymeter disabled', 0)

        return True

    def weatherDispatch(self):
        """
        weatherDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        self.ui.weatherGroup.setEnabled(False)

        self.app.weather.stopCommunication()
        if self.ui.weatherDevice.currentText().startswith('INDI'):
            self.app.weather.client.host = self.ui.weatherHost.text()
            self.app.weather.name = self.ui.weatherDeviceName.currentText()
            self.app.weather.startCommunication()
            self.app.message.emit('Weather enabled', 0)
        else:
            self.app.message.emit('Weather disabled', 0)

        return True

    def powerDispatch(self):
        """
        powerDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        self.ui.powerGroup.setEnabled(False)
        # get index for power tab
        tabWidget = self.ui.mainTabWidget.findChild(PyQt5.QtWidgets.QWidget, 'Power')
        tabIndex = self.ui.mainTabWidget.indexOf(tabWidget)

        self.app.power.stopCommunication()
        if self.ui.powerDevice.currentText().startswith('INDI'):
            self.app.power.startCommunication()
            self.ui.mainTabWidget.setTabEnabled(tabIndex, True)
            self.ui.mainTabWidget.setStyleSheet(self.getStyle())
            self.app.message.emit('Power enabled', 0)
            self.app.power.client.host = self.ui.powerHost.text()
            self.app.power.name = self.ui.powerDeviceName.currentText()
        else:
            self.ui.mainTabWidget.setTabEnabled(tabIndex, False)
            self.ui.mainTabWidget.setStyleSheet(self.getStyle())
            self.app.message.emit('Power disabled', 0)

        # update the style for showing the Relay tab
        self.ui.mainTabWidget.style().unpolish(self.ui.mainTabWidget)
        self.ui.mainTabWidget.style().polish(self.ui.mainTabWidget)
        return True

    def astrometryDispatch(self):
        """
        astrometryDispatch selects the type of device for environment measures and start / stop
        them.

        :return: true for test purpose
        """

        if self.ui.astrometryDevice.currentText() in self.app.astrometry.available:
            if self.ui.astrometryDevice.currentText() not in self.app.astrometry.binPath:
                self.app.message.emit('Astrometry not available', 2)
                self.changeStyleDynamic(self.ui.astrometryConnected, 'color', 'red')
                return False
            self.ui.astrometryDevice.setStyleSheet(self.BACK_GREEN)
            self.changeStyleDynamic(self.ui.astrometryConnected, 'color', 'green')
            self.app.message.emit('Astrometry enabled', 0)
        else:
            self.app.message.emit('Astrometry disabled', 0)
            self.changeStyleDynamic(self.ui.astrometryConnected, 'color', 'gray')
            self.ui.astrometryDevice.setStyleSheet(self.BACK_NORM)

        return True
