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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import os
import json
import sys
from queue import Queue
import platform

# external packages
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool, QTimer
from skyfield.api import wgs84
from importlib_metadata import version
from PyQt5.QtTest import QTest

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
from logic.environment.directWeather import DirectWeather
from logic.environment.weatherUPB import WeatherUPB
from logic.cover.cover import Cover
from logic.telescope.telescope import Telescope
from logic.powerswitch.pegasusUPB import PegasusUPB
from logic.measure.measure import MeasureData
from logic.remote.remote import Remote
from logic.astrometry.astrometry import Astrometry


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

    message = pyqtSignal(str, int)
    messageQueue = Queue()
    redrawHemisphere = pyqtSignal()
    updatePointMarker = pyqtSignal()
    drawBuildPoints = pyqtSignal()
    enableEditPoints = pyqtSignal(object)
    buildPointsChanged = pyqtSignal()
    drawHorizonPoints = pyqtSignal()
    updateDomeSettings = pyqtSignal()
    sendSatelliteData = pyqtSignal()
    showImage = pyqtSignal(str)
    showAnalyse = pyqtSignal(str)
    remoteCommand = pyqtSignal(str)

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

    def __init__(self,
                 mwGlob=None,
                 application=None
                 ):

        super().__init__()

        self.application = application
        self.expireData = False
        self.mountUp = False
        self.mwGlob = mwGlob
        self.timerCounter = 0
        self.mainW = None
        self.threadPool = QThreadPool()
        self.threadPool.setMaxThreadCount(30)
        self.message.connect(self.writeMessageQueue)
        self.config = {}
        self.loadConfig()
        self.deviceStat = {
            'dome': None,
            'mount': None,
            'camera': None,
            'astrometry': None,
            'environOverall': None,
            'sensorWeather': None,
            'directWeather': None,
            'onlineWeather': None,
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
        self.messageQueue.put(('MountWizzard4 started', 1))
        self.messageQueue.put((f'Workdir is: [{self.mwGlob["workDir"]}]', 1))
        self.messageQueue.put((f'Profile              [{profile}] loaded', 1))

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
        self.ephemeris = self.mount.obsSite.loader('de421_23.bsp')
        self.relay = KMRelay()
        self.sensorWeather = SensorWeather(self)
        self.onlineWeather = OnlineWeather(self)
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
        self.hipparcos = Hipparcos(self)
        self.measure = MeasureData(self)
        self.remote = Remote(self)
        self.astrometry = Astrometry(self)
        self.automation = self.checkAndSetAutomation()

        self.uiWindows = {}
        self.mainW = MainWindow(self)

        self.mount.startTimers()
        self.timer0_1s = QTimer()
        self.timer0_1s.setSingleShot(False)
        self.timer0_1s.timeout.connect(self.sendUpdate)
        self.timer0_1s.start(100)
        self.application.aboutToQuit.connect(self.aboutToQuit)

        if os.path.isfile('test.txt'):
            self.update3s.connect(self.quit)

        if len(sys.argv) > 1:
            self.message.emit(sys.argv[1], 1)

    def checkAndSetAutomation(self):
        """
        the windows automation with pywinauto has a serious bug in python lib.
        the bugfix is done from python 3.8.2 onwards. so to enable this work,
        we have to check the python version used and set the topic adequately.

        :return:
        """
        if platform.system() != 'Windows':
            return None
        if platform.python_version() < '3.8.2':
            return None

        from logic.automation.automateWindows import AutomateWindows
        automation = AutomateWindows(self)

        return automation

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
        self.threadPool.waitForDone(5000)
        self.message.emit('MountWizzard4 manual stopped', 1)
        self.application.quit()
        return True

    @staticmethod
    def defaultConfig(config=None):
        """
        :param config:
        :return:
        """
        if config is None:
            config = dict()

        config['profileName'] = 'config'
        config['version'] = '4.0'
        return config

    def loadConfig(self, name=None):
        """
        loadConfig loads a json file from disk and stores it to the config
        dicts for persistent data. if a file path is given, that's the relevant
        file, otherwise loadConfig loads from th default file, which is
        config.cfg

        :param      name:   name of the config file
        :return:    success if file could be loaded
        """
        configDir = self.mwGlob['configDir']
        if name is None:
            profileFile = f'{configDir}/profile'
            if os.path.isfile(profileFile):
                with open(profileFile, 'r') as profile:
                    name = profile.readline().strip()
            else:
                name = 'config'

        self.config['profileName'] = name

        fileName = f'{configDir}/{name}.cfg'

        if not os.path.isfile(fileName):
            self.config = self.defaultConfig()
            self.log.info(f'Config file {fileName} not existing')
            return False

        try:
            with open(fileName, 'r') as configFile:
                configData = json.load(configFile)
        except Exception as e:
            self.log.critical(f'Cannot parse: {fileName}, error: {e}')
            self.config = self.defaultConfig()
            return False
        else:
            self.config = configData

        return True

    @staticmethod
    def convertData(data):
        """
        convertDate tries to convert data from an older or newer version of the
        config file to the actual needed one.

        :param      data: config data as dict
        :return:    data: config data as dict
        """
        return data

    def saveConfig(self, name=None):
        """
        :param      name:   name of the config file
        :return:    success
        """
        configDir = self.mwGlob['configDir']
        if name is None:
            name = self.config['profileName']

        profileFile = f'{configDir}/profile'
        with open(profileFile, 'w') as profile:
            profile.writelines(f'{name}')

        fileName = configDir + '/' + name + '.cfg'
        with open(fileName, 'w') as outfile:
            json.dump(self.config,
                      outfile,
                      sort_keys=True,
                      indent=4)
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
            QTest.qWait(500)
            self.mount.getTLE()
            return True

        elif not status and self.mountUp:
            location = self.mount.obsSite.location
            self.mount.resetData()
            self.mount.obsSite.location = location
            self.mountUp = False
            return False
        return status

    def writeMessageQueue(self, message, mType):
        """
        :param message:
        :param mType:
        :return: True for test purpose
        """
        self.log.ui(f'Message window: [{message}]')
        self.messageQueue.put((message, mType))
        return True
