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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import shutil
import os
import json
import builtins

# external packages
from PyQt5.QtCore import QThreadPool

# local import
from tests.baseTestSetupMixins import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabMinorPlanetTime import MinorPlanetTime
from logic.databaseProcessing.dataWriter import DataWriter


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, MinorPlanetTime):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.databaseProcessing = DataWriter(self.app)
            self.threadPool = QThreadPool()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            MinorPlanetTime.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    with mock.patch.object(function,
                           'setupMinorPlanetSourceURLsDropDown'):
        suc = function.initConfig()
        assert suc
        assert function.installPath == 'tests/data'


def test_initConfig_2(function):
    function.app.automation = None
    with mock.patch.object(function,
                           'setupMinorPlanetSourceURLsDropDown'):
        suc = function.initConfig()
        assert suc
        assert function.installPath == 'tests/data'


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
    with mock.patch('gui.mainWmixin.tabMinorPlanetTime.DownloadPopup'):
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
    with mock.patch('gui.mainWmixin.tabMinorPlanetTime.DownloadPopup'):
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
    with mock.patch('gui.mainWmixin.tabMinorPlanetTime.DownloadPopup'):
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


def test_loadDataFromSourceURLs_1(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('xxx')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    suc = function.loadMPCDataFromSourceURLs()
    assert not suc


def test_loadDataFromSourceURLs_2(function):
    function.ui.minorPlanetSource.clear()
    function.minorPlanetSourceURLs['test'] = 'test.json.gz'
    function.ui.minorPlanetSource.addItem('Please select')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    suc = function.loadMPCDataFromSourceURLs()
    assert not suc


def test_loadDataFromSourceURLs_3(function):
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        function.minorPlanetSourceURLs['test'] = 'test.json.gz'
        function.ui.minorPlanetSource.clear()
        function.ui.minorPlanetSource.addItem('test')
        function.ui.minorPlanetSource.setCurrentIndex(0)
        function.ui.isOnline.setChecked(False)


def test_progEarthRotationDataToMount_1(function):
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.progEarthRotationDataToMount()
        assert not suc


def test_progEarthRotationDataToMount_3(function):
    function.app.automation = None
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeEarthRotationData',
                               return_value=False):
            suc = function.progEarthRotationDataToMount()
            assert not suc


def test_progEarthRotationDataToMount_4(function):
    function.app.automation = None
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeEarthRotationData',
                               return_value=True):
            suc = function.progEarthRotationDataToMount()
            assert not suc


def test_progEarthRotationDataToMount_5(function):
    class Test:
        installPath = 'None'

        @staticmethod
        def uploadEarthRotationData():
            return False

    function.app.automation = Test()
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeEarthRotationData',
                               return_value=True):
            suc = function.progEarthRotationDataToMount()
            assert not suc


def test_progEarthRotationDataToMount_6(function):
    class Test:
        installPath = None

        @staticmethod
        def uploadEarthRotationData():
            return True

    function.app.automation = Test()
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeEarthRotationData',
                               return_value=True):
            suc = function.progEarthRotationDataToMount()
            assert not suc


def test_progEarthRotationDataToMount_7(function):
    class Test:
        installPath = 'test'

        @staticmethod
        def uploadEarthRotationData():
            return True

    function.app.automation = Test()
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeEarthRotationData',
                               return_value=True):
            suc = function.progEarthRotationDataToMount()
            assert suc


def test_progMinorPlanetToMount_1(function):
    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('00000: test')
    function.ui.listMinorPlanetNames.setCurrentRow(0)
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.minorPlanets = [1]
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.progMinorPlanetToMount()
        assert not suc


def test_progMinorPlanetToMount_2(function):
    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('00000: test')
    function.ui.listMinorPlanetNames.setCurrentRow(0)
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.minorPlanets = [1]
    function.app.automation = None
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=False):
            suc = function.progMinorPlanetToMount()
            assert not suc


def test_progMinorPlanetToMount_3(function):
    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('00000: test')
    function.ui.listMinorPlanetNames.setCurrentRow(0)
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Asteroid')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.minorPlanets = [1]
    function.app.automation = None
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeAsteroidMPC',
                               return_value=False):
            suc = function.progMinorPlanetToMount()
            assert not suc


def test_progMinorPlanetToMount_4(function):
    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('00000: test')
    function.ui.listMinorPlanetNames.setCurrentRow(0)
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Asteroid')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.minorPlanets = [1]
    function.app.automation = None
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeAsteroidMPC',
                               return_value=True):
            suc = function.progMinorPlanetToMount()
            assert not suc


def test_progMinorPlanetToMount_5(function):
    class Test:
        installPath = 'None'

        @staticmethod
        def uploadMPCData(comets=False):
            return False

    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('00000: test')
    function.ui.listMinorPlanetNames.setCurrentRow(0)
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.minorPlanets = [1]
    function.app.automation = Test()
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            suc = function.progMinorPlanetToMount()
            assert not suc


def test_progMinorPlanetToMount_6(function):
    class Test:
        installPath = None

        @staticmethod
        def uploadMPCData(comets=False):
            return True

    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('00000: test')
    function.ui.listMinorPlanetNames.setCurrentRow(0)
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.minorPlanets = [1]
    function.app.automation = Test()
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            suc = function.progMinorPlanetToMount()
            assert not suc


def test_progMinorPlanetToMount_7(function):
    class Test:
        installPath = None

        @staticmethod
        def uploadMPCData(comets=False):
            return True

    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('00000: test')
    function.ui.listMinorPlanetNames.setCurrentRow(0)
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Asteroid')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.minorPlanets = [1]
    function.app.automation = Test()
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeAsteroidMPC',
                               return_value=True):
            suc = function.progMinorPlanetToMount()
            assert not suc


def test_progMinorPlanetToMount_8(function):
    class Test:
        installPath = 'test'

        @staticmethod
        def uploadMPCData(comets=False):
            return True

    function.ui.listMinorPlanetNames.clear()
    function.ui.listMinorPlanetNames.addItem('00000: test')
    function.ui.listMinorPlanetNames.setCurrentRow(0)
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Asteroid')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.minorPlanets = [1]
    function.app.automation = Test()
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeAsteroidMPC',
                               return_value=True):
            suc = function.progMinorPlanetToMount()
            assert suc


def test_progMinorPlanetsFiltered_1(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Please')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    suc = function.progMinorPlanetsFiltered()
    assert not suc


def test_progMinorPlanetsFiltered_2(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.progMinorPlanetsFiltered()
        assert not suc


def test_progMinorPlanetsFiltered_3(function):
    function.app.automation = None
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=False):
            suc = function.progMinorPlanetsFiltered()
            assert not suc


def test_progMinorPlanetsFiltered_4(function):
    function.app.automation = None
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            suc = function.progMinorPlanetsFiltered()
            assert not suc


def test_progMinorPlanetsFiltered_4a(function):
    function.app.automation = None
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Asteroid')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'00000: test'}, {'00000: 0815'}]
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeAsteroidMPC',
                               return_value=True):
            suc = function.progMinorPlanetsFiltered()
            assert not suc


def test_progMinorPlanetsFiltered_5(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            suc = function.progMinorPlanetsFiltered()
            assert not suc


def test_progMinorPlanetsFiltered_6(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadMPCData',
                                   return_value=False):
                suc = function.progMinorPlanetsFiltered()
                assert not suc


def test_progMinorPlanetsFiltered_7(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadMPCData',
                                   return_value=True):
                suc = function.progMinorPlanetsFiltered()
                assert suc


def test_progMinorPlanetsFiltered_8(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]
    function.app.automation.installPath = None
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadMPCData',
                                   return_value=True):
                suc = function.progMinorPlanetsFiltered()
                assert not suc


def test_progMinorPlanetsFull_1(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Please')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    suc = function.progMinorPlanetsFull()
    assert not suc


def test_progMinorPlanetsFull_2(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=False):
        suc = function.progMinorPlanetsFull()
        assert not suc


def test_progMinorPlanetsFull_3(function):
    function.app.automation = None
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=False):
            suc = function.progMinorPlanetsFull()
            assert not suc


def test_progMinorPlanetsFull_4(function):
    function.app.automation = None
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]

    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            suc = function.progMinorPlanetsFull()
            assert not suc


def test_progMinorPlanetsFull_4a(function):
    function.app.automation = None
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Asteroid')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeAsteroidMPC',
                               return_value=True):
            suc = function.progMinorPlanetsFull()
            assert not suc


def test_progMinorPlanetsFull_5(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]
    function.app.automation.installPath = 'None'
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadMPCData',
                                   return_value=False):
                suc = function.progMinorPlanetsFull()
                assert not suc


def test_progMinorPlanetsFull_6(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]
    function.app.automation.installPath = 'None'
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadMPCData',
                                   return_value=True):
                suc = function.progMinorPlanetsFull()
                assert suc


def test_progMinorPlanetsFull_7(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Comet')
    function.ui.minorPlanetSource.setCurrentIndex(0)
    function.ui.filterMinorPlanet.setText('test')
    function.minorPlanets = [{'Principal_desig': 'test'}, {'Principal_desig': '0815'}]
    function.app.automation.installPath = None
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        with mock.patch.object(function.databaseProcessing,
                               'writeCometMPC',
                               return_value=True):
            with mock.patch.object(function.app.automation,
                                   'uploadMPCData',
                                   return_value=True):
                suc = function.progMinorPlanetsFull()
                assert not suc
