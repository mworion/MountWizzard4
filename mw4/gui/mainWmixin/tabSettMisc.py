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
# Python  v3.7.4
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
# external packages
import PyQt5.QtMultimedia
import requests
from importlib_metadata import version
# local import
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

        self.setupAudioSignals()

        # setting functional signals
        self.app.mount.signals.firmwareDone.connect(self.updateFwGui)
        self.app.mount.signals.alert.connect(self.playAudioMountAlert)
        self.app.dome.signals.slewFinished.connect(self.playAudioDomeSlewFinished)
        self.app.mount.signals.slewFinished.connect(self.playAudioMountSlewFinished)

        # setting ui signals
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelInfo.clicked.connect(self.setLoggingLevel)
        self.ui.isOnline.clicked.connect(self.showUpdates)
        self.ui.isOnline.clicked.connect(self.setWeatherOnline)
        self.ui.versionAlpha.clicked.connect(self.showUpdates)
        self.ui.versionBeta.clicked.connect(self.showUpdates)
        self.ui.versionRelease.clicked.connect(self.showUpdates)
        self.ui.installVersion.clicked.connect(self.installVersion)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
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
        config['loglevelDebug'] = self.ui.loglevelDebug.isChecked()
        config['loglevelInfo'] = self.ui.loglevelInfo.isChecked()
        config['isOnline'] = self.ui.isOnline.isChecked()
        config['soundMountSlewFinished'] = self.ui.soundMountSlewFinished.currentIndex()
        config['soundDomeSlewFinished'] = self.ui.soundDomeSlewFinished.currentIndex()
        config['soundMountAlert'] = self.ui.soundMountAlert.currentIndex()
        config['soundModelingFinished'] = self.ui.soundModelingFinished.currentIndex()

        return True

    def setWeatherOnline(self):
        """

        :return: success
        """

        weather = self.app.weather

        if not weather:
            return False

        weather.online = self.ui.isOnline.isChecked()

        return True

    def versionPackage(self, packageName):
        """

        :param packageName:
        :return:
        """

        url = f'https://pypi.python.org/pypi/{packageName}/json'
        try:
            response = requests.get(url).json()
        except Exception as e:
            self.logger.error(f'Cannot determine package version: {e}')
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

        :return: success
        """

        packageName = 'mountwizzard4'
        actPackage = version(packageName)
        self.ui.versionActual.setText(actPackage)
        if self.ui.isOnline.isChecked():
            availPackage = self.versionPackage(packageName)
            if availPackage is None:
                self.app.message.emit('Failed get package', 2)
                return False
            self.ui.versionAvailable.setText(availPackage)
            self.ui.installVersion.setEnabled(True)
            if availPackage > actPackage:
                self.app.message.emit('A new version of MountWizzard is available', 1)
            return True
        else:
            self.ui.versionAvailable.setText('not online')
            self.ui.installVersion.setEnabled(False)
            return False

    @staticmethod
    def isVenv():
        hasReal = hasattr(sys, 'real_prefix')
        hasBase = hasattr(sys, 'base_prefix')
        return hasReal or hasBase and sys.base_prefix != sys.prefix

    def runInstall(self, versionPackage='', timeout=10):
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
                    '--upgrade',
                    '--no-cache-dir',
                    ]

        timeStart = time.time()
        try:
            self.process = subprocess.Popen(args=runnable,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE
                                            )
            stdout, stderr = self.process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as e:
            self.logger.debug(e)
            return False
        except Exception as e:
            self.logger.error(f'error: {e} happened')
            return False
        else:
            delta = time.time() - timeStart
            self.logger.debug(f'astap took {delta}s return code: '
                              + str(self.process.returncode)
                              + ' stderr: '
                              + stderr.decode().replace('\n', ' ')
                              + ' stdout: '
                              + stdout.decode().replace('\n', ' ')
                              )

        success = (self.process.returncode == 0)
        return success, versionPackage

    def installFinished(self, result):
        """

        :param result:
        :return:
        """

        if isinstance(result, tuple):
            success, versionPackage = result
        else:
            success = False

        if success:
            self.app.message.emit(f'MountWizzard4 {versionPackage} installed', 1)
            self.app.message.emit('Please restart to enable new version', 1)
        else:
            self.app.message.emit(f'Could not install MountWizzard4 {versionPackage}', 2)
        self.mutexInstall.unlock()
        self.changeStyleDynamic(self.ui.installVersion, 'running', False)

        return success

    def installVersion(self):
        """

        :return: success
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

        if self.ui.loglevelDebug.isChecked():
            logging.getLogger().setLevel(logging.DEBUG)
            logging.getLogger('indibase').setLevel(logging.DEBUG)
            logging.getLogger('mountcontrol').setLevel(logging.DEBUG)
        elif self.ui.loglevelInfo.isChecked():
            logging.getLogger().setLevel(logging.INFO)
            logging.getLogger('indibase').setLevel(logging.INFO)
            logging.getLogger('mountcontrol').setLevel(logging.INFO)
        elif self.ui.loglevelWarning.isChecked():
            logging.getLogger().setLevel(logging.WARNING)
            logging.getLogger('indibase').setLevel(logging.WARNING)
            logging.getLogger('mountcontrol').setLevel(logging.WARNING)
        elif self.ui.loglevelError.isChecked():
            logging.getLogger().setLevel(logging.ERROR)
            logging.getLogger('indibase').setLevel(logging.ERROR)
            logging.getLogger('mountcontrol').setLevel(logging.ERROR)

    def setupAudioGui(self):
        """
        setupAudioGui populates the audio selection gui

        :return: True for test purpose
        """

        self.guiAudioList['MountSlew'] = self.ui.soundMountSlewFinished
        self.guiAudioList['DomeSlew'] = self.ui.soundDomeSlewFinished
        self.guiAudioList['MountAlert'] = self.ui.soundMountAlert
        self.guiAudioList['ModelingFinished'] = self.ui.soundModelingFinished

        for itemKey, itemValue in self.guiAudioList.items():
            self.guiAudioList[itemKey].addItem('None')
            self.guiAudioList[itemKey].addItem('Beep')
            self.guiAudioList[itemKey].addItem('Horn')
            self.guiAudioList[itemKey].addItem('Beep1')
            self.guiAudioList[itemKey].addItem('Alarm')
            self.guiAudioList[itemKey].addItem('Alert')
        return True

    def setupAudioSignals(self):
        """
        setupAudioSignals pre loads all know audio signals for events handling

        :return: True for test purpose
        """

        self.audioSignalsSet['Beep'] = PyQt5.QtMultimedia.QSound(':/beep.wav')
        self.audioSignalsSet['Alert'] = PyQt5.QtMultimedia.QSound(':/alert.wav')
        self.audioSignalsSet['Horn'] = PyQt5.QtMultimedia.QSound(':/horn.wav')
        self.audioSignalsSet['Beep1'] = PyQt5.QtMultimedia.QSound(':/beep1.wav')
        self.audioSignalsSet['Alarm'] = PyQt5.QtMultimedia.QSound(':/alarm.wav')
        return True

    def playAudioMountSlewFinished(self):
        """
        playAudioMountSlewFinished plays a defined sound if this events happens

        :return: success of playing sound
        """

        listEntry = self.guiAudioList.get('MountSlew', None)
        if listEntry is None:
            return False
        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            self.audioSignalsSet[sound].play()
        return True

    def playAudioDomeSlewFinished(self):
        """
        playAudioDomeSlewFinished plays a defined sound if this events happens

        :return: success of playing sound
        """

        listEntry = self.guiAudioList.get('DomeSlew', None)
        if listEntry is None:
            return False
        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            self.audioSignalsSet[sound].play()
        return True

    def playAudioMountAlert(self):
        """
        playAudioMountAlert plays a defined sound if this events happens

        :return: success of playing sound
        """

        listEntry = self.guiAudioList.get('MountAlert', None)
        if listEntry is None:
            return False
        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            self.audioSignalsSet[sound].play()
        return True

    def playAudioModelFinished(self):
        """
        playAudioModelFinished plays a defined sound if this events happens

        :return: success of playing sound
        """

        listEntry = self.guiAudioList.get('ModelingFinished', None)
        if listEntry is None:
            return False
        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            self.audioSignalsSet[sound].play()
        return True
