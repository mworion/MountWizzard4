# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import datetime
from collections.abc import Callable
from mw4.base import transform
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.nativeQt.qtInputDialog import MWInputDialog
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, clickable, guiSetText
from mw4.logic.controllers.mount.locationCalculations import buildLocation
from mw4.logic.controllers.mount.mountSettings import (
    SWITCHES,
    VALUES,
    MountSettingsController,
    SettingSpec,
)
from mw4.logic.controllers.mount.trackingMode import activeTrackingMode
from mw4.mountcontrol.convertGui import (
    convertLatToAngle,
    convertLonToAngle,
    formatLatToText,
    formatLonToText,
)
from mw4.mountcontrol.firmware import Firmware
from mw4.mountcontrol.obsSite import ObsSite
from mw4.mountcontrol.setting import Setting
from skyfield.api import Angle
from typing import TYPE_CHECKING, Any, ClassVar, cast

if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow


class MountSett(TabAddon):
    TRACKING_BUTTONS: ClassVar = (
        "followSat",
        "setLunarTracking",
        "setSiderealTracking",
        "setSolarTracking",
    )
    SETTING_TEXT_FIELDS: ClassVar = (
        ("statusUnattendedFlip", "s", "statusUnattendedFlip"),
        ("statusDualAxisTracking", "s", "statusDualAxisTracking"),
        ("statusRefraction", "s", "statusRefraction"),
        ("statusWOL", "s", "wakeOnLan"),
        ("statusAPO", "s", "autoPowerOn"),
        ("slewRate", "2.0f", "slewRate"),
        ("timeToFlip", "3.0f", "timeToFlip"),
        ("refractionTemp", "+4.1f", "refractionTemp"),
        ("refractionTemp1", "+4.1f", "refractionTemp"),
        ("refractionPress", "6.1f", "refractionPress"),
        ("refractionPress1", "6.1f", "refractionPress"),
        ("meridianLimitTrack", "3.0f", "meridianLimitTrack"),
        ("meridianLimitSlew", "3.0f", "meridianLimitSlew"),
        ("horizonLimitLow", "3.0f", "horizonLimitLow"),
        ("horizonLimitHigh", "3.0f", "horizonLimitHigh"),
        ("settleTimeMount", "3.0f", "settleTime"),
    )

    def __init__(self, mainW: "MainWindow") -> None:
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.signals.ui.msg
        self.ui = mainW.ui
        self.typeConnectionTexts = ["RS-232", "GPS/RS-232", "LAN", "WiFi"]
        self.controller = MountSettingsController(self.app.dReg.mount.setting, self.msg.emit)

        ms = self.app.dReg.mount.signals
        ms.locationDone.connect(self.updateLocGUI)
        ms.pointDone.connect(self.updatePointGUI)
        ms.settingDone.connect(self.updateSettingGUI)
        self.app.timeMgr.update1s.connect(self.showTimeDiff)
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
        clickable(self.ui.statusWebInterface).connect(self.setWebinterface)
        clickable(self.ui.statusDualAxisTracking).connect(self.setDualAxisTracking)
        clickable(self.ui.statusWOL).connect(self.setWOL)
        clickable(self.ui.statusAPO).connect(self.setAPO)
        clickable(self.ui.statusRefraction).connect(self.setRefraction)
        clickable(self.ui.settleTimeMount).connect(self.setSettleTimeMount)
        self.app.dReg.mount.signals.firmwareDone.connect(self.setWOLorAPO)
        self.updateLocGUI(self.app.dReg.mount.obsSite)

    def setWOLorAPO(self, fw: Firmware) -> None:
        self.ui.statusWOL.setEnabled(fw.isHW2012())
        self.ui.label_statusWOL.setEnabled(fw.isHW2012())
        self.ui.statusAPO.setEnabled(fw.isHW2024())
        self.ui.label_statusAPO.setEnabled(fw.isHW2024())
        self.ui.statusWOL.setVisible(fw.isHW2012())
        self.ui.label_statusWOL.setVisible(fw.isHW2012())
        self.ui.statusAPO.setVisible(fw.isHW2024())
        self.ui.label_statusAPO.setVisible(fw.isHW2024())

    def updatePointGUI(self, obs: ObsSite) -> None:
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

    def updateExpireGui(self, expireText: str | None) -> None:
        ui = self.ui.UTCExpire
        guiSetText(ui, "s", expireText)
        if expireText is None:
            return
        now = datetime.datetime.now(datetime.UTC)
        expire = datetime.datetime.strptime(expireText, "%Y-%m-%d").replace(tzinfo=datetime.UTC)
        if now > expire:
            changeStyleDynamic(ui, "color", "red")
        elif now > expire - datetime.timedelta(days=30):
            changeStyleDynamic(ui, "color", "yellow")
        else:
            changeStyleDynamic(ui, "color", "")

    def updateTrackingGui(self, sett: Setting) -> None:
        obsSite = self.app.dReg.mount.obsSite
        mode = activeTrackingMode(obsSite.status, obsSite.isFollowingSatellite, sett)
        if mode == "unchanged":
            return
        for name in self.TRACKING_BUTTONS:
            changeStyleDynamic(getattr(self.ui, name), "run", "true" if name == mode else "false")

    def updateSettingGUI(self, sett: Setting) -> None:
        self.updateExpireGui(sett.UTCExpire)
        for uiName, fmt, attribute in self.SETTING_TEXT_FIELDS:
            guiSetText(getattr(self.ui, uiName), fmt, getattr(sett, attribute))

        guiSetText(self.ui.statusGPSSynced, "s", ["OFF", "ON", "PPS"][sett.gpsSynced])
        guiSetText(self.ui.statusWebInterface, "s", "ON" if sett.webInterfaceStat else "OFF")
        if sett.typeConnection is not None:
            self.ui.mountTypeConnection.setText(self.typeConnectionTexts[sett.typeConnection])
        guiSetText(self.ui.timeToMeridian, "3.0f", sett.timeToMeridian())
        self.updateTrackingGui(sett)

    def updateLocGUI(self, obs: ObsSite) -> None:
        if obs is None:
            return
        location = obs.location
        if location is None:
            return

        self.ui.siteLongitude.setText(formatLonToText(location.longitude))
        self.ui.siteLatitude.setText(formatLatToText(location.latitude))
        self.ui.siteElevation.setText(str(location.elevation.m))

    def setMeridianLimitTrack(self) -> bool:
        return self.askAndApplyValue(VALUES["meridianTrack"])

    def setMeridianLimitSlew(self) -> bool:
        return self.askAndApplyValue(VALUES["meridianSlew"])

    def setHorizonLimitHigh(self) -> bool:
        return self.askAndApplyValue(VALUES["horizonHigh"])

    def setHorizonLimitLow(self) -> bool:
        return self.askAndApplyValue(VALUES["horizonLow"])

    def setSlewRate(self) -> bool:
        return self.askAndApplyValue(VALUES["slewRate"])

    def setLocationValues(
        self, lat: Angle | None = None, lon: Angle | None = None, elev: float | None = None
    ) -> None:
        obs = self.app.dReg.mount.obsSite
        topo, text = buildLocation(obs.location, lat, lon, elev)
        if self.app.dReg.mount.stat:
            obs.setLocation(topo)
            self.app.dReg.mount.instance.getLocation()
        else:
            obs.location = topo
            self.updateLocGUI(self.app.dReg.mount.obsSite)
            self.app.dReg.mount.signals.locationDone.emit(self.app.dReg.mount.obsSite)
        self.msg.emit(0, "Mount", "Setting", text)

    def setLongitude(self) -> None:
        value, ok = MWInputDialog.getText(
            self.mainW,
            "Set Site Longitude",
            "Format: <dd[EW] mm ss.s> or <[+-]d.d>, East is positive",
            self.ui.siteLongitude.text(),
        )
        if not ok:
            return
        value = convertLonToAngle(value)
        self.setLocationValues(lon=value)

    def setLatitude(self) -> None:
        value, ok = MWInputDialog.getText(
            self.mainW,
            "Set Site Latitude",
            "Format: <dd[SN] mm ss.s> or <[+-]d.d>",
            self.ui.siteLatitude.text(),
        )
        if not ok:
            return
        value = convertLatToAngle(value)
        self.setLocationValues(lat=value)

    def setElevation(self) -> bool:
        obs = self.app.dReg.mount.obsSite
        value, ok = MWInputDialog.getDouble(
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

    def askAndApplySwitch(self, spec: SettingSpec) -> bool:
        value, ok = MWInputDialog.getItem(
            self.mainW,
            spec.title,
            "Value: On / Off",
            ["ON", "OFF"],
            self.controller.switchIndex(spec),
        )
        if not ok:
            return False
        return self.controller.applySwitch(spec, value)

    def askAndApplyValue(self, spec: SettingSpec) -> bool:
        actValue = self.controller.currentValue(spec)
        minVal, maxVal, prompt = self.controller.valueRange(spec)
        dialog = cast(
            "Callable[..., tuple[Any, bool]]",
            MWInputDialog.getInt if spec.isInt else MWInputDialog.getDouble,
        )
        value, ok = dialog(self.mainW, spec.title, prompt, actValue, minVal, maxVal, spec.step)
        if not ok:
            return False
        return self.controller.applyValue(spec, value)

    def setUnattendedFlip(self) -> bool:
        return self.askAndApplySwitch(SWITCHES["unattendedFlip"])

    def setWebinterface(self) -> bool:
        return self.askAndApplySwitch(SWITCHES["webInterface"])

    def setDualAxisTracking(self) -> bool:
        return self.askAndApplySwitch(SWITCHES["dualAxisTracking"])

    def setWOL(self) -> bool:
        return self.askAndApplySwitch(SWITCHES["wol"])

    def setAPO(self) -> bool:
        return self.askAndApplySwitch(SWITCHES["apo"])

    def setRefraction(self) -> bool:
        return self.askAndApplySwitch(SWITCHES["refraction"])

    def setRefractionTemp(self) -> bool:
        return self.askAndApplyValue(VALUES["refractionTemp"])

    def setRefractionPress(self) -> bool:
        return self.askAndApplyValue(VALUES["refractionPress"])

    def setSettleTimeMount(self) -> bool:
        return self.askAndApplyValue(VALUES["settleTime"])

    def showTimeDiff(self) -> None:
        delta = self.app.dReg.mount.instance.mountTimeConn.timeDiff * 1000
        rtt = self.app.dReg.mount.instance.mountTimeConn.rtt * 1000
        guiSetText(self.ui.timeDeltaPC2Mount, "4.0f", delta)
        guiSetText(self.ui.rtt, "4.1f", rtt)
        if abs(delta) < 100:
            changeStyleDynamic(self.ui.timeDeltaPC2Mount, "color", "")
        elif abs(delta) < 500:
            changeStyleDynamic(self.ui.timeDeltaPC2Mount, "color", "yellow")
        else:
            changeStyleDynamic(self.ui.timeDeltaPC2Mount, "color", "red")
        guiSetText(self.ui.timeUTC, "s", self.app.dReg.mount.timeJD.utc_strftime("%H:%M:%S"))
