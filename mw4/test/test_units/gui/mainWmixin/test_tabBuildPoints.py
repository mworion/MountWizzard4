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
import time
# external packages
import skyfield.api
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


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


def test_genBuildDSO_3(qtbot):
    app.mount.obsSite.raJNow = 0
    app.mount.obsSite.decJNow = 0
    with mock.patch.object(app.data,
                           'generateDSOPath',
                           return_value=True):
        suc = app.mainW.genBuildDSO()
        assert suc


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
def test_updateAlignGui_numberStars():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.numberStars = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '50' == app.mainW.ui.numberStars.text()
        assert '50' == app.mainW.ui.numberStars1.text()
        value = None
        app.mount.model.numberStars = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '-' == app.mainW.ui.numberStars.text()
        assert '-' == app.mainW.ui.numberStars1.text()


def test_updateAlignGui_altitudeError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.altitudeError = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert ' 50.0' == app.mainW.ui.altitudeError.text()
        value = None
        app.mount.model.altitudeError = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '-' == app.mainW.ui.altitudeError.text()


def test_updateAlignGui_errorRMS():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.errorRMS = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '50.0' == app.mainW.ui.errorRMS.text()
        assert '50.0' == app.mainW.ui.errorRMS1.text()
        value = None
        app.mount.model.errorRMS = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '-' == app.mainW.ui.errorRMS.text()
        assert '-' == app.mainW.ui.errorRMS1.text()


def test_updateAlignGui_azimuthError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.azimuthError = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert ' 50.0' == app.mainW.ui.azimuthError.text()
        value = None
        app.mount.model.azimuthError = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '-' == app.mainW.ui.azimuthError.text()


def test_updateAlignGui_terms():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.terms = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '50.0' == app.mainW.ui.terms.text()
        value = None
        app.mount.model.terms = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '-' == app.mainW.ui.terms.text()


def test_updateAlignGui_orthoError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.orthoError = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '3000.00' == app.mainW.ui.orthoError.text()
        value = None
        app.mount.model.orthoError = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '-' == app.mainW.ui.orthoError.text()


def test_updateAlignGui_positionAngle():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.positionAngle = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert ' 50.0' == app.mainW.ui.positionAngle.text()
        value = None
        app.mount.model.positionAngle = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '-' == app.mainW.ui.positionAngle.text()


def test_updateAlignGui_polarError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.polarError = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '3000.00' == app.mainW.ui.polarError.text()
        value = None
        app.mount.model.polarError = value
        app.mainW.updateAlignGUI(app.mount.model)
        assert '-' == app.mainW.ui.polarError.text()


def test_updateTurnKnobsGUI_altitudeTurns_1():
    value = 1.5
    app.mount.model.altitudeTurns = value
    app.mainW.updateTurnKnobsGUI(app.mount.model)
    assert '1.5 revs down' == app.mainW.ui.altitudeTurns.text()
    value = None
    app.mount.model.altitudeTurns = value
    app.mainW.updateTurnKnobsGUI(app.mount.model)
    assert '-' == app.mainW.ui.altitudeTurns.text()


def test_updateTurnKnobsGUI_altitudeTurns_2():
    value = -1.5
    app.mount.model.altitudeTurns = value
    app.mainW.updateTurnKnobsGUI(app.mount.model)
    assert '1.5 revs up' == app.mainW.ui.altitudeTurns.text()
    value = None
    app.mount.model.altitudeTurns = value
    app.mainW.updateTurnKnobsGUI(app.mount.model)
    assert '-' == app.mainW.ui.altitudeTurns.text()


def test_updateTurnKnobsGUI_azimuthTurns_1():
    value = 1.5
    app.mount.model.azimuthTurns = value
    app.mainW.updateTurnKnobsGUI(app.mount.model)
    assert '1.5 revs left' == app.mainW.ui.azimuthTurns.text()
    value = None
    app.mount.model.azimuthTurns = value
    app.mainW.updateTurnKnobsGUI(app.mount.model)
    assert '-' == app.mainW.ui.azimuthTurns.text()


def test_updateTurnKnobsGUI_azimuthTurns_2():
    value = -1.5
    app.mount.model.azimuthTurns = value
    app.mainW.updateTurnKnobsGUI(app.mount.model)
    assert '1.5 revs right' == app.mainW.ui.azimuthTurns.text()
    value = None
    app.mount.model.azimuthTurns = value
    app.mainW.updateTurnKnobsGUI(app.mount.model)
    assert '-' == app.mainW.ui.azimuthTurns.text()