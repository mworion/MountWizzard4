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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import logging
# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
from skyfield.toposlib import Topos

# local import
from gui.mainWmixin.tabSettDevice import SettDevice
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.widget import MWidget
from logic.environment.sensorWeather import SensorWeather
from logic.environment.onlineWeather import OnlineWeather
from logic.environment.directWeather import DirectWeather
from logic.environment.skymeter import Skymeter
from logic.cover.flipflat import FlipFlat
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
from base.loggerMW import CustomLogger
from gui.extWindows.devicePopupW import DevicePopup


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
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        sensorWeather = SensorWeather(app=Test1())
        onlineWeather = OnlineWeather(app=Test1())
        directWeather = DirectWeather(app=Test1())
        skymeter = Skymeter(app=Test1())
        cover = FlipFlat(app=Test1())
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
    app.findIndexValue = MWidget.findIndexValue
    app.deviceStat = dict()
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()
    app.config = dict()
    app.BACK_NORM = '#000000'
    app.BACK_GREEN = '#000000'
    app.driversData = {'camera': {}}

    qtbot.addWidget(app)

    yield

    app.threadPool.waitForDone(1000)


def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_initConfig_2():
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
    suc = app.setupDeviceGui()
    assert suc


def test_setupDeviceGui_2():
    class Test:
        pass

    app.drivers['dome']['class'] = Test()
    suc = app.setupDeviceGui()
    assert suc


def test_processPopupResults_1():
    values = {'framework': 'alpaca',
              'copyAlpaca': True}

    app.app.camera.framework = 'alpaca'

    with mock.patch.object(app,
                           'dispatch'):
        suc = app.processPopupResults(driverSelected='camera',
                                      returnValues=values)
    assert suc


def test_processPopupResults_2():
    values = {'framework': 'indi',
              'copyIndi': True}

    app.app.camera.framework = 'indi'

    with mock.patch.object(app,
                           'dispatch'):
        suc = app.processPopupResults(driverSelected='camera',
                                      returnValues=values)
    assert suc


def test_processPopupResults_3():
    values = {'framework': 'alpaca',
              'copyAlpaca': True}

    app.app.camera.framework = 'indi'

    with mock.patch.object(app,
                           'dispatch'):
        suc = app.processPopupResults(driverSelected='camera',
                                      returnValues=values)
    assert suc


def test_processPopupResults_4():
    values = {'framework': 'indi',
              'copyIndi': True}

    app.app.camera.framework = 'alpaca'

    with mock.patch.object(app,
                           'dispatch'):
        suc = app.processPopupResults(driverSelected='camera',
                                      returnValues=values)
    assert suc


def test_setupPopUp_1():
    class Test1:
        @staticmethod
        def x():
            return 0

        @staticmethod
        def y():
            return 0

    def Sender():
        return ui.cameraSetup

    def default():
        return 0

    app.sender = Sender
    app.pos = Test1
    app.height = default
    app.width = default
    with mock.patch.object(app,
                           'processPopupResults'):
        with mock.patch.object(DevicePopup,
                               'exec_',
                               return_value=False):
            suc = app.setupPopup()
            assert not suc


def test_dispatchStopDriver_1():
    suc = app.dispatchStopDriver(driver='dome')
    assert suc


def test_dispatchStopDriver_2():
    app.drivers['dome']['uiDropDown'].setItemText(0, 'test')
    suc = app.dispatchStopDriver(driver='dome')
    assert suc


def test_dispatchStopDriver_3():
    app.drivers['dome']['class'].name = 'dome'
    suc = app.dispatchStopDriver(driver='dome')
    assert suc


def test_dispatchStopDriver_4():
    app.drivers['dome']['class'].name = 'dome'
    app.drivers['dome']['uiDropDown'].addItem('device disabled')
    suc = app.dispatchStopDriver(driver='dome')
    assert not suc


def test_stopAllDrivers():
    with mock.patch.object(app,
                           'dispatchStopDriver'):
        suc = app.stopDrivers()
        assert suc


def test_dispatchConfigDriver_1():
    suc = app.dispatchConfigDriver(driver=None)
    assert not suc


def test_dispatchConfigDriver_2():
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_3():
    app.drivers['dome']['uiDropDown'].setItemText(0, 'indi')
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_4():
    app.drivers['dome']['uiDropDown'].setItemText(0, 'alpaca')
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_5():
    app.drivers['dome']['deviceType'] = 'astrometry'
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_6():
    app.drivers['dome']['uiDropDown'].setItemText(0, 'test')
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_7():
    app.drivers['dome']['uiDropDown'].addItem('indi')
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_8():
    app.drivers['dome']['uiDropDown'].addItem('alpaca')
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_9():
    app.drivers['dome']['uiDropDown'].addItem('ascom')
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_10():
    app.drivers['dome']['uiDropDown'].addItem('astap')
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchConfigDriver_11():
    app.drivers['dome']['uiDropDown'].addItem('astrometry')
    suc = app.dispatchConfigDriver(driver='dome')
    assert suc


def test_dispatchStartDriver_1():
    suc = app.dispatchStartDriver(driver=None)
    assert not suc


def test_dispatchStartDriver_2():
    app.drivers['dome']['uiDropDown'].setItemText(0, 'internal')
    app.BACK_GREEN = '#000000'
    suc = app.dispatchStartDriver(driver='dome')
    assert not suc


def test_dispatchStartDriver_1(qtbot):
    suc = app.dispatchStartDriver()
    assert not suc


def test_dispatchStartDriver_2(qtbot):
    app.ui.relayDevice.addItem('internal')
    with mock.patch.object(app.app.relay,
                           'startCommunication',
                           return_value=False):
        suc = app.dispatchStartDriver(driver='relay')
        assert not suc


def test_dispatchStartDriver_3(qtbot):
    app.ui.relayDevice.addItem('test')
    with mock.patch.object(app.app.relay,
                           'startCommunication',
                           return_value=True):
        suc = app.dispatchStartDriver(driver='relay')
        assert suc


def test_dispatch_1(qtbot):
    with mock.patch.object(app,
                           'dispatchStopDriver',
                           return_value=True):
        with mock.patch.object(app,
                               'dispatchConfigDriver'):
            with mock.patch.object(app,
                                   'dispatchStartDriver'):
                suc = app.dispatch(driverName='test')
                assert suc


def test_dispatch_2(qtbot):
    def Sender():
        return ui.relayDevice
    app.sender = Sender

    with mock.patch.object(app,
                           'dispatchStopDriver',
                           return_value=True):
        with mock.patch.object(app,
                               'dispatchConfigDriver'):
            with mock.patch.object(app,
                                   'dispatchStartDriver'):
                suc = app.dispatch(driverName=None)
                assert suc


def test_dispatch_3(qtbot):
    def Sender():
        return ui.relayDevice
    app.sender = Sender

    with mock.patch.object(app,
                           'dispatchStopDriver',
                           return_value=False):
        with mock.patch.object(app,
                               'dispatchConfigDriver'):
            with mock.patch.object(app,
                                   'dispatchStartDriver'):
                suc = app.dispatch()
                assert suc


def test_scanValid_1():
    suc = app.scanValid()
    assert not suc


def test_scanValid_2():
    suc = app.scanValid('dome')
    assert not suc


def test_scanValid_3():
    def Sender():
        return app.drivers['filter']['class'].signals
    app.sender = Sender

    suc = app.scanValid(driver='dome', deviceName='dome')
    assert not suc


def test_scanValid_4():
    app.drivers['filter']['class'].name = 'test'
    suc = app.scanValid(driver='measure', deviceName='dome')
    assert not suc


def test_scanValid_5():
    def Sender():
        return app.drivers['dome']['class'].signals
    app.sender = Sender

    app.drivers['dome']['class'].name = 'dome'
    suc = app.scanValid(driver='dome', deviceName='dome')
    assert suc


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
