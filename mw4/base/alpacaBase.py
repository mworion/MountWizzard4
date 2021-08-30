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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import datetime
import uuid
from dateutil.parser import parser

# external packages
import requests

# local imports
from base.driverDataClass import Signals


class AlpacaBase(Signals):
    """
    the class AlpacaBase inherits all information and handling of alpaca devices
    this class will be only referenced from other classes and will be not used
    directly

        >>> a = AlpacaBase()
    """

    __all__ = ['AlpacaBase']

    log = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

        self.signals = Signals()

        self.protocol = 'http'
        self.host = ('localhost', 11111)
        self.apiVersion = 1
        self.deviceName = ''
        self.deviceType = ''
        self.number = 0

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
            self.number,
        )
        return val

    @property
    def baseUrl(self):
        return self.generateBaseUrl()

    @property
    def deviceName(self):
        return self._deviceName

    @deviceName.setter
    def deviceName(self, value):
        self._deviceName = value
        valueSplit = value.split(':')
        if len(valueSplit) != 3:
            return
        self.deviceType = valueSplit[1].strip()
        self.number = valueSplit[2].strip()
        self.number = int(self.number)

    def discoverAPIVersion(self):
        """

        :return:
        """

        self.log.trace('get api version')

        url = '{0}://{1}:{2}/management/apiversions'.format(
            self.protocol,
            self.host[0],
            self.host[1],
        )

        try:
            response = requests.get(url, timeout=5)

        except requests.exceptions.Timeout:
            self.log.info('timeout')
            return None

        except requests.exceptions.ConnectionError:
            self.log.debug('[connection error')
            return None

        except Exception as e:
            self.log.critical(f'[error in request: {e}')
            return None

        if response.status_code == 400 or response.status_code == 500:
            self.log.debug(f'{response.text}')
            return None

        response = response.json()
        if response['ErrorNumber'] != 0:
            self.log.warning(f'{response} err:{response["ErrorNumber"]}'
                             f',{response["ErrorMessage"]}')
            return None

        self.log.trace(f'[response:{response}')
        return response['Value']

    def discoverDevices(self):
        """

        :return:
        """
        url = '{0}://{1}:{2}/management/v{3}/configureddevices'.format(
            self.protocol,
            self.host[0],
            self.host[1],
            self.apiVersion,
        )

        try:
            response = requests.get(url, timeout=10)

        except requests.exceptions.Timeout:
            self.log.info('timeout')
            return None

        except requests.exceptions.ConnectionError:
            self.log.debug('[connection error')
            return None

        except Exception as e:
            self.log.critical(f'[error in request: {e}')
            return None

        if response.status_code == 400 or response.status_code == 500:
            self.log.debug(f'{response.text}')
            return None

        response = response.json()

        if response['ErrorNumber'] != 0:
            self.log.warning(f'{response} err:{response["ErrorNumber"]}'
                             f',{response["ErrorMessage"]}')
            return None

        self.log.trace(f'[response:{response}')
        return response['Value']

    def get(self, attr: str, **data):
        """
        Send an HTTP GET request to an Alpaca server and check response for errors.
        In addition a unique Transaction ID is generated, to verify which send /
        response pair belongs together.

        :param
            attr (str): attr to get from server.
            **data: Data to send with request.

        """
        if not self.deviceName:
            return None

        uid = uuid.uuid4().int % 2**32
        data['ClientTransactionID'] = uid

        self.log.trace(f'[{uid:10d}] {self.baseUrl}/{attr}], data:[{data}]')

        try:
            response = requests.get(f'{self.baseUrl}/{attr}', params=data, timeout=10)

        except requests.exceptions.Timeout:
            self.log.info(f'[{uid:10d}] timeout')
            return None

        except requests.exceptions.ConnectionError:
            self.log.debug(f'[{uid:10d}] connection error')
            return None

        except Exception as e:
            self.log.critical(f'[{uid:10d}] error in request: {e}')
            return None

        if response.status_code == 400 or response.status_code == 500:
            self.log.debug(f'{response.text}')
            return None

        response = response.json()

        if response['ErrorNumber'] != 0:
            self.log.debug(f'{response} err:{response["ErrorNumber"]}'
                           f',{response["ErrorMessage"]}')
            return None

        if attr != 'imagearray':
            self.log.trace(f'[{uid:10d}] response:{response}')

        return response['Value']

    def put(self, attr: str, **data):
        """
        Send an HTTP PUT request to an Alpaca server and check response for errors.
        In addition a unique Transaction ID is generated, to verify which send /
        response pair belongs together.

        :param
            attr (str): attr to put to server.
            **data: Data to send with request.

        """
        if not self.deviceName:
            return None

        uid = uuid.uuid4().int % 2**32
        data['ClientTransactionID'] = uid

        self.log.trace(f'[{uid:08d}] {self.baseUrl}, attr:[{attr}]')

        try:
            response = requests.put(f'{self.baseUrl}/{attr}', data=data, timeout=10)

        except requests.exceptions.Timeout:
            self.log.info(f'[{uid:10d}] timeout')
            return None

        except requests.exceptions.ConnectionError:
            self.log.debug(f'[{uid:10d}] connection error')
            return None

        except Exception as e:
            self.log.critical(f'[{uid:10d}] Error in request: {e}')
            return None

        if response.status_code == 400 or response.status_code == 500:
            self.log.debug(f'[{uid:10d}] {response.text}')
            return None

        response = response.json()

        if response['ErrorNumber'] != 0:
            self.log.warning(f'err:{response["ErrorNumber"]},{response["ErrorMessage"]}')
            return None

        self.log.trace(f'[{uid:10d}] response:{response}')
        return response

    def action(self, Action: str, *Parameters):
        """
        Access functionality beyond the built-in capabilities of the ASCOM device interfaces.

        :param
            Action (str): A well known name that represents the action to be carried out.
            *Parameters: List of required parameters or empty if none are required.
        """

        return self.put('action', Action=Action, Parameters=Parameters)

    def commandblind(self, Command, Raw):
        """
        Transmit an arbitrary string to the device and does not wait for a response.
        :param
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """

        self.put('commandblind', Command=Command, Raw=Raw)

    def commandbool(self, Command, Raw):
        """
        Transmit an arbitrary string to the device and wait for a boolean response.

        :param
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """

        return self.put('commandbool', Command=Command, Raw=Raw)

    def commandstring(self, Command, Raw):
        """
        Transmit an arbitrary string to the device and wait for a string response.
        :param
            Command (str): The literal command string to be transmitted.
            Raw (bool): If true, command is transmitted 'as-is'.
                If false, then protocol framing characters may be added prior to
                transmission.
        """

        return self.put('commandstring', Command=Command, Raw=Raw)

    def connected(self, Connected=None):
        """
        Retrieve or set the connected state of the device.
        :param
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

        if not val:
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

    def nameDevice(self):
        """
        Get name of the device.
        """
        return self.get('name')

    def supportedActions(self):
        """
        Get list of action names supported by this driver.
        """

        return self.get('supportedactions')


class Switch(AlpacaBase):
    """
    Switch specific methods.
    """

    __all__ = ['Switch']

    def maxswitch(self):
        """
        Count of switch devices managed by this driver.
        :return:
            Number of switch devices managed by this driver. Devices are numbered from 0
            to MaxSwitch - 1.
        """

        return self.get("maxswitch")

    def canwrite(self, Id=0):
        """
        Indicate whether the specified switch device can be written to.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.
        :return:
            Whether the specified switch device can be written to, default true. This is
            false if the device cannot be written to, for example a limit switch or a
            sensor.
        """

        return self.get("canwrite", Id=Id)

    def getswitch(self, Id=0):
        """
        Return the state of switch device id as a boolean.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param: Id (int: The device number.

        :return:
            State of switch device id as a boolean.
        """

        return self.get("getswitch", Id=Id)

    def getswitchdescription(self, Id=0):
        """
        Get the description of the specified switch device.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.

        :return:
            Description of the specified switch device.
        """

        return self.get("getswitchdescription", Id=Id)

    def getswitchname(self, Id=0):
        """
        Get the name of the specified switch device.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.

        :return:
            Name of the specified switch device.
        """

        return self.get("getswitchname", Id=Id)

    def getswitchvalue(self, Id=0):
        """
        Get the value of the specified switch device as a double.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.

        :return:
            Value of the specified switch device.
        """

        return self.get("getswitchvalue", Id=Id)

    def minswitchvalue(self, Id=0):
        """
        Get the minimum value of the specified switch device as a double.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.

        :return:
            Minimum value of the specified switch device as a double.
        """

        return self.get("minswitchvalue", Id=Id)

    def setswitch(self, Id: int, State: bool):
        """
        Set a switch controller device to the specified state, True or False.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.
            State (bool): The required control state (True or False).
        """

        self.put("setswitch", Id=Id, State=State)

    def setswitchname(self, Id: int, Name: str):
        """
        Set a switch device name to the specified value.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.
            Name (str): The name of the device.
        """

        self.put("setswitchname", Id=Id, Name=Name)

    def setswitchvalue(self, Id: int, Value):
        """
        Set a switch device value to the specified value.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.
            Value (float): Value to be set, between MinSwitchValue and MaxSwitchValue.
        """

        self.put("setswitchvalue", Id=Id, Value=Value)

    def switchstep(self, Id=0):
        """
        Return the step size that this device supports.
        Return the step size that this device supports (the difference between
        successive values of the device).
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        :param
            Id (int): The device number.

        :return:
            Maximum value of the specified switch device as a double.
        """

        return self.get("switchstep", Id=Id)


class SafetyMonitor(AlpacaBase):
    """
    Safety monitor specific methods.
    """

    __all__ = ['SafetyMonitor']

    def issafe(self):
        """
        Indicate whether the monitored state is safe for use.
        :return:
            True if the state is safe, False if it is unsafe.
        """

        return self.get("issafe")


class Dome(AlpacaBase):
    """
    Dome specific methods.
    """

    __all__ = ['Dome']

    def altitude(self):
        """
        Dome altitude.
        :return:
            Dome altitude (degrees, horizon zero and increasing positive to 90 zenith).
        """

        return self.get("altitude")

    def athome(self):
        """
        Indicate whether the dome is in the home position.
        Notes:
            This is normally used following a findhome() operation. The value is reset
            with any azimuth slew operation that moves the dome away from the home
            position. athome() may also become true during normal slew operations, if the
            dome passes through the home position and the dome controller hardware is
            capable of detecting that; or at the end of a slew operation if the dome
            comes to rest at the home position.
        :return:
            True if dome is in the home position.
        """

        return self.get("athome")

    def atpark(self):
        """
        Indicate whether the telescope is at the park position.
        Notes:
            Set only following a park() operation and reset with any slew operation.
        :return:
            True if the dome is in the programmed park position.
        """

        return self.get("atpark")

    def azimuth(self):
        """
        Dome azimuth.
        :return:
            Dome azimuth (degrees, North zero and increasing clockwise, i.e., 90 East,
            180 South, 270 West).
        """

        return self.get("azimuth")

    def canfindhome(self):
        """
        Indicate whether the dome can find the home position.
        :return:
            True if the dome can move to the home position.
        """

        return self.get("canfindhome")

    def canpark(self):
        """
        Indicate whether the dome can be parked.
        :return:
            True if the dome is capable of programmed parking (park() method).
        """

        return self.get("canpark")

    def cansetaltitude(self):
        """
        Indicate whether the dome altitude can be set.
        :return:
            True if driver is capable of setting the dome altitude.
        """

        return self.get("cansetaltitude")

    def cansetazimuth(self):
        """
        Indicate whether the dome azimuth can be set.
        :return:
            True if driver is capable of setting the dome azimuth.
        """

        return self.get("cansetazimuth")

    def cansetpark(self):
        """
        Indicate whether the dome park position can be set.
        :return:
            True if driver is capable of setting the dome park position.
        """

        return self.get("cansetpark")

    def cansetshutter(self):
        """
        Indicate whether the dome shutter can be opened.
        :return:
            True if driver is capable of automatically operating shutter.
        """

        return self.get("cansetshutter")

    def canslave(self):
        """
        Indicate whether the dome supports slaving to a telescope.
        :return:
            True if driver is capable of slaving to a telescope.
        """

        return self.get("canslave")

    def cansyncazimuth(self):
        """
        Indicate whether the dome azimuth position can be synched.
        Notes:
            True if driver is capable of synchronizing the dome azimuth position using
            the synctoazimuth(float) method.

        :return:
            True or False value.
        """

        return self.get("cansyncazimuth")

    def shutterstatus(self):
        """
        Status of the dome shutter or roll-off roof.
        Notes:
            0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error.

        :return:
            Status of the dome shutter or roll-off roof.
        """

        return self.get("shutterstatus")

    def slaved(self, Slaved=None):
        """
        Set or indicate whether the dome is slaved to the telescope.

        :return:
            True or False value in not set.
        """

        if Slaved is None:
            return self.get("slaved")

        self.put("slaved", Slaved=Slaved)

    def slewing(self):
        """
        Indicate whether the any part of the dome is moving.
        Notes:
            True if any part of the dome is currently moving, False if all dome
            components are steady.

        Return:
            True or False value.
        """

        return self.get("slewing")

    def abortslew(self):
        """
        Immediately cancel current dome operation.
        Notes:
            Calling this method will immediately disable hardware slewing (Slaved will
            become False).
        """

        self.put("abortslew")

    def closeshutter(self):
        """
        Close the shutter or otherwise shield telescope from the sky.
        """

        self.put("closeshutter")

    def findhome(self):
        """
        Start operation to search for the dome home position.
        Notes:
            After home position is established initializes azimuth to the default value
            and sets the athome flag.
        """

        self.put("findhome")

    def openshutter(self):
        """
        Open shutter or otherwise expose telescope to the sky.
        """

        self.put("openshutter")

    def park(self):
        """
        Rotate dome in azimuth to park position.
        Notes:
            After assuming programmed park position, sets atpark flag.
        """

        self.put("park")

    def setpark(self):
        """
        Set current azimuth, altitude position of dome to be the park position.
        """

        self.put("setpark")

    def slewtoaltitude(self, Altitude):
        """
        Slew the dome to the given altitude position.
        """

        self.put("slewtoaltitude", Altitude=Altitude)

    def slewtoazimuth(self, Azimuth):
        """
        Slew the dome to the given azimuth position.

        :param
            Azimuth (float): Target dome azimuth (degrees, North zero and increasing
                clockwise. i.e., 90 East, 180 South, 270 West).
        """

        self.put("slewtoazimuth", Azimuth=Azimuth)

    def synctoazimuth(self, Azimuth):
        """
        Synchronize the current position of the dome to the given azimuth.
        :param
            Azimuth (float): Target dome azimuth (degrees, North zero and increasing
                clockwise. i.e., 90 East, 180 South, 270 West).
        """

        self.put("synctoazimuth", Azimuth=Azimuth)


class Camera(AlpacaBase):
    """
    Camera specific methods.
    """

    __all__ = ['Camera']

    def bayeroffsetx(self):
        """
        Return the X offset of the Bayer matrix, as defined in SensorType.
        """

        return self.get("bayeroffsetx")

    def bayeroffsety(self):
        """
        Return the Y offset of the Bayer matrix, as defined in SensorType.
        """

        return self.get("bayeroffsety")

    def binx(self, BinX=None):
        """
        Set or return the binning factor for the X axis.
        :param
            BinX (int): The X binning value.

        :return:
            Binning factor for the X axis.
        """

        if BinX is None:
            return self.get("binx")

        self.put("binx", BinX=BinX)

    def biny(self, BinY=None):
        """
        Set or return the binning factor for the Y axis.
        :param
            BinY (int): The Y binning value.

        :return:
            Binning factor for the Y axis.
        """

        if BinY is None:
            return self.get("biny")

        self.put("biny", BinY=BinY)

    def camerastate(self):
        """
        Return the camera operational state.
        Notes:
            0 = CameraIdle, 1 = CameraWaiting, 2 = CameraExposing,
            3 = CameraReading, 4 = CameraDownload, 5 = CameraError.

        :return:
            Current camera operational state as an integer.
        """

        return self.get("camerastate")

    def cameraxsize(self):
        """
        Return the width of the CCD camera chip.
        """

        return self.get("cameraxsize")

    def cameraysize(self):
        """
        Return the height of the CCD camera chip.
        """

        return self.get("cameraysize")

    def canabortexposure(self):
        """
        Indicate whether the camera can abort exposures.
        """

        return self.get("canabortexposure")

    def canasymmetricbin(self):
        """
        Indicate whether the camera supports asymmetric binning.
        """

        return self.get("canasymmetricbin")

    def canfastreadout(self):
        """
        Indicate whether the camera has a fast readout mode.
        """

        return self.get("canfastreadout")

    def cangetcoolerpower(self):
        """
        Indicate whether the camera's cooler power setting can be read.
        """

        return self.get("cangetcoolerpower")

    def canpulseguide(self):
        """
        Indicate whether this camera supports pulse guiding.
        """

        return self.get("canpulseguide")

    def cansetccdtemperature(self):
        """
        Indicate whether this camera supports setting the CCD temperature.
        """

        return self.get("cansetccdtemperature")

    def canstopexposure(self):
        """
        Indicate whether this camera can stop an exposure that is in progress.
        """

        return self.get("canstopexposure")

    def ccdtemperature(self):
        """
        Return the current CCD temperature in degrees Celsius.
        """

        return self.get("ccdtemperature")

    def cooleron(self, CoolerOn=None):
        """
        Turn the camera cooler on and off or return the current cooler on/off state.
        Notes:
            True = cooler on, False = cooler off.
        :param
            CoolerOn (bool): Cooler state.
        :return:
            Current cooler on/off state.
        """

        if CoolerOn is None:
            return self.get("cooleron")

        self.put("cooleron", CoolerOn=CoolerOn)

    def coolerpower(self):
        """
        Return the present cooler power level, in percent.
        """

        return self.get("coolerpower")

    def electronsperadu(self):
        """
        Return the gain of the camera in photoelectrons per A/D unit.
        """

        return self.get("electronsperadu")

    def exposuremax(self):
        """
        Return the maximum exposure time supported by StartExposure.
        """

        return self.get("exposuremax")

    def exposuremin(self):
        """
        Return the minimum exposure time supported by StartExposure.
        """

        return self.get("exposuremin")

    def exposureresolution(self):
        """
        Return the smallest increment in exposure time supported by StartExposure.
        """

        return self.get("exposureresolution")

    def fastreadout(self, FastReadout=None):
        """
        Set or return whether Fast Readout Mode is enabled.
        :param
            FastReadout (bool): True to enable fast readout mode.

        :return:
            Whether Fast Readout Mode is enabled.
        """

        if FastReadout is None:
            return self.get("fastreadout")

        self.put("fastreadout", FastReadout=FastReadout)

    def fullwellcapacity(self):
        """
        Report the full well capacity of the camera.
        Report the full well capacity of the camera in electrons, at the current
        camera settings (binning, SetupDialog settings, etc.).
        :return:
            Full well capacity of the camera.
        """

        return self.get("fullwellcapacity")

    def gain(self, Gain=None):
        """
        Set or return an index into the Gains array.
        :param
            Gain (int): Index of the current camera gain in the Gains string array.

        :return:
            Index into the Gains array for the selected camera gain.
        """

        if Gain is None:
            return self.get("gain")

        self.put("gain", Gain=Gain)

    def gainmax(self):
        """
        Maximum value of Gain.
        """

        return self.get("gainmax")

    def gainmin(self):
        """
        Minimum value of Gain.
        """

        return self.get("gainmin")

    def gains(self):
        """
        Gains supported by the camera.
        """

        return self.get("gains")

    def hasshutter(self):
        """
        Indicate whether the camera has a mechanical shutter.
        """

        return self.get("hasshutter")

    def heatsinktemperature(self):
        """
        Return the current heat sink temperature.
        :return:
            Current heat sink temperature (called "ambient temperature" by some
            manufacturers) in degrees Celsius.
        """

        return self.get("heatsinktemperature")

    def imagearray(self):
        """
        Return an array of integers containing the exposure pixel values.
        Return an array of 32bit integers containing the pixel values from the last
        exposure. This call can return either a 2 dimension (monochrome images) or 3
        dimension (colour or multi-plane images) array of size NumX * NumY or NumX *
        NumY * NumPlanes. Where applicable, the size of NumPlanes has to be determined
        by inspection of the returned Array. Since 32bit integers are always returned
        by this call, the returned JSON Type value (0 = Unknown, 1 = short(16bit),
        2 = int(32bit), 3 = Double) is always 2. The number of planes is given in the
        returned Rank value. When de-serialising to an object it helps enormously to
        know the array Rank beforehand so that the correct data class can be used. This
        can be achieved through a regular expression or by direct parsing of the
        returned JSON string to extract the Type and Rank values before de-serialising.
        :return:
            Array of integers containing the exposure pixel values.

        """

        return self.get("imagearray")

    def imagearrayvariant(self):
        """
        Return an array of integers containing the exposure pixel values.
        Return an array of 32bit integers containing the pixel values from the last
        exposure. This call can return either a 2 dimension (monochrome images) or 3
        dimension (colour or multi-plane images) array of size NumX * NumY or NumX *
        NumY * NumPlanes. Where applicable, the size of NumPlanes has to be determined
        by inspection of the returned Array. Since 32bit integers are always returned
        by this call, the returned JSON Type value (0 = Unknown, 1 = short(16bit),
        2 = int(32bit), 3 = Double) is always 2. The number of planes is given in the
        returned Rank value. When de-serialising to an object it helps enormously to
        know the array Rank beforehand so that the correct data class can be used. This
        can be achieved through a regular expression or by direct parsing of the
        returned JSON string to extract the Type and Rank values before de-serialising.
        :return:
            Array of integers containing the exposure pixel values.

        """

        return self.get("imagearrayvariant")

    def imageready(self):
        """
        Indicate that an image is ready to be downloaded.
        """
        return self.get("imageready")

    def ispulseguiding(self):
        """
        Indicatee that the camera is pulse guideing.
        """
        return self.get("ispulseguiding")

    def lastexposureduration(self):
        """
        Report the actual exposure duration in seconds (i.e. shutter open time).
        """
        return self.get("lastexposureduration")

    def lastexposurestarttime(self):
        """
        Start time of the last exposure in FITS standard format.

        Reports the actual exposure start in the FITS-standard
        CCYY-MM-DDThh:mm:ss[.sss...] format.
        :return:
            Start time of the last exposure in FITS standard format.
        """
        return self.get("lastexposurestarttime")

    def maxadu(self):
        """
        Camera's maximum ADU value.
        """
        return self.get("maxadu")

    def maxbinx(self):
        """
        Maximum binning for the camera X axis.
        """
        return self.get("maxbinx")

    def maxbiny(self):
        """
        Maximum binning for the camera Y axis.
        """
        return self.get("maxbiny")

    def numx(self, NumX=None):
        """
        Set or return the current subframe width.

        :param
            NumX (int): Subframe width, if binning is active, value is in binned
                pixels.
        :return:
            Current subframe width.
        """
        if NumX is None:
            return self.get("numx")

        self.put("numx", NumX=NumX)

    def numy(self, NumY=None):
        """
        Set or return the current subframe height.

        :param
            NumY (int): Subframe height, if binning is active, value is in binned
                pixels.
        :return:
            Current subframe height.
        """
        if NumY is None:
            return self.get("numy")

        self.put("numy", NumY=NumY)

    def offset(self, Offset=None):
        """
        Indicate the camera's Offset.
        """
        if Offset is None:
            return self.get("offset")

        self.put("offset", Offset=Offset)

    def percentcompleted(self):
        """
        Indicate percentage completeness of the current operation.
        :return:
            If valid, returns an integer between 0 and 100, where 0 indicates 0%
            progress (function just started) and 100 indicates 100% progress (i.e.
            completion).

        """
        return self.get("percentcompleted")

    def pixelsizex(self):
        """
        Width of CCD chip pixels (microns).
        """
        return self.get("pixelsizex")

    def pixelsizey(self):
        """
        Height of CCD chip pixels (microns).
        """
        return self.get("pixelsizey")

    def readoutmode(self, ReadoutMode=None):
        """
        Indicate the camera's readout mode as an index into the array ReadoutModes.
        """
        if ReadoutMode is None:
            return self.get("readoutmode")

        self.put("readoutmode", ReadoutMode=ReadoutMode)

    def readoutmodes(self):
        """
        List of available readout modes.
        """
        return self.get("readoutmodes")

    def sensorname(self):
        """
        Name of the sensor used within the camera.
        """
        return self.get("sensorname")

    def sensortype(self):
        """
        Type of information returned by the the camera sensor (monochrome or colour).

        Notes:
            0 = Monochrome, 1 = Colour not requiring Bayer decoding, 2 = RGGB Bayer
            encoding, 3 = CMYG Bayer encoding, 4 = CMYG2 Bayer encoding, 5 = LRGB
            TRUESENSE Bayer encoding.

        :return:
            Value indicating whether the sensor is monochrome, or what Bayer matrix it
            encodes.
        """
        return self.get("sensortype")

    def setccdtemperature(self, SetCCDTemperature=None):
        """
        Set or return the camera's cooler setpoint (degrees Celsius).
        :param
            SetCCDTemperature (float): 	Temperature set point (degrees Celsius).

        :return:
            Camera's cooler setpoint (degrees Celsius).
        """
        if SetCCDTemperature is None:
            return self.get("setccdtemperature")

        self.put("setccdtemperature", SetCCDTemperature=SetCCDTemperature)

    def startx(self, StartX=None):
        """
        Set or return the current subframe X axis start position.
        :param
            StartX (int): The subframe X axis start position in binned pixels.

        :return:
            Sets the subframe start position for the X axis (0 based) and returns the
            current value. If binning is active, value is in binned pixels.
        """
        if StartX is None:
            return self.get("startx")

        self.put("startx", StartX=StartX)

    def starty(self, StartY=None):
        """
        Set or return the current subframe Y axis start position.
        :param
            StartY (int): The subframe Y axis start position in binned pixels.

        :return:
            Sets the subframe start position for the Y axis (0 based) and returns the
            current value. If binning is active, value is in binned pixels.
        """
        if StartY is None:
            return self.get("starty")

        self.put("starty", StartY=StartY)

    def abortexposure(self):
        """
        Abort the current exposure, if any, and returns the camera to Idle state.
        """
        self.put("abortexposure")

    def pulseguide(self, Direction: int, Duration: int):
        """
        Pulse guide in the specified direction for the specified time.

        :param
            Direction (int): Direction of movement (0 = North, 1 = South, 2 = East,
                3 = West).
            Duration (int): Duration of movement in milli-seconds.
        """
        self.put("pulseguide", Direction=Direction, Duration=Duration)

    def startexposure(self, Duration=0, Light=True):
        """
        Start an exposure.

        Notes:
            Use ImageReady to check when the exposure is complete.

        :param
            Duration (float): Duration of exposure in seconds.
            Light (bool): True if light frame, false if dark frame.
        """
        self.put("startexposure", Duration=Duration, Light=Light)

    def stopexposure(self):
        """
        Stop the current exposure, if any.

        Notes:
            If an exposure is in progress, the readout process is initiated. Ignored if
            readout is already in process.
        """
        self.put("stopexposure")


class FilterWheel(AlpacaBase):
    """
    Filter wheel specific methods.
    """

    def focusoffsets(self):
        """
        Filter focus offsets.
        :return:
            An integer array of filter focus offsets.

        """
        return self.get("focusoffsets")

    def names(self):
        """
        Filter wheel filter names.
        :return:
            Names of the filters.
        """

        return self.get("names")

    def position(self, Position=None):
        """
        Set or return the filter wheel position.
        :param
            Position (int): Number of the filter wheel position to select.
        :return:
            Returns the current filter wheel position.
        """

        if Position is None:
            return self.get("position")

        self.put("position", Position=Position)


class Telescope(AlpacaBase):
    """
    Telescope specific methods.
    """

    def alignmentmode(self):
        """
        Return the current mount alignment mode.
        :return:
            Alignment mode of the mount (Alt/Az, Polar, German Polar).

        """
        return self.get("alignmentmode")

    def altitude(self):
        """
        Return the mount's Altitude above the horizon.
        :return:
            Altitude of the telescope's current position (degrees, positive up).
        """
        return self.get("altitude")

    def aperturearea(self):
        """
        Return the telescope's aperture.
        :return:
            Area of the telescope's aperture (square meters).
        """
        return self.get("aperturearea")

    def aperturediameter(self):
        """
        Return the telescope's effective aperture.
        :return:
            Telescope's effective aperture diameter (meters).
        """
        value = self.get("aperturediameter")
        if value:
            return value * 1000

        else:
            return None

    def athome(self):
        """
        Indicate whether the mount is at the home position.
        :return:
            True if the mount is stopped in the Home position. Must be False if the
            telescope does not support homing.

        """

        return self.get("athome")

    def atpark(self):
        """
        Indicate whether the telescope is at the park position.
        :return:
            True if the telescope has been put into the parked state by the set park()
            method. Set False by calling the unpark() method.
        """

        return self.get("atpark")

    def azimuth(self):
        """
        Return the telescope's aperture.

        Return:
            Azimuth of the telescope's current position (degrees, North-referenced,
            positive East/clockwise).
        """

        return self.get("azimuth")

    def canfindhome(self):
        """
        Indicate whether the mount can find the home position.

        :return:
            True if this telescope is capable of programmed finding its home position.
        """

        return self.get("canfindhome")

    def canpark(self):
        """
        Indicate whether the telescope can be parked.
        :return:
            True if this telescope is capable of programmed parking.
        """

        return self.get("canpark")

    def canpulseguide(self):
        """
        Indicate whether the telescope can be pulse guided.
        :return:
            True if this telescope is capable of software-pulsed guiding (via the
            pulseguide(int, int) method).
        """

        return self.get("canpulseguide")

    def cansetdeclinationrate(self):
        """
        Indicate whether the DeclinationRate property can be changed.
        :return:
            True if the DeclinationRate property can be changed to provide offset
            tracking in the declination axis.
        """

        return self.get("cansetdeclinationrate")

    def cansetguiderates(self):
        """
        Indicate whether the DeclinationRate property can be changed.
        :return:
            True if the guide rate properties used for pulseguide(int, int) can ba
            adjusted.
        """

        return self.get("cansetguiderates")

    def cansetpark(self):
        """
        Indicate whether the telescope park position can be set.
        :return:
            True if this telescope is capable of programmed setting of its park position
            (setpark() method).
        """

        return self.get("cansetpark")

    def cansetpierside(self):
        """
        Indicate whether the telescope SideOfPier can be set.
        :return:
            True if the SideOfPier property can be set, meaning that the mount can be
            forced to flip.
        """

        return self.get("cansetpierside")

    def cansetrightascensionrate(self):
        """
        Indicate whether the RightAscensionRate property can be changed.
        :return:
            True if the RightAscensionRate property can be changed to provide offset
            tracking in the right ascension axis.
        """

        return self.get("cansetrightascensionrate")

    def cansettracking(self):
        """
        Indicate whether the Tracking property can be changed.
        :return:
            True if the Tracking property can be changed, turning telescope sidereal
            tracking on and off.
        """

        return self.get("cansettracking")

    def canslew(self):
        """
        Indicate whether the telescope can slew synchronously.
        :return:
            True if this telescope is capable of programmed slewing (synchronous or
            asynchronous) to equatorial coordinates.
        """

        return self.get("canslew")

    def canslewaltaz(self):
        """
        Indicate whether the telescope can slew synchronously to AltAz coordinates.
        :return:
            True if this telescope is capable of programmed slewing (synchronous or
            asynchronous) to local horizontal coordinates.
        """

        return self.get("canslewaltaz")

    def canslewaltazasync(self):
        """
        Indicate whether the telescope can slew asynchronusly to AltAz coordinates.
        :return:
            True if this telescope is capable of programmed asynchronus slewing
            (synchronous or asynchronous) to local horizontal coordinates.
        """

        return self.get("canslewaltazasync")

    def cansync(self):
        """
        Indicate whether the telescope can sync to equatorial coordinates.
        :return:
            True if this telescope is capable of programmed synching to equatorial
            coordinates.
        """

        return self.get("cansync")

    def cansyncaltaz(self):
        """
        Indicate whether the telescope can sync to local horizontal coordinates.
        :return:
            True if this telescope is capable of programmed synching to local horizontal
            coordinates.
        """

        return self.get("cansyncaltaz")

    def declination(self):
        """
        Return the telescope's declination.
        Notes:
            Reading the property will raise an error if the value is unavailable.
        :return:
            The declination (degrees) of the telescope's current equatorial coordinates,
            in the coordinate system given by the EquatorialSystem property.
        """

        return self.get("declination")

    def declinationrate(self, DeclinationRate=None):
        """
        Set or return the telescope's declination tracking rate.
        :param
            DeclinationRate (float): Declination tracking rate (arcseconds per second).

        :return:
            The declination tracking rate (arcseconds per second) if DeclinationRate is
            not set.
        """

        if DeclinationRate is None:
            return self.get("declinationrate")

        self.put("declinationrate", DeclinationRate=DeclinationRate)

    def doesrefraction(self, DoesRefraction=None):
        """
        Indicate or determine if atmospheric refraction is applied to coordinates.
        :param
            DoesRefraction (bool): Set True to make the telescope or driver apply
                atmospheric refraction to coordinates.

        :return:
            True if the telescope or driver applies atmospheric refraction to
            coordinates.
        """

        if DoesRefraction is None:
            return self.get("doesrefraction")

        self.put("doesrefraction", DoesRefraction=DoesRefraction)

    def equatorialsystem(self):
        """
        Return the current equatorial coordinate system used by this telescope.
        :return:
            Current equatorial coordinate system used by this telescope
            (e.g. Topocentric or J2000).
        """

        return self.get("equatorialsystem")

    def focallength(self):
        """
        Return the telescope's focal length in meters.
        :return:
            The telescope's focal length in meters.
        """

        value = self.get("focallength")
        if value:
            return value * 1000

        else:
            return None

    def guideratedeclination(self, GuideRateDeclination=None):
        """
        Set or return the current Declination rate offset for telescope guiding.
        :param
            GuideRateDeclination (float): Declination movement rate offset
                (degrees/sec).
        :return:
            Current declination rate offset for telescope guiding if not set.
        """

        if GuideRateDeclination is None:
            return self.get("guideratedeclination")

        self.put("guideratedeclination", GuideRateDeclination=GuideRateDeclination)

    def guideraterightascension(self, GuideRateRightAscension=None):
        """
        Set or return the current RightAscension rate offset for telescope guiding.
        :param
            GuideRateRightAscension (float): RightAscension movement rate offset
                (degrees/sec).
        :return:
            Current right ascension rate offset for telescope guiding if not set.
        """

        if GuideRateRightAscension is None:
            return self.get("guideraterightascension")

        self.put("guideraterightascension", GuideRateRightAscension=GuideRateRightAscension)

    def ispulseguiding(self):
        """
        Indicate whether the telescope is currently executing a PulseGuide command.
        :return:
            True if a pulseguide(int, int) command is in progress, False otherwise.

        """

        return self.get("ispulseguiding")

    def rightascension(self):
        """
        Return the telescope's right ascension coordinate.
        :return:
            The right ascension (hours) of the telescope's current equatorial
            coordinates, in the coordinate system given by the EquatorialSystem
            property.
        """

        return self.get("rightascension")

    def rightascensionrate(self, RightAscensionRate=None):
        """
        Set or return the telescope's right ascension tracking rate.
        :param
            RightAscensionRate (float): Right ascension tracking rate (arcseconds per
                second).
        :return:
            Telescope's right ascension tracking rate if not set.
        """

        if RightAscensionRate is None:
            return self.get("rightascensionrate")

        self.put("rightascensionrate", RightAscensionRate=RightAscensionRate)

    def sideofpier(self, SideOfPier=None):
        """
        Set or return the mount's pointing state.
        :param
            SideOfPier (int): New pointing state. 0 = pierEast, 1 = pierWest

        :return:
            Side of pier if not set.
        """

        if SideOfPier is None:
            return self.get("sideofpier")

        self.put("sideofpier", SideOfPier=SideOfPier)

    def siderealtime(self):
        """
        Return the local apparent sidereal time.
        :return:
            The local apparent sidereal time from the telescope's internal clock (hours,
            sidereal).
        """

        return self.get("siderealtime")

    def siteelevation(self, SiteElevation=None):
        """
        Set or return the observing site's elevation above mean sea level.
        :param
            SiteElevation (float): Elevation above mean sea level (metres).

        :return:
            Elevation above mean sea level (metres) of the site at which the telescope
            is located if not set.
        """

        if SiteElevation is None:
            return self.get("siteelevation")

        self.put("siteelevation", SiteElevation=SiteElevation)

    def sitelatitude(self, SiteLatitude=None):
        """
        Set or return the observing site's latitude.
        :param
            SiteLatitude (float): Site latitude (degrees).

        :return:
            Geodetic(map) latitude (degrees, positive North, WGS84) of the site at which
            the telescope is located if not set.
        """

        if SiteLatitude is None:
            return self.get("sitelatitude")

        self.put("sitelatitude", SiteLatitude=SiteLatitude)

    def sitelongitude(self, SiteLongitude=None):
        """
        Set or return the observing site's longitude.
        :param
            SiteLongitude (float): Site longitude (degrees, positive East, WGS84)

        :return:
            Longitude (degrees, positive East, WGS84) of the site at which the telescope
            is located.
        """

        if SiteLongitude is None:
            return self.get("sitelongitude")

        self.put("sitelongitude", SiteLongitude=SiteLongitude)

    def slewing(self):
        """
        Indicate whether the telescope is currently slewing.
        :return:
            True if telescope is currently moving in response to one of the Slew methods
            or the moveaxis(int, float) method, False at all other times.
        """

        return self.get("slewing")

    def slewsettletime(self, SlewSettleTime=None):
        """
        Set or return the post-slew settling time.
        :param
            SlewSettleTime (int): Settling time (integer sec.).
        :return:
            Returns the post-slew settling time (sec.) if not set.
        """

        if SlewSettleTime is None:
            return self.get("slewsettletime")

        self.put("slewsettletime", SlewSettleTime=SlewSettleTime)

    def targetdeclination(self, TargetDeclination=None):
        """
        Set or return the target declination of a slew or sync.
        :param
            TargetDeclination (float): Target declination(degrees)

        :return:
            Declination (degrees, positive North) for the target of an equatorial slew
            or sync operation.
        """

        if TargetDeclination is None:
            return self.get("targetdeclination")

        self.put("targetdeclination", TargetDeclination=TargetDeclination)

    def targetrightascension(self, TargetRightAscension=None):
        """
        Set or return the current target right ascension.
        :param
            TargetRightAscension (float): Target right ascension (hours).

        :return:
            Right ascension (hours) for the target of an equatorial slew or sync
            operation.
        """

        if TargetRightAscension is None:
            return self.get("targetrightascension")

        self.put("targetrightascension", TargetRightAscension=TargetRightAscension)

    def tracking(self, Tracking=None):
        """
        Enable, disable, or indicate whether the telescope is tracking.
        :param
            Tracking (bool): Tracking enabled / disabled.

        :return:
            State of the telescope's sidereal tracking drive.
        """

        if Tracking is None:
            return self.get("tracking")

        self.put("tracking", Tracking=Tracking)

    def trackingrate(self, TrackingRate=None):
        """
        Set or return the current tracking rate.
        :param
            TrackingRate (int): New tracking rate. 0 = driveSidereal, 1 = driveLunar,
                2 = driveSolar, 3 = driveKing.

        :return:
            Current tracking rate of the telescope's sidereal drive if not set.
        """

        if TrackingRate is None:
            return self.get("trackingrate")

        self.put("trackingrate", TrackingRate=TrackingRate)

    def trackingrates(self):
        """
        Return a collection of supported DriveRates values.
        :return:
            List of supported DriveRates values that describe the permissible values of
            the TrackingRate property for this telescope type.
        """

        return self.get("trackingrates")

    def utcdate(self, UTCDate=None):
        """
        Set or return the UTC date/time of the telescope's internal clock.
        :param
            UTCDate: UTC date/time as an str or datetime.

        :return:
            datetime of the UTC date/time if not set.
        """

        if UTCDate is None:
            return parser.parse(self.get("utcdate"), fuzzy=True)

        if type(UTCDate) is str:
            data = UTCDate

        elif type(UTCDate) is datetime.datetime:
            data = UTCDate.isoformat()

        else:
            self.log.warning(f'type error in: [{UTCDate}]')
            return None

        self.put("utcdate", UTCDate=data)

    def abortslew(self):
        """
        Immediately stops a slew in progress.
        """

        self.put("abortslew")

    def axisrates(self, Axis):
        """
        Return rates at which the telescope may be moved about the specified axis.
        :return:
            The rates at which the telescope may be moved about the specified axis by
            the moveaxis(int, float) method.
        """

        return self.get("axisrates", Axis=Axis)

    def canmoveaxis(self, Axis):
        """
        Indicate whether the telescope can move the requested axis.
        :return:
            True if this telescope can move the requested axis.
        """

        return self.get("canmoveaxis", Axis=Axis)

    def destinationsideofpier(self, RightAscension, Declination):
        """
        Predict the pointing state after a German equatorial mount slews to given coordinates.
        :param
            RightAscension (float): Right Ascension coordinate (0.0 to 23.99999999
                hours).
            Declination (float): Declination coordinate (-90.0 to +90.0 degrees).
        :return:
            Pointing state that a German equatorial mount will be in if it slews to the
            given coordinates. The return value will be one of - 0 = pierEast,
            1 = pierWest, -1 = pierUnknown.
        """

        return self.get(
            "destinationsideofpier",
            RightAscension=RightAscension,
            Declination=Declination,
        )

    def findhome(self):
        """
        Move the mount to the "home" position.
        """

        self.put("findhome")

    def moveaxis(self, Axis, Rate):
        """
        Move a telescope axis at the given rate.
        :param
            Axis (int): The axis about which rate information is desired.
                0 = axisPrimary, 1 = axisSecondary, 2 = axisTertiary.
            Rate (float): The rate of motion (deg/sec) about the specified axis
        """

        self.put("moveaxis", Axis=Axis, Rate=Rate)

    def park(self):
        """
        Park the mount.
        """

        self.put("park")

    def pulseguide(self, Direction, Duration):
        """
        Move the scope in the given direction for the given time.
        Notes:
            0 = guideNorth, 1 = guideSouth, 2 = guideEast, 3 = guideWest.
        :param
            Direction (int): Direction in which the guide-rate motion is to be made.
            Duration (int): Duration of the guide-rate motion (milliseconds).
        """

        self.put("pulseguide", Direction=Direction, Duration=Duration)

    def setpark(self):
        """
        Set the telescope's park position.
        """

        self.put("setpark")

    def slewtoaltaz(self, Azimuth, Altitude):
        """
        Slew synchronously to the given local horizontal coordinates.
        :param
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).
        """

        self.put("slewtoaltaz", Azimuth=Azimuth, Altitude=Altitude)

    def slewtoaltazasync(self, Azimuth, Altitude):
        """
        Slew asynchronously to the given local horizontal coordinates.
        :param
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).
        """

        self.put("slewtoaltazasync", Azimuth=Azimuth, Altitude=Altitude)

    def slewtocoordinates(self, RightAscension, Declination):
        """
        Slew synchronously to the given equatorial coordinates.
        :param
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).
        """

        self.put("slewtocoordinates", RightAscension=RightAscension, Declination=Declination)

    def slewtocoordinatesasync(self, RightAscension, Declination):
        """
        Slew asynchronously to the given equatorial coordinates.
        :param
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).
        """

        self.put(
            "slewtocoordinatesasync",
            RightAscension=RightAscension,
            Declination=Declination,
        )

    def slewtotarget(self):
        """
        Slew synchronously to the TargetRightAscension and TargetDeclination coordinates.
        """

        self.put("slewtotarget")

    def slewtotargetasync(self):
        """
        Asynchronously slew to the TargetRightAscension and TargetDeclination coordinates.
        """

        self.put("slewtotargetasync")

    def synctoaltaz(self, Azimuth, Altitude):
        """
        Sync to the given local horizontal coordinates.
        :param
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).
        """

        self.put("synctoaltaz", Azimuth=Azimuth, Altitude=Altitude)

    def synctocoordinates(self, RightAscension, Declination):
        """
        Sync to the given equatorial coordinates.
        :param
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).
        """

        self.put(
            "synctocoordinates", RightAscension=RightAscension, Declination=Declination
        )

    def synctotarget(self):
        """
        Sync to the TargetRightAscension and TargetDeclination coordinates.
        """

        self.put("synctotarget")

    def unpark(self):
        """
        Unpark the mount.
        """

        self.put("unpark")


class ObservingConditions(AlpacaBase):
    """
    ObservingConditions  specific methods.
    """

    def averageperiod(self, AveragePeriod=None):
        if AveragePeriod is None:
            return self.get("averageperiod")

        self.put("averageperiod", AveragePeriod=AveragePeriod)

    def cloudcover(self):
        return self.get("cloudcover")

    def dewpoint(self):
        return self.get("dewpoint")

    def humidity(self):
        return self.get("humidity")

    def pressure(self):
        return self.get("pressure")

    def rainrate(self):
        return self.get("rainrate")

    def skybrightness(self):
        return self.get("skybrightness")

    def skyquality(self):
        return self.get("skyquality")

    def skytemperature(self):
        return self.get("skytemperature")

    def starfwhm(self):
        return self.get("starfwhm")

    def temperature(self):
        return self.get("temperature")

    def winddirection(self):
        return self.get("winddirection")

    def windgust(self):
        return self.get("windgust")

    def windspeed(self):
        return self.get("windspeed")

    def refresh(self):
        self.put("refresh")

    def sensordescription(self):
        return self.get("sensordescription")

    def timesincelastupdate(self):
        return self.get("timesincelastupdate")


class Focuser(AlpacaBase):
    """
    Focuser  specific methods.
    """

    def absolut(self):
        return self.get("absolut")

    def ismoving(self):
        return self.get("ismoving")

    def maxincrement(self):
        return self.get("maxincrement")

    def maxstep(self):
        return self.get("maxstep")

    def position(self):
        return self.get("position")

    def stepsize(self):
        return self.get("stepsize")

    def tempcomp(self, TempComp=None):
        if TempComp is None:
            return self.get("tempcomp")

        self.put("tempcomp", TempComp=TempComp)

    def tempcompavailable(self):
        return self.get("tempcompavailable")

    def temperature(self):
        return self.get("temperature")

    def halt(self):
        self.put("halt")

    def move(self, Position=None):
        if Position is None:
            return self.get("move")

        self.put("move", Position=int(Position))


class Covercalibrator(AlpacaBase):
    """
    Covercalibrator  specific methods.
    """

    def brightness(self):
        return self.get("brightness")

    def calibratoroff(self):
        self.put("calibratoroff")

    def calibratoron(self, Brightness=None):
        if Brightness:
            self.put("calibratoron", Brightness=Brightness)

    def calibratorstate(self):
        return self.get("calibratorstate")

    def closecover(self):
        self.put("closecover")

    def opencover(self):
        self.put("opencover")

    def haltcover(self):
        self.put("haltcover")

    def coverstate(self):
        return self.get("coverstate")

    def maxbrightness(self):
        return self.get("maxbrightness")
