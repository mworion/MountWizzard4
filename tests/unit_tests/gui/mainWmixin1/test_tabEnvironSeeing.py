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
import shutil
import webbrowser
import platform

# external packages
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWmixin.tabEnvironSeeing import EnvironSeeing
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    shutil.copy('tests/testData/meteoblue.data',
                'tests/workDir/data/meteoblue.data')

    class Mixin(MWidget, EnvironSeeing):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = {}
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            EnvironSeeing.__init__(self)

    window = Mixin()
    yield window
    window.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_clearSeeingEntries(function):
    suc = function.clearSeeingEntries()
    assert suc


def test_enableSeeingEntries_1(function):
    function.seeingEnabled = False
    suc = function.enableSeeingEntries()
    assert not suc


def test_addSkyfieldTimeObject(function):
    data = {
        'hour': [10, 11],
        'date': ['2022-01-01', '2022-01-01']
    }

    suc = function.addSkyfieldTimeObject(data)
    assert suc
    assert 'time' in data


def test_updateSeeingEntries_1(function):
    function.app.seeingWeather.data = {
        'test': {
            'hour': [10, 11],
            'date': ['2022-01-01', '2022-01-01']
        }
    }
    suc = function.updateSeeingEntries()
    assert not suc


def test_updateSeeingEntries_2(function):
    function.app.seeingWeather.data = {
        'meta': {
            'last_model_update': '2022-01-01',
        },
        'hourly': {
            'hour': [10] * 96,
            'date': ['2022-01-01'] * 96,
            'high_clouds': [1] * 96,
            'mid_clouds': [1] * 96,
            'low_clouds': [1] * 96,
            'seeing_arcsec': [1] * 96,
            'seeing1': [1] * 96,
            'seeing1_color': ['#404040'] * 96,
            'seeing2': [1] * 96,
            'seeing2_color': ['#404040'] * 96,
            'temperature': [1] * 96,
            'relative_humidity': [1] * 96,
            'badlayer_top': ['1'] * 96,
            'badlayer_bottom': ['1'] * 96,
            'badlayer_gradient': ['1'] * 96,
            'jetstream': [1] * 96,
        }
    }
    t = function.app.mount.obsSite.ts.utc(2022, 1, 1, 10, 0, 0)
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=t):
        suc = function.updateSeeingEntries()
        assert suc


def test_updateSeeingEntries_3(function):
    function.app.seeingWeather.data = {
        'meta': {
            'last_model_update': '2022-01-01',
        },
        'hourly': {
            'hour': [10] * 96,
            'date': ['2022-01-01'] * 96,
            'high_clouds': [1] * 96,
            'mid_clouds': [1] * 96,
            'low_clouds': [1] * 96,
            'seeing_arcsec': [1] * 96,
            'seeing1': [1] * 96,
            'seeing1_color': ['#404040'] * 96,
            'seeing2': [1] * 96,
            'seeing2_color': ['#404040'] * 96,
            'temperature': [1] * 96,
            'relative_humidity': [1] * 96,
            'badlayer_top': ['1'] * 96,
            'badlayer_bottom': ['1'] * 96,
            'badlayer_gradient': ['1'] * 96,
            'jetstream': [1] * 96,
        }
    }
    t = function.app.mount.obsSite.ts.utc(2023, 1, 1, 10, 0, 0)
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=t):
        suc = function.updateSeeingEntries()
        assert suc


def test_prepareSeeingTable_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = function.prepareSeeingTable()
        assert suc


def test_prepareSeeingTable_2(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        suc = function.prepareSeeingTable()
        assert suc


def test_openMeteoblue_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openMeteoblue()
        assert suc


def test_openMeteoblue_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openMeteoblue()
        assert suc