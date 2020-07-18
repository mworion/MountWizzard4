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
#
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
import PyQt5
from indibase import qtIndiBase

# local imports
from mw4.base.loggerMW import CustomLogger


class IndiClass(object):
    """
    the class indiClass inherits all information and handling of indi devices
    this class will be only referenced from other classes and not directly used

        >>> indi = IndiClass(app=None, data=None)
    """

    __all__ = ['IndiClass']

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    RETRY_DELAY = 1500
    NUMBER_RETRY = 5

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()

        self.app = app

        self.client = qtIndiBase.Client(host=None, threadPool=threadPool)
        self.name = ''
        self._host = ('localhost', 7624)
        self.data = data
        self.loadIndiConfig = False

        self.retryCounter = 0
        self.device = None
        self.showMessages = False

        self.timerRetry = PyQt5.QtCore.QTimer()
        self.timerRetry.setSingleShot(True)
        self.timerRetry.timeout.connect(self.startRetry)

        # link signals
        self.client.signals.newDevice.connect(self.newDevice)
        self.client.signals.removeDevice.connect(self.removeDevice)
        self.client.signals.newProperty.connect(self.connectDevice)
        self.client.signals.newNumber.connect(self.updateNumber)
        self.client.signals.defNumber.connect(self.updateNumber)
        self.client.signals.newSwitch.connect(self.updateSwitch)
        self.client.signals.defSwitch.connect(self.updateSwitch)
        self.client.signals.newText.connect(self.updateText)
        self.client.signals.defText.connect(self.updateText)
        self.client.signals.newLight.connect(self.updateLight)
        self.client.signals.defLight.connect(self.updateLight)
        self.client.signals.newBLOB.connect(self.updateBLOB)
        self.client.signals.defBLOB.connect(self.updateBLOB)
        self.client.signals.deviceConnected.connect(self.loadConfig)
        self.client.signals.deviceConnected.connect(self.setUpdateConfig)
        self.client.signals.serverConnected.connect(self.serverConnected)
        self.client.signals.serverDisconnected.connect(self.serverDisconnected)
        self.client.signals.newMessage.connect(self.updateMessage)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self.client.host = value

    def serverConnected(self):
        """
        serverConnected is called when the server signals the connection. if so, we would
        like to start watching the defined device. this will be triggered directly

        :return: success
        """

        if self.name:
            suc = self.client.watchDevice(self.name)
            self.log.info(f'INDI watch: {self.name}, watch: result:{suc}')
            return suc
        return False

    def serverDisconnected(self, devices):
        """

        :param devices:
        :return: true for test purpose
        """

        self.log.info(f'INDI server disconnected, devices: {devices}')
        return True

    def newDevice(self, deviceName):
        """
        newDevice is called whenever a new device entry is received in indi client. it
        adds the device if the name fits to the given name in configuration.

        :param deviceName:
        :return: true for test purpose
        """

        if deviceName == self.name:
            self.device = self.client.getDevice(deviceName)
            self.app.message.emit(f'INDI device found:   [{deviceName}]', 0)
        else:
            self.log.warning(f'INDI device snoop: {deviceName}')

        return True

    def removeDevice(self, deviceName):
        """
        removeDevice is called whenever a device is removed from indi client. it sets
        the device entry to None

        :param deviceName:
        :return: true for test purpose
        """

        if deviceName == self.name:
            self.app.message.emit(f'INDI removed device: [{deviceName}]', 0)
            self.device = None
            self.data.clear()
            return True
        else:
            return False

    def startRetry(self):
        """
        startRetry tries to connect the server a NUMBER_RETRY times, if necessary with a
        delay of RETRY_DELAY

        :return: True for test purpose
        """

        if not self.name:
            return False
        if self.data:
            return True

        self.retryCounter += 1
        suc = self.client.connectServer()

        if suc:
            return True

        self.log.info(f'Cannot start connection to: {self.name} retry: {self.retryCounter}')

        if self.retryCounter < self.NUMBER_RETRY:
            self.timerRetry.start(self.RETRY_DELAY)

        return True

    def startCommunication(self, loadConfig=False):
        """
        startCommunication adds a device on the watch list of the server.

        :param loadConfig:
        :return: success of reconnecting to server
        """

        self.loadIndiConfig = loadConfig
        self.retryCounter = 0
        self.data.clear()
        self.client.startTimers()
        suc = self.client.connectServer()

        if not suc:
            self.log.info(f'Cannot start connection to: {self.name} retry: {self.retryCounter}')
        else:
            self.timerRetry.start(self.RETRY_DELAY)

        return suc

    def stopCommunication(self):
        """
        stopCommunication adds a device on the watch list of the server.

        :return: success of reconnecting to server
        """

        self.client.stopTimers()
        suc = self.client.disconnectServer(self.name)
        self.name = ''
        return suc

    def connectDevice(self, deviceName, propertyName):
        """
        connectDevice is called when a new property is received and checks it against
        property CONNECTION. if this is there, we could check the connection state of
        a given device

        :param deviceName:
        :param propertyName:
        :return: success if device could connect
        """

        if propertyName != 'CONNECTION':
            return False

        suc = False
        if deviceName == self.name:
            suc = self.client.connectDevice(deviceName=deviceName)
        return suc

    def loadConfig(self, deviceName):
        """
        loadConfig send the command to the indi server to load the default config for
        the given device.

        :param deviceName:
        :return: success
        """

        if not self.loadIndiConfig:
            return False

        # setting a object name
        loadObject = self.device.getSwitch('CONFIG_PROCESS')
        loadObject['CONFIG_LOAD'] = True
        suc = self.client.sendNewSwitch(deviceName=deviceName,
                                        propertyName='CONFIG_PROCESS',
                                        elements=loadObject,
                                        )

        return suc

    def setUpdateConfig(self, deviceName):
        """
        setUpdateConfig does all things for initializing the devices when starting up.


        :param deviceName:
        :return: success
        """
        pass

    def updateNumber(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client. it runs
        through the device list and writes the number data to the according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getNumber(propertyName).items():
            key = propertyName + '.' + element
            self.data[key] = value

            print(self.name, key, value)

        return True

    def updateSwitch(self, deviceName, propertyName):
        """
        updateSwitch is called whenever a new switch is received in client. it runs
        through the device list and writes the switch data to the according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getSwitch(propertyName).items():
            key = propertyName + '.' + element
            self.data[key] = value

            # print(self.name, key, value)

        return True

    def updateText(self, deviceName, propertyName):
        """
        updateText is called whenever a new text is received in client. it runs
        through the device list and writes the text data to the according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getText(propertyName).items():
            key = propertyName + '.' + element
            self.data[key] = value

            # print(self.name, key, value)

        return True

    def updateLight(self, deviceName, propertyName):
        """
        updateLight is called whenever a new light is received in client. it runs
        through the device list and writes the light data to the according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """
        if self.device is None:
            return False
        if deviceName != self.name:
            return False

        for element, value in self.device.getLight(propertyName).items():
            key = propertyName + '.' + element
            self.data[key] = value

            # print(self.name, key, value)

        return True

    def updateBLOB(self, deviceName, propertyName):
        """
        updateBLOB is called whenever a new BLOB is received in client. it runs
        through the device list and writes the BLOB data to the according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """

        if self.device is None:
            return False
        if deviceName != self.name:
            return False

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

    def updateMessage(self, device, text):
        """
        message take a message send by indi device and emits them in the user message
        window as well.

        :param device: device name
        :param text: message received
        :return: success
        """

        if self.showMessages:
            if text.startswith('[WARNING]'):
                text = self.removePrefix(text, '[WARNING]')
                self.app.message.emit(f'INDI {device:15s} {text}', 0)
            elif text.startswith('[ERROR]'):
                text = self.removePrefix(text, '[ERROR]')
                self.app.message.emit(f'INDI {device:15s} {text}', 2)
            else:
                self.app.message.emit(f'INDI {device:15s} {text}', 0)
            return True
        return False
