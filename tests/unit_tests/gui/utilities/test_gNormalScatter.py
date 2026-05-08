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
# License APL2.0
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


def test_setupRangeLimits_with_limits():
    p = NormalScatter()
    with mock.patch.object(p.p[0], "setLimits") as mockLimits:
        with mock.patch.object(p.p[0], "setXRange") as mockX:
            with mock.patch.object(p.p[0], "setYRange") as mockY:
                p.setupRangeLimits(
                    np.array([0, 1]),
                    np.array([0, 1]),
                    {"limits": True},
                )
                assert mockLimits.called
                assert mockX.called
                assert mockY.called


def test_setupRangeLimits_no_limits():
    p = NormalScatter()
    with mock.patch.object(p.p[0], "setLimits") as mockLimits:
        p.setupRangeLimits(
            np.array([0, 1]),
            np.array([0, 1]),
            {"limits": False},
        )
        assert not mockLimits.called


def test_setupRangeLimits_custom_range():
    p = NormalScatter()
    p.setupRangeLimits(
        np.array([0, 1]),
        np.array([0, 1]),
        {"range": {"xMin": 0, "xMax": 2, "yMin": 0, "yMax": 2}},
    )
    assert p.defRange == {"xMin": 0, "xMax": 2, "yMin": 0, "yMax": 2}


def test_computeZColorMap():
    p = NormalScatter()
    z = np.array([1.0, 2.0, 3.0])
    colorInx, minE, maxE = p.computeZColorMap(z)
    assert minE == 1.0
    assert maxE == 3.0
    assert colorInx[0] == 0.0
    assert colorInx[2] == 1.0


def test_computeZColorMap_flat():
    p = NormalScatter()
    z = np.array([2.0, 2.0, 2.0])
    colorInx, minE, maxE = p.computeZColorMap(z)
    assert minE == maxE == 2.0
    # divisor falls back to 0.1, all values map to 0
    assert all(colorInx == 0.0)


def test_setupColorData_string_color():
    p = NormalScatter()
    x = np.array([0, 1, 2])
    minE, maxE = p.setupColorData(x, {"color": "#ff0000"})
    assert len(p.col) == 3
    assert minE == 0.0
    assert maxE == 0.0


def test_setupColorData_list_color():
    p = NormalScatter()
    x = np.array([0, 1, 2])
    cols = ["#ff0000", "#00ff00", "#0000ff"]
    p.setupColorData(x, {"color": cols})
    assert p.col == cols


def test_setupColorData_with_z():
    p = NormalScatter()
    x = np.array([0, 1, 2])
    z = np.array([1.0, 2.0, 3.0])
    minE, maxE = p.setupColorData(x, {"z": z})
    assert minE == 1.0
    assert maxE == 3.0
    assert p.colorInx is not None


def test_setupBarItem_active():
    p = NormalScatter()
    p.barItem = pg.ColorBarItem()
    with mock.patch.object(p.barItem, "setVisible") as mockVis:
        with mock.patch.object(p.barItem, "setLevels") as mockLev:
            with mock.patch.object(p.barItem, "setColorMap") as mockCM:
                p.setupBarItem({"bar": True, "z": np.array([1])}, 0.0, 1.0)
                assert mockVis.called
                assert mockLev.called
                assert mockCM.called


def test_setupBarItem_no_bar():
    p = NormalScatter()
    p.barItem = pg.ColorBarItem()
    with mock.patch.object(p.barItem, "setVisible") as mockVis:
        p.setupBarItem({"bar": False, "z": np.array([1])}, 0.0, 1.0)
        assert not mockVis.called


def test_setupBarItem_no_z():
    p = NormalScatter()
    p.barItem = pg.ColorBarItem()
    with mock.patch.object(p.barItem, "setVisible") as mockVis:
        p.setupBarItem({"bar": True}, 0.0, 1.0)
        assert not mockVis.called


def test_buildSpots_no_z():
    p = NormalScatter()
    x = np.array([0.0, 1.0])
    y = np.array([2.0, 3.0])
    p.col = ["#ff0000", "#00ff00"]
    spots = p.buildSpots(x, y, {})
    assert len(spots) == 2
    assert spots[0]["pos"] == (0.0, 2.0)


def test_buildSpots_with_z():
    p = NormalScatter()
    x = np.array([0.0, 1.0])
    y = np.array([2.0, 3.0])
    z = np.array([1.0, 2.0])
    p.colorInx, _, _ = p.computeZColorMap(z)
    spots = p.buildSpots(x, y, {"z": z})
    assert len(spots) == 2


def test_addScatterPoints_no_tip():
    p = NormalScatter()
    p.plot(np.array([0, 1]), np.array([0, 1]))
    with mock.patch.object(p.scatterItem, "addPoints") as mockAdd:
        p.addScatterPoints([{"pos": (0, 0)}], {})
        mockAdd.assert_called_once_with([{"pos": (0, 0)}])


def test_addScatterPoints_with_tip():
    p = NormalScatter()
    p.plot(np.array([0, 1]), np.array([0, 1]))
    tip = "{data}".format
    with mock.patch.object(p.scatterItem, "addPoints") as mockAdd:
        p.addScatterPoints([{"pos": (0, 0)}], {"tip": tip})
        mockAdd.assert_called_once_with([{"pos": (0, 0)}], tip=tip)


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
