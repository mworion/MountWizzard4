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
import json
import locale
import logging
import os
import platform
import socket
import sys
import traceback
import warnings

# the following lines should avoid errors messages from OLE Automation with PySide6
# see
# https://stackoverflow.com/questions/51284268/
#         windowscontext-oleinitialize-failed-com-error-0x80010106-rpc-e-changed-mode
# and https://github.com/pywinauto/pywinauto/issues/472
# order is important to set sys.coinit_flags = 2 before import pywinauto
warnings.filterwarnings('ignore', category=Warning, append=True)
sys.coinit_flags = 2

# external packages
import astropy
from PySide6.QtCore import QFile, QEvent, __version__, qVersion
from PySide6.QtGui import QMouseEvent, QIcon
from PySide6.QtWidgets import QRadioButton, QGroupBox, QCheckBox, QLineEdit
from PySide6.QtWidgets import QApplication, QTabBar, QComboBox, QPushButton
from importlib_metadata import version

# local import
from base.loggerMW import setupLogging
setupLogging()
from gui.utilities.splashScreen import SplashScreen
from mainApp import MountWizzard4
import resource.resources as res
res.qInitResources()
astropy.utils.iers.conf.auto_download = False
astropy.utils.data.conf.allow_internet = False
log = logging.getLogger()


class MyApp(QApplication):
    """
    MyApp implements a custom notify handler to log errors, when C++ classes
    and python wrapper in PySide6 environment mismatch. mostly this relates to the
    situation when a C++ object is already deleted, but the python wrapper still
    exists. so far I know that's the only chance to log this issues.

    in addition it writes mouse pressed and key pressed events in debug level
    to log including event and object name to be analysed the input methods.
    """

    log = logging.getLogger(__name__)

    def __init__(self, *argv):
        super().__init__(*argv)
        self.last = None

    def handleButtons(self, obj, returnValue):
        """
        :param obj:
        :param returnValue:
        :return:
        """
        if 'Window' in obj.objectName():
            return returnValue

        if isinstance(obj, QTabBar):
            self.log.ui(f'Click Tab     : [{obj.tabText(obj.currentIndex())}]')
        elif isinstance(obj, QComboBox):
            self.log.ui(f'Click DropDown: [{obj.objectName()}]')
        elif isinstance(obj, QPushButton):
            text = obj.objectName()
            if not text:
                text = f'Popup - {obj.text()}'
            self.log.ui(f'Click Button  : [{text}]')
        elif isinstance(obj, QRadioButton):
            self.log.ui(f'Click Radio   : [{obj.objectName()}]'
                        f', value: [{not obj.isChecked()}]')
        elif isinstance(obj, QGroupBox):
            self.log.ui(f'Click Group   : [{obj.objectName()}]'
                        f', value: [{not obj.isChecked()}]')
        elif isinstance(obj, QCheckBox):
            self.log.ui(f'Click Checkbox: [{obj.objectName()}]'
                        f', value: [{not obj.isChecked()}]')
        elif isinstance(obj, QLineEdit):
            self.log.ui(f'Click EditLine: [{obj.objectName()}]:{obj.text()}')
        else:
            if obj.objectName() not in ['qt_scrollarea_viewport',
                                        'QComboBoxPrivateContainerClassWindow',
                                        '']:
                self.log.ui(f'Click Object  : [{obj.objectName()}]')

        return returnValue

    def notify(self, obj, event):
        """
        notify is the replacement for the original notify method. This is done to
        catch all undefined exception (object already deleted in C++) before the
        app crashes and stores it to the app log file.

        :param obj:
        :param event:
        :return:
        """
        try:
            returnValue = QApplication.notify(self, obj, event)

        except Exception as e:
            self.log.critical('-' * 100)
            self.log.critical('Event: {0}'.format(event))
            self.log.critical('EventType: {0}'.format(event.type()))
            self.log.critical('Exception error in event loop: {0}'.format(e))
            self.log.critical('-' * 100)
            returnValue = False

        if not isinstance(event, QMouseEvent):
            return returnValue
        if not event.button():
            return returnValue
        if event.type() == QEvent.Type.MouseButtonRelease:
            return returnValue
        returnValue = self.handleButtons(obj, returnValue)
        return returnValue


def except_hook(typeException, valueException, tbackException):
    """
    except_hook implements a wrapper around except hook to log uncatched
    exceptions to the log file. so during user phase I get all the exceptions
    and logs catched in the file.

    :param typeException:
    :param valueException:
    :param tbackException:
    :return: nothing
    """
    result = traceback.format_exception(typeException, valueException, tbackException)
    log.critical('')
    log.critical('Logging an uncatched Exception')
    log.critical('')
    for i in range(0, len(result)):
        log.critical(result[i].replace('\n', ''))

    log.critical('')
    sys.__excepthook__(typeException, valueException, tbackException)


def setupWorkDirs(mwGlob):
    """
    setupWorkDirs defines the necessary work dirs and checks if they are
    writable

    :param mwGlob:
    :return: mwGlob
    """
    mwGlob['modeldata'] = '4.0'
    mwGlob['workDir'] = os.getcwd()
    mwGlob['configDir'] = mwGlob['workDir'] + '/config'
    mwGlob['dataDir'] = mwGlob['workDir'] + '/data'
    mwGlob['imageDir'] = mwGlob['workDir'] + '/image'
    mwGlob['tempDir'] = mwGlob['workDir'] + '/temp'
    mwGlob['modelDir'] = mwGlob['workDir'] + '/model'
    mwGlob['measureDir'] = mwGlob['workDir'] + '/measure'
    mwGlob['logDir'] = mwGlob['workDir'] + '/log'

    for dirPath in ['workDir', 'configDir', 'imageDir', 'dataDir',
                    'tempDir', 'modelDir', 'measureDir', 'logDir']:
        if not os.path.isdir(mwGlob[dirPath]):
            os.makedirs(mwGlob[dirPath])

        if not os.access(mwGlob[dirPath], os.W_OK):
            log.warning('no write access to {0}'.format(dirPath))

    return mwGlob


def checkIsAdmin():
    """
    :return:
    """
    if platform.system() == 'Windows':
        import ctypes
        try:
            state = ctypes.windll.shell32.IsUserAnAdmin() == 1
        except Exception as e:
            log.error(f'Check admin error: [{e}]')
            state = None
    else:
        try:
            state = os.getuid() == 0
        except Exception as e:
            log.error(f'Check admin error: [{e}]')
            state = None
    if state is None:
        return 'unknown'
    elif state:
        return 'yes'
    else:
        return 'no'


def writeSystemInfo(mwGlob=None):
    """
    writeSystemInfo print overview data to the log file at the beginning of
    the start

    :return: true for test purpose
    """
    log.header('-' * 100)
    log.header(f'mountwizzard4    : {version("mountwizzard4")}')
    log.header(f'platform         : {platform.system()}')
    log.header(f'sys.executable   : {sys.executable}')
    log.header(f'actual workdir   : {mwGlob["workDir"]}')
    log.header(f'machine          : {platform.machine()}')
    log.header(f'cpu              : {platform.processor()}')
    log.header(f'release          : {platform.release()}')
    log.header(f'python           : {platform.python_version()}')
    log.header(f'python runtime   : {platform.architecture()[0]}')
    log.header(f'PySide6 / Qt     : {__version__} / {qVersion()}')
    log.header(f'node / hostname  : {platform.node()} / {socket.gethostname()}')
    log.header(f'run as admin     : {checkIsAdmin()}')
    log.header('-' * 100)

    return True


def extractFile(filePath=None, file=None, fileTimeStamp=None):
    """
    :param filePath:
    :param file:
    :param fileTimeStamp:
    :return:
    """
    fileExist = os.path.isfile(filePath)
    if fileExist:
        mtime = os.stat(filePath).st_mtime
        overwrite = mtime < fileTimeStamp
    else:
        overwrite = False

    if overwrite:
        log.info(f'Writing new file: [{file}]')
        os.remove(filePath)
    else:
        log.info(f'Using existing: [{file}]')

    QFile.copy(f':/data/{file}', filePath)
    os.chmod(filePath, 0o666)
    return True


def extractDataFiles(mwGlob=None, splashW=None):
    """
    we have the necessary files for leap second, ephemeris and satellite already
    stored in the files system of the app. we bring them to the file system of
    the user, if they do not exist.

    :return: True fpr test purpose
    """
    if mwGlob is None:
        return False

    files = {
        'de440_mw4.bsp': 0,
        'CDFLeapSeconds.txt': 0,
        'tai-utc.dat': 0,
        'finals2000A.all': 0,
        'finals.data': 0,
    }

    content = QFile(':/data/content.txt')
    content.open(QFile.OpenModeFlag.ReadOnly)
    lines = content.readAll().data().decode().splitlines()
    content.close()
    for line in lines:
        name, date = line.split(' ')
        if name in files:
            files[name] = float(date)

    for file in files:
        if splashW is not None:
            splashW.showMessage('Loading {0}'.format(file))
        filePath = mwGlob['dataDir'] + '/' + file
        fileTimeStamp = files[file]
        extractFile(filePath=filePath, file=file, fileTimeStamp=fileTimeStamp)
    return True


def getWindowPos():
    """
    :return:
    """
    configDir = os.getcwd() + '/config'
    profile = os.path.normpath(configDir + '/profile')
    if not os.path.isfile(profile):
        return 0, 0

    with open(profile) as f:
        configName = f.readline()

    configFile = configDir + '/' + configName + '.cfg'
    configFile = os.path.normpath(configFile)
    if not os.path.isfile(configFile):
        return 0, 0

    with open(configFile) as f:
        try:
            data = json.load(f)
        except Exception:
            return 0, 0
        else:
            x = data['mainW'].get('winPosX', 0)
            y = data['mainW'].get('winPosY', 0)
            return x, y


def minimizeStartTerminal():
    """
    :return:
    """
    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)


def main():
    """
    main prepares the loading of mountwizzard application. it prepares a
    splash screen and handler the setup of the logger, bundle handling etc. in
    addition some information about the system are written into the logfile to be
    able to debug in different conditions the system environment.

    :return: nothing
    """
    locale.setlocale(locale.LC_ALL, '')
    app = MyApp(sys.argv)
    # app = QApplication(sys.argv)

    minimizeStartTerminal()

    x, y = getWindowPos()
    splashW = SplashScreen(application=app, x=x, y=y)
    splashW.showMessage('Start initialising')
    splashW.setValue(0)
    mwGlob = dict()
    mwGlob = setupWorkDirs(mwGlob)

    splashW.showMessage('Write system info to log')
    splashW.setValue(40)
    writeSystemInfo(mwGlob=mwGlob)

    splashW.showMessage('Loading star and time data')
    splashW.setValue(60)
    extractDataFiles(mwGlob=mwGlob, splashW=splashW)

    splashW.showMessage('Initialize Application')
    splashW.setValue(80)
    sys.excepthook = except_hook
    app.setWindowIcon(QIcon(':/icon/mw4.ico'))
    MountWizzard4(mwGlob=mwGlob, application=app)

    splashW.showMessage('Finishing loading')
    splashW.setValue(100)
    splashW.close()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
