############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock

# external packages
import numpy as np
import pyqtgraph as pg
import pytest

# local import
from mw4.gui.utilities.gNormalScatter import NormalScatter


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_NormalScatter():
    NormalScatter()


def test_NormalScatter_plot1():
    p = NormalScatter()
    p.barItem = pg.ColorBarItem()
    suc = p.plot(
        np.array([0, 1, 2]),
        np.array([2, 3, 4]),
        color="#000000",
        z=np.array([2, 3, 4]),
        bar=True,
    )
    assert suc


def test_NormalScatter_plot2():
    p = NormalScatter()
    suc = p.plot(
        np.array([0, 1, 2]),
        np.array([2, 3, 4]),
        color=["#000000", "#000000", "#000000"],
        ang=np.array([2, 3, 4]),
    )
    assert suc


def test_NormalScatter_plot3():
    p = NormalScatter()
    suc = p.plot(
        np.array([0, 1, 2]),
        np.array([2, 3, 4]),
        z=np.array([2, 3, 4]),
        ang=np.array([2, 3, 4]),
        tip="{data}".format,
    )
    assert suc


def test_NormalScatter_plot4():
    p = NormalScatter()
    with mock.patch.object(p, "addIsoItemHorizon"):
        suc = p.plot(
            np.array([0, 1, 2]),
            np.array([2, 3, 4]),
            z=np.array([2, 3, 4]),
            ang=np.array([2, 3, 4]),
            tip="{data}".format,
            limits=True,
            range={"xMin": 0, "xMax": 1, "yMin": 0, "yMax": 1},
            isoLevels=1,
        )
        assert suc
