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
# written in python3, (c) 2019-2022 by mworion
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
from skyfield.api import wgs84

# local import
from gui.mainWmixin.tabSettParkPos import SettParkPos
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        update1s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        update30m = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettParkPos(app=Test(), ui=ui,
                      clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.deviceStat = dict()
    app.log = logging.getLogger(__name__)
    app.threadPool = QThreadPool()
    yield
    app.threadPool.waitForDone(1000)


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_initConfig_2():
    suc = app.initConfig()
    assert suc


def test_initConfig_3():
    config = app.app.config['mainW']
    for i in range(0, 10):
        config[f'posText{i:1d}'] = str(i)
        config[f'posAlt{i:1d}'] = i
        config[f'posAz{i:1d}'] = i
    app.initConfig()
    assert app.ui.posText0.text() == '0'
    assert app.ui.posAlt0.value() == 0
    assert app.ui.posAz0.value() == 0
    assert app.ui.posText4.text() == '4'
    assert app.ui.posAlt4.value() == 4
    assert app.ui.posAz4.value() == 4
    assert app.ui.posText7.text() == '7'
    assert app.ui.posAlt7.value() == 7
    assert app.ui.posAz7.value() == 7


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setupParkPosGui(qtbot):
    assert 10 == len(app.posButtons)
    assert 10 == len(app.posTexts)
    assert 10 == len(app.posAlt)
    assert 10 == len(app.posAz)
    assert 10 == len(app.posSaveButtons)


def test_parkAtPos_1(qtbot):
    app.app.mount.signals.slewFinished.connect(app.parkAtPos)
    with mock.patch.object(app.app.mount.obsSite,
                           'parkOnActualPosition',
                           return_value=False):
        suc = app.parkAtPos()
        assert not suc


def test_parkAtPos_2(qtbot):
    app.app.mount.signals.slewFinished.connect(app.parkAtPos)
    with mock.patch.object(app.app.mount.obsSite,
                           'parkOnActualPosition',
                           return_value=True):
        suc = app.parkAtPos()
        assert suc


def test_slewParkPos_1(qtbot):
    def Sender():
        return ui.powerPort1
    app.sender = Sender
    with mock.patch.object(app.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'startSlewing',
                               return_value=True):
            suc = app.slewToParkPos()
            assert not suc


def test_slewParkPos_2(qtbot):
    def Sender():
        return ui.posButton0
    app.sender = Sender
    with mock.patch.object(app.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'startSlewing',
                               return_value=True):
            suc = app.slewToParkPos()
            assert suc


def test_slewParkPos_3(qtbot):
    def Sender():
        return ui.posButton0
    app.sender = Sender
    app.ui.posAlt0.setValue(40)
    app.ui.posAz0.setValue(180)
    with mock.patch.object(app.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'startSlewing',
                               return_value=True):
            suc = app.slewToParkPos()
            assert suc


def test_slewParkPos_3a(qtbot):
    app.ui.parkMountAfterSlew.setChecked(True)

    def Sender():
        return ui.posButton0
    app.sender = Sender
    app.ui.posAlt0.setValue(40)
    app.ui.posAz0.setValue(180)
    with mock.patch.object(app.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'startSlewing',
                               return_value=True):
            suc = app.slewToParkPos()
            assert suc


def test_slewParkPos_4(qtbot):
    def Sender():
        return ui.posButton0
    app.sender = Sender
    app.ui.posAlt0.setValue(-40)
    app.ui.posAz0.setValue(180)
    with mock.patch.object(app.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        with mock.patch.object(app.app.mount.obsSite,
                               'startSlewing',
                               return_value=True):
            suc = app.slewToParkPos()
            assert not suc


def test_slewParkPos_5(qtbot):
    def Sender():
        return ui.posButton0
    app.sender = Sender
    app.ui.posAlt0.setValue(180)
    app.ui.posAz0.setValue(180)
    with mock.patch.object(app.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(app.app.mount.obsSite,
                               'startSlewing',
                               return_value=False):
            suc = app.slewToParkPos()
            assert not suc


def test_saveActualPosition_1():
    suc = app.saveActualPosition()
    assert not suc


def test_saveActualPosition_2():
    app.app.mount.obsSite.Alt = 40
    suc = app.saveActualPosition()
    assert not suc


def test_saveActualPosition_3():
    def Sender():
        return ui.posAlt0

    app.sender = Sender
    app.app.mount.obsSite.Alt = 40
    app.app.mount.obsSite.Az = 40
    suc = app.saveActualPosition()
    assert suc


def test_saveActualPosition_4():
    def Sender():
        return ui.posSave0

    app.app.mount.obsSite.Alt = 40
    app.app.mount.obsSite.Az = 40
    app.sender = Sender
    suc = app.saveActualPosition()
    assert suc
