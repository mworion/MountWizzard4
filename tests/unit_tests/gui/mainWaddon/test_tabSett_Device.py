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
import pytest
from unittest import mock

# external packages
from PySide6.QtWidgets import QPushButton, QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabSett_Device import SettDevice
from gui.widgets.main_ui import Ui_MainWindow


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.threadPool = mainW.app.threadPool
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)

    window = SettDevice(mainW)
    yield window


def test_setDefaultData(function):
    config = {'camera': {}}
    function.setDefaultData('camera', config)


def test_loadDriversDataFromConfig_1(function):
    config = {}
    function.loadDriversDataFromConfig(config)


def test_loadDriversDataFromConfig_2(function):
    config = {'driversData': {'test': ''}}
    function.loadDriversDataFromConfig(config)


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    with mock.patch.object(function,
                           'setupDeviceGui'):
        with mock.patch.object(function,
                               'startDrivers'):
            with mock.patch.object(function,
                                   'loadDriversDataFromConfig'):
                function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_storeConfig_2(function):
    function.driversData['dome'] = {}
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_setupDeviceGui_1(function):
    function.driversData = {
        'telescope': {
            'framework': 'astap',
            'frameworks': {
                'astap': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                    'searchRadius': 30,
                    'appPath': 'test',
                },
            }
        }
    }
    suc = function.setupDeviceGui()
    assert suc


def test_setupDeviceGui_2(function):
    function.driversData = {
        'test': {
            'framework': 'astap',
            'frameworks': {
                'astap': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                    'searchRadius': 30,
                    'appPath': 'test',
                },
            }
        }
    }
    suc = function.setupDeviceGui()
    assert suc


def test_processPopupResults_1(function):
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {'driver': ''}
        ui = UI()

    function.driversData = {
        'telescope': {
            'framework': 'astap',
            'frameworks': {
                'astap': {
                    'deviceName': '',
                    'deviceList': ['test', 'test1'],
                    'searchRadius': 30,
                    'appPath': 'test',
                },
            }
        }
    }
    function.devicePopup = Test()
    function.devicePopup.ui.ok.clicked.connect(function.processPopupResults)
    suc = function.processPopupResults()
    assert not suc


def test_processPopupResults_2(function):
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {'driver': 'telescope',
                        'indiCopyConfig': True,
                        'alpacaCopyConfig': True,
        }
        ui = UI()

    function.driversData = {
        'telescope': {
            'framework': 'astap',
            'frameworks': {
                'astap': {
                    'deviceName': '',
                    'deviceList': ['test', 'test1'],
                    'searchRadius': 30,
                    'appPath': 'test',
                },
            }
        }
    }
    function.devicePopup = Test()
    function.devicePopup.ui.ok.clicked.connect(function.processPopupResults)
    with mock.patch.object(function,
                           'copyConfig'):
        suc = function.processPopupResults()
        assert not suc


def test_processPopupResults_3(function):
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {'driver': 'telescope'}
        ui = UI()

    function.driversData = {
        'telescope': {
            'framework': 'astap',
            'frameworks': {
                'astap': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                    'searchRadius': 30,
                    'appPath': 'test',
                },
            }
        }
    }
    function.devicePopup = Test()
    function.devicePopup.ui.ok.clicked.connect(function.processPopupResults)
    with mock.patch.object(function,
                           'stopDriver'):
        with mock.patch.object(function,
                               'startDriver'):
            suc = function.processPopupResults()
            assert suc


def test_copyConfig_1(function):
    function.driversData = {
        'telescope': {
            'framework': 'astap',
            'frameworks': {
                'astap': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                    'searchRadius': 30,
                    'appPath': 'test',
                },
            }
        }
    }
    with mock.patch.object(function,
                           'stopDriver'):
        with mock.patch.object(function,
                               'startDriver'):
            function.copyConfig('telescope', 'telescope')


def test_copyConfig_2(function):
    function.drivers['telescope']['class'].framework = 'indi'
    function.drivers['cover']['class'].framework = 'indi'
    function.driversData = {
        'telescope': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        },
        'cover': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        }

    }
    with mock.patch.object(function,
                           'stopDriver'):
        with mock.patch.object(function,
                               'startDriver'):
            function.copyConfig('telescope', 'indi')


def test_copyConfig_3(function):
    function.drivers['telescope']['class'].framework = 'indi'
    function.drivers['cover']['class'].framework = 'indi'
    function.driversData = {
        'telescope': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        },
        'cover': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        }

    }
    with mock.patch.object(function,
                           'stopDriver'):
        with mock.patch.object(function,
                               'startDriver'):
            function.copyConfig('telescope', 'test')


def test_copyConfig_4(function):
    function.drivers['telescope']['class'].framework = 'indi'
    function.drivers['cover']['class'].framework = 'indi'
    function.driversData = {
        'telescope': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                    'test': 1,
                },
            }
        },
        'cover': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                    'test': 2,
                },
            }
        }

    }
    with mock.patch.object(function,
                           'stopDriver'):
        with mock.patch.object(function,
                               'startDriver'):
            function.copyConfig('telescope', 'indi')
            assert function.driversData['cover']['frameworks']['indi']['test'] == 1


def test_callPopup_1(function):
    class Pop:
        class OK:
            class Clicked:
                class Connect:
                    @staticmethod
                    def connect(a):
                        return
                clicked = Connect()
            ok = Clicked()
        ui = OK()
    function.driversData = {
        'cover': {
        }
    }
    test = function.drivers
    function.drivers = {
        'cover': {
            'deviceType': 'cover'
        }
    }
    with mock.patch('gui.mainWaddon.tabSett_Device.DevicePopup',
                    return_value=Pop()):
        function.callPopup('cover')
    function.drivers = test


def test_stopDriver_1(function):
    suc = function.stopDriver('')
    assert not suc


def test_stopDriver_2(function):
    function.drivers['telescope']['class'].framework = None
    suc = function.stopDriver('telescope')
    assert not suc


def test_stopDriver_3(function):
    function.drivers['telescope']['class'].framework = 'indi'
    function.drivers['telescope']['class'].run['indi'].deviceName = 'indi'
    suc = function.stopDriver('telescope')
    assert suc


def test_stopDrivers(function):
    with mock.patch.object(function,
                           'stopDriver'):
        suc = function.stopDrivers()
        assert suc


def test_configDriver_1(function):
    suc = function.configDriver('')
    assert not suc


def test_configDriver_2(function):
    function.driversData = {
        'telescope': {
            'framework': '',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        }
    }
    suc = function.configDriver('telescope')
    assert not suc


def test_configDriver_3(function):
    function.driversData = {
        'telescope': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        }
    }
    suc = function.configDriver('telescope')
    assert suc


def test_startDriver_1(function):
    suc = function.startDriver()
    assert not suc


def test_startDriver_2(function):
    function.driversData = {
        'telescope': {
            'framework': '',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        }
    }
    suc = function.startDriver('telescope')
    assert not suc


def test_startDriver_3(function):
    function.driversData = {
        'telescope': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        }
    }
    with mock.patch.object(function,
                           'configDriver'):
        suc = function.startDriver('telescope', False)
        assert suc


def test_startDriver_4(function):
    function.driversData = {
        'telescope': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        }
    }
    with mock.patch.object(function,
                           'configDriver'):
        with mock.patch.object(function,
                               'configDriver'):
            suc = function.startDriver('telescope', True)
            assert suc


def test_startDrivers_1(function):
    function.driversData = {
        'telescope': {
            'framework': '',
            'frameworks': {
                'indi': {
                    'deviceName': 'astap',
                    'deviceList': ['test', 'test1'],
                },
            }
        }
    }
    suc = function.startDrivers()
    assert suc


def test_startDrivers_2(function):
    function.ui.autoConnectASCOM.setChecked(False)
    function.driversData = {
        'telescope': {
            'framework': 'ascom',
        }
    }
    with mock.patch.object(function,
                           'startDriver') as testMock:
        suc = function.startDrivers()
        assert suc
        assert testMock.call_args.kwargs.get('driver') == 'telescope'
        assert not testMock.call_args.kwargs.get('autoStart')


def test_startDrivers_3(function):
    function.ui.autoConnectASCOM.setChecked(True)
    function.driversData = {
        'telescope': {
            'framework': 'ascom',
        }
    }
    with mock.patch.object(function,
                           'startDriver') as testMock:
        suc = function.startDrivers()
        assert suc
        assert testMock.call_args.kwargs.get('driver') == 'telescope'
        assert testMock.call_args.kwargs.get('autoStart')


def test_startDrivers_4(function):
    function.ui.autoConnectASCOM.setChecked(False)
    function.driversData = {
        'telescope': {
            'framework': 'indi',
        }
    }
    with mock.patch.object(function,
                           'startDriver') as testMock:
        suc = function.startDrivers()
        assert suc
        assert testMock.call_args.kwargs.get('driver') == 'telescope'
        assert testMock.call_args.kwargs.get('autoStart')


def test_manualStopAllAscomDrivers_1(function):
    function.driversData = {
        'telescope': {
            'framework': 'ascom',
        }
    }
    with mock.patch.object(function,
                           'stopDriver'):
        suc = function.manualStopAllAscomDrivers()
        assert suc


def test_manualStartAllAscomDrivers_1(function):
    function.driversData = {
        'telescope': {
            'framework': 'ascom',
        }
    }
    with mock.patch.object(function,
                           'startDriver'):
        suc = function.manualStartAllAscomDrivers()
        assert suc


def test_dispatchDriverDropdown_1(function):
    function.driversData = {
        'telescope': {
            'framework': 'indi',
        }
    }
    function.drivers['telescope']['uiDropDown'].addItem('indi - test')
    with mock.patch.object(function,
                           'stopDriver'):
        with mock.patch.object(function,
                               'startDriver'):
            function.dispatchDriverDropdown('telescope')


def test_dispatchDriverDropdown_2(function):
    function.driversData = {
        'dome': {
            'framework': 'indi',
        }
    }
    function.drivers['dome']['uiDropDown'].addItem('device disabled')
    with mock.patch.object(function,
                           'stopDriver'):
        with mock.patch.object(function,
                               'startDriver'):
            function.dispatchDriverDropdown('dome')


def test_scanValid_1(function):
    suc = function.scanValid('telescope')
    assert not suc


def test_scanValid_2(function):
    def sender():
        return function.drivers['telescope']['class'].signals

    function.sender = sender
    suc = function.scanValid('telescope', 'test')
    assert suc


def test_scanValid_3(function):
    def sender():
        return function.drivers['telescope']['class'].signals

    class Test:
        framework = ''

    function.sender = sender
    function.drivers['test'] = {'class': Test()}
    suc = function.scanValid('test', 'test')
    assert not suc


def test_scanValid_4(function):
    def sender():
        return function.drivers['telescope']['class'].signals

    class Test1:
        deviceName = 'asdfg'

    class Test:
        framework = 'test'
        run = {'test': Test1()}

    function.sender = sender
    function.drivers['test'] = {'class': Test()}
    suc = function.scanValid('test', 'test')
    assert not suc


def test_serverDisconnected_1(function):
    def Sender():
        return function.drivers['filter']['class'].signals
    function.sender = Sender

    suc = function.serverDisconnected({})
    assert not suc


def test_serverDisconnected_2(function):
    def Sender():
        return function.drivers['filter']['class'].signals
    function.sender = Sender
    function.BACK_NORM = '#000000'

    suc = function.serverDisconnected({'dome': 1})
    assert suc


def test_deviceConnected_1(function):
    function.BACK_GREEN = '#000000'
    suc = function.deviceConnected('')
    assert not suc


def test_deviceConnected_2(function):
    function.driversData = {
        'filter': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'loadConfig': True
                }
            }
        }
    }

    def Sender():
        return function.drivers['filter']['class'].signals
    function.sender = Sender

    function.BACK_GREEN = '#000000'
    suc = function.deviceConnected('dome')
    assert suc


def test_deviceConnected_3(function):
    function.driversData = {
        'dome': {
            'framework': 'indi',
            'frameworks': {
                'indi': {
                    'loadConfig': True
                }
            }
        }
    }

    def Sender():
        return function.drivers['dome']['class'].signals
    function.sender = Sender

    function.BACK_GREEN = '#000000'
    suc = function.deviceConnected('dome')
    assert suc


def test_deviceDisconnected_1(function):
    suc = function.deviceDisconnected('')
    assert suc


def test_deviceDisconnected_2(function):
    def Sender():
        return function.drivers['filter']['class'].signals
    function.sender = Sender

    suc = function.deviceDisconnected('dome')
    assert suc
