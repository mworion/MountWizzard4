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
import unittest.mock as mock
import pytest

# external packages
from PyQt5.QtCore import QEvent

# local import
from tests.baseTestSetup import App
from gui.utilities.widget import MWidget
from gui.extWindows.hemisphereW import HemisphereWindow


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    window = HemisphereWindow(app=App())
    yield window


@pytest.fixture(autouse=True, scope='function')
def function(qtbot, module):
    window = module
    yield window


def test_initConfig_1(module):
    suc = module.initConfig()
    assert suc


def test_initConfig_3(module):
    module.app.config['hemisphereW']['winPosX'] = 10000
    module.app.config['hemisphereW']['winPosY'] = 10000
    suc = module.initConfig()
    assert suc


def test_storeConfig_1(module):
    module.storeConfig()


def test_resizeEvent_1(module):
    module.startup = False
    with mock.patch.object(MWidget,
                           'resizeEvent'):
        module.resizeEvent(QEvent)


def test_resizeEvent_2(module):
    module.startup = True
    with mock.patch.object(MWidget,
                           'resizeEvent'):
        module.resizeEvent(QEvent)


def test_resizeTimer_1(module):
    module.resizeTimerValue = 3
    with mock.patch.object(module,
                           'drawHemisphere'):
        suc = module.resizeTimer()
        assert suc


def test_resizeTimer_2(module):
    module.resizeTimerValue = 1
    with mock.patch.object(module,
                           'drawHemisphere'):
        suc = module.resizeTimer()
        assert suc
