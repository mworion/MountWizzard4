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
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
from pathlib import Path

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal, QThreadPool
from mountcontrol.qtmount import Mount
from skyfield.api import wgs84, Angle
from astroquery.simbad import Simbad

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
        mwGlob = {'configDir': 'tests/workDir/config'}
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')

    class Test(QObject):
        config = {'mainW': {}}
        redrawHemisphere = pyqtSignal()
        drawBuildPoints = pyqtSignal()
        buildPointsChanged = pyqtSignal()
                mes = pyqtSignal(object, object, object, object)
        sendBuildPoints = pyqtSignal(object)
        threadPool = QThreadPool()
        mwGlob = {'configDir': 'tests/workDir/config'}
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/workDir/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                              longitude_degrees=10,
                                              elevation_m=500)
        data = DataPoint(app=Test1())
        uiWindows = {'showHemisphereW': {'classObj': None}}

    class Mixin(MWidget, BuildPoints):
        def __init__(self):
            super().__init__()
            self.app = Test()
            self.threadPool = self.app.threadPool
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


def test_genBuildAlign12_1(function):
    with mock.patch.object(function.app.data,
                           'genAlign',
                           return_value=False):
        suc = function.genBuildAlign12()
        assert not suc


def test_genBuildAlign12_2(function):
    with mock.patch.object(function.app.data,
                           'genAlign',
                           return_value=True):
        suc = function.genBuildAlign12()
        assert suc


def test_genBuildMax_1(function):
    function.ui.autoDeleteHorizon.setChecked(False)
    suc = function.genBuildMax()
    assert not suc


def test_genBuildMax_2(function):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=False):
        suc = function.genBuildMax()
        assert not suc


def test_genBuildMax_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = function.genBuildMax()
        assert suc


def test_genBuildMed_1(function):
    suc = function.genBuildMed()
    assert not suc


def test_genBuildMed_2(function):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=False):
        suc = function.genBuildMed()
        assert not suc


def test_genBuildMed_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = function.genBuildMed()
        assert suc


def test_genBuildNorm_1(function):
    suc = function.genBuildNorm()
    assert not suc


def test_genBuildNorm_2(function):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=False):
        suc = function.genBuildNorm()
        assert not suc


def test_genBuildNorm_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = function.genBuildNorm()
        assert suc


def test_genBuildMin_1(function):
    function.ui.autoDeleteHorizon.setChecked(True)
    suc = function.genBuildMin()
    assert not suc


def test_genBuildMin_1b(function):
    function.ui.autoDeleteHorizon.setChecked(False)
    suc = function.genBuildMin()
    assert not suc


def test_genBuildMin_2(function):
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=False):
        suc = function.genBuildMin()
        assert not suc


def test_genBuildMin_3(function):
    function.ui.ditherBuildPoints.setChecked(True)
    with mock.patch.object(function.app.data,
                           'genGreaterCircle',
                           return_value=True):
        suc = function.genBuildMin()
        assert suc


def test_genBuildDSO_1(function):
    suc = function.genBuildDSO()
    assert not suc


def test_genBuildDSO_2(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    with mock.patch.object(function.app.data,
                           'generateDSOPath',
                           return_value=False):
        suc = function.genBuildDSO()
        assert not suc


def test_genBuildDSO_3(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = 0
    function.simbadRa = None
    function.simbadDec = None
    with mock.patch.object(function.app.data,
                           'generateDSOPath',
                           return_value=False):
        suc = function.genBuildDSO()
        assert not suc


def test_genBuildDSO_4(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = 0
    function.simbadRa = None
    function.simbadDec = None
    with mock.patch.object(function.app.data,
                           'generateDSOPath',
                           return_value=False):
        suc = function.genBuildDSO()
        assert not suc


def test_genBuildDSO_5(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    with mock.patch.object(function.app.data,
                           'generateDSOPath',
                           return_value=True):
        suc = function.genBuildDSO()
        assert suc


def test_genBuildDSO_6(function):
    function.app.mount.obsSite.raJNow = 0
    function.app.mount.obsSite.decJNow = 0
    function.app.mount.obsSite.timeSidereal = Angle(hours=0)
    function.ui.ditherBuildPoints.setChecked(True)
    function.simbadRa = Angle(hours=0)
    function.simbadDec = Angle(degrees=0)
    with mock.patch.object(function.app.data,
                           'generateDSOPath',
                           return_value=True):
        with mock.patch.object(function.app.data,
                               'ditherPoints'):
            suc = function.genBuildDSO()
            assert suc


def test_genBuildGoldenSpiral_1(function):
    suc = function.genBuildSpiralMax()
    assert suc


def test_genBuildGoldenSpiral_1a(function):
    suc = function.genBuildSpiralMed()
    assert suc


def test_genBuildGoldenSpiral_1b(function):
    suc = function.genBuildSpiralNorm()
    assert suc


def test_genBuildGoldenSpiral_1c(function):
    suc = function.genBuildSpiralMin()
    assert suc


def test_genBuildGoldenSpiral_2(function):
    with mock.patch.object(function.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        suc = function.genBuildSpiralMax()
        assert not suc


def test_genBuildGoldenSpiral_2a(function):
    with mock.patch.object(function.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        suc = function.genBuildSpiralMed()
        assert not suc


def test_genBuildGoldenSpiral_2b(function):
    with mock.patch.object(function.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        suc = function.genBuildSpiralNorm()
        assert not suc


def test_genBuildGoldenSpiral_2c(function):
    with mock.patch.object(function.app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        suc = function.genBuildSpiralMin()
        assert not suc


def test_genModel_1(function):
    class Star:
        alt = Angle(degrees=10)
        az = Angle(degrees=10)

    function.app.mount.model.starList.append(Star())
    with mock.patch.object(function.app.data,
                           'addBuildP'):
        suc = function.genModel()
        assert suc


def test_loadBuildFile_1(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadBuildP',
                               return_value=True):
            suc = function.loadBuildFile()
            assert suc


def test_loadBuildFile_2(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('', '', '')):
        suc = function.loadBuildFile()
        assert not suc


def test_loadBuildFile_3(function):
    with mock.patch.object(function,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'loadBuildP',
                               return_value=False):
            suc = function.loadBuildFile()
            assert suc


def test_saveBuildFile_1(function):
    function.ui.buildPFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveBuildP',
                               return_value=True):
            suc = function.saveBuildFile()
            assert suc


def test_saveBuildFile_2(function):
    function.ui.buildPFileName.setText('')
    suc = function.saveBuildFile()
    assert not suc


def test_saveBuildFile_3(function):
    function.ui.buildPFileName.setText('test')
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveBuildP',
                               return_value=False):
            suc = function.saveBuildFile()
            assert suc


def test_saveBuildFileAs_1(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveBuildP',
                               return_value=True):
            suc = function.saveBuildFileAs()
            assert suc


def test_saveBuildFileAs_2(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('', '', '')):
        suc = function.saveBuildFileAs()
        assert not suc


def test_saveBuildFileAs_3(function):
    with mock.patch.object(function,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(function.app.data,
                               'saveBuildP',
                               return_value=False):
            suc = function.saveBuildFileAs()
            assert suc


def test_genBuildFile_1(function):
    function.ui.buildPFileName.setText('')
    function.ui.autoDeleteHorizon.setChecked(True)
    suc = function.genBuildFile()
    assert not suc


def test_genBuildFile_2(function):
    function.ui.buildPFileName.setText('test')
    function.ui.autoDeleteHorizon.setChecked(True)
    with mock.patch.object(function.app.data,
                           'loadBuildP',
                           return_value=False):
        suc = function.genBuildFile()
        assert not suc


def test_genBuildFile_3(function):
    function.ui.buildPFileName.setText('test')
    function.ui.autoDeleteHorizon.setChecked(True)
    with mock.patch.object(function.app.data,
                           'loadBuildP',
                           return_value=True):
        suc = function.genBuildFile()
        assert suc


def test_genBuildFile_4(function):
    function.ui.buildPFileName.setText('test')
    function.ui.autoDeleteHorizon.setChecked(False)
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
    function.ui.autoDeleteHorizon.setChecked(True)
    function.ui.autoDeleteMeridian.setChecked(True)
    function.ui.useSafetyMargin.setChecked(True)
    suc = function.autoDeletePoints()
    assert suc


def test_doSortDomeAzData_1(function):
    function.sortRunning.lock()
    with mock.patch.object(function.app.data,
                           'sort'):
        suc = function.doSortDomeAzData((0, 1))
        assert suc


def test_sortDomeAzWorker_1(function):
    with mock.patch.object(function.app.mount,
                           'calcMountAltAzToDomeAltAz',
                           return_value=(0, Angle(degrees=10))):
        suc = function.sortDomeAzWorker([(10, 10, True)])
        assert suc


def test_sortDomeAzWorker_2(function):
    with mock.patch.object(function.app.mount,
                           'calcMountAltAzToDomeAltAz',
                           return_value=(None, None)):
        suc = function.sortDomeAzWorker([(10, 10, True)])
        assert suc


def test_sortDomeAz_1(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.sortDomeAz([])
        assert suc
        function.sortRunning.unlock()


def test_sortDomeAz_2(function):
    function.sortRunning.lock()
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.sortDomeAz([])
        assert not suc
        function.sortRunning.unlock()


def test_sortMountAz(function):
    with mock.patch.object(function.app.data,
                           'sort'):
        suc = function.sortMountAz([])
        assert suc


def test_autoSortPoints_1(function):
    function.ui.sortEW.setChecked(False)
    function.ui.sortHL.setChecked(False)
    function.ui.avoidFlip.setChecked(False)
    function.ui.useDomeAz.setChecked(False)
    function.ui.useDomeAz.setEnabled(False)
    suc = function.autoSortPoints()
    assert not suc


def test_autoSortPoints_2(function):
    function.ui.sortEW.setChecked(True)
    function.ui.sortHL.setChecked(False)
    function.ui.avoidFlip.setChecked(False)
    function.ui.useDomeAz.setChecked(True)
    function.ui.useDomeAz.setEnabled(True)
    with mock.patch.object(function,
                           'sortDomeAz'):
        suc = function.autoSortPoints()
        assert suc


def test_autoSortPoints_3(function):
    function.ui.sortEW.setChecked(False)
    function.ui.sortHL.setChecked(False)
    function.ui.avoidFlip.setChecked(True)
    function.ui.useDomeAz.setChecked(False)
    function.ui.useDomeAz.setEnabled(False)
    with mock.patch.object(function,
                           'sortMountAz'):
        suc = function.autoSortPoints()
        assert suc


def test_buildPointsChanged(function):
    function.lastGenerator = 'test'
    suc = function.buildPointsChanged()
    assert suc
    assert function.lastGenerator == 'none'


def test_rebuildPoints_1(function):
    function.lastGenerator = 'align3'
    suc = function.rebuildPoints()
    assert suc


def test_processPoints(function):
    suc = function.processPoints()
    assert suc


def test_setupDsoGui(function):
    suc = function.setupDsoGui()
    assert suc


def test_querySimbad_1(function):
    function.ui.isOnline.setChecked(False)
    suc = function.querySimbad()
    assert not suc


def test_querySimbad_2(function):
    function.ui.isOnline.setChecked(True)
    function.ui.generateQuery.setText('')
    suc = function.querySimbad()
    assert not suc


def test_querySimbad_3(function):
    function.ui.isOnline.setChecked(True)
    function.ui.generateQuery.setText('m31')
    with mock.patch.object(Simbad,
                           'query_object',
                           return_value=None):
        suc = function.querySimbad()
        assert not suc


def test_querySimbad_4(function):
    class Data2:
        data = ['10 00 00']

    class Data:
        value = Data2()

    result = {'RA': Data(),
              'DEC': Data()}

    function.ui.isOnline.setChecked(True)
    function.ui.generateQuery.setText('m31')
    with mock.patch.object(Simbad,
                           'query_object',
                           return_value=result):
        suc = function.querySimbad()
        assert suc
