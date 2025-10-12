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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock

# external packages
from PyQt5.QtWidgets import QPushButton, QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.mainWmixin.tabSett_Device import SettDevice
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    class Mixin(MWidget, SettDevice):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = {}
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SettDevice.__init__(self)

    window = Mixin()
    yield window
    window.threadPool.waitForDone(1000)


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
                suc = function.initConfig()
                assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.driversData['dome'] = {}
    suc = function.storeConfig()
    assert suc


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
    function.popupUi = Test()
    function.popupUi.ui.ok.clicked.connect(function.processPopupResults)
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
    function.popupUi = Test()
    function.popupUi.ui.ok.clicked.connect(function.processPopupResults)
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
    function.popupUi = Test()
    function.popupUi.ui.ok.clicked.connect(function.processPopupResults)
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
            suc = function.copyConfig('telescope', 'telescope')
            assert suc


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
            suc = function.copyConfig('telescope', 'indi')
            assert suc


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
            suc = function.copyConfig('telescope', 'test')
            assert suc


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
            suc = function.copyConfig('telescope', 'indi')
            assert suc
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
    function.drivers = {
        'cover': {
            'deviceType': 'cover'
        }
    }
    with mock.patch('gui.mainWmixin.tabSett_Device.DevicePopup',
                    return_value=Pop()):
        suc = function.callPopup('cover')
        assert suc


def test_returnDriver_1(function):
    sender = QWidget()
    searchDict = {}
    driver = function.returnDriver(sender, searchDict)
    assert driver == ''


def test_returnDriver_2(function):
    sender = QWidget()
    searchDict = {}
    driver = function.returnDriver(sender, searchDict, addKey='test')
    assert driver == ''


def test_dispatchPopup(function):
    def sender():
        return 'test'

    function.sender = sender

    with mock.patch.object(function,
                           'callPopup'):
        with mock.patch.object(function,
                               'returnDriver',
                               return_values='test'):
            suc = function.dispatchPopup()
            assert suc


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
    class Sender:
        @staticmethod
        def currentText():
            return 'device disabled'

    function.sender = Sender
    function.driversData = {
        'telescope': {
            'framework': 'indi',
        }
    }

    with mock.patch.object(function,
                           'returnDriver',
                           return_value='telescope'):
        with mock.patch.object(function,
                               'stopDriver'):
            with mock.patch.object(function,
                                   'startDriver'):
                suc = function.dispatchDriverDropdown()
                assert suc


def test_dispatchDriverDropdown_2(function):
    class Sender:
        @staticmethod
        def currentText():
            return 'astap - astap'

    function.sender = Sender
    function.driversData = {
        'telescope': {
            'framework': 'indi',
        }
    }

    with mock.patch.object(function,
                           'returnDriver',
                           return_value='telescope'):
        with mock.patch.object(function,
                               'stopDriver'):
            with mock.patch.object(function,
                                   'startDriver'):
                suc = function.dispatchDriverDropdown()
                assert suc


def test_scanValid_1(function):
    suc = function.scanValid()
    assert not suc


def test_scanValid_2(function):
    suc = function.scanValid('telescope')
    assert not suc


def test_scanValid_3(function):
    def sender():
        return function.drivers['telescope']['class'].signals

    function.sender = sender
    suc = function.scanValid('telescope', 'test')
    assert suc


def test_scanValid_4(function):
    def sender():
        return function.drivers['telescope']['class'].signals

    class Test:
        framework = ''

    function.sender = sender
    function.drivers['test'] = {'class': Test()}
    suc = function.scanValid('test', 'test')
    assert not suc


def test_scanValid_5(function):
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
