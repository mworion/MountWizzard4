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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
from PyQt5.QtTest import QTest
from PyQt5.QtCore import QTimer

# local imports
from indibase import qtIndiBase


class IndiClass:
    """
    the class indiClass inherits all information and handling of indi devices
    this class will be only referenced from other classes and not directly used

        >>> indi = IndiClass(app=None, data=None)
    """

    __all__ = ['IndiClass']

    log = logging.getLogger(__name__)

    RETRY_DELAY = 1500
    NUMBER_RETRY = 5

    INDIGO = {
        # numbers
        'WEATHER_PARAMETERS.WEATHER_BAROMETER': 'WEATHER_PARAMETERS.WEATHER_PRESSURE',
        # SQM device
        'AUX_INFO.X_AUX_SKY_BRIGHTNESS': 'SKY_QUALITY.SKY_BRIGHTNESS',
        'AUX_INFO.X_AUX_SKY_TEMPERATURE': 'SKY_QUALITY.SKY_TEMPERATURE',
        # UPB device
        'AUX_INFO.X_AUX_AVERAGE': 'POWER_CONSUMPTION.CONSUMPTION_AVG_AMPS',
        'AUX_INFO.X_AUX_AMP_HOUR': 'POWER_CONSUMPTION.CONSUMPTION_AMP_HOURS',
        'AUX_INFO.X_AUX_WATT_HOUR': 'POWER_CONSUMPTION.CONSUMPTION_WATT_HOURS',
        'AUX_INFO.X_AUX_VOLTAGE': 'POWER_SENSORS.SENSOR_VOLTAGE',
        'AUX_INFO.X_AUX_CURRENT': 'POWER_SENSORS.SENSOR_CURRENT',
        'AUX_INFO.X_AUX_POWER_OUTLET': 'POWER_SENSORS.SENSOR_POWER',
        'AUX_POWER_OUTLET_CURRENT.OUTLET_1': 'POWER_CURRENT.POWER_CURRENT_1',
        'AUX_POWER_OUTLET_CURRENT.OUTLET_2': 'POWER_CURRENT.POWER_CURRENT_2',
        'AUX_POWER_OUTLET_CURRENT.OUTLET_3': 'POWER_CURRENT.POWER_CURRENT_3',
        'AUX_POWER_OUTLET_CURRENT.OUTLET_4': 'POWER_CURRENT.POWER_CURRENT_4',
        'AUX_HEATER_OUTLET_CURRENT.OUTLET_1': 'DEW_CURRENT.DEW_CURRENT_A',
        'AUX_HEATER_OUTLET_CURRENT.OUTLET_2': 'DEW_CURRENT.DEW_CURRENT_B',
        'AUX_HEATER_OUTLET_CURRENT.OUTLET_3': 'DEW_CURRENT.DEW_CURRENT_C',
        'AUX_HEATER_OUTLET.OUTLET_1': 'DEW_PWM.DEW_A',
        'AUX_HEATER_OUTLET.OUTLET_2': 'DEW_PWM.DEW_B',
        'AUX_HEATER_OUTLET.OUTLET_3': 'DEW_PWM.DEW_C',
        'X_AUX_VARIABLE_POWER_OUTLET.OUTLET_1': 'ADJUSTABLE_VOLTAGE.ADJUSTABLE_VOLTAGE_VALUE',
        # switches
        # UPB device
        'AUX_POWER_OUTLET.OUTLET_1': 'POWER_CONTROL.POWER_CONTROL_1',
        'AUX_POWER_OUTLET.OUTLET_2': 'POWER_CONTROL.POWER_CONTROL_2',
        'AUX_POWER_OUTLET.OUTLET_3': 'POWER_CONTROL.POWER_CONTROL_3',
        'AUX_POWER_OUTLET.OUTLET_4': 'POWER_CONTROL.POWER_CONTROL_4',
        'AUX_USB_PORT.PORT_1': 'USB_PORT_CONTROL.PORT_1',
        'AUX_USB_PORT.PORT_2': 'USB_PORT_CONTROL.PORT_2',
        'AUX_USB_PORT.PORT_3': 'USB_PORT_CONTROL.PORT_3',
        'AUX_USB_PORT.PORT_4': 'USB_PORT_CONTROL.PORT_4',
        'AUX_USB_PORT.PORT_5': 'USB_PORT_CONTROL.PORT_5',
        'AUX_USB_PORT.PORT_6': 'USB_PORT_CONTROL.PORT_6',
        'AUX_DEW_CONTROL.MANUAL': 'AUTO_DEW.INDI_DISABLED',
        'AUX_DEW_CONTROL.AUTOMATIC': 'AUTO_DEW.INDI_ENABLED',
        'X_AUX_REBOOT.REBOOT': 'REBOOT_DEVICE.REBOOT',
        # text
        # UPB device
        'X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_1': 'POWER_CONTROL_LABEL.POWER_LABEL_1',
        'X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_2': 'POWER_CONTROL_LABEL.POWER_LABEL_2',
        'X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_3': 'POWER_CONTROL_LABEL.POWER_LABEL_3',
        'X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_4': 'POWER_CONTROL_LABEL.POWER_LABEL_4',
    }

    INDI = {y: x for x, y in INDIGO.items()}

    INDI_TYPES = {
        'telescope': (1 << 0),
        'camera': (1 << 1),
        'guider': (1 << 2),
        'focuser': (1 << 3),
        'filterwheel': (1 << 4),
        'dome': (1 << 5),
        'observingconditions': (1 << 7) | (1 << 15),
        'skymeter': (1 << 15) | (1 << 19),
        'covercalibrator': (1 << 9) | (1 << 10),
        'switch': (1 << 7) | (1 << 3) | (1 << 15) | (1 << 18),
    }

    def __init__(self, app=None, data=None, threadPool=None):
        super().__init__()

        self.app = app
        self.data = data
        self.client = qtIndiBase.Client(host=None, threadPool=threadPool)
        self.deviceName = ''
        self.device = None
        self.deviceConnected = False
        self._hostaddress = None
        self._host = None
        self._port = None
        self.retryCounter = 0
        self.discoverType = None
        self.discoverList = None
        self.loadIndiConfig = False
        self.isINDIGO = False
        self.showMessages = False

        self.defaultConfig = {
            'indi': {
                'deviceName': '',
                'deviceList': [],
                'hostaddress': 'localhost',
                'port': 7624,
                'loadConfig': False,
                'messages': False,
            }
        }

        self.timerRetry = QTimer()
        self.timerRetry.setSingleShot(True)
        self.timerRetry.timeout.connect(self.startRetry)

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

    @property
    def hostaddress(self):
        return self._hostaddress

    @hostaddress.setter
    def hostaddress(self, value):
        self._hostaddress = value
        self.client.host = (self._hostaddress, self._port)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = int(value)
        self.client.host = (self._hostaddress, self._port)

    def serverConnected(self):
        """
        serverConnected is called when the server signals the connection. if
        so, we would like to start watching the defined device. this will be
        triggered directly

        :return: success
        """
        if self.deviceName:
            suc = self.client.watchDevice(self.deviceName)
            self.log.debug(f'INDI watch: [{self.deviceName}], result: [{suc}]')
            return suc
        return False

    def serverDisconnected(self, devices):
        """
        :param devices:
        :return: true for test purpose
        """
        t = f'INDI server for [{self.deviceName}] disconnected, '
        t += f'related devices: {devices.keys()}'
        self.log.debug(t)
        return True

    def newDevice(self, deviceName):
        """
        newDevice is called whenever a new device entry is received in indi
        client. it adds the device if the name fits to the given name in
        configuration.

        :param deviceName:
        :return: true for test purpose
        """
        if deviceName == self.deviceName:
            self.device = self.client.getDevice(deviceName)
            self.app.message.emit(f'INDI device found:   [{deviceName}]', 0)
        else:
            self.log.info(f'INDI device snoop: [{deviceName}]')
        return True

    def removeDevice(self, deviceName):
        """
        removeDevice is called whenever a device is removed from indi client.
        it sets the device entry to None

        :param deviceName:
        :return: true for test purpose
        """
        if deviceName == self.deviceName:
            self.app.message.emit(f'INDI removed device: [{deviceName}]', 0)
            self.device = None
            self.data.clear()
            return True

        else:
            return False

    def startRetry(self):
        """
        startRetry tries to connect the server a NUMBER_RETRY times, if
        necessary with a delay of RETRY_DELAY

        :return: True for test purpose
        """
        if not self.deviceName:
            return False
        if self.data:
            self.deviceConnected = True
            return True

        self.retryCounter += 1
        suc = self.client.connectServer()
        if suc:
            return True

        t = f'Cannot start: [{self.deviceName}] retries: [{self.retryCounter}]'
        self.log.debug(t)
        if self.retryCounter < self.NUMBER_RETRY:
            self.timerRetry.start(self.RETRY_DELAY)
        return False

    def startCommunication(self, loadConfig=False):
        """
        :param loadConfig:
        :return: success of reconnecting to server
        """
        self.loadIndiConfig = loadConfig
        self.retryCounter = 0
        self.client.startTimers()
        suc = self.client.connectServer()
        if not suc:
            t = f'Cannot start: [{self.deviceName}] retries: [{self.retryCounter}]'
            self.log.debug(t)
        else:
            self.timerRetry.start(self.RETRY_DELAY)
        return suc

    def stopCommunication(self):
        """
        :return: success of reconnecting to server
        """
        self.client.stopTimers()
        suc = self.client.disconnectServer(self.deviceName)
        self.deviceName = ''
        self.deviceConnected = False
        return suc

    def connectDevice(self, deviceName, propertyName):
        """
        connectDevice is called when a new property is received and checks it
        against property CONNECTION. if this is there, we could check the
        connection state of a given device

        :param deviceName:
        :param propertyName:
        :return: success if device could connect
        """
        if propertyName != 'CONNECTION':
            return False

        suc = False
        if deviceName == self.deviceName:
            suc = self.client.connectDevice(deviceName=deviceName)
        return suc

    def loadConfig(self, deviceName):
        """
        loadConfig send the command to the indi server to load the default
        config for the given device.

        :param deviceName:
        :return: success
        """
        if not self.loadIndiConfig:
            return False

        loadObject = self.device.getSwitch('CONFIG_PROCESS')
        loadObject['CONFIG_LOAD'] = True
        suc = self.client.sendNewSwitch(deviceName=deviceName,
                                        propertyName='CONFIG_PROCESS',
                                        elements=loadObject,
                                        )
        return suc

    def setUpdateConfig(self, deviceName):
        """
        :param deviceName:
        :return: success
        """
        pass

    def convertIndigoProperty(self, key):
        """
        :param key:
        :return:
        """
        if key in self.INDIGO:
            key = self.INDIGO.get(key)
        return key

    def updateNumber(self, deviceName, propertyName):
        """
        updateNumber is called whenever a new number is received in client.
        it runs through the device list and writes the number data to the
        according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """
        if self.device is None:
            return False
        if deviceName != self.deviceName:
            return False

        for element, value in self.device.getNumber(propertyName).items():
            key = propertyName + '.' + element
            # print('number', self.deviceName, key, value)
            key = self.convertIndigoProperty(key)
            self.data[key] = float(value)

        return True

    def updateSwitch(self, deviceName, propertyName):
        """
        updateSwitch is called whenever a new switch is received in client.
        it runs through the device list and writes the switch data to the
        according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """
        if self.device is None:
            return False
        if deviceName != self.deviceName:
            return False

        for element, value in self.device.getSwitch(propertyName).items():
            key = propertyName + '.' + element
            # todo: is that the item which tells me it's an indigo server ?
            if propertyName == 'PROFILE':
                self.isINDIGO = True
            # print('switch', self.deviceName, key, value)
            key = self.convertIndigoProperty(key)
            self.data[key] = value == 'On'

        return True

    def updateText(self, deviceName, propertyName):
        """
        updateText is called whenever a new text is received in client.
        it runs through the device list and writes the text data to the according
        locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """
        if self.device is None:
            return False
        if deviceName != self.deviceName:
            return False

        for element, value in self.device.getText(propertyName).items():
            key = propertyName + '.' + element
            # print('text  ', self.deviceName, key, value)
            key = self.convertIndigoProperty(key)
            self.data[key] = value

        return True

    def updateLight(self, deviceName, propertyName):
        """
        updateLight is called whenever a new light is received in client.
        it runs through the device list and writes the light data to the
        according locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """
        if self.device is None:
            return False
        if deviceName != self.deviceName:
            return False

        for element, value in self.device.getLight(propertyName).items():
            key = propertyName + '.' + element
            # print('light ', self.deviceName, key, value)
            key = self.convertIndigoProperty(key)
            self.data[key] = value

        return True

    def updateBLOB(self, deviceName, propertyName):
        """
        updateBLOB is called whenever a new BLOB is received in client.
        it runs through the device list and writes the BLOB data to the according
        locations.

        :param deviceName:
        :param propertyName:
        :return: success
        """
        if self.device is None:
            return False
        if deviceName != self.deviceName:
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
        message take a message send by indi device and emits them in the user
        message window as well.

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

    def addDiscoveredDevice(self, deviceName, propertyName):
        """
        addDevicesWithType gety called whenever a new device send out text
        messages. than it checks, if the device type fits to the search type
        desired. if they match, the device name is added to the list.

        unfortunately the indi definitions are not well defined. so for example
        SQM reports only aux general. this is value '0'. So i have to treat all
        devices reporting device type '0' as devices which could be used for
        everything.

        :param deviceName:
        :param propertyName:
        :return: success
        """
        if propertyName != 'DRIVER_INFO':
            return False

        device = self.client.devices.get(deviceName)
        if not device:
            return False

        interface = device.getText(propertyName).get('DRIVER_INTERFACE', None)
        if interface is None:
            return False
        if interface == '0':
            interface = 0xffff
        if self.discoverType is None:
            return False

        self.log.debug(f'Found: [{deviceName}], interface: [{interface}]')
        interface = int(interface)
        if interface & self.discoverType:
            self.discoverList.append(deviceName)
        return True

    def discoverDevices(self, deviceType=''):
        """
        discoverDevices implements a discover for devices of a certain device
        type. it is called from a button press and checks which button it was.
        after that for the right device it collects all necessary data for host
        value, instantiates an INDI client and watches for all devices connected
        to this server. Than it connects a subroutine for collecting the right
        device names and waits a certain amount of time. the data collection
        takes place as long as the model dialog is open. when the user closes
        this dialog, the collected data is written to the drop down list.

        :param deviceType: device type of discovered indi devices
        :return: success
        """
        self.discoverList = list()
        self.discoverType = self.INDI_TYPES.get(deviceType, 0)
        self.client.signals.defText.connect(self.addDiscoveredDevice)
        self.client.connectServer()
        self.client.watchDevice()
        QTest.qWait(2000)
        self.client.signals.defText.disconnect(self.addDiscoveredDevice)
        self.client.disconnectServer()
        return self.discoverList
