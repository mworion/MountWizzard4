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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import socket

# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import wakeonlan
import numpy as np

# local imports
from base.tpool import Worker
import mountcontrol.mount


__all__ = ['Mount',
           'MountSignals',
           ]


class MountSignals(PyQt5.QtCore.QObject):
    """
    The MountSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['MountSignals']

    pointDone = PyQt5.QtCore.pyqtSignal(object)
    domeDone = PyQt5.QtCore.pyqtSignal(object)
    settingDone = PyQt5.QtCore.pyqtSignal(object)
    alignDone = PyQt5.QtCore.pyqtSignal(object)
    namesDone = PyQt5.QtCore.pyqtSignal(object)
    firmwareDone = PyQt5.QtCore.pyqtSignal(object)
    locationDone = PyQt5.QtCore.pyqtSignal(object)
    calcTLEdone = PyQt5.QtCore.pyqtSignal(object)
    statTLEdone = PyQt5.QtCore.pyqtSignal(object)
    getTLEdone = PyQt5.QtCore.pyqtSignal(object)
    trajectoryProgress = PyQt5.QtCore.pyqtSignal(object)
    calcTrajectoryDone = PyQt5.QtCore.pyqtSignal(object)
    mountUp = PyQt5.QtCore.pyqtSignal(object)
    slewFinished = PyQt5.QtCore.pyqtSignal()
    alert = PyQt5.QtCore.pyqtSignal()


class Mount(mountcontrol.mount.Mount):
    """
    The Mount class is the main interface for interacting with the mount computer.
    The user could:
        setup / change the interface to the mount
        start / stop cyclic tasks to poll data from mount
        send and get data from mount
        has signals for interfacing to external GUI's for data updates

        >>> settings = Mount(
        >>>                     host=host,
        >>>                     MAC=MAC,
        >>>                     threadPool=threadPool,
        >>>                     pathToData=pathToData,
        >>>                     expire=expire,
        >>>                     verbose=verbose,
        >>>                 )

    """

    CYCLE_POINTING = 500
    CYCLE_DOME = 950
    CYCLE_CLOCK = 1000
    CYCLE_MOUNT_UP = 2700
    CYCLE_SETTING = 3100

    # set timeout
    SOCKET_TIMEOUT = 3.5

    def __init__(self, host=None, MAC=None,
                 threadPool=None, pathToData=None, verbose=None):

        super().__init__(host=host, MAC=MAC,
                         pathToData=pathToData, verbose=verbose)

        self.threadPool = threadPool
        self.mountUp = False
        self._settlingTime = 0
        self.statusAlert = False
        self.statusSlew = True
        self.signals = MountSignals()

        self.timerPointing = PyQt5.QtCore.QTimer()
        self.timerPointing.setSingleShot(False)
        self.timerPointing.timeout.connect(self.cyclePointing)
        self.timerDome = PyQt5.QtCore.QTimer()
        self.timerDome.setSingleShot(False)
        self.timerDome.timeout.connect(self.cycleDome)
        self.timerClock = PyQt5.QtCore.QTimer()
        self.timerClock.setSingleShot(False)
        self.timerClock.timeout.connect(self.cycleClock)
        self.timerSetting = PyQt5.QtCore.QTimer()
        self.timerSetting.setSingleShot(False)
        self.timerSetting.timeout.connect(self.cycleSetting)
        self.timerMountUp = PyQt5.QtCore.QTimer()
        self.timerMountUp.setSingleShot(False)
        self.timerMountUp.timeout.connect(self.cycleCheckMountUp)
        self.settlingWait = PyQt5.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitSettlingAndEmit)

    @property
    def settlingTime(self):
        return self._settlingTime / 1000

    @settlingTime.setter
    def settlingTime(self, value):
        self._settlingTime = value * 1000

    def waitSettlingAndEmit(self):
        """
        :return: true for test purpose
        """
        self.signals.slewFinished.emit()
        return True

    def startTimers(self):
        """
        :return: true for test purpose
        """
        self.timerSetting.start(self.CYCLE_SETTING)
        self.timerPointing.start(self.CYCLE_POINTING)
        self.timerMountUp.start(self.CYCLE_MOUNT_UP)
        return True

    def stopTimers(self):
        """
        :return: true for test purpose
        """
        self.timerPointing.stop()
        self.timerDome.stop()
        self.timerClock.stop()
        self.timerSetting.stop()
        self.timerMountUp.stop()
        return True

    def startDomeTimer(self):
        """
        :return:
        """
        self.timerDome.start(self.CYCLE_DOME)
        return True

    def stopDomeTimer(self):
        """
        :return:
        """
        self.timerDome.stop()
        return True

    def startClockTimer(self):
        """
        :return:
        """
        self.timerClock.start(self.CYCLE_CLOCK)
        return True

    def stopClockTimer(self):
        """
        :return:
        """
        self.timerClock.stop()
        return True

    def resetData(self):
        """
        :return: true for test purpose
        """
        super().resetData()
        self.signals.pointDone.emit(self.obsSite)
        self.signals.settingDone.emit(self.setting)
        self.signals.alignDone.emit(self.model)
        self.signals.namesDone.emit(self.model)
        self.signals.firmwareDone.emit(self.firmware)
        self.signals.locationDone.emit(self.obsSite.location)
        return True

    def checkMountUp(self):
        """
        :return: true for test purpose
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

    def errorCycleCheckMountUp(self, e):
        """
        :return: true for test purpose
        """
        self.log.info(f'Cycle error: {e}')
        return True

    def clearCycleCheckMountUp(self):
        """
        :return: true for test purpose
        """
        self.signals.mountUp.emit(self.mountUp)
        return True

    def cycleCheckMountUp(self):
        """
        :return: success
        """
        if not self.host:
            self.signals.mountUp.emit(False)
            return False

        worker = Worker(self.checkMountUp)
        worker.signals.finished.connect(self.clearCycleCheckMountUp)
        worker.signals.error.connect(self.errorCycleCheckMountUp)
        self.threadPool.start(worker)
        return True

    def errorCyclePointing(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearCyclePointing(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should
        not run twice for the same data at the same time.

        :return: true for test purpose
        """
        if self.obsSite.status in [1, 98, 99]:
            if not self.statusAlert:
                self.signals.alert.emit()
            self.statusAlert = True
        else:
            self.statusAlert = False

        if self.obsSite.status not in [2, 6]:
            if not self.statusSlew:
                self.settlingWait.start(self._settlingTime)
            self.statusSlew = True
        else:
            self.statusSlew = False

        self.signals.pointDone.emit(self.obsSite)
        return True

    def cyclePointing(self):
        """
        :return: success
        """
        if not self.mountUp:
            self.signals.pointDone.emit(self.obsSite)
            return False

        worker = Worker(self.obsSite.pollPointing)
        worker.signals.finished.connect(self.clearCyclePointing)
        worker.signals.error.connect(self.errorCyclePointing)
        self.threadPool.start(worker)
        return True

    def errorCycleSetting(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearCycleSetting(self):
        """
        :return: true for test purpose
        """
        self.signals.settingDone.emit(self.setting)
        return True

    def cycleSetting(self):
        """
        cycleSet prepares the worker thread and the signals for getting the
        settings data.

        :return: success
        """
        if not self.mountUp:
            self.signals.settingDone.emit(self.setting)
            return False

        worker = Worker(self.setting.pollSetting)
        worker.signals.finished.connect(self.clearCycleSetting)
        worker.signals.error.connect(self.errorCycleSetting)
        self.threadPool.start(worker)
        return True

    def errorGetAlign(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearGetAlign(self):
        """
        :return: true for test purpose
        """
        self.signals.alignDone.emit(self.model)
        return True

    def getAlign(self):
        """
        getAlign prepares the worker thread and the signals for getting the
        alignment model data.

        :return: success
        """
        if not self.mountUp:
            self.signals.alignDone.emit(self.model)
            return False

        worker = Worker(self.model.pollStars)
        worker.signals.finished.connect(self.clearGetAlign)
        worker.signals.error.connect(self.errorGetAlign)
        self.threadPool.start(worker)
        return True

    def errorGetNames(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearGetNames(self):
        """
        :return: true for test purpose
        """
        self.signals.namesDone.emit(self.model)
        return True

    def getNames(self):
        """
        getNames prepares the worker thread and the signals for getting the
        alignment model names.

        :return: success
        """
        if not self.mountUp:
            self.signals.namesDone.emit(self.model)
            return False

        worker = Worker(self.model.pollNames)
        worker.signals.finished.connect(self.clearGetNames)
        worker.signals.error.connect(self.errorGetNames)
        self.threadPool.start(worker)
        return True

    def errorGetFW(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearGetFW(self):
        """
        :return: true for test purpose
        """
        self.log.header('-' * 100)
        self.log.header(f'10micron product : {self.firmware.product}')
        self.log.header(f'10micron firmware: {self.firmware.vString}')
        self.log.header(f'10micron host    : {self.host}')
        self.log.header('-' * 100)
        self.geometry.initializeGeometry(self.firmware.product)
        self.signals.firmwareDone.emit(self.firmware)
        return True

    def getFW(self):
        """
        :return: success
        """
        if not self.mountUp:
            self.signals.firmwareDone.emit(self.firmware)
            return False

        worker = Worker(self.firmware.poll)
        worker.signals.finished.connect(self.clearGetFW)
        worker.signals.error.connect(self.errorGetFW)
        self.threadPool.start(worker)
        return True

    def errorGetLocation(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearGetLocation(self):
        """
        :return: true for test purpose
        """
        self.signals.locationDone.emit(self.obsSite)
        return True

    def getLocation(self):
        """
        :return: success
        """
        if not self.mountUp:
            self.signals.locationDone.emit(self.obsSite)
            return False

        worker = Worker(self.obsSite.getLocation)
        worker.signals.finished.connect(self.clearGetLocation)
        worker.signals.error.connect(self.errorGetLocation)
        self.threadPool.start(worker)
        return True

    def errorCalcTLE(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearCalcTLE(self):
        """
        :return: true for test purpose
        """
        self.signals.calcTLEdone.emit(self.satellite.tleParams)
        return True

    def calcTLE(self, start):
        """
        :param start:
        :return:
        """
        if not self.mountUp:
            self.signals.calcTLEdone.emit(self.satellite.tleParams)
            return False

        worker = Worker(self.satellite.calcTLE, start)
        worker.signals.finished.connect(self.clearCalcTLE)
        worker.signals.error.connect(self.errorCalcTLE)
        self.threadPool.start(worker)
        return True

    def errorStatTLE(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearStatTLE(self):
        """
        :return: true for test purpose
        """
        self.signals.statTLEdone.emit(self.satellite.tleParams)
        return True

    def statTLE(self):
        """
        :return: success
        """
        if not self.mountUp:
            self.signals.statTLEdone.emit(self.satellite.tleParams)
            return False

        worker = Worker(self.satellite.statTLE)
        worker.signals.finished.connect(self.clearStatTLE)
        worker.signals.error.connect(self.errorStatTLE)
        self.threadPool.start(worker)
        return True

    def errorGetTLE(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearGetTLE(self):
        """
        :return: true for test purpose
        """
        self.signals.getTLEdone.emit(self.satellite.tleParams)
        return True

    def getTLE(self):
        """
        :return: success
        """
        if not self.mountUp:
            self.signals.getTLEdone.emit(self.satellite.tleParams)
            return False

        worker = Worker(self.satellite.getTLE)
        worker.signals.finished.connect(self.clearGetTLE)
        worker.signals.error.connect(self.errorGetTLE)
        self.threadPool.start(worker)
        return True

    def bootMount(self, bAddress='', bPort=0):
        """
        :param bAddress:
        :param bPort:
        :return:    True if success
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
        :return:
        """
        suc = self.obsSite.shutdown()
        if suc:
            self.mountUp = False

        return suc

    def errorDome(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearDome(self):
        """
        :return: true for test purpose
        """
        self.signals.domeDone.emit(self.dome)
        return True

    def cycleDome(self):
        """
        :return: success
        """
        if not self.mountUp:
            self.signals.domeDone.emit(self.dome)
            return False

        worker = Worker(self.dome.poll)
        worker.signals.finished.connect(self.clearDome)
        worker.signals.error.connect(self.errorDome)
        self.threadPool.start(worker)
        return True

    def errorClock(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    @staticmethod
    def clearClock():
        """
        :return: true for test purpose
        """
        return True

    def cycleClock(self):
        """
        :return: success
        """
        if not self.mountUp:
            return False

        worker = Worker(self.obsSite.pollSyncClock)
        worker.signals.finished.connect(self.clearClock)
        self.threadPool.start(worker)
        return True

    def errorCalcTrajectory(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearCalcTrajectory(self):
        """
        :return: true for test purpose
        """
        self.signals.calcTrajectoryDone.emit(self.satellite.trajectoryParams)
        return True

    def calcTrajectory(self, replay=False):
        """
        :return: success
        """
        if not self.mountUp:
            self.signals.calcTrajectoryDone.emit(self.satellite.trajectoryParams)
            return False

        worker = Worker(self.satellite.calcTrajectory, replay=replay)
        worker.signals.finished.connect(self.clearCalcTrajectory)
        worker.signals.error.connect(self.errorCalcTrajectory)
        self.threadPool.start(worker)
        return True

    def errorProgTrajectory(self, e):
        """
        :return: true for test purpose
        """
        self.log.warning(f'Cycle error: {e}')
        return True

    def clearProgTrajectory(self, sim=False):
        """
        :param sim:
        :return: true for test purpose
        """
        self.calcTrajectory(replay=sim)
        return True

    def workerProgTrajectory(self, alt=[], az=[], sim=False):
        """
        :param alt:
        :param az:
        :param sim:
        :return:
        """
        factor = int(len(alt) / 32)
        if factor < 1:
            factor = 1
        altP = np.array_split(alt, factor)
        azP = np.array_split(az, factor)
        chunks = len(altP)

        for i, (altitude, azimuth) in enumerate(zip(altP, azP)):
            self.satellite.progTrajectory(alt=altitude, az=azimuth)
            self.signals.trajectoryProgress.emit(min((i + 1) / chunks * 100, 100))
        self.signals.trajectoryProgress.emit(100)
        return sim

    def progTrajectory(self, start, alt=[], az=[], sim=False):
        """
        :param start:
        :param alt:
        :param az:
        :param sim:
        :return:
        """
        if not self.mountUp:
            return False

        self.satellite.startProgTrajectory(julD=start)

        worker = Worker(self.workerProgTrajectory, alt=alt, az=az, sim=sim)
        worker.signals.result.connect(self.clearProgTrajectory)
        worker.signals.error.connect(self.errorProgTrajectory)
        self.threadPool.start(worker)
        return True
