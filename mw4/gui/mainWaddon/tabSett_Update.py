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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import sys
import platform
from packaging.utils import Version

# external packages
import requests
import importlib_metadata
from astropy.utils import iers, data
import webbrowser

# local import
from base.loggerMW import setCustomLoggingLevel
from gui.utilities.toolsQtWidget import MWidget


class SettUpdate(MWidget):
    """
    """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.ui.loglevelTrace.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelStandard.clicked.connect(self.setLoggingLevel)
        self.ui.isOnline.clicked.connect(self.setWeatherOnline)
        self.ui.isOnline.clicked.connect(self.setSeeingOnline)
        self.ui.isOnline.clicked.connect(self.setupIERS)
        self.ui.versionBeta.clicked.connect(self.showUpdates)
        self.ui.versionRelease.clicked.connect(self.showUpdates)
        self.ui.versionReleaseNotes.clicked.connect(self.showUpdates)
        self.ui.isOnline.clicked.connect(self.showUpdates)
        self.ui.installVersion.clicked.connect(self.installVersion)
        self.ui.openPDF.clicked.connect(self.openPDF)

    def initConfig(self):
        """
        """
        config = self.app.config['mainW']
        self.ui.loglevelTrace.setChecked(config.get('loglevelTrace', False))
        self.ui.loglevelDebug.setChecked(config.get('loglevelDebug', True))
        self.ui.loglevelStandard.setChecked(config.get('loglevelStandard', False))
        self.ui.isOnline.setChecked(config.get('isOnline', False))
        self.ui.versionReleaseNotes.setChecked(
            config.get('versionReleaseNotes', True))

        self.setWeatherOnline()
        self.setSeeingOnline()
        self.setupIERS()
        self.showUpdates()
        return True

    def storeConfig(self):
        """
        """
        config = self.app.config['mainW']
        config['loglevelTrace'] = self.ui.loglevelTrace.isChecked()
        config['loglevelDebug'] = self.ui.loglevelDebug.isChecked()
        config['loglevelStandard'] = self.ui.loglevelStandard.isChecked()
        config['isOnline'] = self.ui.isOnline.isChecked()
        config['versionReleaseNotes'] = self.ui.versionReleaseNotes.isChecked()

    def setWeatherOnline(self):
        """
        """
        weather = self.app.onlineWeather
        if not weather:
            return False
        weather.online = self.ui.isOnline.isChecked()
        return True

    def setSeeingOnline(self):
        """
        """
        seeing = self.app.seeingWeather
        if not seeing:
            return False
        seeing.online = self.ui.isOnline.isChecked()
        return True

    def setupIERS(self):
        """
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
        isOnline = self.ui.isOnline.isChecked()

        if not isOnline:
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

    def checkNewLibNeeded(self, versionPackage):
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

        targetLib = response['info']['keywords'].split(',')[0]
        actLib = importlib_metadata.version('PySide6')
        self.log.debug(f'target: [{targetLib}], actual: [{actLib}]')
        return targetLib == actLib

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

        needNewLib = self.checkNewLibNeeded(versionPackage)
        if needNewLib is None:
            return False
        elif needNewLib:
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

    def openPDF(self):
        """
        :return:
        """
        url = 'https://mworion.github.io/MountWizzard4/'
        if not webbrowser.open(url, new=0):
            self.msg.emit(2, 'System', 'Setting Misc', 'Browser failed')
        else:
            self.msg.emit(0, 'System', 'Setting Misc', 'Doc opened')
        return True
