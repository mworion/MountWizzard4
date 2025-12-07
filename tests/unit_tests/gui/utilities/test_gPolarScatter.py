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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import unittest.mock as mock


import numpy as np
import pytest


from mw4.gui.utilities.gPolarScatter import PolarScatter


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_PolarScatter():
    PolarScatter()


def test_PolarScatter_plot1():
    p = PolarScatter()
    with mock.patch.object(p, "setGrid"):
        suc = p.plot(
            np.array([0, 1, 2]),
            np.array([2, 3, 4]),
            color="#000000",
            z=np.array([2, 3, 4]),
        )
        assert not suc


def test_PolarScatter_plot2():
    p = PolarScatter()
    with mock.patch.object(p, "setGrid"):
        suc = p.plot(
            np.array([0, 1, 2]),
            np.array([2, 3, 4]),
            color=["#000000", "#000000", "#000000"],
            ang=np.array([2, 3, 4]),
            reverse=True,
        )
        assert suc


def test_PolarScatter_plot3():
    p = PolarScatter()
    with mock.patch.object(p, "setGrid"):
        suc = p.plot(
            np.array([0, 1, 2]),
            np.array([2, 3, 4]),
            color=["#000000", "#000000", "#000000"],
            ang=np.array([2, 3, 4]),
            reverse=True,
            z=np.array([0, 1, 2]),
        )
        assert suc


def test_PolarScatter_plotLoc():
    p = PolarScatter()
    p.plotLoc(47)
