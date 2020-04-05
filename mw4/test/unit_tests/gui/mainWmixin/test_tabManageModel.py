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

# external packages
import PyQt5
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount

# local import
from mw4.gui.mainWmixin.tabManageModel import ManageModel
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, app, matplot

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        update1s = pyqtSignal()
        message = pyqtSignal(str, int)
        mwGlob = {'imageDir': 'mw4/test/image'}

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)
    matplot = MWidget.embedMatplot(widget, False)

    app = ManageModel(app=Test(), ui=ui,
                      clickable=MWidget().clickable)

    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.openDir = MWidget.openDir
    app.clearPolar = MWidget.clearPolar
    app.deleteLater = MWidget().deleteLater
    app.polarPlot = matplot
    app.errorPlot = matplot
    app.M_BLUE = MWidget.M_BLUE
    app.M_GREY = MWidget.M_GREY
    app.M_RED = MWidget.M_RED
    qtbot.addWidget(app)

    yield

    del widget, ui, Test, app


def test_initConfig_1():
    app.app.config['mainW'] = {}
    with mock.patch.object(app,
                           'showModelPolar'):
        app.initConfig()
        assert app.ui.targetRMS.value() == 99
        assert not app.ui.checkShowErrorValues.isChecked()


def test_storeConfig_1():
    app.ui.targetRMS.setValue(33)
    app.ui.checkShowErrorValues.setChecked(True)
    app.storeConfig()
    conf = app.app.config['mainW']
    assert conf['checkShowErrorValues']
    assert 33 == conf['targetRMS']


def test_setNameList():
    value = ['Test1', 'test2', 'test3', 'test4']
    app.app.mount.model.nameList = value
    app.setNameList(app.app.mount.model)
    assert 4 == app.ui.nameList.count()
    value = None
    app.app.mount.model.nameList = value
    app.setNameList(app.app.mount.model)
    assert 0 == app.ui.nameList.count()


def test_showModelPolar1():
    app.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    app.app.mount.model.parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                    '21:06:10.79,+45*20:52.8,  12.1,329',
                                    '23:13:58.02,+38*48:18.8,  31.0,162',
                                    '17:43:41.26,+59*15:30.7,   8.4,005',
                                    ],
                                   4)
    app.ui.checkShowErrorValues.setChecked(True)
    suc = app.showModelPolar(app.app.mount.model)
    assert suc


def test_showModelPolar2():
    app.app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    app.app.mount.model._starList = list()
    app.ui.checkShowErrorValues.setChecked(True)
    suc = app.showModelPolar(app.app.mount.model)
    assert not suc


def test_showModelPolar3():
    app.app.mount.obsSite.location = []
    app.app.mount.model._starList = list()
    app.ui.checkShowErrorValues.setChecked(True)
    suc = app.showModelPolar(app.app.mount.model)
    assert not suc


def test_showModelPolar4():
    app.ui.checkShowErrorValues.setChecked(True)
    app.app.mount.model._starList = list()
    suc = app.showModelPolar(app.app.mount.model)
    assert not suc


def test_clearRefreshName():
    app.app.mount.signals.namesDone.connect(app.clearRefreshName)
    suc = app.clearRefreshName()
    assert suc


def test_refreshName_1():
    with mock.patch.object(app.app.mount,
                           'getNames',
                           return_value=True):
        suc = app.refreshName()
        assert suc
        suc = app.clearRefreshName()
        assert suc


def test_refreshName_2(qtbot):
    suc = app.refreshName()
    assert suc
    with qtbot.waitSignal(app.app.message) as blocker:
        suc = app.refreshName()
        assert suc
        assert ['Model names refreshed', 0] == blocker.args


def test_loadName_1(qtbot):
    with mock.patch.object(app.ui.nameList,
                           'currentItem',
                           return_value=None):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.loadName()
            assert not suc
            assert ['No model name selected', 2] == blocker.args


def test_loadName_2(qtbot):
    class Test:
        pass

        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(app.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(app.app.mount.model,
                               'loadName',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.loadName()
                assert suc
                assert ['Model [test] loaded', 0] == blocker.args


def test_loadName_3(qtbot):
    class Test:
        pass

        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(app.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(app.app.mount.model,
                               'loadName',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.loadName()
                assert not suc
                assert ['Model [test] cannot be loaded', 2] == blocker.args


def test_saveName_1(qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('', True)):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.saveName()
            assert not suc
            assert ['No model name given', 2] == blocker.args


def test_saveName_2(qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(None, True)):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.saveName()
            assert not suc
            assert ['No model name given', 2] == blocker.args


def test_saveName_3(qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', False)):
        with qtbot.assertNotEmitted(app.app.message):
            suc = app.saveName()
            assert not suc


def test_saveName_4(qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', True)):
        with mock.patch.object(app.app.mount.model,
                               'storeName',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveName()
                assert not suc
                assert ['Model [test] cannot be saved', 2] == blocker.args


def test_saveName_5(qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('test', True)):
        with mock.patch.object(app.app.mount.model,
                               'storeName',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.saveName()
                assert suc
                assert ['Model [test] saved', 0] == blocker.args


def test_deleteName_1(qtbot):
    with mock.patch.object(app.ui.nameList,
                           'currentItem',
                           return_value=None):
        with qtbot.waitSignal(app.app.message) as blocker:
            suc = app.deleteName()
            assert not suc
            assert ['No model name selected', 2] == blocker.args


def test_deleteName_2(qtbot):
    class Test:
        pass

        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(app.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'question',
                               return_value=PyQt5.QtWidgets.QMessageBox.No):
            with qtbot.assertNotEmitted(app.app.message):
                suc = app.deleteName()
                assert not suc


def test_deleteName_3(qtbot):
    class Test:
        pass

        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(app.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'question',
                               return_value=PyQt5.QtWidgets.QMessageBox.Yes):
            with mock.patch.object(app.app.mount.model,
                                   'deleteName',
                                   return_value=True):
                with qtbot.waitSignal(app.app.message) as blocker:
                    suc = app.deleteName()
                    assert suc
                    assert ['Model [test] deleted', 0] == blocker.args


def test_deleteName_4(qtbot):
    class Test:
        pass

        @staticmethod
        def text():
            return 'test'
    with mock.patch.object(app.ui.nameList,
                           'currentItem',
                           return_value=Test):
        with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                               'question',
                               return_value=PyQt5.QtWidgets.QMessageBox.Yes):
            with mock.patch.object(app.app.mount.model,
                                   'deleteName',
                                   return_value=False):
                with qtbot.waitSignal(app.app.message) as blocker:
                    suc = app.deleteName()
                    assert not suc
                    assert ['Model [test] cannot be deleted', 2] == blocker.args


def test_cancelTargetRMS():
    app.runningTargetRMS = True
    suc = app.cancelTargetRMS()
    assert suc
    assert not app.runningTargetRMS


def test_clearRefreshModel():
    app.app.mount.signals.alignDone.connect(app.clearRefreshModel)
    suc = app.clearRefreshModel()
    assert suc


def test_refreshModel():
    app.app.mount.signals.alignDone.connect(app.clearRefreshModel)
    with mock.patch.object(app.app.mount,
                           'getAlign'):
        suc = app.clearRefreshModel()
        assert suc


def test_clearRunTargetRMS_1():
    app.app.mount.signals.alignDone.connect(app.clearRunTargetRMS)
    app.app.mount.model.errorRMS = 0.1
    suc = app.clearRunTargetRMS()
    assert suc


def test_clearRunTargetRMS_2():
    app.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    app.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    app.app.mount.model.errorRMS = 100
    app.app.mount.model.numberStars = 2
    app.runningTargetRMS = True
    app.app.mount.signals.alignDone.connect(app.clearRunTargetRMS)
    with mock.patch.object(app.app.mount.model,
                           'deletePoint',
                           return_value=False):
        with mock.patch.object(app.app.mount,
                               'getAlign'):
            suc = app.clearRunTargetRMS()
            assert suc


def test_clearRunTargetRMS_3():
    app.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    app.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    app.app.mount.model.errorRMS = 100
    app.app.mount.model.numberStars = 2
    app.runningTargetRMS = True
    app.app.mount.signals.alignDone.connect(app.clearRunTargetRMS)
    with mock.patch.object(app.app.mount.model,
                           'deletePoint',
                           return_value=True):
        with mock.patch.object(app.app.mount,
                               'getAlign'):
            suc = app.clearRunTargetRMS()
            assert suc


def test_clearRunTargetRMS_4():
    app.app.mount.model.errorRMS = 100
    app.runningTargetRMS = False
    app.app.mount.signals.alignDone.connect(app.clearRunTargetRMS)
    suc = app.clearRunTargetRMS()
    assert suc


def test_runTargetRMS():
    with mock.patch.object(app,
                           'clearRunTargetRMS'):
        suc = app.runTargetRMS()
        assert suc
    app.app.mount.signals.alignDone.connect(app.clearRunTargetRMS)


def test_cancelTargetRMS():
    suc = app.cancelTargetRMS()
    assert suc
    assert not app.runningTargetRMS


def test_clearModel_1(qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.No):
        suc = app.clearModel()
        assert not suc


def test_clearModel_2(qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(app.app.mount.model,
                               'clearAlign',
                               return_value=False):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.clearModel()
                assert not suc
                assert ['Actual model cannot be cleared', 2] == blocker.args


def test_clearModel_3(qtbot):
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'question',
                           return_value=PyQt5.QtWidgets.QMessageBox.Yes):
        with mock.patch.object(app.app.mount.model,
                               'clearAlign',
                               return_value=True):
            with qtbot.waitSignal(app.app.message) as blocker:
                suc = app.clearModel()
                assert suc
                assert ['Actual model cleared', 0] == blocker.args


def test_deleteWorstPoint_1():
    app.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    app.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    with mock.patch.object(app.app.mount.model,
                           'deletePoint',
                           return_value=False):
        suc = app.deleteWorstPoint()
        assert not suc


def test_deleteWorstPoint_2():
    app.app.mount.model.addStar('12:00:00, 180:00:00, 5, 90, 1')
    app.app.mount.model.addStar('12:00:00, 120:00:00, 4, 90, 2')
    with mock.patch.object(app.app.mount.model,
                           'deletePoint',
                           return_value=True):
        with mock.patch.object(app,
                               'refreshModel'):
            suc = app.deleteWorstPoint()
            assert suc
