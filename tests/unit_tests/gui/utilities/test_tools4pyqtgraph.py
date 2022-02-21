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
from gui.utilities.tools4pyqtgraph import PlotNormalScatter
from gui.utilities.tools4pyqtgraph import PlotPolarScatterBar
from gui.utilities.tools4pyqtgraph import PlotNormalScatterPier
from gui.utilities.tools4pyqtgraph import PlotNormalScatterPierPoints
from gui.utilities.tools4pyqtgraph import PlotImageBar


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


def test_Plot():
    Plot()


def test_PlotNormalScatterPierPoints_constructPlot():
    function = PlotNormalScatterPierPoints()
    function.constructPlot()


def test_PlotNormalScatterPierPoints_plot():
    function = PlotNormalScatterPierPoints()
    function.plot(np.array([0]), np.array([1]), np.array(['E']))


def test_PlotPolarScatterBar_constructPlot():
    function = PlotPolarScatterBar()
    function.constructPlot()


def test_PlotPolarScatterBar_plot():
    function = PlotPolarScatterBar()
    function.plot(np.array([0]), np.array([1]), np.array([2]))


def test_PlotNormalScatterPier_constructPlot_1():
    function = PlotNormalScatterPier()
    function.constructPlot(True)


def test_PlotNormalScatterPier_constructPlot_2():
    function = PlotNormalScatterPier()
    function.constructPlot(False)


def test_PlotNormalScatterPier_plot():
    function = PlotNormalScatterPier()
    function.plot(np.array([0]), np.array([1]), np.array([2]), True)


def test_PlotPolarScatterBar_plot():
    function = PlotPolarScatterBar()
    function.plot(np.array([1]), np.array([1]), np.array([2]))


def test_PlotNormalScatter_constructPlot():
    function = PlotNormalScatter()
    function.constructPlot()


def test_PlotNormalScatter_plot():
    function = PlotNormalScatter()
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
