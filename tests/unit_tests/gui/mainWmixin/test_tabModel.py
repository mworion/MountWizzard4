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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import logging
import pytest
import time
import os
import shutil
import glob

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
import skyfield.api
from skyfield.api import Angle
from skyfield.api import Topos
from mountcontrol.modelStar import ModelStar

# local import
from gui.mainWmixin.tabModel import Model
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.widget import MWidget
from logic.imaging.camera import Camera
from logic.dome.dome import Dome
from logic.astrometry.astrometry import Astrometry
from base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def app(qtbot):

    class Test1(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        update1s = pyqtSignal()
        update10s = pyqtSignal()
        threadPool = QThreadPool()
        mwGlob = {'modelDir': 'tests/model',
                  'imageDir': 'tests/image',
                  'tempDir': 'tests/temp'}

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        showImage = pyqtSignal(str)
        __version__ = 'test'
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        camera = Camera(app=Test1())
        astrometry = Astrometry(app=Test1())
        dome = Dome(app=Test1())
        mwGlob = {'modelDir': 'tests/model',
                  'imageDir': 'tests/image'}
        uiWindows = {'showImageW': {'classObj': None}}

    def refreshModel():
        return

    def refreshName():
        return

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = Model(app=Test(), ui=ui,
                clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.deviceStat = dict()
    app.lastGenerator = 'test'
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()
    app.refreshName = refreshName
    app.refreshModel = refreshModel

    qtbot.addWidget(app)

    yield app

    app.threadPool.waitForDone(1000)
    files = glob.glob('tests/model/m-*.model')
    for f in files:
        os.remove(f)
    for path in glob.glob('tests/image/m-*'):
        shutil.rmtree(path)


def test_initConfig_1(app):
    app.app.config['mainW'] = {}
    suc = app.initConfig()
    assert suc


def test_storeConfig_1(app):
    suc = app.storeConfig()
    assert suc


def test_updateProgress_1(app):
    app.startModeling = time.time()
    suc = app.updateProgress()
    assert not suc


def test_updateProgress_2(app):
    app.startModeling = time.time()
    suc = app.updateProgress(number=3, count=2)
    assert suc


def test_updateProgress_3(app):
    app.startModeling = time.time()
    suc = app.updateProgress(number=2, count=3)
    assert not suc


def test_updateProgress_4(app):
    suc = app.updateProgress(number=0, count=2)
    app.startModeling = time.time()
    assert not suc


def test_updateProgress_5(app):
    app.startModeling = time.time()
    suc = app.updateProgress(number=3, count=0)
    assert suc


def test_updateProgress_6(app):
    app.startModeling = time.time()
    suc = app.updateProgress(number=3, count=-1)
    assert not suc


def test_updateProgress_7(app):
    app.startModeling = time.time()
    suc = app.updateProgress(number=3, count=2)
    assert suc


def test_updateProgress_8(app):
    app.startModeling = time.time()
    suc = app.updateProgress(count=-1)
    assert not suc


def test_modelSolveDone_0(qtbot, app):
    result = {'raJ2000S': 0,
              'decJ2000S': 0,
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 1,
              'flippedS': False,
              'success': False,
              'message': 'test',
              }

    suc = app.modelSolveDone(result)
    assert not suc


def test_modelSolveDone_1(qtbot, app):
    mPoint = {'lenSequence': 3,
              'countSequence': 3}

    app.resultQueue.put(mPoint)

    result = {'raJ2000S': 0,
              'decJ2000S': 0,
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 1,
              'flippedS': False,
              'success': False,
              'message': 'test',
              }

    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.modelSolveDone(result)
        assert suc
    assert ['Solving  image-003:  test', 2] == blocker.args


def test_modelSolveDone_2(app):
    mPoint = {'lenSequence': 3,
              'countSequence': 3}

    app.resultQueue.put(mPoint)

    suc = app.modelSolveDone({})
    assert not suc


def test_modelSolveDone_3(app):
    mPoint = {'lenSequence': 3,
              'countSequence': 3}

    app.resultQueue.put(mPoint)

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

    app.resultQueue.put(mPoint)
    suc = app.modelSolveDone(result)
    assert suc


def test_modelSolveDone_4(app):
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
              'julianDate': app.app.mount.obsSite.timeJD,
              }

    app.resultQueue.put(mPoint)

    suc = app.modelSolveDone(result)
    assert suc


def test_modelSolveDone_5(app):
    mPoint = {'lenSequence': 3,
              'countSequence': 2}

    result = {'raJ2000S': skyfield.api.Angle(hours=0),
              'decJ2000S': skyfield.api.Angle(degrees=0),
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 999999999,
              'flippedS': False,
              'success': True,
              'message': 'test',
              'julianDate': app.app.mount.obsSite.timeJD,
              }

    app.startModeling = 0
    app.resultQueue.put(mPoint)

    with mock.patch.object(app,
                           'modelCycleThroughBuildPointsFinished'):
        suc = app.modelSolveDone(result)
        assert suc


def test_modelSolve_1(app):
    suc = app.modelSolve()
    assert not suc


def test_modelSolve_2(app):
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'searchRadius': 1,
              'solveTimeout': 10,

              }

    app.solveQueue.put(mPoint)
    with mock.patch.object(app.app.astrometry,
                           'solveThreading'):
        suc = app.modelSolve()
        assert suc


def test_modelImage_1(app):
    suc = app.modelImage()
    assert not suc


def test_modelImage_2(app):
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              'focalLength': 1,
              }

    app.imageQueue.put(mPoint)
    with mock.patch.object(app.app.camera,
                           'expose'):
        suc = app.modelImage()
        assert suc


def test_modelSlew_1(app):
    suc = app.modelSlew()
    assert not suc


def test_modelSlew_2(app):
    app.deviceStat['dome'] = False
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

    app.slewQueue.put(mPoint)
    with mock.patch.object(app.app.camera,
                           'expose'):
        suc = app.modelSlew()
        assert not suc


def test_modelSlew_3(app):
    app.deviceStat['dome'] = True
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
    app.slewQueue.put(mPoint)
    with mock.patch.object(app.app.camera,
                           'expose'):
        with mock.patch.object(app.app.dome,
                               'slewDome',
                               return_value=0):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                suc = app.modelSlew()
                assert suc


def test_modelSlew_4(app):
    app.deviceStat['dome'] = True
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
    app.slewQueue.put(mPoint)
    app.ui.checkDomeGeometry.setChecked(True)
    with mock.patch.object(app.app.camera,
                           'expose'):
        with mock.patch.object(app.app.dome,
                               'slewDome',
                               return_value=0):
            with mock.patch.object(app.app.mount.obsSite,
                                   'setTargetAltAz',
                                   return_value=True):
                suc = app.modelSlew()
                assert suc


def test_changeStatusDAT_1(app):
    app.ui.checkDisableDAT.setChecked(True)
    app.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(app.app.mount.setting,
                           'setDualAxisTracking'):
        suc = app.disableDAT()
        assert suc
        assert app.statusDAT


def test_changeStatusDAT_2(app):
    app.ui.checkDisableDAT.setChecked(True)
    app.app.mount.setting.statusDualAxisTracking = False
    with mock.patch.object(app.app.mount.setting,
                           'setDualAxisTracking'):
        suc = app.disableDAT()
        assert suc
        assert not app.statusDAT


def test_changeStatusDAT_3(app):
    app.ui.checkDisableDAT.setChecked(True)
    app.statusDAT = True
    app.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(app.app.mount.setting,
                           'setDualAxisTracking'):
        suc = app.disableDAT()
        assert suc
        assert app.statusDAT


def test_changeStatusDAT_4(app):
    app.ui.checkDisableDAT.setChecked(False)
    app.statusDAT = True
    app.app.mount.setting.statusDualAxisTracking = True
    with mock.patch.object(app.app.mount.setting,
                           'setDualAxisTracking'):
        suc = app.disableDAT()
        assert not suc
        assert app.statusDAT


def test_restoreStatusDAT_1(app):
    app.ui.checkDisableDAT.setChecked(True)
    app.statusDAT = None
    suc = app.restoreStatusDAT()
    assert not suc


def test_restoreStatusDAT_2(app):
    app.ui.checkDisableDAT.setChecked(True)
    app.statusDAT = True
    with mock.patch.object(app.app.mount.setting,
                           'setDualAxisTracking'):
        suc = app.restoreStatusDAT()
        assert suc


def test_restoreStatusDAT_3(app):
    app.ui.checkDisableDAT.setChecked(False)
    suc = app.restoreStatusDAT()
    assert not suc


def test_clearQueues(app):
    suc = app.clearQueues()
    assert suc


def test_prepareGUI(app):
    suc = app.prepareGUI()
    assert suc


def test_defaultGUI(app):
    suc = app.restoreModelDefaultContextAndGuiStatus()
    assert suc


def test_prepareSignals_1(app):
    suc = app.setupSignalsForModelRun()
    assert suc


def test_prepareSignals_2(app):
    app.deviceStat['dome'] = True
    app.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 1}

    suc = app.setupSignalsForModelRun()
    assert suc


def test_prepareSignals_3(app):
    app.deviceStat['dome'] = True

    suc = app.setupSignalsForModelRun()
    assert suc


def test_defaultSignals(app):
    app.app.camera.signals.saved.connect(app.modelSolve)
    app.app.camera.signals.integrated.connect(app.modelSlew)
    app.app.astrometry.signals.done.connect(app.modelSolveDone)
    app.collector.ready.connect(app.modelImage)

    suc = app.restoreSignalsModelDefault()
    assert suc


def test_pauseBuild_1(app):
    app.ui.pauseModel.setProperty('pause', True)
    suc = app.pauseBuild()
    assert suc
    assert not app.ui.pauseModel.property('pause')


def test_pauseBuild_2(app):
    app.ui.pauseModel.setProperty('pause', False)
    suc = app.pauseBuild()
    assert suc
    assert app.ui.pauseModel.property('pause')


def test_cancelFull(qtbot, app):
    suc = app.setupSignalsForModelRun()
    assert suc
    with mock.patch.object(app.app.camera,
                           'abort'):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.cancelBuild()
            assert suc
        assert blocker.args == ['Modeling cancelled', 2]


def test_retrofitModel_1(app):
    app.app.mount.model.starList = list()

    point = ModelStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0))
    stars = list()
    stars.append(point)
    stars.append(point)
    stars.append(point)

    mPoint = {}
    app.model = list()
    app.model.append(mPoint)
    app.model.append(mPoint)
    app.model.append(mPoint)

    suc = app.retrofitModel()
    assert suc
    assert app.model == []


def test_retrofitModel_2(app):
    app.app.mount.model.starList = list()
    point = ModelStar(coord=skyfield.api.Star(ra_hours=0, dec_degrees=0),
                      number=1,
                      errorRMS=10,
                      errorAngle=skyfield.api.Angle(degrees=0))
    app.app.mount.model.addStar(point)
    app.app.mount.model.addStar(point)
    app.app.mount.model.addStar(point)
    app.app.mount.model.orthoError = 1
    app.app.mount.model.polarError = 1

    mPoint = {'test': 1}
    app.model = list()
    app.model.append(mPoint)
    app.model.append(mPoint)
    app.model.append(mPoint)

    suc = app.retrofitModel()
    assert suc


def test_generateSaveModel_1(app):
    mPoint = {'raJNowM': Angle(hours=0),
              'decJNowM': Angle(degrees=0),
              'raJNowS': Angle(hours=0),
              'decJNowS': Angle(degrees=0),
              'angularPosRA': Angle(degrees=0),
              'angularPosDEC': Angle(degrees=0),
              'raJ2000S': Angle(hours=0),
              'decJ2000S': Angle(degrees=0),
              'siderealTime': Angle(hours=0),
              'julianDate': app.app.mount.obsSite.timeJD,
              }
    app.model = list()
    app.model.append(mPoint)
    app.model.append(mPoint)
    app.model.append(mPoint)

    val = app.generateSaveModel()
    assert len(val) == 3


def test_saveModelFinish_1(app):
    app.modelName = 'test'
    app.app.mount.signals.alignDone.connect(app.saveModelFinish)
    suc = app.saveModelFinish()
    assert suc


def test_saveModel_1(app):
    suc = app.saveModelPrepare()
    assert not suc


def test_saveModel_2(app):
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

    app.model = list()
    app.model.append(mPoint)
    app.model.append(mPoint)

    suc = app.saveModelPrepare()
    assert not suc


def test_saveModel_3(app):
    class Julian:
        ut1 = 2458635.168

    def refreshModel():
        return

    app.refreshModel = refreshModel

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

    app.model = list()
    app.modelName = 'test'
    app.model.append(mPoint)
    app.model.append(mPoint)
    app.model.append(mPoint)

    suc = app.saveModelPrepare()
    assert suc


def test_saveModel_4(app):
    class Julian:
        @staticmethod
        def utc_iso():
            return 2458635.168

    def refreshModel():
        return
    app.refreshModel = refreshModel

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
    app.model = list()
    app.model.append(mPoint)
    app.model.append(mPoint)
    app.model.append(mPoint)

    suc = app.saveModelPrepare()
    assert suc


def test_generateBuildData_1(app):
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

    build = app.generateBuildData(inputData)
    assert build[0].sCoord.dec.degrees == 64.3246


def test_modelFinished_1(qtbot, app):
    class Julian:
        ut1 = 2458635.168

    def playSound(a):
        return
    app.playSound = playSound

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

    app.modelQueue.put(inputData)

    app.app.camera.signals.saved.connect(app.modelSolve)
    app.app.camera.signals.integrated.connect(app.modelSlew)
    app.app.astrometry.signals.done.connect(app.modelSolveDone)
    app.collector.ready.connect(app.modelImage)

    with mock.patch.object(app.app.mount.model,
                           'programAlign',
                           return_value=False):
        suc = app.modelCycleThroughBuildPointsFinished()
        assert not suc


def test_modelFinished_2(qtbot, app):
    class Julian:
        ut1 = 2458635.168

    def playSound(a):
        return
    app.playSound = playSound

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

    app.modelQueue.put(inputData)
    app.modelQueue.put(inputData)
    app.modelQueue.put(inputData)

    app.app.camera.signals.saved.connect(app.modelSolve)
    app.app.camera.signals.integrated.connect(app.modelSlew)
    app.app.astrometry.signals.done.connect(app.modelSolveDone)
    app.collector.ready.connect(app.modelImage)

    with mock.patch.object(app.app.mount.model,
                           'programAlign',
                           return_value=True):
        suc = app.modelCycleThroughBuildPointsFinished()
        assert suc


def test_modelFinished_3(qtbot, app):
    class Julian:
        ut1 = 2458635.168

    def playSound(a):
        return
    app.playSound = playSound

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

    app.modelQueue.put(inputData)
    app.modelQueue.put(inputData)
    app.modelQueue.put(inputData)

    app.app.camera.signals.saved.connect(app.modelSolve)
    app.app.camera.signals.integrated.connect(app.modelSlew)
    app.app.astrometry.signals.done.connect(app.modelSolveDone)
    app.collector.ready.connect(app.modelImage)

    app.ui.checkEnableBackup.setChecked(True)
    with mock.patch.object(app.app.mount.model,
                           'programAlign',
                           return_value=True):
        suc = app.modelCycleThroughBuildPointsFinished()
        assert suc


def test_modelCore_1(app):
    app.ui.astrometryDevice.setCurrentIndex(0)
    with mock.patch.object(app,
                           'modelSlew'):
        suc = app.modelCycleThroughBuildPoints(points=[(0, 0)])
        assert not suc


def test_modelCore_2(app):
    app.ui.astrometryDevice.setCurrentIndex(1)
    with mock.patch.object(app,
                           'modelSlew'):
        suc = app.modelCycleThroughBuildPoints()
        assert not suc


def test_modelCore_3(app):
    app.ui.astrometryDevice.setCurrentIndex(1)
    with mock.patch.object(app,
                           'modelSlew'):
        suc = app.modelCycleThroughBuildPoints(points=[(0, 0)])
        assert not suc


def test_modelCore_4(app):
    app.ui.astrometryDevice.setCurrentIndex(1)
    with mock.patch.object(app,
                           'modelSlew'):
        suc = app.modelCycleThroughBuildPoints(points=[(0, 0), (0, 0), (0, 0)])
        assert suc


def test_modelBuild_1(app):
    class Test:
        buildP = {}

    app.app.data = Test()

    with mock.patch.object(app,
                           'modelCycleThroughBuildPoints',
                           return_value=True):
        suc = app.modelBuild()
        assert not suc


def test_modelBuild_2(app):
    class Test:
        buildP = [(90, 90), (90, 90), (90, 90)]

    app.app.data = Test()

    with mock.patch.object(app,
                           'modelCycleThroughBuildPoints',
                           return_value=True):
        suc = app.modelBuild()
        assert not suc


def test_modelBuild_2a(app):
    class Test:
        buildP = [(90, 90), (90, 90), (90, 90)]

    app.app.data = Test()

    with mock.patch.object(app,
                           'modelCycleThroughBuildPoints',
                           return_value=True):
        with mock.patch.object(app.app.mount.model,
                               'clearAlign',
                               return_value=True):
            with mock.patch.object(app.app.astrometry,
                                   'checkAvailability',
                                   return_value=(True, True)):
                suc = app.modelBuild()
                assert suc


def test_modelBuild_3(app):
    class Test:
        buildP = [(1, 1)] * 100

    app.app.data = Test()

    with mock.patch.object(app,
                           'modelCycleThroughBuildPoints',
                           return_value=True):
        with mock.patch.object(app.app.astrometry,
                               'checkAvailability',
                               return_value=(True, True)):
            suc = app.modelBuild()
            assert not suc


def test_modelBuild_4(app):
    class Test:
        buildP = [(1, 1)] * 10

    app.app.data = Test()

    with mock.patch.object(app,
                           'modelCycleThroughBuildPoints',
                           return_value=False):
        with mock.patch.object(app.app.astrometry,
                               'checkAvailability',
                               return_value=(True, True)):
            suc = app.modelBuild()
            assert not suc


def test_modelBuild_5(app):
    class Test:
        buildP = [(1, 1)] * 10

    app.app.data = Test()

    with mock.patch.object(app,
                           'modelCycleThroughBuildPoints',
                           return_value=False):
        with mock.patch.object(app.app.mount.model,
                               'clearAlign',
                               return_value=False):
            with mock.patch.object(app.app.astrometry,
                                   'checkAvailability',
                                   return_value=(True, True)):
                suc = app.modelBuild()
                assert not suc


def test_modelBuild_6(app):
    class Test:
        buildP = [(1, 1)] * 10

    app.app.data = Test()

    with mock.patch.object(app,
                           'modelCycleThroughBuildPoints',
                           return_value=True):
        with mock.patch.object(app.app.mount.model,
                               'clearAlign',
                               return_value=True):
            with mock.patch.object(app.app.astrometry,
                                   'checkAvailability',
                                   return_value=(True, True)):
                suc = app.modelBuild()
                assert suc


def test_loadProgramModel_1(app):
    def openFile(a, b, c, d, multiple=False):
        return ('', '', '')

    app.openFile = openFile

    with mock.patch.object(app.app.mount.model,
                           'programAlign',
                           return_value=True):
        suc = app.loadProgramModel()
        assert not suc


def test_loadProgramModel_2(app):
    shutil.copy('tests/testData/m-test.model', 'tests/model/m-test.model')

    def openFile(a, b, c, d, multiple=False):
        return ('tests/model/m-test.model', 'm-test', '.model')
    app.openFile = openFile

    def refreshModel():
        return
    app.refreshModel = refreshModel

    with mock.patch.object(app.app.mount.model,
                           'programAlign',
                           return_value=True):
        with mock.patch.object(app.app.mount.model,
                               'clearAlign',
                               return_value=True):
            suc = app.loadProgramModel()
            assert suc


def test_updateAlignGui_numberStars(app):
    value = '50'
    app.app.mount.model.numberStars = value
    app.updateAlignGUI(app.app.mount.model)
    assert ' 50' == app.ui.numberStars.text()
    assert ' 50' == app.ui.numberStars1.text()
    value = None
    app.app.mount.model.numberStars = value
    app.updateAlignGUI(app.app.mount.model)
    assert '-' == app.ui.numberStars.text()
    assert '-' == app.ui.numberStars1.text()


def test_updateAlignGui_altitudeError(app):
    value = '50'
    app.app.mount.model.altitudeError = value
    app.updateAlignGUI(app.app.mount.model)
    assert ' 50.0' == app.ui.altitudeError.text()
    value = None
    app.app.mount.model.altitudeError = value
    app.updateAlignGUI(app.app.mount.model)
    assert '-' == app.ui.altitudeError.text()


def test_updateAlignGui_errorRMS(app):
    value = '50'
    app.app.mount.model.errorRMS = value
    app.updateAlignGUI(app.app.mount.model)
    assert '50.0' == app.ui.errorRMS.text()
    assert '50.0' == app.ui.errorRMS1.text()
    value = None
    app.app.mount.model.errorRMS = value
    app.updateAlignGUI(app.app.mount.model)
    assert '-' == app.ui.errorRMS.text()
    assert '-' == app.ui.errorRMS1.text()


def test_updateAlignGui_azimuthError(app):
    value = '50'
    app.app.mount.model.azimuthError = value
    app.updateAlignGUI(app.app.mount.model)
    assert ' 50.0' == app.ui.azimuthError.text()
    value = None
    app.app.mount.model.azimuthError = value
    app.updateAlignGUI(app.app.mount.model)
    assert '-' == app.ui.azimuthError.text()


def test_updateAlignGui_terms(app):
    value = '50'
    app.app.mount.model.terms = value
    app.updateAlignGUI(app.app.mount.model)
    assert '50' == app.ui.terms.text()
    value = None
    app.app.mount.model.terms = value
    app.updateAlignGUI(app.app.mount.model)
    assert '-' == app.ui.terms.text()


def test_updateAlignGui_orthoError(app):
    value = '50'
    app.app.mount.model.orthoError = value
    app.updateAlignGUI(app.app.mount.model)
    assert '180000' == app.ui.orthoError.text()
    value = None
    app.app.mount.model.orthoError = value
    app.updateAlignGUI(app.app.mount.model)
    assert '-' == app.ui.orthoError.text()


def test_updateAlignGui_positionAngle(app):
    value = '50'
    app.app.mount.model.positionAngle = value
    app.updateAlignGUI(app.app.mount.model)
    assert ' 50.0' == app.ui.positionAngle.text()
    value = None
    app.app.mount.model.positionAngle = value
    app.updateAlignGUI(app.app.mount.model)
    assert '-' == app.ui.positionAngle.text()


def test_updateAlignGui_polarError(app):
    value = '50'
    app.app.mount.model.polarError = value
    app.updateAlignGUI(app.app.mount.model)
    assert '180000' == app.ui.polarError.text()
    value = None
    app.app.mount.model.polarError = value
    app.updateAlignGUI(app.app.mount.model)
    assert '-' == app.ui.polarError.text()


def test_updateTurnKnobsGUI_altitudeTurns_1(app):
    value = 1.5
    app.app.mount.model.altitudeTurns = value
    app.updateTurnKnobsGUI(app.app.mount.model)
    assert '1.50 revs down' == app.ui.altitudeTurns.text()
    value = None
    app.app.mount.model.altitudeTurns = value
    app.updateTurnKnobsGUI(app.app.mount.model)
    assert '-' == app.ui.altitudeTurns.text()


def test_updateTurnKnobsGUI_altitudeTurns_2(app):
    value = -1.5
    app.app.mount.model.altitudeTurns = value
    app.updateTurnKnobsGUI(app.app.mount.model)
    assert '1.50 revs up' == app.ui.altitudeTurns.text()
    value = None
    app.app.mount.model.altitudeTurns = value
    app.updateTurnKnobsGUI(app.app.mount.model)
    assert '-' == app.ui.altitudeTurns.text()


def test_updateTurnKnobsGUI_azimuthTurns_1(app):
    value = 1.5
    app.app.mount.model.azimuthTurns = value
    app.updateTurnKnobsGUI(app.app.mount.model)
    assert '1.50 revs left' == app.ui.azimuthTurns.text()
    value = None
    app.app.mount.model.azimuthTurns = value
    app.updateTurnKnobsGUI(app.app.mount.model)
    assert '-' == app.ui.azimuthTurns.text()


def test_updateTurnKnobsGUI_azimuthTurns_2(app):
    value = -1.5
    app.app.mount.model.azimuthTurns = value
    app.updateTurnKnobsGUI(app.app.mount.model)
    assert '1.50 revs right' == app.ui.azimuthTurns.text()
    value = None
    app.app.mount.model.azimuthTurns = value
    app.updateTurnKnobsGUI(app.app.mount.model)
    assert '-' == app.ui.azimuthTurns.text()
