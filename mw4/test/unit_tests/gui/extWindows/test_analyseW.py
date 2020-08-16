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
import faulthandler
faulthandler.enable()

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

    shutil.copy('mw4/test/testData/test.model', 'mw4/test/model/test.model')

    class Test(QObject):
        config = {'mainW': {}}
        update1s = pyqtSignal()
        messageQueue = Queue()
        mwGlob = {'modelDir': 'mw4/test/model'}

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
    app.closeEvent(QCloseEvent())


def test_loadModel_1(app):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('', '', '')):
        suc = app.loadModel()
        assert not suc


def test_loadModel_2(app):
    with mock.patch.object(app,
                           'openFile',
                           return_value=('mw4/test/model/test.model',
                                         'test.model', '.model')):
        suc = app.loadModel()
        assert suc
