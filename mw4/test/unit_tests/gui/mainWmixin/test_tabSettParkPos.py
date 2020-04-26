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
from mw4.gui.mainWmixin.tabSettParkPos import SettParkPos
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.dome.dome import Dome
from mw4.cover.flipflat import FlipFlat
from mw4.base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        update1s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        update30m = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        dome = Dome(app=Test1())
        cover = FlipFlat(app=Test1())

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettParkPos(app=Test(), ui=ui,
                      clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.deviceStat = dict()
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()

    qtbot.addWidget(app)

    yield

    app.threadPool.waitForDone(1000)


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_initConfig_2():
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_initConfig_1():
    config = app.app.config['mainW']
    for i in range(0, 10):
        config[f'posText{i:1d}'] = str(i)
        config[f'posAlt{i:1d}'] = str(i)
        config[f'posAz{i:1d}'] = str(i)
    app.initConfig()
    assert app.ui.posText0.text() == '0'
    assert app.ui.posAlt0.text() == '0'
    assert app.ui.posAz0.text() == '0'
    assert app.ui.posText4.text() == '4'
    assert app.ui.posAlt4.text() == '4'
    assert app.ui.posAz4.text() == '4'
    assert app.ui.posText7.text() == '7'
    assert app.ui.posAlt7.text() == '7'
    assert app.ui.posAz7.text() == '7'


def test_storeConfig_1():
    app.storeConfig()


def test_setupParkPosGui(qtbot):
    assert 10 == len(app.posButtons)
    assert 10 == len(app.posTexts)
    assert 10 == len(app.posAlt)
    assert 10 == len(app.posAz)
    assert 10 == len(app.posSaveButtons)


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
            assert not suc


def test_slewParkPos_3(qtbot):
    def Sender():
        return ui.posButton0
    app.sender = Sender
    app.ui.posAlt0.setText('40')
    app.ui.posAz0.setText('180')
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
    app.ui.posAlt0.setText('-40')
    app.ui.posAz0.setText('180')
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
    app.ui.posAlt0.setText('180')
    app.ui.posAz0.setText('180')
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


def test_toggleUseGeometry_1():
    suc = app.setUseGeometryInMount()
    assert suc


def test_toggleUseGeometry_2():
    app.ui.domeRadius.setValue(0.3)
    suc = app.setUseGeometryInMount()
    assert suc


def test_updateDomeGeometry_1():
    suc = app.updateDomeGeometryToGui()
    assert suc


def test_updateCoverStatGui_1():
    app.app.cover.data['Status.Cover'] = 'OPEN'
    suc = app.updateCoverStatGui()
    assert suc


def test_updateCoverStatGui_2():
    app.app.cover.data['Status.Cover'] = 'CLOSED'
    suc = app.updateCoverStatGui()
    assert suc


def test_updateCoverStatGui_3():
    app.app.cover.data['Status.Cover'] = '...'
    suc = app.updateCoverStatGui()
    assert suc


def test_setCoverPark_1():
    suc = app.setCoverPark()
    assert suc


def test_setCoverUnpark_1():
    suc = app.setCoverUnpark()
    assert suc


def test_setSettlingTimes_1():
    suc = app.setSettlingTimes()
    assert suc
