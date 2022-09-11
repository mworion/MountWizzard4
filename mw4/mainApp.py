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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import os
import sys
from queue import Queue

# external packages
from base.packageConfig import checkAutomation
if checkAutomation():
    from logic.automation.automateWindows import AutomateWindows

from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool, QTimer
from skyfield.api import wgs84
from importlib_metadata import version

# local import
from base.loggerMW import setCustomLoggingLevel
from mountcontrol import qtmount
from gui.mainWindow.mainW import MainWindow
from logic.powerswitch.kmRelay import KMRelay
from logic.modeldata.buildpoints import DataPoint
from logic.modeldata.hipparcos import Hipparcos
from logic.dome.dome import Dome
from logic.camera.camera import Camera
from logic.filter.filter import Filter
from logic.focuser.focuser import Focuser
from logic.environment.sensorWeather import SensorWeather
from logic.environment.skymeter import Skymeter
from logic.environment.onlineWeather import OnlineWeather
from logic.environment.seeingWeather import SeeingWeather
from logic.environment.directWeather import DirectWeather
from logic.environment.weatherUPB import WeatherUPB
from logic.cover.cover import Cover
from logic.telescope.telescope import Telescope
from logic.powerswitch.pegasusUPB import PegasusUPB
from logic.measure.measure import MeasureData
from logic.remote.remote import Remote
from logic.plateSolve.plateSolve import PlateSolve
from logic.profiles.profile import loadProfile


class MountWizzard4(QObject):
    """
    MountWizzard4 class is the main class for the application. it loads all
    windows and classes needed to fulfil the work of mountwizzard. any gui work
    should be handled through the window classes. main class is for setup,
    config, start, persist and shutdown the application.
    """

    __all__ = ['MountWizzard4']
    __version__ = version('mountwizzard4')
    log = logging.getLogger(__name__)

    msg = pyqtSignal(object, object, object, object)
    messageQueue = Queue()
    redrawHemisphere = pyqtSignal()
    redrawHorizon = pyqtSignal()
    updatePointMarker = pyqtSignal()
    drawBuildPoints = pyqtSignal()
    operationRunning = pyqtSignal(object)
    playSound = pyqtSignal(object)
    buildPointsChanged = pyqtSignal()
    drawHorizonPoints = pyqtSignal()
    updateDomeSettings = pyqtSignal()
    sendSatelliteData = pyqtSignal()
    showImage = pyqtSignal(str)
    showAnalyse = pyqtSignal(str)
    remoteCommand = pyqtSignal(str)
    colorChange = pyqtSignal()
    hostChanged = pyqtSignal()
    virtualStop = pyqtSignal()
    mountOff = pyqtSignal()
    mountOn = pyqtSignal()
    gameABXY = pyqtSignal(object)
    gamePMH = pyqtSignal(object)
    gameDirection = pyqtSignal(object)
    game_sL = pyqtSignal(object, object)
    game_sR = pyqtSignal(object, object)

    update0_1s = pyqtSignal()
    update1s = pyqtSignal()
    update3s = pyqtSignal()
    update10s = pyqtSignal()
    update30s = pyqtSignal()
    update60s = pyqtSignal()
    update3m = pyqtSignal()
    update10m = pyqtSignal()
    update30m = pyqtSignal()
    update1h = pyqtSignal()
    start1s = pyqtSignal()
    start3s = pyqtSignal()
    start5s = pyqtSignal()
    start10s = pyqtSignal()
    start30s = pyqtSignal()

    def __init__(self, mwGlob=None, application=None):
        super().__init__()

        self.application = application
        self.expireData = False
        self.mountUp = False
        self.mwGlob = mwGlob
        self.timerCounter = 0
        self.statusOperationRunning = 0
        self.mainW = None
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(30)
        self.msg.connect(self.writeMessageQueue)
        self.config = loadProfile(configDir=self.mwGlob['configDir'])
        self.deviceStat = {
            'dome': None,
            'mount': None,
            'camera': None,
            'plateSolve': None,
            'refraction': None,
            'sensorWeather': None,
            'directWeather': None,
            'onlineWeather': None,
            'seeingWeather': None,
            'powerWeather': None,
            'skymeter': None,
            'cover': None,
            'telescope': None,
            'power': None,
            'remote': None,
            'relay': None,
            'measure': None,
        }
        profile = self.config.get('profileName', '-')
        workDir = self.mwGlob['workDir']
        self.messageQueue.put((1, 'System', 'Lifecycle', 'MountWizzard4 started...'))
        self.messageQueue.put((1, 'System', 'Workdir', f'{workDir}'))
        self.messageQueue.put((1, 'System', 'Profile', f'Base: {profile}'))
        # initialize commands to mount
        pathToData = self.mwGlob['dataDir']
        self.mount = qtmount.Mount(host='localhost',
                                   MAC='00.c0.08.87.35.db',
                                   threadPool=self.threadPool,
                                   pathToData=pathToData,
                                   verbose=False,
                                   )
        # setting location to last know config
        topo = self.initConfig()
        self.mount.obsSite.location = topo
        self.mount.signals.mountUp.connect(self.loadMountData)
        self.ephemeris = self.mount.obsSite.loader('de440_mw4.bsp')
        self.relay = KMRelay()
        self.sensorWeather = SensorWeather(self)
        self.onlineWeather = OnlineWeather(self)
        self.seeingWeather = SeeingWeather(self)
        self.directWeather = DirectWeather(self)
        self.powerWeather = WeatherUPB(self)
        self.cover = Cover(self)
        self.dome = Dome(self)
        self.camera = Camera(self)
        self.filter = Filter(self)
        self.focuser = Focuser(self)
        self.telescope = Telescope(self)
        self.skymeter = Skymeter(self)
        self.power = PegasusUPB(self)
        self.data = DataPoint(self)
        self.loadHorizonData()
        self.hipparcos = Hipparcos(self)
        self.measure = MeasureData(self)
        self.remote = Remote(self)
        self.plateSolve = PlateSolve(self)
        self.automation = self.checkAndSetAutomation()

        self.uiWindows = {}
        self.mainW = MainWindow(self)

        self.mount.startTimers()
        self.timer0_1s = QTimer()
        self.timer0_1s.setSingleShot(False)
        self.timer0_1s.timeout.connect(self.sendUpdate)
        self.timer0_1s.start(100)
        self.application.aboutToQuit.connect(self.aboutToQuit)
        self.operationRunning.connect(self.storeStatusOperationRunning)

        if os.path.isfile(self.mwGlob["workDir"] + '/test.run'):
            self.update3s.connect(self.quit)

        if len(sys.argv) > 1:
            self.messageQueue.put((1, 'System', 'Arguments', sys.argv[1]))

    def checkAndSetAutomation(self):
        """
        the windows' automation with pywinauto has a serious bug in python lib.
        the bugfix is done from python 3.8.2 onwards. so to enable this work,
        we have to check the python version used and set the topic adequately.

        :return:
        """
        if not checkAutomation():
            return None

        automation = AutomateWindows(self)
        if automation.updaterApp != '':
            path = automation.installPath
            app = automation.updaterApp
            t = f'{path}{app}'
            self.messageQueue.put((1, 'System', '10micron updater', t))
        else:
            self.messageQueue.put((2, 'System', '10micron updater',
                                  'Not available !'))
        return automation

    def storeStatusOperationRunning(self, status):
        """
        :return:
        """
        self.statusOperationRunning = status
        return True

    def initConfig(self):
        """
        :return: topo object with location
        """
        lat = self.config.get('topoLat', 51.47)
        lon = self.config.get('topoLon', 0)
        elev = self.config.get('topoElev', 46)
        topo = wgs84.latlon(longitude_degrees=lon,
                            latitude_degrees=lat,
                            elevation_m=elev)

        config = self.config.get('mainW', {})
        if config.get('loglevelTrace', False):
            level = 'TRACE'
        elif config.get('loglevelDebug', False):
            level = 'DEBUG'
        else:
            level = 'INFO'
        setCustomLoggingLevel(level)
        return topo

    def storeConfig(self):
        """
        :return: success for test purpose
        """
        location = self.mount.obsSite.location
        if location is not None:
            self.config['topoLat'] = location.latitude.degrees
            self.config['topoLon'] = location.longitude.degrees
            self.config['topoElev'] = location.elevation.m
        return True

    def sendUpdate(self):
        """
        sendUpdate send regular signals in 1 and 10 seconds to enable regular
        tasks. it tries to avoid sending the signals at the same time.

        :return: true for test purpose
        """
        self.timerCounter += 1
        if self.timerCounter % 1 == 0:
            self.update0_1s.emit()
        if (self.timerCounter + 5) % 10 == 0:
            self.update1s.emit()
        if (self.timerCounter + 10) % 30 == 0:
            self.update3s.emit()
        if (self.timerCounter + 20) % 100 == 0:
            self.update10s.emit()
        if (self.timerCounter + 25) % 300 == 0:
            self.update30s.emit()
        if (self.timerCounter + 25) % 600 == 0:
            self.update60s.emit()
        if (self.timerCounter + 12) % 1800 == 0:
            self.update3m.emit()
        if (self.timerCounter + 13) % 6000 == 0:
            self.update10m.emit()
        if (self.timerCounter + 14) % 18000 == 0:
            self.update30m.emit()
        if (self.timerCounter + 15) % 36000 == 0:
            self.update1h.emit()
        if self.timerCounter == 10:
            self.start1s.emit()
        if self.timerCounter == 30:
            self.start3s.emit()
        if self.timerCounter == 50:
            self.start5s.emit()
        if self.timerCounter == 100:
            self.start10s.emit()
        if self.timerCounter == 300:
            self.start30s.emit()
        return True

    def aboutToQuit(self):
        """
        :return:    True for test purpose
        """
        self.timer0_1s.stop()
        self.mount.stopTimers()
        return True

    def quit(self):
        """
        :return:    True for test purpose
        """
        self.aboutToQuit()
        self.deviceStat['mount'] = False
        self.messageQueue.put((1, 'System', 'Lifecycle',
                              'MountWizzard4 manual stopped'))
        self.application.quit()
        return True

    def loadHorizonData(self):
        """
        :return:
        """
        config = self.config.get('hemisphereW', {})
        fileName = config.get('horizonMaskFileName', '')
        self.data.loadHorizonP(fileName=fileName)
        return True

    def loadMountData(self, status):
        """
        :param      status: connection status to mount computer
        :return:    status how it was called
        """
        if status and not self.mountUp:
            self.mount.cycleSetting()
            self.mount.getFW()
            self.mount.getLocation()
            self.mainW.refreshName()
            self.mainW.refreshModel()
            self.mountUp = True
            self.mount.getTLE()
            return True

        elif not status and self.mountUp:
            location = self.mount.obsSite.location
            self.mount.resetData()
            self.mount.obsSite.location = location
            self.mountUp = False
            self.playSound.emit('ConnectionLost')
            return False
        return status

    def writeMessageQueue(self, prio, source, mType, message):
        """
        :param prio:
        :param source:
        :param mType:
        :param message:
        :return: True for test purpose
        """
        self.log.ui(f'Message window: [{source} - {mType} - {message}]')
        self.messageQueue.put((prio, source, mType, message))
        return True
