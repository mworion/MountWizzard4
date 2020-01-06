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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import time
import subprocess
import os
import sys
import platform
# external packages
import PyQt5
if platform.machine() != 'armv7l':
    import PyQt5.QtMultimedia
import requests
from importlib_metadata import version
# local import
from mw4.base.loggerMW import setCustomLoggingLevel
from mw4.base import tpool


class SettMisc(object):
    """
    the SettMisc window class handles the settings misc menu. all necessary processing
    for functions of that gui will be linked to this class.
    """

    def __init__(self):

        self.audioSignalsSet = dict()
        self.guiAudioList = dict()
        self.process = None
        self.mutexInstall = PyQt5.QtCore.QMutex()

        # setting functional signals
        self.app.mount.signals.firmwareDone.connect(self.updateFwGui)
        self.app.mount.signals.alert.connect(lambda: self.playSound('MountAlert'))
        self.app.dome.signals.slewFinished.connect(lambda: self.playSound('DomeSlew'))
        self.app.mount.signals.slewFinished.connect(lambda: self.playSound('MountSlew'))
        self.app.camera.signals.saved.connect(lambda: self.playSound('ImageSaved'))
        self.app.astrometry.signals.done.connect(lambda: self.playSound('ImageSolved'))

        # setting ui signals
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelInfo.clicked.connect(self.setLoggingLevel)
        self.ui.isOnline.clicked.connect(self.showUpdates)
        self.ui.isOnline.clicked.connect(self.setWeatherOnline)
        self.ui.versionAlpha.clicked.connect(self.showUpdates)
        self.ui.versionBeta.clicked.connect(self.showUpdates)
        self.ui.versionRelease.clicked.connect(self.showUpdates)
        self.ui.installVersion.clicked.connect(self.installVersion)

        # defining and loading all necessary audio files
        self.setupAudioSignals()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        self.ui.loglevelDeepDebug.setChecked(config.get('loglevelDeepDebug', True))
        self.ui.loglevelDebug.setChecked(config.get('loglevelDebug', True))
        self.ui.loglevelInfo.setChecked(config.get('loglevelInfo', False))
        self.setLoggingLevel()
        self.ui.isOnline.setChecked(config.get('isOnline', False))
        self.setWeatherOnline()
        self.setupAudioGui()
        self.ui.soundMountSlewFinished.setCurrentIndex(config.get('soundMountSlewFinished', 0))
        self.ui.soundDomeSlewFinished.setCurrentIndex(config.get('soundDomeSlewFinished', 0))
        self.ui.soundMountAlert.setCurrentIndex(config.get('soundMountAlert', 0))
        self.ui.soundModelingFinished.setCurrentIndex(config.get('soundModelingFinished', 0))
        self.ui.soundImageSaved.setCurrentIndex(config.get('soundImageSaved', 0))
        self.ui.soundImageSolved.setCurrentIndex(config.get('soundImageSolved', 0))

        self.showUpdates()

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        config['loglevelDeepDebug'] = self.ui.loglevelDeepDebug.isChecked()
        config['loglevelDebug'] = self.ui.loglevelDebug.isChecked()
        config['loglevelInfo'] = self.ui.loglevelInfo.isChecked()
        config['isOnline'] = self.ui.isOnline.isChecked()
        config['soundMountSlewFinished'] = self.ui.soundMountSlewFinished.currentIndex()
        config['soundDomeSlewFinished'] = self.ui.soundDomeSlewFinished.currentIndex()
        config['soundMountAlert'] = self.ui.soundMountAlert.currentIndex()
        config['soundModelingFinished'] = self.ui.soundModelingFinished.currentIndex()
        config['soundImageSaved'] = self.ui.soundImageSaved.currentIndex()
        config['soundImageSolved'] = self.ui.soundImageSolved.currentIndex()

        return True

    def setWeatherOnline(self):
        """
        setWeatherOnline set the flag inside the online weather class to the gui accordingly

        :return: success
        """

        weather = self.app.onlineWeather

        if not weather:
            return False

        weather.online = self.ui.isOnline.isChecked()

        return True

    def versionPackage(self, packageName):
        """
        versionPackage will look the package up in pypi.org website and parses the
        resulting versions. if you have an alpa or beta release found it returns the correct
        version for download an install.

        :param packageName:
        :return:
        """

        url = f'https://pypi.python.org/pypi/{packageName}/json'
        try:
            response = requests.get(url).json()
        except Exception as e:
            self.log.critical(f'Cannot determine package version: {e}')
            return None
        else:
            vPackage = reversed(list(response['releases'].keys()))

            if self.ui.versionBeta.isChecked():
                vPackage = [x for x in vPackage if 'b' in x]
            elif self.ui.versionAlpha.isChecked():
                vPackage = [x for x in vPackage if 'a' in x]
            else:
                vPackage = [x for x in vPackage if 'a' not in x and 'b' not in x]

            return vPackage[0]

    def showUpdates(self):
        """
        showUpdates compares the actual installed and running package with the one on the
        server. if you have a newer version available, mw4 will inform the user about it.

        :return: success
        """

        packageName = 'mountwizzard4'
        actPackage = version(packageName)
        self.ui.versionActual.setText(actPackage)

        if not self.ui.isOnline.isChecked():
            self.ui.versionAvailable.setText('Online connections are disabled!')
            self.ui.installVersion.setEnabled(False)
            return False

        availPackage = self.versionPackage(packageName)

        if availPackage is None:
            self.app.message.emit('Failed get actual package from server', 2)
            return False

        self.ui.versionAvailable.setText(availPackage)
        self.ui.installVersion.setEnabled(True)

        if availPackage > actPackage:
            self.app.message.emit('A new version of MountWizzard is available', 1)

        return True

    @staticmethod
    def isVenv():
        """
        detects if the actual package is running in a virtual environment

        :return: status
        """

        hasReal = hasattr(sys, 'real_prefix')
        hasBase = hasattr(sys, 'base_prefix')

        return hasReal or hasBase and sys.base_prefix != sys.prefix

    @staticmethod
    def formatPIP(line=''):
        """
        formatPIP shortens the stdout line for presenting it to the user. as the lines are
        really long, mw4 concentrates on package names and action.

        :param line:
        :return: formatted line
        """
        # lines with additional information are deleted
        if line.startswith(' '):
            return ''

        # shorten the string for packages
        elif line.startswith('Requirement'):
            val = line.split(':')
            prefix = val[0]
            packageName = val[1].split('<')[0].split('>')[0].split('=')[0].split(' ')[1]
            line = f'{prefix} : {packageName}'

        elif line.startswith('Collecting'):
            line = line.split('<')[0].split('>')[0].split('=')[0]

        elif line.startswith('Installing') or line.startswith('Building'):
            line = line.split(':')[0]

        elif line.startswith('Successfully'):
            line = line.split('\n')[0]

        return line

    def runInstall(self, versionPackage='', timeout=20):
        """
        runInstall enables the virtual environment and install via pip the desired
        package version

        :param versionPackage:   package version to install
        :param timeout:
        :return: success
        """

        runnable = ['pip',
                    'install',
                    f'mountwizzard4=={versionPackage}',
                    '--no-cache-dir',
                    '--disable-pip-version-check',
                    ]

        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True,
                                            )
            for stdout_line in iter(self.process.stdout.readline, ""):
                # nicely format text
                line = self.formatPIP(line=stdout_line)
                if line:
                    self.app.message.emit(line, 0)

            _, stderr = self.process.communicate(timeout=timeout)

        except subprocess.TimeoutExpired as e:
            self.log.critical(e)
            return False

        except Exception as e:
            self.log.critical(f'error: {e} happened')
            return False

        else:
            delta = time.time() - timeStart
            self.log.info(f'pip install took {delta}s return code: '
                          + str(self.process.returncode)
                          + ' stderr: '
                          + stderr.replace('\n', ' ')
                          )

        success = (self.process.returncode == 0)
        return success, versionPackage

    def installFinished(self, result):
        """
        installFinished is called when the installation thread is finished. It writes the
        final messages to the user and resets the gui to default.

        :param result:
        :return: success
        """

        if isinstance(result, tuple):
            success, versionPackage = result
        else:
            success = False

        if success:
            self.app.message.emit(f'MountWizzard4 {versionPackage} installed', 1)
            self.app.message.emit('Please restart to enable new version', 1)
        else:
            self.app.message.emit(f'Could not install update installation ', 2)
        self.mutexInstall.unlock()
        self.changeStyleDynamic(self.ui.installVersion, 'running', False)

        return success

    def installVersion(self):
        """
        installVersion updates mw4 with the standard pip package installer. this is
        actually only tested and ok for running in a virtual environment. updates have to run
        only once at a time, so a mutex ensures this. If everything is ok, a thread it
        started doing the install work and a callback is defined when finished.

        :return: True for test purpose
        """

        if not self.isVenv():
            self.app.message.emit('Not running in Virtual Environment', 2)
            return False

        if not self.mutexInstall.tryLock():
            self.app.message.emit('Install already running', 2)
            return False

        versionPackage = self.ui.versionAvailable.text()
        self.changeStyleDynamic(self.ui.installVersion, 'running', True)
        self.app.message.emit('Installing selected version ... please wait', 1)

        worker = tpool.Worker(self.runInstall,
                              versionPackage=versionPackage)

        worker.signals.result.connect(self.installFinished)
        self.threadPool.start(worker)

        return True

    def updateFwGui(self, fw):
        """
        updateFwGui write all firmware data to the gui.

        :return:    True if ok for testing
        """

        if fw.product is not None:
            self.ui.product.setText(fw.product)
        else:
            self.ui.product.setText('-')

        if fw.vString is not None:
            self.ui.vString.setText(fw.vString)
        else:
            self.ui.vString.setText('-')

        if fw.date is not None:
            self.ui.fwdate.setText(fw.date)
        else:
            self.ui.fwdate.setText('-')

        if fw.time is not None:
            self.ui.fwtime.setText(fw.time)
        else:
            self.ui.fwtime.setText('-')

        if fw.hardware is not None:
            self.ui.hardware.setText(fw.hardware)
        else:
            self.ui.hardware.setText('-')

        return True

    def setLoggingLevel(self):
        """
        Setting the log level according to the setting in the gui.

        :return: nothing
        """
        if self.ui.loglevelDeepDebug.isChecked():
            setCustomLoggingLevel('DEBUG')

        elif self.ui.loglevelDebug.isChecked():
            setCustomLoggingLevel('INFO')

        elif self.ui.loglevelInfo.isChecked():
            setCustomLoggingLevel('WARN')

    def setupAudioGui(self):
        """
        setupAudioGui populates the audio selection gui

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
        setupAudioSignals pre loads all know audio signals for events handling

        :return: True for test purpose
        """
        if platform.machine() == 'armv7l':
            return False

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
        else:
            return False

        return True
