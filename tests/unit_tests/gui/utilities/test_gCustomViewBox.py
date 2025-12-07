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

import builtins
import unittest.mock as mock


import pyqtgraph as pg
import pytest
from PySide6.QtCore import QEvent, QPointF, Qt


from mw4.gui.utilities.gCustomViewBox import CustomViewBox
from mw4.gui.utilities.gNormalScatter import NormalScatter


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_CustomViewBox_0():
    CustomViewBox()


def test_CustomViewBox_1():
    vb = CustomViewBox()
    vb.setPlotDataItem("test")
    assert vb.plotDataItem == "test"


def test_CustomViewBox_2():
    vb = CustomViewBox()
    vb.setOpts(enableLimitX=True)
    assert vb.enableLimitX


def test_CustomViewBox_3():
    pdi = pg.PlotDataItem()
    vb = CustomViewBox()
    vb.plotDataItem = pdi
    vb.updateData([0, 1, 2], [0, 1, 2])


def test_CustomViewBox_4():
    vb = CustomViewBox()
    event = QEvent(QEvent.Type.MouseButtonDblClick)
    vb.callbackMDC(event, pg.Point(1, 1))


def test_CustomViewBox_5():
    vb = CustomViewBox()
    val = vb.distance([1, 1], [2, 1])
    assert val == 1


def test_CustomViewBox_6():
    vb = CustomViewBox()
    val = vb.isBetween([1, 1], [3, 1], [2, 1])
    assert val == 0


def test_CustomViewBox_7():
    vb = CustomViewBox()
    val = vb.isBetween([1, 1], [3, 1], [2, 3])
    assert val > 2


def test_CustomViewBox_8():
    class Pos:
        @staticmethod
        def x():
            return 1

        @staticmethod
        def y():
            return 1

    vb = CustomViewBox()
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.plotDataItem = pdi
    val = vb.getCurveIndex(Pos())
    assert val == 1


def test_CustomViewBox_9():
    class Pos:
        @staticmethod
        def x():
            return 5

        @staticmethod
        def y():
            return 5

    vb = CustomViewBox()
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.plotDataItem = pdi
    val = vb.getCurveIndex(Pos())
    assert val is None


def test_CustomViewBox_10():
    class Pos:
        @staticmethod
        def x():
            return 2

        @staticmethod
        def y():
            return 2

    vb = CustomViewBox()
    pdi = pg.PlotDataItem(x=[], y=[])
    vb.plotDataItem = pdi
    val = vb.getNearestPointIndex(Pos())
    assert val == 0


def test_CustomViewBox_11():
    class Pos:
        @staticmethod
        def x():
            return 1000

        @staticmethod
        def y():
            return 1000

    vb = CustomViewBox()
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.plotDataItem = pdi
    val = vb.getNearestPointIndex(Pos())
    assert val is None


def test_CustomViewBox_12():
    class Pos:
        @staticmethod
        def x():
            return 3

        @staticmethod
        def y():
            return 3

    vb = CustomViewBox()
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.plotDataItem = pdi
    val = vb.getNearestPointIndex(Pos())
    assert val == 3


def test_CustomViewBox_13():
    class Pos:
        @staticmethod
        def x():
            return 1

        @staticmethod
        def y():
            return 1

    vb = CustomViewBox()
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.plotDataItem = pdi
    with mock.patch.object(vb, "updateData"):
        vb.addUpdate(0, Pos())


def test_CustomViewBox_14():
    class Pos:
        @staticmethod
        def x():
            return 1

        @staticmethod
        def y():
            return 1

    vb = CustomViewBox()
    pdi = pg.PlotDataItem()
    vb.plotDataItem = pdi
    with mock.patch.object(vb, "updateData"):
        vb.addUpdate(0, Pos())


def test_CustomViewBox_15():
    vb = CustomViewBox()
    pdi = pg.PlotDataItem()
    vb.plotDataItem = pdi
    with mock.patch.object(vb, "updateData"):
        suc = vb.delUpdate(0)
        assert not suc


def test_CustomViewBox_16():
    vb = CustomViewBox()
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.plotDataItem = pdi
    with mock.patch.object(vb, "updateData"):
        suc = vb.delUpdate(0)
        assert suc


def test_CustomViewBox_checkLimits_1():
    class Pos:
        @staticmethod
        def x():
            return -2

        @staticmethod
        def y():
            return -2

    vb = CustomViewBox()
    vb.enableLimitX = False
    vb.state["limits"]["xLimits"] = [-1, 1]
    vb.state["limits"]["yLimits"] = [-1, 1]
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    data = pdi.getData()
    vb.plotDataItem = pdi
    x, y = vb.checkLimits(data, 1, Pos())
    assert x[1] == -1
    assert y[1] == -1


def test_CustomViewBox_checkLimits_2():
    class Pos:
        @staticmethod
        def x():
            return 2

        @staticmethod
        def y():
            return 2

    vb = CustomViewBox()
    vb.enableLimitX = False
    vb.state["limits"]["xLimits"] = [-1, 1]
    vb.state["limits"]["yLimits"] = [-1, 1]
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    data = pdi.getData()
    vb.plotDataItem = pdi
    x, y = vb.checkLimits(data, 1, Pos())
    assert x[1] == 1
    assert y[1] == 1


def test_CustomViewBox_checkLimits_3():
    class Pos:
        @staticmethod
        def x():
            return -2

        @staticmethod
        def y():
            return -2

    vb = CustomViewBox()
    vb.enableLimitX = True
    vb.state["limits"]["xLimits"] = [-10, 10]
    vb.state["limits"]["yLimits"] = [-10, 10]
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    data = pdi.getData()
    vb.plotDataItem = pdi
    x, y = vb.checkLimits(data, 1, Pos())
    assert x[1] == 0


def test_CustomViewBox_checkLimits_4():
    class Pos:
        @staticmethod
        def x():
            return 3

        @staticmethod
        def y():
            return 3

    vb = CustomViewBox()
    vb.enableLimitX = True
    vb.state["limits"]["xLimits"] = [-10, 10]
    vb.state["limits"]["yLimits"] = [-10, 10]
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    data = pdi.getData()
    vb.plotDataItem = pdi
    x, y = vb.checkLimits(data, 1, Pos())
    assert x[1] == 2


def test_CustomViewBox_checkLimits_5():
    class Pos:
        @staticmethod
        def x():
            return -2

        @staticmethod
        def y():
            return -2

    vb = CustomViewBox()
    vb.enableLimitX = True
    vb.state["limits"]["xLimits"] = [-10, 10]
    vb.state["limits"]["yLimits"] = [-10, 10]
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    data = pdi.getData()
    vb.plotDataItem = pdi
    x, y = vb.checkLimits(data, 0, Pos())
    assert x[0] == -2


def test_CustomViewBox_checkLimits_6():
    class Pos:
        @staticmethod
        def x():
            return 3

        @staticmethod
        def y():
            return 3

    vb = CustomViewBox()
    vb.enableLimitX = True
    vb.state["limits"]["xLimits"] = [-10, 10]
    vb.state["limits"]["yLimits"] = [-10, 10]
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    data = pdi.getData()
    vb.plotDataItem = pdi
    x, y = vb.checkLimits(data, 2, Pos())
    assert x[2] == 3


def test_posInViewRange_1():
    plot = NormalScatter()
    plot.plot([-1, 1], [-1, 1])
    vb = plot.p[0].getViewBox()
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0.5, 0.5)):
        val = vb.posInViewRange(pg.Point(1, 1))
        assert val


def test_posInViewRange_2():
    plot = NormalScatter()
    plot.plot([-1, 1], [-1, 1])
    vb = plot.p[0].getViewBox()
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(5, 5)):
        val = vb.posInViewRange(pg.Point(1, 1))
        assert not val


def test_CustomViewBox_rightMouseRange_2():
    vb = CustomViewBox()
    vb.state["limits"]["xLimits"] = [-10, 10]
    vb.state["limits"]["yLimits"] = [-10, 10]

    with mock.patch.object(vb, "setYRange"):
        with mock.patch.object(vb, "setXRange"):
            vb.rightMouseRange()


def test_CustomViewBox_mouseDragEvent_1():
    event = "test"
    vb = CustomViewBox()
    with mock.patch.object(builtins, "super"):
        vb.mouseDragEvent(event)


def test_CustomViewBox_mouseDragEvent_2():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.NoButton

        @staticmethod
        def ignore():
            return 1

    event = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.mouseDragEvent(event)


def test_CustomViewBox_mouseDragEvent_3():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def ignore():
            return 1

        @staticmethod
        def isStart():
            return True

        @staticmethod
        def buttonDownScenePos():
            return (0, 0)

    event = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem()
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        vb.mouseDragEvent(event)


def test_CustomViewBox_mouseDragEvent_4():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def isStart():
            return True

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

        @staticmethod
        def buttonDownScenePos():
            return (0, 0)

    event = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2], symbol="o")
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        with mock.patch.object(
            vb.plotDataItem.scatter,
            "pointsAt",
            return_value=vb.plotDataItem.scatter.points(),
        ):
            vb.mouseDragEvent(event)


def test_CustomViewBox_mouseDragEvent_5():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def isStart():
            return False

        @staticmethod
        def isFinish():
            return True

    event = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem()
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        vb.mouseDragEvent(event)


def test_CustomViewBox_mouseDragEvent_6():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def ignore():
            return 1

        @staticmethod
        def isStart():
            return False

        @staticmethod
        def isFinish():
            return False

    ev = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        vb.mouseDragEvent(ev)


def test_CustomViewBox_mouseClickEvent_1():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.RightButton

        @staticmethod
        def accept():
            return 1

    vb = CustomViewBox()
    vb.plotDataItem = None
    vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_2():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def accept():
            return 1

    vb = CustomViewBox()
    vb.plotDataItem = None
    with mock.patch.object(builtins, "super"):
        vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_3():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.RightButton

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem()
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        with mock.patch.object(
            vb.plotDataItem.scatter,
            "pointsAt",
            return_value=vb.plotDataItem.scatter.points(),
        ):
            with mock.patch.object(vb, "rightMouseRange"):
                vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_4():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.RightButton

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol="o")
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        with mock.patch.object(
            vb.plotDataItem.scatter,
            "pointsAt",
            return_value=vb.plotDataItem.scatter.points(),
        ):
            with mock.patch.object(vb, "delUpdate"):
                vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_5():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol="o")
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        with mock.patch.object(vb, "getCurveIndex", return_value=0):
            with mock.patch.object(vb, "addUpdate"):
                vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_6():
    class EV:
        @staticmethod
        def button():
            return Qt.MouseButton.LeftButton

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol="o")
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        with mock.patch.object(vb, "getCurveIndex", return_value=None):
            with mock.patch.object(vb, "getNearestPointIndex", return_value=0):
                with mock.patch.object(vb, "addUpdate"):
                    vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_7():
    class EV:
        @staticmethod
        def button():
            return 0

        @staticmethod
        def ignore():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol="o")
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        with mock.patch.object(vb.plotDataItem.scatter, "pointsAt", return_value=False):
            vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseDoubleClickEvent_1():
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol="o")
    vb.mouseDoubleClickEvent(1)


def test_CustomViewBox_mouseDoubleClickEvent_2():
    class EV:
        @staticmethod
        def scenePos():
            return 1

    vb = CustomViewBox()
    vb.plotDataItem = None
    with mock.patch.object(vb, "mapSceneToView", return_value=QPointF(0, 0)):
        with mock.patch.object(vb, "callbackMDC"):
            vb.mouseDoubleClickEvent(EV())
