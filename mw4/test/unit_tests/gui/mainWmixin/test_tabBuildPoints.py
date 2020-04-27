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
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
from skyfield.toposlib import Topos

# local import
from mw4.gui.mainWmixin.tabBuildPoints import BuildPoints
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.base.loggerMW import CustomLogger
from mw4.modeldata.buildpoints import DataPoint


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, app

    class Test1(QObject):
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')

    class Test(QObject):
        config = {'mainW': {}}
        redrawHemisphere = pyqtSignal()
        message = pyqtSignal(str, int)
        mwGlob = {'configDir': 'mw4/test/config'}
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        data = DataPoint(app=Test1(), configDir='mw4/test/config')
        uiWindows = {'showHemisphereW': {'classObj': None}}

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = BuildPoints(app=Test(), ui=ui)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.openFile = MWidget().openFile
    app.saveFile = MWidget().saveFile
    app.deleteLater = MWidget().deleteLater
    app.deviceStat = dict()
    app.log = CustomLogger(logging.getLogger(__name__), {})

    qtbot.addWidget(app)

    yield


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_genBuildGrid_1():
    app.ui.numberGridPointsRow.setValue(10)
    app.ui.numberGridPointsCol.setValue(10)
    app.ui.altitudeMin.setValue(10)
    app.ui.altitudeMax.setValue(60)
    suc = app.genBuildGrid()
    assert suc


def test_genBuildGrid_2():
    app.ui.numberGridPointsRow.setValue(10)
    app.ui.numberGridPointsCol.setValue(9)
    app.ui.altitudeMin.setValue(10)
    app.ui.altitudeMax.setValue(60)
    suc = app.genBuildGrid()
    assert suc


def test_genBuildGrid_3():
    app.ui.numberGridPointsRow.setValue(10)
    app.ui.numberGridPointsCol.setValue(9)
    app.ui.altitudeMin.setValue(10)
    app.ui.altitudeMax.setValue(60)

    with mock.patch.object(app.app.data,
                           'genGrid',
                           return_value=False):
        suc = app.genBuildGrid()
        assert not suc


def test_genBuildAlign3_1():
    with mock.patch.object(app.app.data,
                           'genAlign',
                           return_value=False):
        suc = app.genBuildAlign3()
        assert not suc


def test_genBuildAlign3_2():
    with mock.patch.object(app.app.data,
                           'genAlign',
                           return_value=True):
        suc = app.genBuildAlign3()
        assert suc


def test_genBuildAlign6_1():
    with mock.patch.object(app.app.data,
                           'genAlign',
                           return_value=False):
        suc = app.genBuildAlign6()
        assert not suc


def test_genBuildAlign6_2():
    with mock.patch.object(app.app.data,
                           'genAlign',
                           return_value=True):
        suc = app.genBuildAlign6()
        assert suc


def test_genBuildAlign9_1():
    with mock.patch.object(app.app.data,
                           'genAlign',
                           return_value=False):
        suc = app.genBuildAlign9()
        assert not suc


def test_genBuildAlign9_2():
    with mock.patch.object(app.app.data,
                           'genAlign',
                           return_value=True):
        suc = app.genBuildAlign9()
        assert suc


def test_genBuildMax_1(qtbot):
    app.ui.checkAutoDeleteHorizon.setChecked(False)
    suc = app.genBuildMax()
    assert not suc


def test_genBuildMax_2(qtbot):
    with mock.patch.object(app.app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildMax()
            assert not suc
        assert ['Build points [max] cannot be generated', 2] == blocker.args


def test_genBuildMax_3(qtbot):
    with mock.patch.object(app.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = app.genBuildMax()
        assert suc


def test_genBuildMed_1(qtbot):
    suc = app.genBuildMed()
    assert not suc


def test_genBuildMed_2(qtbot):
    with mock.patch.object(app.app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildMed()
            assert not suc
        assert ['Build points [med] cannot be generated', 2] == blocker.args


def test_genBuildMed_3(qtbot):
    with mock.patch.object(app.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = app.genBuildMed()
        assert suc


def test_genBuildNorm_1(qtbot):
    suc = app.genBuildNorm()
    assert not suc


def test_genBuildNorm_2(qtbot):
    with mock.patch.object(app.app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildNorm()
            assert not suc
        assert ['Build points [norm] cannot be generated', 2] == blocker.args


def test_genBuildNorm_3(qtbot):
    with mock.patch.object(app.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = app.genBuildNorm()
        assert suc


def test_genBuildMin_1(qtbot):
    app.ui.checkAutoDeleteHorizon.setChecked(True)
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.genBuildMin()
        assert not suc
        assert ['Build points [min] cannot be generated', 2] == blocker.args


def test_genBuildMin_1b(qtbot):
    app.ui.checkAutoDeleteHorizon.setChecked(False)
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.genBuildMin()
        assert not suc
        assert ['Build points [min] cannot be generated', 2] == blocker.args


def test_genBuildMin_2(qtbot):
    with mock.patch.object(app.app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildMin()
            assert not suc
        assert ['Build points [min] cannot be generated', 2] == blocker.args


def test_genBuildMin_3(qtbot):
    with mock.patch.object(app.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = app.genBuildMin()
        assert suc


def test_genBuildDSO_1(qtbot):
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.genBuildDSO()
        assert not suc
    assert ['DSO Path cannot be generated', 2] == blocker.args


def test_genBuildDSO_2(qtbot):
    with mock.patch.object(app.app.data,
                           'generateDSOPath',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildDSO()
            assert not suc
        assert ['DSO Path cannot be generated', 2] == blocker.args


def test_genBuildDSO_3(qtbot):
    app.app.mount.obsSite.raJNow = 0
    app.app.mount.obsSite.decJNow = 0
    with mock.patch.object(app.app.data,
                           'generateDSOPath',
                           return_value=True):
        suc = app.genBuildDSO()
        assert suc


def test_genBuildDSO_4(qtbot):
    app.app.mount.obsSite.raJNow = 0
    app.app.mount.obsSite.decJNow = 0
    with mock.patch.object(app.app.data,
                           'generateDSOPath',
                           return_value=False):
        suc = app.genBuildDSO()
        assert not suc


def test_genBuildGoldenSpiral_1(qtbot):
    with qtbot.assertNotEmitted(app.app.message):
        suc = app.genBuildSpiralMax()
        assert suc


def test_genBuildGoldenSpiral_1a(qtbot):
    with qtbot.assertNotEmitted(app.app.message):
        suc = app.genBuildSpiralMed()
        assert suc


def test_genBuildGoldenSpiral_1b(qtbot):
    with qtbot.assertNotEmitted(app.app.message):
        suc = app.genBuildSpiralNorm()
        assert suc


def test_genBuildGoldenSpiral_1c(qtbot):
    with qtbot.assertNotEmitted(app.app.message):
        suc = app.genBuildSpiralMin()
        assert suc


def test_genBuildGoldenSpiral_2(qtbot):
    with mock.patch.object(app.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildSpiralMax()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_genBuildGoldenSpiral_2a(qtbot):
    with mock.patch.object(app.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildSpiralMed()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_genBuildGoldenSpiral_2b(qtbot):
    with mock.patch.object(app.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildSpiralNorm()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_genBuildGoldenSpiral_2c(qtbot):
    with mock.patch.object(app.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildSpiralMin()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_loadBuildFile_1(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'loadBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.loadBuildFile()
                assert suc
            assert ['Build file [test] loaded', 0] == blocker.args


def test_loadBuildFile_2(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('', '', '')):
        suc = app.loadBuildFile()
        assert not suc


def test_loadBuildFile_3(qtbot):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'loadBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.loadBuildFile()
                assert suc
            assert ['Build file [test] cannot no be loaded', 2] == blocker.args


def test_saveBuildFile_1(qtbot):
    app.ui.buildPFileName.setText('test')
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'saveBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveBuildFile()
                assert suc
            assert ['Build file [test] saved', 0] == blocker.args


def test_saveBuildFile_2(qtbot):
    app.ui.buildPFileName.setText('')
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.saveBuildFile()
        assert not suc
    assert ['Build points file name not given', 2] == blocker.args


def test_saveBuildFile_3(qtbot):
    app.ui.buildPFileName.setText('test')
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'saveBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveBuildFile()
                assert suc
            assert ['Build file [test] cannot no be saved', 2] == blocker.args


def test_saveBuildFileAs_1(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'saveBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveBuildFileAs()
                assert suc
            assert ['Build file [test] saved', 0] == blocker.args


def test_saveBuildFileAs_2(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('', '', '')):
        suc = app.saveBuildFileAs()
        assert not suc


def test_saveBuildFileAs_3(qtbot):
    with mock.patch.object(app,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.app.data,
                               'saveBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveBuildFileAs()
                assert suc
            assert ['Build file [test] cannot no be saved', 2] == blocker.args


def test_genBuildFile_1(qtbot):
    app.ui.buildPFileName.setText('')
    app.ui.checkAutoDeleteHorizon.setChecked(True)
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.genBuildFile()
        assert not suc
    assert ['Build points file name not given', 2] == blocker.args


def test_genBuildFile_2(qtbot):
    app.ui.buildPFileName.setText('test')
    app.ui.checkAutoDeleteHorizon.setChecked(True)
    with mock.patch.object(app.app.data,
                           'loadBuildP',
                           return_value=False):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.genBuildFile()
            assert not suc
        assert ['Build points file [test] could not be loaded', 2] == blocker.args


def test_genBuildFile_3(qtbot):
    app.ui.buildPFileName.setText('test')
    app.ui.checkAutoDeleteHorizon.setChecked(True)
    with mock.patch.object(app.app.data,
                           'loadBuildP',
                           return_value=True):
        suc = app.genBuildFile()
        assert suc


def test_genBuildFile_4(qtbot):
    app.ui.buildPFileName.setText('test')
    app.ui.checkAutoDeleteHorizon.setChecked(False)
    with mock.patch.object(app.app.data,
                           'loadBuildP',
                           return_value=True):
        suc = app.genBuildFile()
        assert suc


def test_clearBuildP_1():
    suc = app.clearBuildP()
    assert not suc


def test_clearBuildP_2():
    class Test:
        @staticmethod
        def clearHemisphere():
            return

    app.app.uiWindows['showHemisphereW']['classObj'] = Test()
    suc = app.clearBuildP()
    assert suc


def test_autoSortPoints_1():
    suc = app.autoSortPoints()
    assert not suc


def test_autoSortPoints_2():
    app.ui.checkSortEW.setChecked(True)
    app.ui.checkSortHL.setChecked(True)
    suc = app.autoSortPoints()
    assert suc


def test_updateSorting():
    suc = app.updateSorting()
    assert suc
