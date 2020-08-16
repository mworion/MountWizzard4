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
