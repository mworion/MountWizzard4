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
# GUI with PyQT5 for python !

#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import time
import os
import shutil
import glob
import json

# external packages
import skyfield.api
from skyfield.api import Angle
from mountcontrol.modelStar import ModelStar

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabModel import Model
import gui.mainWaddon
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    class Mixin(MWidget, Model):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = {}
            self.refreshName = None
            self.refreshModel = None
            self.setupFilenamesAndDirectories = None
            self.setupRunPoints = None
            self.playSound = None
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Model.__init__(self)

    window = Mixin()
    yield window

    files = glob.glob('tests/workDir/model/m-*.model')
    for f in files:
        os.remove(f)
    for path in glob.glob('tests/workDir/image/m-*'):
        shutil.rmtree(path)


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_setModelOperationMode_1(function):
    suc = function.setModelOperationMode(1)
    assert suc


def test_setModelOperationMode_2(function):
    suc = function.setModelOperationMode(2)
    assert suc


def test_setModelOperationMode_3(function):
    suc = function.setModelOperationMode(3)
    assert suc


def test_setModelOperationMode_4(function):
    suc = function.setModelOperationMode(0)
    assert suc


def test_setModelOperationMode_5(function):
    suc = function.setModelOperationMode(4)
    assert suc


def test_updateAlignGui_numberStars(function):
    function.updateAlignGUI(function.app.mount.model)
    assert ' 1' == function.ui.numberStars.text()
    assert ' 1' == function.ui.numberStars1.text()


def test_updateAlignGui_altitudeError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert '  0.0' == function.ui.altitudeError.text()


def test_updateAlignGui_errorRMS_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert '  1.0' == function.ui.errorRMS.text()
    assert '  1.0' == function.ui.errorRMS1.text()


def test_updateAlignGui_azimuthError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert '  0.0' == function.ui.azimuthError.text()


def test_updateAlignGui_terms_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert ' 1' == function.ui.terms.text()


def test_updateAlignGui_orthoError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert '    0' == function.ui.orthoError.text()


def test_updateAlignGui_positionAngle_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert '  0.0' == function.ui.positionAngle.text()


def test_updateAlignGui_polarError_1(function):
    function.updateAlignGUI(function.app.mount.model)
    assert '    0' == function.ui.polarError.text()


def test_updateTurnKnobsGUI_1(function):
    class Test:
        azimuthTurns = None
        altitudeTurns = None

    function.updateTurnKnobsGUI(Test())
    assert '-' == function.ui.altitudeTurns.text()
    assert '-' == function.ui.azimuthTurns.text()


def test_updateTurnKnobsGUI_2(function):
    class Test:
        azimuthTurns = -1
        altitudeTurns = -1

    function.updateTurnKnobsGUI(Test())
    assert '1.0 revs up' == function.ui.altitudeTurns.text()
    assert '1.0 revs right' == function.ui.azimuthTurns.text()


def test_updateTurnKnobsGUI_3(function):
    class Test:
        azimuthTurns = 1
        altitudeTurns = 1

    function.updateTurnKnobsGUI(Test())
    assert '1.0 revs down' == function.ui.altitudeTurns.text()
    assert '1.0 revs left' == function.ui.azimuthTurns.text()


def test_updateModelProgress_1(function):
    function.timeStartModeling = time.time()
    mPoint = {}
    suc = function.updateModelProgress(mPoint)
    assert not suc


def test_updateModelProgress_2(function):
    function.timeStartModeling = time.time()
    mPoint = {'lenSequence': 3,
              'countSequence': 2}
    suc = function.updateModelProgress(mPoint)
    assert suc


def test_updateModelProgress_3(function):
    function.timeStartModeling = time.time()
    mPoint = {'lenSequence': 2,
              'countSequence': 3}
    suc = function.updateModelProgress(mPoint)
    assert not suc


def test_updateModelProgress_4(function):
    mPoint = {'lenSequence': 0,
              'countSequence': 2}
    suc = function.updateModelProgress(mPoint)
    function.timeStartModeling = time.time()
    assert not suc


def test_updateModelProgress_5(function):
    function.timeStartModeling = time.time()
    mPoint = {'lenSequence': 3,
              'countSequence': 1}
    suc = function.updateModelProgress(mPoint)
    assert suc


def test_updateModelProgress_6(function):
    function.timeStartModeling = time.time()
    mPoint = {'lenSequence': 3,
              'countSequence': -1}
    suc = function.updateModelProgress(mPoint)
    assert not suc


def test_updateModelProgress_7(function):
    function.timeStartModeling = time.time()
    mPoint = {'lenSequence': 3,
              'countSequence': 2}
    suc = function.updateModelProgress(mPoint)
    assert suc


def test_updateModelProgress_8(function):
    function.timeStartModeling = time.time()
    mPoint = {'lenSequence': 0,
              'countSequence': -1}
    suc = function.updateModelProgress(mPoint)
    assert not suc


def test_setupModelRunContextAndGuiStatus_1(function):
    function.app.uiWindows = {'showImageW': {'classObj': None}}
    suc = function.setupModelRunContextAndGuiStatus()
    assert suc


def test_pauseBuild_1(function):
    function.ui.pauseModel.setProperty('pause', True)
    suc = function.pauseBuild()
    assert suc
    assert not function.ui.pauseModel.property('pause')


def test_pauseBuild_2(function):
    function.ui.pauseModel.setProperty('pause', False)
    suc = function.pauseBuild()
    assert suc
    assert function.ui.pauseModel.property('pause')


def writeRFD(a, b):
    return {}


@mock.patch('gui.mainWmixin.tabManageModel.writeRetrofitData', writeRFD)
def test_retrofitModel_1(function):
    function.app.mount.model.starList = list()

    point = ModelStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0),
                      obsSite=function.app.mount.obsSite)
    stars = list()
    stars.append(point)
    mPoint = {}
    function.model = list()
    function.model.append(mPoint)
    suc = function.retrofitModel()
    assert suc


def test_saveModelFinish_1(function):
    def test():
        return

    shutil.copy('tests/testData/test.model', 'tests/workDir/model/test.model')
    function.modelName = 'test'
    function.generateSaveData = test
    function.app.mount.signals.alignDone.connect(function.saveModelFinish)
    suc = function.saveModelFinish()
    assert suc


def test_generateBuildData_1(function):
    build = function.generateBuildData()
    assert build == []


def test_generateBuildData_2(function):
    function.model = [
        {
            "altitude": 44.556745182012854,
            "azimuth": 37.194805194805184,
            "binning": 1.0,
            "countSequence": 0,
            "decJNowS": 64.3246,
            "decJNowM": 64.32841185357267,
            "errorDEC": -229.0210134131381,
            "errorRMS": 237.1,
            "errorRA": -61.36599559380768,
            "exposureTime": 3.0,
            "fastReadout": True,
            "julianDate": "2019-06-08T08:57:57Z",
            "name": "m-file-2019-06-08-08-57-44",
            "lenSequence": 3,
            "imagePath": "/Users/mw/PycharmProjects/MountWizzard4/image/m-file-2019-06-08-08"
                         "-57-44/image-000.fits",
            "pierside": "W",
            "raJNowS": 8.42882,
            "raJNowM": 8.427692953132278,
            "siderealTime": skyfield.api.Angle(hours=12.5),
            "subFrame": 100.0
        },
    ]

    build = function.generateBuildData()
    assert build[0].sCoord.dec.degrees == 64.3246


def test_programModelToMount_1(function):
    function.model = []
    with mock.patch.object(function,
                           'generateBuildData',
                           return_value=[]):
        with mock.patch.object(function.app.mount.model,
                               'programAlign',
                               return_value=False):
            suc = function.programModelToMount()
            assert not suc


def test_programModelToMount_2(function):
    function.model = []
    with mock.patch.object(function,
                           'generateBuildData',
                           return_value=[1, 2, 3]):
        with mock.patch.object(function.app.mount.model,
                               'programAlign',
                               return_value=False):
            suc = function.programModelToMount()
            assert not suc


def test_programModelToMount_3(function):
    with mock.patch.object(function,
                           'generateBuildData',
                           return_value=[1, 2, 3]):
        with mock.patch.object(function.app.mount.model,
                               'programAlign',
                               return_value=True):
            with mock.patch.object(function,
                                   'refreshName'):
                with mock.patch.object(function,
                                       'refreshModel'):
                    suc = function.programModelToMount()
                    assert suc


def test_renewHemisphereView_1(function):
    function.app.data.buildP = [(0, 0, True), (1, 1, True), (2, 2, True)]

    with mock.patch.object(function.app.data,
                           'setStatusBuildP'):
        suc = function.renewHemisphereView()
        assert suc


def test_processModelData_1(function):
    suc = function.processModelData([])
    assert not suc


def test_processModelData_2(function):
    def playSound(a):
        return

    function.playSound = playSound
    with mock.patch.object(function,
                           'programModelToMount',
                           return_value=False):
        with mock.patch.object(function,
                               'renewHemisphereView'):
            with mock.patch.object(function.app.mount.obsSite,
                                   'park',
                                   return_value=False):
                suc = function.processModelData([0, 1, 2])
                assert suc


def test_processModelData_3(function):
    def playSound(a):
        return

    function.playSound = playSound
    function.ui.parkMountAfterModel.setChecked(True)
    with mock.patch.object(function,
                           'programModelToMount',
                           return_value=True):
        with mock.patch.object(function,
                               'renewHemisphereView'):
            with mock.patch.object(function.app.mount.obsSite,
                                   'park',
                                   return_value=False):
                suc = function.processModelData([0, 1, 2])
                assert suc


def test_processModelData_4(function):
    def playSound(a):
        return

    function.playSound = playSound
    function.ui.parkMountAfterModel.setChecked(True)
    with mock.patch.object(function,
                           'programModelToMount',
                           return_value=True):
        with mock.patch.object(function,
                               'renewHemisphereView'):
            with mock.patch.object(function.app.mount.obsSite,
                                   'park',
                                   return_value=True):
                suc = function.processModelData([0, 1, 2])
                assert suc


def test_checkModelRunConditions_1(function):
    function.app.data.buildP = [(0, 0, True)]
    suc = function.checkModelRunConditions()
    assert not suc


def test_checkModelRunConditions_2(function):
    function.app.data.buildP = [(0, 0, True)] * 100
    suc = function.checkModelRunConditions()
    assert not suc


def test_checkModelRunConditions_3(function):
    function.app.data.buildP = [(0, 0, True)] * 2
    function.ui.excludeDonePoints.setChecked(True)
    suc = function.checkModelRunConditions()
    assert not suc


def test_checkModelRunConditions_4(function):
    function.app.data.buildP = [(0, 0, True)] * 5
    with mock.patch.object(function.ui.plateSolveDevice,
                           'currentText',
                           return_value='No device'):
        suc = function.checkModelRunConditions()
        assert not suc


def test_checkModelRunConditions_5(function):
    function.app.data.buildP = [(0, 0, True)] * 5
    with mock.patch.object(function.app.plateSolve,
                           'checkAvailability',
                           return_value=(False, False)):
        suc = function.checkModelRunConditions()
        assert not suc


def test_checkModelRunConditions_6(function):
    function.app.data.buildP = [(0, 0, True)] * 5
    with mock.patch.object(function.app.plateSolve,
                           'checkAvailability',
                           return_value=(True, True)):
        suc = function.checkModelRunConditions()
        assert suc


def test_clearAlignAndBackup_1(function):
    with mock.patch.object(function.app.mount.model,
                           'clearAlign',
                           return_value=False):
        suc = function.clearAlignAndBackup()
        assert not suc


def test_clearAlignAndBackup_2(function):
    with mock.patch.object(function.app.mount.model,
                           'clearAlign',
                           return_value=True):
        with mock.patch.object(function.app.mount.model,
                               'deleteName',
                               return_value=False):
            with mock.patch.object(function,
                                   'refreshModel'):
                with mock.patch.object(gui.mainWmixin.tabModel,
                                       'sleepAndEvents'):
                    suc = function.clearAlignAndBackup()
                    assert suc


def test_clearAlignAndBackup_3(function):
    with mock.patch.object(function.app.mount.model,
                           'clearAlign',
                           return_value=True):
        with mock.patch.object(function.app.mount.model,
                               'deleteName',
                               return_value=True):
            with mock.patch.object(function,
                                   'refreshModel'):
                with mock.patch.object(function.app.mount.model,
                                       'storeName',
                                       return_value=False):
                    with mock.patch.object(gui.mainWmixin.tabModel,
                                           'sleepAndEvents'):
                        suc = function.clearAlignAndBackup()
                        assert suc


def test_clearAlignAndBackup_4(function):
    with mock.patch.object(function.app.mount.model,
                           'clearAlign',
                           return_value=True):
        with mock.patch.object(function.app.mount.model,
                               'deleteName',
                               return_value=True):
            with mock.patch.object(function.app.mount.model,
                                   'storeName',
                                   return_value=True):
                with mock.patch.object(function,
                                       'refreshModel'):
                    with mock.patch.object(gui.mainWmixin.tabModel,
                                           'sleepAndEvents'):
                        suc = function.clearAlignAndBackup()
                        assert suc


def test_modelBuild_1(function):
    function.lastGenerator = 'test'
    with mock.patch.object(function,
                           'setupFilenamesAndDirectories',
                           return_value=('', '')):
        with mock.patch.object(function,
                               'checkModelRunConditions',
                               return_value=False):
            suc = function.modelBuild()
            assert not suc


def test_modelBuild_2(function):
    function.lastGenerator = 'test'
    with mock.patch.object(function,
                           'checkModelRunConditions',
                           return_value=True):
        with mock.patch.object(function,
                               'setupFilenamesAndDirectories',
                               return_value=('', '')):
            with mock.patch.object(function,
                                   'clearAlignAndBackup',
                                   return_value=False):
                suc = function.modelBuild()
                assert not suc


def test_modelBuild_3(function):
    function.lastGenerator = ''
    with mock.patch.object(function,
                           'checkModelRunConditions',
                           return_value=True):
        with mock.patch.object(function,
                               'clearAlignAndBackup',
                               return_value=True):
            with mock.patch.object(function,
                                   'setupFilenamesAndDirectories',
                                   return_value=('', '')):
                with mock.patch.object(function,
                                       'setupRunPoints',
                                       return_value=[]):
                    suc = function.modelBuild()
                    assert not suc


def test_modelBuild_4(function):
    def test(modelPoints=None,
             retryCounter=None,
             runType=None,
             processData=None,
             progress=None,
             imgDir=None,
             keepImages=None):
        return

    function.lastGenerator = ''
    function.cycleThroughPoints = test
    function.ui.excludeDonePoints.setChecked(True)
    function.app.data.buildP = [(0, 0, True), (10, 10, False), (20, 20, True)]
    with mock.patch.object(function,
                           'checkModelRunConditions',
                           return_value=True):
        with mock.patch.object(function,
                               'clearAlignAndBackup',
                               return_value=True):
            with mock.patch.object(function,
                                   'setupFilenamesAndDirectories',
                                   return_value=('', '')):
                with mock.patch.object(function,
                                       'setupRunPoints',
                                       return_value=[1, 2]):
                    with mock.patch.object(function,
                                           'setupModelRunContextAndGuiStatus'):
                        suc = function.modelBuild()
                        assert suc


def test_loadProgramModel_1(function):
    def openFile(a, b, c, d, multiple=False):
        return ([],
                [],
                [])
    function.openFile = openFile

    suc = function.loadProgramModel()
    assert not suc


def test_loadProgramModel_2(function):
    shutil.copy('tests/testData/test.model', 'tests/workDir/model/test.model')

    def openFile(a, b, c, d, multiple=False):
        return ('tests/workDir/model/test.model',
                'test',
                '.model')
    function.openFile = openFile

    with mock.patch.object(function,
                           'clearAlignAndBackup',
                           return_value=False):
        suc = function.loadProgramModel()
        assert not suc


def test_loadProgramModel_3(function):
    shutil.copy('tests/testData/test.model', 'tests/workDir/model/test.model')

    def openFile(a, b, c, d, multiple=False):
        return (['tests/workDir/model/test.model'],
                ['test'],
                ['.model'])
    function.openFile = openFile

    with mock.patch.object(function,
                           'clearAlignAndBackup',
                           return_value=True):
        with mock.patch.object(function,
                               'programModelToMount',
                               return_value=False):
            suc = function.loadProgramModel()
            assert not suc


def test_loadProgramModel_4(function):
    shutil.copy('tests/testData/test.model', 'tests/workDir/model/test.model')

    def openFile(a, b, c, d, multiple=False):
        return (['tests/workDir/model/test.model'],
                ['test'],
                ['.model'])
    function.openFile = openFile

    with mock.patch.object(function,
                           'clearAlignAndBackup',
                           return_value=True):
        with mock.patch.object(function,
                               'programModelToMount',
                               return_value=True):
            suc = function.loadProgramModel()
            assert suc


def test_loadProgramModel_5(function):
    shutil.copy('tests/testData/test.model', 'tests/workDir/model/test.model')

    def openFile(a, b, c, d, multiple=False):
        return (['tests/workDir/model/test.model'],
                ['test'],
                ['.model'])
    function.openFile = openFile

    with mock.patch.object(function,
                           'clearAlignAndBackup',
                           return_value=True):
        with mock.patch.object(function,
                               'programModelToMount',
                               return_value=True):
            with mock.patch.object(json,
                                   'load',
                                   return_value={},
                                   side_effect=Exception):
                suc = function.loadProgramModel()
                assert suc


def test_loadProgramModel_6(function):
    shutil.copy('tests/testData/test.model', 'tests/workDir/model/test.model')
    shutil.copy('tests/testData/test1.model', 'tests/workDir/model/test1.model')

    def openFile(a, b, c, d, multiple=False):
        return (['tests/workDir/model/test.model',
                 'tests/workDir/model/test1.model'],
                ['test', 'test1'],
                ['.model', '.model'])
    function.openFile = openFile

    with mock.patch.object(function,
                           'clearAlignAndBackup',
                           return_value=True):

        suc = function.loadProgramModel()
        assert not suc


def test_solveDone_1(function):
    function.app.plateSolve.signals.done.connect(function.solveDone)
    suc = function.solveDone()
    assert not suc


def test_solveDone_2(function):
    result = {
        'success': False,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'message': 'test',
    }

    function.app.plateSolve.signals.done.connect(function.solveDone)
    suc = function.solveDone(result=result)
    assert not suc


def test_solveDone_3(function):
    result = {
        'success': True,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'message': 'test',
        'solvedPath': 'test'
    }

    function.app.plateSolve.signals.done.connect(function.solveDone)
    with mock.patch.object(function.app.mount.obsSite,
                           'syncPositionToTarget',
                           return_value=True):
        suc = function.solveDone(result=result)
        assert suc


def test_solveDone_4(function):
    result = {
        'success': True,
        'raJ2000S': Angle(hours=10),
        'decJ2000S': Angle(degrees=20),
        'angleS': 30,
        'scaleS': 1,
        'errorRMS_S': 3,
        'flippedS': False,
        'imagePath': 'test',
        'message': 'test',
        'solvedPath': 'test'
    }

    function.app.plateSolve.signals.done.connect(function.solveDone)
    with mock.patch.object(function.app.mount.obsSite,
                           'syncPositionToTarget',
                           return_value=False):
        suc = function.solveDone(result=result)
        assert not suc


def test_solveImage_1(function):
    suc = function.solveImage()
    assert not suc


def test_solveImage_2(function):
    suc = function.solveImage(imagePath='testFile')
    assert not suc


def test_solveImage_3(function):
    shutil.copy('tests/testData/m51.fit', 'tests/workDir/image/m51.fit')
    file = 'tests/workDir/image/m51.fit'
    with mock.patch.object(function.app.plateSolve,
                           'solveThreading'):
        suc = function.solveImage(imagePath=file)
        assert suc


def test_exposeRaw_1(function, qtbot):
    with mock.patch.object(function.app.camera,
                           'expose'):
        suc = function.exposeRaw(3, 1, 100, False, 100)
        assert suc


def test_exposeImageDone_1(function):
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with mock.patch.object(function,
                           'solveImage'):
        suc = function.exposeImageDone()
        assert suc


def test_exposeImage_1(function):
    with mock.patch.object(function,
                           'exposeRaw'):
        suc = function.exposeImage()
        assert suc


def test_plateSolveSync_1(function):
    with mock.patch.object(function.app.plateSolve,
                           'checkAvailability',
                           return_value=(False, False)):
        suc = function.plateSolveSync()
        assert not suc


def test_plateSolveSync_2(function):
    with mock.patch.object(function.app.plateSolve,
                           'checkAvailability',
                           return_value=(True, True)):
        with mock.patch.object(function,
                               'exposeImage'):
            suc = function.plateSolveSync()
            assert suc
