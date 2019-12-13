"""Wraps the HTTP requests for the ASCOM Alpaca API into pythonic classes with methods.
Attributes:
    DEFAULT_API_VERSION (int): Default Alpaca API spec to use if none is specified when
    needed.
"""

from datetime import datetime
from typing import Optional, Union, List, Dict, Mapping, Any
import dateutil.parser
import requests

DEFAULT_API_VERSION = 1


class Device:
    """Common methods across all ASCOM Alpaca devices.
    Attributes:
        address (str): Domain name or IP address of Alpaca server.
            Can also specify port number if needed.
        device_type (str): One of the recognised ASCOM device types
            e.g. telescope (must be lower case).
        device_number (int): Zero based device number as set on the server (0 to
            4294967295).
        protocol (str): Protocol used to communicate with Alpaca server.
        api_version (int): Alpaca API version.
        base_url (str): Basic URL to easily append with commands.
    """

    __all__ = [
               ]

    logger = logging.getLogger(__name__)

    def __init__(
            self,
            address: str,
            device_type: str,
            device_number: int,
            protocol: str,
            api_version: int,
    ):
        """Initialize Device object."""
        self.address = address
        self.device_type = device_type
        self.device_number = device_number
        self.api_version = api_version
        self.base_url = "%s://%s/api/v%d/%s/%d" % (
            protocol,
            address,
            api_version,
            device_type,
            device_number,
        )

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


class Switch(Device):
    """Switch specific methods."""

    __all__ = [
               ]

    logger = logging.getLogger(__name__)

    def __init__(
            self,
            address: str,
            device_number: int,
            protocol: str = "http",
            api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize Switch object."""
        super().__init__(address, "switch", device_number, protocol, api_version)

    def maxswitch(self) -> int:
        """Count of switch devices managed by this driver.
        Returns:
            Number of switch devices managed by this driver. Devices are numbered from 0
            to MaxSwitch - 1.

        """
        return self._get("maxswitch")

    def canwrite(self, Id: Optional[int] = 0) -> bool:
        """Indicate whether the specified switch device can be written to.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.
        Returns:
            Whether the specified switch device can be written to, default true. This is
            false if the device cannot be written to, for example a limit switch or a
            sensor.

        """
        return self._get("canwrite", Id=Id)

    def getswitch(self, Id: Optional[int] = 0) -> bool:
        """Return the state of switch device id as a boolean.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.

        Returns:
            State of switch device id as a boolean.

        """
        return self._get("getswitch", Id=Id)

    def getswitchdescription(self, Id: Optional[int] = 0) -> str:
        """Get the description of the specified switch device.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.

        Returns:
            Description of the specified switch device.

        """
        return self._get("getswitchdescription", Id=Id)

    def getswitchname(self, Id: Optional[int] = 0) -> str:
        """Get the name of the specified switch device.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.

        Returns:
            Name of the specified switch device.

        """
        return self._get("getswitchname", Id=Id)

    def getswitchvalue(self, Id: Optional[int] = 0) -> str:
        """Get the value of the specified switch device as a double.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.

        Returns:
            Value of the specified switch device.

        """
        return self._get("getswitchvalue", Id=Id)

    def minswitchvalue(self, Id: Optional[int] = 0) -> str:
        """Get the minimum value of the specified switch device as a double.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.

        Returns:
            Minimum value of the specified switch device as a double.

        """
        return self._get("minswitchvalue", Id=Id)

    def setswitch(self, Id: int, State: bool):
        """Set a switch controller device to the specified state, True or False.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.
            State (bool): The required control state (True or False).
        """
        self._put("setswitch", Id=Id, State=State)

    def setswitchname(self, Id: int, Name: str):
        """Set a switch device name to the specified value.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.
            Name (str): The name of the device.
        """
        self._put("setswitchname", Id=Id, Name=Name)

    def setswitchvalue(self, Id: int, Value: float):
        """Set a switch device value to the specified value.
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.
            Value (float): Value to be set, between MinSwitchValue and MaxSwitchValue.
        """
        self._put("setswitchvalue", Id=Id, Value=Value)

    def switchstep(self, Id: Optional[int] = 0) -> str:
        """Return the step size that this device supports.
        Return the step size that this device supports (the difference between
        successive values of the device).
        Notes:
            Devices are numbered from 0 to MaxSwitch - 1.
        Args:
            Id (int): The device number.

        Returns:
            Maximum value of the specified switch device as a double.

        """
        return self._get("switchstep", Id=Id)


class SafetyMonitor(Device):
    """Safety monitor specific methods."""
    __all__ = [
               ]

    logger = logging.getLogger(__name__)

    def __init__(
            self,
            address: str,
            device_number: int,
            protocol: str = "http",
            api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize SafetyMonitor object."""
        super().__init__(
            address, "safetymonitor", device_number, protocol, api_version
        )

    def issafe(self) -> bool:
        """Indicate whether the monitored state is safe for use.
        Returns:
            True if the state is safe, False if it is unsafe.

        """
        return self._get("issafe")


class Dome(Device):
    """Dome specific methods."""
    __all__ = [
               ]

    logger = logging.getLogger(__name__)

    def __init__(
            self,
            address: str,
            device_number: int,
            protocol: str = "http",
            api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize Dome object."""
        super().__init__(address, "dome", device_number, protocol, api_version)

    def altitude(self) -> float:
        """Dome altitude.
        Returns:
            Dome altitude (degrees, horizon zero and increasing positive to 90 zenith).

        """
        return self._get("altitude")

    def athome(self) -> bool:
        """Indicate whether the dome is in the home position.
        Notes:
            This is normally used following a findhome() operation. The value is reset
            with any azimuth slew operation that moves the dome away from the home
            position. athome() may also become true during normal slew operations, if the
            dome passes through the home position and the dome controller hardware is
            capable of detecting that; or at the end of a slew operation if the dome
            comes to rest at the home position.
        Returns:
            True if dome is in the home position.

        """
        return self._get("athome")

    def atpark(self) -> bool:
        """Indicate whether the telescope is at the park position.
        Notes:
            Set only following a park() operation and reset with any slew operation.
        Returns:
            True if the dome is in the programmed park position.
        """
        return self._get("atpark")

    def azimuth(self) -> float:
        """Dome azimuth.
        Returns:
            Dome azimuth (degrees, North zero and increasing clockwise, i.e., 90 East,
            180 South, 270 West).
        """
        return self._get("azimuth")

    def canfindhome(self) -> bool:
        """Indicate whether the dome can find the home position.
        Returns:
            True if the dome can move to the home position.

        """
        return self._get("canfindhome")

    def canpark(self) -> bool:
        """Indicate whether the dome can be parked.
        Returns:
            True if the dome is capable of programmed parking (park() method).

        """
        return self._get("canpark")

    def cansetaltitude(self) -> bool:
        """Indicate whether the dome altitude can be set.
        Returns:
            True if driver is capable of setting the dome altitude.

        """
        return self._get("cansetaltitude")

    def cansetazimuth(self) -> bool:
        """Indicate whether the dome azimuth can be set.
        Returns:
            True if driver is capable of setting the dome azimuth.

        """
        return self._get("cansetazimuth")

    def cansetpark(self) -> bool:
        """Indicate whether the dome park position can be set.
        Returns:
            True if driver is capable of setting the dome park position.

        """
        return self._get("cansetpark")

    def cansetshutter(self) -> bool:
        """Indicate whether the dome shutter can be opened.
        Returns:
            True if driver is capable of automatically operating shutter.
        """
        return self._get("cansetshutter")

    def canslave(self) -> bool:
        """Indicate whether the dome supports slaving to a telescope.
        Returns:
            True if driver is capable of slaving to a telescope.

        """
        return self._get("canslave")

    def cansyncazimuth(self) -> bool:
        """Indicate whether the dome azimuth position can be synched.
        Notes:
            True if driver is capable of synchronizing the dome azimuth position using
            the synctoazimuth(float) method.

        Returns:
            True or False value.

        """
        return self._get("cansyncazimuth")

    def shutterstatus(self) -> int:
        """Status of the dome shutter or roll-off roof.
        Notes:
            0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error.

        Returns:
            Status of the dome shutter or roll-off roof.
        """
        return self._get("shutterstatus")

    def slaved(self, Slaved: Optional[bool] = None) -> bool:
        """Set or indicate whether the dome is slaved to the telescope.

        Returns:
            True or False value in not set.

        """
        if Slaved is None:
            return self._get("slaved")
        self._put("slaved", Slaved=Slaved)

    def slewing(self) -> bool:
        """Indicate whether the any part of the dome is moving.
        Notes:
            True if any part of the dome is currently moving, False if all dome
            components are steady.

        Return:
            True or False value.

        """
        return self._get("slewing")

    def abortslew(self):
        """Immediately cancel current dome operation.
        Notes:
            Calling this method will immediately disable hardware slewing (Slaved will
            become False).
        """
        self._put("abortslew")

    def closeshutter(self):
        """Close the shutter or otherwise shield telescope from the sky."""
        self._put("closeshutter")

    def findhome(self):
        """Start operation to search for the dome home position.
        Notes:
            After home position is established initializes azimuth to the default value
            and sets the athome flag.

        """
        self._put("findhome")

    def openshutter(self):
        """Open shutter or otherwise expose telescope to the sky."""
        self._put("openshutter")

    def park(self):
        """Rotate dome in azimuth to park position.
        Notes:
            After assuming programmed park position, sets atpark flag.

        """
        self._put("park")

    def setpark(self):
        """Set current azimuth, altitude position of dome to be the park position."""
        self._put("setpark")

    def slewtoaltitude(self, Altitude: float):
        """Slew the dome to the given altitude position."""
        self._put("slewtoaltitude", Altitude=Altitude)

    def slewtoazimuth(self, Azimuth: float):
        """Slew the dome to the given azimuth position.

        Args:
            Azimuth (float): Target dome azimuth (degrees, North zero and increasing
                clockwise. i.e., 90 East, 180 South, 270 West).
        """
        self._put("slewtoazimuth", Azimuth=Azimuth)

    def synctoazimuth(self, Azimuth: float):
        """Synchronize the current position of the dome to the given azimuth.
        Args:
            Azimuth (float): Target dome azimuth (degrees, North zero and increasing
                clockwise. i.e., 90 East, 180 South, 270 West).

        """
        self._put("synctoazimuth", Azimuth=Azimuth)


class Camera(Device):
    """Camera specific methods."""
    __all__ = [
               ]

    logger = logging.getLogger(__name__)

    def __init__(
            self,
            address: str,
            device_number: int,
            protocol: str = "http",
            api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize Camera object."""
        super().__init__(address, "camera", device_number, protocol, api_version)

    def bayeroffsetx(self) -> int:
        """Return the X offset of the Bayer matrix, as defined in SensorType."""
        return self._get("bayeroffsetx")

    def bayeroffsety(self) -> int:
        """Return the Y offset of the Bayer matrix, as defined in SensorType."""
        return self._get("bayeroffsety")

    def binx(self, BinX: Optional[int] = None) -> int:
        """Set or return the binning factor for the X axis.
        Args:
            BinX (int): The X binning value.

        Returns:
            Binning factor for the X axis.

        """
        if BinX is None:
            return self._get("binx")
        self._put("binx", BinX=BinX)

    def biny(self, BinY: Optional[int] = None) -> int:
        """Set or return the binning factor for the Y axis.
        Args:
            BinY (int): The Y binning value.

        Returns:
            Binning factor for the Y axis.

        """
        if BinY is None:
            return self._get("biny")
        self._put("biny", BinY=BinY)

    def camerastate(self) -> int:
        """Return the camera operational state.
        Notes:
            0 = CameraIdle, 1 = CameraWaiting, 2 = CameraExposing,
            3 = CameraReading, 4 = CameraDownload, 5 = CameraError.

        Returns:
            Current camera operational state as an integer.

        """
        return self._get("camerastate")

    def cameraxsize(self) -> int:
        """Return the width of the CCD camera chip."""
        return self._get("cameraxsize")

    def cameraysize(self) -> int:
        """Return the height of the CCD camera chip."""
        return self._get("cameraysize")

    def canabortexposure(self) -> bool:
        """Indicate whether the camera can abort exposures."""
        return self._get("canabortexposure")

    def canasymmetricbin(self) -> bool:
        """Indicate whether the camera supports asymmetric binning."""
        return self._get("canasymmetricbin")

    def canfastreadout(self) -> bool:
        """Indicate whether the camera has a fast readout mode."""
        return self._get("canfastreadout")

    def cangetcoolerpower(self) -> bool:
        """Indicate whether the camera's cooler power setting can be read."""
        return self._get("cangetcoolerpower")

    def canpulseguide(self) -> bool:
        """Indicate whether this camera supports pulse guiding."""
        return self._get("canpulseguide")

    def cansetccdtemperature(self) -> bool:
        """Indicate whether this camera supports setting the CCD temperature."""
        return self._get("cansetccdtemperature")

    def canstopexposure(self) -> bool:
        """Indicate whether this camera can stop an exposure that is in progress."""
        return self._get("canstopexposure")

    def ccdtemperature(self) -> float:
        """Return the current CCD temperature in degrees Celsius."""
        return self._get("ccdtemperature")

    def cooleron(self, CoolerOn: Optional[bool] = None) -> bool:
        """Turn the camera cooler on and off or return the current cooler on/off state.
        Notes:
            True = cooler on, False = cooler off.
        Args:
            CoolerOn (bool): Cooler state.

        Returns:
            Current cooler on/off state.

        """
        if CoolerOn is None:
            return self._get("cooleron")
        self._put("cooleron", CoolerOn=CoolerOn)

    def coolerpower(self) -> float:
        """Return the present cooler power level, in percent."""
        return self._get("coolerpower")

    def electronsperadu(self) -> object:
        """Return the gain of the camera in photoelectrons per A/D unit."""
        return self._get("electronsperadu")

    def exposuremax(self) -> float:
        """Return the maximum exposure time supported by StartExposure."""
        return self._get("exposuremax")

    def exposuremin(self) -> float:
        """Return the minimum exposure time supported by StartExposure."""
        return self._get("exposuremin")

    def exposureresolution(self) -> float:
        """Return the smallest increment in exposure time supported by StartExposure."""
        return self._get("exposureresolution")

    def fastreadout(self, FastReadout: Optional[bool] = None) -> bool:
        """Set or return whether Fast Readout Mode is enabled.
        Args:
            FastReadout (bool): True to enable fast readout mode.

        Returns:
            Whether Fast Readout Mode is enabled.
        """
        if FastReadout is None:
            return self._get("fastreadout")
        self._put("fastreadout", FastReadout=FastReadout)

    def fullwellcapacity(self) -> float:
        """Report the full well capacity of the camera.
        Report the full well capacity of the camera in electrons, at the current
        camera settings (binning, SetupDialog settings, etc.).
        Returns:
            Full well capacity of the camera.
        """
        return self._get("fullwellcapacity")

    def gain(self, Gain: Optional[int] = None) -> int:
        """Set or return an index into the Gains array.
        Args:
            Gain (int): Index of the current camera gain in the Gains string array.

        Returns:
            Index into the Gains array for the selected camera gain.

        """
        if Gain is None:
            return self._get("gain")
        self._put("gain", Gain=Gain)

    def gainmax(self) -> int:
        """Maximum value of Gain."""
        return self._get("gainmax")

    def gainmin(self) -> int:
        """Minimum value of Gain."""
        return self._get("gainmin")

    def gains(self) -> List[int]:
        """Gains supported by the camera."""
        return self._get("gains")

    def hasshutter(self) -> bool:
        """Indicate whether the camera has a mechanical shutter."""
        return self._get("hasshutter")

    def heatsinktemperature(self) -> float:
        """Return the current heat sink temperature.
        Returns:
            Current heat sink temperature (called "ambient temperature" by some
            manufacturers) in degrees Celsius.
        """
        return self._get("heatsinktemperature")

    def imagearray(self) -> List[int]:
        r"""Return an array of integers containing the exposure pixel values.
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
        This regular expression accomplishes the extraction into two named groups Type
        and Rank ^*"Type":(?<Type>\d*),"Rank":(?<Rank>\d*) which can then be used to
        select the correct de-serialisation data class.
        Returns:
            Array of integers containing the exposure pixel values.

        """
        return self._get("imagearray")

    def imagearrayvariant(self) -> List[int]:
        r"""Return an array of integers containing the exposure pixel values.
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
        This regular expression accomplishes the extraction into two named groups Type
        and Rank ^*"Type":(?<Type>\d*),"Rank":(?<Rank>\d*) which can then be used to
        select the correct de-serialisation data class.
        Returns:
            Array of integers containing the exposure pixel values.

        """
        return self._get("imagearrayvariant")

    def imageready(self) -> bool:
        """Indicate that an image is ready to be downloaded."""
        return self._get("imageready")

    def ispulseguiding(self) -> bool:
        """Indicatee that the camera is pulse guideing."""
        return self._get("ispulseguiding")

    def lastexposureduration(self) -> float:
        """Report the actual exposure duration in seconds (i.e. shutter open time)."""
        return self._get("lastexposureduration")

    def lastexposurestarttime(self) -> str:
        """Start time of the last exposure in FITS standard format.

        Reports the actual exposure start in the FITS-standard
        CCYY-MM-DDThh:mm:ss[.sss...] format.
        Returns:
            Start time of the last exposure in FITS standard format.
        """
        return self._get("lastexposurestarttime")

    def maxadu(self) -> int:
        """Camera's maximum ADU value."""
        return self._get("maxadu")

    def maxbinx(self) -> int:
        """Maximum binning for the camera X axis."""
        return self._get("maxbinx")

    def maxbiny(self) -> int:
        """Maximum binning for the camera Y axis."""
        return self._get("maxbiny")

    def numx(self, NumX: Optional[int] = None) -> int:
        """Set or return the current subframe width.

        Args:
            NumX (int): Subframe width, if binning is active, value is in binned
                pixels.

        Returns:
            Current subframe width.

        """
        if NumX is None:
            return self._get("numx")
        self._put("numx", NumX=NumX)

    def numy(self, NumY: Optional[int] = None) -> int:
        """Set or return the current subframe height.

        Args:
            NumY (int): Subframe height, if binning is active, value is in binned
                pixels.

        Returns:
            Current subframe height.

        """
        if NumY is None:
            return self._get("numy")
        self._put("numy", NumY=NumY)

    def percentcompleted(self) -> int:
        """Indicate percentage completeness of the current operation.
        Returns:
            If valid, returns an integer between 0 and 100, where 0 indicates 0%
            progress (function just started) and 100 indicates 100% progress (i.e.
            completion).

        """
        return self._get("percentcompleted")

    def pixelsizex(self):
        """Width of CCD chip pixels (microns)."""
        return self._get("pixelsizex")

    def pixelsizey(self):
        """Height of CCD chip pixels (microns)."""
        return self._get("pixelsizey")

    def readoutmode(self, ReadoutMode: Optional[int] = None) -> int:
        """Indicate the canera's readout mode as an index into the array ReadoutModes."""
        if ReadoutMode is None:
            return self._get("readoutmode")
        self._put("readoutmode", ReadoutMode=ReadoutMode)

    def readoutmodes(self) -> List[int]:
        """List of available readout modes."""
        return self._get("readoutmodes")

    def sensorname(self) -> str:
        """Name of the sensor used within the camera."""
        return self._get("sensorname")

    def sensortype(self) -> int:
        """Type of information returned by the the camera sensor (monochrome or colour).

        Notes:
            0 = Monochrome, 1 = Colour not requiring Bayer decoding, 2 = RGGB Bayer
            encoding, 3 = CMYG Bayer encoding, 4 = CMYG2 Bayer encoding, 5 = LRGB
            TRUESENSE Bayer encoding.

        Returns:
            Value indicating whether the sensor is monochrome, or what Bayer matrix it
            encodes.

        """
        return self._get("sensortype")

    def setccdtemperature(self, SetCCDTemperature: Optional[float] = None) -> float:
        """Set or return the camera's cooler setpoint (degrees Celsius).
        Args:
            SetCCDTemperature (float): 	Temperature set point (degrees Celsius).

        Returns:
            Camera's cooler setpoint (degrees Celsius).

        """
        if SetCCDTemperature is None:
            return self._get("setccdtemperature")
        self._put("setccdtemperature", SetCCDTemperature=SetCCDTemperature)

    def startx(self, StartX: Optional[int] = None) -> int:
        """Set or return the current subframe X axis start position.
        Args:
            StartX (int): The subframe X axis start position in binned pixels.

        Returns:
            Sets the subframe start position for the X axis (0 based) and returns the
            current value. If binning is active, value is in binned pixels.

        """
        if StartX is None:
            return self._get("startx")
        self._put("startx", StartX=StartX)

    def starty(self, StartY: Optional[int] = None) -> int:
        """Set or return the current subframe Y axis start position.
        Args:
            StartY (int): The subframe Y axis start position in binned pixels.

        Returns:
            Sets the subframe start position for the Y axis (0 based) and returns the
            current value. If binning is active, value is in binned pixels.

        """
        if StartY is None:
            return self._get("starty")
        self._put("starty", StartY=StartY)

    def abortexposure(self):
        """Abort the current exposure, if any, and returns the camera to Idle state."""
        self._put("abortexposure")

    def pulseguide(self, Direction: int, Duration: int):
        """Pulse guide in the specified direction for the specified time.

        Args:
            Direction (int): Direction of movement (0 = North, 1 = South, 2 = East,
                3 = West).
            Duration (int): Duration of movement in milli-seconds.

        """
        self._put("pulseguide", Direction=Direction, Duration=Duration)

    def startexposure(self, Duration: float, Light: bool):
        """Start an exposure.

        Notes:
            Use ImageReady to check when the exposure is complete.

        Args:
            Duration (float): Duration of exposure in seconds.
            Light (bool): True if light frame, false if dark frame.
        """
        self._put("startexposure", Duration=Duration, Light=Light)

    def stopexposure(self):
        """Stop the current exposure, if any.

        Notes:
            If an exposure is in progress, the readout process is initiated. Ignored if
            readout is already in process.

        """
        self._put("stopexposure")


class FilterWheel(Device):
    """Filter wheel specific methods."""

    def __init__(
            self,
            address: str,
            device_number: int,
            protocol: str = "http",
            api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize FilterWheel object."""
        super().__init__(address, "filterwheel", device_number, protocol, api_version)

    def focusoffsets(self) -> List[int]:
        """Filter focus offsets.
        Returns:
            An integer array of filter focus offsets.

        """
        return self._get("focusoffsets")

    def names(self) -> List[str]:
        """Filter wheel filter names.
        Returns:
            Names of the filters.
        """
        return self._get("names")

    def position(self, Position: Optional[int] = None):
        """Set or return the filter wheel position.
        Args:
            Position (int): Number of the filter wheel position to select.
        Returns:
            Returns the current filter wheel position.

        """
        if Position is None:
            return self._get("position")
        self._put("position", Position=Position)


class Telescope(Device):
    """Telescope specific methods."""
    __all__ = [
               ]

    logger = logging.getLogger(__name__)

    def __init__(
            self,
            address: str,
            device_number: int,
            protocol: str = "http",
            api_version: int = DEFAULT_API_VERSION,
    ):
        """Initialize Telescope object."""
        super().__init__(address, "telescope", device_number, protocol, api_version)

    def alignmentmode(self):
        """Return the current mount alignment mode.
        Returns:
            Alignment mode of the mount (Alt/Az, Polar, German Polar).

        """
        return self._get("alignmentmode")

    def altitude(self):
        """Return the mount's Altitude above the horizon.
        Returns:
            Altitude of the telescope's current position (degrees, positive up).
        """
        return self._get("altitude")

    def aperturearea(self):
        """Return the telescope's aperture.
        Returns:
            Area of the telescope's aperture (square meters).
        """
        return self._get("aperturearea")

    def aperturediameter(self):
        """Return the telescope's effective aperture.
        Returns:
            Telescope's effective aperture diameter (meters).
        """
        return self._get("aperturediameter")

    def athome(self):
        """Indicate whether the mount is at the home position.
        Returns:
            True if the mount is stopped in the Home position. Must be False if the
            telescope does not support homing.

        """
        return self._get("athome")

    def atpark(self):
        """Indicate whether the telescope is at the park position.
        Returns:
            True if the telescope has been put into the parked state by the set park()
            method. Set False by calling the unpark() method.

        """
        return self._get("atpark")

    def azimuth(self):
        """Return the telescope's aperture.

        Return:
            Azimuth of the telescope's current position (degrees, North-referenced,
            positive East/clockwise).
        """
        return self._get("azimuth")

    def canfindhome(self):
        """Indicate whether the mount can find the home position.

        Returns:
            True if this telescope is capable of programmed finding its home position.

        """
        return self._get("canfindhome")

    def canpark(self):
        """Indicate whether the telescope can be parked.
        Returns:
            True if this telescope is capable of programmed parking.

        """
        return self._get("canpark")

    def canpulseguide(self):
        """Indicate whether the telescope can be pulse guided.
        Returns:
            True if this telescope is capable of software-pulsed guiding (via the
            pulseguide(int, int) method).

        """
        return self._get("canpulseguide")

    def cansetdeclinationrate(self):
        """Indicate whether the DeclinationRate property can be changed.
        Returns:
            True if the DeclinationRate property can be changed to provide offset
            tracking in the declination axis.
        """
        return self._get("cansetdeclinationrate")

    def cansetguiderates(self):
        """Indicate whether the DeclinationRate property can be changed.
        Returns:
            True if the guide rate properties used for pulseguide(int, int) can ba
            adjusted.
        """
        return self._get("cansetguiderates")

    def cansetpark(self):
        """Indicate whether the telescope park position can be set.
        Returns:
            True if this telescope is capable of programmed setting of its park position
            (setpark() method).
        """
        return self._get("cansetpark")

    def cansetpierside(self):
        """Indicate whether the telescope SideOfPier can be set.
        Returns:
            True if the SideOfPier property can be set, meaning that the mount can be
            forced to flip.

        """
        return self._get("cansetpierside")

    def cansetrightascensionrate(self):
        """Indicate whether the RightAscensionRate property can be changed.
        Returns:
            True if the RightAscensionRate property can be changed to provide offset
            tracking in the right ascension axis.

        """
        return self._get("cansetrightascensionrate")

    def cansettracking(self):
        """Indicate whether the Tracking property can be changed.
        Returns:
            True if the Tracking property can be changed, turning telescope sidereal
            tracking on and off.

        """
        return self._get("cansettracking")

    def canslew(self):
        """Indicate whether the telescope can slew synchronously.
        Returns:
            True if this telescope is capable of programmed slewing (synchronous or
            asynchronous) to equatorial coordinates.

        """
        return self._get("canslew")

    def canslewaltaz(self):
        """Indicate whether the telescope can slew synchronously to AltAz coordinates.
        Returns:
            True if this telescope is capable of programmed slewing (synchronous or
            asynchronous) to local horizontal coordinates.
        """
        return self._get("canslewaltaz")

    def canslewaltazasync(self):
        """Indicate whether the telescope can slew asynchronusly to AltAz coordinates.
        Returns:
            True if this telescope is capable of programmed asynchronus slewing
            (synchronous or asynchronous) to local horizontal coordinates.
        """
        return self._get("canslewaltazasync")

    def cansync(self):
        """Indicate whether the telescope can sync to equatorial coordinates.
        Returns:
            True if this telescope is capable of programmed synching to equatorial
            coordinates.

        """
        return self._get("cansync")

    def cansyncaltaz(self):
        """Indicate whether the telescope can sync to local horizontal coordinates.
        Returns:
            True if this telescope is capable of programmed synching to local horizontal
            coordinates.

        """
        return self._get("cansyncaltaz")

    def declination(self):
        """Return the telescope's declination.
        Notes:
            Reading the property will raise an error if the value is unavailable.
        Returns:
            The declination (degrees) of the telescope's current equatorial coordinates,
            in the coordinate system given by the EquatorialSystem property.

        """
        return self._get("declination")

    def declinationrate(self, DeclinationRate: Optional[float] = None):
        """Set or return the telescope's declination tracking rate.
        Args:
            DeclinationRate (float): Declination tracking rate (arcseconds per second).

        Returns:
            The declination tracking rate (arcseconds per second) if DeclinationRate is
            not set.

        """
        if DeclinationRate is None:
            return self._get("declinationrate")
        self._put("declinationrate", DeclinationRate=DeclinationRate)

    def doesrefraction(self, DoesRefraction: Optional[bool] = None):
        """Indicate or determine if atmospheric refraction is applied to coordinates.
        Args:
            DoesRefraction (bool): Set True to make the telescope or driver apply
                atmospheric refraction to coordinates.

        Returns:
            True if the telescope or driver applies atmospheric refraction to
            coordinates.
        """
        if DoesRefraction is None:
            return self._get("doesrefraction")
        self._put("doesrefraction", DoesRefraction=DoesRefraction)

    def equatorialsystem(self):
        """Return the current equatorial coordinate system used by this telescope.
        Returns:
            Current equatorial coordinate system used by this telescope
            (e.g. Topocentric or J2000).
        """
        return self._get("equatorialsystem")

    def focallength(self):
        """Return the telescope's focal length in meters.
        Returns:
            The telescope's focal length in meters.
        """
        return self._get("focallength")

    def guideratedeclination(self, GuideRateDeclination: Optional[float] = None):
        """Set or return the current Declination rate offset for telescope guiding.
        Args:
            GuideRateDeclination (float): Declination movement rate offset
                (degrees/sec).
        Returns:
            Current declination rate offset for telescope guiding if not set.
        """
        if GuideRateDeclination is None:
            return self._get("guideratedeclination")
        self._put("guideratedeclination", GuideRateDeclination=GuideRateDeclination)

    def guideraterightascension(self, GuideRateRightAscension: Optional[float] = None):
        """Set or return the current RightAscension rate offset for telescope guiding.
        Args:
            GuideRateRightAscension (float): RightAscension movement rate offset
                (degrees/sec).
        Returns:
            Current right ascension rate offset for telescope guiding if not set.
        """
        if GuideRateRightAscension is None:
            return self._get("guideraterightascension")
        self._put(
            "guideraterightascension", GuideRateRightAscension=GuideRateRightAscension
        )

    def ispulseguiding(self):
        """Indicate whether the telescope is currently executing a PulseGuide command.
        Returns:
            True if a pulseguide(int, int) command is in progress, False otherwise.

        """
        return self._get("ispulseguiding")

    def rightascension(self):
        """Return the telescope's right ascension coordinate.
        Returns:
            The right ascension (hours) of the telescope's current equatorial
            coordinates, in the coordinate system given by the EquatorialSystem
            property.
        """
        return self._get("rightascension")

    def rightascensionrate(self, RightAscensionRate: Optional[float] = None):
        """Set or return the telescope's right ascension tracking rate.
        Args:
            RightAscensionRate (float): Right ascension tracking rate (arcseconds per
                second).
        Returns:
            Telescope's right ascension tracking rate if not set.
        """
        if RightAscensionRate is None:
            return self._get("rightascensionrate")
        self._put("rightascensionrate", RightAscensionRate=RightAscensionRate)

    def sideofpier(self, SideOfPier: Optional[int] = None):
        """Set or return the mount's pointing state.
        Args:
            SideOfPier (int): New pointing state. 0 = pierEast, 1 = pierWest

        Returns:
            Side of pier if not set.

        """
        if SideOfPier is None:
            return self._get("sideofpier")
        self._put("sideofpier", SideOfPier=SideOfPier)

    def siderealtime(self):
        """Return the local apparent sidereal time.
        Returns:
            The local apparent sidereal time from the telescope's internal clock (hours,
            sidereal).
        """
        return self._get("siderealtime")

    def siteelevation(self, SiteElevation: Optional[float] = None):
        """Set or return the observing site's elevation above mean sea level.
        Args:
            SiteElevation (float): Elevation above mean sea level (metres).

        Returns:
            Elevation above mean sea level (metres) of the site at which the telescope
            is located if not set.
        """
        if SiteElevation is None:
            return self._get("siteelevation")
        self._put("siteelevation", SiteElevation=SiteElevation)

    def sitelatitude(self, SiteLatitude: Optional[float] = None):
        """Set or return the observing site's latitude.
        Args:
            SiteLatitude (float): Site latitude (degrees).

        Returns:
            Geodetic(map) latitude (degrees, positive North, WGS84) of the site at which
            the telescope is located if not set.

        """
        if SiteLatitude is None:
            return self._get("sitelatitude")
        self._put("sitelatitude", SiteLatitude=SiteLatitude)

    def sitelongitude(self, SiteLongitude: Optional[float] = None):
        """Set or return the observing site's longitude.
        Args:
            SiteLongitude (float): Site longitude (degrees, positive East, WGS84)

        Returns:
            Longitude (degrees, positive East, WGS84) of the site at which the telescope
            is located.

        """
        if SiteLongitude is None:
            return self._get("sitelongitude")
        self._put("sitelongitude", SiteLongitude=SiteLongitude)

    def slewing(self):
        """Indicate whether the telescope is currently slewing.
        Returns:
            True if telescope is currently moving in response to one of the Slew methods
            or the moveaxis(int, float) method, False at all other times.
        """
        return self._get("slewing")

    def slewsettletime(self, SlewSettleTime: Optional[int] = None):
        """Set or return the post-slew settling time.
        Args:
            SlewSettleTime (int): Settling time (integer sec.).
        Returns:
            Returns the post-slew settling time (sec.) if not set.
        """
        if SlewSettleTime is None:
            return self._get("slewsettletime")
        self._put("slewsettletime", SlewSettleTime=SlewSettleTime)

    def targetdeclination(self, TargetDeclination: Optional[float] = None):
        """Set or return the target declination of a slew or sync.
        Args:
            TargetDeclination (float): Target declination(degrees)

        Returns:
            Declination (degrees, positive North) for the target of an equatorial slew
            or sync operation.

        """
        if TargetDeclination is None:
            return self._get("targetdeclination")
        self._put("targetdeclination", TargetDeclination=TargetDeclination)

    def targetrightascension(self, TargetRightAscension: Optional[float] = None):
        """Set or return the current target right ascension.
        Args:
            TargetRightAscension (float): Target right ascension (hours).

        Returns:
            Right ascension (hours) for the target of an equatorial slew or sync
            operation.
        """
        if TargetRightAscension is None:
            return self._get("targetrightascension")
        self._put("targetrightascension", TargetRightAscension=TargetRightAscension)

    def tracking(self, Tracking: Optional[bool] = None):
        """Enable, disable, or indicate whether the telescope is tracking.
        Args:
            Tracking (bool): Tracking enabled / disabled.

        Returns:
            State of the telescope's sidereal tracking drive.

        """
        if Tracking is None:
            return self._get("tracking")
        self._put("tracking", Tracking=Tracking)

    def trackingrate(self, TrackingRate: Optional[int] = None):
        """Set or return the current tracking rate.
        Args:
            TrackingRate (int): New tracking rate. 0 = driveSidereal, 1 = driveLunar,
                2 = driveSolar, 3 = driveKing.

        Returns:
            Current tracking rate of the telescope's sidereal drive if not set.

        """
        if TrackingRate is None:
            return self._get("trackingrate")
        self._put("trackingrate", TrackingRate=TrackingRate)

    def trackingrates(self):
        """Return a collection of supported DriveRates values.
        Returns:
            List of supported DriveRates values that describe the permissible values of
            the TrackingRate property for this telescope type.
        """
        return self._get("trackingrates")

    def utcdate(self, UTCDate: Optional[Union[str, datetime]] = None):
        """Set or return the UTC date/time of the telescope's internal clock.
        Args:
            UTCDate: UTC date/time as an str or datetime.

        Returns:
            datetime of the UTC date/time if not set.

        """
        if UTCDate is None:
            return dateutil.parser.parse(self._get("utcdate"))

        if type(UTCDate) is str:
            data = UTCDate
        elif type(UTCDate) is datetime:
            data = UTCDate.isoformat()
        else:
            raise TypeError()

        self._put("utcdate", UTCDate=data)

    def abortslew(self):
        """Immediately stops a slew in progress."""
        self._put("abortslew")

    def axisrates(self, Axis: int):
        """Return rates at which the telescope may be moved about the specified axis.
        Returns:
            The rates at which the telescope may be moved about the specified axis by
            the moveaxis(int, float) method.

        """
        return self._get("axisrates", Axis=Axis)

    def canmoveaxis(self, Axis: int):
        """Indicate whether the telescope can move the requested axis.
        Returns:
            True if this telescope can move the requested axis.
        """
        return self._get("canmoveaxis", Axis=Axis)

    def destinationsideofpier(self, RightAscension: float, Declination: float):
        """Predict the pointing state after a German equatorial mount slews to given coordinates.
        Args:
            RightAscension (float): Right Ascension coordinate (0.0 to 23.99999999
                hours).
            Declination (float): Declination coordinate (-90.0 to +90.0 degrees).
        Returns:
            Pointing state that a German equatorial mount will be in if it slews to the
            given coordinates. The return value will be one of - 0 = pierEast,
            1 = pierWest, -1 = pierUnknown.
        """
        return self._get(
            "destinationsideofpier",
            RightAscension=RightAscension,
            Declination=Declination,
        )

    def findhome(self):
        """Move the mount to the "home" position."""
        self._put("findhome")

    def moveaxis(self, Axis: int, Rate: float):
        """Move a telescope axis at the given rate.
        Args:
            Axis (int): The axis about which rate information is desired.
                0 = axisPrimary, 1 = axisSecondary, 2 = axisTertiary.
            Rate (float): The rate of motion (deg/sec) about the specified axis
        """
        self._put("moveaxis", Axis=Axis, Rate=Rate)

    def park(self):
        """Park the mount."""
        self._put("park")

    def pulseguide(self, Direction: int, Duration: int):
        """Move the scope in the given direction for the given time.
        Notes:
            0 = guideNorth, 1 = guideSouth, 2 = guideEast, 3 = guideWest.
        Args:
            Direction (int): Direction in which the guide-rate motion is to be made.
            Duration (int): Duration of the guide-rate motion (milliseconds).

        """
        self._put("pulseguide", Direction=Direction, Duration=Duration)

    def setpark(self):
        """Set the telescope's park position."""
        self._put("setpark")

    def slewtoaltaz(self, Azimuth: float, Altitude: float):
        """Slew synchronously to the given local horizontal coordinates.
        Args:
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).
        """
        self._put("slewtoaltaz", Azimuth=Azimuth, Altitude=Altitude)

    def slewtoaltazasync(self, Azimuth: float, Altitude: float):
        """Slew asynchronously to the given local horizontal coordinates.
        Args:
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).
        """
        self._put("slewtoaltazasync", Azimuth=Azimuth, Altitude=Altitude)

    def slewtocoordinates(self, RightAscension: float, Declination: float):
        """Slew synchronously to the given equatorial coordinates.
        Args:
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).
        """
        self._put(
            "slewtocoordinates", RightAscension=RightAscension, Declination=Declination
        )

    def slewtocoordinatesasync(self, RightAscension: float, Declination: float):
        """Slew asynchronously to the given equatorial coordinates.
        Args:
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).

        """
        self._put(
            "slewtocoordinatesasync",
            RightAscension=RightAscension,
            Declination=Declination,
        )

    def slewtotarget(self):
        """Slew synchronously to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("slewtotarget")

    def slewtotargetasync(self):
        """Asynchronously slew to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("slewtotargetasync")

    def synctoaltaz(self, Azimuth: float, Altitude: float):
        """Sync to the given local horizontal coordinates.
        Args:
            Azimuth (float): Azimuth coordinate (degrees, North-referenced, positive
                East/clockwise).
            Altitude (float): Altitude coordinate (degrees, positive up).
        """
        self._put("synctoaltaz", Azimuth=Azimuth, Altitude=Altitude)

    def synctocoordinates(self, RightAscension: float, Declination: float):
        """Sync to the given equatorial coordinates.
        Args:
            RightAscension (float): Right Ascension coordinate (hours).
            Declination (float): Declination coordinate (degrees).
        """
        self._put(
            "synctocoordinates", RightAscension=RightAscension, Declination=Declination
        )

    def synctotarget(self):
        """Sync to the TargetRightAscension and TargetDeclination coordinates."""
        self._put("synctotarget")

    def unpark(self):
        """Unpark the mount."""
        self._put("unpark")
