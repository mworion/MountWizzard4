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
import logging

# external packages
import PySide6.QtCore
import PySide6.QtWidgets
import wakeonlan
import numpy as np

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

__all__ = ['MountDevice']


class MountDevice:
    """
    """
    CYCLE_POINTING = 500
    CYCLE_DOME = 950
    CYCLE_CLOCK = 1000
    CYCLE_MOUNT_UP = 2000
    CYCLE_SETTING = 3100
    DEFAULT_PORT = 3492
    SOCKET_TIMEOUT = 1.5

    log = logging.getLogger('MW4')

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
        self.obsSite = ObsSite(parent=self,
                               pathToData=self.pathToData,
                               verbose=self.verbose)
        self.satellite = Satellite(parent=self)
        self.geometry = Geometry(parent=self)
        self.dome = Dome(parent=self)
        self.model = Model(parent=self)

        self.mountUp = False
        self.mountUpLastStatus = False
        self.statusAlert = False
        self.statusSlew = True

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
        """
        """
        self.signals.slewFinished.emit()

    def startMountTimers(self):
        """
        """
        self.timerSetting.start(self.CYCLE_SETTING)
        self.timerPointing.start(self.CYCLE_POINTING)
        self.timerMountUp.start(self.CYCLE_MOUNT_UP)

    def stopAllMountTimers(self):
        """
        """
        self.timerSetting.stop()
        self.timerPointing.stop()
        self.timerMountUp.stop()
        self.timerDome.stop()
        self.timerClock.stop()

    def startDomeTimer(self):
        """
        """
        self.timerDome.start(self.CYCLE_DOME)

    def stopDomeTimer(self):
        """
        """
        self.timerDome.stop()

    def startMountClockTimer(self):
        """
        """
        self.timerClock.start(self.CYCLE_CLOCK)

    def stopMountClockTimer(self):
        """
        """
        self.timerClock.stop()

    def resetData(self):
        """
        """
        self.firmware = Firmware(parent=self)
        self.dome = Dome(parent=self)
        self.setting = Setting(parent=self)
        self.model = Model(parent=self)
        self.obsSite = ObsSite(parent=self,
                               pathToData=self.pathToData,
                               verbose=self.verbose)
        self.satellite = Satellite(parent=self)
        self.geometry = Geometry(parent=self)
        self.signals.pointDone.emit(self.obsSite)
        self.signals.settingDone.emit(self.setting)
        self.signals.alignDone.emit(self.model)
        self.signals.namesDone.emit(self.model)
        self.signals.firmwareDone.emit(self.firmware)
        self.signals.locationDone.emit(self.obsSite.location)

    def startupMountData(self, status: bool) -> None:
        """
        """
        if status and not self.mountUpLastStatus:
            self.mountUpLastStatus = True
            self.cycleSetting()
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
        """
        """
        with socket.socket() as client:
            client.settimeout(self.SOCKET_TIMEOUT)
            try:
                client.connect(self.host)
            except (socket.timeout, socket.error):
                self.mountUp = False
            else:
                self.mountUp = True
        return self.mountUp

    def clearCycleCheckMountUp(self):
        """
        """
        self.startupMountData(self.mountUp)
        self.signals.mountUp.emit(self.mountUp)

    def cycleCheckMountUp(self):
        """
        """
        if not self.host:
            self.signals.mountUp.emit(False)
            return

        worker = Worker(self.checkMountUp)
        worker.signals.finished.connect(self.clearCycleCheckMountUp)
        self.threadPool.start(worker)

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
        worker = Worker(self.obsSite.pollPointing)
        worker.signals.finished.connect(self.clearCyclePointing)
        self.threadPool.start(worker)

    def clearCycleSetting(self):
        """
        """
        self.signals.settingDone.emit(self.setting)

    def cycleSetting(self):
        """
        """
        worker = Worker(self.setting.pollSetting)
        worker.signals.finished.connect(self.clearCycleSetting)
        self.threadPool.start(worker)

    def clearGetAlign(self):
        """
        """
        self.signals.alignDone.emit(self.model)

    def getAlign(self):
        """
        """
        worker = Worker(self.model.pollStars)
        worker.signals.finished.connect(self.clearGetAlign)
        self.threadPool.start(worker)

    def clearGetNames(self):
        """
        """
        self.signals.namesDone.emit(self.model)

    def getNames(self):
        """
        """
        worker = Worker(self.model.pollNames)
        worker.signals.finished.connect(self.clearGetNames)
        self.threadPool.start(worker)

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
        worker = Worker(self.firmware.poll)
        worker.signals.finished.connect(self.clearGetFW)
        self.threadPool.start(worker)

    def clearGetLocation(self):
        """
        """
        self.signals.locationDone.emit(self.obsSite)

    def getLocation(self):
        """
        """
        worker = Worker(self.obsSite.getLocation)
        worker.signals.finished.connect(self.clearGetLocation)
        self.threadPool.start(worker)

    def clearCalcTLE(self):
        """
        """
        self.signals.calcTLEdone.emit(self.satellite.tleParams)

    def calcTLE(self, start):
        """
        """
        worker = Worker(self.satellite.calcTLE, start)
        worker.signals.finished.connect(self.clearCalcTLE)
        self.threadPool.start(worker)

    def clearStatTLE(self):
        """
        """
        self.signals.statTLEdone.emit(self.satellite.tleParams)

    def statTLE(self):
        """
        """
        worker = Worker(self.satellite.statTLE)
        worker.signals.finished.connect(self.clearStatTLE)
        self.threadPool.start(worker)

    def clearGetTLE(self):
        """
        """
        self.signals.getTLEdone.emit(self.satellite.tleParams)

    def getTLE(self):
        """
        """
        worker = Worker(self.satellite.getTLE)
        worker.signals.finished.connect(self.clearGetTLE)
        self.threadPool.start(worker)

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
        worker = Worker(self.dome.poll)
        worker.signals.finished.connect(self.clearDome)
        self.threadPool.start(worker)

    def cycleClock(self):
        """
        """
        worker = Worker(self.obsSite.pollSyncClock)
        self.threadPool.start(worker)

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
        self.satellite.preCalcTrajectory(replay=replay)
        return replay

    def progTrajectory(self, start, alt=None, az=None, replay=False):
        """
        """
        self.satellite.startProgTrajectory(julD=start)

        worker = Worker(self.workerProgTrajectory, alt=alt, az=az, replay=replay)
        worker.signals.result.connect(self.clearProgTrajectory)
        self.threadPool.start(worker)

    def calcTransformationMatricesTarget(self):
        """
        """
        ha = self.obsSite.haJNowTarget
        dec = self.obsSite.decJNowTarget
        lat = self.obsSite.location.latitude
        pierside = self.obsSite.piersideTarget
        return self.geometry.calcTransformationMatrices(ha=ha,
                                                        dec=dec,
                                                        lat=lat,
                                                        pierside=pierside)

    def calcTransformationMatricesActual(self):
        """
        """
        ha = self.obsSite.haJNow
        dec = self.obsSite.decJNow
        lat = self.obsSite.location.latitude
        pierside = self.obsSite.pierside
        return self.geometry.calcTransformationMatrices(ha=ha,
                                                        dec=dec,
                                                        lat=lat,
                                                        pierside=pierside)

    def calcMountAltAzToDomeAltAz(self, alt, az):
        """
        """
        suc = self.obsSite.setTargetAltAz(alt_degrees=alt, az_degrees=az)
        if not suc:
            return None, None
        alt, az, _, _, _ = self.calcTransformationMatricesTarget()
        return alt, az
