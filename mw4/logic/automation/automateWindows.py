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
# standard libraries
import os
import logging
import platform

# external packages
from PyQt5.QtCore import QObject
from pywinauto.findwindows import find_windows
from pywinauto import application
from pywinauto.application import AppStartError, Application, Timings
import pywinauto.controls.win32_controls as controls
import winreg
from winreg import HKEY_LOCAL_MACHINE

# local imports


class AutomateWindows(QObject):
    __all__ = ['AutomateWindows',
               ]

    log = logging.getLogger(__name__)

    UTC_1_FILE = 'finals.data'
    UTC_2a_FILE = 'CDFLeapSeconds.txt'
    UTC_2b_FILE = 'tai-utc.dat'

    COMET_FIELDS = [
        'Orbit_type',
        'Provisional_packed_desig',
        'Year_of_perihelion',
        'Month_of_perihelion',
        'Day_of_perihelion',
        'Perihelion_dist',
        'e',
        'Peri',
        'Node',
        'i',
        'Epoch_year',
        'Epoch_month',
        'Epoch_day',
        'H',
        'G',
        'Designation_and_name',
        'Ref'
    ]

    ASTEROID_FIELDS = [
        'H',
        'G',
        'Num_obs',
        'rms',
        'U',
        'Arc_years',
        'Perturbers',
        'Perturbers_2',
        'Principal_desig',
        'Epoch',
        'M',
        'Peri',
        'Node',
        'i',
        'e',
        'n',
        'a',
        'Ref',
        'Num_opps',
        'Computer',
        'Hex_flags',
        'Last_obs',
        'Tp',
        'Orbital_period',
        'Perihelion_dist',
        'Aphelion_dist',
        'Semilatus_rectum',
        'Synodic_period',
        'Orbit_type'
    ]

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.threadPool = app.threadPool

        self.installPath = ''
        self.name = ''
        self.available = False
        self.updaterApp = ''
        self.updaterAppList = ['tenmicron_v2.exe', 'GmQCIv2.exe']
        self.getAppSettings('10micron')
        self.updater = None
        self.actualWorkDir = os.getcwd()

    @staticmethod
    def getRegistryPath():
        """
        :return:
        """
        if platform.machine().endswith('64'):
            regPath = 'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
        else:
            regPath = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'

        return regPath

    @staticmethod
    def convertRegistryEntryToDict(subkey):
        """
        :param subkey:
        :return:
        """
        values = dict()

        for j in range(0, winreg.QueryInfoKey(subkey)[1]):
            values[winreg.EnumValue(subkey, j)[0]] = winreg.EnumValue(subkey, j)[1]

        return values

    def getValuesForNameKeyFromRegistry(self, nameKey):
        """
        :param nameKey:
        :return:
        """
        regPath = self.getRegistryPath()
        key = winreg.OpenKey(HKEY_LOCAL_MACHINE, regPath)
        subkey = winreg.OpenKey(key, nameKey)
        values = self.convertRegistryEntryToDict(subkey)
        winreg.CloseKey(subkey)
        winreg.CloseKey(key)

        return values

    @staticmethod
    def searchNameInRegistry(appName, key):
        """
        :param appName:
        :param key:
        :return:
        """
        nameKeys = []
        for i in range(0, winreg.QueryInfoKey(key)[0]):
            nameKey = winreg.EnumKey(key, i)
            if appName in nameKey:
                nameKeys.append(nameKey)
        return nameKeys

    def getNameKeyFromRegistry(self, appName):
        """
        :param appName:
        :return:
        """
        regPath = self.getRegistryPath()
        key = winreg.OpenKey(HKEY_LOCAL_MACHINE, regPath)
        nameKeys = self.searchNameInRegistry(appName, key)
        winreg.CloseKey(key)
        return nameKeys

    def checkRegistryNameKeys(self, winKey):
        """
        :param winKey:
        :return:
        """
        nameKeys = self.getNameKeyFromRegistry(winKey)
        for nameKey in nameKeys:
            values = self.getValuesForNameKeyFromRegistry(nameKey)
            path = values.get('InstallLocation', '')
            if 'Updater' in path:
                break
            t = f'Key tested: [{winKey}], values: [{values}]'
            self.log.debug(t)
        else:
            self.log.warning('No install location found')
            return '', {}
        return nameKey, values

    def findAppSetup(self, winKey):
        """
        :param winKey:
        :return:
        """
        nameKey, values = self.checkRegistryNameKeys(winKey)
        if not nameKey:
            return False, '', '', ''

        for updaterApp in self.updaterAppList:
            fullPath = f'{values["InstallLocation"]}/{updaterApp}'
            if os.path.isfile(fullPath):
                break
        else:
            t = f'No 10micron updater found in [{values["InstallLocation"]}]'
            self.log.warning(t)
            return False, '', '', ''

        name = values['DisplayName']
        installPath = values['InstallLocation']
        app = updaterApp
        return True, name, installPath, app

    def getAppSettings(self, winKey):
        """
        :param winKey:
        :return:
        """
        try:
            val = self.findAppSetup(winKey)
            self.available = val[0]
            self.name = val[1]
            self.installPath = val[2]
            self.updaterApp = val[3]
        except Exception as e:
            self.available = False
            self.installPath = ''
            self.name = ''
            self.updaterApp = ''
            self.log.debug(f'App settings error: [{e}]')
        return True

    def checkFloatingPointErrorWindow(self):
        """
        :return:
        """
        try:
            dialog = application.wait_until_passes(2,
                                                   0.2,
                                                   lambda: find_windows(title='GmQCIv2',
                                                                        class_name='#32770')[0])
            winOK = self.updater.window(handle=dialog)
            winOK['OK'].click()
        except application.TimeoutError:
            return True
        except Exception as e:
            self.log.error(f'Error: [{e}]')
            return False
        else:
            return True

    def startUpdater(self):
        """
        :return:
        """
        if platform.architecture()[0] == '32bit':
            self.updater = Application(backend='win32')
            self.log.info('Using 32Bit backend win32')
        else:
            self.updater = Application(backend='uia')
            self.log.info('Using 64Bit backend uia')
            Timings.slow()

        try:
            self.updater.start(self.installPath + self.updaterApp)
        except AppStartError as e:
            e = f'{e}'.replace('\n', '')
            self.log.error(f'Start error: [{e}]')
            self.log.error(f'Path: [{self.installPath}{self.updaterApp}]')
            return False
        except Exception as e:
            e = f'{e}'.replace('\n', '')
            self.log.error(f'General error: [{e}]')
            self.log.error(f'Path: [{self.installPath}{self.updaterApp}]')
            return False
        else:
            suc = self.checkFloatingPointErrorWindow()
            return suc

    def clearUploadMenuCommands(self):
        """
        :return:
        """
        win = self.updater['10 micron control box update']
        win['next'].click()
        win['next'].click()
        controls.ButtonWrapper(win['Control box firmware']).uncheck_by_click()
        controls.ButtonWrapper(win['Orbital parameters of comets']).uncheck_by_click()
        controls.ButtonWrapper(win['Orbital parameters of asteroids']).uncheck_by_click()
        controls.ButtonWrapper(win['Orbital parameters of satellites']).uncheck_by_click()
        controls.ButtonWrapper(win['UTC / Earth rotation data']).uncheck_by_click()
        return True

    def clearUploadMenu(self):
        """
        :return:
        """
        try:
            self.clearUploadMenuCommands()
        except Exception as e:
            self.log.error(f'Clear upload error: [{e}]')
            return False
        return True

    def prepareUpdater(self):
        """
        :return:
        """
        if not self.installPath:
            self.log.error(f'No updater available: {self.installPath}')
            return False

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

        return True

    def doUploadAndCloseInstallerCommands(self):
        """
        :return:
        """
        win = self.updater['10 micron control box update']
        win['next'].click()
        win['next'].click()
        win['Update Now'].click()
        return True

    def pressOK(self):
        """
        :return:
        """
        dialog = application.wait_until_passes(60,
                                               0.5,
                                               lambda: find_windows(title='Update completed',
                                                                    class_name='#32770')[0])
        winOK = self.updater.window(handle=dialog)
        winOK['OK'].click()

        return True

    def doUploadAndCloseInstaller(self):
        """
        :return:
        """
        try:
            self.doUploadAndCloseInstallerCommands()
            self.pressOK()
        except Exception as e:
            self.log.error(f'Upload and close error: {e}')
            return False

        return True

    @staticmethod
    def getIdentifiers(element):
        """
        :param element:
        :return:
        """
        return element._ctrl_identifiers()

    @staticmethod
    def dialogClick(element):
        """
        :param element:
        :return:
        """
        return element.child_window(title='Open', auto_id='1',
                                    control_type='Button').click()

    def uploadMPCDataCommands(self, comets=False):
        """
        :param comets:
        :return:
        """
        win = self.updater['10 micron control box update']
        self.log.debug(f'Updater win: [{self.getIdentifiers(win)}]')

        if comets:
            controls.ButtonWrapper(win['Orbital parameters of comets']).check_by_click()
            win['Edit...4'].click()
            popup = self.updater['Comet orbits']
        else:
            controls.ButtonWrapper(win['Orbital parameters of asteroids']).check_by_click()
            win['Edit...3'].click()
            popup = self.updater['Asteroid orbits']

        self.log.debug(f'Updater popup: [{self.getIdentifiers(popup)}]')

        popup['MPC file'].click()
        filedialog = self.updater['Open']
        self.log.debug(f'Updater filedialog: [{self.getIdentifiers(filedialog)}]')

        text = self.installPath + 'minorPlanets.mpc'
        controls.EditWrapper(filedialog['File &name:Edit']).set_edit_text(text)
        self.dialogClick(filedialog)
        popup['Close'].click()
        return True

    def uploadMPCData(self, comets=False):
        """
        :param comets:
        :return:
        """
        try:
            self.prepareUpdater()
            self.uploadMPCDataCommands(comets=comets)
        except Exception as e:
            self.log.error(f'Upload MPC data error: [{e}]')
            return False
        else:
            suc = self.doUploadAndCloseInstaller()
            return suc
        finally:
            os.chdir(self.actualWorkDir)

    def uploadEarthRotationDataCommands(self):
        """
        :return:
        """
        win = self.updater['10 micron control box update']
        self.log.debug(f'Updater win: [{self.getIdentifiers(win)}]')

        controls.ButtonWrapper(win['UTC / Earth rotation data']).check_by_click()
        win['Edit...1'].click()
        popup = self.updater['UTC / Earth rotation data']
        self.log.debug(f'Updater popup: [{self.getIdentifiers(popup)}]')

        popup['Import files...'].click()
        filedialog = self.updater['Open finals data']
        self.log.debug(f'Updater filedialog: [{self.getIdentifiers(filedialog)}]')

        text = self.installPath + self.UTC_1_FILE
        controls.EditWrapper(filedialog['File &name:Edit']).set_edit_text(text)
        self.dialogClick(filedialog)

        if self.updaterApp == 'tenmicron_v2.exe':
            text = self.installPath + self.UTC_2a_FILE
            filedialog = self.updater['Open CDFLeapSeconds.txt or tai-utc.dat']
        else:
            text = self.installPath + self.UTC_2b_FILE
            filedialog = self.updater['Open tai-utc.dat']

        controls.EditWrapper(filedialog['File &name:Edit']).set_edit_text(text)
        self.dialogClick(filedialog)
        fileOK = self.updater['UTC data']
        fileOK['OK'].click()
        return True

    def uploadEarthRotationData(self):
        """
        :return:
        """
        self.prepareUpdater()
        try:
            self.uploadEarthRotationDataCommands()
        except Exception as e:
            self.log.error(f'Upload earth rotation error: [{e}]')
            os.chdir(self.actualWorkDir)
            return False
        else:
            suc = self.doUploadAndCloseInstaller()
            return suc
        finally:
            os.chdir(self.actualWorkDir)

    def uploadTLEDataCommands(self):
        """
        :return:
        """
        win = self.updater['10 micron control box update']
        self.log.debug(f'Updater win: [{self.getIdentifiers(win)}]')

        controls.ButtonWrapper(win['Orbital parameters of satellites']).check_by_click()
        win['Edit...2'].click()
        popup = self.updater['Satellites orbits']
        self.log.debug(f'Updater popup: [{self.getIdentifiers(popup)}]')

        popup['Load from file'].click()
        filedialog = self.updater['Open']
        self.log.debug(f'Updater filedialog: [{self.getIdentifiers(filedialog)}]')

        text = self.installPath + 'satellites.tle'
        controls.EditWrapper(filedialog['File &name:Edit']).set_edit_text(text)
        self.dialogClick(filedialog)
        popup['Close'].click()
        return True

    def uploadTLEData(self):
        """
        :return:
        """
        self.prepareUpdater()
        try:
            self.uploadTLEDataCommands()
        except Exception as e:
            self.log.error(f'Upload TLE error: [{e}]')
            os.chdir(self.actualWorkDir)
            return False
        else:
            suc = self.doUploadAndCloseInstaller()
            return suc
        finally:
            os.chdir(self.actualWorkDir)
