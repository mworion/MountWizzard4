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
import requests
import comtypes.client
from pywinauto import Application, timings, findwindows, application
from pywinauto.controls.win32_controls import ButtonWrapper, EditWrapper
from winreg import OpenKey, CloseKey, EnumKey, EnumValue, HKEY_LOCAL_MACHINE, QueryInfoKey

# local imports
from base.loggerMW import CustomLogger


class AutomationWindows(QObject):
    __all__ = ['AutomationWindows',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool

        self.appAvailable = False
        self.appName = ''
        self.appInstallPath = ''
        self.appExe = 'GmQCIv2.exe'

        self.checkApplication()
        self.TARGET_DIR = self.appInstallPath
        if self.TARGET_DIR == '':
            self.TARGET_DIR = os.getcwd()+'/config/'

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """

        config = self.app.config['mainW']
        config['checkFilterMPC'] = self.ui.checkFilterMPC.isChecked()
        config['filterExpressionMPC'] = self.ui.filterExpressionMPC.text()

    @staticmethod
    def getRegistrationKeyPath():
        """

        :return:
        """

        if platform.machine().endswith('64'):
            regPath = 'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'

        else:
            regPath = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'

        return regPath

    def checkRegistrationKeys(self, appSearchName):
        """

        :param appSearchName:
        :return:
        """

        regPath = self.getRegistrationKeyPath()

        appInstallPath = ''
        appInstalled = False
        appName = ''

        try:
            key = OpenKey(HKEY_LOCAL_MACHINE, regPath)
            for i in range(0, QueryInfoKey(key)[0]):
                nameKey = EnumKey(key, i)
                subkey = OpenKey(key, nameKey)
                for j in range(0, QueryInfoKey(subkey)[1]):
                    values = EnumValue(subkey, j)
                    if values[0] == 'DisplayName':
                        appName = values[1]
                    if values[0] == 'InstallLocation':
                        appInstallPath = values[1]
                if appSearchName in appName:
                    appInstalled = True
                    CloseKey(subkey)
                    break
                else:
                    CloseKey(subkey)
            CloseKey(key)
            if not appInstalled:
                appInstallPath = ''
                appName = ''
        except Exception as e:
            self.logger.debug('Name: {0}, Path: {1}, error: {2}'.format(appName, appInstallPath, e))
        finally:
            return appInstalled, appName, appInstallPath

    def checkApplication(self):
        self.appAvailable, self.appName, self.appInstallPath = self.app.checkRegistrationKeys('10micron QCI')
        if self.appAvailable:
            self.app.messageQueue.put('Found: {0}\n'.format(self.appName))
            self.logger.info('Name: {0}, Path: {1}'.format(self.appName, self.appInstallPath))
        else:
            self.logger.info('Application 10micron Updater  not found on computer')

    def filterFileMPC(self, directory, filename, expression, start, end):
        numberEntry = 0
        with open(directory + filename, 'r') as inFile, open(directory + 'filter.mpc', 'w') as outFile:
            for line in inFile:
                searchExp = expression.split(',')
                for exp in searchExp:
                    if line.find(exp, start, end) != -1:
                        outFile.write(line)
                        numberEntry += 1
        if numberEntry == 0:
            return False
        else:
            self.app.messageQueue.put('Found {0} target(s) in MPC file: {1}\n'.format(numberEntry, filename))
            self.logger.info('Found {0} target(s) in MPC file: {1}!'.format(numberEntry, filename))
            return True

    def downloadFile(self, url, filename):
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                numberOfChunks = 0
                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(128):
                        numberOfChunks += 1
                        f.write(chunk)
            self.app.messageQueue.put('Downloaded {0} Bytes\n'.format(128 * numberOfChunks))
        except Exception as e:
            self.logger.error('Download of {0} failed, error{1}'.format(url, e))
            self.app.messageQueue.put('#BRDownload Error {0}\n'.format(e))
        return

    def uploadMount(self):
        actual_work_dir = ''
        try:
            actual_work_dir = os.getcwd()
            os.chdir(os.path.dirname(self.appInstallPath))
            app = Application(backend='win32')
            app.start(self.appInstallPath + self.appExe)
            # timings.Timings.Slow()
        except application.AppStartError:
            self.logger.error('Failed to start updater, please check!')
            self.app.messageQueue.put('#BRFailed to start updater, please check\n')
            os.chdir(actual_work_dir)
            return
        try:
            dialog = timings.WaitUntilPasses(2, 0.2, lambda: findwindows.find_windows(title='GmQCIv2', class_name='#32770')[0])
            winOK = app.window_(handle=dialog)
            winOK['OK'].click()
        except timings.TimeoutError as e:
            self.logger.warning('No invalid floating point windows occurred - moving forward')
        except Exception as e:
            self.logger.error('error{0}'.format(e))
        finally:
            pass
        try:
            win = app['10 micron control box update']
            win['next'].click()
            win['next'].click()
            ButtonWrapper(win['Control box firmware']).UncheckByClick()
        except Exception as e:
            self.logger.error('error{0}'.format(e))
            self.app.messageQueue.put('#BRError in starting 10micron updater, please check\n')
            os.chdir(actual_work_dir)
            return
        ButtonWrapper(win['Orbital parameters of comets']).UncheckByClick()
        ButtonWrapper(win['Orbital parameters of asteroids']).UncheckByClick()
        ButtonWrapper(win['Orbital parameters of satellites']).UncheckByClick()
        ButtonWrapper(win['UTC / Earth rotation data']).UncheckByClick()
        try:
            uploadNecessary = False
            if self.app.ui.checkComets.isChecked():
                ButtonWrapper(win['Orbital parameters of comets']).CheckByClick()
                win['Edit...4'].click()
                popup = app['Comet orbits']
                popup['MPC file'].click()
                filedialog = app[self.OPENDIALOG]
                if self.app.ui.checkFilterMPC.isChecked():
                    if self.filterFileMPC(self.TARGET_DIR, self.COMETS_FILE, self.app.ui.le_filterExpressionMPC.text(), self.COMETS_START, self.COMETS_END):
                        uploadNecessary = True
                    EditWrapper(filedialog['Edit13']).SetText(self.TARGET_DIR + 'filter.mpc')
                else:
                    uploadNecessary = True
                    EditWrapper(filedialog['Edit13']).SetText(self.TARGET_DIR + self.COMETS_FILE)
                filedialog['Button16'].click()
                popup['Close'].click()
            else:
                ButtonWrapper(win['Orbital parameters of comets']).UncheckByClick()
            if self.app.ui.checkAsteroids.isChecked():
                ButtonWrapper(win['Orbital parameters of asteroids']).CheckByClick()
                win['Edit...3'].click()
                popup = app['Asteroid orbits']
                popup['MPC file'].click()
                filedialog = app[self.OPENDIALOG]
                if self.app.ui.checkFilterMPC.isChecked():
                    if self.filterFileMPC(self.TARGET_DIR, self.ASTEROIDS_FILE, self.app.ui.le_filterExpressionMPC.text(), self.ASTEROIDS_START, self.ASTEROIDS_END):
                        uploadNecessary = True
                    EditWrapper(filedialog['Edit13']).SetText(self.TARGET_DIR + 'filter.mpc')
                else:
                    uploadNecessary = True
                    EditWrapper(filedialog['Edit13']).SetText(self.TARGET_DIR + self.ASTEROIDS_FILE)
                filedialog['Button16'].click()
                popup['Close'].click()
            else:
                ButtonWrapper(win['Orbital parameters of asteroids']).UncheckByClick()
            if self.app.ui.checkTLE.isChecked():
                ButtonWrapper(win['Orbital parameters of satellites']).CheckByClick()
                win['Edit...2'].click()
                popup = app['Satellites orbits']
                popup['Load from file'].click()
                filedialog = app[self.OPENDIALOG]
                EditWrapper(filedialog['Edit13']).SetText(self.TARGET_DIR + self.SATBRIGHTEST_FILE)
                filedialog['Button16'].click()
                popup['Close'].click()
                uploadNecessary = True
            else:
                ButtonWrapper(win['Orbital parameters of satellites']).UncheckByClick()
            if self.app.ui.checkTLE.isChecked():
                ButtonWrapper(win['Orbital parameters of satellites']).CheckByClick()
                win['Edit...2'].click()
                popup = app['Satellites orbits']
                popup['Load from file'].click()
                filedialog = app[self.OPENDIALOG]
                EditWrapper(filedialog['Edit13']).SetText(self.TARGET_DIR + self.SPACESTATIONS_FILE)
                filedialog['Button16'].click()
                popup['Close'].click()
                uploadNecessary = True
            else:
                ButtonWrapper(win['Orbital parameters of satellites']).UncheckByClick()
            if self.app.ui.checkEarthrotation.isChecked():
                ButtonWrapper(win['UTC / Earth rotation data']).CheckByClick()
                win['Edit...1'].click()
                popup = app['UTC / Earth rotation data']
                popup['Import files...'].click()
                filedialog = app['Open finals data']
                EditWrapper(filedialog['Edit13']).SetText(self.TARGET_DIR + self.UTC_1_FILE)
                filedialog['Button16'].click()
                filedialog = app['Open tai-utc.dat']
                EditWrapper(filedialog['Edit13']).SetText(self.TARGET_DIR + self.UTC_2_FILE)
                filedialog['Button16'].click()
                fileOK = app['UTC data']
                fileOK['OK'].click()
                uploadNecessary = True
            else:
                ButtonWrapper(win['UTC / Earth rotation data']).UncheckByClick()
        except Exception as e:
            self.logger.error('error{0}'.format(e))
            self.app.messageQueue.put('#BRError in choosing upload files, please check 10micron updater\n')
            os.chdir(actual_work_dir)
            return
        if not self.app.workerMountDispatcher.mountStatus['Once']:
            self.app.messageQueue.put('Upload only possible with connected mount !')
            uploadNecessary = False
        if uploadNecessary:
            try:
                win['next'].click()
                win['next'].click()
                win['Update Now'].click()
            except Exception as e:
                self.logger.error('error{0}'.format(e))
                self.app.messageQueue.put('#BRError in uploading files, please check 10micron updater\n')
                os.chdir(actual_work_dir)
                return
            try:
                dialog = timings.WaitUntilPasses(60, 0.5, lambda: findwindows.find_windows(title='Update completed', class_name='#32770')[0])
                winOK = app.window_(handle=dialog)
                winOK['OK'].click()
            except Exception as e:
                self.logger.error('error{0}'.format(e))
                self.app.messageQueue.put('#BRError in closing 10micron updater, please check\n')
                os.chdir(actual_work_dir)
                return
        else:
            try:
                win['Cancel'].click()
                winOK = app['Exit updater']
                winOK['Yes'].click()
            except Exception as e:
                self.logger.error('error{0}'.format(e))
                self.app.messageQueue.put('#BRError in closing Updater, please check\n')
                os.chdir(actual_work_dir)
                return


if __name__ == "__main__":
    pass
