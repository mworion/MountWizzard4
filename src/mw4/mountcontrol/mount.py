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
import socket
import wakeonlan
from mw4.base.ethernet import checkFormatMAC
from mw4.base.tpool import Worker
from mw4.mountcontrol.dome import Dome
from mw4.mountcontrol.firmware import Firmware
from mw4.mountcontrol.geometry import Geometry
from mw4.mountcontrol.model import Model
from mw4.mountcontrol.mountSignals import MountSignals
from mw4.mountcontrol.obsSite import ObsSite
from mw4.mountcontrol.satellite import Satellite
from mw4.mountcontrol.setting import Setting
from PySide6.QtCore import QMutex, QTimer
from skyfield.api import Angle


class MountDevice:
    """ """

    CYCLE_POINTING = 500
    CYCLE_DOME = 950
    CYCLE_CLOCK = 1000
    CYCLE_MOUNT_UP = 2000
    CYCLE_SETTING = 3100
    DEFAULT_PORT = 3492
    SOCKET_TIMEOUT = 2

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

        self.workerMountIsUp: Worker = None
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
        self.mutexCycleMountIsUp = QMutex()
        self.mutexCycleClock = QMutex()
        self.mutexCycleDome = QMutex()
        self.mutexCycleSetting = QMutex()
        self.mutexCyclePointing = QMutex()
        self.mutexGetTLE = QMutex()
        self.mutexCalcTLE = QMutex()
        self.mountIsUp: bool = False
        self.mountIsUpLastStatus: bool = False
        self.statusAlert: bool = False
        self.statusSlew: bool = False

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
        self.timerMountIsUp = QTimer()
        self.timerMountIsUp.setSingleShot(False)
        self.timerMountIsUp.timeout.connect(self.cycleCheckMountIsUp)
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
        self._waitTimeFlip = int(value * 1000)

    def waitAfterSettlingAndEmit(self):
        """ """
        self.signals.slewed.emit()

    def startMountTimers(self):
        """ """
        self.timerMountIsUp.start(self.CYCLE_MOUNT_UP)
        self.timerPointing.start(self.CYCLE_POINTING)
        self.timerSetting.start(self.CYCLE_SETTING)

    def stopAllMountTimers(self):
        """ """
        self.timerMountIsUp.stop()
        self.timerPointing.stop()
        self.timerClock.stop()
        self.timerDome.stop()
        self.timerSetting.stop()

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

    def startupMountData(self, mountIsUp: bool) -> None:
        """ """
        if mountIsUp and not self.mountIsUpLastStatus:
            self.mountIsUpLastStatus = True
            self.obsSite.setHighPrecision()
            self.getFW()
            self.getLocation()
            self.app.refreshModel.emit()
            self.app.refreshName.emit()
            self.getTLE()

        elif not mountIsUp:
            self.mountIsUpLastStatus = False

    def checkMountIsUp(self):
        """ """
        client = socket.socket()
        client.settimeout(self.SOCKET_TIMEOUT)
        try:
            client.connect(self.host)
            client.shutdown(socket.SHUT_RDWR)
        except TimeoutError:
            self.mountIsUp = False
            self.log.info("Mount connection timed out")
        except Exception as e:
            self.log.error(f"Mount {e}")
            self.mountIsUp = False
        else:
            self.mountIsUp = True
        finally:
            client.close()

    def clearCycleCheckMountIsUp(self):
        """ """
        self.startupMountData(self.mountIsUp)
        self.signals.mountIsUp.emit(self.mountIsUp)
        self.mutexCycleMountIsUp.unlock()

    def cycleCheckMountIsUp(self):
        """ """
        if not self.host:
            self.signals.mountIsUp.emit(False)
            return

        if not self.mutexCycleMountIsUp.tryLock():
            return

        self.workerMountIsUp = Worker(self.checkMountIsUp)
        self.workerMountIsUp.signals.finished.connect(self.clearCycleCheckMountIsUp)
        self.threadPool.start(self.workerMountIsUp)

    def clearCyclePointing(self, result: bool) -> None:
        """ """
        if self.obsSite.status in [1, 98, 99]:
            if not self.statusAlert:
                self.signals.alert.emit()
            self.statusAlert = True
        else:
            self.statusAlert = False

        settleWait = self._waitTimeFlip if self.obsSite.flipped else 0

        if self.obsSite.statusSlew:
            self.statusSlew = True
        else:
            if self.statusSlew:
                self.statusSlew = False
                self.settlingWait.start(settleWait)

        if result:
            self.signals.pointDone.emit(self.obsSite)
        self.mutexCyclePointing.unlock()

    def cyclePointing(self):
        """"""
        if not self.mountIsUp:
            return

        if not self.mutexCyclePointing.tryLock():
            return

        self.workerCyclePointing = Worker(self.obsSite.pollPointing)
        self.workerCyclePointing.signals.result.connect(self.clearCyclePointing)
        self.threadPool.start(self.workerCyclePointing)

    def clearCycleSetting(self, result):
        """ """
        if result:
            self.signals.settingDone.emit(self.setting)
        self.mutexCycleSetting.unlock()

    def cycleSetting(self):
        """ """
        if not self.mountIsUp:
            return
        if not self.mutexCycleSetting.tryLock():
            return

        self.workerCycleSetting = Worker(self.setting.pollSetting)
        self.workerCycleSetting.signals.result.connect(self.clearCycleSetting)
        self.threadPool.start(self.workerCycleSetting)

    def clearGetModel(self):
        """ """
        self.signals.getModelDone.emit(self.model)

    def getModel(self):
        """ """
        if not self.mountIsUp:
            return
        self.workerGetModel = Worker(self.model.pollStars)
        self.workerGetModel.signals.finished.connect(self.clearGetModel)
        self.threadPool.start(self.workerGetModel)

    def clearGetNames(self):
        """ """
        self.signals.namesDone.emit(self.model)

    def getNames(self):
        """ """
        if not self.mountIsUp:
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
        if not self.mountIsUp:
            return

        self.workerGetFW = Worker(self.firmware.poll)
        self.workerGetFW.signals.finished.connect(self.clearGetFW)
        self.threadPool.start(self.workerGetFW)

    def clearGetLocation(self):
        """ """
        self.signals.locationDone.emit(self.obsSite)

    def getLocation(self):
        """ """
        if not self.mountIsUp:
            return

        self.workerGetLocation = Worker(self.obsSite.getLocation)
        self.workerGetLocation.signals.finished.connect(self.clearGetLocation)
        self.threadPool.start(self.workerGetLocation)

    def clearCalcTLE(self):
        """ """
        self.mutexCalcTLE.unlock()
        self.signals.calcTLEdone.emit(self.satellite.tleParams)

    def calcTLE(self, start: float) -> None:
        """ """
        if not self.mountIsUp:
            return
        if not self.mutexCalcTLE.tryLock():
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
        self.mutexGetTLE.unlock()
        self.signals.getTLEdone.emit(self.satellite.tleParams)

    def getTLE(self):
        """ """
        if not self.mountIsUp:
            return
        if not self.mutexGetTLE.tryLock():
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
            self.mountIsUp = False
        return suc

    def clearDome(self, result):
        """ """
        if result:
            self.signals.domeDone.emit(self.dome)

    def cycleDome(self):
        """ """
        if not self.mountIsUp:
            return

        self.workerCycleDome = Worker(self.dome.poll)
        self.workerCycleDome.signals.result.connect(self.clearDome)
        self.threadPool.start(self.workerCycleDome)

    def clearCycleClock(self):
        """ """
        self.mutexCycleClock.unlock()

    def cycleClock(self):
        """ """
        if not self.mountIsUp:
            return

        if not self.mutexCycleClock.tryLock():
            return

        self.workerCycleClock = Worker(self.obsSite.pollSyncClock)
        self.workerCycleClock.signals.finished.connect(self.clearCycleClock)
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
        if not self.mountIsUp:
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
