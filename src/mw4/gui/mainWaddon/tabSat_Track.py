# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from mw4.base.tpool import Worker, startWorker
from mw4.gui.mainWaddon.satData import SatData
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, positionCursorInTable
from mw4.logic.controllers.satellites.satellite_calculations import calcSatPasses
from mw4.logic.controllers.satellites.trackCalculations import (
    calcTrajectoryData,
    dataAgeColor,
    filterHorizon,
    formatSatPass,
    reduceTrajectory,
    selectStartEnd,
)
from mw4.mountcontrol.obsSite import ObsSite
from mw4.mountcontrol.tleParams import TLEParams
from PySide6.QtWidgets import QLineEdit
from sgp4.exporter import export_tle
from skyfield.api import Angle, EarthSatellite
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from mw4.gui.mainWindow.mainWindow import MainWindow


class SatTrack(SatData):
    def __init__(self, mainW: "MainWindow") -> None:
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.threadPool = mainW.app.threadPool
        self.msg = mainW.app.signals.ui.msg
        self.ui = mainW.ui
        self.satellite: EarthSatellite | None = None
        self.satellitesRawTLE = {}
        self.nextSatPass = [None, None, None]
        self.lastMeridianLimit = None
        self.workerPasses: Worker | None = None

        self.passUI: dict[int, dict[str, QLineEdit]] = {
            0: {
                "rise": self.ui.satRise_1,
                "culminate": self.ui.satCulminate_1,
                "settle": self.ui.satSettle_1,
                "flip": self.ui.satFlip_1,
                "date": self.ui.satDate_1,
            },
            1: {
                "rise": self.ui.satRise_2,
                "culminate": self.ui.satCulminate_2,
                "settle": self.ui.satSettle_2,
                "flip": self.ui.satFlip_2,
                "date": self.ui.satDate_2,
            },
            2: {
                "rise": self.ui.satRise_3,
                "culminate": self.ui.satCulminate_3,
                "settle": self.ui.satSettle_3,
                "flip": self.ui.satFlip_3,
                "date": self.ui.satDate_3,
            },
        }
        self.satOrbits: list[dict] = []
        self.app.dReg.mount.signals.calcTLEdone.connect(self.updateSatelliteTrackGui)
        self.app.dReg.mount.signals.calcTrajectoryDone.connect(self.updateInternalTrackGui)
        self.app.dReg.mount.signals.getTLEdone.connect(self.getSatelliteDataFromDatabase)
        self.app.dReg.mount.signals.pointDone.connect(self.followMount)
        self.app.dReg.mount.signals.pointDone.connect(self.toggleTrackingOffset)
        self.app.dReg.mount.signals.firmwareDone.connect(self.enableGuiFunctions)

        self.ui.startSatelliteTracking.clicked.connect(self.startTrack)
        self.ui.stopSatelliteTracking.clicked.connect(self.stopTrack)
        self.app.signals.model.sendSatelliteData.connect(self.signalSatelliteData)
        self.ui.satAfterFlip.clicked.connect(self.showSatPasses)
        self.ui.satBeforeFlip.clicked.connect(self.showSatPasses)
        self.ui.avoidHorizon.clicked.connect(self.showSatPasses)
        self.ui.useInternalSatCalc.clicked.connect(self.showSatPasses)
        self.ui.useInternalSatCalc.clicked.connect(self.enableGuiFunctions)
        self.ui.progTrajectory.clicked.connect(self.startProg)
        self.ui.listSats.itemDoubleClicked.connect(self.chooseSatellite)
        trackingOffsetWidgets = [self.ui.satOffTime, self.ui.satOffRa, self.ui.satOffDec]
        for widget in trackingOffsetWidgets:
            widget.valueChanged.connect(self.setTrackingOffsets)
        self.app.timeMgr.update1s.connect(self.updateOrbit)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
        self.ui.domeAutoFollowSat.setChecked(config.get("domeAutoFollowSat", False))
        self.ui.useInternalSatCalc.setChecked(config.get("useInternalSatCalc", False))
        self.ui.satBeforeFlip.setChecked(config.get("satBeforeFlip", True))
        self.ui.satAfterFlip.setChecked(config.get("satAfterFlip", True))
        self.ui.avoidHorizon.setChecked(config.get("avoidHorizon", False))
        self.ui.trackingReplay.setChecked(config.get("trackingReplay", False))
        self.app.signals.system.timebaseChanged.connect(self.changeUnitTimeUTC)

    def storeConfig(self) -> None:
        config = self.app.config["WindowMain"]
        config["domeAutoFollowSat"] = self.ui.domeAutoFollowSat.isChecked()
        config["useInternalSatCalc"] = self.ui.useInternalSatCalc.isChecked()
        config["satBeforeFlip"] = self.ui.satBeforeFlip.isChecked()
        config["satAfterFlip"] = self.ui.satAfterFlip.isChecked()
        config["avoidHorizon"] = self.ui.avoidHorizon.isChecked()
        config["trackingReplay"] = self.ui.trackingReplay.isChecked()

    def setupIcons(self) -> None:
        self.mainW.wIcon(self.ui.stopSatelliteTracking, "cross-circle")
        self.mainW.wIcon(self.ui.startSatelliteTracking, "start")
        self.mainW.wIcon(self.ui.progSatFull, "run")
        self.mainW.wIcon(self.ui.progSatFiltered, "run")
        self.mainW.wIcon(self.ui.progSatSelected, "run")
        self.mainW.wIcon(self.ui.progTrajectory, "run")

    def enableGuiFunctions(self) -> None:
        useInternal = self.ui.useInternalSatCalc.isChecked()
        availableInternal = self.app.dReg.mount.firmware.checkNewer("3")
        if availableInternal is None:
            return

        progAvailable = availableInternal and useInternal
        self.ui.trackingReplay.setEnabled(progAvailable)
        self.ui.progTrajectory.setEnabled(progAvailable)

    def signalSatelliteData(self, alt: np.ndarray, az: np.ndarray) -> None:
        if not self.satellite:
            return

        name = self.satellite.name
        self.app.signals.model.showSatellite.emit(self.satellite, self.satOrbits, alt, az, name)

    def clearTrackingParameters(self) -> None:
        self.ui.satTrajectoryStart.setText("-")
        self.ui.satTrajectoryEnd.setText("-")
        self.ui.satTrajectoryFlip.setText("-")
        self.ui.stopSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setText("Start satellite tracking")
        changeStyleDynamic(self.ui.startSatelliteTracking, "run", "false")

    def calcTrajectoryData(self, start: float, end: float) -> tuple[np.ndarray, np.ndarray]:
        m = self.app.dReg.mount.instance
        return calcTrajectoryData(
            start,
            end,
            satellite=self.satellite,
            earth=self.app.ephemeris["earth"],
            location=m.obsSite.location,
            ts=m.obsSite.ts,
            temperature=m.setting.refractionTemp,
            pressure=m.setting.refractionPress,
        )

    def calcTrajectoryAndShow(self) -> None:
        useInternal = self.ui.useInternalSatCalc.isChecked()
        start, end = self.selectStartEnd()
        if useInternal:
            alt, az = self.calcTrajectoryData(start, end)
            start, end, alt, az = self.filterHorizon(start, end, alt, az)
            self.signalSatelliteData(alt=alt, az=az)
        else:
            self.app.dReg.mount.instance.calcTLE(start)
            self.signalSatelliteData(alt=np.array([]), az=np.array([]))

    def updateSatPassesGui(self) -> None:
        for i in range(3):
            self.passUI[i]["rise"].setText("-")
            self.passUI[i]["culminate"].setText("-")
            self.passUI[i]["settle"].setText("-")
            self.passUI[i]["flip"].setText("-")
            self.passUI[i]["date"].setText("-")

        for i, satOrbit in enumerate(self.satOrbits):
            texts = formatSatPass(satOrbit, self.app.timeMgr.convertTime)
            for key, text in texts.items():
                self.passUI[i][key].setText(text)

    def runnerShowSatPasses(self) -> None:
        if not self.satellite:
            return
        self.clearTrackingParameters()
        obsSite = self.app.dReg.mount.obsSite
        setting = self.app.dReg.mount.setting
        self.satOrbits = calcSatPasses(self.satellite, obsSite, setting)

    def showSatPasses(self) -> None:
        title = "Satellite passes " + self.app.timeMgr.timeZoneString()
        self.ui.satPassesGroup.setTitle(title)
        self.workerPasses = startWorker(
            self.workerPasses,
            self.threadPool,
            self.runnerShowSatPasses,
            resultMethod=self.updateSatPassesGui,
            finishedMethod=self.calcTrajectoryAndShow,
        )

    def extractSatelliteData(self, satName: str) -> None:
        if satName not in self.satellites.objects:
            self.ui.satelliteNumber.setText("-----")
            self.ui.satelliteDataAge.setText("-----")
            self.ui.satelliteEpoch.setText("-----")
            self.ui.satelliteName.setText(f"{satName}...not found...")
            self.msg.emit(2, "Satellite", "Data", f"[{satName}] not found in database")
            return

        positionCursorInTable(self.ui.listSats, satName)
        self.satellite = self.satellites.objects[satName]
        self.msg.emit(0, "Satellite", "Data", f"{'Actual Sat:':12s} [{satName}]")

        self.ui.satelliteName.setText(self.satellite.name)
        self.ui.satelliteNumber.setText(f"{self.satellite.model.satnum:5d}")

        epochText = self.satellite.epoch.utc_strftime("%Y-%m-%d, %H:%M")
        self.ui.satelliteEpoch.setText(epochText)

        now = self.app.dReg.mount.obsSite.ts.now()
        days = now - self.satellite.epoch
        self.ui.satelliteDataAge.setText(f"{days:2.2f}")

        changeStyleDynamic(self.ui.satelliteDataAge, "color", dataAgeColor(days))

    def programSatToMount(self, satName: str) -> None:
        satellite = self.app.dReg.mount.satellite
        self.msg.emit(0, "TLE", "Program", f"Upload satellite: [{satName}]")
        line1, line2 = export_tle(self.satellites.objects[satName].model)
        suc = satellite.setTLE(line0=satName, line1=line1, line2=line2)
        if not suc:
            self.msg.emit(2, "TLE", "Program error", "Uploading error")
            return
        self.app.dReg.mount.instance.getTLE()

    def chooseSatellite(self) -> None:
        item = self.ui.listSats.item(self.ui.listSats.currentRow(), 1)
        if item is None:
            return

        satName = item.text()
        if self.app.dReg.mount.stat:
            self.programSatToMount(satName)
        else:
            self.extractSatelliteData(satName)
            self.showSatPasses()

    def getSatelliteDataFromDatabase(self, tleParams: TLEParams) -> None:
        self.extractSatelliteData(tleParams.name)
        self.showSatPasses()

    def updateOrbit(self) -> None:
        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            self.ui.stopSatelliteTracking.setEnabled(False)
            changeStyleDynamic(self.ui.startSatelliteTracking, "run", "false")
            return

        now = self.app.dReg.mount.obsSite.ts.now()
        location = self.app.dReg.mount.obsSite.location
        self.app.signals.model.updateSatellite.emit(now, location)

    def selectStartEnd(self) -> tuple[float, float]:
        return selectStartEnd(
            self.satOrbits, self.ui.satBeforeFlip.isChecked(), self.ui.satAfterFlip.isChecked()
        )

    def filterHorizon(
        self, start: float, end: float, alt: np.ndarray, az: np.ndarray
    ) -> tuple[float, float, np.ndarray, np.ndarray]:
        if not self.ui.avoidHorizon.isChecked():
            return start, end, alt, az
        return filterHorizon(start, end, alt, az, self.app.buildPoint.isAboveHorizon)

    def startProg(self) -> None:
        self.clearTrackingParameters()
        isReplay = self.ui.trackingReplay.isChecked()
        t = "for simulation" if isReplay else ""
        self.msg.emit(1, "TLE", "Program", f"Satellite track data {t}")
        self.msg.emit(1, "", "", "This takes some time, please wait...")
        start, end = self.selectStartEnd()
        if not start or not end:
            return
        alt, az = self.calcTrajectoryData(start, end)
        start, end, alt, az = self.filterHorizon(start, end, alt, az)

        if len(alt) == 0:
            text = "No track data (white), please revise settings"
            self.msg.emit(2, "TLE", "Program error", text)
            return

        alt, az = reduceTrajectory(alt, az)
        alt = Angle(degrees=alt)
        az = Angle(degrees=az)

        changeStyleDynamic(self.ui.progTrajectory, "run", "true")
        changeStyleDynamic(self.ui.satTrackGroup, "run", "true")
        self.ui.satTrackGroup.setTitle("Calculating")
        self.ui.progTrajectory.setEnabled(False)
        self.app.dReg.mount.instance.progTrajectory(start, alt, az, replay=isReplay)

    def changeUnitTimeUTC(self) -> None:
        self.showSatPasses()
        self.updateSatelliteTrackGui(self.app.dReg.mount.satellite.tleParams)

    def updateSatelliteTrackGui(self, tleParams: TLEParams) -> None:
        title = "Satellite tracking " + self.app.timeMgr.timeZoneString()
        self.ui.satTrackGroup.setTitle(title)
        if self.satOrbits:
            t = self.app.timeMgr.convertTime(tleParams.jdStart, "%d %b  %H:%M:%S")
            self.ui.satTrajectoryStart.setText(t)
            t = self.app.timeMgr.convertTime(tleParams.jdEnd, "%d %b  %H:%M:%S")
            self.ui.satTrajectoryEnd.setText(t)
            self.ui.stopSatelliteTracking.setEnabled(True)
            self.ui.startSatelliteTracking.setEnabled(True)
        else:
            self.ui.satTrajectoryStart.setText("No transit")
            self.ui.satTrajectoryEnd.setText("No transit")
            self.ui.stopSatelliteTracking.setEnabled(False)
            self.ui.startSatelliteTracking.setEnabled(False)

        if tleParams.flip and self.satOrbits:
            self.ui.satTrajectoryFlip.setText("YES")
        else:
            self.ui.satTrajectoryFlip.setText("NO")

    def updateInternalTrackGui(self, tleParams: TLEParams) -> None:
        self.ui.progTrajectory.setEnabled(True)
        title = "Satellite tracking " + self.app.timeMgr.timeZoneString()
        self.ui.satTrackGroup.setTitle(title)
        changeStyleDynamic(self.ui.satTrackGroup, "run", "false")
        self.updateSatelliteTrackGui(tleParams)
        self.msg.emit(1, "TLE", "Program", "Satellite track data ready!")

    def startTrack(self) -> None:
        if not self.app.dReg.mount.stat:
            self.msg.emit(2, "TLE", "Program", "Mount is not online")
            return

        if self.app.dReg.mount.obsSite.isParked:
            suc = self.app.dReg.mount.obsSite.unpark()
            if suc:
                self.msg.emit(0, "TLE", "Command", "Mount unparked")
            else:
                self.msg.emit(2, "TLE", "Command error", "Cannot unpark mount")

        self.app.dReg.dome.instance.avoidFirstOvershoot()
        suc, message = self.app.dReg.mount.satellite.slewTLE()
        if not suc:
            self.msg.emit(2, "TLE", "Command error", f"{message}")
            return

        changeStyleDynamic(self.ui.startSatelliteTracking, "run", "true")
        self.msg.emit(0, "TLE", "Command ", f"{message}")
        self.app.dReg.mount.satellite.setTrackingOffsets()

    def stopTrack(self) -> None:
        if not self.app.dReg.mount.stat:
            self.msg.emit(2, "TLE", "Command", "Mount is not online")
            return

        suc = self.app.dReg.mount.obsSite.startTracking()
        if not suc:
            self.msg.emit(2, "TLE", "Command", "Cannot stop tracking")
            return

        self.ui.startSatelliteTracking.setText("Start satellite tracking")
        changeStyleDynamic(self.ui.startSatelliteTracking, "run", "false")
        self.msg.emit(0, "TLE", "Command", "Stopped tracking")

    def toggleTrackingOffset(self, obs: ObsSite) -> None:
        if not self.app.dReg.mount.firmware.checkNewer("3"):
            return

        if obs.status == 10:
            self.ui.satOffGroup.setEnabled(True)
        else:
            self.ui.satOffGroup.setEnabled(False)

    def followMount(self, obs: ObsSite) -> None:
        TLESCK = {
            "V": "is slewing to transit start",
            "P": "is waiting for satellite",
            "S": "is catching satellite",
            "T": "is tracking satellite",
        }

        status = obs.status
        if status != 10:
            return
        if not self.ui.domeAutoFollowSat.isChecked():
            return
        if not self.app.dReg.dome.stat:
            return

        stat = obs.statusSat
        statText = TLESCK.get(stat, "")
        self.ui.startSatelliteTracking.setText(statText)

        azimuth = cast(float, obs.Az.degrees)
        altitude = cast(float, obs.Alt.degrees)
        self.app.dReg.dome.instance.slewDome(altitude=altitude, azimuth=azimuth, follow=True)

    def setTrackingOffsets(self) -> None:
        valT = self.ui.satOffTime.value()
        valR = self.ui.satOffRa.value()
        valD = self.ui.satOffDec.value()
        suc = self.app.dReg.mount.satellite.setTrackingOffsets(Time=valT, RA=valR, DECcorr=valD)
        if not suc:
            self.msg.emit(2, "TLE", "Command error", "Cannot change offset")
