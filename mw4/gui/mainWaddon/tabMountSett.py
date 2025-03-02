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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import datetime

# external packages
from PySide6.QtWidgets import QInputDialog, QLineEdit
from PySide6.QtCore import QObject
from skyfield.api import wgs84

# local import
from base import transform
from mountcontrol.convert import convertLatToAngle, convertLonToAngle
from mountcontrol.convert import formatLatToText, formatLonToText
from gui.utilities.toolsQtWidget import changeStyleDynamic, guiSetText, clickable


class MountSett(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.typeConnectionTexts = ["RS-232", "GPS/RS-232", "LAN", "WiFi"]

        ms = self.app.mount.signals
        ms.locationDone.connect(self.updateLocGUI)
        ms.pointDone.connect(self.updatePointGUI)
        ms.settingDone.connect(self.updateSettingGUI)
        self.app.update1s.connect(self.showOffset)
        clickable(self.ui.refractionTemp).connect(self.setRefractionTemp)
        clickable(self.ui.refractionPress).connect(self.setRefractionPress)
        clickable(self.ui.meridianLimitTrack).connect(self.setMeridianLimitTrack)
        clickable(self.ui.meridianLimitSlew).connect(self.setMeridianLimitSlew)
        clickable(self.ui.horizonLimitHigh).connect(self.setHorizonLimitHigh)
        clickable(self.ui.horizonLimitLow).connect(self.setHorizonLimitLow)
        clickable(self.ui.slewRate).connect(self.setSlewRate)
        clickable(self.ui.siteLatitude).connect(self.setLatitude)
        clickable(self.ui.siteLongitude).connect(self.setLongitude)
        clickable(self.ui.siteElevation).connect(self.setElevation)
        clickable(self.ui.statusUnattendedFlip).connect(self.setUnattendedFlip)
        clickable(self.ui.statusDualAxisTracking).connect(self.setDualAxisTracking)
        clickable(self.ui.statusWOL).connect(self.setWOL)
        clickable(self.ui.statusRefraction).connect(self.setRefraction)
        clickable(self.ui.settleTimeMount).connect(self.setSettleTimeMount)

    def updatePointGUI(self, obs):
        """ """
        isJ2000 = self.ui.coordsJ2000.isChecked()
        isValid = obs.raJNow is not None
        isValid = isValid and obs.decJNow is not None
        isValid = isValid and obs.timeJD is not None
        if isJ2000 and isValid:
            ra, dec = transform.JNowToJ2000(obs.raJNow, obs.decJNow, obs.timeJD)
        else:
            ra = obs.raJNow
            dec = obs.decJNow

        guiSetText(self.ui.RA, "HSTR", ra)
        guiSetText(self.ui.RAfloat, "H5.5f", ra)
        guiSetText(self.ui.DEC, "DSTR", dec)
        guiSetText(self.ui.DECfloat, "D5.5f", dec)
        guiSetText(self.ui.HA, "HSTR", obs.haJNow)
        guiSetText(self.ui.HAfloat, "H5.5f", obs.haJNow)
        guiSetText(self.ui.ALT, "D5.2f", obs.Alt)
        guiSetText(self.ui.AZ, "D5.2f", obs.Az)
        guiSetText(self.ui.pierside, "s", obs.pierside)
        guiSetText(self.ui.timeSidereal, "HSTR", obs.timeSidereal)

    def updateSettingGUI(self, sett):
        """ """
        ui = self.ui.UTCExpire
        guiSetText(ui, "s", sett.UTCExpire)
        if sett.UTCExpire is not None:
            now = datetime.datetime.now()
            expire = datetime.datetime.strptime(sett.UTCExpire, "%Y-%m-%d")
            deltaYellow = datetime.timedelta(days=30)
            if now > expire:
                changeStyleDynamic(ui, "color", "red")
            elif now > expire - deltaYellow:
                changeStyleDynamic(ui, "color", "yellow")
            else:
                changeStyleDynamic(ui, "color", "")

        ui = self.ui.statusUnattendedFlip
        guiSetText(ui, "s", sett.statusUnattendedFlip)

        ui = self.ui.statusDualAxisTracking
        guiSetText(ui, "s", sett.statusDualAxisTracking)

        ui = self.ui.statusRefraction
        guiSetText(ui, "s", sett.statusRefraction)

        ui = self.ui.statusGPSSynced
        guiSetText(ui, "s", sett.gpsSynced)

        ui = self.ui.statusWOL
        guiSetText(ui, "s", sett.wakeOnLan)

        ui = self.ui.statusWebInterface
        guiSetText(ui, "s", sett.webInterfaceStat)

        if sett.typeConnection is not None:
            text = self.typeConnectionTexts[sett.typeConnection]
            self.ui.mountTypeConnection.setText(text)

        guiSetText(self.ui.slewRate, "2.0f", sett.slewRate)
        guiSetText(self.ui.timeToFlip, "3.0f", sett.timeToFlip)
        guiSetText(self.ui.timeToMeridian, "3.0f", sett.timeToMeridian())
        guiSetText(self.ui.refractionTemp, "+4.1f", sett.refractionTemp)
        guiSetText(self.ui.refractionTemp1, "+4.1f", sett.refractionTemp)
        guiSetText(self.ui.refractionPress, "6.1f", sett.refractionPress)
        guiSetText(self.ui.refractionPress1, "6.1f", sett.refractionPress)
        guiSetText(self.ui.meridianLimitTrack, "3.0f", sett.meridianLimitTrack)
        guiSetText(self.ui.meridianLimitSlew, "3.0f", sett.meridianLimitSlew)
        guiSetText(self.ui.horizonLimitLow, "3.0f", sett.horizonLimitLow)
        guiSetText(self.ui.horizonLimitHigh, "3.0f", sett.horizonLimitHigh)
        guiSetText(self.ui.settleTimeMount, "3.0f", sett.settleTime)

        # todo: this might be a little bit too slow
        if self.app.mount.obsSite.status is None:
            changeStyleDynamic(self.ui.followSat, "running", False)
            changeStyleDynamic(self.ui.setLunarTracking, "running", False)
            changeStyleDynamic(self.ui.setSiderealTracking, "running", False)
            changeStyleDynamic(self.ui.setSolarTracking, "running", False)

        elif self.app.mount.obsSite.status == 10:
            changeStyleDynamic(self.ui.followSat, "running", True)
            changeStyleDynamic(self.ui.setLunarTracking, "running", False)
            changeStyleDynamic(self.ui.setSiderealTracking, "running", False)
            changeStyleDynamic(self.ui.setSolarTracking, "running", False)

        elif sett.checkRateLunar():
            changeStyleDynamic(self.ui.followSat, "running", False)
            changeStyleDynamic(self.ui.setLunarTracking, "running", True)
            changeStyleDynamic(self.ui.setSiderealTracking, "running", False)
            changeStyleDynamic(self.ui.setSolarTracking, "running", False)

        elif sett.checkRateSidereal():
            changeStyleDynamic(self.ui.followSat, "running", False)
            changeStyleDynamic(self.ui.setLunarTracking, "running", False)
            changeStyleDynamic(self.ui.setSiderealTracking, "running", True)
            changeStyleDynamic(self.ui.setSolarTracking, "running", False)

        elif sett.checkRateSolar():
            changeStyleDynamic(self.ui.followSat, "running", False)
            changeStyleDynamic(self.ui.setLunarTracking, "running", False)
            changeStyleDynamic(self.ui.setSiderealTracking, "running", False)
            changeStyleDynamic(self.ui.setSolarTracking, "running", True)

    def updateLocGUI(self, obs):
        """ """
        if obs is None:
            return
        location = obs.location
        if location is None:
            return

        self.ui.siteLongitude.setText(formatLonToText(location.longitude))
        self.ui.siteLatitude.setText(formatLatToText(location.latitude))
        self.ui.siteElevation.setText(str(location.elevation.m))

    def setMeridianLimitTrack(self):
        """ """
        sett = self.app.mount.setting
        actValue = 0 if sett.meridianLimitTrack is None else int(sett.meridianLimitTrack)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self.mainW, "Set Meridian Limit Track", "Value (1-30):", actValue, 1, 30, 1
        )

        if not ok:
            return False
        if sett.setMeridianLimitTrack(value):
            self.msg.emit(0, "Mount", "Setting", f"Meridian Lim Track: [{value}]")
            return True
        else:
            self.msg.emit(2, "Mount", "Setting", "Meridian Limit Track cannot be set")
            return False

    def setMeridianLimitSlew(self):
        """ """
        sett = self.app.mount.setting
        actValue = 0 if sett.meridianLimitSlew is None else int(sett.meridianLimitSlew)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self.mainW, "Set Meridian Limit Slew", "Value (0-30):", actValue, 0, 30, 1
        )

        if not ok:
            return False
        if sett.setMeridianLimitSlew(value):
            self.msg.emit(0, "Mount", "Setting", f"Meridian Lim Slew: [{value}]")
            return True
        else:
            self.msg.emit(2, "Mount", "Setting", "Meridian Limit Slew cannot be set")
            return False

    def setHorizonLimitHigh(self):
        """ """
        sett = self.app.mount.setting
        actValue = 0 if sett.horizonLimitHigh is None else int(sett.horizonLimitHigh)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self.mainW, "Set Horizon Limit High", "Value (0-90):", actValue, 0, 90, 1
        )

        if not ok:
            return False
        if sett.setHorizonLimitHigh(value):
            self.msg.emit(0, "Mount", "Setting", f"Horizon Limit High: [{value}]")
            return True
        else:
            self.msg.emit(2, "Mount", "Setting", "Horizon Limit High cannot be set")
            return False

    def setHorizonLimitLow(self):
        """ """
        sett = self.app.mount.setting
        actValue = 0 if sett.horizonLimitLow is None else int(sett.horizonLimitLow)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self.mainW,
            "Set Horizon Limit Low",
            "Value (-5 - 90):",
            actValue,
            -5,
            90,
            1,
        )

        if not ok:
            return False
        if sett.setHorizonLimitLow(value):
            self.msg.emit(0, "Mount", "Setting", f"Horizon Limit Low: [{value}]")
            return True
        else:
            self.msg.emit(2, "Mount", "Setting", "Horizon Limit Low cannot be set")
            return False

    def setSlewRate(self):
        """ """
        sett = self.app.mount.setting
        actValue = 0 if sett.slewRate is None else int(sett.slewRate)
        minRate = 0 if sett.slewRateMin is None else int(sett.slewRateMin)
        maxRate = 0 if sett.slewRateMax is None else int(sett.slewRateMax)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self.mainW,
            "Set Slew Rate",
            f"Value ({minRate}...{maxRate}):",
            actValue,
            minRate,
            maxRate,
            1,
        )

        if not ok:
            return False
        if sett.setSlewRate(value):
            self.msg.emit(0, "Mount", "Setting", f"Slew Rate: [{value}]")
            return True
        else:
            self.msg.emit(2, "Mount", "Setting", "Slew Rate cannot be set")
            return False

    def setLocationValues(self, lat=None, lon=None, elev=None):
        """ """
        obs = self.app.mount.obsSite
        loc = obs.location
        lat = loc.latitude if lat is None else lat
        lon = loc.longitude if lon is None else lon
        elev = loc.elevation.m if elev is None else elev

        topo = wgs84.latlon(
            longitude_degrees=lon.degrees,
            latitude_degrees=lat.degrees,
            elevation_m=elev,
        )

        if self.app.deviceStat["mount"]:
            obs.setLocation(topo)
            self.app.mount.getLocation()
        else:
            obs.location = topo
            self.updateLocGUI(self.app.mount.obsSite)

        t = f"Location set to:     [{lat.degrees:3.2f} deg, "
        t += f"{lon.degrees:3.2f} deg, {elev:4.1f} m]"
        self.msg.emit(0, "Mount", "Setting", t)

    def setLongitude(self):
        """ """
        obs = self.app.mount.obsSite
        if obs.location is None:
            return False

        dlg = QInputDialog()
        value, ok = dlg.getText(
            self.mainW,
            "Set Site Longitude",
            "Format: <dd[EW] mm ss.s> or <[+-]d.d>, East is positive",
            QLineEdit.EchoMode.Normal,
            self.ui.siteLongitude.text(),
        )
        if not ok:
            return False

        value = convertLonToAngle(value)
        self.setLocationValues(lon=value)
        return True

    def setLatitude(self):
        """ """
        obs = self.app.mount.obsSite
        if obs.location is None:
            return False

        dlg = QInputDialog()
        value, ok = dlg.getText(
            self.mainW,
            "Set Site Latitude",
            "Format: <dd[SN] mm ss.s> or <[+-]d.d>",
            QLineEdit.EchoMode.Normal,
            self.ui.siteLatitude.text(),
        )
        if not ok:
            return False

        value = convertLatToAngle(value)
        self.setLocationValues(lat=value)
        return True

    def setElevation(self):
        """ """
        obs = self.app.mount.obsSite
        if obs.location is None:
            return False

        dlg = QInputDialog()
        value, ok = dlg.getDouble(
            self.mainW,
            "Set Site Elevation",
            "Format: d.d",
            obs.location.elevation.m,
            0,
            8000,
            1,
        )
        if not ok:
            return False

        self.setLocationValues(elev=value)
        return True

    def setUnattendedFlip(self):
        """ """
        sett = self.app.mount.setting
        dlg = QInputDialog()
        value, ok = dlg.getItem(
            self.mainW,
            "Set Unattended Flip",
            "Value: On / Off",
            ["ON", "OFF"],
            0,
            False,
        )
        if not ok:
            return False
        suc = sett.setUnattendedFlip(value == "ON")
        if suc:
            self.msg.emit(0, "Mount", "Setting", f"Unattended flip: [{value}]")
        else:
            self.msg.emit(2, "Mount", "Setting", "Unattended flip cannot be set")
        return suc

    def setDualAxisTracking(self):
        """ """
        sett = self.app.mount.setting
        dlg = QInputDialog()
        value, ok = dlg.getItem(
            self.mainW,
            "Set Dual Axis Tracking",
            "Value: On / Off",
            ["ON", "OFF"],
            0,
            False,
        )
        if not ok:
            return False

        suc = sett.setDualAxisTracking(value == "ON")
        if suc:
            self.msg.emit(0, "Mount", "Setting", f"DualAxis tracking: [{value}]")
        else:
            self.msg.emit(2, "Mount", "Setting", "DualAxis tracking cannot be set")
        return suc

    def setWOL(self):
        """ """
        sett = self.app.mount.setting
        dlg = QInputDialog()
        value, ok = dlg.getItem(
            self.mainW, "Set Wake On Lan", "Value: On / Off", ["ON", "OFF"], 0, False
        )
        if not ok:
            return False

        suc = sett.setWOL(value == "ON")
        if suc:
            self.msg.emit(0, "Mount", "Setting", f"Wake On Lan: [{value}]")
        else:
            self.msg.emit(2, "Mount", "Setting", "Wake On Lan cannot be set")
        return suc

    def setRefractionTemp(self):
        """ """
        sett = self.app.mount.setting
        actValue = 0 if sett.refractionTemp is None else sett.refractionTemp
        minVal = -40
        maxVal = 75
        dlg = QInputDialog()
        value, ok = dlg.getDouble(
            self.mainW,
            "Set Refraction Temperature",
            f"Value ({minVal}...{maxVal}):",
            actValue,
            minVal,
            maxVal,
            1,
        )

        if not ok:
            return False
        if sett.setRefractionTemp(value):
            self.msg.emit(0, "Mount", "Setting", f"Refraction Temp: [{value}]")
            return True
        else:
            self.msg.emit(2, "Mount", "Setting", "Refraction Temp cannot be set")
            return False

    def setRefractionPress(self):
        """ """
        sett = self.app.mount.setting
        actValue = 0 if sett.refractionPress is None else sett.refractionPress
        minVal = 500
        maxVal = 1300
        dlg = QInputDialog()
        value, ok = dlg.getDouble(
            self.mainW,
            "Set Refraction Pressure",
            f"Value ({minVal}...{maxVal}):",
            actValue,
            minVal,
            maxVal,
            1,
        )

        if not ok:
            return False
        if sett.setRefractionPress(value):
            self.msg.emit(0, "Mount", "Setting", f"Refraction Press: [{value}]")
            return True
        else:
            self.msg.emit(2, "Mount", "Setting", "Refraction Press cannot be set")
            return False

    def setRefraction(self):
        """ """
        sett = self.app.mount.setting
        dlg = QInputDialog()
        value, ok = dlg.getItem(
            self.mainW,
            "Set Refraction Correction",
            "Value: On / Off",
            ["ON", "OFF"],
            0,
            False,
        )
        if not ok:
            return False

        suc = sett.setRefraction(value == "ON")
        if suc:
            self.msg.emit(0, "Mount", "Setting", f"Refraction corr: [{value}]")
        else:
            self.msg.emit(2, "Mount", "Setting", "Refraction correction cannot be set")
        return suc

    def setSettleTimeMount(self):
        """ """
        sett = self.app.mount.setting
        actValue = 0 if sett.settleTime is None else int(sett.settleTime)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self.mainW, "Set Settle Time", "Value (0-999):", actValue, 0, 999, 1
        )

        if not ok:
            return False
        if sett.setSettleTime(value):
            self.msg.emit(0, "Mount", "Setting", f"Settle Time: [{value}]")
            return True
        else:
            self.msg.emit(2, "Mount", "Setting", "Settle Time cannot be set")
            return False

    def showOffset(self):
        """ """
        connectSync = self.ui.clockSync.isChecked()
        delta = self.app.mount.obsSite.timeDiff * 1000
        ui = self.ui.timeDeltaPC2Mount
        if connectSync:
            text = f"{delta:4.0f}"
        else:
            text = "-"
        ui.setText(text)

        if not connectSync:
            changeStyleDynamic(ui, "color", "")
        elif abs(delta) < 100:
            changeStyleDynamic(ui, "color", "")
        elif abs(delta) < 500:
            changeStyleDynamic(ui, "color", "yellow")
        else:
            changeStyleDynamic(ui, "color", "red")

        timeJD = self.app.mount.obsSite.timeJD
        if timeJD is not None:
            text = timeJD.utc_strftime("%H:%M:%S")
            self.ui.timeUTC.setText(text)
