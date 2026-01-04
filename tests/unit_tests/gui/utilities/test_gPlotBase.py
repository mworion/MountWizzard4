############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################

import numpy as np
import pyqtgraph as pg
import pytest
import unittest.mock as mock
from mw4.gui.utilities.gPlotBase import PlotBase
from PySide6.QtWidgets import QApplication


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_PlotBase():
    PlotBase()


def test_PlotBase_colorChange():
    p = PlotBase()
    p.addBarItem()
    p.colorChange()


def test_PlotBase_setupItems():
    p = PlotBase()
    p.setupItems()


def test_PlotBase_addBarItem_1():
    p = PlotBase()
    p.addBarItem()


def test_PlotBase_addBarItem_2():
    p = PlotBase()
    p.addBarItem(plotItem=p.p[0])


def test_toPolar():
    p = PlotBase()
    az = [0, 90, 180, 270]
    alt = [0, 0, 0, 0]
    x, y = p.toPolar(az, alt)
    assert len(x) == 4
    assert len(y) == 4
    assert round(x[0], 0) == 0
    assert round(x[1], 0) == 90
    assert round(x[2], 0) == 0
    assert round(x[3], 0) == -90
    assert round(y[0], 0) == 90
    assert round(y[1], 0) == 0
    assert round(y[2], 0) == -90
    assert round(y[3], 0) == 0


def test_findItemByName():
    p = PlotBase()
    item = pg.TextItem()
    item.nameStr = "test"
    p.p[0].addItem(item)
    assert item == p.findItemByName(p.p[0], "test")


def test_PlotBase_drawHorizon_0():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    with mock.patch.object(p, "show"):
        suc = p.drawHorizon([], plotItem=p.p[0])
        assert not suc


def test_PlotBase_drawHorizon_1():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    with mock.patch.object(p, "show"):
        suc = p.drawHorizon([])
        assert not suc


def test_PlotBase_drawHorizon_2():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    with mock.patch.object(p, "show"):
        suc = p.drawHorizon([(0, 0)])
        assert not suc


def test_PlotBase_drawHorizon_3():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    p.p[0].addItem(pg.PlotDataItem())
    with mock.patch.object(p, "show"):
        suc = p.drawHorizon([(0, 0), (1, 1)])
        assert suc


def test_PlotBase_drawHorizon_4():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    p.p[0].addItem(pg.PlotDataItem())
    with mock.patch.object(p, "show"):
        suc = p.drawHorizon([(0, 0), (1, 1)], polar=True)
        assert suc


def test_addIsoBasic_1():
    p = PlotBase()
    az = np.random.uniform(low=10, high=350, size=(50,))
    alt = np.random.uniform(low=15, high=85, size=(50,))
    err = np.random.uniform(low=5, high=15, size=(50,))
    with mock.patch.object(QApplication, "processEvents"):
        p.addIsoBasic(p.p[0], err, levels=1)


def test_addIsoItem_1():
    p = PlotBase()
    az = np.random.uniform(low=10, high=350, size=(50,))
    alt = np.random.uniform(low=15, high=85, size=(50,))
    err = np.random.uniform(low=5, high=15, size=(50,))
    with mock.patch.object(p, "addIsoBasic"):
        p.addIsoItem(az, alt, err)


def test_PlotBase_setGrid_0():
    p = PlotBase()
    p.setGrid(np.array([0, 1, 2]), plotItem=p.p[0])


def test_PlotBase_setGrid_1():
    p = PlotBase()
    p.setGrid(np.array([0, 1, 2]))


def test_PlotBase_setGrid_2():
    p = PlotBase()
    p.setGrid(np.array([0, 1, 2]), reverse=True)
