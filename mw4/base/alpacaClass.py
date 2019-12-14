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
import logging
# external packages
import PyQt5.QtCore
import requests
# local imports
from mw4.base import tpool


class AlpacaSignals(PyQt5.QtCore.QObject):

    """
    The AlpacaSignals class offers a list of signals to be used and instantiated by
    the Alpaca class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['AlpacaSignals']

    serverConnected = PyQt5.QtCore.pyqtSignal()
    serverDisconnected = PyQt5.QtCore.pyqtSignal()
    deviceConnected = PyQt5.QtCore.pyqtSignal()
    deviceDisconnected = PyQt5.QtCore.pyqtSignal()


class AlpacaClass(object):
    """
    the class AlpacaClass inherits all information and handling of alpaca devices
    this class will be only referenced from other classes and not directly used

        >>> a = AlpacaClass(
        >>>         protocol='http',
        >>>         host=('localhost', 11111),
        >>>         deviceNumber=0,
        >>>         deviceType='',
        >>>         apiVersion=1,
        >>>         app=None,
        >>>                 )
    """

    __all__ = ['AlpacaClass']

    logger = logging.getLogger(__name__)

    CYCLE = 1000

    def __init__(self,
                 protocol='http',
                 host=('localhost', 11111),
                 deviceNumber=0,
                 deviceType='',
                 apiVersion=1,
                 app=None,
                 ):
        super().__init__()

        self.app = app
        self.threadPool = threadPool
        self.baseUrl = 'localhost'
        self.protocol = protocol
        self.deviceNumber = deviceNumber
        self.apiVersion = apiVersion
        self.deviceType = deviceType
        self.host = host
        self.signals = AlpacaSignals()

        self.data = {}
        self.deviceConnected = False
        self.serverConnected = False

        self.timeCycle = PyQt5.QtCore.QTimer()
        self.timeCycle.setSingleShot(False)
        self.timeCycle.timeout.connect(self.cycleAlpaca)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self.baseUrl = self.generateBaseUrl()

    def generateBaseUrl(self):
        """
        :return: value for base url
        """

        val = '{0}://{1}:{2}/api/v{3}/{4}/{5}'.format(
            self.protocol,
            self.host[0],
            self.host[1],
            self.apiVersion,
            self.deviceType,
            self.deviceNumber,
        )
        return val

    def get(self, attribute: str, **data):
        """
        Send an HTTP GET request to an Alpaca server and check response for errors.
        Args:
            attribute (str): Attribute to get from server.
            **data: Data to send with request.

        """
        response = requests.get(f'{self.baseUrl}/{attribute}', data=data, timeout=3)

        if response.status_code == 400 or response.status_code == 500:
            self.logger.error(f'{response.text}')
            return None

        response = response.json()

        if response['ErrorNumber'] != 0:
            self.logger.error(f'{response["ErrorNumber"]}, {response["ErrorMessage"]}')
            return None

        return response['Value']

    def put(self, attribute: str, **data):
        """
        Send an HTTP PUT request to an Alpaca server and check response for errors.
        Args:
            attribute (str): Attribute to put to server.
            **data: Data to send with request.

        """
        response = requests.put(f'{self.baseUrl}/{attribute}', data=data, timeout=3)

        if response.status_code == 400 or response.status_code == 500:
            self.logger.error(f'{response.text}')
            return {}

        response = response.json()

        if response['ErrorNumber'] != 0:
            self.logger.error(f'{response["ErrorNumber"]}, {response["ErrorMessage"]}')
            return {}

        return response

    def action(self, Action: str, *Parameters):
        """
        Access functionality beyond the built-in capabilities of the ASCOM device interfaces.

        Args:
            Action (str): A well known name that represents the action to be carried out.
            *Parameters: List of required parameters or empty if none are required.
        """
        return self.put('action', Action=Action, Parameters=Parameters)

    def commandblind(self, Command, Raw):
        """
        Transmit an arbitrary string to the device and does not wait for a response.
        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """
        self.put('commandblind', Command=Command, Raw=Raw)

    def commandbool(self, Command, Raw):
        """
        Transmit an arbitrary string to the device and wait for a boolean response.

        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """
        return self.put('commandbool', Command=Command, Raw=Raw)

    def commandstring(self, Command, Raw):
        """
        Transmit an arbitrary string to the device and wait for a string response.
        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """
        return self.put('commandstring', Command=Command, Raw=Raw)

    def connected(self, Connected=None):
        """
        Retrieve or set the connected state of the device.
        Args:
            Connected (bool): Set True to connect to device hardware.
                Set False to disconnect from device hardware.
                Set None to get connected state (default).

        """
        if Connected is None:
            return self.get('connected')
        self.put('connected', Connected=Connected)

    def description(self):
        """
        Get description of the device.
        """
        return self.get('name')

    def driverInfo(self):
        """
        Get information of the device.
        """
        val = self.get('driverinfo')

        if val is None:
            return ''

        return [i.strip() for i in val.split(',')]

    def driverVersion(self):
        """
        Get string containing only the major and minor version of the driver.
        """
        return self.get('driverversion')

    def interfaceVersion(self):
        """
        ASCOM Device interface version number that this device supports.
        """
        return self.get('interfaceversion')

    def name(self):
        """
        Get name of the device.
        """
        return self.get('name')

    def supportedActions(self):
        """
        Get list of action names supported by this driver.
        """
        return self.get('supportedactions')

    def cycleAlpaca(self):
        """

        :return: true for test purpose
        """

        return True

    def getInitialConfig(self):
        """

        :return: success of reconnecting to server
        """
        self.connected(Connected=True)
        suc = self.connected()

        if not suc:
            return False

        if not self.serverConnected:
            self.serverConnected = True
            self.signals.serverConnected.emit()

        if not self.deviceConnected:
            self.deviceConnected = True
            self.signals.deviceConnected.emit()

        self.data['DRIVER_INFO.DRIVER_NAME'] = self.name()
        self.data['DRIVER_INFO.DRIVER_VERSION'] = self.driverVersion()
        self.data['DRIVER_INFO.DRIVER_EXEC'] = self.driverInfo()

        return True

    def startCommunication(self):
        """
        startCommunication adds a device on the watch list of the server.

        :return: success of reconnecting to server
        """

        suc = self.getInitialConfig()
        if not suc:
            self.logger.info(f'Cannot start connection to: {self.deviceType}')
        else:
            self.timeCycle.start(self.CYCLE)

        return suc

    def stopCommunication(self):
        """
        stopCommunication adds a device on the watch list of the server.

        :return: true for test purpose
        """

        self.connected(Connected=False)
        self.deviceConnected = False
        self.signals.deviceDisconnected.emit()
        self.timeCycle.stop()

        return True


if __name__ == '__main__':
    import time

    a = AlpacaClass(
                    protocol='http',
                    host=('mw-develop.fritz.box', 11111),
                    apiVersion=1,
                    deviceType='dome',
                    deviceNumber=0,
    )

    start = time.time()

    print('start', a.startCommunication())
    print(a.data)
    print('stop', a.stopCommunication())

    print(time.time() - start)
