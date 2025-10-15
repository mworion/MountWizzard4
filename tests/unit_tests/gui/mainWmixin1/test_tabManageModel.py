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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import glob
import json
import shutil
import os

# external packages
import PyQt5
from PyQt5.QtWidgets import QWidget
from skyfield.api import Star, Angle
from mw4.mountcontrol.modelStar import ModelStar

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.mainWmixin.tabManageModel import ManageModel
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    files = glob.glob('tests/workDir/model/*.model')
    for f in files:
        os.remove(f)
    shutil.copy('tests/testData/test.model', 'tests/workDir/model/test.model')
    shutil.copy('tests/testData/test1.model', 'tests/workDir/model/test1.model')
    shutil.copy('tests/testData/test-opt.model', 'tests/workDir/model/test-opt.model')
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    class Mixin(MWidget, ManageModel):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.widget1 = QWidget()
            self.widget2 = QWidget()
            self.widget3 = QWidget()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            ManageModel.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    with mock.patch.object(function,
                           'showModelPosition'):
        with mock.patch.object(function,
                               'showErrorAscending'):
            with mock.patch.object(function,
                                   'showErrorDistribution'):
                function.initConfig()
                assert function.ui.targetRMS.value() == 10


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_colorChangeManageModel(function):
    with mock.patch.object(function,
                           'showModelPosition'):
        with mock.patch.object(function,
                               'showErrorAscending'):
            with mock.patch.object(function,
                                   'showErrorDistribution'):
                suc = function.colorChangeManageModel()
                assert suc


def test_setNameList(function):
    value = ['Test1', 'test2', 'test3', 'test4']
    function.app.mount.model.nameList = value
    function.setNameList(function.app.mount.model)
    assert 4 == function.ui.nameList.count()
    function.app.mount.model.nameList = []


def test_findKeysFromSourceInDest_1(function):
    val1, val2 = function.findKeysFromSourceInDest({}, {})
    assert val1 == []
    assert val2 == []


def test_findKeysFromSourceInDest_2(function):
    source = {1: {'ha': 1, 'dec': 2}, 2: {'ha': 4, 'dec': 3}}
    dest = {1: {'ha': 2, 'dec': 1}, 2: {'ha': 3, 'dec': 4}}
    val1, val2 = function.findKeysFromSourceInDest(source, dest)
    assert val1 == []
    assert 1 in val2
    assert 2 in val2


def test_findKeysFromSourceInDest_3(function):
    source = {1: {'ha': 1, 'dec': 2}, 2: {'ha': 3, 'dec': 4}}
    dest = {1: {'ha': 2, 'dec': 1}, 2: {'ha': 3, 'dec': 4}}
    val1, val2 = function.findKeysFromSourceInDest(source, dest)
    assert 2 in val1
    assert 1 in val2


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
    function.app.mount.model.starList = list()
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
    function.app.mwGlob['modelDir'] = 'tests/workDir/model'


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
    function.app.mwGlob['modelDir'] = 'tests/workDir/model'


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
                               return_value=([1, 2, 3], [4])):
            name, pointsIn, pointsOut = function.findFittingModel()

            assert pointsIn == [1, 2, 3]
            assert pointsOut == [4]
    function.app.mwGlob['modelDir'] = 'tests/workDir/model'


def test_showModelPosition_1(function):
    function.app.mount.model.starList = list()
    suc = function.showModelPosition()
    assert not suc


def test_showModelPosition_2(function):
    star = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=0, errorAngle=0,
                     number=1, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star, star, star]
    suc = function.showModelPosition()
    assert suc


def test_showErrorAscending_1(function):
    star = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=0, errorAngle=0,
                     number=1, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star, star, star]
    suc = function.showErrorAscending()
    assert suc


def test_showErrorAscending_2(function):
    function.app.mount.model.starList = list()
    suc = function.showErrorAscending()
    assert not suc


def test_showErrorAscending_3(function):
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    function.app.mount.model.starList = list()
    suc = function.showErrorAscending()
    assert not suc
    function.app.mount.obsSite.location = temp


def test_showErrorAscending_4(function):
    function.app.mount.model.starList = list()
    suc = function.showErrorAscending()
    assert not suc


def test_showErrorDistribution_1(function):
    star = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=0, errorAngle=0,
                     number=1, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star, star, star]
    suc = function.showErrorDistribution()
    assert suc


def test_showErrorDistribution_2(function):
    function.app.mount.model.starList = list()
    suc = function.showErrorDistribution()
    assert not suc


def test_showErrorDistribution_3(function):
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    function.app.mount.model.starList = list()
    suc = function.showErrorDistribution()
    assert not suc
    function.app.mount.obsSite.location = temp


def test_showErrorDistribution_4(function):
    function.app.mount.model.starList = list()
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


def test_refreshName_2(function):
    suc = function.refreshName()
    assert suc
    suc = function.refreshName()
    assert suc


def test_loadName_1(function):
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=None):
        suc = function.loadName()
        assert not suc


def test_loadName_2(function):
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
            suc = function.loadName()
            assert suc


def test_loadName_3(function):
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
            suc = function.loadName()
            assert not suc


def test_saveName_1(function):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('', True)):
        suc = function.saveName()
        assert not suc


def test_saveName_2(function):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(None, True)):
        suc = function.saveName()
        assert not suc


def test_saveName_3(function):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', False)):
        suc = function.saveName()
        assert not suc


def test_saveName_4(function):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', True)):
        with mock.patch.object(function.app.mount.model,
                               'storeName',
                               return_value=False):
            suc = function.saveName()
            assert not suc


def test_saveName_5(function):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', True)):
        with mock.patch.object(function.app.mount.model,
                               'storeName',
                               return_value=True):
            suc = function.saveName()
            assert suc


def test_deleteName_1(function):
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=None):
        suc = function.deleteName()
        assert not suc


def test_deleteName_2(function):
    class Test:
        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=False):
            suc = function.deleteName()
            assert not suc


def test_deleteName_3(function):
    class Test:
        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=True):
            with mock.patch.object(function.app.mount.model,
                                   'deleteName',
                                   return_value=True):
                suc = function.deleteName()
                assert suc


def test_deleteName_4(function):
    class Test:
        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(function.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=True):
            with mock.patch.object(function.app.mount.model,
                                   'deleteName',
                                   return_value=False):
                suc = function.deleteName()
                assert not suc


def writeRFD(a, b):
    return {}


@mock.patch('mw4.gui.mainWmixin.tabManageModel.writeRetrofitData', writeRFD)
def test_writeBuildModelOptimized_1(function):
    with mock.patch.object(json,
                           'load',
                           return_value=[{'errorIndex': 1}, {'errorIndex': 3}]):
        with mock.patch.object(json,
                               'dump'):
            suc = function.writeBuildModelOptimized('test', [1])
            assert suc


@mock.patch('mw4.gui.mainWmixin.tabManageModel.writeRetrofitData', writeRFD)
def test_writeBuildModelOptimized_2(function):
    with mock.patch.object(json,
                           'load',
                           return_value=[{'errorIndex': 1}, {'errorIndex': 3}],
                           side_effect=Exception):
        suc = function.writeBuildModelOptimized('test', [1])
        assert not suc


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


def test_clearModel_1(function):
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.clearModel()
        assert not suc


def test_clearModel_2(function):
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.app.mount.model,
                               'clearAlign',
                               return_value=False):
            suc = function.clearModel()
            assert not suc


def test_clearModel_3(function):
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.app.mount.model,
                               'clearAlign',
                               return_value=True):
            suc = function.clearModel()
            assert suc


def test_deleteWorstPoint_1(function):
    star = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=0, errorAngle=0,
                     number=1, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star, star, star]
    function.app.mount.model.numberStars = 0
    suc = function.deleteWorstPoint()
    assert not suc


def test_deleteWorstPoint_2(function):
    star = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=0, errorAngle=0,
                     number=1, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star, star, star]
    function.app.mount.model.numberStars = 3
    with mock.patch.object(function.app.mount.model,
                           'deletePoint',
                           return_value=True):
        with mock.patch.object(function,
                               'refreshModel'):
            suc = function.deleteWorstPoint()
            assert suc


def test_deleteWorstPoint_3(function):
    star = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=0, errorAngle=0,
                     number=1, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star, star, star]
    function.app.mount.model.numberStars = 3
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
    star1 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=5, errorAngle=90,
                      number=1, obsSite=function.app.mount.obsSite)
    star2 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=4, errorAngle=90,
                      number=2, obsSite=function.app.mount.obsSite)
    star3 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=3, errorAngle=90,
                      number=3, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star1, star2, star3]

    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 3
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
    star1 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=5, errorAngle=90,
                      number=1, obsSite=function.app.mount.obsSite)
    star2 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=4, errorAngle=90,
                      number=2, obsSite=function.app.mount.obsSite)
    star3 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=3, errorAngle=90,
                      number=3, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star1, star2, star3]

    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 3
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
    function.app.mount.model.numberStars = None
    function.runningTargetRMS = False
    function.app.mount.signals.alignDone.connect(function.runTargetRMS)
    suc = function.runTargetRMS()
    assert suc


def test_runSingleRMS_1(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    star1 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=0.1, errorAngle=90,
                      number=1, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star1]
    function.app.mount.signals.alignDone.connect(function.runSingleRMS)
    function.app.mount.model.errorRMS = 0.1
    suc = function.runSingleRMS()
    assert suc


def test_runSingleRMS_2(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    star1 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=5, errorAngle=90,
                      number=1, obsSite=function.app.mount.obsSite)
    star2 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=4, errorAngle=90,
                      number=2, obsSite=function.app.mount.obsSite)
    star3 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=3, errorAngle=90,
                      number=3, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star1, star2, star3]
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 3
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
    star1 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=5, errorAngle=90,
                      number=1, obsSite=function.app.mount.obsSite)
    star2 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=4, errorAngle=90,
                      number=2, obsSite=function.app.mount.obsSite)
    star3 = ModelStar(Star(ra_hours=0, dec_degrees=0), errorRMS=3, errorAngle=90,
                      number=3, obsSite=function.app.mount.obsSite)
    function.app.mount.model.starList = [star1, star2, star3]
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 3
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
    function.app.mount.model.numberStars = None
    function.runningTargetRMS = False
    function.app.mount.signals.alignDone.connect(function.runSingleRMS)
    with mock.patch.object(function,
                           'finishOptimize'):
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


def test_pointClicked_1(function):
    class Event:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def double():
            return True

    suc = function.pointClicked(None, None, Event())
    assert not suc


def test_pointClicked_2(function):
    class Event:
        @staticmethod
        def button():
            return 2

        @staticmethod
        def double():
            return False

    suc = function.pointClicked(None, None, Event())
    assert not suc


def test_pointClicked_3(function):
    class Event:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def double():
            return False

    class Points:
        @staticmethod
        def data():
            return []

    points = [Points()]
    suc = function.pointClicked(None, points, Event())
    assert not suc


def test_pointClicked_4(function):
    class Event:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def double():
            return False

    class Points:
        @staticmethod
        def data():
            return [1, 1]

    points = [Points()]

    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)
    function.app.mount.model.starList.append(a)

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.pointClicked(None, points, Event())
        assert not suc


def test_pointClicked_5(function):
    class Event:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def double():
            return False

    class Points:
        @staticmethod
        def data():
            return [1, 1]

    points = [Points()]
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)
    function.app.mount.model.starList.append(a)

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.app.mount.model,
                               'deletePoint',
                               return_value=False):
            suc = function.pointClicked(None, points, Event())
            assert not suc


def test_pointClicked_6(function):
    class Event:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def double():
            return False

    class Points:
        @staticmethod
        def data():
            return [1, 1]

    points = [Points()]
    function.app.mount.model.starList = list()
    a = ModelStar(obsSite=function.app.mount.obsSite)
    a.alt = 0
    a.az = 0
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    function.app.mount.model.starList.append(a)
    function.app.mount.model.starList.append(a)

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.app.mount.model,
                               'deletePoint',
                               return_value=True):
            with mock.patch.object(function,
                                   'refreshModel'):
                suc = function.pointClicked(None, points, Event())
                assert suc
