############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import logging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.convert import valueToFloat, valueToInt


class Setting:
    """ """

    CONFIG = {
        "A": "altazimuth mount",
        "E": "equatorial mount",
        "G": "german mount",
        "F": "fork mount",
        "N": "northern hemisphere",
        "S": "southern hemisphere",
        "H": "homing present",
        "h": "no homing",
    }
    log = logging.getLogger("MW4")

    def __init__(self, parent):
        self.parent = parent
        self.slewRate: float = 0
        self.slewRateMin: float = 0
        self.slewRateMax: float = 99
        self.timeToFlip: float = 0
        self.meridianLimitTrack: float = 0
        self.meridianLimitSlew: float = 0
        self.refractionTemp: float = 0
        self.refractionPress: float = 0
        self.telescopeTempDEC: float = 0
        self.statusRefraction: bool = False
        self.statusUnattendedFlip: bool = False
        self.statusDualAxisTracking: bool = False
        self.horizonLimitHigh: float = 0
        self.horizonLimitLow: float = 0
        self.UTCValid: bool = False
        self.UTCExpire: str = "2000-01-01"
        self.gpsSynced: int = 0
        self._typeConnection: int = 0
        self._addressLanMAC: str = ""
        self._addressWirelessMAC: str = ""
        self._wakeOnLan: str = "None"
        self._weatherStatus: bool = False
        self.weatherPressure: float = 950
        self.weatherTemperature: float = 0
        self.weatherHumidity: float = 0
        self.weatherDewPoint: float = 0
        self.weatherAge: int = 0
        self.trackingRate: float = 0
        self.webInterfaceStat: str = ""
        self.settleTime: float = 0
        self._autoPowerOn: str = "None"
        self.configEquatorial: str = ""
        self.configGerman: str = ""
        self.configHemisphere: str = ""
        self.configHoming: str = ""

    @property
    def typeConnection(self):
        return self._typeConnection

    @typeConnection.setter
    def typeConnection(self, value):
        value = valueToInt(value)
        if value not in [0, 1, 2, 3]:
            value = 0
        self._typeConnection = value

    @property
    def addressLanMAC(self):
        return self._addressLanMAC

    @addressLanMAC.setter
    def addressLanMAC(self, value):
        self._addressLanMAC = value.upper().replace(".", ":")

    @property
    def addressWirelessMAC(self):
        return self._addressWirelessMAC

    @addressWirelessMAC.setter
    def addressWirelessMAC(self, value):
        self._addressWirelessMAC = value.upper().replace(".", ":")

    @property
    def wakeOnLan(self):
        return self._wakeOnLan

    @wakeOnLan.setter
    def wakeOnLan(self, value):
        if value == "0":
            self._wakeOnLan = "OFF"
        elif value == "1":
            self._wakeOnLan = "ON"
        else:
            self._wakeOnLan = "None"

    @property
    def autoPowerOn(self):
        return self._autoPowerOn

    @autoPowerOn.setter
    def autoPowerOn(self, value):
        if value == "0":
            self._autoPowerOn = "OFF"
        elif value == "1":
            self._autoPowerOn = "ON"
        else:
            self._autoPowerOn = "None"

    @property
    def weatherStatus(self):
        return self._weatherStatus

    @weatherStatus.setter
    def weatherStatus(self, value):
        value = valueToInt(value)
        if value not in [0, 1, 2]:
            value = 0
        self._weatherStatus = value

    def timeToMeridian(self):
        """"""
        return int(self.timeToFlip - self.meridianLimitTrack * 4)

    def parseSetting(self, response: list, numberOfChunks: int) -> bool:
        """ """
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False

        self.slewRate = valueToFloat(response[0])
        self.slewRateMin = valueToFloat(response[1])
        self.slewRateMax = valueToFloat(response[2])
        self.timeToFlip = valueToFloat(response[3])
        self.meridianLimitTrack = valueToFloat(response[4])
        self.meridianLimitSlew = valueToFloat(response[5])
        self.refractionTemp = valueToFloat(response[6])
        self.refractionPress = valueToFloat(response[7])
        self.telescopeTempDEC = valueToFloat(response[8])
        self.statusRefraction = response[9][0] == "1"
        self.statusUnattendedFlip = response[9][1] == "1"
        self.statusDualAxisTracking = response[9][2] == "1"
        self.horizonLimitHigh = valueToFloat(response[9][3:6])
        self.horizonLimitLow = valueToFloat(response[10][0:3])
        valid, expirationDate = response[11].split(",")
        self.UTCValid = valid == "V"
        self.UTCExpire = expirationDate
        self.typeConnection = response[12]
        self.addressLanMAC = response[14]
        self.wakeOnLan = response[15]
        self.weatherStatus = response[16]
        if len(response[17].split(",")) > 1:
            self.weatherAge = valueToInt(response[17].split(",")[1])
        else:
            self.weatherAge = ""
        self.weatherPressure = valueToFloat(response[17].split(",")[0])
        self.weatherTemperature = valueToFloat(response[18].split(",")[0])
        self.weatherHumidity = valueToFloat(response[19].split(",")[0])
        self.weatherDewPoint = valueToFloat(response[20].split(",")[0])
        self.trackingRate = valueToFloat(response[21])
        self.webInterfaceStat = bool(valueToInt(response[22]))
        self.settleTime = valueToFloat(response[23])
        if not self.parent.firmware.checkNewer("3.2.5"):
            self.gpsSynced = valueToInt(response[13])
            return True
        self.autoPowerOn = response[24]
        config = response[25].split(",")
        self.configEquatorial = self.CONFIG.get(config[0], "Unknown")
        self.configGerman = self.CONFIG.get(config[1], "Unknown")
        self.configHemisphere = self.CONFIG.get(config[2], "Unknown")
        self.configHoming = self.CONFIG.get(config[3], "Unknown")
        self.gpsSynced = valueToInt(response[26])

        return True

    def pollSetting(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        cs1 = ":GMs#:GMsa#:GMsb#:Gmte#:Glmt#:Glms#:GRTMP#:GRPRS#:GTMP1#"
        cs2 = ":GREF#:Guaf#:Gdat#:Gh#:Go#:GDUTV#:GINQ#:gtg#:GMAC#:GWOL#"
        cs3 = ":WSG#:WSP#:WST#:WSH#:WSD#:GT#:NTGweb#:Gstm#"
        if self.parent.firmware.checkNewer("3.2.5"):
            cs3 += ":GAPO#:GCFG#:gtgpps#"
        commandString = cs1 + cs2 + cs3
        suc, response, numberOfChunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parseSetting(response, numberOfChunks)

    def setSlewRate(self, value: int | float) -> bool:
        """ """
        if value < 2 or value > 15:
            return False
        conn = Connection(self.parent.host)
        commandString = f":Sw{value:02.0f}#:RMs{value:02.0f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="10")
        return suc

    def setSlewSpeedMax(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":RC3#"
        suc, _, _ = conn.communicate(commandString)
        return suc

    def setSlewSpeedHigh(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = ":RC2#"
        suc, _, _ = conn.communicate(commandString)
        return suc

    def setSlewSpeedMed(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        centerSpeed = 255
        commandString = f":Rc{centerSpeed:02.0f}#"
        suc, _, _ = conn.communicate(commandString)
        return suc

    def setSlewSpeedLow(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        centerSpeed = 128
        commandString = f":Rc{centerSpeed:02.0f}#"
        suc, _, _ = conn.communicate(commandString)
        return suc

    def setRefractionParam(self, temperature: float, pressure: float) -> bool:
        """ """
        if temperature < -40 or temperature > 75:
            return False
        if pressure < 500 or pressure > 1300:
            return False
        conn = Connection(self.parent.host)
        commandString = f":SRPRS{pressure:06.1f}#:SRTMP{temperature:+06.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="11")
        return suc

    def setRefractionTemp(self, value: float) -> bool:
        """ """
        if value < -40 or value > 75:
            return False
        conn = Connection(self.parent.host)
        commandString = f":SRTMP{value:+06.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setRefractionPress(self, value: float) -> bool:
        """ """
        if value < 500 or value > 1300:
            return False
        conn = Connection(self.parent.host)
        commandString = f":SRPRS{value:06.1f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setRefraction(self, status: bool) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":SREF{1 if status else 0:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setUnattendedFlip(self, status: bool) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":Suaf{1 if status else 0:1d}#"
        suc, _, _ = conn.communicate(commandString)
        return suc

    def setDualAxisTracking(self, status: bool) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":Sdat{1 if status else 0:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setWOL(self, status):
        """ """
        conn = Connection(self.parent.host)
        commandString = f":SWOL{1 if status else 0:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setMeridianLimitTrack(self, value: int) -> bool:
        """ """
        if value < 1 or value > 30:
            return False
        conn = Connection(self.parent.host)
        commandString = f":Slmt{value:02d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setMeridianLimitSlew(self, value: int) -> bool:
        """ """
        if value < 0 or value > 30:
            return False
        conn = Connection(self.parent.host)
        commandString = f":Slms{value:02d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setHorizonLimitHigh(self, value: int) -> bool:
        """ """
        if value < 0 or value > 90:
            return False
        conn = Connection(self.parent.host)
        commandString = f":Sh+{value:02d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setHorizonLimitLow(self, value: int) -> bool:
        """ """
        if value < -5 or value > 45:
            return False
        conn = Connection(self.parent.host)
        commandString = f":So{value:+02d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setDirectWeatherUpdateType(self, value: int) -> bool:
        """ """
        if value < 0 or value > 2:
            return False

        conn = Connection(self.parent.host)
        commandString = f":WSS{value:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def checkRateLunar(self) -> bool:
        """ """
        return f"{self.trackingRate:2.1f}" == "62.4"

    def checkRateSidereal(self) -> bool:
        """ """
        return f"{self.trackingRate:2.1f}" == "60.2"

    def checkRateSolar(self) -> bool:
        """ """
        return f"{self.trackingRate:2.1f}" == "60.3"

    def setLunarTracking(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":RT0#")
        return suc

    def setSiderealTracking(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":RT2#")
        return suc

    def setSolarTracking(self) -> bool:
        """ """
        conn = Connection(self.parent.host)
        suc, _, _ = conn.communicate(":RT1#")
        return suc

    def setWebInterface(self, status: bool) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":NTSweb{1 if status else 0:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setSettleTime(self, time: float) -> bool:
        """ """
        conn = Connection(self.parent.host)
        commandString = f":Sstm{time:08.3f}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc

    def setAutoPower(self, setOn: bool) -> bool:
        """ """
        value = 1 if setOn else 0
        conn = Connection(self.parent.host)
        commandString = f":SAPO{value:1d}#"
        suc, _, _ = conn.communicate(commandString, responseCheck="1")
        return suc
