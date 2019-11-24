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
import os
import shutil
import glob
# external packages
import skyfield.api
from mountcontrol.modelStar import ModelStar
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.mainW.lastGenerator = 'test'
    yield
    files = glob.glob(mwGlob['modelDir'] + '/m-*.model')
    for f in files:
        os.remove(f)
    for path in glob.glob(mwGlob['imageDir'] + '/m-*'):
        shutil.rmtree(path)


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


def test_updateProgress_8():
    app.mainW.startModeling = time.time()
    suc = app.mainW.updateProgress(count=-1)
    assert not suc


def test_modelSolveDone_1():
    suc = app.mainW.modelSolveDone(result={})
    assert not suc


def test_modelSolveDone_3(qtbot):
    mPoint = {'lenSequence': 3,
              'countSequence': 3}

    app.mainW.resultQueue.put(mPoint)

    result = {'raJ2000S': 0,
              'decJ2000S': 0,
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 1,
              'flippedS': False,
              'success': False,
              'message': 'test',
              }

    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.modelSolveDone(result=result)
        assert suc
    assert ['Solving error for image-003: test', 2] == blocker.args


def test_modelSolveDone_6():
    mPoint = {'lenSequence': 3,
              'countSequence': 3}

    app.mainW.resultQueue.put(mPoint)

    class Julian:
        ut1 = 2458635.168

    result = {'raJ2000S': skyfield.api.Angle(hours=0),
              'decJ2000S': skyfield.api.Angle(degrees=0),
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 1,
              'flippedS': False,
              'success': True,
              'message': 'test',
              'raJNowM': skyfield.api.Angle(hours=0),
              'decJNowM': skyfield.api.Angle(degrees=0),
              'raJNowS': skyfield.api.Angle(hours=0),
              'decJNowS': skyfield.api.Angle(degrees=0),
              'siderealTime': 0,
              'julianDate': Julian(),
              'pierside': 'E',
              'errorRA': 1,
              'errorDEC': 2,
              'errorRMS': 3,
              }

    app.mainW.resultQueue.put(mPoint)
    suc = app.mainW.modelSolveDone(result=result)
    assert suc


def test_modelSolveDone_7():
    mPoint = {'lenSequence': 3,
              'countSequence': 3}

    result = {'raJ2000S': skyfield.api.Angle(hours=0),
              'decJ2000S': skyfield.api.Angle(degrees=0),
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 1,
              'flippedS': False,
              'success': True,
              'message': 'test',
              }

    app.mainW.resultQueue.put(mPoint)

    suc = app.mainW.modelSolveDone(result=result)
    assert suc


def test_modelSolve_1():
    suc = app.mainW.modelSolve()
    assert not suc


def test_modelSolve_2():
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'searchRadius': 1,
              'solveTimeout': 10,

              }

    app.mainW.solveQueue.put(mPoint)
    with mock.patch.object(app.astrometry,
                           'solveThreading'):
        suc = app.mainW.modelSolve()
        assert suc


def test_modelImage_1():
    suc = app.mainW.modelImage()
    assert not suc


def test_modelImage_2():
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              }

    app.mainW.imageQueue.put(mPoint)
    with mock.patch.object(app.imaging,
                           'expose'):
        suc = app.mainW.modelImage()
        assert suc


def test_modelSlew_1():
    suc = app.mainW.modelSlew()
    assert not suc


def test_modelSlew_2():
    app.mainW.deviceStat['dome'] = False
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              'azimuth': 0,
              'altitude': 0,
              }

    app.mainW.slewQueue.put(mPoint)
    with mock.patch.object(app.imaging,
                           'expose'):
        suc = app.mainW.modelSlew()
        assert not suc


def test_modelSlew_3():
    app.mainW.deviceStat['dome'] = True
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              'azimuth': 0,
              'altitude': 0,
              }
    app.mainW.slewQueue.put(mPoint)
    with mock.patch.object(app.imaging,
                           'expose'):
        with mock.patch.object(app.mount.obsSite,
                               'setTargetAltAz',
                               return_value=True):
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
            suc = app.mainW.cancelBuild()
            assert suc
        assert blocker.args == ['Modeling cancelled', 2]


def test_retrofitModel_1():
    app.mount.model.starList = list()

    point = ModelStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0))
    stars = list()
    stars.append(point)
    stars.append(point)
    stars.append(point)

    mPoint = {}
    app.mainW.model = list()
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)

    suc = app.mainW.retrofitModel()
    assert suc
    assert app.mainW.model == []


def test_retrofitModel_3():
    app.mount.model.starList = list()
    point = ModelStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0))
    app.mount.model.addStar(point)
    app.mount.model.addStar(point)

    mPoint = {}
    app.mainW.model = list()
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)

    suc = app.mainW.retrofitModel()
    assert suc


def test_saveModel_1():
    suc = app.mainW.saveModel()
    assert not suc


def test_saveModel_2():
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': 'testPath',
              'name': 'test',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              'azimuth': 0,
              'altitude': 0,
              }

    app.mainW.model = list()
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)

    suc = app.mainW.saveModel()
    assert not suc


def test_saveModel_3():
    class Julian:
        ut1 = 2458635.168

    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': 'testPath',
              'name': 'test',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              'azimuth': 0,
              'altitude': 0,
              'raJNowM': skyfield.api.Angle(hours=0),
              'decJNowM': skyfield.api.Angle(degrees=0),
              'raJNowS': skyfield.api.Angle(hours=0),
              'decJNowS': skyfield.api.Angle(degrees=0),
              'siderealTime': 0,
              'julianDate': Julian(),
              'pierside': 'E',
              'errorRA': 1,
              'errorDEC': 2,
              'errorRMS': 3,
              }

    app.mainW.model = list()
    app.mainW.modelName = 'test'
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)

    suc = app.mainW.saveModel()
    assert suc


def test_saveModel_4():
    class Julian:
        @staticmethod
        def utc_iso():
            return 2458635.168

    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': 'testPath',
              'name': 'test',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              'azimuth': 0,
              'altitude': 0,
              'raJ2000S': skyfield.api.Angle(hours=0),
              'decJ2000S': skyfield.api.Angle(degrees=0),
              'raJNowM': skyfield.api.Angle(hours=0),
              'decJNowM': skyfield.api.Angle(degrees=0),
              'raJNowS': skyfield.api.Angle(hours=0),
              'decJNowS': skyfield.api.Angle(degrees=0),
              'siderealTime': skyfield.api.Angle(hours=0),
              'julianDate': Julian(),
              'pierside': 'E',
              'errorRA': 1,
              'errorDEC': 2,
              'errorRMS': 3,
              }
    app.mainW.model = list()
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)
    app.mainW.model.append(mPoint)

    suc = app.mainW.saveModel()
    assert suc

    os.remove(mwGlob['modelDir'] + '/test.model')


def test_generateBuildData_1():
    inputData = [
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

    build = app.mainW.generateBuildData(inputData)
    assert build[0].sCoord.dec.degrees == 64.3246


def test_modelFinished_1(qtbot):
    class Julian:
        ut1 = 2458635.168

    inputData = {
         'raJ2000S': skyfield.api.Angle(hours=0),
         'decJ2000S': skyfield.api.Angle(degrees=0),
         'angleS': 0,
         'scaleS': 1,
         'errorRMS_S': 1,
         'flippedS': False,
         'success': True,
         'message': 'test',
         'raJNowM': skyfield.api.Angle(hours=0),
         'decJNowM': skyfield.api.Angle(degrees=0),
         'raJNowS': skyfield.api.Angle(hours=0),
         'decJNowS': skyfield.api.Angle(degrees=0),
         'siderealTime': skyfield.api.Angle(hours=0),
         'julianDate': Julian(),
         'pierside': 'E',
         'errorRA': 1,
         'errorDEC': 2,
         'errorRMS': 3,
         }

    app.mainW.modelQueue.put(inputData)

    app.imaging.signals.saved.connect(app.mainW.modelSolve)
    app.imaging.signals.integrated.connect(app.mainW.modelSlew)
    app.astrometry.signals.done.connect(app.mainW.modelSolveDone)
    app.mainW.collector.ready.connect(app.mainW.modelImage)

    with mock.patch.object(app.mount.model,
                           'programAlign',
                           return_value=False):
        suc = app.mainW.modelFinished()
        assert suc


def test_modelFinished_2(qtbot):
    class Julian:
        ut1 = 2458635.168

    inputData = {
         'raJ2000S': skyfield.api.Angle(hours=0),
         'decJ2000S': skyfield.api.Angle(degrees=0),
         'angleS': 0,
         'scaleS': 1,
         'errorRMS_S': 1,
         'flippedS': False,
         'success': True,
         'message': 'test',
         'raJNowM': skyfield.api.Angle(hours=0),
         'decJNowM': skyfield.api.Angle(degrees=0),
         'raJNowS': skyfield.api.Angle(hours=0),
         'decJNowS': skyfield.api.Angle(degrees=0),
         'siderealTime': skyfield.api.Angle(hours=0),
         'julianDate': Julian(),
         'pierside': 'E',
         'errorRA': 1,
         'errorDEC': 2,
         'errorRMS': 3,
         }


    app.mainW.modelQueue.put(inputData)

    app.imaging.signals.saved.connect(app.mainW.modelSolve)
    app.imaging.signals.integrated.connect(app.mainW.modelSlew)
    app.astrometry.signals.done.connect(app.mainW.modelSolveDone)
    app.mainW.collector.ready.connect(app.mainW.modelImage)

    with mock.patch.object(app.mount.model,
                           'programAlign',
                           return_value=True):
        suc = app.mainW.modelFinished()
        assert suc


def test_modelCore_1():
    app.mainW.ui.astrometryDevice.setCurrentIndex(0)
    with mock.patch.object(app.mainW,
                           'modelSlew'):
        suc = app.mainW.modelCore(points=[(0, 0)])
        assert not suc


def test_modelCore_2():
    app.mainW.ui.astrometryDevice.setCurrentIndex(1)
    with mock.patch.object(app.mainW,
                           'modelSlew'):
        suc = app.mainW.modelCore()
        assert not suc


def test_modelCore_3():
    app.mainW.ui.astrometryDevice.setCurrentIndex(1)
    with mock.patch.object(app.mainW,
                           'modelSlew'):
        suc = app.mainW.modelCore(points=[(0, 0)])
        assert suc


def test_modelFull_1():
    with mock.patch.object(app.mainW,
                           'modelCore',
                           return_value=False):
        suc = app.mainW.modelBuild()
        assert not suc


def test_modelFull_2():
    app.mainW.genBuildMin()
    with mock.patch.object(app.mainW,
                           'modelCore',
                           return_value=True):
        suc = app.mainW.modelBuild()
        assert suc


def test_loadProgramModel_1():
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('', '', '')):
        with mock.patch.object(app.mount.model,
                               'programAlign',
                               return_value=True):
            suc = app.mainW.loadProgramModel()
            assert not suc


def test_loadProgramModel_2():
    modelDir = mwGlob['modelDir'] + '/test.test'
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=(modelDir, 'm-test', '.model')):
        with mock.patch.object(app.mount.model,
                               'programAlign',
                               return_value=True):
            suc = app.mainW.loadProgramModel()
            assert suc
