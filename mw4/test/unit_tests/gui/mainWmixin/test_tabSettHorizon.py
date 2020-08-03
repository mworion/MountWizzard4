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
import unittest.mock as mock
import pytest
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount

# local import
from mw4.gui.mainWmixin.tabSettHorizon import SettHorizon
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.modeldata.buildpoints import DataPoint
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, app

    class Test2:

        def drawHemisphere(self):
            return

    class Test1(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='mw4/test/data')

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='mw4/test/data')
        update1s = pyqtSignal()
        redrawHemisphere = pyqtSignal()
        drawHorizonPoints = pyqtSignal()
        drawBuildPoints = pyqtSignal()
        message = pyqtSignal(str, int)
        mwGlob = {'configDir': 'mw4/test/config'}
        data = DataPoint(app=Test1(), configDir='mw4/test/config')
        uiWindows = {'showHemisphereW': {'classObj': Test2()}}

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = SettHorizon(app=Test(), ui=ui,
                      clickable=MWidget().clickable)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.openDir = MWidget().openDir
    app.openFile = MWidget().openFile
    app.saveFile = MWidget().saveFile
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)

    yield


def test_initConfig_1():
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_loadHorizonMaskFile_1(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'loadHorizonP',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.loadHorizonMask()
                assert suc
            assert ['Horizon mask [test] loaded', 0] == blocker.args


def test_loadHorizonMaskFile_2(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('', '', '')):
        suc = app.loadHorizonMask()
        assert not suc


def test_loadHorizonMaskFile_3(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'loadHorizonP',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.loadHorizonMask()
                assert suc
            assert ['Horizon mask [test] cannot no be loaded', 2] == blocker.args


def test_saveHorizonMaskFile_1(qtbot):
    app.ui.horizonFileName.setText('test')
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'saveHorizonP',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveHorizonMask()
                assert suc
            assert ['Horizon mask [test] saved', 0] == blocker.args


def test_saveHorizonMaskFile_2(qtbot):
    app.ui.horizonFileName.setText('')
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.saveHorizonMask()
        assert not suc
    assert ['Horizon mask file name not given', 2] == blocker.args


def test_saveHorizonMaskFile_3(qtbot):
    app.ui.horizonFileName.setText('test')
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'saveHorizonP',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveHorizonMask()
                assert suc
            assert ['Horizon mask [test] cannot no be saved', 2] == blocker.args


def test_saveHorizonMaskFileAs_1(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'saveHorizonP',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveHorizonMaskAs()
                assert suc
            assert ['Horizon mask [test] saved', 0] == blocker.args


def test_saveHorizonMaskFileAs_2(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('', '', '')):
        suc = app.saveHorizonMaskAs()
        assert not suc


def test_saveHorizonMaskFileAs_3(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'saveHorizonP',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveHorizonMaskAs()
                assert suc
            assert ['Horizon mask [test] cannot no be saved', 2] == blocker.args
