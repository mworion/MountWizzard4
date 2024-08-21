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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import socket

# external packages
import PySide6.QtCore
import PySide6.QtWidgets
import wakeonlan
import numpy as np

# local imports
from base.tpool import Worker
import mountcontrol.mount


__all__ = ['Mount',
           'MountSignals']


class MountSignals(PySide6.QtCore.QObject):
    """
    """
    pointDone = PySide6.QtCore.Signal(object)
    domeDone = PySide6.QtCore.Signal(object)
    settingDone = PySide6.QtCore.Signal(object)
    alignDone = PySide6.QtCore.Signal(object)
    namesDone = PySide6.QtCore.Signal(object)
    firmwareDone = PySide6.QtCore.Signal(object)
    locationDone = PySide6.QtCore.Signal(object)
    calcTLEdone = PySide6.QtCore.Signal(object)
    statTLEdone = PySide6.QtCore.Signal(object)
    getTLEdone = PySide6.QtCore.Signal(object)
    calcProgress = PySide6.QtCore.Signal(object)
    calcTrajectoryDone = PySide6.QtCore.Signal(object)
    mountUp = PySide6.QtCore.Signal(object)
    slewFinished = PySide6.QtCore.Signal()
    alert = PySide6.QtCore.Signal()


class Mount(mountcontrol.mount.Mount):
    """
    """
    CYCLE_POINTING = 500
    CYCLE_DOME = 950
    CYCLE_CLOCK = 1000
    CYCLE_MOUNT_UP = 2700
    CYCLE_SETTING = 3100
    SOCKET_TIMEOUT = 3.5

    def __init__(self, host=None, MAC=None,
                 threadPool=None, pathToData=None, verbose=None):

        super().__init__(host=host, MAC=MAC,
                         pathToData=pathToData, verbose=verbose)

        self.threadPool = threadPool
        self.mountUp = False
        self._waitTime = 0
        self._waitTimeFlip = 0
        self.statusAlert = False
        self.statusSlew = True
        self.signals = MountSignals()

        self.timerPointing = PySide6.QtCore.QTimer()
        self.timerPointing.setSingleShot(False)
        self.timerPointing.timeout.connect(self.cyclePointing)
        self.timerDome = PySide6.QtCore.QTimer()
        self.timerDome.setSingleShot(False)
        self.timerDome.timeout.connect(self.cycleDome)
        self.timerClock = PySide6.QtCore.QTimer()
        self.timerClock.setSingleShot(False)
        self.timerClock.timeout.connect(self.cycleClock)
        self.timerSetting = PySide6.QtCore.QTimer()
        self.timerSetting.setSingleShot(False)
        self.timerSetting.timeout.connect(self.cycleSetting)
        self.timerMountUp = PySide6.QtCore.QTimer()
        self.timerMountUp.setSingleShot(False)
        self.timerMountUp.timeout.connect(self.cycleCheckMountUp)
        self.settlingWait = PySide6.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitAfterSettlingAndEmit)

    @property
    def waitTimeFlip(self):
        return self._waitTimeFlip / 1000

    @waitTimeFlip.setter
    def waitTimeFlip(self, value):
        self._waitTimeFlip = value * 1000

    def waitAfterSettlingAndEmit(self):
        """
        """
        self.signals.slewFinished.emit()

    def startTimers(self):
        """
        """
        self.timerSetting.start(self.CYCLE_SETTING)
        self.timerPointing.start(self.CYCLE_POINTING)
        self.timerMountUp.start(self.CYCLE_MOUNT_UP)

    def stopTimers(self):
        """
        """
        self.timerPointing.stop()
        self.timerDome.stop()
        self.timerClock.stop()
        self.timerSetting.stop()
        self.timerMountUp.stop()

    def startDomeTimer(self):
        """
        """
        self.timerDome.start(self.CYCLE_DOME)

    def stopDomeTimer(self):
        """
        """
        self.timerDome.stop()

    def startClockTimer(self):
        """
        """
        self.timerClock.start(self.CYCLE_CLOCK)

    def stopClockTimer(self):
        """
        """
        self.timerClock.stop()

    def resetData(self):
        """
        """
        super().resetData()
        self.signals.pointDone.emit(self.obsSite)
        self.signals.settingDone.emit(self.setting)
        self.signals.alignDone.emit(self.model)
        self.signals.namesDone.emit(self.model)
        self.signals.firmwareDone.emit(self.firmware)
        self.signals.locationDone.emit(self.obsSite.location)

    def checkMountUp(self):
        """
        """
        with socket.socket() as client:
            client.settimeout(self.SOCKET_TIMEOUT)
            try:
                client.connect(self.host)
            except Exception:
                self.mountUp = False
            else:
                self.mountUp = True

            return self.mountUp

    def clearCycleCheckMountUp(self):
        """
        """
        self.signals.mountUp.emit(self.mountUp)

    def cycleCheckMountUp(self):
        """
        """
        if not self.host:
            self.signals.mountUp.emit(False)
            return False

        worker = Worker(self.checkMountUp)
        worker.signals.finished.connect(self.clearCycleCheckMountUp)
        self.threadPool.start(worker)
        return True

    def clearCyclePointing(self):
        """
        """
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

    def cyclePointing(self):
        """
        :return: success
        """
        if not self.mountUp:
            self.signals.pointDone.emit(self.obsSite)
            return False

        worker = Worker(self.obsSite.pollPointing)
        worker.signals.finished.connect(self.clearCyclePointing)
        self.threadPool.start(worker)
        return True

    def clearCycleSetting(self):
        """
        """
        self.signals.settingDone.emit(self.setting)

    def cycleSetting(self):
        """
        """
        if not self.mountUp:
            self.signals.settingDone.emit(self.setting)
            return False

        worker = Worker(self.setting.pollSetting)
        worker.signals.finished.connect(self.clearCycleSetting)
        self.threadPool.start(worker)
        return True

    def clearGetAlign(self):
        """
        """
        self.signals.alignDone.emit(self.model)

    def getAlign(self):
        """
        """
        if not self.mountUp:
            self.signals.alignDone.emit(self.model)
            return False

        worker = Worker(self.model.pollStars)
        worker.signals.finished.connect(self.clearGetAlign)
        self.threadPool.start(worker)
        return True

    def clearGetNames(self):
        """
        """
        self.signals.namesDone.emit(self.model)

    def getNames(self):
        """
        """
        if not self.mountUp:
            self.signals.namesDone.emit(self.model)
            return False

        worker = Worker(self.model.pollNames)
        worker.signals.finished.connect(self.clearGetNames)
        self.threadPool.start(worker)
        return True

    def clearGetFW(self):
        """
        """
        self.log.header('-' * 100)
        self.log.header(f'10micron product : {self.firmware.product}')
        self.log.header(f'10micron firmware: {self.firmware.vString}')
        self.log.header(f'10micron host    : {self.host}')
        self.log.header('-' * 100)
        self.geometry.initializeGeometry(self.firmware.product)
        self.signals.firmwareDone.emit(self.firmware)

    def getFW(self):
        """
        """
        if not self.mountUp:
            self.signals.firmwareDone.emit(self.firmware)
            return False

        worker = Worker(self.firmware.poll)
        worker.signals.finished.connect(self.clearGetFW)
        self.threadPool.start(worker)
        return True

    def clearGetLocation(self):
        """
        """
        self.signals.locationDone.emit(self.obsSite)

    def getLocation(self):
        """
        """
        if not self.mountUp:
            self.signals.locationDone.emit(self.obsSite)
            return False

        worker = Worker(self.obsSite.getLocation)
        worker.signals.finished.connect(self.clearGetLocation)
        self.threadPool.start(worker)
        return True

    def clearCalcTLE(self):
        """
        """
        self.signals.calcTLEdone.emit(self.satellite.tleParams)

    def calcTLE(self, start):
        """
        """
        if not self.mountUp:
            self.signals.calcTLEdone.emit(self.satellite.tleParams)
            return False

        worker = Worker(self.satellite.calcTLE, start)
        worker.signals.finished.connect(self.clearCalcTLE)
        self.threadPool.start(worker)
        return True

    def clearStatTLE(self):
        """
        """
        self.signals.statTLEdone.emit(self.satellite.tleParams)

    def statTLE(self):
        """
        """
        if not self.mountUp:
            self.signals.statTLEdone.emit(self.satellite.tleParams)
            return False

        worker = Worker(self.satellite.statTLE)
        worker.signals.finished.connect(self.clearStatTLE)
        self.threadPool.start(worker)
        return True

    def clearGetTLE(self):
        """
        """
        self.signals.getTLEdone.emit(self.satellite.tleParams)

    def getTLE(self):
        """
        """
        if not self.mountUp:
            self.signals.getTLEdone.emit(self.satellite.tleParams)
            return False

        worker = Worker(self.satellite.getTLE)
        worker.signals.finished.connect(self.clearGetTLE)
        self.threadPool.start(worker)
        return True

    def bootMount(self, bAddress='', bPort=0):
        """
        """
        t = f'MAC: [{self.MAC}], broadcast address: [{bAddress}], port: [{bPort}]'
        self.log.debug(t)
        if self.MAC is None:
            return False
        if bAddress and bPort:
            wakeonlan.send_magic_packet(self.MAC,
                                        ip_address=bAddress,
                                        port=bPort)
        else:
            wakeonlan.send_magic_packet(self.MAC)
        return True

    def shutdown(self):
        """
        """
        suc = self.obsSite.shutdown()
        if suc:
            self.mountUp = False
        return suc

    def clearDome(self):
        """
        """
        self.signals.domeDone.emit(self.dome)

    def cycleDome(self):
        """
        """
        if not self.mountUp:
            self.signals.domeDone.emit(self.dome)
            return False

        worker = Worker(self.dome.poll)
        worker.signals.finished.connect(self.clearDome)
        self.threadPool.start(worker)
        return True

    def cycleClock(self):
        """
        :return: success
        """
        if not self.mountUp:
            return False

        worker = Worker(self.obsSite.pollSyncClock)
        self.threadPool.start(worker)
        return True

    def clearProgTrajectory(self):
        """
        """
        self.signals.calcTrajectoryDone.emit(self.satellite.trajectoryParams)

    def workerProgTrajectory(self, alt=None, az=None, replay=False):
        """
        """
        factor = int(len(alt) / 32)
        if factor < 1:
            factor = 1
        altP = np.array_split(alt, factor)
        azP = np.array_split(az, factor)
        chunks = len(altP)

        for i, (altitude, azimuth) in enumerate(zip(altP, azP)):
            self.satellite.addTrajectoryPoint(alt=altitude, az=azimuth)
            self.signals.calcProgress.emit(min((i + 1) / chunks * 100, 100))
        self.signals.calcProgress.emit(100)
        self.satellite.preCalcTrajectory(replay = replay)
        return replay

    def progTrajectory(self, start, alt=None, az=None, replay=False):
        """
        """
        if not self.mountUp:
            return

        self.satellite.startProgTrajectory(julD=start)

        worker = Worker(self.workerProgTrajectory, alt=alt, az=az, replay=replay)
        worker.signals.result.connect(self.clearProgTrajectory)
        self.threadPool.start(worker)
