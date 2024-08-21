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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import astropy
import unittest.mock as mock

# external packages
from PySide6.QtGui import QCloseEvent

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.videoW2 import VideoWindow2


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    func = VideoWindow2(app=App())
    with mock.patch.object(func,
                           'show'):
        yield func


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    if 'videoW2' in function.app.config:
        del function.app.config['videoW2']

    suc = function.storeConfig()
    assert suc


def test_storeConfig_2(function):
    function.app.config['videoW2'] = {}

    suc = function.storeConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'stopVideo'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.showWindow()
            function.closeEvent(QCloseEvent)
