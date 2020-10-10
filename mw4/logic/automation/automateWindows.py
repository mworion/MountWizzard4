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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import logging
import platform

# external packages
from PyQt5.QtCore import QObject
from pywinauto import Application, timings, findwindows, application
from pywinauto.controls.win32_controls import ButtonWrapper, EditWrapper
from winreg import OpenKey, CloseKey, EnumKey, EnumValue, HKEY_LOCAL_MACHINE, QueryInfoKey

# local imports
from base.loggerMW import CustomLogger


class AutomateWindows(QObject):
    __all__ = ['AutomateWindows',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    UPDATER_EXE = 'GmQCIv2.exe'
    UTC_1_FILE = 'finals.data'
    UTC_2_FILE = 'tai-utc.dat'

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool

        val = self.checkRegistrationKeys('10micron QCI')
        self.available, self.name, self.installPath = val
        self.updaterRunnable = self.installPath + self.UPDATER_EXE
        self.updater = None
        self.actualWorkDir = os.getcwd()

    @staticmethod
    def getRegistrationKeyPath():
        if platform.machine().endswith('64'):
            regPath = 'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'

        else:
            regPath = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'

        return regPath

    def checkRegistrationKeys(self, appSearchName):
        regPath = self.getRegistrationKeyPath()

        installPath = ''
        available = False
        name = ''

        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, regPath)
            for i in range(0, QueryInfoKey(key)[0]):
                nameKey = EnumKey(key, i)
                subkey = OpenKey(key, nameKey)

                for j in range(0, QueryInfoKey(subkey)[1]):
                    values = EnumValue(subkey, j)

                    if values[0] == 'DisplayName':
                        name = values[1]

                    if values[0] == 'InstallLocation':
                        installPath = values[1]

                if appSearchName in name:
                    available = True
                    CloseKey(subkey)
                    break

                else:
                    CloseKey(subkey)

            CloseKey(key)
            if not available:
                installPath = ''
                name = ''

        except Exception as e:
            self.logger.debug(f'Name: {name}, path: {installPath}, error: {e}')

        finally:
            return available, name, installPath

    def checkFloatingPointErrorWindow(self):
        try:
            dialog = timings.wait_until_passes(2, 0.2, lambda: findwindows.find_windows(title='GmQCIv2',
                                                                                        class_name='#32770')[0])
            winOK = self.updater.window(handle=dialog)
            winOK['OK'].click()

        except timings.TimeoutError:
            return True

        except Exception as e:
            self.logger.error(f'error{e}')
            return False

        else:
            return True

    def startUpdater(self):
        self.updater = Application(backend='win32')

        try:
            self.updater.start(self.installPath + self.UPDATER_EXE)

        except application.AppStartError:
            self.logger.error('Failed to start updater, please check!')
            return False

        else:
            suc = self.checkFloatingPointErrorWindow()
            return suc

    def clearUploadMenu(self):

        try:
            win = self.updater['10 micron control box update']
            win['next'].click()
            win['next'].click()
            ButtonWrapper(win['Control box firmware']).uncheck_by_click()

        except Exception as e:
            self.logger.error('error{0}'.format(e))
            return False

        ButtonWrapper(win['Orbital parameters of comets']).uncheck_by_click()
        ButtonWrapper(win['Orbital parameters of asteroids']).uncheck_by_click()
        ButtonWrapper(win['Orbital parameters of satellites']).uncheck_by_click()
        ButtonWrapper(win['UTC / Earth rotation data']).uncheck_by_click()

        return True

    def prepareUpdater(self):
        """

        :return:
        """

        self.updater = None
        os.chdir(os.path.dirname(self.installPath))

        suc = self.startUpdater()
        if not suc:
            os.chdir(self.actualWorkDir)
            return False

        suc = self.clearUploadMenu()
        if not suc:
            os.chdir(self.actualWorkDir)
            return False

    def doUploadAndCloseInstaller(self):
        win = self.updater['10 micron control box update']
        try:
            win['next'].click()
            win['next'].click()
            win['Update Now'].click()

        except Exception as e:
            self.logger.error(f'error{e}')
            return False

        try:
            dialog = timings.wait_until_passes(60, 0.5, lambda: findwindows.find_windows(title='Update completed',
                                                                                       class_name='#32770')[0])
            winOK = self.updater.window(handle=dialog)
            winOK['OK'].click()

        except Exception as e:
            self.logger.error('error{0}'.format(e))
            return False

        return True

    def uploadMPCData(self, comets=False):
        self.prepareUpdater()

        try:
            win = self.updater['10 micron control box update']
            if comets:
                ButtonWrapper(win['Orbital parameters of comets']).check_by_click()
                win['Edit...4'].click()
                popup = self.updater['Comet orbits']

            else:
                ButtonWrapper(win['Orbital parameters of asteroids']).check_by_click()
                win['Edit...3'].click()
                popup = self.updater['Asteroid orbits']

            popup['MPC file'].click()
            filedialog = self.updater['Dialog']
            EditWrapper(filedialog['Edit13']).set_text(self.installPath + 'minorPlanets.mpc')
            filedialog['Button16'].click()
            popup['Close'].click()

        except Exception as e:
            self.logger.error(f'error{e}')
            return False

        else:
            suc = self.doUploadAndCloseInstaller()
            return suc

        finally:
            os.chdir(self.actualWorkDir)

    def uploadEarthRotationData(self):
        self.prepareUpdater()

        try:
            win = self.updater['10 micron control box update']
            ButtonWrapper(win['UTC / Earth rotation data']).check_by_click()
            win['Edit...1'].click()
            popup = self.updater['UTC / Earth rotation data']
            popup['Import files...'].click()
            filedialog = self.updater['Open finals data']
            EditWrapper(filedialog['Edit13']).set_text(self.installPath + self.UTC_1_FILE)
            filedialog['Button16'].click()
            filedialog = self.updater['Open tai-utc.dat']
            EditWrapper(filedialog['Edit13']).set_text(self.installPath + self.UTC_2_FILE)
            filedialog['Button16'].click()
            fileOK = self.updater['UTC data']
            fileOK['OK'].click()

        except Exception as e:
            self.logger.error(f'error{e}')
            os.chdir(self.actualWorkDir)
            return False

        else:
            suc = self.doUploadAndCloseInstaller()
            return suc

        finally:
            os.chdir(self.actualWorkDir)

    def writeEarthRotationData(self):
        """

        :return:
        """

        return True

    def writeCometMPC(self, dataDict):
        """

        :param dataDict:
        :return:
        """

        return True

    def writeAstroidMPC(self, dataDict):
        """

        :param dataDict:
        :return:
        """

        return True


if __name__ == "__main__":
    from PyQt5.QtCore import QThreadPool

    class App:
        threadPool = QThreadPool()
        mwGlob = {'dataDir': 'c:/Users/astro/PycharmProjects/MountWizzard4/data'}

    a = AutomateWindows(App())
    a.uploadMPCData(comets=False)
