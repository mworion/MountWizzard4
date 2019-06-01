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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import logging
import pytest
import time
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import PyQt5.QtTest
import PyQt5.QtCore
import skyfield.api
# local import
from mw4 import mainApp
from mw4.test_units.test_setupQt import setupQt
from mw4.definitions import Solution, Solve, MPoint, MData, MParam, IParam, Point, RData


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showHemisphereW'] = True
    app.toggleHemisphereWindow()
    yield

"""
def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.mainW.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setupIcons():
    suc = app.mainW.setupIcons()
    assert suc


def test_clearGUI():
    suc = app.mainW.clearGUI()
    assert suc


def test_genBuildGrid_1():
    app.mainW.ui.numberGridPointsRow.setValue(10)
    app.mainW.ui.numberGridPointsCol.setValue(10)
    app.mainW.ui.altitudeMin.setValue(10)
    app.mainW.ui.altitudeMax.setValue(60)
    suc = app.mainW.genBuildGrid()
    assert suc


def test_genBuildGrid_2():
    app.mainW.ui.numberGridPointsRow.setValue(10)
    app.mainW.ui.numberGridPointsCol.setValue(9)
    app.mainW.ui.altitudeMin.setValue(10)
    app.mainW.ui.altitudeMax.setValue(60)
    suc = app.mainW.genBuildGrid()
    assert not suc


def test_genBuildMax_1(qtbot):
    app.mainW.ui.checkAutoDeletePoints.setChecked(False)
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildMax()
        assert suc


def test_genBuildMax_1b(qtbot):
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildMax()
        assert suc


def test_genBuildMax_2(qtbot):
    with mock.patch.object(app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.genBuildMax()
            assert not suc
        assert ['Build points [max] cannot be generated', 2] == blocker.args


def test_genBuildMed_1(qtbot):
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildMed()
        assert suc


def test_genBuildMed_1b(qtbot):
    app.mainW.ui.checkAutoDeletePoints.setChecked(False)
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildMed()
        assert suc


def test_genBuildMed_2(qtbot):
    with mock.patch.object(app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.genBuildMed()
            assert not suc
        assert ['Build points [med] cannot be generated', 2] == blocker.args


def test_genBuildNorm_1(qtbot):
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildNorm()
        assert suc


def test_genBuildNorm_1b(qtbot):
    app.mainW.ui.checkAutoDeletePoints.setChecked(False)
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildNorm()
        assert suc


def test_genBuildNorm_2(qtbot):
    with mock.patch.object(app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.genBuildNorm()
            assert not suc
        assert ['Build points [norm] cannot be generated', 2] == blocker.args


def test_genBuildMin_1(qtbot):
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildMin()
        assert suc


def test_genBuildMin_1b(qtbot):
    app.mainW.ui.checkAutoDeletePoints.setChecked(False)
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildMin()
        assert suc


def test_genBuildMin_2(qtbot):
    with mock.patch.object(app.data,
                           'genGreaterCircle',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.genBuildMin()
            assert not suc
        assert ['Build points [min] cannot be generated', 2] == blocker.args


def test_genBuildDSO_1(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.genBuildDSO()
        assert not suc
    assert ['DSO Path cannot be generated', 2] == blocker.args


def test_genBuildDSO_2(qtbot):
    with mock.patch.object(app.data,
                           'generateDSOPath',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.genBuildDSO()
            assert not suc
        assert ['DSO Path cannot be generated', 2] == blocker.args


def test_genBuildGoldenSpiral_1(qtbot):
    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.genBuildGoldenSpiral()
        assert suc


def test_genBuildGoldenSpiral_2(qtbot):
    with mock.patch.object(app.data,
                           'generateGoldenSpiral',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.genBuildGoldenSpiral()
            assert not suc
        assert ['Golden spiral cannot be generated', 2] == blocker.args


def test_loadBuildFile_1(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'loadBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadBuildFile()
                assert suc
            assert ['Build file [test] loaded', 0] == blocker.args


def test_loadBuildFile_2(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('', '', '')):
        suc = app.mainW.loadBuildFile()
        assert not suc


def test_loadBuildFile_3(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'loadBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadBuildFile()
                assert suc
            assert ['Build file [test] cannot no be loaded', 2] == blocker.args


def test_saveBuildFile_1(qtbot):
    app.mainW.ui.buildPFileName.setText('test')
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'saveBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveBuildFile()
                assert suc
            assert ['Build file [test] saved', 0] == blocker.args


def test_saveBuildFile_2(qtbot):
    app.mainW.ui.buildPFileName.setText('')
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.saveBuildFile()
        assert not suc
    assert ['Build points file name not given', 2] == blocker.args


def test_saveBuildFile_3(qtbot):
    app.mainW.ui.buildPFileName.setText('test')
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'saveBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveBuildFile()
                assert suc
            assert ['Build file [test] cannot no be saved', 2] == blocker.args


def test_saveBuildFileAs_1(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'saveBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveBuildFileAs()
                assert suc
            assert ['Build file [test] saved', 0] == blocker.args


def test_saveBuildFileAs_2(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('', '', '')):
        suc = app.mainW.saveBuildFileAs()
        assert not suc


def test_saveBuildFileAs_3(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'saveBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveBuildFileAs()
                assert suc
            assert ['Build file [test] cannot no be saved', 2] == blocker.args


def test_genBuildFile_1(qtbot):
    app.mainW.ui.buildPFileName.setText('')
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.genBuildFile()
        assert not suc
    assert ['Build points file name not given', 2] == blocker.args


def test_genBuildFile_2(qtbot):
    app.mainW.ui.buildPFileName.setText('test')
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with mock.patch.object(app.data,
                           'loadBuildP',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.genBuildFile()
            assert not suc
        assert ['Build points file [test] could not be loaded', 2] == blocker.args


def test_genBuildFile_3(qtbot):
    app.mainW.ui.buildPFileName.setText('test')
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with mock.patch.object(app.data,
                           'loadBuildP',
                           return_value=True):
        suc = app.mainW.genBuildFile()
        assert suc


def test_genBuildFile_4(qtbot):
    app.mainW.ui.buildPFileName.setText('test')
    app.mainW.ui.checkAutoDeletePoints.setChecked(False)
    with mock.patch.object(app.data,
                           'loadBuildP',
                           return_value=True):
        suc = app.mainW.genBuildFile()
        assert suc


def test_updateProgress_1():
    app.mainW.startModeling = time.time()
    suc = app.mainW.updateProgress()
    assert not suc


def test_updateProgress_2():
    app.mainW.startModeling = time.time()
    suc = app.mainW.updateProgress(number=3, count=2)
    assert suc


def test_updateProgress_3():
    app.mainW.startModeling = time.time()
    suc = app.mainW.updateProgress(number=2, count=3)
    assert not suc


def test_updateProgress_4():
    suc = app.mainW.updateProgress(number=0, count=2)
    app.mainW.startModeling = time.time()
    assert not suc


def test_updateProgress_5():
    app.mainW.startModeling = time.time()
    suc = app.mainW.updateProgress(number=3, count=0)
    assert suc


def test_updateProgress_6():
    app.mainW.startModeling = time.time()
    suc = app.mainW.updateProgress(number=3, count=-1)
    assert not suc


def test_updateProgress_7():
    app.mainW.startModeling = time.time()
    suc = app.mainW.updateProgress(number=3, count=3, modelingDone=True)
    assert not suc


def test_addResultToModel_1():
    class Julian:
        ut1 = 2458635.168

    solve = Solve(raJ2000=0, decJ2000=0, angle=0, scale=1, error=1, flipped=False)
    result = Solution(success=True, solve=solve)
    mPoint = MPoint(mParam=list(),
                    iParam=list(),
                    point=list(),
                    mData=MData(raMJNow=0,
                                decMJNow=0,
                                raSJNow=0,
                                decSJNow=0,
                                sidereal=0,
                                julian=Julian(),
                                pierside='E'),
                    rData=list())

    mPoint = app.mainW.addResultToModel(mPoint=mPoint, result=result)
    assert mPoint.mData.raSJNow.hours == 0.016163840047991124
    assert mPoint.mData.decSJNow.degrees == 0.10534288528388286


def test_modelSolveDone_1():
    suc = app.mainW.modelSolveDone(result=tuple())
    assert not suc


def test_modelSolveDone_2():
    app.mainW.resultQueue.put(MPoint)
    suc = app.mainW.modelSolveDone(result=tuple())
    assert not suc


def test_modelSolveDone_3(qtbot):
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry=''),
                    iParam=list(),
                    point=list(),
                    mData=list(),
                    rData=list())

    with mock.patch.object(app.mainW.resultQueue,
                           'get',
                           return_value=mPoint):
        result = Solution(success=False, solve=tuple())
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.modelSolveDone(result=result)
            assert suc
        assert ['Solving error for image-003', 2] == blocker.args


def test_modelSolveDone_5():
    app.mainW.resultQueue.put(MPoint)
    result = Solution(success=True, solve=None)
    suc = app.mainW.modelSolveDone(result=result)
    assert not suc


def test_modelSolveDone_6():
    class Julian:
        ut1 = 2458635.168

    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry=''),
                    iParam=list(),
                    point=list(),
                    mData=MData(raMJNow=0,
                                decMJNow=0,
                                raSJNow=0,
                                decSJNow=0,
                                sidereal=0,
                                julian=Julian(),
                                pierside='E'),
                    rData=RData(errorRA=1,
                                errorDEC=2,
                                errorRMS=3))

    with mock.patch.object(app.mainW.resultQueue,
                           'get',
                           return_value=mPoint):
        solve = Solve(raJ2000=0, decJ2000=0, angle=0, scale=1, error=1, flipped=False)
        result = Solution(success=True, solve=solve)
        suc = app.mainW.modelSolveDone(result=result)
        assert suc


def test_modelSolveDone_7():
    app.mainW.resultQueue.put(MPoint)
    result = (True, 'test')
    suc = app.mainW.modelSolveDone(result=result)
    assert not suc

"""
def test_modelSolve_1():
    suc = app.mainW.modelSolve()
    assert not suc


def test_modelSolve_2():
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry=''),
                    iParam=list(),
                    point=list(),
                    mData=list(),
                    rData=list())
    app.mainW.solveQueue.put(mPoint)
    with mock.patch.object(app.astrometry,
                           'solveThreading'):
        suc = app.mainW.modelSolve()
        assert suc


def test_modelImage_1():
    suc = app.mainW.modelImage()
    assert not suc


def test_modelImage_2():
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry=''),
                    iParam=IParam(expTime=1,
                                  binning=1,
                                  subFrame=100,
                                  fast=False),
                    point=list(),
                    mData=list(),
                    rData=list())
    app.mainW.imageQueue.put(mPoint)
    with mock.patch.object(app.imaging,
                           'expose'):
        suc = app.mainW.modelImage()
        assert suc


def test_modelSlew_1():
    suc = app.mainW.modelSlew()
    assert not suc


def test_modelSlew_2():
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry=''),
                    iParam=list(),
                    point=Point(azimuth=0,
                                altitude=0),
                    mData=list(),
                    rData=list())
    app.mainW.slewQueue.put(mPoint)
    with mock.patch.object(app.imaging,
                           'expose'):
        suc = app.mainW.modelSlew()
        assert suc


def test_clearQueues():
    suc = app.mainW.clearQueues()
    assert suc


def test_prepareGUI():
    suc = app.mainW.prepareGUI()
    assert suc


def test_defaultGUI():
    suc = app.mainW.defaultGUI()
    assert suc


def test_prepareSignals():
    suc = app.mainW.prepareSignals()
    assert suc


def test_defaultSignals():
    suc = app.mainW.defaultSignals()
    assert suc


def test_cancelFull(qtbot):
    suc = app.mainW.prepareSignals()
    assert suc
    with mock.patch.object(app.imaging,
                           'abort'):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.cancelFull()
            assert suc
        assert blocker.args == ['Modeling cancelled', 2]


def test_retrofitModel_1():
    pass