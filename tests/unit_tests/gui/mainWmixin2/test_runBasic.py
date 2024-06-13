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
import os
import shutil
import glob

# external packages
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWmixin.runBasic import BasicRun
import gui.mainWmixin.tabModel
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    class Mixin(MWidget, BasicRun):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = {}
            self.scaleHint = None
            self.fovHint = None
            self.playSound = None
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            BasicRun.__init__(self)

    window = Mixin()
    yield window

    files = glob.glob('tests/workDir/model/m-*.model')
    for f in files:
        os.remove(f)
    for path in glob.glob('tests/workDir/image/m-*'):
        shutil.rmtree(path)


def test_runSolveDone_0(function, qtbot):
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'pointNumber': 1}
    function.slewQueue.put(mPoint)
    result = {'raJ2000S': 0,
              'decJ2000S': 0,
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 1,
              'flippedS': False,
              'success': False,
              'message': 'test',
              }

    with mock.patch.object(function,
                           'cancelRun'):
        suc = function.runSolveDone(result)
        assert not suc


def test_runSolveDone_1(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'pointNumber': 1}

    function.resultQueue.put(mPoint)
    suc = function.runSolveDone({})
    assert not suc


def test_runSolveDone_2(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'pointNumber': 1}
    function.resultQueue.put(mPoint)
    result = {'raJ2000S': Angle(hours=0),
              'decJ2000S': Angle(degrees=0),
              'success': False,
              }

    def test(number=0, count=0):
        return

    function.runProgressCB = test
    with mock.patch.object(function,
                           'cycleThroughPointsFinished'):
        suc = function.runSolveDone(result)
        assert suc


def test_runSolveDone_3(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 2,
              'imagePath': '',
              'pointNumber': 1}
    function.resultQueue.put(mPoint)
    function.app.data.buildP = [(0, 0, True), (1, 1, True), (2, 2, True)]

    class Julian:
        ut1 = 2458635.168

    result = {'raJ2000S': Angle(hours=0),
              'decJ2000S': Angle(degrees=0),
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 1,
              'flippedS': False,
              'success': True,
              'message': 'test',
              'raJNowM': Angle(hours=0),
              'decJNowM': Angle(degrees=0),
              'raJNowS': Angle(hours=0),
              'decJNowS': Angle(degrees=0),
              'siderealTime': 0,
              'julianDate': Julian(),
              'pierside': 'E',
              'errorRA': 1,
              'errorDEC': 2,
              'errorRMS': 3,
              }

    def test(number=0, count=0):
        return

    function.runProgressCB = test
    function.resultQueue.put(mPoint)
    with mock.patch.object(function,
                           'cycleThroughPointsFinished'):
        suc = function.runSolveDone(result)
        assert suc


def test_runSolveDone_4(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 2,
              'imagePath': '',
              'pointNumber': 1}

    result = {'raJ2000S': Angle(hours=0),
              'decJ2000S': Angle(degrees=0),
              'angleS': 0,
              'scaleS': 1,
              'errorRMS_S': 999999999,
              'flippedS': False,
              'success': True,
              'message': 'test',
              'julianDate': function.app.mount.obsSite.timeJD,
              }

    def test(number=0, count=0):
        return

    function.timeStartModeling = 0
    function.resultQueue.put(mPoint)
    function.runProgressCB = test
    with mock.patch.object(function,
                           'cycleThroughPointsFinished'):
        suc = function.runSolveDone(result)
        assert suc


def test_runSolve_1(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 2,
              'pointNumber': 1}
    function.slewQueue.put(mPoint)
    with mock.patch.object(function,
                           'cancelRun'):
        suc = function.runSolve()
        assert not suc


def test_runSolve_2(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'searchRadius': 1,
              'solveTimeout': 10,
              'raJNowM': 10,
              'decJNowM': 10,
              }
    function.solveQueue.put(mPoint)
    with mock.patch.object(function.app.plateSolve,
                           'solveThreading', return_value=False):
        suc = function.runSolve()
        assert not suc


def test_runSolve_3(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'searchRadius': 1,
              'solveTimeout': 10,
              'raJNowM': 10,
              'decJNowM': 10,
              }
    function.solveQueue.put(mPoint)
    with mock.patch.object(function.app.plateSolve,
                           'solveThreading', return_value=True):
        suc = function.runSolve()
        assert suc


def test_runImage_1(function):
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'searchRadius': 1,
              'solveTimeout': 10,
              }
    function.slewQueue.put(mPoint)
    function.imageQueue.queue.clear()
    with mock.patch.object(function,
                           'cancelRun'):
        suc = function.runImage()
        assert not suc


def test_runImage_2(function):
    def qWaitBreak(a):
        function.ui.pauseModel.setProperty('pause', False)

    gui.mainWmixin.runBasic.sleepAndEvents = qWaitBreak
    function.ui.pauseModel.setProperty('pause', True)
    function
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              'focalLength': 1,
              }

    function.imageQueue.put(mPoint)

    with mock.patch.object(function.app.camera,
                           'expose', return_value=False):
        suc = function.runImage()
        assert not suc


def test_runImage_3(function):
    def qWaitBreak(a):
        function.ui.pauseModel.setProperty('pause', False)

    gui.mainWmixin.runBasic.sleepAndEvents = qWaitBreak
    function.ui.pauseModel.setProperty('pause', True)
    function
    mPoint = {'lenSequence': 3,
              'countSequence': 3,
              'imagePath': '',
              'exposureTime': 1,
              'binning': 1,
              'subFrame': 100,
              'fastReadout': False,
              'focalLength': 1,
              }

    function.imageQueue.put(mPoint)

    with mock.patch.object(function.app.camera,
                           'expose', return_value=True):
        suc = function.runImage()
        assert suc


def test_runSlew_1(function):
    function.slewQueue.queue.clear()
    suc = function.runSlew()
    assert not suc


def test_runSlew_2(function):
    function.deviceStat['dome'] = False
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

    function.slewQueue.put(mPoint)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=False):
        suc = function.runSlew()
        assert not suc


def test_runSlew_3(function):
    function.deviceStat['dome'] = True
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
    function.slewQueue.put(mPoint)
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetAltAz',
                           return_value=True):
        with mock.patch.object(function.app.dome,
                               'slewDome',
                               return_value=0):
            suc = function.runSlew()
            assert suc


def test_runSlew_4(function):
    function.deviceStat['dome'] = True
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
    function.slewQueue.put(mPoint)
    function.ui.useDomeGeometry.setChecked(True)
    with mock.patch.object(function.app.dome,
                           'slewDome',
                           return_value=0):
        with mock.patch.object(function.app.mount.obsSite,
                               'setTargetAltAz',
                               return_value=True):
            suc = function.runSlew()
            assert suc


@mock.patch('gui.mainWmixin.runBasic.isSimulationMount', True)
def test_runSlew_5(function):
    function.deviceStat['dome'] = True
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
    function.slewQueue.put(mPoint)
    function.ui.useDomeGeometry.setChecked(True)
    with mock.patch.object(function.app.dome,
                           'slewDome',
                           return_value=0):
        with mock.patch.object(function.app.mount.obsSite,
                               'setTargetAltAz',
                               return_value=True):
            suc = function.runSlew()
            assert suc


def test_clearQueues(function):
    suc = function.clearQueues()
    assert suc


def test_setupSignalsForRun_1(function):
    suc = function.setupSignalsForRun()
    assert suc


def test_setupSignalsForRun_2(function):
    function.deviceStat['dome'] = True
    function.app.dome.data = {'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION': 1}

    suc = function.setupSignalsForRun()
    assert suc


def test_setupSignalsForRun_3(function):
    function.deviceStat['dome'] = True
    function.app.dome.data = {}
    function.ui.progressiveTiming.setChecked(True)
    suc = function.setupSignalsForRun()
    assert suc


def test_setupSignalsForRun_4(function):
    function.deviceStat['dome'] = True
    function.ui.normalTiming.setChecked(True)
    suc = function.setupSignalsForRun()
    assert suc


def test_setupSignalsForRun_5(function):
    function.deviceStat['dome'] = True
    function.ui.conservativeTiming.setChecked(True)
    suc = function.setupSignalsForRun()
    assert suc


def test_restoreModelDefaultContextAndGuiStatus(function):
    with mock.patch.object(function,
                           'cancelRun'):
        suc = function.restoreModelDefaultContextAndGuiStatus()
        assert suc


def test_cancelRun(function):
    with mock.patch.object(function,
                           'restoreModelDefaultContextAndGuiStatus'):
        with mock.patch.object(function,
                               'clearQueues'):
            with mock.patch.object(function,
                                   'restoreSignalsRunDefault'):
                with mock.patch.object(function.app.camera,
                                       'abort'):
                    with mock.patch.object(function.app.plateSolve,
                                           'abort'):
                        suc = function.cancelRun()
                        assert suc


def test_generateSaveData_1(function):
    mPoint = {'raJNowM': Angle(hours=0),
              'decJNowM': Angle(degrees=0),
              'raJNowS': Angle(hours=0),
              'decJNowS': Angle(degrees=0),
              'angularPosRA': Angle(degrees=0),
              'angularPosDEC': Angle(degrees=0),
              'raJ2000S': Angle(hours=0),
              'decJ2000S': Angle(degrees=0),
              'raJ2000M': Angle(hours=0),
              'decJ2000M': Angle(degrees=0),
              'siderealTime': Angle(hours=0),
              'julianDate': function.app.mount.obsSite.timeJD,
              }
    function.model = list()
    function.model.append(mPoint)
    function.model.append(mPoint)
    function.model.append(mPoint)

    val = function.generateSaveData()
    assert len(val) == 3
    assert 'profile' in val[0]
    assert 'firmware' in val[0]
    assert 'latitude' in val[0]
    assert 'version' in val[0]


def test_restoreSignalsModelDefault(function):
    function.performanceTimingSignal = function.app.camera.signals.exposed
    function.app.camera.signals.saved.connect(function.runSolve)
    function.performanceTimingSignal.connect(function.runSlew)
    function.app.plateSolve.signals.done.connect(function.runSolveDone)
    function.collector.ready.connect(function.runImage)

    suc = function.restoreSignalsRunDefault()
    assert suc


def test_collectingModelRunOutput_1(function):
    suc = function.collectingRunOutput()
    assert not suc


def test_collectingModelRunOutput_2(function):
    class Julian:
        ut1 = 2458635.168

    inputData = {
        'raJ2000S': Angle(hours=0),
        'decJ2000S': Angle(degrees=0),
        'angleS': 0,
        'scaleS': 1,
        'errorRMS_S': 1,
        'flippedS': False,
        'success': True,
        'message': 'test',
        'raJNowM': Angle(hours=0),
        'decJNowM': Angle(degrees=0),
        'raJNowS': Angle(hours=0),
        'decJNowS': Angle(degrees=0),
        'siderealTime': Angle(hours=0),
        'julianDate': Julian(),
        'pierside': 'E',
        'errorRA': 1,
        'errorDEC': 2,
        'errorRMS': 3,
    }

    function.modelQueue.put(inputData)
    function.modelQueue.put(inputData)
    function.modelQueue.put(inputData)

    suc = function.collectingRunOutput()
    assert suc


def test_processData_1(function):
    def test(a):
        return

    function.processDataCB = test
    function.ui.parkMountAfterModel.setChecked(True)
    function.ui.keepModelImages.setChecked(False)
    with mock.patch.object(function,
                           'collectingRunOutput',
                           return_value=[]):
        with mock.patch.object(function,
                               'restoreSignalsRunDefault'):
            with mock.patch.object(function,
                                   'clearQueues'):
                with mock.patch.object(function.app.mount.obsSite,
                                       'park',
                                       return_value=False):
                    suc = function.processDataAndFinishRun()
                    assert suc


def test_processData_2(function):
    def test(a):
        return

    function.processDataCB = test
    function.ui.parkMountAfterModel.setChecked(True)
    function.ui.keepModelImages.setChecked(False)
    with mock.patch.object(function,
                           'collectingRunOutput',
                           return_value=[]):
        with mock.patch.object(function,
                               'restoreSignalsRunDefault'):
            with mock.patch.object(function,
                                   'clearQueues'):
                with mock.patch.object(function.app.mount.obsSite,
                                       'park',
                                       return_value=True):
                    suc = function.processDataAndFinishRun()
                    assert suc


def test_cycleThroughPointsFinished_1(function):
    inputData = {
         'lenSequence': 0,
         'countSequence': 1,
         }

    function.modelQueue.put(inputData)

    with mock.patch.object(function,
                           'processDataAndFinishRun'):
        suc = function.cycleThroughPointsFinished()
        assert suc


def test_cycleThroughPointsFinished_2(function):
    inputData = {
        'lenSequence': 0,
        'countSequence': 1,
    }

    function.retryQueue.put(inputData)

    with mock.patch.object(function,
                           'processDataAndFinishRun'):
        with mock.patch.object(function,
                               'runSlew'):
            suc = function.cycleThroughPointsFinished()
            assert suc


def test_cycleThroughPointsFinished_3(function):
    inputData = {
        'lenSequence': 0,
        'countSequence': 1,
    }

    function.retryQueue.put(inputData)
    function.retryCounter = 1

    with mock.patch.object(function,
                           'processDataAndFinishRun'):
        with mock.patch.object(function,
                               'runSlew'):
            suc = function.cycleThroughPointsFinished()
            assert suc


def test_cycleThroughPoints_1(function):
    points = [1, 2]
    with mock.patch.object(function,
                           'setupSignalsForRun'):
        with mock.patch.object(function,
                               'runSlew'):
            suc = function.cycleThroughPoints(points)
            assert suc


def test_setupFilenamesAndDirectories_1(function):
    function.lastGenerator = 'test'
    with mock.patch.object(os.path,
                           'isdir',
                           return_value=False):
        with mock.patch.object(os,
                               'mkdir'):
            n, d = function.setupFilenamesAndDirectories(prefix='a', postfix='b')
            assert n
            assert d


def test_setupRunPoints_1(function):
    class Test:
        timeout = 1
        searchRadius = 1

    function.app.plateSolve.framework = 'astap'
    function.app.plateSolve.run = {'astap': Test()}
    function.app.data.buildP = []
    val = function.setupRunPoints()
    assert val == []


def test_setupRunPoints_2(function):
    class Test:
        timeout = 1
        searchRadius = 1

    function.app.plateSolve.framework = 'astap'
    function.app.plateSolve.run = {'astap': Test()}
    data = [(0, 0, True), (10, 10, True), (20, 20, True)]
    val = function.setupRunPoints(data=data)
    assert len(val) == 3
    assert val[0]['lenSequence'] == 3
    assert val[0]['countSequence'] == 1
    assert val[1]['countSequence'] == 2
    assert val[1]['altitude'] == 10
    assert val[1]['azimuth'] == 10
