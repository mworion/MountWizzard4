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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock
import builtins

# external packages
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import QPointF
import numpy as np
import pyqtgraph as pg

# local import
from mw4.gui.utilities.tools4pyqtgraph import PlotBase
from mw4.gui.utilities.tools4pyqtgraph import PolarScatter
from mw4.gui.utilities.tools4pyqtgraph import NormalScatter
from mw4.gui.utilities.tools4pyqtgraph import ImageBar
from mw4.gui.utilities.tools4pyqtgraph import Measure
from mw4.gui.utilities.tools4pyqtgraph import TimeMeasure
from mw4.gui.utilities.tools4pyqtgraph import CustomViewBox
from mw4.gui.utilities.tools4pyqtgraph import Hemisphere


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


def test_CustomViewBox_0():
    CustomViewBox()


def test_CustomViewBox_1():
    vb = CustomViewBox()
    vb.setPlotDataItem('test')
    assert vb.plotDataItem == 'test'


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
    suc = vb.callbackMDC(1, 2)
    assert suc


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
    with mock.patch.object(vb,
                           'updateData'):
        suc = vb.addUpdate(0, Pos())
        assert suc


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
    with mock.patch.object(vb,
                           'updateData'):
        suc = vb.addUpdate(0, Pos())
        assert suc


def test_CustomViewBox_15():
    vb = CustomViewBox()
    pdi = pg.PlotDataItem()
    vb.plotDataItem = pdi
    with mock.patch.object(vb,
                           'updateData'):
        suc = vb.delUpdate(0)
        assert not suc


def test_CustomViewBox_16():
    vb = CustomViewBox()
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.plotDataItem = pdi
    with mock.patch.object(vb,
                           'updateData'):
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
    vb.state['limits']['xLimits'] = [-1, 1]
    vb.state['limits']['yLimits'] = [-1, 1]
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
    vb.state['limits']['xLimits'] = [-1, 1]
    vb.state['limits']['yLimits'] = [-1, 1]
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
    vb.state['limits']['xLimits'] = [-10, 10]
    vb.state['limits']['yLimits'] = [-10, 10]
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
    vb.state['limits']['xLimits'] = [-10, 10]
    vb.state['limits']['yLimits'] = [-10, 10]
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
    vb.state['limits']['xLimits'] = [-10, 10]
    vb.state['limits']['yLimits'] = [-10, 10]
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
    vb.state['limits']['xLimits'] = [-10, 10]
    vb.state['limits']['yLimits'] = [-10, 10]
    pdi = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    data = pdi.getData()
    vb.plotDataItem = pdi
    x, y = vb.checkLimits(data, 2, Pos())
    assert x[2] == 3


def test_CustomViewBox_rightMouseRange_1():
    vb = CustomViewBox()
    vb.state['limits']['xLimits'] = [None, 10]
    vb.state['limits']['yLimits'] = [None, 10]

    with mock.patch.object(vb,
                           'enableAutoRange'):
        suc = vb.rightMouseRange()
        assert suc


def test_CustomViewBox_rightMouseRange_2():
    vb = CustomViewBox()
    vb.state['limits']['xLimits'] = [-10, 10]
    vb.state['limits']['yLimits'] = [-10, 10]

    with mock.patch.object(vb,
                           'setYRange'):
        with mock.patch.object(vb,
                               'setXRange'):
            suc = vb.rightMouseRange()
            assert suc


def test_CustomViewBox_mouseDragEvent_1():
    ev = 'test'
    vb = CustomViewBox()
    with mock.patch.object(builtins,
                           'super'):
        vb.mouseDragEvent(ev)


def test_CustomViewBox_mouseDragEvent_2():
    class EV:
        @staticmethod
        def button():
            return 0

        @staticmethod
        def ignore():
            return 1

    ev = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2])
    vb.mouseDragEvent(ev)


def test_CustomViewBox_mouseDragEvent_3():
    class EV:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def ignore():
            return 1

        @staticmethod
        def isStart():
            return True

        @staticmethod
        def buttonDownScenePos():
            return (0, 0)

    ev = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem()
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        vb.mouseDragEvent(ev)


def test_CustomViewBox_mouseDragEvent_4():
    class EV:
        @staticmethod
        def button():
            return 1

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

    ev = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 1, 2], y=[0, 1, 2], symbol='o')
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        with mock.patch.object(vb.plotDataItem.scatter,
                               'pointsAt',
                               return_value=vb.plotDataItem.scatter.points()):
            vb.mouseDragEvent(ev)


def test_CustomViewBox_mouseDragEvent_5():
    class EV:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def isStart():
            return False

        @staticmethod
        def isFinish():
            return True

    ev = EV()
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem()
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        vb.mouseDragEvent(ev)


def test_CustomViewBox_mouseDragEvent_6():
    class EV:
        @staticmethod
        def button():
            return 1

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
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        vb.mouseDragEvent(ev)


def test_CustomViewBox_mouseClickEvent_1():
    class EV:
        @staticmethod
        def button():
            return 2

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
            return 1

        @staticmethod
        def accept():
            return 1

    vb = CustomViewBox()
    vb.plotDataItem = None
    with mock.patch.object(builtins,
                           'super'):
        vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_3():
    class EV:
        @staticmethod
        def button():
            return 2

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem()
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        with mock.patch.object(vb.plotDataItem.scatter,
                               'pointsAt',
                               return_value=vb.plotDataItem.scatter.points()):
            with mock.patch.object(vb,
                                   'rightMouseRange'):
                vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_4():
    class EV:
        @staticmethod
        def button():
            return 2

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol='o')
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        with mock.patch.object(vb.plotDataItem.scatter,
                               'pointsAt',
                               return_value=vb.plotDataItem.scatter.points()):
            with mock.patch.object(vb,
                                   'delUpdate'):
                vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_5():
    class EV:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol='o')
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        with mock.patch.object(vb,
                               'getCurveIndex',
                               return_value=0):
            with mock.patch.object(vb,
                                   'addUpdate'):
                vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseClickEvent_6():
    class EV:
        @staticmethod
        def button():
            return 1

        @staticmethod
        def accept():
            return 1

        @staticmethod
        def scenePos():
            return QPointF(0, 0)

    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol='o')
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        with mock.patch.object(vb,
                               'getCurveIndex',
                               return_value=None):
            with mock.patch.object(vb,
                                   'getNearestPointIndex',
                                   return_value=0):
                with mock.patch.object(vb,
                                       'addUpdate'):
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
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol='o')
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        with mock.patch.object(vb.plotDataItem.scatter,
                               'pointsAt',
                               return_value=False):
            vb.mouseClickEvent(EV())


def test_CustomViewBox_mouseDoubleClickEvent_1():
    vb = CustomViewBox()
    vb.plotDataItem = pg.PlotDataItem(x=[0, 0, 0], y=[0, 0, 0], symbol='o')
    vb.mouseDoubleClickEvent(1)


def test_CustomViewBox_mouseDoubleClickEvent_2():
    class EV:
        @staticmethod
        def scenePos():
            return 1

    vb = CustomViewBox()
    vb.plotDataItem = None
    with mock.patch.object(vb,
                           'mapSceneToView',
                           return_value=QPointF(0, 0)):
        with mock.patch.object(vb,
                               'callbackMDC'):
            vb.mouseDoubleClickEvent(EV())


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
    item.nameStr = 'test'
    p.p[0].addItem(item)
    assert item == p.findItemByName(p.p[0], 'test')


def test_PlotBase_drawHorizon_0():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    with mock.patch.object(p,
                           'show'):
        suc = p.drawHorizon([], plotItem=p.p[0])
        assert not suc


def test_PlotBase_drawHorizon_1():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    with mock.patch.object(p,
                           'show'):
        suc = p.drawHorizon([])
        assert not suc


def test_PlotBase_drawHorizon_2():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    with mock.patch.object(p,
                           'show'):
        suc = p.drawHorizon([(0, 0)])
        assert not suc


def test_PlotBase_drawHorizon_3():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    p.p[0].addItem(pg.PlotDataItem())
    with mock.patch.object(p,
                           'show'):
        suc = p.drawHorizon([(0, 0), (1, 1)])
        assert suc


def test_PlotBase_drawHorizon_4():
    p = PlotBase()
    p.horizon = pg.PlotDataItem()
    p.p.append(p.horizon)
    p.p[0].addItem(pg.PlotDataItem())
    with mock.patch.object(p,
                           'show'):
        suc = p.drawHorizon([(0, 0), (1, 1)], polar=True)
        assert suc


def test_addIsoBasic_1():
    p = PlotBase()
    az = np.random.uniform(low=10, high=350, size=(50,))
    alt = np.random.uniform(low=15, high=85, size=(50,))
    err = np.random.uniform(low=5, high=15, size=(50,))
    with mock.patch.object(QApplication,
                           'processEvents'):
        suc = p.addIsoBasic(p.p[0], err, levels=1)
        assert suc


def test_addIsoItem_1():
    p = PlotBase()
    az = np.random.uniform(low=10, high=350, size=(50,))
    alt = np.random.uniform(low=15, high=85, size=(50,))
    err = np.random.uniform(low=5, high=15, size=(50,))
    suc = p.addIsoItem(az, alt, err)
    assert suc


def test_PlotBase_setGrid_0():
    p = PlotBase()
    suc = p.setGrid(np.array([0, 1, 2]), plotItem=p.p[0])
    assert suc


def test_PlotBase_setGrid_1():
    p = PlotBase()
    suc = p.setGrid(np.array([0, 1, 2]))
    assert suc


def test_PlotBase_setGrid_2():
    p = PlotBase()
    suc = p.setGrid(np.array([0, 1, 2]), reverse=True)
    assert suc


def test_NormalScatter():
    NormalScatter()


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
    p = NormalScatter()
    suc = p.plot(np.array([0, 1, 2]), np.array([2, 3, 4]),
                 z=np.array([2, 3, 4]),
                 ang=np.array([2, 3, 4]),
                 tip='{data}'.format)
    assert suc


def test_NormalScatter_plot4():
    p = NormalScatter()
    suc = p.plot(np.array([0, 1, 2]), np.array([2, 3, 4]),
                 z=np.array([2, 3, 4]),
                 ang=np.array([2, 3, 4]),
                 tip='{data}'.format,
                 limits=True, range={'xMin': 0, 'xMax': 1, 'yMin': 0, 'yMax': 1},
                 isoLevels=1)
    assert suc


def test_PolarScatter():
    p = PolarScatter()


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


def test_PolarScatter_plot3():
    p = PolarScatter()
    with mock.patch.object(p,
                           'setGrid'):
        suc = p.plot(np.array([0, 1, 2]), np.array([2, 3, 4]),
                     color=['#000000', '#000000', '#000000'],
                     ang=np.array([2, 3, 4]),
                     reverse=True, z=np.array([0, 1, 2]))
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


def test_ImageBar_setImage_1():
    function = ImageBar()
    suc = function.setImage(None)
    assert not suc


def test_ImageBar_setImage_2():
    function = ImageBar()
    img = np.random.rand(100, 100)
    suc = function.setImage(img)
    assert suc


def test_ImageBar_setImage_3():
    function = ImageBar()
    img = np.random.rand(100, 100)
    suc = function.setImage(img, False)
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

        
def test_TimeMeasure():
    TimeMeasure(orientation='left')

        
def test_TimeMeasure_tickStrings():
    values = [-1, 0, 1]
    TimeMeasure(orientation='left').tickStrings(values, 0, 0)


def test_Measure():
    Measure()


def test_Hemisphere():
    Hemisphere()
