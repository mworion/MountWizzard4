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
import wakeonlan
from dataclasses import dataclass, field
from mw4.base.tpool import Worker, startWorker
from mw4.mountcontrol.firmware import Firmware
from mw4.mountcontrol.geometry import Geometry
from mw4.mountcontrol.model import Model
from mw4.mountcontrol.mountSignals import MountSignals
from mw4.mountcontrol.mountTime import MountTime
from mw4.mountcontrol.obsSite import MountStatus, ObsSite
from mw4.mountcontrol.satellite import Satellite
from mw4.mountcontrol.setting import Setting
from pathlib import Path
from PySide6.QtCore import QMutex, QObject, QTimer
from skyfield.api import Angle
from typing import Any, Final


@dataclass
class DeviceConfigMount:
    deviceName: str = field(default="10micron")
    hostAddress: str = field(default="127.0.0.1")
    port: int = field(default=3492)
    MAC: str = field(default="00:00:00:00:00:00")
    syncTimeNone: bool = field(default=True)
    syncTimeCont: bool = field(default=False)
    syncTimeNotTrack: bool = field(default=False)
    wolAutomatic: bool = field(default=False)
    wolAddress: str = field(default="255.255.255.255")
    wolPort: int = field(default=9)


class MountDevice(QObject):
    CYCLE_POINTING: Final[int] = 500
    CYCLE_DOME: Final[int] = 950
    CYCLE_SETTING: Final[int] = 3100
    SOCKET_TIMEOUT: Final[float] = 1.0
    ALERT_STATUS_CODES: Final[frozenset[MountStatus]] = frozenset(
        {MountStatus.STOPPED, MountStatus.UNKNOWN, MountStatus.ERROR}
    )
    log = logging.getLogger("MW4")

    def __init__(
        self,
        app: Any,
        verbose: bool = False,
    ) -> None:
        super().__init__()
        self._waitTime = 0
        self._waitTimeFlip = 0
        self.app = app
        self.config = DeviceConfigMount()
        self.run: dict[str, Any] = {"10micron": self}
        self.framework: str = "10micron"
        self.threadPool = app.threadPool
        self.pathToData: Path = app.mwGlob["dataDir"]
        self.verbose: bool = verbose
        self.loggingTrace: bool = False
        self.mountIsUp: bool = False
        self.signals = MountSignals()
        self.firmware = Firmware(self)
        self.setting = Setting(self)
        self.obsSite = ObsSite(self, verbose=self.verbose)
        self.satellite = Satellite(self)
        self.geometry = Geometry(self)
        self.model = Model(self)
        self.mountTime = MountTime(self)

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
        self.mutexCycleSetting = QMutex()
        self.mutexCyclePointing = QMutex()
        self.mutexGetTLE = QMutex()
        self.mutexCalcTLE = QMutex()
        self.mountIsUp: bool = False
        self.statusAlert: bool = False
        self.statusSlew: bool = False

        self.settlingWait = QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitAfterSettlingAndEmit)
        self.signals.mountIsUp.connect(self.startupMountData)
        self.app.timeMgr.update0_5s.connect(self.cyclePointing)
        self.app.timeMgr.update1s.connect(self.cycleSetting)
        self.app.timeMgr.update1s.connect(self.collectData)
        self.app.timeMgr.start3s.connect(self.resetAfterStart)
        self.data: dict = {}
        self.raRef: float = 0.0
        self.decRef: float = 0.0

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
        self.data["timeDiff"] = self.mountTime.timeDiff * 1000
        self.data["rtt"] = self.mountTime.rtt * 1000

    def waitAfterSettlingAndEmit(self) -> None:
        self.signals.slewed.emit()

    def stopAllMountTimers(self) -> None:
        self.settlingWait.stop()

    def startupMountData(self, status) -> None:
        if status and not self.mountIsUp:
            self.mountIsUp = True
            self.obsSite.setHighPrecision()
            self.getFW()
            self.getLocation()
            self.app.refreshModel.emit()
            self.app.refreshName.emit()
            self.getTLE()
            self.signals.deviceConnected.emit("mount")
        elif not status and self.mountIsUp:
            self.signals.deviceDisconnected.emit("mount")
            self.mountIsUp = False

    def resultCyclePointing(self, result: bool) -> None:
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

    def cyclePointing(self) -> None:
        self.workerCyclePointing = startWorker(
            self.threadPool,
            self.obsSite.pollPointing,
            self.resultCyclePointing,
            guard=lambda: self.mountIsUp,
        )

    def resultCycleSetting(self, result: bool) -> None:
        if result:
            self.signals.settingDone.emit(self.setting)

    def cycleSetting(self) -> None:
        self.workerCycleSetting = startWorker(
            self.threadPool,
            self.setting.pollSetting,
            self.resultCycleSetting,
            guard=lambda: self.mountIsUp,
        )

    def resultGetModel(self) -> None:
        self.signals.getModelDone.emit(self.model)

    def getModel(self) -> None:
        self.workerGetModel = startWorker(
            self.threadPool,
            self.model.pollStars,
            self.resultGetModel,
            guard=lambda: self.mountIsUp,
        )

    def resultGetNames(self) -> None:
        self.signals.namesDone.emit(self.model)

    def getNames(self) -> None:
        self.workerGetNames = startWorker(
            self.threadPool,
            self.model.pollNames,
            self.resultGetNames,
            guard=lambda: self.mountIsUp,
        )

    def resultGetFW(self) -> None:
        self.log.info(f"Product : {self.firmware.product}")
        self.log.info(f"Firmware: {self.firmware.vString}")
        self.log.info(f"Hardware: {self.firmware.hardware}")
        self.geometry.initializeGeometry(self.firmware.product)
        self.signals.firmwareDone.emit(self.firmware)

    def getFW(self) -> None:
        self.workerGetFW = startWorker(
            self.threadPool,
            self.firmware.poll,
            self.resultGetFW,
            guard=lambda: self.mountIsUp,
        )

    def resultGetLocation(self) -> None:
        self.signals.locationDone.emit(self.obsSite)

    def getLocation(self) -> None:
        self.workerGetLocation = startWorker(
            self.threadPool,
            self.obsSite.getLocation,
            self.resultGetLocation,
            guard=lambda: self.mountIsUp,
        )

    def resultCalcTLE(self) -> None:
        self.signals.calcTLEdone.emit(self.satellite.tleParams)

    def calcTLE(self, start: float) -> None:
        self.workerCalcTLE = startWorker(
            self.threadPool,
            self.satellite.calcTLE,
            self.resultCalcTLE,
            start,
            guard=lambda: self.mountIsUp,
        )

    def resultStatTLE(self) -> None:
        self.signals.statTLEdone.emit(self.satellite.tleParams)

    def statTLE(self) -> None:
        self.workerStatTLE = startWorker(
            self.threadPool,
            self.satellite.statTLE,
            self.resultStatTLE,
            guard=lambda: self.mountIsUp,
        )

    def resultGetTLE(self) -> None:
        self.signals.getTLEdone.emit(self.satellite.tleParams)

    def getTLE(self) -> None:
        self.workerGetTLE = startWorker(
            self.threadPool,
            self.satellite.getTLE,
            self.resultGetTLE,
            guard=lambda: self.mountIsUp,
        )

    def bootMount(self) -> bool:
        t = f"MAC: [{self.config.MAC}], [{self.config.wolAddress}]:[{self.config.wolPort}]"
        self.log.debug(t)
        if self.config.MAC is None:
            return False
        kwargs: dict[str, Any] = {}
        if self.config.wolAddress:
            kwargs["ip_address"] = self.config.wolAddress
        if self.config.wolPort:
            kwargs["port"] = self.config.wolPort
        try:
            wakeonlan.wake(self.config.MAC, **kwargs)
        except (OSError, ValueError) as e:
            self.log.warning(f"Boot mount failed: {e}")
            return False
        return True

    def shutdown(self) -> bool:
        suc = self.obsSite.shutdown()
        if suc:
            self.mountIsUp = False
        return suc

    def resultProgTrajectory(self) -> None:
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
        self.workerTrajectory = startWorker(
            self.threadPool,
            self.runnerProgTrajectory,
            self.resultProgTrajectory,
            alt,
            az,
            replay=replay,
            guard=lambda: self.mountIsUp,
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
