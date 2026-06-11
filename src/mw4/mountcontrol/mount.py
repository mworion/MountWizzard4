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
# License APL2.0
#
###########################################################
import logging
import socket
import wakeonlan
from collections.abc import Callable
from mw4.base.ethernet import checkFormatMAC
from mw4.base.tpool import Worker
from mw4.mountcontrol.dome import Dome
from mw4.mountcontrol.firmware import Firmware
from mw4.mountcontrol.geometry import Geometry
from mw4.mountcontrol.model import Model
from mw4.mountcontrol.mountSignals import MountSignals
from mw4.mountcontrol.obsSite import MountStatus, ObsSite
from mw4.mountcontrol.satellite import Satellite
from mw4.mountcontrol.setting import Setting
from pathlib import Path
from PySide6.QtCore import QMutex, QObject, QTimer
from skyfield.api import Angle
from typing import Any, Final


class MountDevice(QObject):
    """Top-level controller for a 10micron mount.

    Owns device sub-objects (firmware, setting, obsSite, satellite, geometry,
    dome, model), manages cyclic polling via QTimers and worker threads, and
    re-emits results through ``MountSignals``.

    Return-value convention used throughout the public API:

    - Imperative commands that can fail (``bootMount``, ``shutdown``) return
      ``bool`` so callers can react to success/failure.
    - Scheduler / cycle / get methods communicate exclusively through Qt
      signals and therefore return ``None``.
    - Pure computations (``calc*``) return their computed values and use
      ``None`` to signal invalid input.
    """

    CYCLE_POINTING: Final[int] = 500
    CYCLE_DOME: Final[int] = 950
    CYCLE_CLOCK: Final[int] = 1000
    CYCLE_MOUNT_UP: Final[int] = 1000
    CYCLE_SETTING: Final[int] = 3100
    DEFAULT_PORT: Final[int] = 3492
    SOCKET_TIMEOUT: Final[int] = 1
    ALERT_STATUS_CODES: Final[frozenset[MountStatus]] = frozenset(
        {MountStatus.STOPPED, MountStatus.UNKNOWN, MountStatus.ERROR}
    )
    log = logging.getLogger("MW4")

    def __init__(
        self,
        app: Any,
        host: tuple[str, int] | None = None,
        MAC: str = "00:00:00:00:00:00",
        verbose: bool = False,
    ) -> None:
        super().__init__()
        self._waitTime = 0
        self._waitTimeFlip = 0
        self.app = app
        self.host = host
        self.MAC = MAC
        self.threadPool = app.threadPool
        self.pathToData: Path = app.mwGlob["dataDir"]
        self.verbose: bool = verbose
        self.loggingTrace: bool = False

        self.signals = MountSignals()
        self.firmware = Firmware(parent=self)
        self.setting = Setting(parent=self)
        self.obsSite = ObsSite(parent=self, verbose=self.verbose)
        self.satellite = Satellite(parent=self)
        self.geometry = Geometry(parent=self)
        self.dome = Dome(parent=self)
        self.model = Model(parent=self)

        self.workerMountIsUp: Worker | None = None
        self.workerCycleClock: Worker | None = None
        self.workerCycleSetting: Worker | None = None
        self.workerCyclePointing: Worker | None = None
        self.workerGetLocation: Worker | None = None
        self.workerGetFW: Worker | None = None
        self.workerGetTLE: Worker | None = None
        self.workerCalcTLE: Worker | None = None
        self.workerStatTLE: Worker | None = None
        self.workerGetModel: Worker | None = None
        self.workerGetNames: Worker | None = None
        self.workerTrajectory: Worker | None = None
        self.workerCycleDome: Worker | None = None
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
        self.app.update1s.connect(self.collectData)
        self.app.start3s.connect(self.resetAfterStart)
        self.data: dict = {}
        self.raRef: float = 0.0
        self.decRef: float = 0.0

    @property
    def MAC(self) -> str:
        return self._MAC

    @MAC.setter
    def MAC(self, value: Any) -> None:
        value = checkFormatMAC(value)
        self._MAC = value

    @property
    def waitTimeFlip(self) -> float:
        return self._waitTimeFlip / 1000

    @waitTimeFlip.setter
    def waitTimeFlip(self, value: float) -> None:
        if value < 0:
            raise ValueError("waitTimeFlip must be non-negative")
        self._waitTimeFlip = int(value * 1000)

    def resetAfterStart(self) -> None:
        self.raRef = self.obsSite.raJNow.degrees
        self.decRef = self.obsSite.decJNow.degrees

    def collectData(self) -> None:
        if self.obsSite.statusSlew:
            self.raRef = self.obsSite.raJNow.degrees
            self.decRef = self.obsSite.decJNow.degrees

        deltaRaJNow = (self.obsSite.raJNow.degrees - self.raRef) * 3600
        deltaDecJNow = (self.obsSite.decJNow.degrees - self.decRef) * 3600
        self.data["deltaRaJNow"] = deltaRaJNow
        self.data["deltaDecJNow"] = deltaDecJNow
        self.data["errorAngularPosRA"] = self.obsSite.errorAngularPosRA.degrees * 3600
        self.data["errorAngularPosDEC"] = self.obsSite.errorAngularPosDEC.degrees * 3600
        self.data["status"] = self.obsSite.status
        self.data["timeDiff"] = self.obsSite.timeDiff * 1000

    def waitAfterSettlingAndEmit(self) -> None:
        self.signals.slewed.emit()

    def runWorker(
        self,
        target: Callable[..., Any],
        clearMethod: Callable[..., Any],
        workerAttr: str,
        *args: Any,
        mutex: QMutex | None = None,
        useResult: bool = False,
        requireMountUp: bool = True,
        **kwargs: Any,
    ) -> None:
        """Schedule ``target`` on the thread pool and wire up its callback.

        Centralises the boilerplate shared by every cycle/get/poll method:

        - Optional ``mountIsUp`` gate (default on).
        - Optional non-blocking mutex acquisition (returns silently if busy).
        - Worker creation, ``finished`` / ``result`` signal connection, and
          storage of the worker on ``self`` under ``workerAttr`` so callers
          can introspect it.
        """
        if requireMountUp and not self.mountIsUp:
            return
        if mutex is not None and not mutex.tryLock():
            return
        worker = Worker(target, *args, **kwargs)
        sig = worker.signals.result if useResult else worker.signals.finished
        sig.connect(clearMethod)
        setattr(self, workerAttr, worker)
        self.threadPool.start(worker)

    def startMountCoreTimers(self) -> None:
        self.timerMountIsUp.start(self.CYCLE_MOUNT_UP)
        self.timerPointing.start(self.CYCLE_POINTING)
        self.timerSetting.start(self.CYCLE_SETTING)

    def stopAllMountTimers(self) -> None:
        self.timerMountIsUp.stop()
        self.timerPointing.stop()
        self.timerClock.stop()
        self.timerDome.stop()
        self.timerSetting.stop()

    def startDomeTimer(self) -> None:
        self.timerDome.start(self.CYCLE_DOME)

    def stopDomeTimer(self) -> None:
        self.timerDome.stop()

    def startMountClockTimer(self) -> None:
        self.timerClock.start(self.CYCLE_CLOCK)

    def stopMountClockTimer(self) -> None:
        self.timerClock.stop()

    def startupMountData(self) -> None:
        if self.mountIsUp and not self.mountIsUpLastStatus:
            self.mountIsUpLastStatus = True
            self.obsSite.setHighPrecision()
            self.getFW()
            self.getLocation()
            self.app.refreshModel.emit()
            self.app.refreshName.emit()
            self.getTLE()
            self.signals.deviceConnected.emit("mount")
        elif not self.mountIsUp and self.mountIsUpLastStatus:
            self.signals.deviceDisconnected.emit("mount")
            self.mountIsUpLastStatus = False

    def checkMountIsUp(self) -> None:
        self.mountIsUp = False
        try:
            with socket.socket() as client:
                client.settimeout(self.SOCKET_TIMEOUT)
                client.connect(self.host)
                client.shutdown(socket.SHUT_RDWR)
                self.mountIsUp = True
        except TimeoutError:
            self.log.info("Mount connection timed out")
        except Exception as e:
            self.log.error(f"Mount {e}")

    def clearCycleCheckMountIsUp(self) -> None:
        self.startupMountData()
        self.signals.mountIsUp.emit(self.mountIsUp)
        self.mutexCycleMountIsUp.unlock()

    def cycleCheckMountIsUp(self) -> None:
        if not self.host:
            self.signals.mountIsUp.emit(False)
            return
        self.runWorker(
            self.checkMountIsUp,
            self.clearCycleCheckMountIsUp,
            "workerMountIsUp",
            mutex=self.mutexCycleMountIsUp,
            requireMountUp=False,
        )

    def clearCyclePointing(self, result: bool) -> None:
        if self.obsSite.status in self.ALERT_STATUS_CODES:
            if not self.statusAlert:
                self.signals.alert.emit()
            self.statusAlert = True
        else:
            self.statusAlert = False

        settleWait = self._waitTimeFlip if self.obsSite.flipped else 0
        if not self.obsSite.statusSlew and self.statusSlew:
            self.settlingWait.start(settleWait)
        self.statusSlew = self.obsSite.statusSlew

        if result:
            self.signals.pointDone.emit(self.obsSite)
        self.mutexCyclePointing.unlock()

    def cyclePointing(self) -> None:
        self.runWorker(
            self.obsSite.pollPointing,
            self.clearCyclePointing,
            "workerCyclePointing",
            mutex=self.mutexCyclePointing,
            useResult=True,
        )

    def clearCycleSetting(self, result: bool) -> None:
        self.mutexCycleSetting.unlock()
        if result:
            self.signals.settingDone.emit(self.setting)

    def cycleSetting(self) -> None:
        self.runWorker(
            self.setting.pollSetting,
            self.clearCycleSetting,
            "workerCycleSetting",
            mutex=self.mutexCycleSetting,
            useResult=True,
        )

    def clearGetModel(self) -> None:
        self.signals.getModelDone.emit(self.model)

    def getModel(self) -> None:
        self.runWorker(self.model.pollStars, self.clearGetModel, "workerGetModel")

    def clearGetNames(self) -> None:
        self.signals.namesDone.emit(self.model)

    def getNames(self) -> None:
        self.runWorker(self.model.pollNames, self.clearGetNames, "workerGetNames")

    def clearGetFW(self) -> None:
        self.geometry.initializeGeometry(self.firmware.product)
        self.signals.firmwareDone.emit(self.firmware)

    def getFW(self) -> None:
        self.runWorker(self.firmware.poll, self.clearGetFW, "workerGetFW")

    def clearGetLocation(self) -> None:
        self.signals.locationDone.emit(self.obsSite)

    def getLocation(self) -> None:
        self.runWorker(self.obsSite.getLocation, self.clearGetLocation, "workerGetLocation")

    def clearCalcTLE(self) -> None:
        self.mutexCalcTLE.unlock()
        self.signals.calcTLEdone.emit(self.satellite.tleParams)

    def calcTLE(self, start: float) -> None:
        self.runWorker(
            self.satellite.calcTLE,
            self.clearCalcTLE,
            "workerCalcTLE",
            start,
            mutex=self.mutexCalcTLE,
        )

    def clearStatTLE(self) -> None:
        self.signals.statTLEdone.emit(self.satellite.tleParams)

    def statTLE(self) -> None:
        self.runWorker(self.satellite.statTLE, self.clearStatTLE, "workerStatTLE")

    def clearGetTLE(self) -> None:
        self.mutexGetTLE.unlock()
        self.signals.getTLEdone.emit(self.satellite.tleParams)

    def getTLE(self) -> None:
        self.runWorker(
            self.satellite.getTLE,
            self.clearGetTLE,
            "workerGetTLE",
            mutex=self.mutexGetTLE,
        )

    def bootMount(self, bAddress: str = "", bPort: int = 0) -> bool:
        t = f"MAC: [{self.MAC}], broadcast address: [{bAddress}], port: [{bPort}]"
        self.log.debug(t)
        if self.MAC is None:
            return False
        kwargs: dict[str, Any] = {}
        if bAddress:
            kwargs["ip_address"] = bAddress
        if bPort:
            kwargs["port"] = bPort
        try:
            wakeonlan.send_magic_packet(self.MAC, **kwargs)
        except Exception as e:
            self.log.warning(f"Boot mount failed: {e}")
            return False
        return True

    def shutdown(self) -> bool:
        suc = self.obsSite.shutdown()
        if suc:
            self.mountIsUp = False
        return suc

    def clearDome(self, result: bool) -> None:
        self.mutexCycleDome.unlock()
        if result:
            self.signals.domeDone.emit(self.dome)

    def cycleDome(self) -> None:
        self.runWorker(
            self.dome.poll,
            self.clearDome,
            "workerCycleDome",
            mutex=self.mutexCycleDome,
            useResult=True,
        )

    def clearCycleClock(self) -> None:
        # Intentional: ``workerCycleClock`` is the public liveness indicator
        # consumed by ``tabMount_Sett.showOffset`` to colour-code the
        # PC↔mount time delta. Resetting it here lets that consumer see when
        # the periodic clock sync has stopped running. Other workers are not
        # cleared because no caller depends on their post-run state.
        self.mutexCycleClock.unlock()
        self.workerCycleClock = None

    def cycleClock(self) -> None:
        self.runWorker(
            self.obsSite.pollSyncClock,
            self.clearCycleClock,
            "workerCycleClock",
            mutex=self.mutexCycleClock,
        )

    def clearProgTrajectory(self) -> None:
        self.signals.calcTrajectoryDone.emit(self.satellite.trajectoryParams)

    def runnerProgTrajectory(self, alt: Angle, az: Angle, replay: bool = False) -> bool:
        self.satellite.addTrajectoryPoint(alt, az)
        self.satellite.preCalcTrajectory(replay=replay)
        return replay

    def progTrajectory(
        self, start: float, alt: Angle, az: Angle, replay: bool = False
    ) -> None:
        if not self.mountIsUp:
            return
        self.satellite.startProgTrajectory(julD=start)
        self.runWorker(
            self.runnerProgTrajectory,
            self.clearProgTrajectory,
            "workerTrajectory",
            alt,
            az,
            replay=replay,
            useResult=True,
        )

    def calcTransformationMatricesTarget(
        self,
    ) -> tuple[Angle | None, Angle | None, Any, Any, Any]:
        ha = self.obsSite.haJNowTarget
        dec = self.obsSite.decJNowTarget
        lat = self.obsSite.location.latitude
        pierside = self.obsSite.piersideTarget
        return self.geometry.calcTransformationMatrices(ha, dec, lat, pierside)

    def calcTransformationMatricesActual(
        self,
    ) -> tuple[Angle | None, Angle | None, Any, Any, Any]:
        ha = self.obsSite.haJNow
        dec = self.obsSite.decJNow
        lat = self.obsSite.location.latitude
        pierside = self.obsSite.pierside
        return self.geometry.calcTransformationMatrices(ha, dec, lat, pierside)

    def calcMountAltAzToDomeAltAz(
        self, alt: float, az: float
    ) -> tuple[Angle | None, Angle | None]:
        suc = self.obsSite.setTargetAltAz(alt=Angle(degrees=alt), az=Angle(degrees=az))
        if not suc:
            return None, None
        alt, az, _, _, _ = self.calcTransformationMatricesTarget()
        return alt, az
