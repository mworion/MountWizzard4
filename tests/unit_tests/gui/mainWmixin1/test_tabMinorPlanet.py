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
import pytest
from unittest import mock
import os
import json
import builtins

# external packages
from PyQt5.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
import mw4.gui.utilities
from mw4.gui.mainWmixin.tabMinorPlanet import MinorPlanet
from mw4.logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    class Mixin(MWidget, MinorPlanet):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.databaseProcessing = DataWriter(self.app)
            self.threadPool = QThreadPool()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            MinorPlanet.__init__(self)

    window = Mixin()
    yield window
    window.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    with mock.patch.object(function,
                           'setupMinorPlanetSourceURLsDropDown'):
        suc = function.initConfig()
        assert suc
        assert function.installPath == 'tests/workDir/data'


def test_initConfig_2(function):
    temp = function.app.automation
    function.app.automation = None
    with mock.patch.object(function,
                           'setupMinorPlanetSourceURLsDropDown'):
        suc = function.initConfig()
        assert suc
        assert function.installPath == 'tests/workDir/data'
    function.app.automation = temp


def test_initConfig_3(function):
    function.app.automation.installPath = 'test'
    with mock.patch.object(function,
                           'setupMinorPlanetSourceURLsDropDown'):
        suc = function.initConfig()
        assert suc
        assert function.installPath == 'test'


def test_storeConfig_1(function):
    function.thread = None
    suc = function.storeConfig()
    assert suc


def test_setupMinorPlanetSourceURLsDropDown(function):
    suc = function.setupMinorPlanetSourceURLsDropDown()
    assert suc


def test_filterMinorPlanetNamesList(function):
    function.ui.filterMinorPlanet.setText('test')
    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('test')
    function.ui.listMinorPlanetNames.addItem('minor')

    suc = function.filterMinorPlanetNamesList()
    assert suc


def test_generateName_1(function):
    val = function.generateName(0, {})
    assert val == ''


def test_generateName_2(function):
    mp = {'Designation_and_name': 'test'}
    val = function.generateName(0, mp)
    assert val == '    0: test'


def test_generateName_3(function):
    mp = {'Name': 'test',
          'Number': '123',
          'Principal_desig': 'base'}
    val = function.generateName(0, mp)
    assert val == '    0: base - test 123'


def test_generateName_4(function):
    mp = {'Principal_desig': 'base'}
    val = function.generateName(0, mp)
    assert val == '    0: base'


def test_generateName_5(function):
    mp = {'Name': 'test',
          'Number': '123'}
    val = function.generateName(0, mp)
    assert val == '    0: test 123'


def test_setupMinorPlanetNameList_1(function):
    function.minorPlanets = ['test', 'aster']
    with mock.patch.object(function,
                           'generateName',
                           return_value=''):
        suc = function.setupMinorPlanetNameList()
        assert suc


def test_setupMinorPlanetNameList_2(function):
    function.minorPlanets = ['test', 'aster']
    with mock.patch.object(function,
                           'generateName',
                           return_value='test1'):
        suc = function.setupMinorPlanetNameList()
        assert suc


def test_processSourceData_1(function):
    with mock.patch.object(mw4.gui.mainWmixin.tabMinorPlanet,
                           'DownloadPopup'):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=False):
            with mock.patch.object(json,
                                   'load',
                                   return_value=[]):
                with mock.patch.object(builtins,
                                       'open'):
                    function.minorPlanetSourceURLs['test'] = 'test.json.gz'
                    function.ui.minorPlanetSource.clear()
                    function.ui.minorPlanetSource.addItem('test')
                    function.ui.minorPlanetSource.setCurrentIndex(0)
                    function.ui.isOnline.setChecked(True)

                    suc = function.processSourceData()
                    assert not suc


def test_processSourceData_2(function):
    with mock.patch.object(mw4.gui.mainWmixin.tabMinorPlanet,
                           'DownloadPopup'):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=True):
            with mock.patch.object(json,
                                   'load',
                                   return_value=[]):
                with mock.patch.object(builtins,
                                       'open'):
                    function.minorPlanetSourceURLs['test'] = 'test.json.gz'
                    function.ui.minorPlanetSource.clear()
                    function.ui.minorPlanetSource.addItem('test')
                    function.ui.minorPlanetSource.setCurrentIndex(0)
                    function.ui.isOnline.setChecked(True)

                    suc = function.processSourceData()
                    assert suc


def test_processSourceData_3(function):
    with mock.patch.object(mw4.gui.mainWmixin.tabMinorPlanet,
                           'DownloadPopup'):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=True):
            with mock.patch.object(json,
                                   'load',
                                   return_value=[],
                                   side_effect=Exception):
                with mock.patch.object(builtins,
                                       'open'):
                    function.minorPlanetSourceURLs['test'] = 'test.json.gz'
                    function.ui.minorPlanetSource.clear()
                    function.ui.minorPlanetSource.addItem('test')
                    function.ui.minorPlanetSource.setCurrentIndex(0)
                    function.ui.isOnline.setChecked(True)

                    suc = function.processSourceData()
                    assert suc


def test_loadMPCDataFromSourceURLs_1(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('xxx')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    suc = function.loadMPCDataFromSourceURLs()
    assert not suc


def test_loadMPCDataFromSourceURLs_2(function):
    function.ui.minorPlanetSource.clear()
    function.minorPlanetSourceURLs['test'] = 'test.json.gz'
    function.ui.minorPlanetSource.addItem('Please select')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    suc = function.loadMPCDataFromSourceURLs()
    assert not suc


def test_loadMPCDataFromSourceURLs_3(function):
    with mock.patch.object(mw4.gui.mainWmixin.tabMinorPlanet,
                           'DownloadPopup'):
        with mock.patch.object(os.path,
                               'isfile',
                               return_value=False):
            function.minorPlanetSourceURLs['test'] = 'test.json.gz'
            function.ui.minorPlanetSource.clear()
            function.ui.minorPlanetSource.addItem('test')
            function.ui.minorPlanetSource.setCurrentIndex(0)
            function.ui.isOnline.setChecked(True)
            suc = function.loadMPCDataFromSourceURLs()
            assert suc


def test_progMinorPlanets_1(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    raw = 'test'

    with mock.patch.object(function.databaseProcessing,
                           'writeCometMPC',
                           return_value=False):
        suc = function.progMinorPlanets(raw)
        assert not suc


def test_progMinorPlanets_2(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Asteroid')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    raw = 'test'

    with mock.patch.object(function.databaseProcessing,
                           'writeAsteroidMPC',
                           return_value=False):
        suc = function.progMinorPlanets(raw)
        assert not suc


def test_progMinorPlanets_3(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    raw = 'test'

    with mock.patch.object(function.databaseProcessing,
                           'writeCometMPC',
                           return_value=True):
        with mock.patch.object(function.app.automation,
                               'uploadMPCData',
                               return_value=False):
            suc = function.progMinorPlanets(raw)
            assert not suc


def test_progMinorPlanets_4(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    raw = 'test'

    with mock.patch.object(function.databaseProcessing,
                           'writeCometMPC',
                           return_value=True):
        with mock.patch.object(function.app.automation,
                               'uploadMPCData',
                               return_value=True):
            suc = function.progMinorPlanets(raw)
            assert suc


def test_mpcFilter_1(function):
    raw = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]
    function.ui.filterMinorPlanet.setText('test')

    val = function.mpcFilter(raw)
    assert val == [{'Principal_desig': 'test'}]


def test_mpcGUI_1(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Please')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    suc = function.mpcGUI()
    assert not suc


def test_mpcGUI_2(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    with mock.patch.object(function,
                           'checkUpdaterOK',
                           return_value=False):
        suc = function.mpcGUI()
        assert not suc


def test_mpcGUI_3(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)

    with mock.patch.object(function,
                           'checkUpdaterOK',
                           return_value=True):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=False):
            suc = function.mpcGUI()
            assert not suc


def test_mpcGUI_4(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)

    with mock.patch.object(function,
                           'checkUpdaterOK',
                           return_value=True):
        with mock.patch.object(function,
                               'messageDialog',
                               return_value=True):
            suc = function.mpcGUI()
            assert suc


def test_progMinorPlanetsSelected_1(function):
    with mock.patch.object(function,
                           'mpcGUI',
                           return_value=False):
        suc = function.progMinorPlanetsSelected()
        assert not suc


def test_progMinorPlanetsSelected_2(function):
    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('0:test')
    function.minorPlanets = ['test']

    model = function.ui.listMinorPlanetNames.model()
    ind = model.index(0)
    function.ui.listMinorPlanetNames.setCurrentIndex(ind)

    with mock.patch.object(function,
                           'mpcGUI',
                           return_value=True):
        with mock.patch.object(function,
                               'progMinorPlanets'):
            suc = function.progMinorPlanetsSelected()
            assert suc


def test_progMinorPlanetsFiltered_1(function):
    with mock.patch.object(function,
                           'mpcGUI',
                           return_value=False):
        suc = function.progMinorPlanetsFiltered()
        assert not suc


def test_progMinorPlanetsFiltered_2(function):
    with mock.patch.object(function,
                           'mpcGUI',
                           return_value=True):
        with mock.patch.object(function,
                               'progMinorPlanets'):
            with mock.patch.object(function,
                                   'mpcFilter'):
                suc = function.progMinorPlanetsFiltered()
                assert suc


def test_progMinorPlanetsFull_1(function):
    with mock.patch.object(function,
                           'mpcGUI',
                           return_value=False):
        suc = function.progMinorPlanetsFull()
        assert not suc


def test_progMinorPlanetsFull_2(function):
    with mock.patch.object(function,
                           'mpcGUI',
                           return_value=True):
        with mock.patch.object(function,
                               'progMinorPlanets'):
            suc = function.progMinorPlanetsFull()
            assert suc
