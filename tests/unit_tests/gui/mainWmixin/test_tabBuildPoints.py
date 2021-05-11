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
from pathlib import Path

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
from skyfield.api import wgs84

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabBuildPoints import BuildPoints
from logic.modeldata.buildpoints import DataPoint


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    class Test1(QObject):
        mwGlob = {'configDir': 'tests/config'}
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')

    class Test(QObject):
        config = {'mainW': {}}
        redrawHemisphere = pyqtSignal()
        drawBuildPoints = pyqtSignal()
        message = pyqtSignal(str, int)
        sendBuildPoints = pyqtSignal(object)
        mwGlob = {'configDir': 'tests/config'}
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                              longitude_degrees=10,
                                              elevation_m=500)
        data = DataPoint(app=Test1())
        uiWindows = {'showHemisphereW': {'classObj': None}}

    class Mixin(MWidget, BuildPoints):
        def __init__(self):
            super().__init__()
            self.app = Test()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            BuildPoints.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_genBuildGrid_1(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(10)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)
    suc = function.genBuildGrid()
    assert suc


def test_genBuildGrid_2(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(9)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)
    suc = function.genBuildGrid()
    assert suc


def test_genBuildGrid_3(function):
    function.ui.numberGridPointsRow.setValue(10)
    function.ui.numberGridPointsCol.setValue(9)
    function.ui.altitudeMin.setValue(10)
    function.ui.altitudeMax.setValue(60)

    with mock.patch.object(function.app.data,
                           'genGrid',
                           return_value=False):
        suc = function.genBuildGrid()
        assert not suc


def test_genBuildAlign3_1(function):
    with mock.patch.object(function.app.data,
                           'genAlign',
                           return_value=False):
        suc = function.genBuildAlign3()
        assert not suc


def test_genBuildAlign3_2(function):
    with mock.patch.object(function.app.data,
                           'genAlign',
                           return_value=True):
        suc = function.genBuildAlign3()
        assert suc


def test_genBuildAlign6_1(function):
    with mock.patch.object(function.app.data,
                           'genAlign',
                           return_value=False):
        suc = function.genBuildAlign6()
        assert not suc


def test_genBuildAlign6_2(function):
    with mock.patch.object(function.app.data,
                           'genAlign',
                           return_value=True):
        suc = function.genBuildAlign6()
        assert suc


def test_genBuildAlign9_1(function):
    with mock.patch.object(function.app.data,
                           'genAlign',
                           return_value=False):
        suc = function.genBuildAlign9()
        assert not suc


def test_genBuildAlign9_2(function):
    with mock.patch.object(function.app.data,
                           'genAlign',
                           return_value=True):
        suc = function.genBuildAlign9()
        assert suc


def test_genBuildMax_1(function):
    function.ui.checkAutoDeleteHorizon.setChecked(False)
    suc = function.genBuildMax()
    assert not suc


def test_genBuildMax_2(function, qtbot):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildMax()
            assert not suc
        assert ['Build points [max] cannot be generated', 2] == blocker.args


def test_genBuildMax_3(function):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = function.genBuildMax()
        assert suc


def test_genBuildMed_1(function):
    suc = function.genBuildMed()
    assert not suc


def test_genBuildMed_2(function, qtbot):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildMed()
            assert not suc
        assert ['Build points [med] cannot be generated', 2] == blocker.args


def test_genBuildMed_3(function):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = function.genBuildMed()
        assert suc


def test_genBuildNorm_1(function):
    suc = function.genBuildNorm()
    assert not suc


def test_genBuildNorm_2(function, qtbot):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildNorm()
            assert not suc
        assert ['Build points [norm] cannot be generated', 2] == blocker.args


def test_genBuildNorm_3(function):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = function.genBuildNorm()
        assert suc


def test_genBuildMin_1(function, qtbot):
    function.ui.checkAutoDeleteHorizon.setChecked(True)
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.genBuildMin()
        assert not suc
        assert ['Build points [min] cannot be generated', 2] == blocker.args


def test_genBuildMin_1b(function, qtbot):
    function.ui.checkAutoDeleteHorizon.setChecked(False)
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.genBuildMin()
        assert not suc
        assert ['Build points [min] cannot be generated', 2] == blocker.args


def test_genBuildMin_2(function, qtbot):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildMin()
            assert not suc
        assert ['Build points [min] cannot be generated', 2] == blocker.args


def test_genBuildMin_3(function):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = function.genBuildMin()
        assert suc


def test_genBuildDSO_1(function, qtbot):
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.genBuildDSO()
        assert not suc
    assert ['DSO Path cannot be generated', 2] == blocker.args


def test_genBuildDSO_2(function, qtbot):
    with mock.patch.object(function.app.data,
                           'generateDSOPath',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildDSO()
            assert not suc
        assert ['DSO Path cannot be generated', 2] == blocker.args


def test_genBuildDSO_3(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    with mock.patch.object(function.app.data,
                           'generateDSOPath',
                           return_value=True):
        suc = function.genBuildDSO()
        assert suc


def test_genBuildDSO_4(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    with mock.patch.object(function.app.data,
                           'generateDSOPath',
                           return_value=False):
        suc = function.genBuildDSO()
        assert not suc


def test_genBuildGoldenSpiral_1(function, qtbot):
    with qtbot.assertNotEmitted(function.app.message):
        suc = function.genBuildSpiralMax()
        assert suc


def test_genBuildGoldenSpiral_1a(function, qtbot):
    with qtbot.assertNotEmitted(function.app.message):
        suc = function.genBuildSpiralMed()
        assert suc


def test_genBuildGoldenSpiral_1b(function, qtbot):
    with qtbot.assertNotEmitted(function.app.message):
        suc = function.genBuildSpiralNorm()
        assert suc


def test_genBuildGoldenSpiral_1c(function, qtbot):
    with qtbot.assertNotEmitted(function.app.message):
        suc = function.genBuildSpiralMin()
        assert suc


def test_genBuildGoldenSpiral_2(function, qtbot):
    with mock.patch.object(function.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildSpiralMax()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_genBuildGoldenSpiral_2a(function, qtbot):
    with mock.patch.object(function.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildSpiralMed()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_genBuildGoldenSpiral_2b(function, qtbot):
    with mock.patch.object(function.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildSpiralNorm()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_genBuildGoldenSpiral_2c(function, qtbot):
    with mock.patch.object(function.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildSpiralMin()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_loadBuildFile_1(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadBuildP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.loadBuildFile()
                assert suc
            assert ['Build file [test] loaded', 0] == blocker.args


def test_loadBuildFile_2(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('', '', '')):
        suc = function.loadBuildFile()
        assert not suc


def test_loadBuildFile_3(function, qtbot):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadBuildP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.loadBuildFile()
                assert suc
            assert ['Build file [test] cannot no be loaded', 2] == blocker.args


def test_saveBuildFile_1(function, qtbot):
    function.ui.buildPFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveBuildP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveBuildFile()
                assert suc
            assert ['Build file [test] saved', 0] == blocker.args


def test_saveBuildFile_2(function, qtbot):
    function.ui.buildPFileName.setText('')
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.saveBuildFile()
        assert not suc
    assert ['Build points file name not given', 2] == blocker.args


def test_saveBuildFile_3(function, qtbot):
    function.ui.buildPFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveBuildP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveBuildFile()
                assert suc
            assert ['Build file [test] cannot no be saved', 2] == blocker.args


def test_saveBuildFileAs_1(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveBuildP',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveBuildFileAs()
                assert suc
            assert ['Build file [test] saved', 0] == blocker.args


def test_saveBuildFileAs_2(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('', '', '')):
        suc = function.saveBuildFileAs()
        assert not suc


def test_saveBuildFileAs_3(function, qtbot):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveBuildP',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveBuildFileAs()
                assert suc
            assert ['Build file [test] cannot no be saved', 2] == blocker.args


def test_genBuildFile_1(function, qtbot):
    function.ui.buildPFileName.setText('')
    function.ui.checkAutoDeleteHorizon.setChecked(True)
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.genBuildFile()
        assert not suc
    assert ['Build points file name not given', 2] == blocker.args


def test_genBuildFile_2(function, qtbot):
    function.ui.buildPFileName.setText('test')
    function.ui.checkAutoDeleteHorizon.setChecked(True)
    with mock.patch.object(function.app.data,
                           'loadBuildP',
                           return_value=False):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.genBuildFile()
            assert not suc
        assert ['Build points file [test] could not be loaded', 2] == blocker.args


def test_genBuildFile_3(function):
    function.ui.buildPFileName.setText('test')
    function.ui.checkAutoDeleteHorizon.setChecked(True)
    with mock.patch.object(function.app.data,
                           'loadBuildP',
                           return_value=True):
        suc = function.genBuildFile()
        assert suc


def test_genBuildFile_4(function):
    function.ui.buildPFileName.setText('test')
    function.ui.checkAutoDeleteHorizon.setChecked(False)
    with mock.patch.object(function.app.data,
                           'loadBuildP',
                           return_value=True):
        suc = function.genBuildFile()
        assert suc


def test_clearBuildP_1(function):
    suc = function.clearBuildP()
    assert not suc


def test_clearBuildP_2(function):
    class Test:
        @staticmethod
        def clearHemisphere():
            return

    function.app.uiWindows['showHemisphereW']['classObj'] = Test()
    suc = function.clearBuildP()
    assert suc


def test_autoDeletePoints(function):
    function.ui.checkAutoDeleteHorizon.setChecked(True)
    function.ui.checkAutoDeleteMeridian.setChecked(True)
    function.ui.checkSafetyMarginHorizon.setChecked(True)
    suc = function.autoDeletePoints()
    assert suc


def test_autoSortPoints_1(function):
    suc = function.autoSortPoints()
    assert not suc


def test_autoSortPoints_2(function):
    function.ui.checkSortEW.setChecked(True)
    function.ui.checkSortHL.setChecked(True)
    function.ui.checkAvoidFlip.setChecked(True)
    suc = function.autoSortPoints()
    assert suc


def test_autoSortPoints_3(function):
    function.ui.checkSortEW.setChecked(True)
    function.ui.checkSortHL.setChecked(True)
    function.ui.checkAvoidFlip.setChecked(True)
    function.app.mount.obsSite.pierside = 'E'
    suc = function.autoSortPoints()
    assert suc


def test_processPoints(function):
    suc = function.processPoints()
    assert suc
