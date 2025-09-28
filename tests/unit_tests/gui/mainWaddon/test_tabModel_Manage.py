############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
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
from pathlib import Path

# external packages
import PySide6
from PySide6.QtCore import Qt
from skyfield.api import Star, Angle
from mountcontrol.modelStar import ModelStar

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import gui
from gui.mainWaddon.tabModel_Manage import ModelManage
import gui.mainWaddon.tabModel_Manage
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    files = glob.glob("tests/work/model/*.model")
    for f in files:
        os.remove(f)
    shutil.copy("tests/testData/test.model", "tests/work/model/test.model")
    shutil.copy("tests/testData/test1.model", "tests/work/model/test1.model")
    shutil.copy("tests/testData/test-opt.model", "tests/work/model/test-opt.model")

    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = ModelManage(mainW)
    yield window
    mainW.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    function.app.config["mainW"] = {}
    with mock.patch.object(function, "showModelPosition"):
        with mock.patch.object(function, "showErrorAscending"):
            with mock.patch.object(function, "showErrorDistribution"):
                function.initConfig()
                assert function.ui.targetRMS.value() == 10


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_updateColorSet(function):
    with mock.patch.object(function, "showModelPosition"):
        with mock.patch.object(function, "showErrorAscending"):
            with mock.patch.object(function, "showErrorDistribution"):
                function.updateColorSet()


def test_setNameList(function):
    value = ["Test1", "test2", "test3", "test4"]
    function.app.mount.model.nameList = value
    function.setNameList(function.app.mount.model)
    assert 4 == function.ui.nameList.count()
    function.app.mount.model.nameList = []


def test_showModelPosition_1(function):
    function.app.mount.model.starList = list()
    function.showModelPosition()


def test_showModelPosition_2(function):
    star = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=0,
        errorAngle=0,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star, star, star]
    function.showModelPosition()


def test_showErrorAscending_1(function):
    star = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=0,
        errorAngle=0,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star, star, star]
    function.showErrorAscending()


def test_showErrorAscending_2(function):
    function.app.mount.model.starList = list()
    function.showErrorAscending()


def test_showErrorAscending_3(function):
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    function.app.mount.model.starList = list()
    function.showErrorAscending()
    function.app.mount.obsSite.location = temp


def test_showErrorAscending_4(function):
    function.app.mount.model.starList = list()
    function.showErrorAscending()


def test_showErrorDistribution_1(function):
    star = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=0,
        errorAngle=0,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star, star, star]
    function.showErrorDistribution()


def test_showErrorDistribution_2(function):
    function.app.mount.model.starList = list()
    function.showErrorDistribution()


def test_showErrorDistribution_3(function):
    temp = function.app.mount.obsSite.location
    function.app.mount.obsSite.location = None
    function.app.mount.model.starList = list()
    function.showErrorDistribution()
    function.app.mount.obsSite.location = temp


def test_showErrorDistribution_4(function):
    function.app.mount.model.starList = list()
    function.showErrorDistribution()


def test_clearRefreshName(function):
    function.app.mount.signals.namesDone.connect(function.clearRefreshName)
    function.clearRefreshName()


def test_refreshName_1(function):
    with mock.patch.object(function.app.mount, "getNames", return_value=True):
        function.refreshName()
        function.clearRefreshName()


def test_refreshName_2(function):
    function.refreshName()


def test_loadName_1(function):
    with mock.patch.object(function.ui.nameList, "currentItem", return_value=None):
        function.loadName()


def test_loadName_2(function):
    class Test:
        @staticmethod
        def text():
            return "test"

    with mock.patch.object(function.ui.nameList, "currentItem", return_value=Test):
        with mock.patch.object(function.app.mount.model, "loadName", return_value=True):
            function.loadName()


def test_loadName_3(function):
    class Test:
        @staticmethod
        def text():
            return "test"

    with mock.patch.object(function.ui.nameList, "currentItem", return_value=Test):
        with mock.patch.object(function.app.mount.model, "loadName", return_value=False):
            function.loadName()


def test_saveName_1(function):
    with mock.patch.object(PySide6.QtWidgets.QInputDialog, "getText", return_value=("", True)):
        function.saveName()


def test_saveName_2(function):
    with mock.patch.object(
        PySide6.QtWidgets.QInputDialog, "getText", return_value=(None, True)
    ):
        function.saveName()


def test_saveName_3(function):
    with mock.patch.object(
        PySide6.QtWidgets.QInputDialog, "getText", return_value=("test", False)
    ):
        function.saveName()


def test_saveName_4(function):
    with mock.patch.object(
        PySide6.QtWidgets.QInputDialog, "getText", return_value=("test", True)
    ):
        with mock.patch.object(function.app.mount.model, "storeName", return_value=False):
            function.saveName()


def test_saveName_5(function):
    with mock.patch.object(
        PySide6.QtWidgets.QInputDialog, "getText", return_value=("test", True)
    ):
        with mock.patch.object(function.app.mount.model, "storeName", return_value=True):
            function.saveName()


def test_deleteName_1(function):
    with mock.patch.object(function.ui.nameList, "currentItem", return_value=None):
        function.deleteName()


def test_deleteName_2(function):
    class Test:
        @staticmethod
        def text():
            return "test"

    with mock.patch.object(function.ui.nameList, "currentItem", return_value=Test):
        with mock.patch.object(MWidget, "messageDialog", return_value=False):
            function.deleteName()


def test_deleteName_3(function):
    class Test:
        @staticmethod
        def text():
            return "test"

    with mock.patch.object(function.ui.nameList, "currentItem", return_value=Test):
        with mock.patch.object(MWidget, "messageDialog", return_value=True):
            with mock.patch.object(function.app.mount.model, "deleteName", return_value=True):
                function.deleteName()


def test_deleteName_4(function):
    class Test:
        @staticmethod
        def text():
            return "test"

    with mock.patch.object(function.ui.nameList, "currentItem", return_value=Test):
        with mock.patch.object(MWidget, "messageDialog", return_value=True):
            with mock.patch.object(function.app.mount.model, "deleteName", return_value=False):
                function.deleteName()


def test_writeBuildModelOptimized_0(function):
    function.fittedModelPath = Path("tests/work/model/test-opt.model")
    function.writeBuildModelOptimized([])


def test_writeBuildModelOptimized_1(function):
    function.fittedModelPath = Path("tests/work/model/test-opt.model")
    with mock.patch.object(
        json,
        "load",
        return_value=[{"errorIndex": 1}, {"errorIndex": 3}],
        side_effect=Exception,
    ):
        function.writeBuildModelOptimized([1])


def test_writeBuildModelOptimized_2(function):
    function.fittedModelPath = Path("tests/work/model/test-opt.model")
    with mock.patch.object(gui.mainWaddon.tabModel_Manage, "writeRetrofitData"):
        with mock.patch.object(
            json, "load", return_value=[{"errorIndex": 1}, {"errorIndex": 3}]
        ):
            with mock.patch.object(json, "dump"):
                function.writeBuildModelOptimized([1])


def test_clearRefreshModel_1(function):
    function.app.mount.signals.getModelDone.connect(function.clearRefreshModel)
    with mock.patch.object(
        gui.mainWaddon.tabModel_Manage, "findFittingModel", return_value=(Path(""), [])
    ):
        with mock.patch.object(Path, "is_file", return_value=True):
            with mock.patch.object(function, "writeBuildModelOptimized"):
                function.clearRefreshModel()


def test_clearRefreshModel_2(function):
    function.app.mount.signals.getModelDone.connect(function.clearRefreshModel)
    with mock.patch.object(
        gui.mainWaddon.tabModel_Manage, "findFittingModel", return_value=(Path(""), [])
    ):
        with mock.patch.object(Path, "is_file", return_value=False):
            with mock.patch.object(function, "sendAnalyseFileName"):
                function.clearRefreshModel()


def test_clearModel_1(function):
    with mock.patch.object(MWidget, "messageDialog", return_value=False):
        function.clearModel()


def test_clearModel_2(function):
    with mock.patch.object(MWidget, "messageDialog", return_value=True):
        with mock.patch.object(function.app.mount.model, "clearModel", return_value=False):
            function.clearModel()


def test_clearModel_3(function):
    with mock.patch.object(MWidget, "messageDialog", return_value=True):
        with mock.patch.object(function.app.mount.model, "clearModel", return_value=True):
            function.clearModel()


def test_deleteWorstPoint_1(function):
    star = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=0,
        errorAngle=0,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star, star, star]
    function.app.mount.model.numberStars = 0
    function.deleteWorstPoint()


def test_deleteWorstPoint_2(function):
    star = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=0,
        errorAngle=0,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star, star, star]
    function.app.mount.model.numberStars = 3
    with mock.patch.object(function.app.mount.model, "deletePoint", return_value=True):
        with mock.patch.object(function, "refreshModel"):
            function.deleteWorstPoint()


def test_deleteWorstPoint_3(function):
    star = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=0,
        errorAngle=0,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star, star, star]
    function.app.mount.model.numberStars = 3
    with mock.patch.object(function.app.mount.model, "deletePoint", return_value=False):
        with mock.patch.object(function, "refreshModel"):
            function.deleteWorstPoint()


def test_runTargetRMS_1(function):
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    function.app.mount.signals.getModelDone.connect(function.runTargetRMS)
    function.app.mount.model.errorRMS = 0.1
    function.runTargetRMS()


def test_runTargetRMS_2(function):
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    star1 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=5,
        errorAngle=90,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    star2 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=4,
        errorAngle=90,
        number=2,
        obsSite=function.app.mount.obsSite,
    )
    star3 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=3,
        errorAngle=90,
        number=3,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star1, star2, star3]

    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 3
    function.runningTargetRMS = True
    function.app.mount.signals.getModelDone.connect(function.runTargetRMS)
    with mock.patch.object(function.app.mount.model, "deletePoint", return_value=False):
        with mock.patch.object(function.app.mount, "getModel"):
            function.runTargetRMS()


def test_runTargetRMS_3(function):
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    star1 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=5,
        errorAngle=90,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    star2 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=4,
        errorAngle=90,
        number=2,
        obsSite=function.app.mount.obsSite,
    )
    star3 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=3,
        errorAngle=90,
        number=3,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star1, star2, star3]

    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 3
    function.runningTargetRMS = True
    function.app.mount.signals.getModelDone.connect(function.runTargetRMS)
    with mock.patch.object(function.app.mount.model, "deletePoint", return_value=True):
        with mock.patch.object(function.app.mount, "getModel"):
            function.runTargetRMS()


def test_runTargetRMS_4(function):
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = None
    function.runningTargetRMS = False
    function.app.mount.signals.getModelDone.connect(function.runTargetRMS)
    function.runTargetRMS()


def test_runSingleRMS_1(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    star1 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=0.1,
        errorAngle=90,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star1]
    function.app.mount.signals.getModelDone.connect(function.runSingleRMS)
    function.app.mount.model.errorRMS = 0.1
    function.runSingleRMS()


def test_runSingleRMS_2(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    star1 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=5,
        errorAngle=90,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    star2 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=4,
        errorAngle=90,
        number=2,
        obsSite=function.app.mount.obsSite,
    )
    star3 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=3,
        errorAngle=90,
        number=3,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star1, star2, star3]
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 3
    function.runningTargetRMS = True
    function.app.mount.signals.getModelDone.connect(function.runSingleRMS)
    with mock.patch.object(function.app.mount.model, "deletePoint", return_value=False):
        with mock.patch.object(function.app.mount, "getModel"):
            function.runSingleRMS()


def test_runSingleRMS_3(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    star1 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=5,
        errorAngle=90,
        number=1,
        obsSite=function.app.mount.obsSite,
    )
    star2 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=4,
        errorAngle=90,
        number=2,
        obsSite=function.app.mount.obsSite,
    )
    star3 = ModelStar(
        Star(ra_hours=0, dec_degrees=0),
        errorRMS=3,
        errorAngle=90,
        number=3,
        obsSite=function.app.mount.obsSite,
    )
    function.app.mount.model.starList = [star1, star2, star3]
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = 3
    function.runningTargetRMS = True
    function.app.mount.signals.getModelDone.connect(function.runSingleRMS)
    with mock.patch.object(function.app.mount.model, "deletePoint", return_value=True):
        with mock.patch.object(function.app.mount, "getModel"):
            function.runSingleRMS()


def test_runSingleRMS_4(function):
    function.ui.targetRMS.setValue(1)
    function.runningOptimize = True
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    function.app.mount.model.errorRMS = 100
    function.app.mount.model.numberStars = None
    function.runningTargetRMS = False
    function.app.mount.signals.getModelDone.connect(function.runSingleRMS)
    with mock.patch.object(function, "finishOptimize"):
        function.runSingleRMS()


def test_runOptimize_1(function):
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    with mock.patch.object(function, "runTargetRMS"):
        function.runOptimize()


def test_runOptimize_2(function):
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    with mock.patch.object(function, "runSingleRMS"):
        function.runOptimize()


def test_finishOptimize_1(function):
    function.ui.optimizeOverall.setChecked(False)
    function.ui.optimizeSingle.setChecked(True)
    function.app.mount.signals.getModelDone.connect(function.runSingleRMS)
    function.finishOptimize()


def test_finishOptimize_2(function):
    function.ui.optimizeOverall.setChecked(True)
    function.ui.optimizeSingle.setChecked(False)
    function.app.mount.signals.getModelDone.connect(function.runTargetRMS)
    function.finishOptimize()


def test_cancelOptimize_1(function):
    function.cancelOptimize()
    assert not function.runningOptimize


def test_sendAnalyseFile_1(function):
    function.fittedModelPath = Path("test")
    function.sendAnalyseFileName()


def test_sendAnalyseFile_2(function):
    function.fittedModelPath = Path("tests/testData/test.model")
    function.sendAnalyseFileName()


def test_pointClicked_1(function):
    class Event:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def double():
            return True

    function.pointClicked(None, None, Event())


def test_pointClicked_2(function):
    class Event:
        @staticmethod
        def button():
            return Qt.MouseButton.RightButton

        @staticmethod
        def double():
            return False

    function.pointClicked(None, None, Event())


def test_pointClicked_3(function):
    class Event:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def double():
            return False

    class Points:
        @staticmethod
        def data():
            return []

    points = [Points()]
    function.pointClicked(None, points, Event())


def test_pointClicked_4(function):
    class Event:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

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

    with mock.patch.object(MWidget, "messageDialog", return_value=False):
        function.pointClicked(None, points, Event())


def test_pointClicked_5(function):
    class Event:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

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

    with mock.patch.object(MWidget, "messageDialog", return_value=True):
        with mock.patch.object(function.app.mount.model, "deletePoint", return_value=False):
            function.pointClicked(None, points, Event())


def test_pointClicked_6(function):
    class Event:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

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

    with mock.patch.object(MWidget, "messageDialog", return_value=True):
        with mock.patch.object(function.app.mount.model, "deletePoint", return_value=True):
            with mock.patch.object(function, "refreshModel"):
                function.pointClicked(None, points, Event())
