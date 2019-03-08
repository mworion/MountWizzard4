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
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp
from mw4.test.test_setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_loadAlignBuildFile_1(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'loadBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadAlignBuildFile()
                assert suc
            assert ['Align build file [test] loaded', 0] == blocker.args


def test_loadAlignBuildFile_2(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('', '', '')):
        suc = app.mainW.loadAlignBuildFile()
        assert not suc


def test_loadAlignBuildFile_3(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'loadBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadAlignBuildFile()
                assert suc
            assert ['Align build file [test] cannot no be loaded', 2] == blocker.args


def test_saveAlignBuildFile_1(qtbot):
    app.mainW.ui.alignBuildPFileName.setText('test')
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'saveBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveAlignBuildFile()
                assert suc
            assert ['Align build file [test] saved', 0] == blocker.args


def test_saveAlignBuildFile_2(qtbot):
    app.mainW.ui.alignBuildPFileName.setText('')
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.saveAlignBuildFile()
        assert not suc
    assert ['Align build points file name not given', 2] == blocker.args


def test_saveAlignBuildFile_3(qtbot):
    app.mainW.ui.alignBuildPFileName.setText('test')
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'saveBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveAlignBuildFile()
                assert suc
            assert ['Align build file [test] cannot no be saved', 2] == blocker.args


def test_saveAlignBuildFileAs_1(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'saveBuildP',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveAlignBuildFileAs()
                assert suc
            assert ['Align build file [test] saved', 0] == blocker.args


def test_saveAlignBuildFileAs_2(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('', '', '')):
        suc = app.mainW.saveAlignBuildFileAs()
        assert not suc


def test_saveAlignBuildFileAs_3(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('build', 'test', 'bpts')):
        with mock.patch.object(app.data,
                               'saveBuildP',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveAlignBuildFileAs()
                assert suc
            assert ['Align build file [test] cannot no be saved', 2] == blocker.args


def test_genAlignBuildFile_1(qtbot):
    app.mainW.ui.alignBuildPFileName.setText('')
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.genAlignBuildFile()
        assert not suc
    assert ['Align build points file name not given', 2] == blocker.args


def test_genAlignBuildFile_2(qtbot):
    app.mainW.ui.alignBuildPFileName.setText('test')
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with mock.patch.object(app.data,
                           'loadBuildP',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.genAlignBuildFile()
            assert not suc
        assert ['Align build points file [test] could not be loaded', 2] == blocker.args


def test_genAlignBuildFile_3(qtbot):
    app.mainW.ui.alignBuildPFileName.setText('test')
    app.mainW.ui.checkAutoDeletePoints.setChecked(True)
    with mock.patch.object(app.data,
                           'loadBuildP',
                           return_value=True):
        suc = app.mainW.genAlignBuildFile()
        assert suc


def test_genAlignBuildFile_4(qtbot):
    app.mainW.ui.alignBuildPFileName.setText('test')
    app.mainW.ui.checkAutoDeletePoints.setChecked(False)
    with mock.patch.object(app.data,
                           'loadBuildP',
                           return_value=True):
        suc = app.mainW.genAlignBuildFile()
        assert suc


def test_genAlignBuild_1():
    app.mainW.ui.altBase.setValue(50)
    app.mainW.ui.azBase.setValue(30)
    app.mainW.ui.numberBase.setValue(5)
    suc = app.mainW.genAlignBuild()
    assert suc


def test_genAlignBuild_2():
    app.mainW.ui.altBase.setValue(50)
    app.mainW.ui.azBase.setValue(30)
    app.mainW.ui.numberBase.setValue(30)
    suc = app.mainW.genAlignBuild()
    assert suc


def test_updateAlignGui_numberStars():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.numberStars = value
        app.mainW.updateAlignGUI()
        assert '50' == app.mainW.ui.numberStars.text()
        assert '50' == app.mainW.ui.numberStars1.text()
        value = None
        app.mount.model.numberStars = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.numberStars.text()
        assert '-' == app.mainW.ui.numberStars1.text()


def test_updateAlignGui_altitudeError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.altitudeError = value
        app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == app.mainW.ui.altitudeError.text()
        value = None
        app.mount.model.altitudeError = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.altitudeError.text()


def test_updateAlignGui_errorRMS():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.errorRMS = value
        app.mainW.updateAlignGUI()
        assert '50.0' == app.mainW.ui.errorRMS.text()
        assert '50.0' == app.mainW.ui.errorRMS1.text()
        value = None
        app.mount.model.errorRMS = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.errorRMS.text()
        assert '-' == app.mainW.ui.errorRMS1.text()


def test_updateAlignGui_azimuthError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.azimuthError = value
        app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == app.mainW.ui.azimuthError.text()
        value = None
        app.mount.model.azimuthError = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.azimuthError.text()


def test_updateAlignGui_terms():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.terms = value
        app.mainW.updateAlignGUI()
        assert '50.0' == app.mainW.ui.terms.text()
        value = None
        app.mount.model.terms = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.terms.text()


def test_updateAlignGui_orthoError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.orthoError = value
        app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == app.mainW.ui.orthoError.text()
        value = None
        app.mount.model.orthoError = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.orthoError.text()


def test_updateAlignGui_positionAngle():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.positionAngle = value
        app.mainW.updateAlignGUI()
        assert ' 50.0' == app.mainW.ui.positionAngle.text()
        value = None
        app.mount.model.positionAngle = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.positionAngle.text()


def test_updateAlignGui_polarError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.polarError = value
        app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == app.mainW.ui.polarError.text()
        value = None
        app.mount.model.polarError = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.polarError.text()


def test_updateTurnKnobsGUI_altitudeTurns_1():
    value = 1.5
    app.mount.model.altitudeTurns = value
    app.mainW.updateTurnKnobsGUI()
    assert '1.5 revs down' == app.mainW.ui.altitudeTurns.text()
    value = None
    app.mount.model.altitudeTurns = value
    app.mainW.updateTurnKnobsGUI()
    assert '-' == app.mainW.ui.altitudeTurns.text()


def test_updateTurnKnobsGUI_altitudeTurns_2():
    value = -1.5
    app.mount.model.altitudeTurns = value
    app.mainW.updateTurnKnobsGUI()
    assert '1.5 revs up' == app.mainW.ui.altitudeTurns.text()
    value = None
    app.mount.model.altitudeTurns = value
    app.mainW.updateTurnKnobsGUI()
    assert '-' == app.mainW.ui.altitudeTurns.text()


def test_updateTurnKnobsGUI_azimuthTurns_1():
    value = 1.5
    app.mount.model.azimuthTurns = value
    app.mainW.updateTurnKnobsGUI()
    assert '1.5 revs left' == app.mainW.ui.azimuthTurns.text()
    value = None
    app.mount.model.azimuthTurns = value
    app.mainW.updateTurnKnobsGUI()
    assert '-' == app.mainW.ui.azimuthTurns.text()


def test_updateTurnKnobsGUI_azimuthTurns_2():
    value = -1.5
    app.mount.model.azimuthTurns = value
    app.mainW.updateTurnKnobsGUI()
    assert '1.5 revs right' == app.mainW.ui.azimuthTurns.text()
    value = None
    app.mount.model.azimuthTurns = value
    app.mainW.updateTurnKnobsGUI()
    assert '-' == app.mainW.ui.azimuthTurns.text()
