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
# Python  v3.7.4
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
# external packages
import skyfield.api
from mountcontrol.model import AlignStar
# local import
from mw4.test.test_units.setupQt import setupQt
from mw4.definitions import Solution, Solve, MPoint, MData, MParam, IParam, Point, RData


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


def test_addResultToModel_1():
    class Julian:
        ut1 = 2458635.168

    solve = Solve(raJ2000=skyfield.api.Angle(degrees=0),
                  decJ2000=skyfield.api.Angle(degrees=0),
                  angle=0, scale=1, error=1, flipped=False, path='')
    result = Solution(success=True, solve=solve)
    mPoint = MPoint(mParam=tuple(),
                    iParam=tuple(),
                    point=tuple(),
                    mData=MData(raMJNow=skyfield.api.Angle(degrees=0),
                                decMJNow=skyfield.api.Angle(degrees=0),
                                raSJNow=skyfield.api.Angle(degrees=0),
                                decSJNow=skyfield.api.Angle(degrees=0),
                                sidereal=0,
                                julian=Julian(),
                                pierside='E'),
                    rData=tuple())

    mPoint = app.mainW.addResultToModel(mPoint=mPoint, result=result)
    assert mPoint.mData.raSJNow.hours == 0.016163840047991124
    assert mPoint.mData.decSJNow.degrees == 0.10534288528388286


def test_modelSolveDone_1():
    suc = app.mainW.modelSolveDone(result=tuple())
    assert not suc


def test_modelSolveDone_2():
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry='',
                                  timeout=10,
                                  radius=1,
                                  ),
                    iParam=tuple(),
                    point=tuple(),
                    mData=tuple(),
                    rData=tuple())
    app.mainW.resultQueue.put(mPoint)
    suc = app.mainW.modelSolveDone(result=Solve)
    assert not suc


def test_modelSolveDone_3(qtbot):
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry='',
                                  timeout=10,
                                  radius=1,
                                  ),
                    iParam=tuple(),
                    point=tuple(),
                    mData=tuple(),
                    rData=tuple())

    app.mainW.resultQueue.put(mPoint)
    solve = Solve(raJ2000=0, decJ2000=0, angle=0, scale=1, error=1, flipped=False, path='')
    result = Solution(success=False, solve=solve)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.modelSolveDone(result=result)
        assert suc
    assert ['Solving error for image-003', 2] == blocker.args


def test_modelSolveDone_5():
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry='',
                                  timeout=10,
                                  radius=1,
                                  ),
                    iParam=tuple(),
                    point=tuple(),
                    mData=tuple(),
                    rData=tuple())

    app.mainW.resultQueue.put(mPoint)
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
                                  timeout=10,
                                  radius=1,
                                  astrometry=''),
                    iParam=tuple(),
                    point=tuple(),
                    mData=MData(raMJNow=skyfield.api.Angle(hours=0),
                                decMJNow=skyfield.api.Angle(degrees=0),
                                raSJNow=skyfield.api.Angle(degrees=0),
                                decSJNow=skyfield.api.Angle(degrees=0),
                                sidereal=0,
                                julian=Julian(),
                                pierside='E'),
                    rData=RData(errorRA=1,
                                errorDEC=2,
                                errorRMS=3))

    app.mainW.resultQueue.put(mPoint)
    solve = Solve(raJ2000=skyfield.api.Angle(hours=0),
                  decJ2000=skyfield.api.Angle(degrees=0),
                  angle=0, scale=1, error=1, flipped=False, path='')
    result = Solution(success=True, solve=solve)
    suc = app.mainW.modelSolveDone(result=result)
    assert suc


def test_modelSolveDone_7():
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  astrometry='',
                                  timeout=10,
                                  radius=1,
                                  ),
                    iParam=tuple(),
                    point=tuple(),
                    mData=tuple(),
                    rData=tuple())

    app.mainW.resultQueue.put(mPoint)

    result = (True, 'test')
    suc = app.mainW.modelSolveDone(result=result)
    assert not suc


def test_modelSolve_1():
    suc = app.mainW.modelSolve()
    assert not suc


def test_modelSolve_2():
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='',
                                  name='',
                                  timeout=10,
                                  radius=1,
                                  astrometry=''),
                    iParam=tuple(),
                    point=tuple(),
                    mData=tuple(),
                    rData=tuple())
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
                                  timeout=10,
                                  radius=1,
                                  astrometry=''),
                    iParam=IParam(expTime=1,
                                  binning=1,
                                  subFrame=100,
                                  fastReadout=False),
                    point=tuple(),
                    mData=tuple(),
                    rData=tuple())
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
                                  timeout=10,
                                  radius=1,
                                  astrometry=''),
                    iParam=tuple(),
                    point=Point(azimuth=0,
                                altitude=0),
                    mData=tuple(),
                    rData=tuple())
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
    app.mount.model.starList = list()
    point = AlignStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0))
    stars = list()
    stars.append(point)
    stars.append(point)
    stars.append(point)

    mPoint = MPoint
    model = list()
    model.append(mPoint)
    model.append(mPoint)
    model.append(mPoint)

    val = app.mainW.retrofitModel()
    assert val == list()


def test_retrofitModel_2():
    app.mount.model.starList = list()
    point = AlignStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0))
    app.mount.model.addStar(point)
    app.mount.model.addStar(point)
    app.mount.model.addStar(point)

    mPoint = MPoint
    model = list()
    model.append(mPoint)
    model.append(mPoint)
    model.append(mPoint)

    val = app.mainW.retrofitModel(model=model)
    assert len(val) == 3


def test_retrofitModel_3():
    app.mount.model.starList = list()
    point = AlignStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0))
    app.mount.model.addStar(point)
    app.mount.model.addStar(point)

    mPoint = MPoint
    model = list()
    model.append(mPoint)
    model.append(mPoint)
    model.append(mPoint)

    val = app.mainW.retrofitModel(model=model)
    assert val == list()


def test_retrofitModel_4():
    app.mount.model.starList = list()
    point = AlignStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0))
    app.mount.model.addStar(point)
    app.mount.model.addStar(point)
    app.mount.model.addStar(point)

    mPoint = MPoint
    model = list()
    model.append(mPoint)
    model.append(mPoint)

    val = app.mainW.retrofitModel(model=model)
    assert val == list()


def test_saveModel_1():
    suc = app.mainW.saveModel()
    assert not suc


def test_saveModel_2():
    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='testPath',
                                  name='test',
                                  timeout=10,
                                  radius=1,
                                  astrometry='astrometry'),
                    iParam=tuple(),
                    point=Point(azimuth=0,
                                altitude=0),
                    mData=tuple(),
                    rData=tuple())
    model = list()
    model.append(mPoint)
    model.append(mPoint)

    suc = app.mainW.saveModel(model=model)
    assert not suc


def test_saveModel_3():

    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='testPath',
                                  name='test',
                                  timeout=10,
                                  radius=1,
                                  astrometry='astrometry'),
                    iParam=IParam(expTime=1,
                                  binning=1,
                                  subFrame=100,
                                  fastReadout=False),
                    point=Point(azimuth=0,
                                altitude=0),
                    mData=MData(raMJNow=skyfield.api.Angle(hours=0),
                                decMJNow=skyfield.api.Angle(degrees=0),
                                raSJNow=skyfield.api.Angle(hours=0),
                                decSJNow=skyfield.api.Angle(degrees=0),
                                sidereal=skyfield.api.Angle(hours=0),
                                julian=app.mount.obsSite.timeJD,
                                pierside='E'),
                    rData=RData(errorRA=1,
                                errorDEC=2,
                                errorRMS=3))
    model = list()
    model.append(mPoint)
    model.append(mPoint)
    model.append(mPoint)

    suc = app.mainW.saveModel(model=model)
    assert not suc


def test_saveModel_4():

    mPoint = MPoint(mParam=MParam(number=3,
                                  count=3,
                                  path='testPath',
                                  name='test',
                                  timeout=10,
                                  radius=1,
                                  astrometry='astrometry'),
                    iParam=IParam(expTime=1,
                                  binning=1,
                                  subFrame=100,
                                  fastReadout=False),
                    point=Point(azimuth=0,
                                altitude=0),
                    mData=MData(raMJNow=skyfield.api.Angle(hours=0),
                                decMJNow=skyfield.api.Angle(degrees=0),
                                raSJNow=skyfield.api.Angle(hours=0),
                                decSJNow=skyfield.api.Angle(degrees=0),
                                sidereal=skyfield.api.Angle(hours=0),
                                julian=app.mount.obsSite.timeJD,
                                pierside='E'),
                    rData=RData(errorRA=1,
                                errorDEC=2,
                                errorRMS=3))
    model = list()
    model.append(mPoint)
    model.append(mPoint)
    model.append(mPoint)

    suc = app.mainW.saveModel(model=model, name='test')
    assert suc

    os.remove(mwGlob['modelDir'] + '/test.model')


def test_collectModelData():
    app.mainW.modelQueue.put('test')
    model = app.mainW.collectModelData()
    assert model[0] == 'test'


def test_generateBuildDataFromJSON_1():
    inputData = [
        {
            "altitude": 44.556745182012854,
            "azimuth": 37.194805194805184,
            "binning": 1.0,
            "count": 0,
            "decMJNow": 64.3246,
            "decSJNow": 64.32841185357267,
            "errorDEC": -229.0210134131381,
            "errorRMS": 237.1,
            "errorRa": -61.36599559380768,
            "expTime": 3.0,
            "fastReadout": True,
            "julian": "2019-06-08T08:57:57Z",
            "name": "m-file-2019-06-08-08-57-44",
            "number": 3,
            "path": "/Users/mw/PycharmProjects/MountWizzard4/image/m-file-2019-06-08-08-57-44/image-000.fits",
            "pierside": "W",
            "raMJNow": 8.42882,
            "raSJNow": 8.427692953132278,
            "sidereal": 12.5,
            "subFrame": 100.0
        },
    ]

    build = app.mainW.generateBuildDataFromJSON(inputData)
    assert build[0].mCoord.dec.degrees == 64.3246


def test_generateBuildData_1():
    inputData = [
        MPoint(MParam,
               MPoint,
               IParam,
               MData(raMJNow=skyfield.api.Angle(hours=0),
                     decMJNow=skyfield.api.Angle(degrees=64.3246),
                     raSJNow=skyfield.api.Angle(hours=0),
                     decSJNow=skyfield.api.Angle(degrees=0),
                     sidereal=0,
                     julian=0,
                     pierside='E'),
               RData)
    ]

    build = app.mainW.generateBuildData(inputData)
    assert build[0].mCoord.dec.degrees == 64.3246


def test_modelFinished_1(qtbot):
    inputData = MPoint(mParam=MParam(number=3,
                                     count=3,
                                     path='',
                                     name='',
                                     astrometry='',
                                     timeout=10,
                                     radius=1,
                                     ),
                       iParam=tuple(),
                       point=tuple(),
                       mData=MData(raMJNow=skyfield.api.Angle(hours=0),
                                   decMJNow=skyfield.api.Angle(degrees=64.3246),
                                   raSJNow=skyfield.api.Angle(hours=0),
                                   decSJNow=skyfield.api.Angle(degrees=0),
                                   sidereal=0,
                                   julian=0,
                                   pierside='E'),
                       rData=RData(errorRA=1,
                                   errorDEC=2,
                                   errorRMS=3))

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
    inputData = MPoint(mParam=MParam(number=3,
                                     count=3,
                                     path='',
                                     name='',
                                     astrometry='',
                                     timeout=10,
                                     radius=1,
                                     ),
                       iParam=tuple(),
                       point=tuple(),
                       mData=MData(raMJNow=skyfield.api.Angle(hours=0),
                                   decMJNow=skyfield.api.Angle(degrees=64.3246),
                                   raSJNow=skyfield.api.Angle(hours=0),
                                   decSJNow=skyfield.api.Angle(degrees=0),
                                   sidereal=0,
                                   julian=0,
                                   pierside='E'),
                       rData=RData(errorRA=1,
                                   errorDEC=2,
                                   errorRMS=3))

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
        suc = app.mainW.modelFull()
        assert not suc


def test_modelFull_2():
    app.mainW.genBuildMin()
    with mock.patch.object(app.mainW,
                           'modelCore',
                           return_value=True):
        suc = app.mainW.modelFull()
        assert suc


def test_modelAlign_1():
    with mock.patch.object(app.mainW,
                           'modelCore',
                           return_value=False):
        suc = app.mainW.modelAlign()
        assert not suc


def test_modelAlign_2():
    app.mainW.genBuildMin()
    with mock.patch.object(app.mainW,
                           'modelCore',
                           return_value=True):
        suc = app.mainW.modelAlign()
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
    modelDir = mwGlob['modelDir'] + '/m-test.model'
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=(modelDir, 'm-test', '.model')):
        with mock.patch.object(app.mount.model,
                               'programAlign',
                               return_value=True):
            suc = app.mainW.loadProgramModel()
            assert suc
