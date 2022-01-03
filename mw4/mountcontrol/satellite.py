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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging

# external packages
import skyfield.timelib
from skyfield.api import Angle

# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToAngle
from mountcontrol.convert import valueToFloat


class TLEParams(object):
    """
    The class TLEParams inherits all information and handling of TLE tracking
    and managing attributes of the connected mount and provides the abstracted
    interface to a 10 micron mount.

        >>> tleParams = TLEParams(host='')
    """

    __all__ = ['TLEParams',
               ]

    log = logging.getLogger(__name__)

    def __init__(self, obsSite=None):
        self.obsSite = obsSite
        self._azimuth = None
        self._altitude = None
        self._ra = None
        self._dec = None
        self._jdStart = None
        self._jdEnd = None
        self._flip = None
        self._message = None
        self._l0 = None
        self._l1 = None
        self._l2 = None
        self._name = None

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value):
        if isinstance(value, Angle):
            self._azimuth = value
            return
        self._azimuth = valueToAngle(value, preference='degrees')

    @property
    def altitude(self):
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        if isinstance(value, Angle):
            self._altitude = value
            return
        self._altitude = valueToAngle(value, preference='degrees')

    @property
    def ra(self):
        return self._ra

    @ra.setter
    def ra(self, value):
        if isinstance(value, Angle):
            self._ra = value
            return
        self._ra = valueToAngle(value, preference='hours')

    @property
    def dec(self):
        return self._dec

    @dec.setter
    def dec(self, value):
        if isinstance(value, Angle):
            self._dec = value
            return
        self._dec = valueToAngle(value, preference='degrees')

    @property
    def flip(self):
        return self._flip

    @flip.setter
    def flip(self, value):
        if isinstance(value, bool):
            self._flip = value
            return
        self._flip = bool(value == 'F')

    @property
    def jdStart(self):
        return self._jdStart

    @jdStart.setter
    def jdStart(self, value):
        value = valueToFloat(value)
        if value:
            self._jdStart = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
        else:
            self._jdStart = None

    @property
    def jdEnd(self):
        return self._jdEnd

    @jdEnd.setter
    def jdEnd(self, value):
        value = valueToFloat(value)
        if value:
            self._jdEnd = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
        else:
            self._jdEnd = None

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if value:
            self._message = value
        else:
            self._message = None

    @property
    def l0(self):
        return self._l0

    @l0.setter
    def l0(self, value):
        self._l0 = value

    @property
    def l1(self):
        return self._l1

    @l1.setter
    def l1(self, value):
        self._l1 = value

    @property
    def l2(self):
        return self._l2

    @l2.setter
    def l2(self, value):
        self._l2 = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value


class TrajectoryParams(object):
    """
    The class TrajectoryParams inherits all information and handling of TLE tracking
    and managing attributes of the connected mount and provides the abstracted
    interface to a 10 micron mount.

        >>> trajectoryParams = TrajectoryParams(host='')
    """

    __all__ = ['TLEParams',
               ]

    log = logging.getLogger(__name__)

    def __init__(self, obsSite=None):
        self._jdStart = None
        self._jdEnd = None
        self._flip = None
        self._message = None
        self.obsSite = obsSite
        self.offsetRA = None
        self.offsetDEC = None
        self.offsetDECcorr = None
        self.offsetTime = None

    @property
    def flip(self):
        return self._flip

    @flip.setter
    def flip(self, value):
        if value is None:
            self._flip = None
            return
        elif isinstance(value, bool):
            self._flip = value
            return
        self._flip = bool(value == 'F')

    @property
    def jdStart(self):
        return self._jdStart

    @jdStart.setter
    def jdStart(self, value):
        value = valueToFloat(value)
        if value:
            self._jdStart = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
        else:
            self._jdStart = None

    @property
    def jdEnd(self):
        return self._jdEnd

    @jdEnd.setter
    def jdEnd(self, value):
        value = valueToFloat(value)
        if value:
            self._jdEnd = self.obsSite.ts.tt_jd(value + self.obsSite.UTC2TT)
        else:
            self._jdEnd = None

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        if value:
            self._message = value
        else:
            self._message = None


class Satellite(object):
    """
    The class Satellite inherits all information and handling of TLE tracking
    and managing attributes of the connected mount and provides the abstracted
    interface to a 10 micron mount.
    Some of the basic commands of the 10micron mount are combined and sent as
    a bulk message. idea of the procedure is to program the TLE parameters
    first, than calculate the parameters with the mount computer. this could
    be done in a cyclic way, so that you could update theses results over time.
    As the calculation takes some time this call will also block your
    application some time. finally you could start the slewing process
    where the mount slews normally to the start of the satellite track and
    waits for it. when satellite reaches the altitude minimum, the mount
    starts to track.

    """

    __all__ = ['Satellite',
               ]

    log = logging.getLogger(__name__)

    TLES = {
        'E': 'No transit pre calculated',
        'F': 'Slew failed',
        'V': 'Slewing to start and track',
        'S': 'Slewing to catch satellite',
        'Q': 'Transit ended, no tracking',
    }

    TLESCK = {
        'V': 'Slewing to the start of the transit',
        'P': 'Waiting for the satellite',
        'S': 'Slewing to catch satellite',
        'T': 'Tracking the satellite',
        'Q': 'Transit ended, no tracking',
        'E': 'No slew to satellite requested'
    }

    def __init__(self, parent=None, host=None):
        self.host = host
        self.obsSite = parent.obsSite
        self.tleParams = TLEParams(obsSite=parent.obsSite)
        self.trajectoryParams = TrajectoryParams(obsSite=parent.obsSite)

    def parseGetTLE(self, response, numberOfChunks):
        """
        Parsing the GetTLE command and entering the resulting parameters. if no
        TLE parameters could be retrieved, they were set to None

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if response[0] == 'E':
            return False
        if numberOfChunks != 1:
            return False

        lines = response[0].split('$0A')
        if len(lines) != 4:
            return False

        self.tleParams.name = lines[0].rstrip()
        self.tleParams.l0 = lines[0]
        self.tleParams.l1 = lines[1]
        self.tleParams.l2 = lines[2]
        return True

    def getTLE(self):
        """
        Returns the currently-loaded two line elements.

        Returns:
        <two line elements>#    a string containing the two line elements.
                                Lines a terminated by the ASCII newline
                                character (ASCII code 10),
                                and the entire string is escaped with the
                                mechanism described in the "escaped strings"
                                section below. If no TLE is currently loaded,
                                returns the string E#.

        :return: success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':TLEG#')
        if not suc:
            return False

        suc = self.parseGetTLE(response, numberOfChunks)
        return suc

    def setTLE(self, line0='', line1='', line2=''):
        """
        Loads satellite orbital elements in two-line format directly from the
        command protocol. <two line element> is a string containing the two
        line elements. Each lines can be terminated by escaped newline (ASCII
        code 10), carriage return (ASCII code 13) or a combination of both. The
        first line may contain the satellite name. The entire string is escaped
        with the mechanism described in the "escaped strings" section below.

        The TLE format is described here:
        https://www.celestrak.com/NORAD/documentation/tle-fmt.asp
        For example, loading the NOAA 14 element set of that page can be
        accomplished with:

        TLEL0NOAA·14·················
        1·23455U·94089A···97320.90946019··.00000140··00000-0··10191-3·0··2621
        2·23455··99.0090·272.6745·0008546·223.1686·136.8816·14.11711747148495

        Returns:
        E# invalid format
        V# valid format

        :param line0:
        :param line1:
        :param line2:
        :return: success
        """
        if not line0 or not line1 or not line2:
            return False
        if len(line1) != 69:
            return False
        if len(line2) != 69:
            return False

        commandString = f':TLEL0{line0}$0a{line1}$0a{line2}#'
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response == 'E':
            return False
        if numberOfChunks != 1:
            return False

        return suc

    def parseCalcTLE(self, response, numberOfChunks):
        """
        Parsing the CalcTLE command and entering the resulting parameters. if
        no calculation could be made, the parameters were set to None

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != 3:
            self.log.warning('wrong number of chunks')
            return False
        if response[0] == 'E':
            return False
        if response[1] == 'E':
            return False
        if response[2] == 'E':
            return False

        value = response[0].split(',')
        if len(value) != 2:
            return False
        alt, az = value

        value = response[1].split(',')
        if len(value) != 2:
            return False
        ra, dec = value

        value = response[2].split(',')
        if len(value) == 3:
            start, end, flip = value
        elif len(value) == 1:
            flip = value[0]
            start = None
            end = None
        else:
            return False

        self.tleParams.altitude = alt
        self.tleParams.azimuth = az
        self.tleParams.ra = ra
        self.tleParams.dec = dec
        self.tleParams.flip = flip
        self.tleParams.jdStart = start
        self.tleParams.jdEnd = end
        return True

    def calcTLE(self, julD=None, duration=1440):
        """
        set of three commands !

        Pre calculates the first transit of the satellite with the currently
        loaded orbital elements, starting from Julian Date JD and for a period
        of min minutes, where min is from 1 to 1440. Two-line elements have to
        be loaded with the :TLEL command.

        Returns:
        E#                  no TLE loaded
        +AA.AAAA,ZZZ.ZZZZ#  the apparent alt azimuth coordinates,
                            where +AA.AAAA is the altitude in degrees with
                            decimals accounting for refraction,
                            and ZZZ.ZZZZ is the azimuth in degrees with
                            decimals.

        Returns:
        E# no TLE loaded
        RR.RRRRR,+DD.DDDD#  the apparent equatorial coordinates,
                            where RR.RRRRR is the
                            right ascension in hours with decimals,
                            and +DD.DDDD is the
                            declination in degrees with decimals.

        Gets the apparent alt azimuth coordinates of the satellite with the
        currently loaded orbital elements, computed for Julian Date JD (UTC).

        Returns:
        E#                      no TLE loaded or invalid command
        N#                      no passes in the given amount of time
        JD start,JD end,flags#  data for the first pass in the given interval.
                                JD start and JD end mark the beginning and the
                                end of the given transit. Flags is a string
                                which can be empty or contain the letter F –
                                meaning that mount will flip during the transit.

        Gets the apparent equatorial coordinates of the satellite with the
        currently loaded orbital elements, computed for Julian Date JD (UTC).

        :param julD:  julianDate as string
        :param duration:    duration in minutes
        :return: success
        """
        if julD is None:
            return False
        if isinstance(julD, skyfield.timelib.Time):
            julD = julD.tt

        # transformation UTC <-> TT time system
        julD -= self.obsSite.UTC2TT

        if not 0 < duration < 1441:
            return False

        conn = Connection(self.host)
        command = f':TLEGAZ{julD}#:TLEGEQ{julD}#:TLEP{julD},{duration}#'
        suc, response, numberOfChunks = conn.communicate(command)
        if not suc:
            return False

        suc = self.parseCalcTLE(response, numberOfChunks)
        return suc

    def getCoordsFromTLE(self, julD=None):
        """
        :param julD:
        :return:
        """
        if julD is None:
            return False
        if isinstance(julD, skyfield.timelib.Time):
            julD = julD.tt

        # transformation UTC <-> TT time system
        julD -= self.obsSite.UTC2TT

        conn = Connection(self.host)
        command = f':TLEGAZ{julD}#:TLEGEQ{julD}#'
        suc, response, numberOfChunks = conn.communicate(command)
        if not suc:
            return False

        value = response[0].split(',')
        if len(value) != 2:
            return False
        alt, az = value
        self.tleParams.altitude = alt
        self.tleParams.azimuth = az

        value = response[1].split(',')
        if len(value) != 2:
            return False
        ra, dec = value
        self.tleParams.ra = ra
        self.tleParams.dec = dec

        return True

    def slewTLE(self):
        """
        Slews to the start of the satellite transit that has been pre
        calculated with the :TLEP command.

        Returns:
        E# no transit has been pre calculated
        F# slew failed due to mount parked or other status blocking slews
        V# slewing to the start of the transit, the mount will automatically
            starts tracking the satellite.
        S# the transit has already started, slewing to catch the satellite
        Q# the transit has already ended, no slew occurs

        :return: success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':TLES#')
        if numberOfChunks != 1:
            return False, 'Error'

        message = self.TLES.get(response[0], 'Error')
        return suc, message

    def parseStatTLE(self, response, numberOfChunks):
        """
        Parsing the statTLE slow command.

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != 1:
            self.log.warning('wrong number of chunks')
            return False
        if not response[0]:
            return False

        self.tleParams.message = self.TLESCK.get(response[0], 'Error')
        return True

    def statTLE(self):
        """
        Gets the status of the slew to a pre calculated satellite transit.

        Returns:
        V# slewing to the start of the transit
        P# stopped at the start of the transit, waiting for the satellite
        S# slewing to catch the satellite
        T# tracking the satellite
        Q# the transit has ended, not tracking
        E# no slew to a satellite has been requested.

        :return: success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':TLESCK#')
        if not suc:
            return False

        suc = self.parseStatTLE(response, numberOfChunks)
        return suc

    def startProgTrajectory(self, julD=None):
        """
        :param julD:
        :return:
        """
        if julD is None:
            return False
        if isinstance(julD, skyfield.timelib.Time):
            julD = julD.tt

        # transformation UTC <-> TT time system
        julD -= self.obsSite.UTC2TT

        cmd = f':TRNEW{julD}#'
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != 1:
            self.log.warning('wrong number of chunks')
            return False
        if response[0] != 'V':
            return False

        return True

    def progTrajectory(self, alt=[], az=[]):
        """
        :param alt:
        :param az:
        :return:
        """
        if len(alt) == 0 or len(alt) != len(az):
            return False

        cmd = ''
        for azimuth, altitude in zip(az, alt):
            cmd += f':TRADD{azimuth},{altitude}#'

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != len(az):
            self.log.warning('wrong number of chunks')
            return False

        for i in range(0, len(az)):
            if response[i] == 'E':
                return False

        return True

    def calcTrajectory(self, replay=False):
        """
        :param replay:    start now
        :return: success
        """
        self.trajectoryParams.flip = None
        self.trajectoryParams.jdStart = None
        self.trajectoryParams.jdEnd = None

        if replay:
            cmd = ':TRREPLAY#'
        else:
            cmd = ':TRP#'

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != 1:
            self.log.warning('wrong number of chunks')
            return False

        # should be 'E' only , actually wrong 'N' in
        if response[0] in ['E', 'N']:
            return False

        value = response[0].split(',')
        if len(value) == 3:
            start, end, flip = value
        else:
            return False

        self.trajectoryParams.flip = flip
        self.trajectoryParams.jdStart = start
        self.trajectoryParams.jdEnd = end
        return True

    def getTrackingOffsets(self):
        """
        :return: success
        """
        cmd = ':TROFFGET1#:TROFFGET2#:TROFFGET3#:TROFFGET4#'
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != 4:
            self.log.warning('wrong number of chunks')
            return False

        val = valueToFloat(response[0])
        if val is not None:
            self.trajectoryParams.offsetRA = val

        val = valueToFloat(response[1])
        if val is not None:
            self.trajectoryParams.offsetDEC = val

        val = valueToFloat(response[2])
        if val is not None:
            self.trajectoryParams.offsetDECcorr = val

        val = valueToFloat(response[3])
        if val is not None:
            self.trajectoryParams.offsetTime = val

        return True

    def setTrackingOffsets(self, RA=None, DEC=None, DECcorr=None, Time=None):
        """
        :param RA:
        :param DEC:
        :param DECcorr:
        :param Time:
        :return:
        """
        cmd = ''
        responseLen = 0
        if RA is not None:
            cmd += f':TROFFSET1,{RA:+05.1f}#'
            responseLen += 1
        if DEC is not None:
            cmd += f':TROFFSET2,{DEC:+05.1f}#'
            responseLen += 1
        if DECcorr is not None:
            cmd += f':TROFFSET3,{DECcorr:+05.1f}#'
            responseLen += 1
        if Time is not None:
            cmd += f':TROFFSET4,{Time:+05.1f}#'
            responseLen += 1

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != responseLen:
            self.log.warning('wrong number of chunks')
            return False

        for res in response:
            if res == 'E':
                break
        else:
            return True
        return False

    def addTrackingOffsets(self, RA=None, DEC=None, DECcorr=None, Time=None):
        """
        :param RA:
        :param DEC:
        :param DECcorr:
        :param Time:
        :return:
        """
        cmd = ''
        responseLen = 0
        if RA is not None:
            cmd += f':TROFFADD1,{RA:+05.1f}#'
            responseLen += 1
        if DEC is not None:
            cmd += f':TROFFADD2,{DEC:+05.1f}#'
        responseLen += 1
        if DECcorr is not None:
            cmd += f':TROFFADD3,{DECcorr:+05.1f}#'
        responseLen += 1
        if Time is not None:
            cmd += f':TROFFADD4,{Time:+05.1f}#'
            responseLen += 1

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != responseLen:
            self.log.warning('wrong number of chunks')
            return False

        for res in response:
            if res == 'E':
                break
        else:
            return True
        return False

    def clearTrackingOffsets(self):
        """
        :return:
        """
        cmd = ':TROFFCLR#'

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(commandString=cmd)
        if not suc:
            return False

        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False
        if len(response) != 1:
            self.log.warning('wrong number of chunks')
            return False

        if response[0] == 'E':
            return False
        else:
            return True
