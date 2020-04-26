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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import logging

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
import wakeonlan

# local import
from mw4.gui.mainWmixin.tabSettMount import SettMount
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.environment.onlineWeather import OnlineWeather
from mw4.gui.widget import MWidget
from mw4.base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        update10s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        onlineWeather = OnlineWeather(app=Test1())
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        mwGlob = {'imageDir': 'mw4/test/image'}

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettMount(app=Test(), ui=ui,
                    clickable=MWidget().clickable)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.openDir = MWidget().openDir
    app.deleteLater = MWidget().deleteLater
    app.log = CustomLogger(logging.getLogger(__name__), {})

    qtbot.addWidget(app)

    yield


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_mountBoot_1():
    with mock.patch.object(app.app.mount,
                           'bootMount',
                           return_value=False):
        suc = app.mountBoot()
        assert not suc


def test_mountBoot_2():
    with mock.patch.object(app.app.mount,
                           'bootMount',
                           return_value=True):
        suc = app.mountBoot()
        assert suc


def test_mountShutdown_1():
    with mock.patch.object(app.app.mount,
                           'shutdown',
                           return_value=False):
        suc = app.mountShutdown()
        assert not suc


def test_mountShutdown_2():
    with mock.patch.object(app.app.mount,
                           'shutdown',
                           return_value=True):
        suc = app.mountShutdown()
        assert suc


def test_storeConfig_1():
    app.storeConfig()


def test_checkFormatMAC_1():
    val = app.checkFormatMAC('')
    assert val is None


def test_checkFormatMAC_2():
    val = app.checkFormatMAC(5)
    assert val is None


def test_checkFormatMAC_3():
    val = app.checkFormatMAC('test')
    assert val is None


def test_checkFormatMAC_4():
    val = app.checkFormatMAC('00:00:00')
    assert val is None


def test_checkFormatMAC_5():
    val = app.checkFormatMAC('00:00:00:00.00.kk')
    assert val is None


def test_checkFormatMAC_6():
    val = app.checkFormatMAC('00.11.22:ab:44:55')
    assert val == '00:11:22:AB:44:55'


def test_bootRackComp_1():
    with mock.patch.object(wakeonlan,
                           'send_magic_packet',
                           return_value=False):
        suc = app.bootRackComp()
        assert suc


def test_bootRackComp_2():
    app.ui.rackCompMAC.setText('00:00:00:00:00:xy')
    with mock.patch.object(wakeonlan,
                           'send_magic_packet',
                           return_value=True):
        suc = app.bootRackComp()
        assert not suc


def test_mountHost():
    app.ui.mountHost.setText('test')
    app.mountHost()

    assert app.app.mount.host == ('test', 3492)


def test_mountMAC():
    app.ui.mountMAC.setText('00:00:00:00:00:00')
    app.mountMAC()

    assert app.app.mount.MAC == '00:00:00:00:00:00'


def test_setMountMAC_1():
    suc = app.setMountMAC()
    assert not suc


def test_setMountMAC_2():
    class Test:
        addressLanMAC = None
        typeConnection = 0
    suc = app.setMountMAC(Test())
    assert not suc


def test_setMountMAC_3():
    class Test:
        addressLanMAC = ''
        typeConnection = 0
    suc = app.setMountMAC(Test())
    assert not suc


def test_setMountMAC_4():
    class Test:
        addressLanMAC = None
        typeConnection = 0
    app.app.mount.MAC = None
    suc = app.setMountMAC(Test())
    assert not suc


def test_setMountMAC_6():
    class Test:
        addressLanMAC = '00:00:00:00:00:00'
        typeConnection = 3
    app.app.mount.MAC = '00:00:00:00:00:00'
    suc = app.setMountMAC(Test())
    assert suc
