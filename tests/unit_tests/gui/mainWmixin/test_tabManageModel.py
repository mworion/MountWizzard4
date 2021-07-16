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
import unittest.mock as mock
import pytest
from pathlib import Path
import json
import shutil

# external packages
import PyQt5
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
from skyfield.api import wgs84, Star, Angle
from mountcontrol.modelStar import ModelStar

# local import
from gui.mainWmixin.tabManageModel import ManageModel
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    shutil.copy('tests/testData/test.model', 'tests/model/test.model')
    shutil.copy('tests/testData/test1.model', 'tests/model/test1.model')
    shutil.copy('tests/testData/test-opt.model', 'tests/model/test-opt.model')
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData='tests/data')
        mount.obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)
        update1s = pyqtSignal()
        showAnalyse = pyqtSignal(object)
        message = pyqtSignal(str, int)
        mwGlob = {'imageDir': 'tests/image',
                  'modelDir': 'tests/model'}

    class Mixin(MWidget, ManageModel):
        def __init__(self):
            super().__init__()
            self.app = Test()
            self.widget1 = QWidget()
            self.widget2 = QWidget()
            self.widget3 = QWidget()
            self.errorAscendingPlot = MWidget().embedMatplot(self.widget1)
            self.modelPositionPlot = MWidget().embedMatplot(self.widget2)
            self.errorDistributionPlot = MWidget().embedMatplot(self.widget3)
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            ManageModel.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    with mock.patch.object(function,
                           'showModelPosition'):
        function.initConfig()
        assert function.ui.targetRMS.value() == 10
        assert not function.ui.showErrorValues.isChecked()


def test_storeConfig_1(function):
    function.ui.targetRMS.setValue(33)
    function.ui.showErrorValues.setChecked(True)
    function.storeConfig()
    conf = function.app.config['mainW']
    assert conf['showErrorValues']
    assert 33 == conf['targetRMS']


def test_setNameList(function):
    value = ['Test1', 'test2', 'test3', 'test4']
    function.app.mount.model.nameList = value
    function.setNameList(function.app.mount.model)
    assert 4 == function.ui.nameList.count()
    value = None
    function.app.mount.model.nameList = value
    function.setNameList(function.app.mount.model)
    assert 0 == function.ui.nameList.count()


def test_findKeysFromSourceInDest_1(function):
    val1, val2 = function.findKeysFromSourceInDest({}, {})
    assert val1 == []
    assert val2 == []


def test_findKeysFromSourceInDest_2(function):
    source = {1: {'ha': 1, 'dec': 2}}
    dest = {1: {'ha': 3, 'dec': 4}}
    val1, val2 = function.findKeysFromSourceInDest(source, dest)
    assert val1 == []
    assert val2 == [1, 2]


def test_findKeysFromSourceInDest_3(function):
    source = {1: {'ha': 1, 'dec': 2}, 2: {'ha': 3, 'dec': 4}}
    dest = {1: {'ha': 2, 'dec': 1}, 2: {'ha': 3, 'dec': 4}}
    val1, val2 = function.findKeysFromSourceInDest(source, dest)
    assert val1 == [1]
    assert val2 == [2]


def test_compareModel_1(function):
    val1, val2 = function.compareModel({}, {})
    assert val1 == []
    assert val2 == []


def test_compareModel_2(function):
    source = [{'errorIndex': 1, 'ha': 10, 'dec': 20}, {'errorIndex': 2, 'ha': 30, 'dec': 40}]
    dest = {'1': {'ha': 30, 'dec': 40}}
    val1, val2 = function.compareModel(source, dest)
    assert val1 == []
    assert val2 == [1, 2]


def test_findFittingModel_1(function):
    name, pointsIn, pointsOut = function.findFittingModel()

    assert name == ''
    assert pointsIn == []
    assert pointsOut == []


def test_findFittingModel_2(function):
    function.app.mwGlob['modelDir'] = 'tests/testData'
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)
    with mock.patch.object(function,
                           'compareModel',
                           return_value=([], [])):
        name, pointsIn, pointsOut = function.findFittingModel()

        assert name == ''
        assert pointsIn == []
        assert pointsOut == []
    function.app.mwGlob['modelDir'] = 'tests/model'


def test_findFittingModel_3(function):
    function.app.mwGlob['modelDir'] = 'tests/testData'
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)
    with mock.patch.object(json,
                           'load',
                           return_value={},
                           side_effect=Exception):
        with mock.patch.object(function,
                               'compareModel',
                               return_value=([], [])):
            name, pointsIn, pointsOut = function.findFittingModel()

            assert name == ''
            assert pointsIn == []
            assert pointsOut == []
    function.app.mwGlob['modelDir'] = 'tests/model'


def test_findFittingModel_4(function):
    function.app.mwGlob['modelDir'] = 'tests/testData'
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)
    with mock.patch.object(json,
                           'load',
                           return_value={}):
        with mock.patch.object(function,
                               'compareModel',
                               return_value=([1], [2])):
            name, pointsIn, pointsOut = function.findFittingModel()

            assert name == 'test'
            assert pointsIn == [1]
            assert pointsOut == [2]
    function.app.mwGlob['modelDir'] = 'tests/model'


def test_showModelPosition_0(function):
    function.app.mount.model = None

    function.ui.showErrorValues.setChecked(True)
    suc = function.showModelPosition()
    assert not suc


def test_showModelPosition_1(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    function.app.mount.model.parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                         '21:06:10.79,+45*20:52.8,  12.1,329',
                                         '23:13:58.02,+38*48:18.8,  31.0,162',
                                         '17:43:41.26,+59*15:30.7,   8.4,005',
                                         ],
                                        4)
    function.ui.showErrorValues.setChecked(True)
    suc = function.showModelPosition()
    assert suc


def test_showModelPosition_2(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    function.app.mount.model._starList = list()
    function.ui.showErrorValues.setChecked(True)
    suc = function.showModelPosition()
    assert not suc


def test_showModelPosition_3(function):
    function.app.mount.obsSite.location = []
    function.app.mount.model._starList = list()
    function.ui.showErrorValues.setChecked(True)
    suc = function.showModelPosition()
    assert not suc


def test_showModelPosition_4(function):
    function.ui.showErrorValues.setChecked(True)
    function.app.mount.model._starList = list()
    suc = function.showModelPosition()
    assert not suc


def test_showModelPosition_5(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    function.app.mount.model.parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                         '21:06:10.79,+45*20:52.8,  12.1,329',
                                         '23:13:58.02,+38*48:18.8,  31.0,162',
                                         '17:43:41.26,+59*15:30.7,   8.4,005',
                                         ],
                                        4)
    function.ui.showNumbers.setChecked(True)
    suc = function.showModelPosition()
    assert suc


def test_showErrorAscending_0(function):
    function.app.mount.model = None
    suc = function.showErrorAscending()
    assert not suc


def test_showErrorAscending_1(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    function.app.mount.model.parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                         '21:06:10.79,+45*20:52.8,  12.1,329',
                                         '23:13:58.02,+38*48:18.8,  31.0,162',
                                         '17:43:41.26,+59*15:30.7,   8.4,005',
                                         ],
                                        4)
    suc = function.showErrorAscending()
    assert suc


def test_showErrorAscending_2(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    function.app.mount.model._starList = list()
    suc = function.showErrorAscending()
    assert not suc


def test_showErrorAscending_3(function):
    function.app.mount.obsSite.location = []
    function.app.mount.model._starList = list()
    suc = function.showErrorAscending()
    assert not suc


def test_showErrorAscending_4(function):
    function.app.mount.model._starList = list()
    suc = function.showErrorAscending()
    assert not suc


def test_showErrorDistribution_0(function):
    function.app.mount.model = None
    suc = function.showErrorDistribution()
    assert not suc


def test_showErrorDistribution_1(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    function.app.mount.model.parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                         '21:06:10.79,+45*20:52.8,  12.1,329',
                                         '23:13:58.02,+38*48:18.8,  31.0,162',
                                         '17:43:41.26,+59*15:30.7,   8.4,005',
                                         ],
                                        4)
    suc = function.showErrorDistribution()
    assert suc


def test_showErrorDistribution_2(function):
    function.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    function.app.mount.model._starList = list()
    suc = function.showErrorDistribution()
    assert not suc


def test_showErrorDistribution_3(function):
    function.app.mount.obsSite.location = []
    function.app.mount.model._starList = list()
    suc = function.showErrorDistribution()
    assert not suc


def test_showErrorDistribution_4(function):
    function.app.mount.model._starList = list()
    suc = function.showErrorDistribution()
    assert not suc


def test_clearRefreshName(function):
    function.app.mount.signals.namesDone.connect(function.clearRefreshName)
    suc = function.clearRefreshName()
    assert suc


def test_refreshName_1(function):
    with mock.patch.object(function.app.mount,
                           'getNames',
                           return_value=True):
        suc = function.refreshName()
        assert suc
        suc = function.clearRefreshName()
        assert suc


def test_refreshName_2(function, qtbot):
    suc = function.refreshName()
    assert suc
    with qtbot.waitSignal(function.app.message) as blocker:
        suc = function.refreshName()
        assert suc
        assert ['Model names refreshed', 0] == blocker.args


def test_loadName_1(function, qtbot):
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=None):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.loadName()
            assert not suc
            assert ['No model name selected', 2] == blocker.args


def test_loadName_2(function, qtbot):
    class Test:
        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(function.app.mount.model,
                               'loadName',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.loadName()
                assert suc
                assert ['Model [test] loaded', 0] == blocker.args


def test_loadName_3(function, qtbot):
    class Test:
        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(function.app.mount.model,
                               'loadName',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.loadName()
                assert not suc
                assert ['Model [test] cannot be loaded', 2] == blocker.args


def test_saveName_1(function, qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('', True)):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.saveName()
            assert not suc
            assert ['No model name given', 2] == blocker.args


def test_saveName_2(function, qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(None, True)):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.saveName()
            assert not suc
            assert ['No model name given', 2] == blocker.args


def test_saveName_3(function, qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', False)):
        with qtbot.assertNotEmitted(function.app.message):
            suc = function.saveName()
            assert not suc


def test_saveName_4(function, qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', True)):
        with mock.patch.object(function.app.mount.model,
                               'storeName',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveName()
                assert not suc
                assert ['Model [test] cannot be saved', 2] == blocker.args


def test_saveName_5(function, qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', True)):
        with mock.patch.object(function.app.mount.model,
                               'storeName',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.saveName()
                assert suc
                assert ['Model [test] saved', 0] == blocker.args


def test_deleteName_1(function, qtbot):
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=None):
        with qtbot.waitSignal(function.app.message) as blocker:
            suc = function.deleteName()
            assert not suc
            assert ['No model name selected', 2] == blocker.args


def test_deleteName_2(function, qtbot):
    class Test:
        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'question',
                               return_value=PyQt5.QtWidgets.QMessageBox.No):
            with qtbot.assertNotEmitted(function.app.message):
                suc = function.deleteName()
                assert not suc


def test_deleteName_3(function, qtbot):
    class Test:
        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'question',
                               return_value=PyQt5.QtWidgets.QMessageBox.Yes):
            with mock.patch.object(function.app.mount.model,
                                   'deleteName',
                                   return_value=True):
                with qtbot.waitSignal(function.app.message) as blocker:
                    suc = function.deleteName()
                    assert suc
                    assert ['Model [test] deleted', 0] == blocker.args


def test_deleteName_4(function, qtbot):
    class Test:
        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'question',
                               return_value=PyQt5.QtWidgets.QMessageBox.Yes):
            with mock.patch.object(function.app.mount.model,
                                   'deleteName',
                                   return_value=False):
                with qtbot.waitSignal(function.app.message) as blocker:
                    suc = function.deleteName()
                    assert not suc
                    assert ['Model [test] cannot be deleted', 2] == blocker.args


def test_writeBuildModelOptimized_1(function):
    with mock.patch.object(function,
                           'writeRetrofitData',
                           return_value={}):
        with mock.patch.object(json,
                               'load',
                               return_value=[{'errorIndex': 1}, {'errorIndex': 3}]):
            suc = function.writeBuildModelOptimized('test', [2], [1])
            assert suc


def test_clearRefreshModel_1(function):
    function.app.mount.signals.alignDone.connect(function.clearRefreshModel)
    suc = function.clearRefreshModel()
    assert suc


def test_clearRefreshModel_2(function):
    function.app.mount.signals.alignDone.connect(function.clearRefreshModel)
    function.ui.autoUpdateActualAnalyse.setChecked(True)
    with mock.patch.object(function,
                           'findFittingModel',
                           return_value=('test', [], [])):
        with mock.patch.object(function,
                               'writeBuildModelOptimized'):
            with mock.patch.object(function,
                                   'showActualModelAnalyse'):
                suc = function.clearRefreshModel()
                assert suc


def test_refreshModel(function):
    function.app.mount.signals.alignDone.connect(function.clearRefreshModel)
    with mock.patch.object(function.app.mount,
                           'getAlign'):
        suc = function.clearRefreshModel()
        assert suc


def test_clearModel_1(function, qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = function.clearModel()
        assert not suc


def test_clearModel_2(function, qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(function.app.mount.model,
                               'clearAlign',
                               return_value=False):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.clearModel()
                assert not suc
                assert ['Actual model cannot be cleared', 2] == blocker.args


def test_clearModel_3(function, qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(function.app.mount.model,
                               'clearAlign',
                               return_value=True):
            with qtbot.waitSignal(function.app.message) as blocker:
                suc = function.clearModel()
                assert suc
                assert ['Actual model cleared', 0] == blocker.args


def test_deleteWorstPoint_1(function):
    function.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    function.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    suc = function.deleteWorstPoint()
    assert not suc


def test_deleteWorstPoint_2(function):
    function.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    function.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    function.app.mount.model.numberStars = 2
    with mock.patch.object(function.app.mount.model,
                           'deletePoint',
                           return_value=True):
        with mock.patch.object(function,
                               'refreshModel'):
            suc = function.deleteWorstPoint()
            assert suc


def test_deleteWorstPoint_3(function):
    function.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    function.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    function.app.mount.model.numberStars = 2
    with mock.patch.object(function.app.mount.model,
                           'deletePoint',
                           return_value=False):
        with mock.patch.object(function,
                               'refreshModel'):
            suc = function.deleteWorstPoint()
            assert not suc


def test_runTargetRMS_1(function):
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    function.app.mount.signals.alignDone.connect(function.runTargetRMS)
    function.app.mount.model.errorRMS = 0.1
    suc = function.runTargetRMS()
    assert suc


def test_runTargetRMS_2(function):
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    function.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    function.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 2
    function.runningTargetRMS = True
    function.app.mount.signals.alignDone.connect(function.runTargetRMS)
    with mock.patch.object(function.app.mount.model,
                           'deletePoint',
                           return_value=False):
        with mock.patch.object(function.app.mount,
                               'getAlign'):
            suc = function.runTargetRMS()
            assert suc


def test_runTargetRMS_3(function):
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    function.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    function.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 2
    function.runningTargetRMS = True
    function.app.mount.signals.alignDone.connect(function.runTargetRMS)
    with mock.patch.object(function.app.mount.model,
                           'deletePoint',
                           return_value=True):
        with mock.patch.object(function.app.mount,
                               'getAlign'):
            suc = function.runTargetRMS()
            assert suc


def test_runTargetRMS_4(function):
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    function.app.mount.model.errorRMS = 100
    function.runningTargetRMS = False
    function.app.mount.signals.alignDone.connect(function.runTargetRMS)
    suc = function.runTargetRMS()
    assert suc


def test_runSingleRMS_1(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    function.app.mount.signals.alignDone.connect(function.runSingleRMS)
    function.app.mount.model.errorRMS = 0.1
    suc = function.runSingleRMS()
    assert suc


def test_runSingleRMS_2(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    function.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    function.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 2
    function.runningTargetRMS = True
    function.app.mount.signals.alignDone.connect(function.runSingleRMS)
    with mock.patch.object(function.app.mount.model,
                           'deletePoint',
                           return_value=False):
        with mock.patch.object(function.app.mount,
                               'getAlign'):
            suc = function.runSingleRMS()
            assert suc


def test_runSingleRMS_3(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    function.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    function.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 2
    function.runningTargetRMS = True
    function.app.mount.signals.alignDone.connect(function.runSingleRMS)
    with mock.patch.object(function.app.mount.model,
                           'deletePoint',
                           return_value=True):
        with mock.patch.object(function.app.mount,
                               'getAlign'):
            suc = function.runSingleRMS()
            assert suc


def test_runSingleRMS_4(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    function.app.mount.model.errorRMS = 100
    function.runningTargetRMS = False
    function.app.mount.signals.alignDone.connect(function.runSingleRMS)
    suc = function.runSingleRMS()
    assert suc


def test_runOptimize_1(function):
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    with mock.patch.object(function,
                           'runTargetRMS'):
        suc = function.runOptimize()
        assert suc


def test_runOptimize_2(function):
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    with mock.patch.object(function,
                           'runSingleRMS'):
        suc = function.runOptimize()
        assert suc


def test_finishOptimize_1(function):
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    function.app.mount.signals.alignDone.connect(function.runSingleRMS)
    suc = function.finishOptimize()
    assert suc


def test_finishOptimize_2(function):
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    function.app.mount.signals.alignDone.connect(function.runTargetRMS)
    suc = function.finishOptimize()
    assert suc


def test_cancelOptimize_1(function):
    suc = function.cancelOptimize()
    assert suc
    assert not function.runningOptimize


def test_showOriginalModelAnalyse_1(function):
    function.fittedModelPath = ''
    suc = function.showOriginalModelAnalyse()
    assert not suc


def test_showOriginalModelAnalyse_2(function):
    function.fittedModelPath = 'test'
    suc = function.showOriginalModelAnalyse()
    assert not suc


def test_showOriginalModelAnalyse_3(function):
    function.fittedModelPath = 'tests/testData/test.model'
    suc = function.showOriginalModelAnalyse()
    assert suc


def test_showActualModelAnalyse_1(function):
    function.fittedModelPath = ''
    suc = function.showActualModelAnalyse()
    assert not suc


def test_showActualModelAnalyse_2(function):
    function.fittedModelPath = 'test'
    suc = function.showActualModelAnalyse()
    assert not suc


def test_showActualModelAnalyse_3(function):
    function.fittedModelPath = 'tests/testData/test.model'
    suc = function.showActualModelAnalyse()
    assert suc


def test_deleteDialog_1(function):
    with mock.patch.object(QMessageBox,
                           'question',
                           return_value=QMessageBox.No):
        suc = function.deleteDialog('test')
        assert not suc


def test_deleteDialog_2(function):
    with mock.patch.object(QMessageBox,
                           'question',
                           return_value=QMessageBox.Yes):
        suc = function.deleteDialog('test')
        assert suc


def test_onMouseEdit_1(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = False
        dblclick = True
        button = 1

    suc = function.onMouseEdit(Event())
    assert not suc


def test_onMouseEdit_2(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    suc = function.onMouseEdit(Event())
    assert not suc


def test_onMouseEdit_3(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.plane = [(0, 0), (0, 360)]

    suc = function.onMouseEdit(Event())
    assert not suc


def test_onMouseEdit_4(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = False
        button = 1

    function.plane = [(0, 0), (0, 360)]

    suc = function.onMouseEdit(Event())
    assert not suc


def test_onMouseEdit_5(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    function.plane = [(0, 0), (0, 360)]
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)

    with mock.patch.object(function,
                           'deleteDialog',
                           return_value=False):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            suc = function.onMouseEdit(Event())
            assert not suc


def test_onMouseEdit_5b(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    function.plane = [(0, 0), (0, 360)]
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)

    with mock.patch.object(function,
                           'deleteDialog',
                           return_value=False):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=None):
            suc = function.onMouseEdit(Event())
            assert not suc


def test_onMouseEdit_6(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    function.plane = [(0, 0), (0, 360)]
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)

    with mock.patch.object(function,
                           'deleteDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            with mock.patch.object(function.app.mount.model,
                                   'deletePoint',
                                   return_value=False):
                suc = function.onMouseEdit(Event())
                assert not suc


def test_onMouseEdit_7(function):
    class Event:
        xdata = 10
        ydata = 10
        inaxes = True
        dblclick = True
        button = 1

    function.plane = [(0, 0), (0, 360)]
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)

    with mock.patch.object(function,
                           'deleteDialog',
                           return_value=True):
        with mock.patch.object(function,
                               'getIndexPoint',
                               return_value=0):
            with mock.patch.object(function.app.mount.model,
                                   'deletePoint',
                                   return_value=True):
                with mock.patch.object(function,
                                       'refreshModel'):
                    suc = function.onMouseEdit(Event())
                    assert suc
