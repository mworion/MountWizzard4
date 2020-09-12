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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import shutil
from queue import Queue
import json

# external packages
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

# local import
from gui.extWindows.analyseW import AnalyseWindow
from gui.utilities.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def app(qtbot):
    global Test

    shutil.copy('tests/testData/test.model', 'tests/model/test.model')

    class Test(QObject):
        config = {'mainW': {}}
        update1s = pyqtSignal()
        showAnalyse = pyqtSignal()
        messageQueue = Queue()
        mwGlob = {'modelDir': 'tests/model'}

    with mock.patch.object(AnalyseWindow,
                           'show'):
        app = AnalyseWindow(app=Test())
        app.generateFlat = MWidget().generateFlat
        app.generatePolar = MWidget().generatePolar
        qtbot.addWidget(app)
        yield app


def test_initConfig_1(qtbot, app):
    suc = app.initConfig()
    assert suc


def test_initConfig_2(qtbot, app):
    app.app.config['messageW'] = {'winPosX': 10000}
    suc = app.initConfig()
    assert suc


def test_initConfig_3(qtbot, app):
    app.app.config['messageW'] = {'winPosY': 10000}
    suc = app.initConfig()
    assert suc


def test_storeConfig_1(qtbot, app):
    if 'messageW' in app.app.config:
        del app.app.config['messageW']
    suc = app.storeConfig()
    assert suc


def test_storeConfig_2(qtbot, app):
    app.app.config['messageW'] = {}
    suc = app.storeConfig()
    assert suc


def test_closeEvent_1(qtbot, app):
    app.app.showOriginalAnalyseData.connect(app.showOriginalAnalyseData)
    app.closeEvent(QCloseEvent())


def test_showWindow_1(qtbot, app):
    suc = app.showWindow()
    assert suc


def test_writeGui_1(qtbot, app):
    suc = app.writeGui([{'a': 1}], 'test')
    assert suc
    assert app.ui.filename.text() == 'test'
    assert app.ui.mirrored.text() == ''


def test_generateDataSets(qtbot, app):
    with open('tests/testData/test.model', 'r') as infile:
        modelJSON = json.load(infile)

    suc = app.generateDataSets(modelJSON)
    assert suc
    assert app.latitude == 48.1


def test_processModel_1(qtbot, app):
    suc = app.processModel('tests/testData/test.model')
    assert suc


def test_loadModel_1(app):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('', '', '')):
        with mock.patch.object(app,
                               'processModel'):
            suc = app.loadModel()
            assert suc


def test_loadModel_2(app):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('test', 'test', 'test')):
        with mock.patch.object(app,
                               'processModel'):
            suc = app.loadModel()
            assert suc


def test_showAnalyse_1(app):
    with mock.patch.object(app,
                           'processModel'):
        suc = app.showOriginalAnalyseData('test')
        assert suc
