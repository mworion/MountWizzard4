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

# external packages
import numpy as np
from sgp4.exporter import export_tle
from skyfield.api import Angle
from PySide6.QtCore import QObject

# local import
from gui.mainWaddon.satData import SatData
from logic.satellites.satellite_calculations import calcSatPasses
from gui.utilities.toolsQtWidget import changeStyleDynamic


class SatTrack(QObject, SatData):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui
        self.satOrbits = None
        self.satellite = {}
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
        self.satOrbits = dict()

        msig = self.app.mount.signals
        msig.calcTLEdone.connect(self.updateSatelliteTrackGui)
        msig.calcTrajectoryDone.connect(self.updateInternalTrackGui)
        msig.getTLEdone.connect(self.getSatelliteDataFromDatabase)
        msig.pointDone.connect(self.followMount)
        msig.settingDone.connect(self.updatePasses)
        msig.pointDone.connect(self.toggleTrackingOffset)
        msig.firmwareDone.connect(self.enableGuiFunctions)

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
        self.ui.unitTimeUTC.toggled.connect(self.showSatPasses)
        self.ui.unitTimeUTC.toggled.connect(self.updateSatelliteTrackGui)
        self.ui.satOffTime.valueChanged.connect(self.setTrackingOffsets)
        self.ui.satOffRa.valueChanged.connect(self.setTrackingOffsets)
        self.ui.satOffDec.valueChanged.connect(self.setTrackingOffsets)

        self.app.update1s.connect(self.updateOrbit)

    def initConfig(self):
        """ """
        config = self.app.config["mainW"]
        self.ui.domeAutoFollowSat.setChecked(config.get("domeAutoFollowSat", False))
        self.ui.useInternalSatCalc.setChecked(config.get("useInternalSatCalc", False))
        self.ui.satBeforeFlip.setChecked(config.get("satBeforeFlip", True))
        self.ui.satAfterFlip.setChecked(config.get("satAfterFlip", True))
        self.ui.avoidHorizon.setChecked(config.get("avoidHorizon", False))
        self.ui.trackingReplay.setChecked(config.get("trackingReplay", False))
        self.ui.unitTimeUTC.toggled.connect(self.showSatPasses)

    def storeConfig(self):
        """ """
        config = self.app.config["mainW"]
        config["domeAutoFollowSat"] = self.ui.domeAutoFollowSat.isChecked()
        config["useInternalSatCalc"] = self.ui.useInternalSatCalc.isChecked()
        config["satBeforeFlip"] = self.ui.satBeforeFlip.isChecked()
        config["satAfterFlip"] = self.ui.satAfterFlip.isChecked()
        config["avoidHorizon"] = self.ui.avoidHorizon.isChecked()
        config["trackingReplay"] = self.ui.trackingReplay.isChecked()

    def setupIcons(self):
        """ """
        self.mainW.wIcon(self.ui.stopSatelliteTracking, "cross-circle")
        self.mainW.wIcon(self.ui.startSatelliteTracking, "start")
        self.mainW.wIcon(self.ui.progSatFull, "run")
        self.mainW.wIcon(self.ui.progSatFiltered, "run")
        self.mainW.wIcon(self.ui.progSatSelected, "run")
        self.mainW.wIcon(self.ui.progTrajectory, "run")

    def enableGuiFunctions(self):
        """ """
        useInternal = self.ui.useInternalSatCalc.isChecked()
        availableInternal = self.app.mount.firmware.checkNewer("3")
        if availableInternal is None:
            return False

        progAvailable = availableInternal and useInternal
        self.ui.trackingReplay.setEnabled(progAvailable)
        self.ui.progTrajectory.setEnabled(progAvailable)
        return True

    def signalSatelliteData(self, alt=[], az=[]):
        """ """
        if not self.satellite:
            return False

        name = self.satellite.name
        self.app.showSatellite.emit(self.satellite, self.satOrbits, alt, az, name)
        return True

    def clearTrackingParameters(self):
        """ """
        self.ui.satTrajectoryStart.setText("-")
        self.ui.satTrajectoryEnd.setText("-")
        self.ui.satTrajectoryFlip.setText("-")
        self.ui.stopSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setEnabled(False)
        self.ui.startSatelliteTracking.setText("Start satellite tracking")
        changeStyleDynamic(self.ui.startSatelliteTracking, "running", False)

    def updatePasses(self):
        """ """
        actMeridianLimit = self.app.mount.setting.meridianLimitTrack
        if actMeridianLimit is None:
            return False

        if actMeridianLimit != self.lastMeridianLimit:
            self.showSatPasses()
            self.lastMeridianLimit = actMeridianLimit
        return True

    def calcTrajectoryData(self, start, end):
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

    def progTrajectoryToMount(self):
        """ """
        useInternal = self.ui.useInternalSatCalc.isChecked()
        isMount = self.app.deviceStat["mount"]
        start, end = self.selectStartEnd()

        if not start or not end:
            return False

        if isMount and useInternal:
            alt, az = self.calcTrajectoryData(start, end)
            start, end, alt, az = self.filterHorizon(start, end, alt, az)
        else:
            alt = []
            az = []

        if isMount and not useInternal:
            self.app.mount.calcTLE(start)

        self.signalSatelliteData(alt=alt, az=az)
        return True

    def showSatPasses(self):
        """ """
        title = "Satellite passes " + self.mainW.timeZoneString()
        self.ui.satPassesGroup.setTitle(title)

        if not self.satellite:
            return False

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

        self.progTrajectoryToMount()
        return True

    def extractSatelliteData(self, satName=""):
        """ """
        satTab = self.ui.listSats
        if satName not in self.satellites.objects:
            return False

        self.mainW.positionCursorInTable(satTab, satName)
        self.satellite = self.satellites.objects[satName]
        self.ui.satelliteName.setText(self.satellite.name)
        epochText = self.satellite.epoch.utc_strftime("%Y-%m-%d, %H:%M")
        self.ui.satelliteEpoch.setText(epochText)

        now = self.app.mount.obsSite.ts.now()
        days = now - self.satellite.epoch
        self.ui.satelliteDataAge.setText(f"{days:2.2f}")
        self.msg.emit(0, "Satellite", "Data", f"Actual satellite: [{satName}]")

        if days > 10:
            changeStyleDynamic(self.ui.satelliteDataAge, "color", "red")
        elif 3 < days < 10:
            changeStyleDynamic(self.ui.satelliteDataAge, "color", "yellow")
        else:
            changeStyleDynamic(self.ui.satelliteDataAge, "color", "")

        self.ui.satelliteNumber.setText(f"{self.satellite.model.satnum:5d}")
        return True

    def programSatToMount(self, satName=""):
        """ """
        if not satName:
            return False
        if satName not in self.satellites.objects:
            return False

        satellite = self.app.mount.satellite
        self.msg.emit(0, "TLE", "Program", f"Upload to mount: [{satName}]")
        line1, line2 = export_tle(self.satellites.objects[satName].model)
        suc = satellite.setTLE(line0=satName, line1=line1, line2=line2)
        if not suc:
            self.msg.emit(2, "TLE", "Program error", "Uploading error")
            return False
        self.app.mount.getTLE()
        return True

    def chooseSatellite(self):
        """ """
        satName = self.ui.listSats.item(self.ui.listSats.currentRow(), 1).text()
        if self.app.deviceStat["mount"]:
            self.programSatToMount(satName=satName)
        else:
            self.extractSatelliteData(satName=satName)
            self.showSatPasses()

        if self.ui.autoSwitchTrack.isChecked():
            self.ui.satTabWidget.setCurrentIndex(1)

    def getSatelliteDataFromDatabase(self, tleParams=None):
        """ """
        if tleParams is None:
            return False

        self.extractSatelliteData(satName=tleParams.name)
        self.showSatPasses()
        return True

    def updateOrbit(self):
        """ """
        if self.satellite is None:
            self.ui.startSatelliteTracking.setEnabled(False)
            self.ui.stopSatelliteTracking.setEnabled(False)
            changeStyleDynamic(self.ui.startSatelliteTracking, "running", False)
            return False

        now = self.app.mount.obsSite.ts.now()
        location = self.app.mount.obsSite.location
        self.app.updateSatellite.emit(now, location)
        return True

    def selectStartEnd(self):
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

    def filterHorizon(self, start, end, alt, az):
        """
        Filter horizon runs from starts on both sides of the track and tries to
        determine, when a track is hidden behind horizon line. As a satellite
        track has to be in one piece, the resulting vectors might have a shorter
        length and a different start and end time.
        """
        useHorizon = self.ui.avoidHorizon.isChecked()
        if not useHorizon:
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

    def startProg(self):
        """ """
        self.clearTrackingParameters()
        isReplay = self.ui.trackingReplay.isChecked()
        t = "for simulation" if isReplay else ""
        self.msg.emit(1, "TLE", "Program", f"Satellite track data {t}")
        start, end = self.selectStartEnd()
        if not start or not end:
            return False
        alt, az = self.calcTrajectoryData(start, end)
        start, end, alt, az = self.filterHorizon(start, end, alt, az)

        if len(alt) == 0:
            text = "Program", "No track data (white), please revise settings"
            self.msg.emit(2, "TLE", "Error", text)
            return False

        factor = int(len(alt) / 900)
        factor = 1 if factor < 1 else factor
        alt = Angle(degrees=np.array_split(alt, factor)[0])
        az = Angle(degrees=np.array_split(az, factor)[0])

        changeStyleDynamic(self.ui.progTrajectory, "running", True)
        self.ui.progTrajectory.setEnabled(False)
        self.ui.progTrajectory.setText("Calculating")
        self.app.mount.progTrajectory(start, alt, az, replay=isReplay)
        return True

    def updateSatelliteTrackGui(self, params=None):
        """ """
        title = "Satellite tracking " + self.mainW.timeZoneString()
        self.ui.satTrackGroup.setTitle(title)

        if params is None or isinstance(params, bool):
            return False

        if params.jdStart is not None and self.satOrbits:
            t = self.mainW.convertTime(params.jdStart, "%d %b  %H:%M:%S")
            self.ui.satTrajectoryStart.setText(t)
        else:
            self.ui.satTrajectoryStart.setText("No transit")

        if params.jdEnd is not None and self.satOrbits:
            t = self.mainW.convertTime(params.jdEnd, "%d %b  %H:%M:%S")
            self.ui.satTrajectoryEnd.setText(t)
        else:
            self.ui.satTrajectoryEnd.setText("No transit")

        if params.flip and self.satOrbits:
            self.ui.satTrajectoryFlip.setText("YES")
        else:
            self.ui.satTrajectoryFlip.setText("NO")

        if params.message is not None:
            self.msg.emit(0, "TLE", "Message", f"{params.message}")

        if params.jdStart is not None and self.satOrbits:
            self.ui.stopSatelliteTracking.setEnabled(True)
            self.ui.startSatelliteTracking.setEnabled(True)
        else:
            self.ui.stopSatelliteTracking.setEnabled(False)
            self.ui.startSatelliteTracking.setEnabled(False)

        return True

    def updateInternalTrackGui(self, params=None):
        """ """
        self.ui.progTrajectory.setEnabled(True)
        self.ui.progTrajectory.setText("Program trajectory")
        self.updateSatelliteTrackGui(params)
        self.msg.emit(1, "TLE", "Program", "Satellite track data ready!")

    def startTrack(self):
        """ """
        if not self.app.deviceStat["mount"]:
            self.msg.emit(2, "TLE", "Program", "Mount is not online")
            return False

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
            return False

        changeStyleDynamic(self.ui.startSatelliteTracking, "running", True)
        self.msg.emit(0, "TLE", "Command ", f"{message}")
        self.app.mount.satellite.setTrackingOffsets()
        return True

    def stopTrack(self):
        """ """
        if not self.app.deviceStat["mount"]:
            self.msg.emit(2, "TLE", "Command", "Mount is not online")
            return False

        suc = self.app.mount.obsSite.startTracking()
        if not suc:
            self.msg.emit(2, "TLE", "Command", "Cannot stop tracking")
            return False

        self.ui.startSatelliteTracking.setText("Start satellite tracking")
        changeStyleDynamic(self.ui.startSatelliteTracking, "running", False)
        self.msg.emit(0, "TLE", "Command", "Stopped tracking")
        return suc

    def toggleTrackingOffset(self, obs):
        """ """
        if not self.app.mount.firmware.checkNewer("3"):
            return False

        if obs.status == 10:
            self.ui.satOffGroup.setEnabled(True)
        else:
            self.ui.satOffGroup.setEnabled(False)
        return True

    def followMount(self, obs):
        """ """
        TLESCK = {
            "V": "is slewing to transit start",
            "P": "is waiting for satellite",
            "S": "is catching satellite",
            "T": "is tracking satellite",
        }

        status = obs.status
        if status != 10:
            return False
        if not self.ui.domeAutoFollowSat.isChecked():
            return False
        if not self.app.deviceStat["dome"]:
            return False

        stat = obs.statusSat
        statText = TLESCK[stat] if stat in TLESCK else ""
        self.ui.startSatelliteTracking.setText(statText)

        azimuth = obs.Az.degrees
        altitude = obs.Alt.degrees
        self.app.dome.slewDome(altitude=altitude, azimuth=azimuth, follow=True)
        return True

    def setTrackingOffsets(self):
        """ """
        valT = self.ui.satOffTime.value()
        valR = self.ui.satOffRa.value()
        valD = self.ui.satOffDec.value()
        suc = self.app.mount.satellite.setTrackingOffsets(Time=valT, RA=valR, DECcorr=valD)
        if not suc:
            self.msg.emit(2, "TLE", "Command error", "Cannot change offset")
        return suc
