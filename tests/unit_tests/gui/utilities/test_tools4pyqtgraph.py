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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

# external packages
import pyqtgraph as pg
import numpy as np

# local import
from gui.utilities.tools4pyqtgraph import PlotImageBar
from tests.unit_tests.unitTestAddOns.baseTestSetupExtWindows import App


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = PlotImageBar()
    yield window


def test_setColorMap(function):
    suc = function.setColorMap('plasma')
    assert suc


def test_setImage(function):
    img = np.random.rand(100, 100)
    suc = function.setImage(img)
    assert suc


def test_showCrosshair(function):
    suc = function.showCrosshair(True)
    assert suc


def test_addEllipse(function):
    with mock.patch.object(function.plotItem,
                           'addItem'):
        suc = function.addEllipse(0, 0, 1, 1, 0)
        assert suc


def test_addValueAnnotation(function):
    with mock.patch.object(function.plotItem,
                           'addItem'):
        suc = function.addValueAnnotation(0, 0, 10)
        assert suc
