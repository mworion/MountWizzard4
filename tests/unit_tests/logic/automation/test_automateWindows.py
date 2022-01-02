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
import pytest
import os
import platform
from unittest import mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject
from skyfield.api import load

# local import
if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)

from logic.automation.automateWindows import AutomateWindows
from logic.automation import automateWindows
import winreg


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class MountObsSite:
        ts = load.timescale(builtin=True)

    class Mount:
        obsSite = MountObsSite()

    class Test(QObject):
        threadPool = QThreadPool()
        mount = Mount()
        mwGlob = {'tempDir': 'tests/workDir/temp',
                  'dataDir': 'tests/workDir/data',
                  }

    for file in ['tai-utc.dat', 'finals2000A.all']:
        path = 'tests/workDir/data/' + file
        if os.path.isfile(path):
            os.remove(path)

    window = AutomateWindows(app=Test())
    yield window


def test_getRegistrationKeyPath_1(function):
    with mock.patch.object(platform,
                           'machine',
                           return_value='64'):
        val = function.getRegistryPath()
        assert val == 'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'


def test_getRegistrationKeyPath_2(function):
    with mock.patch.object(platform,
                           'machine',
                           return_value='32'):
        val = function.getRegistryPath()
        assert val == 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'


def test_convertRegistryEntryToDict(function):
    with mock.patch.object(winreg,
                           'QueryInfoKey',
                           return_value=[0, 1]):
        with mock.patch.object(winreg,
                               'EnumValue',
                               return_value=['test', 'test']):
            val = function.convertRegistryEntryToDict('test')
            assert val


def test_getValuesForNameKeyFromRegistry_1(function):
    with mock.patch.object(function,
                           'getRegistryPath'):
        with mock.patch.object(winreg,
                               'OpenKey'):
            with mock.patch.object(function,
                                   'convertRegistryEntryToDict',
                                   return_value='test'):
                with mock.patch.object(winreg,
                                       'CloseKey'):
                    val = function.getValuesForNameKeyFromRegistry('test')
                    assert val == 'test'


def test_searchNameInRegistry_1(function):
    with mock.patch.object(winreg,
                           'QueryInfoKey',
                           return_value=[1]):
        with mock.patch.object(winreg,
                               'EnumKey',
                               return_value=['test']):
            val = function.searchNameInRegistry('test', 'test')
            assert val


def test_searchNameInRegistry_2(function):
    with mock.patch.object(winreg,
                           'QueryInfoKey',
                           return_value=[1]):
        with mock.patch.object(winreg,
                               'EnumKey',
                               return_value=['test']):
            val = function.searchNameInRegistry('none', 'none')
            assert not val


def test_getNameKeyFromRegistry_1(function):
    with mock.patch.object(function,
                           'getRegistryPath',
                           return_value='test'):
        with mock.patch.object(winreg,
                               'OpenKey',
                               return_value='test'):
            with mock.patch.object(function,
                                   'searchNameInRegistry',
                                   return_value='test'):
                with mock.patch.object(winreg,
                                       'CloseKey',
                                       return_value='test'):
                    val = function.getNameKeyFromRegistry('test')
                    assert val == 'test'


def test_checkRegistryNameKeys_1(function):
    with mock.patch.object(function,
                           'getNameKeyFromRegistry',
                           return_value=''):
        nameKey, values = function.checkRegistryNameKeys('')
        assert nameKey == ''
        assert values == {}


def test_checkRegistryNameKeys_2(function):
    with mock.patch.object(function,
                           'getNameKeyFromRegistry',
                           return_value=['test']):
        with mock.patch.object(function,
                               'getValuesForNameKeyFromRegistry',
                               return_value={}):
            nameKey, values = function.checkRegistryNameKeys('')
            assert nameKey == ''
            assert values == {}


def test_checkRegistryNameKeys_3(function):
    with mock.patch.object(function,
                           'getNameKeyFromRegistry',
                           return_value=['test']):
        with mock.patch.object(function,
                               'getValuesForNameKeyFromRegistry',
                               return_value={'DisplayName': 'test',
                                             'InstallLocation': 'test'}):
            nameKey, values = function.checkRegistryNameKeys('')
            assert nameKey == ''
            assert values == {}


def test_checkRegistryNameKeys_4(function):
    with mock.patch.object(function,
                           'getNameKeyFromRegistry',
                           return_value=['test']):
        with mock.patch.object(function,
                               'getValuesForNameKeyFromRegistry',
                               return_value={'DisplayName': 'none',
                                             'InstallLocation': 'Updater'}):
            nameKey, values = function.checkRegistryNameKeys('')
            assert nameKey == 'test'
            assert values == {'DisplayName': 'none', 'InstallLocation': 'Updater'}


def test_findAppSetup_1(function):
    with mock.patch.object(function,
                           'checkRegistryNameKeys',
                           return_value=('', {})):
        avail, name, path, exe = function.findAppSetup('appNames')
        assert not avail
        assert path == ''
        assert name == ''
        assert exe == ''


def test_findAppSetup_2(function):
    with mock.patch.object(function,
                           'checkRegistryNameKeys',
                           return_value=('test', {'DisplayName': 'Name',
                                                  'InstallLocation': 'Path'})):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=False):
            avail, name, path, exe = function.findAppSetup('appNames')
            assert not avail
            assert path == ''
            assert name == ''
            assert exe == ''


def test_findAppSetup_3(function):
    with mock.patch.object(function,
                           'checkRegistryNameKeys',
                           return_value=('test', {'DisplayName': 'Name',
                                                  'InstallLocation': 'Path'})):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=True):
            avail, name, path, exe = function.findAppSetup('appNames')
            assert avail
            assert path == 'Path'
            assert name == 'Name'
            assert exe == 'tenmicron_v2.exe'


def test_getAppSettings_1(function):
    with mock.patch.object(function,
                           'findAppSetup',
                           return_value=(True, 'test', 'test', 'test.exe')):
        function.getAppSettings('test')
        assert function.available
        assert function.installPath == 'test'
        assert function.name == 'test'
        assert function.updaterApp == 'test.exe'


def test_getAppSettings_2(function):
    with mock.patch.object(function,
                           'findAppSetup',
                           return_value=(False, 'test', 'test', 'test.exe'),
                           side_effect=Exception()):
        appNames = {'10micron control': 'tenmicron_v2.exe'}
        function.getAppSettings(appNames)
        assert not function.available
        assert function.installPath == ''
        assert function.name == ''
        assert function.updaterApp == ''


def test_checkFloatingPointErrorWindow_1(function):
    class Test1:
        @staticmethod
        def click():
            pass

    class Test:
        @staticmethod
        def window(handle=None):
            return {'OK': Test1()}

    function.updater = Test()
    with mock.patch.object(automateWindows.application,
                           'wait_until_passes'):
        suc = function.checkFloatingPointErrorWindow()
        assert suc


def test_checkFloatingPointErrorWindow_2(function):
    class Test1:
        @staticmethod
        def click():
            pass

    class Test:
        @staticmethod
        def window(handle=None):
            return {'OK': Test1()}

    function.updater = Test()
    with mock.patch.object(automateWindows.application,
                           'wait_until_passes',
                           side_effect=Exception):
        suc = function.checkFloatingPointErrorWindow()
        assert not suc


def test_checkFloatingPointErrorWindow_3(function):
    class Test1:
        @staticmethod
        def click():
            pass

    class Test:
        @staticmethod
        def window(handle=None):
            return {'OK': Test1()}

    function.updater = Test()
    with mock.patch.object(automateWindows.application,
                           'wait_until_passes',
                           side_effect=automateWindows.application.TimeoutError):
        suc = function.checkFloatingPointErrorWindow()
        assert suc


def test_startUpdater_1(function):
    class Test:
        @staticmethod
        def start(a):
            pass

    with mock.patch.object(platform,
                           'architecture',
                           return_value=['32bit']):
        with mock.patch.object(automateWindows,
                               'Application',
                               return_value=Test()):
            with mock.patch.object(Test,
                                   'start',
                                   side_effect=automateWindows.AppStartError()):
                suc = function.startUpdater()
                assert not suc


def test_startUpdater_2(function):
    class Test:
        @staticmethod
        def start(a):
            pass

    with mock.patch.object(platform,
                           'architecture',
                           return_value=['64bit']):
        with mock.patch.object(automateWindows,
                               'Application',
                               return_value=Test()):
            with mock.patch.object(Test,
                                   'start',
                                   side_effect=Exception()):
                suc = function.startUpdater()
                assert not suc


def test_startUpdater_3(function):
    class Test:
        @staticmethod
        def start(a):
            pass

    with mock.patch.object(automateWindows,
                           'Application',
                           return_value=Test()):
        with mock.patch.object(function,
                               'checkFloatingPointErrorWindow'):
            suc = function.startUpdater()
            assert suc


def test_clearUploadMenuCommands(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def uncheck_by_click():
            pass

    win = {'next': Test(),
           'Control box firmware': Test(),
           'Orbital parameters of comets': Test(),
           'Orbital parameters of asteroids': Test(),
           'Orbital parameters of satellites': Test(),
           'UTC / Earth rotation data': Test()
           }
    function.updater = {'10 micron control box update': win}
    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(function,
                               'moveWindow'):
            suc = function.clearUploadMenuCommands()
            assert suc


def test_clearUploadMenu_1(function):
    with mock.patch.object(function,
                           'clearUploadMenuCommands'):
        suc = function.clearUploadMenu()
        assert suc


def test_clearUploadMenu_2(function):
    with mock.patch.object(function,
                           'clearUploadMenuCommands',
                           side_effect=Exception()):
        suc = function.clearUploadMenu()
        assert not suc


def test_prepareUpdater_0(function):
    function.installPath = ''
    with mock.patch.object(os,
                           'chdir'):
        with mock.patch.object(function,
                               'startUpdater',
                               return_value=False):
            suc = function.prepareUpdater()
            assert not suc


def test_prepareUpdater_1(function):
    function.installPath = 'test'
    with mock.patch.object(os,
                           'chdir'):
        with mock.patch.object(function,
                               'startUpdater',
                               return_value=False):
            suc = function.prepareUpdater()
            assert not suc


def test_prepareUpdater_2(function):
    function.installPath = 'test'
    with mock.patch.object(os,
                           'chdir'):
        with mock.patch.object(function,
                               'startUpdater',
                               return_value=True):
            with mock.patch.object(function,
                                   'clearUploadMenu',
                                   return_value=False):
                suc = function.prepareUpdater()
                assert not suc


def test_prepareUpdater_3(function):
    function.installPath = 'test'
    with mock.patch.object(os,
                           'chdir'):
        with mock.patch.object(function,
                               'startUpdater',
                               return_value=True):
            with mock.patch.object(function,
                                   'clearUploadMenu',
                                   return_value=True):
                suc = function.prepareUpdater()
                assert suc


def test_doUploadAndCloseInstallerCommands(function):
    class Test:
        @staticmethod
        def click():
            pass

    win = {'next': Test(),
           'Update Now': Test(),
           'OK': Test()
           }

    class Timings:
        @staticmethod
        def wait_until_passes():
            return

    if not hasattr(automateWindows, 'timings'):
        automateWindows.timings = Timings()

    function.updater = {'10 micron control box update': win}
    with mock.patch.object(automateWindows.timings,
                           'wait_until_passes'):
        with mock.patch.object(function,
                               'moveWindow'):
            suc = function.doUploadAndCloseInstallerCommands()
            assert suc


def test_pressOK(function):
    class Test1:
        @staticmethod
        def click():
            pass

    class Test:
        @staticmethod
        def window(handle=None):
            return {'OK': Test1()}

    class Timings:
        @staticmethod
        def wait_until_passes():
            return

    if not hasattr(automateWindows, 'timings'):
        automateWindows.timings = Timings()

    function.updater = Test()
    with mock.patch.object(automateWindows.application,
                           'wait_until_passes'):
        with mock.patch.object(function,
                               'moveWindow'):
            suc = function.pressOK()
            assert suc


def test_doUploadAndCloseInstaller_1(function):
    with mock.patch.object(function,
                           'doUploadAndCloseInstallerCommands'):
        with mock.patch.object(function,
                               'pressOK'):
            suc = function.doUploadAndCloseInstaller()
            assert suc


def test_doUploadAndCloseInstaller_2(function):
    with mock.patch.object(function,
                           'doUploadAndCloseInstallerCommands'):
        with mock.patch.object(function,
                               'pressOK',
                               side_effect=Exception()):
            suc = function.doUploadAndCloseInstaller()
            assert not suc

            
def test_moveWindow_1(function):
    class Move:
        @staticmethod
        def Move(a, b):
            pass

    class Iface:
        iface_transform = Move()

    class Element:
        @staticmethod
        def wrapper_object():
            return Iface()
        
    suc = function.moveWindow(Element(), 0, 0)
    assert suc


def test_getIdentifiers(function):
    class Test:
        @staticmethod
        def _ctrl_identifiers():
            pass

    function.getIdentifiers(Test())


def test_dialogInput(function):
    class Type_Keys:
        @staticmethod
        def type_keys(a, with_spaces=False):
            pass

    class Element:
        @staticmethod
        def wrapper_object():
            return Type_Keys()

    function.dialogInput(Element(), 'text')


def test_findFileDialogWindow_1(function):
    class Win:
        @staticmethod
        def window_text():
            return 'test'

    class Updater:
        @staticmethod
        def windows():
            return [Win()]

    function.updater = Updater()
    val = function.findFileDialogWindow('test')
    assert val


def test_findFileDialogWindow_2(function):
    class Win:
        @staticmethod
        def window_text():
            return 'other'

    class Updater:
        @staticmethod
        def windows():
            return [Win()]

    function.updater = Updater()
    val = function.findFileDialogWindow('test')
    assert val


def test_uploadMPCDataCommands_1(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def wait(a):
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    win = {'Orbital parameters of comets': Test(),
           'Orbital parameters of asteroids': Test(),
           'Edit...4': Test(),
           'Edit...3': Test(),
           }
    popup = {'MPC file': Test(),
             'Close': Test(),
             }
    dialog = {'OpenButton4': Test(),
              'Button16': Test(),
              'File &name:Edit': Test(),
              'Look in:': Test(),
              }
    function.updater = {'10 micron control box update': win,
                        'Asteroid orbits': popup,
                        'Comet orbits': popup,
                        'Open': dialog,
                        }
    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(automateWindows.controls,
                               'EditWrapper'):
            with mock.patch.object(function,
                                   'getIdentifiers'):
                with mock.patch.object(function,
                                       'moveWindow'):
                    with mock.patch.object(function,
                                           'dialogInput'):
                        with mock.patch.object(function,
                                               'findFileDialogWindow',
                                               return_value='Open'):
                            suc = function.uploadMPCDataCommands()
                        assert suc


def test_uploadMPCDataCommands_2(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def wait(a):
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    win = {'Orbital parameters of comets': Test(),
           'Orbital parameters of asteroids': Test(),
           'Edit...4': Test(),
           'Edit...3': Test(),
           }
    popup = {'MPC file': Test(),
             'Close': Test(),
             }
    dialog = {'OpenButton4': Test(),
              'Button16': Test(),
              'File &name:Edit': Test(),
              'Look in:': Test(),
              }
    function.updater = {'10 micron control box update': win,
                        'Asteroid orbits': popup,
                        'Comet orbits': popup,
                        'Open': dialog,
                        }
    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(automateWindows.controls,
                               'EditWrapper'):
            with mock.patch.object(function,
                                   'getIdentifiers'):
                with mock.patch.object(function,
                                       'moveWindow'):
                    with mock.patch.object(function,
                                           'dialogInput'):
                        with mock.patch.object(function,
                                               'findFileDialogWindow',
                                               return_value='Open'):
                            suc = function.uploadMPCDataCommands(comets=True)
                            assert suc


def test_uploadMPCDataCommands_3(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def wait(a):
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    win = {'Orbital parameters of comets': Test(),
           'Orbital parameters of asteroids': Test(),
           'Edit...4': Test(),
           'Edit...3': Test(),
           }
    popup = {'MPC file': Test(),
             'Close': Test(),
             }
    dialog = {'OpenButton4': Test(),
              'Button16': Test(),
              'File &name:Edit': Test(),
              'Look in:': Test(),
              }
    function.updater = {'10 micron control box update': win,
                        'Asteroid orbits': popup,
                        'Comet orbits': popup,
                        'Open': dialog,
                        }
    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(automateWindows.controls,
                               'EditWrapper'):
            with mock.patch.object(function,
                                   'findFileDialogWindow',
                                   return_value='Open'):
                with mock.patch.object(function,
                                       'getIdentifiers'):
                    with mock.patch.object(function,
                                           'moveWindow'):
                        with mock.patch.object(function,
                                               'dialogInput'):
                            suc = function.uploadMPCDataCommands(comets=True)
                            assert suc


def test_uploadMPCData_1(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadMPCDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=False):
                suc = function.uploadMPCData()
                assert not suc


def test_uploadMPCData_2(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadMPCDataCommands',
                               side_effect=Exception()):
            suc = function.uploadMPCData()
            assert not suc


def test_uploadMPCData_3(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadMPCDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=True):
                suc = function.uploadMPCData()
                assert suc


def test_uploadEarthRotationDataCommands_1(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def wait(a):
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    function.updaterApp = 'tenmicron.exe'
    win = {'UTC / Earth rotation data': Test(),
           'Edit...1': Test(),
           }
    popup = {'Import files...': Test()
             }
    dialog = {'OpenButton4': Test(),
              'Button16': Test(),
              'File &name:Edit': Test(),
              'Look in:': Test(),
              }
    ok = {'OK': Test()
          }
    function.updater = {'10 micron control box update': win,
                        'UTC / Earth rotation data': popup,
                        'Open finals data': dialog,
                        'Open tai-utc.dat': dialog,
                        'UTC data': ok
                        }
    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(automateWindows.controls,
                               'EditWrapper'):
            with mock.patch.object(function,
                                   'findFileDialogWindow',
                                   return_value='Open finals data'):
                with mock.patch.object(function,
                                       'getIdentifiers'):
                    with mock.patch.object(function,
                                           'moveWindow'):
                        with mock.patch.object(function,
                                               'dialogInput'):
                            suc = function.uploadEarthRotationDataCommands()
                            assert suc


def test_uploadEarthRotationDataCommands_2(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def wait(a):
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    function.updaterApp = 'tenmicron_v2.'
    win = {'UTC / Earth rotation data': Test(),
           'Edit...1': Test(),
           }
    popup = {'Import files...': Test()
             }
    dialog = {'OpenButton4': Test(),
              'Button16': Test(),
              'File &name:Edit': Test(),
              'Look in:': Test(),
              }
    ok = {'OK': Test()
          }
    function.updater = {'10 micron control box update': win,
                        'UTC / Earth rotation data': popup,
                        'Open finals data': dialog,
                        'Open tai-utc.dat': dialog,
                        'UTC data': ok
                        }
    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(automateWindows.controls,
                               'EditWrapper'):
            with mock.patch.object(function,
                                   'findFileDialogWindow',
                                   return_value='Open finals data'):
                with mock.patch.object(function,
                                       'getIdentifiers'):
                    with mock.patch.object(function,
                                           'moveWindow'):
                        with mock.patch.object(function,
                                               'dialogInput'):
                            suc = function.uploadEarthRotationDataCommands()
                            assert suc


def test_uploadEarthRotationDataCommands_3(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def wait(a):
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    function.updaterApp = 'tenmicron_v2.exe'
    win = {'UTC / Earth rotation data': Test(),
           'Edit...1': Test(),
           }
    popup = {'Import files...': Test()
             }
    dialog = {'OpenButton4': Test(),
              'Button16': Test(),
              'File &name:Edit': Test(),
              'Look in:': Test(),
              }
    ok = {'OK': Test()
          }
    function.updater = {'10 micron control box update': win,
                        'UTC / Earth rotation data': popup,
                        'Open finals data': dialog,
                        'Open CDFLeapSeconds.txt or tai-utc.dat': dialog,
                        'UTC data': ok
                        }
    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(automateWindows.controls,
                               'EditWrapper'):
            with mock.patch.object(function,
                                   'findFileDialogWindow',
                                   return_value='Open finals data'):
                with mock.patch.object(function,
                                       'getIdentifiers'):
                    with mock.patch.object(function,
                                           'moveWindow'):
                        with mock.patch.object(function,
                                               'dialogInput'):
                            suc = function.uploadEarthRotationDataCommands()
                            assert suc


def test_uploadEarthRotationData_1(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadEarthRotationDataCommands',
                               side_effect=Exception()):
            suc = function.uploadEarthRotationData()
            assert not suc


def test_uploadEarthRotationData_2(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadEarthRotationDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=False):
                suc = function.uploadEarthRotationData()
                assert not suc


def test_uploadEarthRotationData_3(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadEarthRotationDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=True):
                suc = function.uploadEarthRotationData()
                assert suc


def test_uploadTLEDataCommands_1(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def wait(a):
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    win = {'Orbital parameters of satellites': Test(),
           'Edit...2': Test(),
           }
    popup = {'Load from file': Test(),
             'Close': Test(),
             }
    dialog = {'OpenButton4': Test(),
              'Button16': Test(),
              'File &name:Edit': Test(),
              'Look in:': Test(),
              }
    function.updater = {'10 micron control box update': win,
                        'Satellites orbits': popup,
                        'Open': dialog,
                        }

    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(automateWindows.controls,
                               'EditWrapper'):
            with mock.patch.object(function,
                                   'findFileDialogWindow',
                                   return_value='Open'):
                with mock.patch.object(function,
                                       'getIdentifiers'):
                    with mock.patch.object(function,
                                           'moveWindow'):
                        with mock.patch.object(function,
                                               'dialogInput'):
                            suc = function.uploadTLEDataCommands()
                            assert suc


def test_uploadTLEDataCommands_2(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def wait(a):
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    win = {'Orbital parameters of satellites': Test(),
           'Edit...2': Test(),
           }
    popup = {'Load from file': Test(),
             'Close': Test(),
             }
    dialog = {'OpenButton4': Test(),
              'Button16': Test(),
              'File &name:Edit': Test(),
              'Look in:': Test(),
              }
    function.updater = {'10 micron control box update': win,
                        'Satellites orbits': popup,
                        'Open': dialog,
                        }

    with mock.patch.object(automateWindows.controls,
                           'ButtonWrapper'):
        with mock.patch.object(automateWindows.controls,
                               'EditWrapper'):
            with mock.patch.object(function,
                                   'findFileDialogWindow',
                                   return_value='Open'):
                with mock.patch.object(function,
                                       'getIdentifiers'):
                    with mock.patch.object(function,
                                           'moveWindow'):
                        with mock.patch.object(function,
                                               'dialogInput'):
                            suc = function.uploadTLEDataCommands()
                            assert suc


def test_uploadTLEData_1(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadTLEDataCommands',
                               side_effect=Exception()):
            suc = function.uploadTLEData()
            assert not suc


def test_uploadTLEData_2(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadTLEDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=False):
                suc = function.uploadTLEData()
                assert not suc


def test_uploadTLEData_3(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadTLEDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=True):
                suc = function.uploadTLEData()
                assert suc


def test_uploadTLEData_4(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadTLEDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=True):
                with mock.patch.object(platform,
                                       'architecture',
                                       return_value=['64bit']):
                    suc = function.uploadTLEData()
                    assert suc
