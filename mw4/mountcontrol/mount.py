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
import socket
import logging

# external packages
from PySide6.QtCore import QTimer, QMutex
import wakeonlan
from skyfield.api import Angle

# local imports
from mountcontrol.mountSignals import MountSignals
from mountcontrol.firmware import Firmware
from mountcontrol.obsSite import ObsSite
from mountcontrol.setting import Setting
from mountcontrol.satellite import Satellite
from mountcontrol.geometry import Geometry
from mountcontrol.dome import Dome
from mountcontrol.model import Model
from base.ethernet import checkFormatMAC
from base.tpool import Worker

__all__ = ["MountDevice"]


class MountDevice:
    """ """

    CYCLE_POINTING = 500
    CYCLE_DOME = 950
    CYCLE_CLOCK = 1000
    CYCLE_MOUNT_UP = 2000
    CYCLE_SETTING = 3100
    DEFAULT_PORT = 3492
    SOCKET_TIMEOUT = 0.5

    log = logging.getLogger("MW4")

    def __init__(self, app, host, MAC, pathToData, verbose):
        self._waitTime = 0
        self._waitTimeFlip = 0

        self.app = app
        self.host = host
        self.MAC = MAC
        self.threadPool = app.threadPool
        self.pathToData = pathToData
        self.verbose = verbose

        self.signals = MountSignals()
        self.firmware = Firmware(parent=self)
        self.setting = Setting(parent=self)
        self.obsSite = ObsSite(parent=self, verbose=self.verbose)
        self.satellite = Satellite(parent=self)
        self.geometry = Geometry(parent=self)
        self.dome = Dome(parent=self)
        self.model = Model(parent=self)

        self.workerMountUp: Worker = None
        self.workerCycleClock: Worker = None
        self.workerCycleSetting: Worker = None
        self.workerCyclePointing: Worker = None
        self.workerGetLocation: Worker = None
        self.workerGetFW: Worker = None
        self.workerGetTLE: Worker = None
        self.workerCalcTLE: Worker = None
        self.workerStatTLE: Worker = None
        self.workerGetModel: Worker = None
        self.workerGetNames: Worker = None
        self.workerTrajectory: Worker = None
        self.workerCycleDome: Worker = None
        self.mutexCycleMountUp = QMutex()
        self.mutexCycleClock = QMutex()
        self.mutexCycleDome = QMutex()
        self.mutexCycleSetting = QMutex()
        self.mutexCyclePointing = QMutex()
        self.mountUp: bool = False
        self.mountUpLastStatus: bool = False
        self.statusAlert: bool = False
        self.statusSlew: bool = True

        self.timerPointing = QTimer()
        self.timerPointing.setSingleShot(False)
        self.timerPointing.timeout.connect(self.cyclePointing)
        self.timerDome = QTimer()
        self.timerDome.setSingleShot(False)
        self.timerDome.timeout.connect(self.cycleDome)
        self.timerClock = QTimer()
        self.timerClock.setSingleShot(False)
        self.timerClock.timeout.connect(self.cycleClock)
        self.timerSetting = QTimer()
        self.timerSetting.setSingleShot(False)
        self.timerSetting.timeout.connect(self.cycleSetting)
        self.timerMountUp = QTimer()
        self.timerMountUp.setSingleShot(False)
        self.timerMountUp.timeout.connect(self.cycleCheckMountUp)
        self.settlingWait = QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitAfterSettlingAndEmit)

    @property
    def MAC(self):
        return self._MAC

    @MAC.setter
    def MAC(self, value):
        value = checkFormatMAC(value)
        self._MAC = value

    @property
    def waitTimeFlip(self):
        return self._waitTimeFlip / 1000

    @waitTimeFlip.setter
    def waitTimeFlip(self, value):
        self._waitTimeFlip = value * 1000

    def waitAfterSettlingAndEmit(self):
        """ """
        self.signals.slewed.emit()

    def startMountTimers(self):
        """ """
        self.timerSetting.start(self.CYCLE_SETTING)
        self.timerPointing.start(self.CYCLE_POINTING)
        self.timerMountUp.start(self.CYCLE_MOUNT_UP)

    def stopAllMountTimers(self):
        """ """
        self.timerSetting.stop()
        self.timerPointing.stop()
        self.timerMountUp.stop()
        self.timerDome.stop()
        self.timerClock.stop()

    def startDomeTimer(self):
        """ """
        self.timerDome.start(self.CYCLE_DOME)

    def stopDomeTimer(self):
        """ """
        self.timerDome.stop()

    def startMountClockTimer(self):
        """ """
        self.timerClock.start(self.CYCLE_CLOCK)

    def stopMountClockTimer(self):
        """ """
        self.timerClock.stop()

    def resetData(self):
        """ """
        self.firmware = Firmware(parent=self)
        self.dome = Dome(parent=self)
        self.setting = Setting(parent=self)
        self.model = Model(parent=self)
        self.obsSite = ObsSite(parent=self, verbose=self.verbose)
        self.satellite = Satellite(parent=self)
        self.geometry = Geometry(parent=self)
        self.signals.pointDone.emit(self.obsSite)
        self.signals.settingDone.emit(self.setting)
        self.signals.getModelDone.emit(self.model)
        self.signals.namesDone.emit(self.model)
        self.signals.firmwareDone.emit(self.firmware)
        self.signals.locationDone.emit(self.obsSite)

    def startupMountData(self, status: bool) -> None:
        """ """
        if status and not self.mountUpLastStatus:
            self.mountUpLastStatus = True
            self.getFW()
            self.getLocation()
            self.app.refreshModel.emit()
            self.app.refreshName.emit()
            self.getTLE()

        elif not status and self.mountUpLastStatus:
            self.mountUpLastStatus = False
            location = self.obsSite.location
            self.resetData()
            self.obsSite.location = location

    def checkMountUp(self):
        """ """
        client = socket.socket()
        client.settimeout(self.SOCKET_TIMEOUT)
        try:
            client.connect(self.host)
            client.shutdown(socket.SHUT_RDWR)
        except Exception:
            self.mountUp = False
        else:
            self.mountUp = True
        finally:
            client.close()

    def clearCycleCheckMountUp(self):
        """ """
        self.startupMountData(self.mountUp)
        self.signals.mountUp.emit(self.mountUp)
        self.mutexCycleMountUp.unlock()

    def cycleCheckMountUp(self):
        """ """
        if not self.host:
            self.signals.mountUp.emit(False)
            return

        if not self.mutexCycleMountUp.tryLock():
            return

        self.workerMountUp = Worker(self.checkMountUp)
        self.workerMountUp.signals.finished.connect(self.clearCycleCheckMountUp)
        self.threadPool.start(self.workerMountUp)

    def clearCyclePointing(self):
        """ """
        if self.obsSite.status in [1, 98, 99]:
            if not self.statusAlert:
                self.signals.alert.emit()
            self.statusAlert = True
        else:
            self.statusAlert = False

        if self.obsSite.flipped:
            settleWait = self._waitTimeFlip
        else:
            settleWait = 0

        if self.obsSite.status not in [2, 6]:
            if not self.statusSlew:
                self.settlingWait.start(int(settleWait))
            self.statusSlew = True
        else:
            self.statusSlew = False

        self.signals.pointDone.emit(self.obsSite)
        self.mutexCyclePointing.unlock()

    def cyclePointing(self):
        """"""
        if not self.mountUp:
            return

        if not self.mutexCyclePointing.tryLock():
            return

        self.workerCyclePointing = Worker(self.obsSite.pollPointing)
        self.workerCyclePointing.signals.finished.connect(self.clearCyclePointing)
        self.threadPool.start(self.workerCyclePointing)

    def clearCycleSetting(self):
        """ """
        self.signals.settingDone.emit(self.setting)
        self.mutexCycleSetting.unlock()

    def cycleSetting(self):
        """ """
        if not self.mountUp:
            return

        if not self.mutexCycleSetting.tryLock():
            return

        self.workerCycleSetting = Worker(self.setting.pollSetting)
        self.workerCycleSetting.signals.finished.connect(self.clearCycleSetting)
        self.threadPool.start(self.workerCycleSetting)

    def clearGetModel(self):
        """ """
        self.signals.getModelDone.emit(self.model)

    def getModel(self):
        """ """
        if not self.mountUp:
            return
        self.workerGetModel = Worker(self.model.pollStars)
        self.workerGetModel.signals.finished.connect(self.clearGetModel)
        self.threadPool.start(self.workerGetModel)

    def clearGetNames(self):
        """ """
        self.signals.namesDone.emit(self.model)

    def getNames(self):
        """ """
        if not self.mountUp:
            return

        self.workerGetNames = Worker(self.model.pollNames)
        self.workerGetNames.signals.finished.connect(self.clearGetNames)
        self.threadPool.start(self.workerGetNames)

    def clearGetFW(self):
        """ """
        self.log.header("-" * 100)
        self.log.header(f"10micron product : {self.firmware.product}")
        self.log.header(f"10micron firmware: {self.firmware.vString}")
        self.log.header(f"10micron host    : {self.host}")
        self.log.header("-" * 100)
        self.geometry.initializeGeometry(self.firmware.product)
        self.signals.firmwareDone.emit(self.firmware)

    def getFW(self):
        """ """
        if not self.mountUp:
            return

        self.workerGetFW = Worker(self.firmware.poll)
        self.workerGetFW.signals.finished.connect(self.clearGetFW)
        self.threadPool.start(self.workerGetFW)

    def clearGetLocation(self):
        """ """
        self.signals.locationDone.emit(self.obsSite)

    def getLocation(self):
        """ """
        if not self.mountUp:
            return

        self.workerGetLocation = Worker(self.obsSite.getLocation)
        self.workerGetLocation.signals.finished.connect(self.clearGetLocation)
        self.threadPool.start(self.workerGetLocation)

    def clearCalcTLE(self):
        """ """
        self.signals.calcTLEdone.emit(self.satellite.tleParams)

    def calcTLE(self, start):
        """ """
        if not self.mountUp:
            return

        self.workerCalcTLE = Worker(self.satellite.calcTLE, start)
        self.workerCalcTLE.signals.finished.connect(self.clearCalcTLE)
        self.threadPool.start(self.workerCalcTLE)

    def clearStatTLE(self):
        """ """
        self.signals.statTLEdone.emit(self.satellite.tleParams)

    def statTLE(self):
        """ """
        self.workerStatTLE = Worker(self.satellite.statTLE)
        self.workerStatTLE.signals.finished.connect(self.clearStatTLE)
        self.threadPool.start(self.workerStatTLE)

    def clearGetTLE(self):
        """ """
        self.signals.getTLEdone.emit(self.satellite.tleParams)

    def getTLE(self):
        """ """
        if not self.mountUp:
            return

        self.workerGetTLE = Worker(self.satellite.getTLE)
        self.workerGetTLE.signals.finished.connect(self.clearGetTLE)
        self.threadPool.start(self.workerGetTLE)

    def bootMount(self, bAddress="", bPort=0):
        """ """
        t = f"MAC: [{self.MAC}], broadcast address: [{bAddress}], port: [{bPort}]"
        self.log.debug(t)
        if self.MAC is None:
            return False
        try:
            if bAddress and bPort:
                wakeonlan.send_magic_packet(self.MAC, ip_address=bAddress, port=bPort)
            else:
                wakeonlan.send_magic_packet(self.MAC)
        except Exception as e:
            self.log.warning(f"Boot mount failed: {e}")
            return False
        return True

    def shutdown(self):
        """ """
        suc = self.obsSite.shutdown()
        if suc:
            self.mountUp = False
        return suc

    def clearDome(self):
        """ """
        self.signals.domeDone.emit(self.dome)

    def cycleDome(self):
        """ """
        if not self.mountUp:
            return

        self.workerCycleDome = Worker(self.dome.poll)
        self.workerCycleDome.signals.finished.connect(self.clearDome)
        self.threadPool.start(self.workerCycleDome)

    def cycleClock(self):
        """ """
        if not self.mountUp:
            return

        if not self.mutexCycleClock.tryLock():
            return

        self.workerCycleClock = Worker(self.obsSite.pollSyncClock)
        self.threadPool.start(self.workerCycleClock)

    def clearProgTrajectory(self):
        """ """
        self.signals.calcTrajectoryDone.emit(self.satellite.trajectoryParams)

    def workerProgTrajectory(self, alt, az, replay=False):
        """ """
        self.satellite.addTrajectoryPoint(alt, az)
        self.satellite.preCalcTrajectory(replay=replay)
        return replay

    def progTrajectory(self, start, alt, az, replay=False):
        """ """
        if not self.mountUp:
            return

        self.satellite.startProgTrajectory(julD=start)
        self.workerTrajectory = Worker(self.workerProgTrajectory, alt, az, replay=replay)
        self.workerTrajectory.signals.result.connect(self.clearProgTrajectory)
        self.threadPool.start(self.workerTrajectory)

    def calcTransformationMatricesTarget(self):
        """ """
        ha = self.obsSite.haJNowTarget
        dec = self.obsSite.decJNowTarget
        lat = self.obsSite.location.latitude
        pierside = self.obsSite.piersideTarget
        return self.geometry.calcTransformationMatrices(ha, dec, lat, pierside)

    def calcTransformationMatricesActual(self):
        """ """
        ha = self.obsSite.haJNow
        dec = self.obsSite.decJNow
        lat = self.obsSite.location.latitude
        pierside = self.obsSite.pierside
        return self.geometry.calcTransformationMatrices(ha, dec, lat, pierside)

    def calcMountAltAzToDomeAltAz(self, alt, az):
        """ """
        suc = self.obsSite.setTargetAltAz(alt=Angle(degrees=alt), az=Angle(degrees=az))
        if not suc:
            return None, None
        alt, az, _, _, _ = self.calcTransformationMatricesTarget()
        return alt, az
