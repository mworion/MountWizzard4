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
from mw4.gui.utilities.gNormalScatter import NormalScatter


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_NormalScatter():
    NormalScatter()


def test_NormalScatter_plot1():
    p = NormalScatter()
    p.barItem = pg.ColorBarItem()
    p.plot(
        np.array([0, 1, 2]),
        np.array([2, 3, 4]),
        color="#000000",
        z=np.array([2, 3, 4]),
        bar=True,
    )


def test_NormalScatter_plot2():
    p = NormalScatter()
    p.plot(
        np.array([0, 1, 2]),
        np.array([2, 3, 4]),
        color=["#000000", "#000000", "#000000"],
        ang=np.array([2, 3, 4]),
    )


def test_NormalScatter_plot3():
    p = NormalScatter()
    p.plot(
        np.array([0, 1, 2]),
        np.array([2, 3, 4]),
        z=np.array([2, 3, 4]),
        ang=np.array([2, 3, 4]),
        tip="{data}".format,
    )


def test_NormalScatter_plot4():
    p = NormalScatter()
    with mock.patch.object(p, "addIsoItemHorizon"):
        p.plot(
            np.array([0, 1, 2]),
            np.array([2, 3, 4]),
            z=np.array([2, 3, 4]),
            ang=np.array([2, 3, 4]),
            tip="{data}".format,
            limits=True,
            range={"xMin": 0, "xMax": 1, "yMin": 0, "yMax": 1},
            isoLevels=1,
        )
