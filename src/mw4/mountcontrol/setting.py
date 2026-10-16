# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from mw4.mountcontrol.connection import Connection
from mw4.mountcontrol.convert import valueToFloat, valueToInt
from mw4.mountcontrol.mountContext import MountContext
from typing import ClassVar


class Setting:
    CONFIG: ClassVar = {
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

    def __init__(self, parent: MountContext) -> None:
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
        self.horizonLimitHigh: float = 90
        self.horizonLimitLow: float = 0
        self.UTCValid: bool = False
        self.UTCExpire: str = "2000-01-01"
        self.gpsSynced: int = 0
        self._typeConnection: int = 0
        self._addressLanMAC: str = ""
        self._addressWirelessMAC: str = ""
        self._wakeOnLan: str = "None"
        self._weatherStatus: int = 0
        self.weatherPressure: float = 950
        self.weatherTemperature: float = 0
        self.weatherHumidity: float = 0
        self.weatherDewPoint: float = 0
        self.weatherAge: int = 0
        self.trackingRate: float = 0
        self.webInterfaceStat: bool = False
        self.settleTime: float = 0
        self._autoPowerOn: str = "None"
        self.configEquatorial: str = ""
        self.configGerman: str = ""
        self.configHemisphere: str = ""
        self.configHoming: str = ""

    @property
    def typeConnection(self) -> int:
        return self._typeConnection

    @typeConnection.setter
    def typeConnection(self, value: str | int | None) -> None:
        value = valueToInt(value)
        if value not in [0, 1, 2, 3]:
            value = 0
        self._typeConnection = value

    @property
    def addressLanMAC(self) -> str:
        return self._addressLanMAC

    @addressLanMAC.setter
    def addressLanMAC(self, value: str) -> None:
        self._addressLanMAC = value.upper().replace(".", ":")

    @property
    def addressWirelessMAC(self) -> str:
        return self._addressWirelessMAC

    @addressWirelessMAC.setter
    def addressWirelessMAC(self, value: str) -> None:
        self._addressWirelessMAC = value.upper().replace(".", ":")

    @property
    def wakeOnLan(self) -> str:
        return self._wakeOnLan

    @wakeOnLan.setter
    def wakeOnLan(self, value: str) -> None:
        if value == "0":
            self._wakeOnLan = "OFF"
        elif value == "1":
            self._wakeOnLan = "ON"
        else:
            self._wakeOnLan = "None"

    @property
    def autoPowerOn(self) -> str:
        return self._autoPowerOn

    @autoPowerOn.setter
    def autoPowerOn(self, value: str) -> None:
        if value == "0":
            self._autoPowerOn = "OFF"
        elif value == "1":
            self._autoPowerOn = "ON"
        else:
            self._autoPowerOn = "None"

    @property
    def weatherStatus(self) -> int:
        return self._weatherStatus

    @weatherStatus.setter
    def weatherStatus(self, value: str | float) -> None:
        value = valueToInt(value)
        if not (0 <= value <= 2):
            value = 0
        self._weatherStatus = value

    def timeToMeridian(self) -> int:
        return int(self.timeToFlip - self.meridianLimitTrack * 4)

    def validateSetting(self, response: list[str]) -> bool:
        """
        The response consists of 24 chunks, with firmware 3.2.5 and newer of 27.
        Commands without a '#' terminator are merged into the next chunk, so
        some chunks carry more than one value.
        """
        newer = self.parent.firmware.checkNewer("3.2.5")
        if len(response) < (27 if newer else 24):
            return False
        if len(response[9]) < 6 or len(response[10]) < 3:
            return False
        if response[11].count(",") != 1:
            return False
        return not (newer and len(response[25].split(",")) < 4)

    def parseSetting(self, response: list, numberOfChunks: int) -> bool:
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        if not self.validateSetting(response):
            self.log.warning(f"malformed setting response: [{response}]")
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
        w17 = response[17].split(",")
        self.weatherAge = valueToInt(w17[1]) if len(w17) > 1 else 0
        self.weatherPressure = valueToFloat(w17[0])
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
        conn = Connection(self.parent)
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

    def sendCommand(self, commandString: str, responseCheck: str = "") -> bool:
        """Send a command to the mount and return only the success flag."""
        conn = Connection(self.parent)
        suc, _, _ = conn.communicate(commandString, responseCheck=responseCheck)
        return suc

    def setSlewRate(self, value: float) -> bool:
        if value < 2 or value > 15:
            return False
        return self.sendCommand(f":Sw{value:02.0f}#:RMs{value:02.0f}#", responseCheck="10")

    def setSlewSpeedMax(self) -> bool:
        return self.sendCommand(":RC3#")

    def setSlewSpeedHigh(self) -> bool:
        return self.sendCommand(":RC2#")

    def setSlewSpeedMed(self) -> bool:
        return self.sendCommand(":Rc255#")

    def setSlewSpeedLow(self) -> bool:
        return self.sendCommand(":Rc128#")

    def setRefractionParam(self, temperature: float, pressure: float) -> bool:
        if temperature < -40 or temperature > 75:
            return False
        if pressure < 500 or pressure > 1300:
            return False
        return self.sendCommand(
            f":SRPRS{pressure:06.1f}#:SRTMP{temperature:+06.1f}#", responseCheck="11"
        )

    def setRefractionTemp(self, value: float) -> bool:
        if value < -40 or value > 75:
            return False
        return self.sendCommand(f":SRTMP{value:+06.1f}#", responseCheck="1")

    def setRefractionPress(self, value: float) -> bool:
        if value < 500 or value > 1300:
            return False
        return self.sendCommand(f":SRPRS{value:06.1f}#", responseCheck="1")

    def setRefraction(self, status: bool) -> bool:
        return self.sendCommand(f":SREF{1 if status else 0:1d}#", responseCheck="1")

    def setUnattendedFlip(self, status: bool) -> bool:
        return self.sendCommand(f":Suaf{1 if status else 0:1d}#")

    def setDualAxisTracking(self, status: bool) -> bool:
        return self.sendCommand(f":Sdat{1 if status else 0:1d}#", responseCheck="1")

    def setWOL(self, status: bool) -> bool:
        return self.sendCommand(f":SWOL{1 if status else 0:1d}#", responseCheck="1")

    def setMeridianLimitTrack(self, value: int) -> bool:
        if value < 1 or value > 30:
            return False
        return self.sendCommand(f":Slmt{value:02d}#", responseCheck="1")

    def setMeridianLimitSlew(self, value: int) -> bool:
        if value < 0 or value > 30:
            return False
        return self.sendCommand(f":Slms{value:02d}#", responseCheck="1")

    def setHorizonLimitHigh(self, value: int) -> bool:
        if value < 0 or value > 90:
            return False
        return self.sendCommand(f":Sh+{value:02d}#", responseCheck="1")

    def setHorizonLimitLow(self, value: int) -> bool:
        if value < -5 or value > 45:
            return False
        return self.sendCommand(f":So{value:+02d}#", responseCheck="1")

    def setDirectWeatherUpdateType(self, value: int) -> bool:
        if value < 0 or value > 2:
            return False

        return self.sendCommand(f":WSS{value:1d}#", responseCheck="1")

    def checkRateLunar(self) -> bool:
        return abs(self.trackingRate - 62.4) < 0.05

    def checkRateSidereal(self) -> bool:
        return abs(self.trackingRate - 60.2) < 0.05

    def checkRateSolar(self) -> bool:
        return abs(self.trackingRate - 60.3) < 0.05

    def setLunarTracking(self) -> bool:
        return self.sendCommand(":RT0#")

    def setSiderealTracking(self) -> bool:
        return self.sendCommand(":RT2#")

    def setSolarTracking(self) -> bool:
        return self.sendCommand(":RT1#")

    def setWebInterface(self, status: bool) -> bool:
        return self.sendCommand(f":NTSweb{1 if status else 0:1d}#", responseCheck="1")

    def setSettleTime(self, time: float) -> bool:
        return self.sendCommand(f":Sstm{time:08.3f}#", responseCheck="1")

    def setAutoPower(self, setOn: bool) -> bool:
        value = 1 if setOn else 0
        return self.sendCommand(f":SAPO{value:1d}#", responseCheck="1")
