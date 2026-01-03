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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
from traceback import print_tb

import numpy as np
from base.tpool import Worker
from mw4.gui.mainWaddon.satData import SatData
from mw4.gui.utilities.toolsQtWidget import changeStyleDynamic
from mw4.logic.satellites.satellite_calculations import calcSatPasses
from mw4.mountcontrol.obsSite import ObsSite
from mw4.mountcontrol.tleParams import TLEParams
from PySide6.QtCore import QObject
from sgp4.exporter import export_tle
from skyfield.api import Angle, EarthSatellite


class SatTrack(QObject, SatData):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.satellite: EarthSatellite = None
        self.satellitesRawTLE = {}
        self.nextSatPass = [None, None, None]
        self.lastMeridianLimit = None

        self.passUI = {
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
        self.satOrbits = {}
        self.app.mount.signals.calcTLEdone.connect(self.updateSatelliteTrackGui)
        self.app.mount.signals.calcTrajectoryDone.connect(self.updateInternalTrackGui)
        self.app.mount.signals.getTLEdone.connect(self.getSatelliteDataFromDatabase)
        self.app.mount.signals.pointDone.connect(self.followMount)
        self.app.mount.signals.pointDone.connect(self.toggleTrackingOffset)
        self.app.mount.signals.firmwareDone.connect(self.enableGuiFunctions)

        self.ui.startSatelliteTracking.clicked.connect(self.startTrack)
        self.ui.stopSatelliteTracking.clicked.connect(self.stopTrack)
        self.app.sendSatelliteData.connect(self.signalSatelliteData)
        self.ui.satAfterFlip.clicked.connect(self.showSatPasses)
        self.ui.satBeforeFlip.clicked.connect(self.showSatPasses)
        self.ui.avoidHorizon.clicked.connect(self.showSatPasses)
        self.ui.useInternalSatCalc.clicked.connect(self.showSatPasses)
        self.ui.useInternalSatCalc.clicked.connect(self.enableGuiFunctions)
        self.ui.progTrajectory.clicked.connect(self.startProg)
        self.ui.listSats.itemDoubleClicked.connect(self.chooseSatellite)
        self.ui.satOffTime.valueChanged.connect(self.setTrackingOffsets)
        self.ui.satOffRa.valueChanged.connect(self.setTrackingOffsets)
        self.ui.satOffDec.valueChanged.connect(self.setTrackingOffsets)
        self.app.update1s.connect(self.updateOrbit)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.domeAutoFollowSat.setChecked(config.get("domeAutoFollowSat", False))
        self.ui.useInternalSatCalc.setChecked(config.get("useInternalSatCalc", False))
        self.ui.satBeforeFlip.setChecked(config.get("satBeforeFlip", True))
        self.ui.satAfterFlip.setChecked(config.get("satAfterFlip", True))
        self.ui.avoidHorizon.setChecked(config.get("avoidHorizon", False))
        self.ui.trackingReplay.setChecked(config.get("trackingReplay", False))
        self.ui.unitTimeUTC.clicked.connect(self.changeUnitTimeUTC)
        self.ui.unitTimeLocal.clicked.connect(self.changeUnitTimeUTC)

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["domeAutoFollowSat"] = self.ui.domeAutoFollowSat.isChecked()
        config["useInternalSatCalc"] = self.ui.useInternalSatCalc.isChecked()
        config["satBeforeFlip"] = self.ui.satBeforeFlip.isChecked()
        config["satAfterFlip"] = self.ui.satAfterFlip.isChecked()
        config["avoidHorizon"] = self.ui.avoidHorizon.isChecked()
        config["trackingReplay"] = self.ui.trackingReplay.isChecked()

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.stopSatelliteTracking, "cross-circle")
        self.mainW.wIcon(self.ui.startSatelliteTracking, "start")
        self.mainW.wIcon(self.ui.progSatFull, "run")
        self.mainW.wIcon(self.ui.progSatFiltered, "run")
        self.mainW.wIcon(self.ui.progSatSelected, "run")
        self.mainW.wIcon(self.ui.progTrajectory, "run")

    def enableGuiFunctions(self) -> None:
        """ """
        useInternal = self.ui.useInternalSatCalc.isChecked()
        availableInternal = self.app.mount.firmware.checkNewer("3")
        if availableInternal is None:
            return

        progAvailable = availableInternal and useInternal
        self.ui.trackingReplay.setEnabled(progAvailable)
        self.ui.progTrajectory.setEnabled(progAvailable)

    def signalSatelliteData(self, alt: list, az: list) -> None:
        """ """
        if not self.satellite:
            return

        name = self.satellite.name
        self.app.showSatellite.emit(self.satellite, self.satOrbits, alt, az, name)

    def clearTrackingParameters(self) -> None:
        """ """
        self.ui.satTrajectoryStart.setText("-")
        self.ui.satTrajectoryEnd.setText("-")
        self.ui.satTrajectoryFlip.setText("-")
        self.ui.stopSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setText("Start satellite tracking")
        changeStyleDynamic(self.ui.startSatelliteTracking, "run", False)

    def calcTrajectoryData(self, start: int, end: int) -> tuple[list, list]:
        """ """
        duration = min(end - start, 900 / 86400)
        if duration < 1 / 86400:
            return [], []

        m = self.app.mount
        temp = m.setting.refractionTemp
        press = m.setting.refractionPress
        timeSeries = start + np.arange(0, duration, 1 / 86400)
        timeVec = m.obsSite.ts.tt_jd(timeSeries)

        earth = self.app.ephemeris["earth"]
        ssb_sat = earth + self.satellite
        ssb_loc = earth + m.obsSite.location
        topocentric = ssb_loc.at(timeVec).observe(ssb_sat).apparent()
        alt, az, _ = topocentric.altaz(pressure_mbar=press, temperature_C=temp)
        return alt.degrees, az.degrees

    def calcTrajectoryAndShow(self) -> None:
        """ """
        useInternal = self.ui.useInternalSatCalc.isChecked()
        isMount = self.app.deviceStat["mount"]
        start, end = self.selectStartEnd()

        if not start or not end:
            return

        if isMount and useInternal:
            alt, az = self.calcTrajectoryData(start, end)
            start, end, alt, az = self.filterHorizon(start, end, alt, az)
        else:
            alt = []
            az = []

        if isMount and not useInternal:
            self.app.mount.calcTLE(start)
        self.signalSatelliteData(alt=alt, az=az)

    def workerShowSatPasses(self) -> None:
        """ """
        title = "Satellite passes " + self.mainW.timeZoneString()
        self.ui.satPassesGroup.setTitle(title)

        if not self.satellite:
            return

        self.clearTrackingParameters()
        obsSite = self.app.mount.obsSite
        setting = self.app.mount.setting
        self.satOrbits = calcSatPasses(self.satellite, obsSite, setting)

        for i in range(0, 3):
            self.passUI[i]["rise"].setText("-")
            self.passUI[i]["culminate"].setText("-")
            self.passUI[i]["settle"].setText("-")
            self.passUI[i]["flip"].setText("-")
            self.passUI[i]["date"].setText("-")

        fString = "%H:%M:%S"
        fStringDate = "%d %b"
        for i, satOrbit in enumerate(self.satOrbits):
            riseT = satOrbit.get("rise", None)
            if riseT is not None:
                riseStr = self.mainW.convertTime(riseT, fString)
                dateStr = self.mainW.convertTime(riseT, fStringDate)
            else:
                riseStr = "unknown"
                dateStr = "---"
            culminateT = satOrbit.get("culminate", None)
            if culminateT is not None:
                culminateStr = self.mainW.convertTime(culminateT, fString)
            else:
                culminateStr = "unknown"
            settleT = satOrbit.get("settle", None)
            if settleT is not None:
                settleStr = self.mainW.convertTime(settleT, fString)
            else:
                settleStr = "unknown"
            flipT = satOrbit.get("flip", None)
            if flipT is not None:
                flipStr = self.mainW.convertTime(flipT, fString)
            else:
                flipStr = "no flip"

            self.passUI[i]["rise"].setText(riseStr)
            self.passUI[i]["culminate"].setText(culminateStr)
            self.passUI[i]["settle"].setText(settleStr)
            self.passUI[i]["flip"].setText(flipStr)
            self.passUI[i]["date"].setText(dateStr)
        self.calcTrajectoryAndShow()

    def showSatPasses(self) -> None:
        """ """
        worker = Worker(self.workerShowSatPasses)
        self.app.threadPool.start(worker)

    def extractSatelliteData(self, satName: str) -> None:
        """ """
        if satName not in self.satellites.objects:
            self.ui.satelliteNumber.setText("-----")
            self.ui.satelliteDataAge.setText("-----")
            self.ui.satelliteEpoch.setText("-----")
            self.ui.satelliteName.setText(f"{satName}...not found...")
            self.msg.emit(2, "Satellite", "Data", f"[{satName}] not found in database")
            return

        self.mainW.positionCursorInTable(self.ui.listSats, satName)
        self.satellite = self.satellites.objects[satName]
        self.msg.emit(0, "Satellite", "Data", f"Actual satellite: [{satName}]")

        self.ui.satelliteName.setText(self.satellite.name)
        self.ui.satelliteNumber.setText(f"{self.satellite.model.satnum:5d}")

        epochText = self.satellite.epoch.utc_strftime("%Y-%m-%d, %H:%M")
        self.ui.satelliteEpoch.setText(epochText)

        now = self.app.mount.obsSite.ts.now()
        days = now - self.satellite.epoch
        self.ui.satelliteDataAge.setText(f"{days:2.2f}")

        if days > 10:
            changeStyleDynamic(self.ui.satelliteDataAge, "color", "red")
        elif 3 < days < 10:
            changeStyleDynamic(self.ui.satelliteDataAge, "color", "yellow")
        else:
            changeStyleDynamic(self.ui.satelliteDataAge, "color", "")

    def programSatToMount(self, satName: str) -> None:
        """ """
        satellite = self.app.mount.satellite
        self.msg.emit(0, "TLE", "Program", f"Upload satellite: [{satName}]")
        line1, line2 = export_tle(self.satellites.objects[satName].model)
        suc = satellite.setTLE(line0=satName, line1=line1, line2=line2)
        if not suc:
            self.msg.emit(2, "TLE", "Program error", "Uploading error")
            return
        self.app.mount.getTLE()

    def chooseSatellite(self) -> None:
        """ """
        satName = self.ui.listSats.item(self.ui.listSats.currentRow(), 1).text()
        if self.app.deviceStat["mount"]:
            self.programSatToMount(satName)
        else:
            self.extractSatelliteData(satName)
            self.showSatPasses()

        if self.ui.autoSwitchTrack.isChecked():
            self.ui.satTabWidget.setCurrentIndex(1)

    def getSatelliteDataFromDatabase(self, tleParams: TLEParams) -> None:
        """ """
        self.extractSatelliteData(tleParams.name)
        self.showSatPasses()

    def updateOrbit(self) -> None:
        """ """
        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            self.ui.stopSatelliteTracking.setEnabled(False)
            changeStyleDynamic(self.ui.startSatelliteTracking, "run", False)
            return

        now = self.app.mount.obsSite.ts.now()
        location = self.app.mount.obsSite.location
        self.app.updateSatellite.emit(now, location)

    def selectStartEnd(self) -> tuple[int, int]:
        """ """
        if not self.satOrbits:
            return 0, 0
        if "rise" not in self.satOrbits[0]:
            return 0, 0
        if "settle" not in self.satOrbits[0]:
            return 0, 0

        isBefore = self.ui.satBeforeFlip.isChecked()
        isAfter = self.ui.satAfterFlip.isChecked()
        start = self.satOrbits[0]["rise"].tt
        end = self.satOrbits[0]["settle"].tt

        if isBefore and isAfter:
            pass
        elif isBefore and not isAfter:
            if "flipLate" in self.satOrbits[0]:
                end = self.satOrbits[0]["flipLate"].tt
        elif not isBefore and isAfter:
            if "flipEarly" in self.satOrbits[0]:
                start = self.satOrbits[0]["flipEarly"].tt
        else:
            return 0, 0

        return start, end

    def filterHorizon(
        self, start: int, end: int, alt: list, az: list
    ) -> tuple[int, int, list, list]:
        """ """
        if not self.ui.avoidHorizon.isChecked():
            return start, end, alt, az

        timeDelayStart = 0
        for altitude, azimuth in list(zip(alt, az)):
            if self.app.data.isAboveHorizon((altitude, azimuth)):
                break
            timeDelayStart += 1
            alt = np.delete(alt, 0)
            az = np.delete(az, 0)

        timeDelayEnd = 0
        for altitude, azimuth in reversed(list(zip(alt, az))):
            if self.app.data.isAboveHorizon((altitude, azimuth)):
                break
            timeDelayEnd += 1
            alt = np.delete(alt, -1)
            az = np.delete(az, -1)

        start += timeDelayStart / 86400
        end -= timeDelayEnd / 86400

        return start, end, alt, az

    def startProg(self) -> None:
        """ """
        self.clearTrackingParameters()
        isReplay = self.ui.trackingReplay.isChecked()
        t = "for simulation" if isReplay else ""
        self.msg.emit(1, "TLE", "Program", f"Satellite track data {t}")
        start, end = self.selectStartEnd()
        if not start or not end:
            return
        alt, az = self.calcTrajectoryData(start, end)
        start, end, alt, az = self.filterHorizon(start, end, alt, az)

        if len(alt) == 0:
            text = "Program", "No track data (white), please revise settings"
            self.msg.emit(2, "TLE", "Error", text)
            return

        factor = int(len(alt) / 900)
        factor = 1 if factor < 1 else factor
        alt = Angle(degrees=np.array_split(alt, factor)[0])
        az = Angle(degrees=np.array_split(az, factor)[0])

        changeStyleDynamic(self.ui.progTrajectory, "run", True)
        self.ui.progTrajectory.setEnabled(False)
        self.ui.progTrajectory.setText("Calculating")
        self.app.mount.progTrajectory(start, alt, az, replay=isReplay)

    def changeUnitTimeUTC(self) -> None:
        """ """
        self.showSatPasses()
        self.updateSatelliteTrackGui(self.app.mount.satellite.tleParams)

    def updateSatelliteTrackGui(self, tleParams: TLEParams) -> None:
        """ """
        title = "Satellite tracking " + self.mainW.timeZoneString()
        self.ui.satTrackGroup.setTitle(title)

        if self.satOrbits:
            t = self.mainW.convertTime(tleParams.jdStart, "%d %b  %H:%M:%S")
            self.ui.satTrajectoryStart.setText(t)
            t = self.mainW.convertTime(tleParams.jdEnd, "%d %b  %H:%M:%S")
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
        """ """
        self.ui.progTrajectory.setEnabled(True)
        self.ui.progTrajectory.setText("Program trajectory")
        self.updateSatelliteTrackGui(tleParams)
        self.msg.emit(1, "TLE", "Program", "Satellite track data ready!")

    def startTrack(self) -> None:
        """ """
        if not self.app.deviceStat["mount"]:
            self.msg.emit(2, "TLE", "Program", "Mount is not online")
            return

        if self.app.mount.obsSite.status == 5:
            suc = self.app.mount.obsSite.unpark()
            if suc:
                self.msg.emit(0, "TLE", "Command", "Mount unparked")
            else:
                self.msg.emit(2, "TLE", "Command error", "Cannot unpark mount")

        self.app.dome.avoidFirstOvershoot()
        suc, message = self.app.mount.satellite.slewTLE()
        if not suc:
            self.msg.emit(2, "TLE", "Command error", f"{message}")
            return

        changeStyleDynamic(self.ui.startSatelliteTracking, "run", True)
        self.msg.emit(0, "TLE", "Command ", f"{message}")
        self.app.mount.satellite.setTrackingOffsets()

    def stopTrack(self) -> None:
        """ """
        if not self.app.deviceStat["mount"]:
            self.msg.emit(2, "TLE", "Command", "Mount is not online")
            return

        suc = self.app.mount.obsSite.startTracking()
        if not suc:
            self.msg.emit(2, "TLE", "Command", "Cannot stop tracking")
            return

        self.ui.startSatelliteTracking.setText("Start satellite tracking")
        changeStyleDynamic(self.ui.startSatelliteTracking, "run", False)
        self.msg.emit(0, "TLE", "Command", "Stopped tracking")

    def toggleTrackingOffset(self, obs: ObsSite) -> None:
        """ """
        if not self.app.mount.firmware.checkNewer("3"):
            return

        if obs.status == 10:
            self.ui.satOffGroup.setEnabled(True)
        else:
            self.ui.satOffGroup.setEnabled(False)

    def followMount(self, obs: ObsSite) -> None:
        """ """
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
        if not self.app.deviceStat["dome"]:
            return

        stat = obs.statusSat
        statText = TLESCK.get(stat, "")
        self.ui.startSatelliteTracking.setText(statText)

        azimuth = obs.Az.degrees
        altitude = obs.Alt.degrees
        self.app.dome.slewDome(altitude=altitude, azimuth=azimuth, follow=True)

    def setTrackingOffsets(self) -> None:
        """ """
        valT = self.ui.satOffTime.value()
        valR = self.ui.satOffRa.value()
        valD = self.ui.satOffDec.value()
        suc = self.app.mount.satellite.setTrackingOffsets(Time=valT, RA=valR, DECcorr=valD)
        if not suc:
            self.msg.emit(2, "TLE", "Command error", "Cannot change offset")
