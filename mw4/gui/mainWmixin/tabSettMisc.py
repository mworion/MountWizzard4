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
# Licence APL2.0
#
###########################################################
import base.packageConfig as pConf
# standard libraries
import os
import time
import subprocess
import sys
import platform
from dateutil.tz import tzlocal

# external packages
from pkg_resources import working_set
from distutils.version import StrictVersion
import PyQt5
if pConf.isAvailable:
    import PyQt5.QtMultimedia
import requests
import importlib_metadata
from astropy.utils import iers
from astropy.utils import data

# local import
from base.loggerMW import setCustomLoggingLevel
from base import tpool


class SettMisc(object):
    """
    """

    def __init__(self):
        self.audioSignalsSet = dict()
        self.guiAudioList = dict()
        self.process = None
        self.mutexInstall = PyQt5.QtCore.QMutex()

        self.ui.loglevelTrace.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelStandard.clicked.connect(self.setLoggingLevel)
        self.ui.isOnline.clicked.connect(self.setWeatherOnline)
        self.ui.isOnline.clicked.connect(self.setupIERS)
        self.ui.versionBeta.clicked.connect(self.showUpdates)
        self.ui.versionRelease.clicked.connect(self.showUpdates)
        self.ui.versionReleaseNotes.clicked.connect(self.showUpdates)
        self.ui.isOnline.clicked.connect(self.showUpdates)
        self.ui.installVersion.clicked.connect(self.installVersion)
        self.ui.pushTime.clicked.connect(self.pushTime)
        self.ui.activateVirtualStop.stateChanged.connect(self.setVirtualStop)
        self.app.update1h.connect(self.pushTimeHourly)
        self.app.update30s.connect(self.syncClock)
        self.ui.autoPushTime.stateChanged.connect(self.pushTimeHourly)
        self.ui.clockSync.stateChanged.connect(self.toggleClockSync)

        if pConf.isAvailable:
            self.app.mount.signals.alert.connect(lambda: self.playSound('MountAlert'))
            self.app.dome.signals.slewFinished.connect(lambda: self.playSound('DomeSlew'))
            self.app.mount.signals.slewFinished.connect(lambda: self.playSound('MountSlew'))
            self.app.camera.signals.saved.connect(lambda: self.playSound('ImageSaved'))
            self.app.astrometry.signals.done.connect(lambda: self.playSound('ImageSolved'))
            self.setupAudioSignals()

    def initConfig(self):
        """
        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.setupAudioGui()
        self.ui.loglevelTrace.setChecked(config.get('loglevelTrace', False))
        self.ui.loglevelDebug.setChecked(config.get('loglevelDebug', False))
        self.ui.loglevelStandard.setChecked(config.get('loglevelStandard', True))
        self.ui.isOnline.setChecked(config.get('isOnline', False))
        self.ui.autoPushTime.setChecked(config.get('autoPushTime', False))
        self.ui.syncNotTracking.setChecked(config.get('syncNotTracking', True))
        self.ui.syncTimePC2Mount.setChecked(config.get('syncTimePC2Mount', False))
        self.ui.clockSync.setChecked(config.get('clockSync', False))
        self.ui.automaticRestart.setChecked(config.get('automaticRestart', False))
        self.ui.activateVirtualStop.setChecked(config.get('activateVirtualStop', False))
        self.ui.versionReleaseNotes.setChecked(config.get('versionReleaseNotes', True))
        self.ui.soundMountSlewFinished.setCurrentIndex(config.get('soundMountSlewFinished', 0))
        self.ui.soundDomeSlewFinished.setCurrentIndex(config.get('soundDomeSlewFinished', 0))
        self.ui.soundMountAlert.setCurrentIndex(config.get('soundMountAlert', 0))
        self.ui.soundModelingFinished.setCurrentIndex(config.get('soundModelingFinished', 0))
        self.ui.soundImageSaved.setCurrentIndex(config.get('soundImageSaved', 0))
        self.ui.soundImageSolved.setCurrentIndex(config.get('soundImageSolved', 0))

        self.toggleClockSync()
        self.setWeatherOnline()
        self.setupIERS()
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
        config['isOnline'] = self.ui.isOnline.isChecked()
        config['autoPushTime'] = self.ui.autoPushTime.isChecked()
        config['syncNotTracking'] = self.ui.syncNotTracking.isChecked()
        config['syncTimePC2Mount'] = self.ui.syncTimePC2Mount.isChecked()
        config['clockSync'] = self.ui.clockSync.isChecked()
        config['automaticRestart'] = self.ui.automaticRestart.isChecked()
        config['activateVirtualStop'] = self.ui.activateVirtualStop.isChecked()
        config['versionReleaseNotes'] = self.ui.versionReleaseNotes.isChecked()
        config['soundMountSlewFinished'] = self.ui.soundMountSlewFinished.currentIndex()
        config['soundDomeSlewFinished'] = self.ui.soundDomeSlewFinished.currentIndex()
        config['soundMountAlert'] = self.ui.soundMountAlert.currentIndex()
        config['soundModelingFinished'] = self.ui.soundModelingFinished.currentIndex()
        config['soundImageSaved'] = self.ui.soundImageSaved.currentIndex()
        config['soundImageSolved'] = self.ui.soundImageSolved.currentIndex()

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
            return None, None

        vPackage = list(response['releases'].keys())
        vPackage.sort(key=StrictVersion, reverse=True)

        verBeta = [x for x in vPackage if 'b' in x]
        verRelease = [x for x in vPackage if 'b' not in x and 'a' not in x]

        self.log.debug(f'Package Beta   : {verBeta[:10]}')
        self.log.debug(f'Package Release: {verRelease[:10]}')

        if self.ui.versionBeta.isChecked():
            finalPackage = verBeta[0]

        else:
            finalPackage = verRelease[0]

        comment = response['releases'][finalPackage][0]['comment_text']
        return finalPackage, comment

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

        availPackage, comment = self.versionPackage(packageName)

        if availPackage is None:
            self.app.message.emit('Failed get actual package from server', 2)
            return False

        self.ui.versionAvailable.setText(availPackage)
        self.ui.installVersion.setEnabled(True)

        if StrictVersion(availPackage) < StrictVersion(actPackage):
            return True

        t = 'A new version of MountWizzard is available!'
        self.app.message.emit(t, 1)

        if not self.ui.versionReleaseNotes.isChecked():
            return True
        if not comment:
            return True

        self.app.message.emit(f'Release notes for {availPackage}:', 1)
        for line in comment.split('\n'):
            self.app.message.emit(line, 0x100)
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
        self.log.debug(f'venv: [{status}], hasReal:[{hasReal}], hasBase:[{hasBase}]')
        self.log.debug(f'venv path: [{os.environ.get("VIRTUAL_ENV", "")}]')
        return status

    @staticmethod
    def formatPIP(line=''):
        """
        formatPIP shortens the stdout line for presenting it to the user. as the
        lines are really long, mw4 concentrates on package names and action.

        :param line:
        :return: formatted line
        """
        if line.startswith(' '):
            return ''

        elif line.startswith('Requirement'):
            val = line.split(':')
            prefix = val[0]
            packageName = val[1].split('<')[0].split('>')[0].split('=')[0].split(' ')[1]
            line = f'{prefix} : {packageName}'

        elif line.startswith('Collecting'):
            line = line.split('<')[0].split('>')[0].split('=')[0]

        elif line.startswith('Installing') or line.startswith('Building'):
            line = line.split(':')[0]

        else:
            line = line.split('\n')[0]

        return line

    @staticmethod
    def restartProgram():
        print("argv was", sys.argv)
        print("sys.executable was", sys.executable)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def runInstall(self, versionPackage='', timeout=60):
        """
        :param versionPackage:   package version to install
        :param timeout:
        :return: success
        """
        runnable = ['pip',
                    'install',
                    f'mountwizzard4=={versionPackage}',
                    '--disable-pip-version-check',
                    ]

        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            text=True,
                                            )
            for stdout_line in iter(self.process.stdout.readline, ""):
                line = self.formatPIP(line=stdout_line)
                if line:
                    self.app.message.emit(line, 0)

            output = self.process.communicate(timeout=timeout)[0]

        except subprocess.TimeoutExpired as e:
            self.log.error(e)
            return False, None

        except Exception as e:
            self.log.error(f'error: {e} happened')
            return False, None

        else:
            delta = time.time() - timeStart
            retCode = str(self.process.returncode)
            self.log.debug(f'pip install took {delta}s [{retCode}] [{output}]')

        success = (self.process.returncode == 0)
        return success, versionPackage

    def installFinished(self, result):
        """
        installFinished is called when the installation thread is finished. It
        writes the final messages to the user and resets the gui to default.

        :param result:
        :return: success
        """
        if isinstance(result, tuple):
            success, versionPackage = result
        else:
            success = False

        if success:
            self.app.message.emit(f'MountWizzard4 {versionPackage} installed', 1)
            packages = sorted(["%s==%s" % (i.key, i.version) for i in working_set])
            self.log.debug(f'After update:   {packages}')

        else:
            self.app.message.emit('Could not install update installation ', 2)

        self.mutexInstall.unlock()
        self.changeStyleDynamic(self.ui.installVersion, 'running', False)

        if not success:
            return False

        if self.ui.automaticRestart.isChecked():
            self.app.message.emit('...restarting', 1)
            self.restartProgram()
        return True

    def installVersion(self):
        """
        installVersion updates mw4 with the standard pip package installer.
        this is actually only tested and ok for running in a virtual environment.
        updates have to run only once at a time, so a mutex ensures this. If
        everything is ok, a thread it started doing the install work and a
        callback is defined when finished.

        as observation, installation on windows side takes for some reasons
        longer than in linux or osx environment. therefore an extended timeout is
        chosen.

        :return: True for test purpose
        """
        if pConf.isWindows:
            timeout = 180
        else:
            timeout = 90

        if not self.isVenv():
            self.app.message.emit('MW4 not running in an virtual environment', 2)
            return False

        if not self.mutexInstall.tryLock():
            self.app.message.emit('Install already running', 2)
            return False

        packages = sorted(["%s==%s" % (i.key, i.version) for i in working_set])
        self.log.debug(f'Before update:  {packages}')

        versionPackage = self.ui.versionAvailable.text()
        self.changeStyleDynamic(self.ui.installVersion, 'running', True)
        self.app.message.emit(f'Installing [{versionPackage}] please wait', 1)

        worker = tpool.Worker(self.runInstall,
                              versionPackage=versionPackage,
                              timeout=timeout)

        worker.signals.result.connect(self.installFinished)
        self.threadPool.start(worker)
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
        self.guiAudioList['ModelingFinished'] = self.ui.soundModelingFinished
        self.guiAudioList['ImageSaved'] = self.ui.soundImageSaved
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
            PyQt5.QtMultimedia.QSound.play(self.audioSignalsSet[sound])
            return True

        else:
            return False

    def pushTime(self):
        """
        :return:
        """
        timeJD = self.app.mount.obsSite.timeJD
        if timeJD is None:
            return False

        if platform.system() == 'Windows':
            timeText = timeJD.astimezone(tzlocal()).strftime('%H:%M:%S')
            runnable = ['time', f'{timeText}']

        elif platform.system() == 'Darwin':
            timeText = timeJD.astimezone(tzlocal()).strftime('%m%d%H%M%y')
            runnable = ['date', f'{timeText}']

        elif platform.system() == 'Linux':
            timeText = timeJD.astimezone(tzlocal()).strftime('%d-%b-%Y %H:%M:%S')
            runnable = ['date', '-s', f'"{timeText}"']

        else:
            runnable = ''

        t = timeJD.astimezone(tzlocal()).strftime('%H:%M:%S')
        self.app.message.emit(f'Set computer time to {t}', 0)
        self.log.debug(f'Command: {runnable}')

        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            shell=True,
                                            text=True
                                            )
            output = self.process.communicate(timeout=10)[0].replace('\n', '-')

        except subprocess.TimeoutExpired as e:
            self.log.error(e)
            return False

        except Exception as e:
            self.log.error(f'Time set error: {e}')
            return False

        else:
            retCode = str(self.process.returncode)
            self.log.debug(f'[{retCode}] [{output}]')

        return self.process.returncode == 0

    def pushTimeHourly(self):
        """
        :return:
        """
        isAuto = self.ui.autoPushTime.isChecked()
        if isAuto:
            self.pushTime()
            return True
        else:
            return False

    def toggleClockSync(self):
        """
        :return:
        """
        enableSync = self.ui.clockSync.isChecked()
        self.ui.syncTimePC2Mount.setEnabled(enableSync)
        self.ui.syncNotTracking.setEnabled(enableSync)
        self.ui.clockOffset.setEnabled(enableSync)
        self.ui.clockOffsetMS.setEnabled(enableSync)
        self.ui.timeDeltaPC2Mount.setEnabled(enableSync)
        if enableSync:
            self.app.mount.startClockTimer()
        else:
            self.app.mount.stopClockTimer()
        return True

    def syncClock(self):
        """
        :return:
        """
        doSync = self.ui.syncTimePC2Mount.isChecked()
        if not doSync:
            return False
        if not self.deviceStat['mount']:
            return False

        doSyncNotTrack = self.ui.syncNotTracking.isChecked()
        mountTracks = self.app.mount.obsSite.status in [0, 10]
        if doSyncNotTrack and mountTracks:
            return False

        delta = self.app.mount.obsSite.timeDiff * 1000
        if abs(delta) < 10:
            return False

        if delta > 999:
            delta = 999
        if delta < -999:
            delta = -999

        delta = int(delta)
        suc = self.app.mount.obsSite.adjustClock(delta)
        if not suc:
            self.app.message.emit('Cannot adjust mount clock', 2)
            return False

        self.app.message.emit(f'Mount clock corrected [{-delta}] ms', 0)
        return True

    def setVirtualStop(self):
        """
        :return:
        """
        isVirtual = self.ui.activateVirtualStop.isChecked()
        self.ui.statusOnline.setEnabled(not isVirtual)
        return True
