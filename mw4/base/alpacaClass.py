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
# local imports


class AlpacaClass(object):
    """
    the class AlpacaClass inherits all information and handling of alpaca devices
    this class will be only referenced from other classes and not directly used

        >>> a = AlpacaClass(
        >>>                  protocol='http:'
        >>>                  host=host,
        >>>                  deviceNumber=0,
        >>>                 )
    """

    __all__ = ['AlpacaClass']

    logger = logging.getLogger(__name__)

    CYCLE = 1000
    DEFAULT_API_VERSION = 1

    def __init__(self,
                 protocol='http:',
                 host=None,
                 deviceNumber=0,
                 app=None,
                 ):
        super().__init__()

        self.app = app
        self.protocol = protocol
        self.host = host
        self.deviceNumber = deviceNumber
        self.data = {}

        self.timeCycle = PyQt5.QtCore.QTimer()
        self.timeCycle.setSingleShot(False)
        self.timeCycle.timeout.connect(self.startRetry)

    def action(self, Action: str, *Parameters):
        """Access functionality beyond the built-in capabilities of the ASCOM device interfaces.

        Args:
            Action (str): A well known name that represents the action to be carried out.
            *Parameters: List of required parameters or empty if none are required.
        """
        return self._put("action", Action=Action, Parameters=Parameters)["Value"]

    def commandblind(self, Command: str, Raw: bool):
        """Transmit an arbitrary string to the device and does not wait for a response.
        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """
        self._put("commandblind", Command=Command, Raw=Raw)

    def commandbool(self, Command: str, Raw: bool):
        """Transmit an arbitrary string to the device and wait for a boolean response.

        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """
        return self._put("commandbool", Command=Command, Raw=Raw)["Value"]

    def commandstring(self, Command: str, Raw: bool):
        """Transmit an arbitrary string to the device and wait for a string response.
        Args:
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """
        return self._put("commandstring", Command=Command, Raw=Raw)["Value"]

    def connected(self, Connected: Optional[bool] = None):
        """Retrieve or set the connected state of the device.
        Args:
            Connected (bool): Set True to connect to device hardware.
                Set False to disconnect from device hardware.
                Set None to get connected state (default).

        """
        if Connected is None:
            return self._get("connected")
        self._put("connected", Connected=Connected)

    def description(self) -> str:
        """Get description of the device."""
        return self._get("name")

    def driverinfo(self) -> List[str]:
        """Get information of the device."""
        return [i.strip() for i in self._get("driverinfo").split(",")]

    def driverversion(self) -> str:
        """Get string containing only the major and minor version of the driver."""
        return self._get("driverversion")

    def interfaceversion(self) -> int:
        """ASCOM Device interface version number that this device supports."""
        return self._get("interfaceversion")

    def name(self) -> str:
        """Get name of the device."""
        return self._get("name")

    def supportedactions(self) -> List[str]:
        """Get list of action names supported by this driver."""
        return self._get("supportedactions")

    def _get(self, attribute: str, **data):
        """Send an HTTP GET request to an Alpaca server and check response for errors.
        Args:
            attribute (str): Attribute to get from server.
            **data: Data to send with request.

        """
        response = requests.get("%s/%s" % (self.base_url, attribute), data=data)
        self.__check_error(response)
        return response.json()["Value"]

    def _put(self, attribute: str, **data):
        """Send an HTTP PUT request to an Alpaca server and check response for errors.
        Args:
            attribute (str): Attribute to put to server.
            **data: Data to send with request.

        """
        response = requests.put("%s/%s" % (self.base_url, attribute), data=data)
        self.__check_error(response)
        return response.json()

    @staticmethod
    def __check_error(response: requests.Response):
        """Check response from Alpaca server for Errors.
        Args:
            response (Response): Response from Alpaca server to check.
        """
        j = response.json()
        if j["ErrorNumber"] != 0:
            self.logger.error(f'{j["ErrorNumber"]}, {j["ErrorMessage"]}')
        elif response.status_code == 400 or response.status_code == 500:
            self.logger.error(f'{j["Value"]}')