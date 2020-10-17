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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import shutil
import os

# external packages
import requests
from PyQt5.QtCore import QThreadPool


# local import
from tests.baseTestSetupMixins import App
from gui.utilities.widget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabMinorPlanetTime import MinorPlanetTime
import base.tpool


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, MinorPlanetTime):
        def __init__(self):
            super().__init__()
            self.app = App()
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
    with mock.patch.object(function,
                           'generateName',
                           return_value=''):
        suc = function.setupMinorPlanetNameList()
        assert suc


def test_setupMinorPlanetNameList_2(function):
    with mock.patch.object(function,
                           'generateName',
                           return_value=['test', 'test1']):
        suc = function.setupMinorPlanetNameList()
        assert suc


def test_setProgress(function):
    suc = function.setProgress(0)
    assert suc
    assert function.ui.downloadMinorPlanetProgress.value() == 0


def test_downloadFile_1(function):
    class Get:
        @staticmethod
        def get(a, b):
            return 100

    class Test:
        headers = Get()

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = function.downloadFile('', '')
        assert not suc


def test_downloadFile_2(function):
    class Get:
        @staticmethod
        def get(a, b):
            return 100

    class Test:
        headers = Get()

        @staticmethod
        def iter_content(a):
            yield b'1234567890'

    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = function.downloadFile('', 'tests/temp/test.txt')
        assert suc


def test_unzipFile(function):
    shutil.copy('tests/testData/test.json.gz', 'tests/temp/test.json.gz')
    suc = function.unzipFile('tests/temp/test.json.gz')
    assert suc
    assert os.path.isfile('tests/temp/test.json')


def test_loadDataFromSourceURLsWorker_1(function):
    suc = function.loadDataFromSourceURLsWorker()
    assert not suc


def test_loadDataFromSourceURLsWorker_2(function):
    with mock.patch.object(function,
                           'downloadFile'):
        with mock.patch.object(function,
                               'unzipFile'):
            suc = function.loadDataFromSourceURLsWorker('Asteroids Daily', True)
            assert not suc


def test_loadDataFromSourceURLsWorker_3(function):
    shutil.copy('tests/testData/test.json', 'tests/data/test.json')
    function.minorPlanetSourceURLs['test'] = 'test.json.gz'
    with mock.patch.object(function,
                           'downloadFile'):
        with mock.patch.object(function,
                               'unzipFile'):
            suc = function.loadDataFromSourceURLsWorker('test', True)
            assert suc


def test_loadDataFromSourceURLs_1(function):
    function.ui.minorPlanetSource.clear()
    suc = function.loadDataFromSourceURLs()
    assert not suc


def test_loadDataFromSourceURLs_2(function):
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('Please select')
    suc = function.loadDataFromSourceURLs()
    assert not suc


def test_loadDataFromSourceURLs_3(function):
    function.minorPlanetSourceURLs['test'] = 'test.json.gz'
    function.ui.minorPlanetSource.clear()
    function.ui.minorPlanetSource.addItem('test')

    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.loadDataFromSourceURLs()
        assert suc
