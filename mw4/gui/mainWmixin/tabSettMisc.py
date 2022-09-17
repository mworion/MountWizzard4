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
import base.packageConfig as pConf
# standard libraries
import os
import sys
import platform
from packaging.utils import Version

# external packages
from pkg_resources import working_set
if pConf.isAvailable:
    from PyQt5.QtMultimedia import QSound
import requests
import importlib_metadata
from astropy.utils import iers, data
import hid
import webbrowser
from PyQt5.QtWidgets import QWidget

# local import
from base.loggerMW import setCustomLoggingLevel
from base.packageConfig import checkAutomation
from gui.utilities.toolsQtWidget import sleepAndEvents
from base.tpool import Worker


class SettMisc(object):
    """
    """

    def __init__(self):
        self.audioSignalsSet = dict()
        self.guiAudioList = dict()
        self.gameControllerList = dict()
        self.process = None
        self.stopWindow = None

        self.ui.loglevelTrace.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelStandard.clicked.connect(self.setLoggingLevel)
        self.ui.automateSlow.clicked.connect(self.setAutomationSpeed)
        self.ui.automateFast.clicked.connect(self.setAutomationSpeed)
        self.ui.automateNormal.clicked.connect(self.setAutomationSpeed)
        self.ui.isOnline.clicked.connect(self.setWeatherOnline)
        self.ui.isOnline.clicked.connect(self.setSeeingOnline)
        self.ui.isOnline.clicked.connect(self.setupIERS)
        self.ui.versionBeta.clicked.connect(self.showUpdates)
        self.ui.versionRelease.clicked.connect(self.showUpdates)
        self.ui.versionReleaseNotes.clicked.connect(self.showUpdates)
        self.ui.isOnline.clicked.connect(self.showUpdates)
        self.ui.installVersion.clicked.connect(self.installVersion)
        self.app.update3s.connect(self.populateGameControllerList)
        self.ui.gameControllerGroup.clicked.connect(self.populateGameControllerList)
        self.ui.openPDF.clicked.connect(self.openPDF)
        self.ui.addProfileGroup.clicked.connect(self.setAddProfileGUI)
        self.ui.showTabAlmanac.clicked.connect(self.minimizeGUI)
        self.ui.showTabEnviron.clicked.connect(self.minimizeGUI)
        self.ui.showTabSatellite.clicked.connect(self.minimizeGUI)
        self.ui.showTabMPC.clicked.connect(self.minimizeGUI)
        self.ui.showTabTools.clicked.connect(self.minimizeGUI)
        self.ui.showTabDome.clicked.connect(self.minimizeGUI)
        self.ui.showTabParkPos.clicked.connect(self.minimizeGUI)
        self.ui.showTabProfile.clicked.connect(self.minimizeGUI)

        if pConf.isAvailable:
            self.app.mount.signals.alert.connect(lambda: self.playSound('MountAlert'))
            self.app.dome.signals.slewFinished.connect(lambda: self.playSound('DomeSlew'))
            self.app.mount.signals.slewFinished.connect(lambda: self.playSound('MountSlew'))
            self.app.camera.signals.saved.connect(lambda: self.playSound('ImageSaved'))
            self.app.plateSolve.signals.done.connect(lambda: self.playSound('ImageSolved'))
            self.app.playSound.connect(self.playSound)
            self.setupAudioSignals()

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.setupAudioGui()
        self.ui.loglevelTrace.setChecked(config.get('loglevelTrace', False))
        self.ui.loglevelDebug.setChecked(config.get('loglevelDebug', True))
        self.ui.loglevelStandard.setChecked(config.get('loglevelStandard', False))
        self.ui.isOnline.setChecked(config.get('isOnline', False))
        self.ui.storeTabOrder.setChecked(config.get('storeTabOrder', False))
        self.ui.automateFast.setChecked(config.get('automateFast', False))
        self.ui.automateNormal.setChecked(config.get('automateSlow', True))
        self.ui.automateSlow.setChecked(config.get('automateSlow', True))
        self.ui.unitTimeUTC.setChecked(config.get('unitTimeUTC', True))
        self.ui.unitTimeLocal.setChecked(config.get('unitTimeLocal', False))
        self.ui.addProfileGroup.setChecked(config.get('addProfileGroup', False))
        self.ui.showTabAlmanac.setChecked(config.get('showTabAlmanac', True))
        self.ui.showTabEnviron.setChecked(config.get('showTabEnviron', True))
        self.ui.showTabSatellite.setChecked(config.get('showTabSatellite', True))
        self.ui.showTabMPC.setChecked(config.get('showTabMPC', True))
        self.ui.showTabTools.setChecked(config.get('showTabTools', True))
        self.ui.showTabDome.setChecked(config.get('showTabDome', True))
        self.ui.showTabParkPos.setChecked(config.get('showTabParkPos', True))
        self.ui.showTabProfile.setChecked(config.get('showTabProfile', True))

        self.ui.versionReleaseNotes.setChecked(
            config.get('versionReleaseNotes', True))
        self.ui.soundMountSlewFinished.setCurrentIndex(
            config.get('soundMountSlewFinished', 0))
        self.ui.soundDomeSlewFinished.setCurrentIndex(
            config.get('soundDomeSlewFinished', 0))
        self.ui.soundMountAlert.setCurrentIndex(config.get('soundMountAlert', 0))
        self.ui.soundRunFinished.setCurrentIndex(
            config.get('soundRunFinished', 0))
        self.ui.soundImageSaved.setCurrentIndex(config.get('soundImageSaved', 0))
        self.ui.soundImageSolved.setCurrentIndex(config.get('soundImageSolved', 0))
        self.ui.soundConnectionLost.setCurrentIndex(
            config.get('soundConnectionLost', 0))
        self.ui.soundSatStartTracking.setCurrentIndex(config.get(
            'soundSatStartTracking', 0))
        self.ui.gameControllerGroup.setChecked(
            config.get('gameControllerGroup', False))
        self.ui.gameControllerList.setCurrentIndex(config.get(
            'gameControllerList', 0))

        isWindows = platform.system() == 'Windows'
        self.ui.automateGroup.setVisible(isWindows)
        self.minimizeGUI()
        self.populateGameControllerList()
        self.setAutomationSpeed()
        self.setWeatherOnline()
        self.setSeeingOnline()
        self.setupIERS()
        self.setAddProfileGUI()
        self.showUpdates()
        return True

    def storeConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['loglevelTrace'] = self.ui.loglevelTrace.isChecked()
        config['loglevelDebug'] = self.ui.loglevelDebug.isChecked()
        config['loglevelStandard'] = self.ui.loglevelStandard.isChecked()
        config['automateFast'] = self.ui.automateFast.isChecked()
        config['automateNormal'] = self.ui.automateNormal.isChecked()
        config['automateSlow'] = self.ui.automateSlow.isChecked()
        config['isOnline'] = self.ui.isOnline.isChecked()
        config['storeTabOrder'] = self.ui.storeTabOrder.isChecked()
        config['unitTimeUTC'] = self.ui.unitTimeUTC.isChecked()
        config['unitTimeLocal'] = self.ui.unitTimeLocal.isChecked()
        config['addProfileGroup'] = self.ui.addProfileGroup.isChecked()
        config['showTabAlmanac'] = self.ui.showTabAlmanac.isChecked()
        config['showTabEnviron'] = self.ui.showTabEnviron.isChecked()
        config['showTabSatellite'] = self.ui.showTabSatellite.isChecked()
        config['showTabMPC'] = self.ui.showTabMPC.isChecked()
        config['showTabTools'] = self.ui.showTabTools.isChecked()
        config['showTabDome'] = self.ui.showTabDome.isChecked()
        config['showTabParkPos'] = self.ui.showTabParkPos.isChecked()
        config['showTabProfile'] = self.ui.showTabProfile.isChecked()
        config['versionReleaseNotes'] = self.ui.versionReleaseNotes.isChecked()
        config['soundMountSlewFinished'] = self.ui.soundMountSlewFinished.currentIndex()
        config['soundDomeSlewFinished'] = self.ui.soundDomeSlewFinished.currentIndex()
        config['soundMountAlert'] = self.ui.soundMountAlert.currentIndex()
        config['soundRunFinished'] = self.ui.soundRunFinished.currentIndex()
        config['soundImageSaved'] = self.ui.soundImageSaved.currentIndex()
        config['soundImageSolved'] = self.ui.soundImageSolved.currentIndex()
        config['soundConnectionLost'] = self.ui.soundConnectionLost.currentIndex()
        config['soundSatStartTracking'] = self.ui.soundSatStartTracking.currentIndex()
        config['gameControllerGroup'] = self.ui.gameControllerGroup.isChecked()
        config['gameControllerList'] = self.ui.gameControllerList.currentIndex()
        return True

    def sendGameControllerSignals(self, act, old):
        """
        :param act:
        :param old:
        :return:
        """
        if act[0] != old[0]:
            self.app.gameABXY.emit(act[0])
        if act[1] != old[1]:
            self.app.gamePMH.emit(act[1])
        if act[2] != old[2]:
            self.app.gameDirection.emit(act[2])
        if act[3] != old[3] or act[4] != old[4]:
            self.app.game_sL.emit(act[3], act[4])
        if act[5] != old[5] or act[6] != old[6]:
            self.app.game_sR.emit(act[5], act[6])
        self.log.trace(f'GameController: {[act]}, {[old]}')
        return True

    def readGameController(self, gamepad):
        """
        :param gamepad:
        :return:
        """
        result = []
        while self.gameControllerRunning:
            try:
                data = gamepad.read(64)
            except Exception as e:
                self.gameControllerRunning = False
                self.log.warning(f'GameController error {e}')
                return []

            if len(data) == 0:
                break
            result = data
        return result

    def convertData(self, name, iR):
        """
        :param name:
        :param iR:
        :return:
        """
        oR = [0, 0, 0, 0, 0, 0, 0]
        if len(iR) == 0:
            return oR
        if name == 'Pro Controller':
            oR = [iR[1], iR[2], iR[3], iR[5], iR[7], iR[9], iR[11]]
        elif name == 'Controller (XBOX 360 For Windows)':
            if iR[11] == 0b00011100:
                val = 0b00000110
            elif iR[11] == 0b00010100:
                val = 0b00000100
            elif iR[11] == 0b00001100:
                val = 0b00000010
            elif iR[11] == 0b00000100:
                val = 0b00000000
            else:
                val = 0b00001111
            oR = [iR[10], 0, val, iR[1], iR[3], iR[5], iR[7]]
        self.log.info(f'Controller: [{name}], values: [{oR}]')
        return oR

    @staticmethod
    def isNewerData(act, old):
        """
        :param act:
        :param old:
        :return:
        """
        if len(act) == 0:
            return False
        for i, dataVal in enumerate(act):
            if dataVal != old[i]:
                break
        else:
            return False
        return True

    def workerGameController(self):
        """
        :return:
        """
        gameControllerDevice = hid.device()
        name = self.ui.gameControllerList.currentText()
        gameController = self.gameControllerList.get(name)
        if gameController is None:
            return False

        vendorId = gameController['vendorId']
        productId = gameController['productId']

        self.log.debug(f'GameController: [{name} {vendorId}:{productId}]')
        self.msg.emit(1, 'System', 'GameController', f'Starting {[name]}')
        gameControllerDevice.open(vendorId, productId)
        gameControllerDevice.set_nonblocking(True)

        reportOld = [0] * 16
        while self.gameControllerRunning:
            sleepAndEvents(100)
            report = self.readGameController(gameControllerDevice)
            if not self.isNewerData(report, reportOld):
                continue
            report = self.convertData(name, report)
            self.sendGameControllerSignals(report, reportOld)
            reportOld = report
        return True

    def startGameController(self):
        """
        :return:
        """
        worker = Worker(self.workerGameController)
        self.threadPool.start(worker)
        return True

    @staticmethod
    def isValidGameControllers(name):
        """
        :param name:
        :return:
        """
        validStrings = ['Controller', 'Game']
        for check in validStrings:
            if check in name:
                break
        else:
            return False
        return True

    def populateGameControllerList(self):
        """
        :return:
        """
        isController = self.ui.gameControllerGroup.isChecked()
        if not isController:
            self.gameControllerRunning = False
            return False
        if self.gameControllerRunning:
            return False

        self.ui.gameControllerList.clear()
        self.gameControllerList.clear()
        for device in hid.enumerate():
            name = device['product_string']
            if not self.isValidGameControllers(name):
                continue
            self.gameControllerList[name] = {'vendorId': device['vendor_id'],
                                             'productId': device['product_id']}
            self.ui.gameControllerList.addItem(name)
            self.msg.emit(0, 'System', 'GameController', f'Found {[name]}')

        if len(self.gameControllerList) == 0:
            return False

        self.gameControllerRunning = True
        self.startGameController()
        return True

    def setWeatherOnline(self):
        """
        :return: success
        """
        weather = self.app.onlineWeather
        if not weather:
            return False

        weather.online = self.ui.isOnline.isChecked()
        return True

    def setSeeingOnline(self):
        """
        :return: success
        """
        seeing = self.app.seeingWeather
        if not seeing:
            return False

        seeing.online = self.ui.isOnline.isChecked()
        return True

    def setupIERS(self):
        """
        setupIERS enables or disables the update of astropy necessary files
        depending on online status .

        :return: True for test purpose
        """
        isOnline = self.ui.isOnline.isChecked()
        if isOnline:
            iers.conf.auto_download = True
            iers.conf.auto_max_age = 30
            data.conf.allow_internet = True

        else:
            iers.conf.auto_download = False
            iers.conf.auto_max_age = 99999
            data.conf.allow_internet = False
        return True

    def versionPackage(self, packageName):
        """
        versionPackage will look the package up in pypi.org website and parses
        the resulting versions. if you have an alpa or beta release found it
        returns the newest version for download and install.

        :param packageName:
        :return: None or the newest possible package
        """
        url = f'https://pypi.python.org/pypi/{packageName}/json'
        try:
            response = requests.get(url).json()

        except Exception as e:
            self.log.critical(f'Cannot determine package version: {e}')
            return None, None, None

        vPackage = list(response['releases'].keys())
        vPackage.sort(key=Version, reverse=True)

        verBeta = [x for x in vPackage if 'b' in x]
        verRelease = [x for x in vPackage if 'b' not in x and 'a' not in x]

        self.log.info(f'Package Beta:   {verBeta[:10]}')
        self.log.info(f'Package Release:{verRelease[:10]}')

        if self.ui.versionBeta.isChecked():
            finalPackage = verBeta
        else:
            finalPackage = verRelease

        if len(finalPackage) == 0:
            return None, None, None

        finalPackage = finalPackage[0]
        comment = response['releases'][finalPackage][0]['comment_text']
        return finalPackage, comment, vPackage

    def showUpdates(self):
        """
        showUpdates compares the actual installed and running package with the
        one on the server. if you have a newer version available, mw4 will inform
        the user about it.

        :return: success
        """
        packageName = 'mountwizzard4'
        actPackage = importlib_metadata.version(packageName)
        self.ui.versionActual.setText(actPackage)

        if not self.ui.isOnline.isChecked():
            self.ui.versionAvailable.setText('disabled')
            self.ui.installVersion.setEnabled(False)
            return False

        availPackage, comment, _ = self.versionPackage(packageName)

        if availPackage is None:
            self.msg.emit(2, 'System', 'Update',
                          'Failed get actual package from server')
            return False

        self.ui.versionAvailable.setText(availPackage)
        self.ui.installVersion.setEnabled(True)

        if Version(availPackage) <= Version(actPackage):
            return True

        t = f'A new version ({availPackage}) of MountWizzard is available!'
        self.msg.emit(1, 'System', 'Update', t)

        if not self.ui.versionReleaseNotes.isChecked():
            return True
        if not comment:
            return True

        self.msg.emit(1, 'System', 'Update',
                      f'Release notes for {availPackage}:')
        for line in comment.split('\n'):
            self.msg.emit(2, '', '', line)
        return True

    def isVenv(self):
        """
        detects if the actual package is running in a virtual environment. this
        should be the case in any situation as mw4 should be installed in a venv.

        :return: status
        """
        hasReal = hasattr(sys, 'real_prefix')
        hasBase = hasattr(sys, 'base_prefix')

        status = hasReal or hasBase and sys.base_prefix != sys.prefix
        if hasReal:
            self.log.debug(f'Real prefix: [{sys.real_prefix}]')
        if hasBase:
            self.log.debug(f'Base prefix: [{sys.base_prefix}]')
        self.log.debug(f'PATH:        [{os.environ.get("PATH", "")}]')
        self.log.debug(f'VENV path:   [{os.environ.get("VIRTUAL_ENV", "")}]')
        self.log.debug(f'VENV status: [{status}]')
        return status

    def checkUpdateVersion(self, versionPackage):
        """
        :return:
        """
        if platform.system() != 'Windows':
            return True

        url = f'https://pypi.python.org/pypi/mountwizzard4/{versionPackage}/json'
        try:
            response = requests.get(url).json()
        except Exception as e:
            self.log.critical(f'Cannot determine package data: {e}')
            return None
        else:
            self.log.trace(f'{response["info"]}')

        targetPyQt5 = response['info']['keywords'].split(',')[0]
        actPyQt5 = importlib_metadata.version('PyQt5')
        self.log.debug(f'target: [{targetPyQt5}], actual: [{actPyQt5}]')
        return targetPyQt5 == actPyQt5

    def startUpdater(self, versionPackage):
        """
        :return:
        """
        pythonPath = os.path.abspath(sys.executable)
        pythonRuntime = pythonPath
        updaterDir = os.path.dirname(sys.argv[0])
        updaterScript = os.path.abspath(updaterDir + '/update.py')

        if platform.system() == 'Windows':
            updaterScript = "\"" + updaterScript + "\""
            pythonRuntime = "\"" + pythonPath + "\""

        uType = self.checkUpdateVersion(versionPackage)
        if uType is None:
            return False
        elif uType:
            updateType = 'GUI'
        else:
            updateType = 'CLI'

        os.execl(pythonPath, pythonRuntime, updaterScript, versionPackage,
                 str(self.pos().x()), str(self.pos().y()), updateType,
                 str(self.colorSet))
        return True

    def installVersion(self):
        """
        installVersion updates mw4 with the standard pip package installer.
        this is actually only tested and ok for running in a virtual environment.
        updates have to run only once at a time, so a mutex ensures this. If
        everything is ok, a thread it started doing the installation work, and a
        callback executes when finished.

        as observation, installation on Windows side takes for some reasons
        longer than in linux or osx environment. therefore, an extended timeout
        runs.

        :return: True for test purpose
        """
        if not (self.isVenv() or platform.machine() == 'armv7l'):
            self.msg.emit(2, 'System', 'Update',
                          'MW4 not running in an virtual environment')
            return False

        packages = sorted([f'{i.key}=={i.version}' for i in working_set])
        self.log.debug(f'Before update:  {packages}')

        versionPackage = self.ui.versionAvailable.text()
        _, _, existPackage = self.versionPackage('MountWizzard4')

        if versionPackage not in existPackage:
            self.msg.emit(2, 'System', 'Update',
                          f'Version {versionPackage} does not exist')
            return False

        self.msg.emit(1, 'System', 'Update',
                      f'Installing [{versionPackage}] please wait')
        self.startUpdater(versionPackage)
        return True

    def setLoggingLevel(self):
        """
        :return: nothing
        """
        if self.ui.loglevelTrace.isChecked():
            setCustomLoggingLevel('TRACE')
        elif self.ui.loglevelDebug.isChecked():
            setCustomLoggingLevel('DEBUG')
        elif self.ui.loglevelStandard.isChecked():
            setCustomLoggingLevel('INFO')

    def setupAudioGui(self):
        """
        :return: True for test purpose
        """
        self.guiAudioList['MountSlew'] = self.ui.soundMountSlewFinished
        self.guiAudioList['DomeSlew'] = self.ui.soundDomeSlewFinished
        self.guiAudioList['MountAlert'] = self.ui.soundMountAlert
        self.guiAudioList['RunFinished'] = self.ui.soundRunFinished
        self.guiAudioList['ImageSaved'] = self.ui.soundImageSaved
        self.guiAudioList['ConnectionLost'] = self.ui.soundConnectionLost
        self.guiAudioList['SatStartTracking'] = self.ui.soundSatStartTracking
        self.guiAudioList['ImageSolved'] = self.ui.soundImageSolved

        for itemKey, itemValue in self.guiAudioList.items():
            self.guiAudioList[itemKey].addItem('None')
            self.guiAudioList[itemKey].addItem('Beep')
            self.guiAudioList[itemKey].addItem('Beep1')
            self.guiAudioList[itemKey].addItem('Beep2')
            self.guiAudioList[itemKey].addItem('Bleep')
            self.guiAudioList[itemKey].addItem('Pan1')
            self.guiAudioList[itemKey].addItem('Pan2')
            self.guiAudioList[itemKey].addItem('Horn')
            self.guiAudioList[itemKey].addItem('Alarm')
            self.guiAudioList[itemKey].addItem('Alert')
        return True

    def setupAudioSignals(self):
        """
        :return: True for test purpose
        """
        self.audioSignalsSet['Beep'] = ':/sound/beep.wav'
        self.audioSignalsSet['Beep1'] = ':/sound/beep1.wav'
        self.audioSignalsSet['Horn'] = ':/sound/horn.wav'
        self.audioSignalsSet['Beep2'] = ':/sound/Beep2.wav'
        self.audioSignalsSet['Bleep'] = ':/sound/Bleep.wav'
        self.audioSignalsSet['Pan1'] = ':/sound/Pan1.wav'
        self.audioSignalsSet['Pan2'] = ':/sound/Pan2.wav'
        self.audioSignalsSet['Alert'] = ':/sound/alert.wav'
        self.audioSignalsSet['Alarm'] = ':/sound/alarm.wav'
        return True

    def playSound(self, value=''):
        """
        :param value:
        :return: success
        """
        listEntry = self.guiAudioList.get(value, None)
        if listEntry is None:
            return False

        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            QSound.play(self.audioSignalsSet[sound])
            return True

        else:
            return False

    def setAutomationSpeed(self):
        """
        :return:
        """
        if not checkAutomation():
            return False

        self.app.automation.automateFast = self.ui.automateFast.isChecked()
        self.app.automation.automateSlow = self.ui.automateSlow.isChecked()
        return True

    def openPDF(self):
        """
        :return:
        """
        fileName = './data/mountwizzard4.pdf'
        filePath = os.path.abspath(fileName)
        url = f'file://{filePath}'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Setting Misc', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Setting Misc', 'Doc opened')
        return True

    def setAddProfileGUI(self):
        """
        :return:
        """
        isEnabled = self.ui.addProfileGroup.isChecked()
        self.ui.addFrom.setEnabled(isEnabled)
        self.ui.addFrom.setVisible(isEnabled)
        self.ui.profileAdd.setEnabled(isEnabled)
        self.ui.profileAdd.setVisible(isEnabled)
        return True

    def minimizeGUI(self):
        """
        :return:
        """
        tabs = {
            'Almanac': {
                'cb': self.ui.showTabAlmanac,
                'tab': self.ui.mainTabWidget
            },
            'Environ': {
                'cb': self.ui.showTabEnviron,
                'tab': self.ui.mainTabWidget
            },
            'Satellite': {
                'cb': self.ui.showTabSatellite,
                'tab': self.ui.mainTabWidget,
            },
            'MPC': {
                'cb': self.ui.showTabMPC,
                'tab': self.ui.mainTabWidget,
            },
            'Tools': {
                'cb': self.ui.showTabTools,
                'tab': self.ui.mainTabWidget,
            },
            'Dome': {
                'cb': self.ui.showTabDome,
                'tab': self.ui.settingsTabWidget,
            },
            'ParkPos': {
                'cb': self.ui.showTabParkPos,
                'tab': self.ui.settingsTabWidget,
            },
            'Profile': {
                'cb': self.ui.showTabProfile,
                'tab': self.ui.settingsTabWidget,
            },
        }
        for tab in tabs:
            isVisible = tabs[tab]['cb'].isChecked()
            tabWidget = tabs[tab]['tab'].findChild(QWidget, tab)
            tabIndex = tabs[tab]['tab'].indexOf(tabWidget)
            tabs[tab]['tab'].setTabVisible(tabIndex, isVisible)
        return True
