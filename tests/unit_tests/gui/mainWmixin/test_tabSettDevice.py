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
from unittest import mock
import logging

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
from skyfield.api import wgs84

# local import
from gui.mainWmixin.tabSettDevice import SettDevice
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from logic.environment.sensorWeather import SensorWeather
from logic.environment.onlineWeather import OnlineWeather
from logic.environment.directWeather import DirectWeather
from logic.environment.weatherUPB import WeatherUPB
from logic.environment.skymeter import Skymeter
from logic.cover.cover import Cover
from logic.imaging.filter import Filter
from logic.imaging.camera import Camera
from logic.imaging.focuser import Focuser
from logic.dome.dome import Dome
from logic.powerswitch.pegasusUPB import PegasusUPB
from logic.telescope.telescope import Telescope
from logic.astrometry.astrometry import Astrometry
from logic.powerswitch.kmRelay import KMRelay
from logic.measure.measure import MeasureData
from logic.remote.remote import Remote


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        update1s = pyqtSignal()
        update10s = pyqtSignal()
        threadPool = QThreadPool()
        mwGlob = {'modelDir': 'tests/model',
                  'imageDir': 'tests/image',
                  'tempDir': 'tests/temp'}

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        sensorWeather = SensorWeather(app=Test1())
        onlineWeather = OnlineWeather(app=Test1())
        directWeather = DirectWeather(app=Test1())
        powerWeather = WeatherUPB(app=Test1())
        skymeter = Skymeter(app=Test1())
        cover = Cover(app=Test1())
        filter = Filter(app=Test1())
        camera = Camera(app=Test1())
        focuser = Focuser(app=Test1())
        dome = Dome(app=Test1())
        power = PegasusUPB(app=Test1())
        astrometry = Astrometry(app=Test1())
        relay = KMRelay()
        measure = MeasureData(app=Test1())
        remote = Remote(app=Test1())
        telescope = Telescope(app=Test1())

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettDevice(app=Test(), ui=ui,
                     clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.findIndexValue = MWidget().findIndexValue
    app.pos = MWidget().pos
    app.height = MWidget().height
    app.width = MWidget().width
    app.returnDriver = MWidget().returnDriver
    app.deviceStat = dict()
    app.log = logging.getLogger(__name__)
    app.threadPool = QThreadPool()
    app.config = dict()
    app.BACK_NORM = '#000000'
    app.BACK_GREEN = '#000000'
    app.driversData = {'camera': {}}

    qtbot.addWidget(app)

    yield

    app.threadPool.waitForDone(1000)


def test_checkStructureDriversData_1():
    config = {
        'driversData': {
            'cover': {}
        }
    }
    with mock.patch('deepdiff.DeepDiff', return_value={}):
        suc = app.checkStructureDriversData('cover', config)
        assert not suc


def test_checkStructureDriversData_2():
    class Test:
        defaultConfig = {}

    config = {
        'driversData': {
            'cover': {}
        }
    }
    app.drivers = {
        'cover': {
            'class': Test()
        }
    }
    with mock.patch('deepdiff.DeepDiff',
                    return_value={'dictionary_item_added'}):
        suc = app.checkStructureDriversData('cover', config)
        assert suc


def test_initConfig_1():
    app.config['mainW'] = {}
    with mock.patch.object(app,
                           'setupDeviceGui'):
        with mock.patch.object(app,
                               'startDrivers'):
            suc = app.initConfig()
            assert suc


def test_initConfig_2():
    app.drivers = {'cover': {}}
    app.app.config['mainW'] = {
        'driversData': {
            'cover': {}
        }
    }
    with mock.patch.object(app,
                           'setupDeviceGui'):
        with mock.patch.object(app,
                               'startDrivers'):
            with mock.patch.object(app,
                                   'checkStructureDriversData'):
                with mock.patch.object(app,
                                       'setDefaultData'):
                    suc = app.initConfig()
                    assert suc


def test_initConfig_3():
    app.drivers = {'cover': {}}
    app.app.config['mainW'] = {
        'driversData': {
            'camera': {}
        }
    }
    with mock.patch.object(app,
                           'setupDeviceGui'):
        with mock.patch.object(app,
                               'startDrivers'):
            with mock.patch.object(app,
                                   'checkStructureDriversData'):
                with mock.patch.object(app,
                                       'setDefaultData'):
                    suc = app.initConfig()
                    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_storeConfig_2():
    app.driversData['dome'] = {}
    suc = app.storeConfig()
    assert suc


def test_setupDeviceGui_1():
    app.driversData = {
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
    suc = app.setupDeviceGui()
    assert suc


def test_setupDeviceGui_2():
    app.driversData = {
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
    suc = app.setupDeviceGui()
    assert suc


def test_processPopupResults_1():
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {'driver': ''}
        ui = UI()

    app.driversData = {
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
    app.popupUi = Test()
    app.popupUi.ui.ok.clicked.connect(app.processPopupResults)
    suc = app.processPopupResults()
    assert not suc


def test_processPopupResults_2():
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {'driver': 'telescope',
                        'indiCopyConfig': True,
                        'alpacaCopyConfig': True,
        }
        ui = UI()

    app.driversData = {
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
    app.popupUi = Test()
    app.popupUi.ui.ok.clicked.connect(app.processPopupResults)
    with mock.patch.object(app,
                           'copyConfig'):
        suc = app.processPopupResults()
        assert not suc


def test_processPopupResults_3():
    class UI:
        ok = QPushButton()

    class Test:
        returnValues = {'driver': 'telescope'}
        ui = UI()

    app.driversData = {
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
    app.popupUi = Test()
    app.popupUi.ui.ok.clicked.connect(app.processPopupResults)
    with mock.patch.object(app,
                           'stopDriver'):
        with mock.patch.object(app,
                               'startDriver'):
            suc = app.processPopupResults()
            assert suc


def test_copyConfig_1():
    app.driversData = {
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
    with mock.patch.object(app,
                           'stopDriver'):
        with mock.patch.object(app,
                               'startDriver'):
            suc = app.copyConfig('telescope', 'telescope')
            assert suc


def test_copyConfig_2():
    app.drivers['telescope']['class'].framework = 'indi'
    app.drivers['cover']['class'].framework = 'indi'
    app.driversData = {
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
    with mock.patch.object(app,
                           'stopDriver'):
        with mock.patch.object(app,
                               'startDriver'):
            suc = app.copyConfig('telescope', 'indi')
            assert suc


def test_copyConfig_3():
    app.drivers['telescope']['class'].framework = 'indi'
    app.drivers['cover']['class'].framework = 'indi'
    app.driversData = {
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
    with mock.patch.object(app,
                           'stopDriver'):
        with mock.patch.object(app,
                               'startDriver'):
            suc = app.copyConfig('telescope', 'test')
            assert suc


def test_copyConfig_4():
    app.drivers['telescope']['class'].framework = 'indi'
    app.drivers['cover']['class'].framework = 'indi'
    app.driversData = {
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
    with mock.patch.object(app,
                           'stopDriver'):
        with mock.patch.object(app,
                               'startDriver'):
            suc = app.copyConfig('telescope', 'indi')
            assert suc
            assert app.driversData['cover']['frameworks']['indi']['test'] == 1


def test_callPopup_1():
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

    app.driversData = {
        'cover': {
        }
    }
    app.drivers = {
        'cover': {
            'deviceType': 'cover'
        }
    }
    with mock.patch('gui.mainWmixin.tabSettDevice.DevicePopup',
                    return_value=Pop()):
        suc = app.callPopup('cover')
        assert suc


def test_dispatchPopup():
    def sender():
        return 'test'

    app.sender = sender

    with mock.patch.object(app,
                           'callPopup'):
        with mock.patch.object(app,
                               'returnDriver',
                               return_values='test'):
            suc = app.dispatchPopup()
            assert suc


def test_stopDriver_1():
    suc = app.stopDriver('')
    assert not suc


def test_stopDriver_2():
    suc = app.stopDriver('telescope')
    assert not suc


def test_stopDriver_3():
    app.drivers['telescope']['class'].framework = 'indi'
    app.drivers['telescope']['class'].run['indi'].deviceName = 'indi'
    suc = app.stopDriver('telescope')
    assert suc


def test_stopDrivers():
    with mock.patch.object(app,
                           'stopDriver'):
        suc = app.stopDrivers()
        assert suc


def test_configDriver_1():
    suc = app.configDriver('')
    assert not suc


def test_configDriver_2():
    app.driversData = {
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
    suc = app.configDriver('telescope')
    assert not suc


def test_configDriver_3():
    app.driversData = {
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
    suc = app.configDriver('telescope')
    assert suc


def test_startDriver_1():
    suc = app.startDriver()
    assert not suc


def test_startDriver_2():
    app.driversData = {
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
    suc = app.startDriver('telescope')
    assert not suc


def test_startDriver_3():
    app.driversData = {
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
    with mock.patch.object(app,
                           'configDriver'):
        suc = app.startDriver('telescope', False)
        assert suc


def test_startDriver_3():
    app.driversData = {
        'telescope': {
            'framework': 'internal',
            }
    }
    with mock.patch.object(app,
                           'configDriver'):
        suc = app.startDriver('telescope')
        assert suc


def test_startDrivers_1():
    app.driversData = {
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
    suc = app.startDrivers()
    assert suc


def test_startDrivers_2():
    app.ui.checkASCOMAutoConnect.setChecked(False)
    app.driversData = {
        'telescope': {
            'framework': 'ascom',
        }
    }
    with mock.patch.object(app,
                           'startDriver') as testMock:
        suc = app.startDrivers()
        assert suc
        assert testMock.call_args.kwargs.get('driver') == 'telescope'
        assert not testMock.call_args.kwargs.get('autoStart')


def test_startDrivers_3():
    app.ui.checkASCOMAutoConnect.setChecked(True)
    app.driversData = {
        'telescope': {
            'framework': 'ascom',
        }
    }
    with mock.patch.object(app,
                           'startDriver') as testMock:
        suc = app.startDrivers()
        assert suc
        assert testMock.call_args.kwargs.get('driver') == 'telescope'
        assert testMock.call_args.kwargs.get('autoStart')


def test_startDrivers_4():
    app.ui.checkASCOMAutoConnect.setChecked(False)
    app.driversData = {
        'telescope': {
            'framework': 'indi',
        }
    }
    with mock.patch.object(app,
                           'startDriver') as testMock:
        suc = app.startDrivers()
        assert suc
        assert testMock.call_args.kwargs.get('driver') == 'telescope'
        assert testMock.call_args.kwargs.get('autoStart')


def test_manualStopAllAscomDrivers_1():
    app.driversData = {
        'telescope': {
            'framework': 'ascom',
        }
    }
    with mock.patch.object(app,
                           'stopDriver'):
        suc = app.manualStopAllAscomDrivers()
        assert suc


def test_manualStartAllAscomDrivers_1():
    app.driversData = {
        'telescope': {
            'framework': 'ascom',
        }
    }
    with mock.patch.object(app,
                           'startDriver'):
        suc = app.manualStartAllAscomDrivers()
        assert suc


def test_dispatchDriverDropdown_1():
    class Sender:
        @staticmethod
        def currentText():
            return 'device disabled'

    app.sender = Sender
    app.driversData = {
        'telescope': {
            'framework': 'indi',
        }
    }

    with mock.patch.object(app,
                           'returnDriver',
                           return_value='telescope'):
        with mock.patch.object(app,
                               'stopDriver'):
            with mock.patch.object(app,
                                   'startDriver'):
                suc = app.dispatchDriverDropdown()
                assert suc


def test_dispatchDriverDropdown_2():
    class Sender:
        @staticmethod
        def currentText():
            return 'astap - astap'

    app.sender = Sender
    app.driversData = {
        'telescope': {
            'framework': 'indi',
        }
    }

    with mock.patch.object(app,
                           'returnDriver',
                           return_value='telescope'):
        with mock.patch.object(app,
                               'stopDriver'):
            with mock.patch.object(app,
                                   'startDriver'):
                suc = app.dispatchDriverDropdown()
                assert suc


def test_scanValid_1():
    suc = app.scanValid()
    assert not suc


def test_scanValid_2():
    suc = app.scanValid('telescope')
    assert not suc


def test_scanValid_3():
    def sender():
        return app.drivers['telescope']['class'].signals

    app.sender = sender
    suc = app.scanValid('telescope', 'test')
    assert suc


def test_scanValid_4():
    def sender():
        return app.drivers['telescope']['class'].signals

    app.sender = sender
    suc = app.scanValid('onlineWeather', 'test')
    assert not suc


def test_scanValid_5():
    delattr(app.drivers['onlineWeather']['class'], 'signals')
    app.drivers['onlineWeather']['class'].framework = 'onlineWeather'
    suc = app.scanValid('onlineWeather', 'test')
    assert not suc


def test_serverDisconnected_1():
    def Sender():
        return app.drivers['filter']['class'].signals
    app.sender = Sender

    suc = app.serverDisconnected({})
    assert not suc


def test_serverDisconnected_2():
    def Sender():
        return app.drivers['filter']['class'].signals
    app.sender = Sender
    app.BACK_NORM = '#000000'

    suc = app.serverDisconnected({'dome': 1})
    assert suc


def test_deviceConnected_1():
    app.BACK_GREEN = '#000000'
    suc = app.deviceConnected('')
    assert not suc


def test_deviceConnected_2():
    def Sender():
        return app.drivers['filter']['class'].signals
    app.sender = Sender

    app.BACK_GREEN = '#000000'
    suc = app.deviceConnected('dome')
    assert suc


def test_deviceDisconnected_1():
    suc = app.deviceDisconnected('')
    assert suc


def test_deviceDisconnected_2():
    def Sender():
        return app.drivers['filter']['class'].signals
    app.sender = Sender

    suc = app.deviceDisconnected('dome')
    assert suc
