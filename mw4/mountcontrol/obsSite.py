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
import skyfield.api as api
import skyfield.starlib as starlib

# local imports
from .connection import Connection
from .convert import stringToAngle
from .convert import valueToFloat
from .convert import valueToInt
from .convert import valueToAngle
from .convert import sexagesimalizeToInt


class ObsSite(object):
    """
    The class Site inherits all information and handling of site data
    attributes of the connected mount and provides the abstracted interface
    to a 10 micron mount. as the mount's time base is julian date, we use this
    value as time base as well. for that reason we should remind how the mount
    calculates the julian date. it is derived from utc. to basically on the
    timeJD for skyfield we calculate julian date from ut1 based on julian date
    from mount based on utc and the value delta utc, ut1 also given from the
    mount.

        >>> site = ObsSite(
        >>>             host=host,
        >>>             pathToData=pathToData,
        >>>             verbose=verbose,
        >>>             location=(0, 0, 0),
        >>>             )

    The Site class needs as parameter a ts object from skyfield.api to
    be able to make all the necessary calculations about time from and to mount
    """

    __all__ = ['ObsSite',
               ]

    log = logging.getLogger(__name__)

    STAT = {
        '0': 'Tracking',
        '1': 'Stopped after STOP',
        '2': 'Slewing to park position',
        '3': 'Unparking',
        '4': 'Slewing to home position',
        '5': 'Parked',
        '6': 'Slewing or going to stop',
        '7': 'Tracking Off no move',
        '8': 'Motor low temperature',
        '9': 'Tracking outside limits',
        '10': 'Following Satellite',
        '11': 'User OK Needed',
        '98': 'Unknown Status',
        '99': 'Error',
    }

    def __init__(self,
                 host=None,
                 pathToData=None,
                 verbose=False,
                 ):

        self.host = host
        self.pathToData = pathToData
        self.verbose = verbose
        self.loader = None
        self._location = None
        self.ts = None
        self._timeJD = None
        self._utc_ut1 = None
        self._timeSidereal = None
        self._raJNow = None
        self._raJNowTarget = None
        self._decJNow = None
        self._decJNowTarget = None
        self._haJNow = None
        self._haJNowTarget = None
        self._sidereal = None
        self._angularPosRA = None
        self._angularPosDEC = None
        self._angularPosRATarget = None
        self._angularPosDECTarget = None
        self._pierside = None
        self._piersideTarget = None
        self._Alt = None
        self._AltTarget = None
        self._Az = None
        self._AzTarget = None
        self._status = None
        self._statusSlew = None
        self.setLoaderAndTimescale()

    def setLoaderAndTimescale(self):
        """
        :return:
        """
        if self.pathToData:
            self.loader = api.Loader(self.pathToData, verbose=self.verbose)
        else:
            self.loader = api.load

        self.ts = self.loader.timescale(builtin=True)
        self.log.debug('Timescale is using built-in')
        return True

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if isinstance(value, api.Topos):
            self._location = value
            return

        if not isinstance(value, (list, tuple)):
            self._location = None
            self.log.info(f'Malformed value: {value}')
            return

        if len(value) != 3:
            self._location = None
            self.log.info(f'Malformed value: {value}')
            return

        lat, lon, elev = value
        if not isinstance(lat, api.Angle):
            lat = stringToAngle(lat, preference='degrees')

        if not isinstance(lon, api.Angle):
            lon = stringToAngle(lon, preference='degrees')

        elev = valueToFloat(elev)
        if lat is None or lon is None or elev is None:
            self._location = None
            self.log.info(f'Malformed value: {value}')
            return

        self._location = api.Topos(longitude=lon,
                                   latitude=lat,
                                   elevation_m=elev)

    @property
    def timeJD(self):
        if self._timeJD is None:
            return self.ts.now()
        else:
            return self._timeJD

    @timeJD.setter
    def timeJD(self, value):
        value = valueToFloat(value)
        if value and self._utc_ut1 is not None:
            self._timeJD = self.ts.ut1_jd(value - self._utc_ut1)
        else:
            self._timeJD = None

    @property
    def utc_ut1(self):
        return self._utc_ut1

    @utc_ut1.setter
    def utc_ut1(self, value):
        value = valueToFloat(value)
        if value is not None:
            self._utc_ut1 = value / 86400
        else:
            self._utc_ut1 = None

    @property
    def timeSidereal(self):
        return self._timeSidereal

    @timeSidereal.setter
    def timeSidereal(self, value):
        if isinstance(value, str):
            self._timeSidereal = stringToAngle(value, preference='hours')
        elif isinstance(value, float):
            self._timeSidereal = valueToAngle(value, preference='hours')
        elif isinstance(value, api.Angle):
            self._timeSidereal = value
        else:
            self._timeSidereal = None

    @property
    def raJNow(self):
        return self._raJNow

    @raJNow.setter
    def raJNow(self, value):
        if isinstance(value, api.Angle):
            self._raJNow = value
            return
        self._raJNow = valueToAngle(value, preference='hours')

    @property
    def raJNowTarget(self):
        return self._raJNowTarget

    @raJNowTarget.setter
    def raJNowTarget(self, value):
        if isinstance(value, api.Angle):
            self._raJNowTarget = value
            return
        self._raJNowTarget = stringToAngle(value, preference='hours')

    @property
    def haJNow(self):
        if self._timeSidereal is None or self._raJNow is None:
            return None
        else:
            # ha is always positive between 0 and 24 hours
            ha = (self._timeSidereal.hours - self._raJNow.hours + 24) % 24
            return api.Angle(hours=ha)

    @property
    def haJNowTarget(self):
        if self._timeSidereal is None or self._raJNowTarget is None:
            return None
        else:
            # ha is always positive between 0 and 24 hours
            ha = (self._timeSidereal.hours - self._raJNowTarget.hours + 24) % 24
            return api.Angle(hours=ha)

    @property
    def decJNow(self):
        return self._decJNow

    @decJNow.setter
    def decJNow(self, value):
        if isinstance(value, api.Angle):
            self._decJNow = value
            return
        self._decJNow = valueToAngle(value, preference='degrees')

    @property
    def decJNowTarget(self):
        return self._decJNowTarget

    @decJNowTarget.setter
    def decJNowTarget(self, value):
        if isinstance(value, api.Angle):
            self._decJNowTarget = value
            return
        self._decJNowTarget = stringToAngle(value, preference='degrees')

    @property
    def angularPosRA(self):
        return self._angularPosRA

    @angularPosRA.setter
    def angularPosRA(self, value):
        if isinstance(value, api.Angle):
            self._angularPosRA = value
            return
        self._angularPosRA = valueToAngle(value, preference='degrees')

    @property
    def angularPosDEC(self):
        return self._angularPosDEC

    @angularPosDEC.setter
    def angularPosDEC(self, value):
        if isinstance(value, api.Angle):
            self._angularPosDEC = value
            return
        self._angularPosDEC = valueToAngle(value, preference='degrees')

    @property
    def angularPosRATarget(self):
        return self._angularPosRATarget

    @angularPosRATarget.setter
    def angularPosRATarget(self, value):
        if isinstance(value, api.Angle):
            self._angularPosRATarget = value
            return
        self._angularPosRATarget = valueToAngle(value, preference='degrees')

    @property
    def angularPosDECTarget(self):
        return self._angularPosDECTarget

    @angularPosDECTarget.setter
    def angularPosDECTarget(self, value):
        if isinstance(value, api.Angle):
            self._angularPosDECTarget = value
            return
        self._angularPosDECTarget = valueToAngle(value, preference='degrees')

    @property
    def pierside(self):
        return self._pierside

    @pierside.setter
    def pierside(self, value):
        if value in ['E', 'W', 'e', 'w']:
            value = value.capitalize()
            self._pierside = value
        else:
            self._pierside = None
            self.log.info(f'Malformed value: {value}')

    @property
    def piersideTarget(self):
        return self._piersideTarget

    @piersideTarget.setter
    def piersideTarget(self, value):
        if value == '2':
            self._piersideTarget = 'W'
        elif value == '3':
            self._piersideTarget = 'E'
        else:
            self._piersideTarget = None
            self.log.info(f'Malformed value: {value}')

    @property
    def Alt(self):
        return self._Alt

    @Alt.setter
    def Alt(self, value):
        if isinstance(value, api.Angle):
            self._Alt = value
            return
        self._Alt = valueToAngle(value, preference='degrees')

    @property
    def AltTarget(self):
        return self._AltTarget

    @AltTarget.setter
    def AltTarget(self, value):
        if isinstance(value, api.Angle):
            self._AltTarget = value
            return
        self._AltTarget = stringToAngle(value, preference='degrees')

    @property
    def Az(self):
        return self._Az

    @Az.setter
    def Az(self, value):
        if isinstance(value, api.Angle):
            self._Az = value
            return
        self._Az = valueToAngle(value, preference='degrees')

    @property
    def AzTarget(self):
        return self._AzTarget

    @AzTarget.setter
    def AzTarget(self, value):
        if isinstance(value, api.Angle):
            self._AzTarget = value
            return
        self._AzTarget = stringToAngle(value, preference='degrees')

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = valueToInt(value)
        if self._status not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 98, 99]:
            self._status = None

    def statusText(self):
        if self._status is None:
            return None
        reference = f'{self._status:d}'
        if reference in self.STAT:
            return self.STAT[reference]

    @property
    def statusSlew(self):
        return self._statusSlew

    @statusSlew.setter
    def statusSlew(self, value):
        self._statusSlew = bool(value)

    def parseLocation(self, response, numberOfChunks):
        """
        Parsing the polling slow command.

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.log.warning('Wrong number of chunks')
            return False
        elev = response[0]
        # due to compatibility to LX200 protocol east is negative, so we change that
        # in class we would like to keep the correct sign for east is positive
        lon = None
        if '-' in response[1]:
            lon = response[1].replace('-', '+')
        if '+' in response[1]:
            lon = response[1].replace('+', '-')
        lat = response[2]

        self.location = [lat, lon, elev]
        return True

    def getLocation(self):
        """
        Sending the polling command. As the mount need polling the data, I send
        a set of commands to get the data back to be able to process and store it.

        :return: success:   True if ok, False if not
        """

        conn = Connection(self.host)
        commandString = ':U2#:Gev#:Gg#:Gt#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self.parseLocation(response, numberOfChunks)
        return suc

    def parsePointing(self, response, numberOfChunks):
        """
        Parsing the polling fast command.

        :param response:        data load from mount
        :param numberOfChunks:  amount of parts
        :return: success:       True if ok, False if not
        """

        if len(response) != numberOfChunks:
            self.log.warning('Wrong number of chunks')
            return False
        self.timeSidereal = response[0]
        # remove the leap seconds flag if present
        self.utc_ut1 = response[1].replace('L', '')
        self.angularPosRA = response[2]
        self.angularPosDEC = response[3]
        responseSplit = response[4].split(',')
        self.raJNow = responseSplit[0]
        self.decJNow = responseSplit[1]
        self.pierside = responseSplit[2]
        self.Az = responseSplit[3]
        self.Alt = responseSplit[4]
        self.timeJD = responseSplit[5]
        self.status = responseSplit[6]
        self.statusSlew = (responseSplit[7] == '1')
        return True

    def pollPointing(self):
        """
        Sending the polling fast command. As the mount need polling the data, I send
        a set of commands to get the data back to be able to process and store it.

        :return: success:   True if ok, False if not
        """

        conn = Connection(self.host)
        commandString = ':U2#:GS#:GDUT#:GaXa#:GaXb#:Ginfo#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self.parsePointing(response, numberOfChunks)
        return suc

    def startSlewing(self, slewType='normal', forceUnpark=False):
        """
        startSlewing issues the final slew command to the mount after the target
        coordinates were set. before issuing the slewing command it automatically unpark
        the mount as well.

        the slew commands are:
            :MS#  :MA#  :MSap#  :MSao# :MaX#, :PiP#

        and return:
            0 no error
                if the target is below the lower limit: the string
            “1Object Below Horizon #”
                if the target is above the high limit: the string
            “2Object Below Higher #”
                if the slew cannot be performed due to another cause: the string
            “3Cannot Perform Slew #”
                if the mount is parked: the string
            “4Mount Parked #”
                if the mount is restricted to one side of the meridian and the object
                is on the other side: the string
            “5Object on the other side #”

        the types of slew is:
        - 'normal'      slew to coordinates and tracking on
        - 'notrack':    slew to coordinates and tracking off
        - 'stop':       slew to coordinates and park
        - 'park':       slew to coordinates and park
        - 'polar':      slew to coordinates and miss for polar alignment
        - 'ortho':      slew to coordinates and miss for orthogonal alignment
        - 'keep':       choose between normal and notrack to keep the tracking mode


        :param slewType:
        :return:
        """
        slewTypes = {
            'normal': ':MS#',
            'notrack': ':MA#',
            'stop': ':MaX#',
            'park': ':PaX#',
            'polar': ':MSap#',
            'ortho': ':MSao#',
            'keep': '',
        }

        if slewType not in slewTypes:
            return False

        if slewType == 'keep':
            if self.status == 0:
                slewTypes['keep'] = ':MS#'

            else:
                slewTypes['keep'] = ':MA#'

        conn = Connection(self.host)

        commandString = ':PO#' + slewTypes[slewType]
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if not response[0].startswith('0'):
            self.log.debug(f'Slew could not be done: [{response}]')
            return False

        return True

    def setTargetAltAz(self,
                       alt=None, az=None,
                       alt_degrees=None, az_degrees=None):
        """
        Slew AltAz unpark the mount sets the targets for alt and az and then
        issue the slew command.

        the unpark command is:
            :PO#
        and returns nothing

        setting alt target is the following:
            :SzDDD*MM# or :SzDDD*MM:SS# or :SzDDD*MM:SS.S#, we use the last one
            :SzDDD*MM:SS.S#

        setting az target is the following:
            :SasDD*MM# or :SasDD*MM:SS# or :SasDD*MM:SS.S#, we use the last one
            :SasDD*MM:SS.S#

        the slew command moves the mount and keeps tracking at the end of the move.
        in the command protocol it is written, that the targets should be ra / dec,
        but it works for targets defined with alt / az commands

        :param alt:     altitude in type Angle
        :param az:      azimuth in type Angle
        :param alt_degrees:     altitude in degrees float
        :param az_degrees:      azimuth in degrees float
        :return:        success
        """
        hasAngles = isinstance(alt, api.Angle) and isinstance(az, api.Angle)
        altHasFloat = isinstance(alt_degrees, (float, int))
        azHasFloat = isinstance(az_degrees, (float, int))

        if hasAngles:
            pass

        elif altHasFloat and azHasFloat:
            alt = api.Angle(degrees=alt_degrees)
            az = api.Angle(degrees=az_degrees)

        else:
            return False

        if alt.preference != 'degrees':
            return False

        if az.preference != 'degrees':
            return False

        conn = Connection(self.host)

        sgn, h, m, s, frac = sexagesimalizeToInt(alt.degrees, 1)
        sign = '+' if sgn >= 0 else '-'
        setAlt = f':Sa{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#'

        sgn, h, m, s, frac = sexagesimalizeToInt(az.degrees, 1)
        sign = '+' if sgn >= 0 else '-'
        setAz = f':Sz{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#'

        getTargetStatus = ':U2#:GTsid#:Ga#:Gz#:Gr#:Gd#'
        commandString = setAlt + setAz + getTargetStatus
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        result = response[0][0:2]
        if result.count('0') > 0:
            self.log.debug(f'Coordinates could not be set: [{response}]')
            return False

        if len(response) != 4:
            self.log.debug(f'Missing return values: [{response}]')
            return False

        self.piersideTarget = response[0][2]
        self.AltTarget = response[0][3:]
        self.AzTarget = response[1]
        self.raJNowTarget = response[2]
        self.decJNowTarget = response[3]
        return suc

    def setTargetRaDec(self,
                       ra=None, dec=None,
                       ra_hours=None, dec_degrees=None,
                       target=None):
        """
        Slew RaDec unpark the mount sets the targets for ra and dec and then
        issue the slew command.

        the unpark command is:
            :PO#
        and returns nothing

        setting ra target is the following:
            :SrHH:MM.T# or :SrHH:MM:SS# or :SrHH:MM:SS.S# or :SrHH:MM:SS.SS#
                , we use the last one
            :SrHH:MM:SS.SS#

        setting dec target is the following:
            :SdsDD*MM# or :SdsDD*MM:SS# or :Sd sDD*MM:SS.S#, we use the last one
            :SdsDD*MM:SS.S#

        the slew command moves the mount and keeps tracking at the end of the move.
        in the command protocol it is written, that the targets should be ra / dec,
        but it works for targets defined with alt / az commands

        :param ra:     right ascension in type Angle
        :param dec:    declination in type Angle preference 'hours'
        :param ra_hours: right ascension in float hours
        :param dec_degrees: declination in float degrees
        :param target:  star in type skyfield.Star
        :return:       success
        """
        hasTarget = isinstance(target, starlib.Star)
        hasAngles = isinstance(ra, api.Angle) and isinstance(dec, api.Angle)
        raHasFloat = isinstance(ra_hours, (float, int))
        decHasFloat = isinstance(dec_degrees, (float, int))
        if hasTarget:
            ra = target.ra
            dec = target.dec

        elif hasAngles:
            pass

        elif raHasFloat and decHasFloat:
            ra = api.Angle(hours=ra_hours, preference='hours')
            dec = api.Angle(degrees=dec_degrees)

        else:
            return False

        if ra.preference != 'hours' or dec.preference != 'degrees':
            return False

        conn = Connection(self.host)

        sgn, h, m, s, frac = sexagesimalizeToInt(ra.hours, 2)
        setRa = f':Sr{h:02d}:{m:02d}:{s:02d}.{frac:02d}#'

        sgn, h, m, s, frac = sexagesimalizeToInt(dec.degrees, 1)
        sign = '+' if sgn >= 0 else '-'
        setDec = f':Sd{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#'

        getTargetStatus = ':U2#:GTsid#:Ga#:Gz#:Gr#:Gd#'
        commandString = setRa + setDec + getTargetStatus
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        result = response[0][0:2]
        if result.count('0') > 0:
            self.log.debug(f'Coordinates could not be set: [{response}]')
            return False

        if len(response) != 4:
            self.log.debug(f'Missing return values: [{response}]')
            return False

        self.piersideTarget = response[0][2]
        self.AltTarget = response[0][3:]
        self.AzTarget = response[1]
        self.raJNowTarget = response[2]
        self.decJNowTarget = response[3]
        return suc

    def setTargetAngular(self,
                         ra=None, dec=None,
                         ra_degrees=None, dec_degrees=None,
                         target=None):
        """
        Slew RaDec unpark the mount sets the targets for ra and dec and then
        issue the slew command.

        the unpark command is:
            :PO#
        and returns nothing

        setting angular RA target is the following:
            :SaXasXXX.XXXX#

        setting angular DEC target is the following:
            ::SaXbsXXX.XXXX#

        :param ra:     right ascension in type Angle
        :param dec:    declination in type Angle preference 'hours'
        :param ra_degrees: right ascension in float degrees
        :param dec_degrees: declination in float degrees
        :param target:  star in type skyfield.Star
        :return:       success
        """
        hasTarget = isinstance(target, starlib.Star)
        hasAngles = isinstance(ra, api.Angle) and isinstance(dec, api.Angle)
        decHasFloat = isinstance(ra_degrees, (float, int))
        raHasFloat = isinstance(dec_degrees, (float, int))
        if hasTarget:
            ra = target.ra
            dec = target.dec

        elif hasAngles:
            pass

        elif raHasFloat and decHasFloat:
            ra = api.Angle(hours=ra_degrees)
            dec = api.Angle(degrees=dec_degrees)

        else:
            return False

        if dec.preference != 'degrees' or ra.preference != 'degrees':
            return False

        conn = Connection(self.host)
        raCommand = f':SaXa{ra.degrees:+03.4f}#'
        decCommand = f':SaXb{dec.degrees:+03.4f}#'
        getTargetStatus = ':U2#:GTsid#:Ga#:Gz#:Gr#:Gd#'
        commandString = raCommand + decCommand + getTargetStatus
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        result = response[0][0:2]
        if result.count('0') > 0:
            self.log.debug(f'Coordinates could not be set: [{response}]')
            return False

        if len(response) != 4:
            self.log.debug(f'Missing return values: [{response}]')
            return False

        # todo: actually SaXa and SaXb commands seem no to set other targets
        # self.piersideTarget = response[0][2]
        # self.AltTarget = response[0][3:]
        # self.AzTarget = response[1]
        # self.raJNowTarget = response[2]
        # self.decJNowTarget = response[3]
        return suc

    def shutdown(self):
        """
        shutdown send the shutdown command to the mount. if succeeded it takes about 20
        seconds before you could switch off the power supply. please check red LED at mount

        :return:    success
        """

        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':shutdown#')
        if not suc:
            return False
        if response[0] == '0':
            return False
        return True

    def setLocation(self, obs):
        """
        set SiteCoordinates sets the value in the mount to the given parameters.
        the longitude will be set for east negative, because that's the definition
        from the LX200 protocol, which the 10micron mount supports. internally we use
        the standard east positive.

        the site parameters could be set be the following commands:

        longitude (we will use the last one with the highest precision):

            :SgsDDD*MM# or :SgsDDD*MM:SS# or :SgsDDD*MM:SS.S#

            Set current site’s longitude to sDDD*MM (sign, degrees, arcminutes),
            sDDD*MM:SS (sign, degrees, arcminutes, arcseconds) or
            sDDD*MM:SS.S (sign, degrees, arcminutes, arcseconds and tenths of arcsecond).
            Note: East Longitudes are expressed as negative.
            Returns:
            0   invalid
            1   valid

        latitude (we will use the last one with the highest precision):

            :StsDD*MM# or :StsDD*MM:SS# or :StsDD*MM:SS.S#

            Sets the current site latitude to sDD*MM (sign, degrees, arcminutes),
            sDD*MM:SS (sign, degrees, arcminutes, arcseconds), or
            sDD*MM:SS.S (sign, degrees, arcminutes, arcseconds and tenths of arcsecond)

            Returns:
            0   invalid
            1   valid

        elevation:

            :SevsXXXX.X#

            Set current site’s elevation to sXXXX.X (sign, metres) in the
            range -1000.0 to 9999.9.
            Returns:
            0   invalid
            1   valid

        :param      obs:        skyfield.api.Topos of site
        :return:    success
        """
        if not isinstance(obs, api.Topos):
            return False

        conn = Connection(self.host)

        sgn, h, m, s, frac = sexagesimalizeToInt(obs.longitude.degrees, 1)
        sign = '+' if sgn < 0 else '-'
        setLon = f':Sg{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#'

        sgn, h, m, s, frac = sexagesimalizeToInt(obs.latitude.degrees, 1)
        sign = '+' if sgn >= 0 else '-'
        setLat = f':St{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#'

        sign = '+' if obs.elevation.m > 0 else '-'
        setElev = f':Sev{sign}{obs.elevation.m:06.1f}#'

        commandString = setLon + setLat + setElev
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if '0' in response[0]:
            return False

        return True

    def setLatitude(self, lat=None, lat_degrees=None):
        """
        setLatitude sets the value in the mount to the given parameters.
        the site parameters could be set be the following commands:
        latitude (we will use the last one with the highest precision):

            :StsDD*MM# or :StsDD*MM:SS# or :StsDD*MM:SS.S#

            Sets the current site latitude to sDD*MM (sign, degrees, arcminutes),
            sDD*MM:SS (sign, degrees, arcminutes, arcseconds), or
            sDD*MM:SS.S (sign, degrees, arcminutes, arcseconds and tenths of arcsecond)

            Returns:
            0   invalid
            1   valid

        :param      lat:  coordinates as Angle
        :param      lat_degrees:  coordinates as float
        :return:    success
        """
        hasAngle = isinstance(lat, api.Angle)
        hasFloat = isinstance(lat_degrees, (float, int))
        hasStr = isinstance(lat, str)
        if hasAngle:
            pass

        elif hasFloat:
            lat = valueToAngle(lat_degrees, preference='degrees')

        elif hasStr:
            lat = lat.replace('deg', '')
            lat = stringToAngle(lat, preference='degrees')

        else:
            return False

        conn = Connection(self.host)

        sgn, h, m, s, frac = sexagesimalizeToInt(lat.degrees, 1)
        sign = '+' if sgn >= 0 else '-'
        setLat = f':St{sign}{h:02d}*{m:02d}:{s:02d}.{frac:1d}#'

        commandString = setLat
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if '0' in response[0]:
            return False

        return True

    def setLongitude(self, lon=None, lon_degrees=None):
        """
        setLongitude sets the value in the mount to the given parameters.
        the longitude will be set for east negative, because that's the definition
        from the LX200 protocol, which the 10micron mount supports. internally we use
        the standard east positive.

        the site parameters could be set be the following commands:
        longitude (we will use the last one with the highest precision):

            :SgsDDD*MM# or :SgsDDD*MM:SS# or :SgsDDD*MM:SS.S#

            Set current site’s longitude to sDDD*MM (sign, degrees, arcminutes),
            sDDD*MM:SS (sign, degrees, arcminutes, arcseconds) or
            sDDD*MM:SS.S (sign, degrees, arcminutes, arcseconds and tenths of arcsecond).
            Note: East Longitudes are expressed as negative.
            Returns:
            0   invalid
            1   valid

        :param      lon:  coordinates as Angle
        :param      lon_degrees:  coordinates as float
        :return:    success
        """
        hasAngle = isinstance(lon, api.Angle)
        hasFloat = isinstance(lon_degrees, (float, int))
        hasStr = isinstance(lon, str)
        if hasAngle:
            pass

        elif hasFloat:
            lon = valueToAngle(lon_degrees, preference='degrees')

        elif hasStr:
            lon = lon.replace('deg', '')
            lon = stringToAngle(lon, preference='degrees')

        else:
            return False

        conn = Connection(self.host)

        sgn, h, m, s, frac = sexagesimalizeToInt(lon.degrees, 1)
        sign = '+' if sgn < 0 else '-'
        setLon = f':Sg{sign}{h:03d}*{m:02d}:{s:02d}.{frac:1d}#'

        commandString = setLon
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if '0' in response[0]:
            return False

        return True

    def setElevation(self, elev):
        """
        setElevation sets the value in the mount to the given parameters.
        the site parameters could be set be the following commands:
        elevation:

            :SevsXXXX.X#

            Set current site’s elevation to sXXXX.X (sign, metres) in the
            range -1000.0 to 9999.9.
            Returns:
            0   invalid
            1   valid

        :param      elev:        string with elevation in meters
        :return:    success
        """
        if not isinstance(elev, (str, int, float)):
            return False

        elev = valueToFloat(elev)
        if elev is None:
            return False

        conn = Connection(self.host)

        setElev = ':Sev{sign}{0:06.1f}#'.format(abs(elev),
                                                sign='+' if elev > 0 else '-')

        commandString = setElev
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False

        if '0' in response[0]:
            return False

        return True

    def startTracking(self):
        """
        startTracking sends the start command to the mount. the command returns nothing.
        it is necessary to make that direct to unpark first, than start tracking

        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PO#:AP#')
        return suc

    def stopTracking(self):
        """
        stopTracking sends the start command to the mount. the command returns nothing.

        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':RT9#')
        return suc

    def park(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':hP#')
        return suc

    def unpark(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PO#')
        return suc

    def parkOnActualPosition(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PiP#')
        if not suc:
            return False

        if '0' in response[0]:
            return False

        return True

    def stop(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':STOP#')
        return suc

    def flip(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':FLIP#')
        if not suc:
            return False

        if response[0] != '1':
            return False

        return True

    def moveNorth(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PO#:Mn#')
        if not suc:
            return False

        return True

    def moveEast(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PO#:Me#')
        if not suc:
            return False

        return True

    def moveSouth(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PO#:Ms#')
        if not suc:
            return False

        return True

    def moveWest(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':PO#:Mw#')
        if not suc:
            return False

        return True

    def stopMoveNorth(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':Qn#')
        if not suc:
            return False

        return True

    def stopMoveAll(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':Q#')
        if not suc:
            return False

        return True

    def stopMoveEast(self):
        """
        stopMoveEast sends the flip command to the mount.

        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':Qe#')
        if not suc:
            return False
        return True

    def stopMoveSouth(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':Qs#')
        if not suc:
            return False

        return True

    def stopMoveWest(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':Ww#')
        if not suc:
            return False

        return True
