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
from PyQt5.QtWidgets import QWidget
import numpy as np

# local import
from gui.utilities.tools4pyqtgraph import Plot
from gui.utilities.tools4pyqtgraph import PolarScatter
from gui.utilities.tools4pyqtgraph import NormalScatter
from gui.utilities.tools4pyqtgraph import PlotImageBar


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


def test_Plot():
    Plot()


def test_PolarScatter():
    function = PolarScatter()


def test_PolarScatter_plot():
    function = PolarScatter()
    function.plot(np.array([0, 1]), np.array([1, 2]))


def test_NormalScatter():
    function = NormalScatter()


def test_NormalScatter_plot():
    function = NormalScatter()
    function.plot(np.array([0]), np.array([1]), np.array([2]))


def test_PlotImageBar_constructPlot():
    function = PlotImageBar()
    function.constructPlot()


def test_PlotImageBar_setColorMap():
    function = PlotImageBar()
    suc = function.setColorMap('plasma')
    assert suc


def test_PlotImageBar_setImage():
    function = PlotImageBar()
    img = np.random.rand(100, 100)
    suc = function.setImage(img)
    assert suc


def test_PlotImageBar_showCrosshair():
    function = PlotImageBar()
    function.lx = QWidget()
    function.ly = QWidget()
    suc = function.showCrosshair(True)
    assert suc


def test_PlotImageBar_addEllipse():
    function = PlotImageBar()
    with mock.patch.object(function.plotItem,
                           'addItem'):
        suc = function.addEllipse(0, 0, 1, 1, 0)
        assert suc


def test_PlotImageBar_addValueAnnotation():
    function = PlotImageBar()
    with mock.patch.object(function.plotItem,
                           'addItem'):
        suc = function.addValueAnnotation(0, 0, 10)
        assert suc
