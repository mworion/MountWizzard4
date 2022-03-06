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
import pyqtgraph as pg

# local import
from gui.utilities.tools4pyqtgraph import PlotBase
from gui.utilities.tools4pyqtgraph import PolarScatter
from gui.utilities.tools4pyqtgraph import NormalScatter
from gui.utilities.tools4pyqtgraph import ImageBar
from gui.utilities.tools4pyqtgraph import Measure


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


def test_PlotBase():
    PlotBase()


def test_PlotBase_colorChange():
    p = PlotBase()
    p.colorChange()


def test_PlotBase_setupItems():
    p = PlotBase()
    p.setupItems()


def test_NormalScatter():
    function = NormalScatter()


def test_NormalScatter_plot1():
    p = NormalScatter()
    p.barItem = pg.ColorBarItem()
    suc = p.plot(np.array([0, 1, 2]), np.array([2, 3, 4]),
                 color='#000000', z=np.array([2, 3, 4]), bar=True)
    assert suc


def test_NormalScatter_plot2():
    p = NormalScatter()
    suc = p.plot(np.array([0, 1, 2]), np.array([2, 3, 4]),
                 color=['#000000', '#000000', '#000000'],
                 ang=np.array([2, 3, 4]))
    assert suc


def test_NormalScatter_plot3():
    p = PolarScatter()
    suc = p.plot(np.array([0, 1, 2]), np.array([2, 3, 4]),
                 z=np.array([2, 3, 4]),
                 ang=np.array([2, 3, 4]),
                 tip='{data}'.format)
    assert suc


def test_PolarScatter():
    p = PolarScatter()


def test_PolarScatter_setGrid_1():
    p = PolarScatter()
    suc = p.setGrid(np.array([0, 1, 2]))
    assert suc


def test_PolarScatter_setGrid_2():
    p = PolarScatter()
    suc = p.setGrid(np.array([0, 1, 2]), reverse=True)
    assert suc


def test_PolarScatter_plot1():
    p = PolarScatter()
    with mock.patch.object(p,
                           'setGrid'):
        suc = p.plot(np.array([0, 1, 2]), np.array([2, 3, 4]),
                     color='#000000', z=np.array([2, 3, 4]))
        assert not suc


def test_PolarScatter_plot2():
    p = PolarScatter()
    with mock.patch.object(p,
                           'setGrid'):
        suc = p.plot(np.array([0, 1, 2]), np.array([2, 3, 4]),
                     color=['#000000', '#000000', '#000000'],
                     ang=np.array([2, 3, 4]),
                     reverse=True)
        assert suc


def test_PolarScatter_plotLoc():
    p = PolarScatter()
    suc = p.plotLoc(47)
    assert suc


def test_ImageBar_constructPlot():
    function = ImageBar()
    function.constructPlot()


def test_ImageBar_setColorMap():
    function = ImageBar()
    suc = function.setColorMap('plasma')
    assert suc


def test_ImageBar_setImage():
    function = ImageBar()
    img = np.random.rand(100, 100)
    suc = function.setImage(img)
    assert suc


def test_ImageBar_showCrosshair():
    function = ImageBar()
    function.lx = QWidget()
    function.ly = QWidget()
    suc = function.showCrosshair(True)
    assert suc


def test_ImageBar_addEllipse():
    function = ImageBar()
    with mock.patch.object(function.p[0],
                           'addItem'):
        suc = function.addEllipse(0, 0, 1, 1, 0)
        assert suc


def test_ImageBar_addValueAnnotation():
    function = ImageBar()
    with mock.patch.object(function.p[0],
                           'addItem'):
        suc = function.addValueAnnotation(0, 0, 10)
        assert suc


def test_Measure():
    Measure()
