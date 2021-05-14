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

# local imports
from mountcontrol.connection import Connection
from mountcontrol.convert import valueToFloat
from mountcontrol.convert import valueToInt


class Setting(object):
    """
    The class Setting inherits all information and handling of setting
    attributes of the connected mount and provides the abstracted interface
    to a 10 micron mount.

        >>> setting = Setting(host='')

    """

    __all__ = ['Setting',
               ]

    log = logging.getLogger(__name__)

    def __init__(self,
                 host=None,
                 ):

        self.host = host
        self._slewRate = None
        self._slewRateMin = None
        self._slewRateMax = None
        self._timeToFlip = None
        self._meridianLimitTrack = None
        self._meridianLimitSlew = None
        self._refractionTemp = None
        self._refractionPress = None
        self._telescopeTempDEC = None
        self._statusRefraction = None
        self._statusUnattendedFlip = None
        self._statusDualAxisTracking = None
        self._horizonLimitHigh = None
        self._horizonLimitLow = None
        self._wakeOnLan = None
        self._UTCValid = None
        self._UTCExpire = None
        self._gpsSynced = None
        self._typeConnection = None
        self._addressLanMAC = None
        self._addressWirelessMAC = None
        self._weatherStatus = None
        self._weatherPressure = None
        self._weatherTemperature = None
        self._weatherHumidity = None
        self._weatherDewPoint = None
        self._trackingRate = None
        self._webInterfaceStat = None

    @property
    def slewRate(self):
        return self._slewRate

    @slewRate.setter
    def slewRate(self, value):
        self._slewRate = valueToFloat(value)

    @property
    def slewRateMin(self):
        return self._slewRateMin

    @slewRateMin.setter
    def slewRateMin(self, value):
        self._slewRateMin = valueToFloat(value)

    @property
    def slewRateMax(self):
        return self._slewRateMax

    @slewRateMax.setter
    def slewRateMax(self, value):
        self._slewRateMax = valueToFloat(value)

    @property
    def timeToFlip(self):
        return self._timeToFlip

    @timeToFlip.setter
    def timeToFlip(self, value):
        self._timeToFlip = valueToFloat(value)

    @property
    def meridianLimitTrack(self):
        return self._meridianLimitTrack

    @meridianLimitTrack.setter
    def meridianLimitTrack(self, value):
        self._meridianLimitTrack = valueToFloat(value)

    @property
    def meridianLimitSlew(self):
        return self._meridianLimitSlew

    @meridianLimitSlew.setter
    def meridianLimitSlew(self, value):
        self._meridianLimitSlew = valueToFloat(value)

    def timeToMeridian(self):
        if self._timeToFlip is not None and self._meridianLimitTrack is not None:
            return int(self._timeToFlip - self._meridianLimitTrack * 4)
        else:
            return None

    @property
    def refractionTemp(self):
        return self._refractionTemp

    @refractionTemp.setter
    def refractionTemp(self, value):
        self._refractionTemp = valueToFloat(value)

    @property
    def refractionPress(self):
        return self._refractionPress

    @refractionPress.setter
    def refractionPress(self, value):
        self._refractionPress = valueToFloat(value)

    @property
    def telescopeTempDEC(self):
        return self._telescopeTempDEC

    @telescopeTempDEC.setter
    def telescopeTempDEC(self, value):
        self._telescopeTempDEC = valueToFloat(value)

    @property
    def statusRefraction(self):
        return self._statusRefraction

    @statusRefraction.setter
    def statusRefraction(self, value):
        self._statusRefraction = bool(value)

    @property
    def statusUnattendedFlip(self):
        return self._statusUnattendedFlip

    @statusUnattendedFlip.setter
    def statusUnattendedFlip(self, value):
        self._statusUnattendedFlip = bool(value)

    @property
    def statusDualAxisTracking(self):
        return self._statusDualAxisTracking

    @statusDualAxisTracking.setter
    def statusDualAxisTracking(self, value):
        self._statusDualAxisTracking = bool(value)

    @property
    def horizonLimitHigh(self):
        return self._horizonLimitHigh

    @horizonLimitHigh.setter
    def horizonLimitHigh(self, value):
        self._horizonLimitHigh = valueToFloat(value)

    @property
    def horizonLimitLow(self):
        return self._horizonLimitLow

    @horizonLimitLow.setter
    def horizonLimitLow(self, value):
        self._horizonLimitLow = valueToFloat(value)

    @property
    def UTCValid(self):
        return self._UTCValid

    @UTCValid.setter
    def UTCValid(self, value):
        self._UTCValid = bool(value)

    @property
    def UTCExpire(self):
        return self._UTCExpire

    @UTCExpire.setter
    def UTCExpire(self, value):
        if isinstance(value, str):
            self._UTCExpire = value
        else:
            self._UTCExpire = None

    @property
    def typeConnection(self):
        return self._typeConnection

    @typeConnection.setter
    def typeConnection(self, value):
        value = valueToInt(value)
        if value is None:
            self._typeConnection = value
        elif not 0 <= value <= 3:
            value = None
        self._typeConnection = value

    @property
    def gpsSynced(self):
        return self._gpsSynced

    @gpsSynced.setter
    def gpsSynced(self, value):
        self._gpsSynced = bool(value)

    @property
    def addressLanMAC(self):
        return self._addressLanMAC

    @addressLanMAC.setter
    def addressLanMAC(self, value):
        self._addressLanMAC = value.upper().replace('.', ':')

    @property
    def addressWirelessMAC(self):
        return self._addressWirelessMAC

    @addressWirelessMAC.setter
    def addressWirelessMAC(self, value):
        self._addressWirelessMAC = value.upper().replace('.', ':')

    @property
    def wakeOnLan(self):
        return self._wakeOnLan

    @wakeOnLan.setter
    def wakeOnLan(self, value):
        if value == 'N':
            self._wakeOnLan = 'None'
        elif value == '0':
            self._wakeOnLan = 'Off'
        elif value == '1':
            self._wakeOnLan = 'On'
        else:
            self._wakeOnLan = None

    @property
    def weatherStatus(self):
        return self._weatherStatus

    @weatherStatus.setter
    def weatherStatus(self, value):
        value = valueToInt(value)
        if value is None:
            self._weatherStatus = value
        elif 0 <= value <= 2:
            self._weatherStatus = value
        else:
            self._weatherStatus = None

    @property
    def weatherPressure(self):
        return self._weatherPressure

    @weatherPressure.setter
    def weatherPressure(self, value):
        self._weatherPressure = valueToFloat(value)

    @property
    def weatherTemperature(self):
        return self._weatherTemperature

    @weatherTemperature.setter
    def weatherTemperature(self, value):
        self._weatherTemperature = valueToFloat(value)

    @property
    def weatherHumidity(self):
        return self._weatherHumidity

    @weatherHumidity.setter
    def weatherHumidity(self, value):
        self._weatherHumidity = valueToFloat(value)

    @property
    def weatherDewPoint(self):
        return self._weatherDewPoint

    @weatherDewPoint.setter
    def weatherDewPoint(self, value):
        self._weatherDewPoint = valueToFloat(value)

    @property
    def trackingRate(self):
        return self._trackingRate

    @trackingRate.setter
    def trackingRate(self, value):
        self._trackingRate = valueToFloat(value)

    @property
    def webInterfaceStat(self):
        return self._webInterfaceStat

    @webInterfaceStat.setter
    def webInterfaceStat(self, value):
        value = valueToFloat(value)
        if value is None:
            self._webInterfaceStat = None
        else:
            self._webInterfaceStat = bool(value)

    def parseSetting(self, response, numberOfChunks):
        """
        Parsing the polling med command.

        :param response:        data load from mount
        :param numberOfChunks:
        :return: success:       True if ok, False if not
        """
        if len(response) != numberOfChunks:
            self.log.warning('wrong number of chunks')
            return False

        self.slewRate = response[0]
        self.slewRateMin = response[1]
        self.slewRateMax = response[2]
        self.timeToFlip = response[3]
        self.meridianLimitTrack = response[4]
        self.meridianLimitSlew = response[5]
        self.refractionTemp = response[6]
        self.refractionPress = response[7]
        self.telescopeTempDEC = response[8]
        self.statusRefraction = (response[9][0] == '1')
        self.statusUnattendedFlip = (response[9][1] == '1')
        self.statusDualAxisTracking = (response[9][2] == '1')
        self.horizonLimitHigh = response[9][3:6]
        self.horizonLimitLow = response[10][0:3]
        valid, expirationDate = response[11].split(',')
        self.UTCValid = (valid == 'V')
        self.UTCExpire = expirationDate
        self.typeConnection = response[12]
        self.gpsSynced = (response[13] == '1')
        self.addressLanMAC = response[14]
        self.wakeOnLan = response[15]
        self.weatherStatus = response[16]
        self.weatherPressure = response[17].split(',')[0]
        self.weatherTemperature = response[18].split(',')[0]
        self.weatherHumidity = response[19].split(',')[0]
        self.weatherDewPoint = response[20].split(',')[0]
        self.trackingRate = response[21]
        self.webInterfaceStat = response[22]
        return True

    def pollSetting(self):
        """
        Sending the polling med command. As the mount need polling the data, I
        send a set of commands to get the data back to be able to process and
        store it.

        :return:    success:    True if ok, False if not
        """
        conn = Connection(self.host)
        cs1 = ':U2#:GMs#:GMsa#:GMsb#:Gmte#:Glmt#:Glms#:GRTMP#:GRPRS#:GTMP1#'
        cs2 = ':GREF#:Guaf#:Gdat#:Gh#:Go#:GDUTV#:GINQ#:gtg#:GMAC#:GWOL#'
        cs3 = ':WSG#:WSP#:WST#:WSH#:WSD#:GT#:NTGweb#'
        commandString = cs1 + cs2 + cs3
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        suc = self.parseSetting(response, numberOfChunks)
        return suc

    def setSlewRate(self, value):
        """
        setSlewRate sends the command for setting the max slew rate to the mount.

        :param value:   float for max slew rate in degrees per second
        :return:        success
        """
        if value is None:
            return False
        if not isinstance(value, (int, float)):
            return False
        if value < 2:
            return False
        elif value > 15:
            return False
        conn = Connection(self.host)
        commandString = f':Sw{value:02.0f}#:RMs{value:02.0f}#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setSlewSpeedMax(self):
        """
        setSlewSpeedMax set the slewing speed to max

        :return: success
        """
        conn = Connection(self.host)
        commandString = ':RS#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        return suc

    def setSlewSpeedHigh(self):
        """
        setSlewSpeedHigh set the slewing speed to centering rate. the different
        speeds are set through setting different centering rates, because setting
        different slew speeds leads to a scenario, that we get a different setup
        in max slew speed as well.

        :return: success
        """
        conn = Connection(self.host)
        commandString = ':RC2#:RC#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        return suc

    def setSlewSpeedMed(self):
        """
        setSlewSpeedMed set the slewing speed to centering rate. the different
        speeds are set through setting different centering rates, because setting
        different slew speeds leads to a scenario, that we get a different setup
        in max slew speed as well.

        :return: success
        """
        conn = Connection(self.host)
        centerSpeed = 255
        commandString = f':Rc{centerSpeed:02.0f}#:RC#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        return suc

    def setSlewSpeedLow(self):
        """
        setSlewSpeedLow set the slewing speed to centering rate. the different
        speeds are set through setting different centering rates, because setting
        different slew speeds leads to a scenario, that we get a different setup
        in max slew speed as well.

        :return: success
        """
        conn = Connection(self.host)
        centerSpeed = 128
        commandString = f':Rc{centerSpeed:02.0f}#:RC#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        return suc

    def setRefractionParam(self, temperature=None, pressure=None):
        """
        setRefractionParam sends the command for setting the temperature and
        pressure to the mount. the limits are set to -40 to +75 for temp and 500
        to 1300 hPa for pressure, but there is not real documented limit.

        :param          temperature:    float for temperature correction in Celsius
        :param          pressure:       float for pressure correction in hPa
        :return:        success
        """
        if temperature is None:
            return False
        if pressure is None:
            return False
        if temperature < -40:
            return False
        elif temperature > 75:
            return False
        if pressure < 500:
            return False
        elif pressure > 1300:
            return False
        conn = Connection(self.host)
        commandString = f':SRPRS{pressure:06.1f}#:SRTMP{temperature:+06.1f}#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '11':
            return False
        return True

    def setRefractionTemp(self, value):
        """
        setRefractionTemp sends the command for setting the temperature to the
        mount. the limit is set to -40 to +75, but there is not real documented
        limit.

        :param value:   float for temperature correction in Celsius
        :return:        success
        """
        if value is None:
            return False
        if value < -40:
            return False
        elif value > 75:
            return False
        conn = Connection(self.host)
        commandString = ':SRTMP{0:+06.1f}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setRefractionPress(self, value):
        """
        setRefractionPress sends the command for setting the pressure to the
        mount. the limit is set from 500 to 1300 hPa. no limit give from the
        mount. limits here are relevant over 5000m height

        :param value:   float for pressure correction
        :return:        success
        """
        if value is None:
            return False
        if value < 500:
            return False
        elif value > 1300:
            return False
        conn = Connection(self.host)
        commandString = ':SRPRS{0:06.1f}#'.format(value)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setRefraction(self, status):
        """
        setRefraction sends the command to the mount.

        :param status:  bool for enable or disable refraction correction
        :return:        success
        """

        conn = Connection(self.host)
        commandString = ':SREF{0:1d}#'.format(1 if status else 0)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setUnattendedFlip(self, status):
        """
        setUnattendedFlip sends the  command to the mount. the command returns nothing.

        :param status:  bool for enable or disable unattended flip
        :return:        success
        """

        conn = Connection(self.host)
        commandString = ':Suaf{0:1d}#'.format(1 if status else 0)
        suc, response, numberOfChunks = conn.communicate(commandString)
        return suc

    def setDualAxisTracking(self, status):
        """
        setDualAxisTracking sends the  command to the mount.

        :param status:  bool for enable or disable dual tracking
        :return:        success
        """

        conn = Connection(self.host)
        commandString = ':Sdat{0:1d}#'.format(1 if status else 0)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setWOL(self, status):
        """
        setWOL sends the  command to the mount.

        :param status:  bool for enable or disable WOL
        :return:        success
        """

        conn = Connection(self.host)
        commandString = ':SWOL{0:1d}#'.format(1 if status else 0)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setMeridianLimitTrack(self, value):
        """
        setMeridianLimitTrack sends the command for setting flip limit to the mount.
        the limit is set from 1 to 30 degrees

        :param value:   float for degrees
        :return:        success
        """
        if value < 1:
            return False
        elif value > 30:
            return False
        conn = Connection(self.host)
        value = int(value)
        commandString = f':Slmt{value:02d}#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setMeridianLimitSlew(self, value):
        """
        setMeridianLimitSlew sends the command for setting flip limit to the mount.
        the limit is set to -20 to 20 degrees

        :param value:   float / int for degrees
        :return:        success
        """
        if value < 0:
            return False
        elif value > 30:
            return False
        conn = Connection(self.host)
        value = int(value)
        commandString = f':Slms{value:02d}#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setHorizonLimitHigh(self, value):
        """
        setHorizonLimitHigh sends the command for setting the limit to the mount.
        the limit is set from 0 to 90 degrees

        :param value:   float / int for degrees
        :return:        success
        """
        if value < 0:
            return False
        elif value > 90:
            return False
        conn = Connection(self.host)
        value = int(value)
        commandString = f':Sh+{value:02d}#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setHorizonLimitLow(self, value):
        """
        setHorizonLimitLow sends the command for setting the limit to the mount. the limit
        has to be between -5 and +45 degrees

        :param value:   float / int for degrees
        :return:        success
        """
        if value < -5:
            return False
        elif value > 45:
            return False
        conn = Connection(self.host)
        value = int(value)
        commandString = f':So{value:+02d}#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def setDirectWeatherUpdateType(self, value):
        """
        setDirectWeatherUpdateType sends the command for setting the operating mode for
        updating the refraction data from weather station.

            0 do not update the refraction model data
            1 update only while the mount is not tracking
            2 update continuously, with a 15s smoothing filter

        :param value:   int
        :return:        success
        """

        if value < 0:
            return False
        elif value > 2:
            return False
        value = int(value)

        conn = Connection(self.host)
        commandString = f':WSS{value:1d}#'
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True

    def checkRateLunar(self):
        """
        :return:
        """
        if self._trackingRate == 62.4:
            return True

        else:
            return False

    def checkRateSidereal(self):
        """
        :return:
        """
        if self._trackingRate == 60.2:
            return True

        else:
            return False

    def checkRateSolar(self):
        """
        :return:
        """
        if self._trackingRate == 60.3:
            return True

        else:
            return False

    def setLunarTracking(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':RT0#')
        return suc

    def setSiderealTracking(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':RT2#')
        return suc

    def setSolarTracking(self):
        """
        :return:    success
        """
        conn = Connection(self.host)
        suc, response, numberOfChunks = conn.communicate(':RT1#')
        return suc

    def setWebInterface(self, status):
        """
        :return:    success
        """
        conn = Connection(self.host)
        commandString = ':NTSweb{0:1d}#'.format(1 if status else 0)
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        if response[0] != '1':
            return False
        return True
