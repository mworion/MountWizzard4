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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest


# external packages
from PyQt5.QtWidgets import QComboBox, QWidget, QPushButton
from skyfield.api import Star, Angle
from mountcontrol.modelStar import ModelStar
from mountcontrol.model import Model

# local import
from gui.utilities.toolsQtWidget import MWidget
from tests.unit_tests.unitTestAddOns.baseTestSetupExtWindows import App


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = MWidget()
    yield window


def test_embedMatplot_1(function):
    ret = function.embedMatplot()
    assert ret is None


def test_embedMatplot_2(function):
    ui = QPushButton()
    ret = function.embedMatplot(ui)
    assert ret


def test_findIndexValue_0(function):
    ui = QComboBox()
    ui.addItem('')
    val = function.findIndexValue(ui=ui,
                                  searchString='dome')
    assert val == 0


def test_findIndexValue_1(function):
    ui = QComboBox()
    ui.addItem('dome')
    ui.addItem('test')
    val = function.findIndexValue(ui=ui,
                                  searchString='dome')
    assert val == 0


def test_findIndexValue_2(function):
    ui = QComboBox()
    ui.addItem('dome')
    ui.addItem('indi')
    val = function.findIndexValue(ui=ui,
                                  searchString='indi')
    assert val == 1


def test_findIndexValue_3(function):
    ui = QComboBox()
    ui.addItem('dome')
    ui.addItem('test')
    ui.addItem('indi - test')
    val = function.findIndexValue(ui=ui,
                                  searchString='indi')
    assert val == 2


def test_findIndexValue_4(function):
    ui = QComboBox()
    ui.addItem('dome')
    ui.addItem('test')
    ui.addItem('indi - test')
    val = function.findIndexValue(ui=ui,
                                  searchString='indi',
                                  relaxed=True)
    assert val == 2


def test_findIndexValue_5(function):
    ui = QComboBox()
    val = function.findIndexValue(ui=ui,
                                  searchString='indi')
    assert val == 0


def test_generatePolar_1(function):
    axe, fig = function.generatePolar()
    assert axe is None
    assert fig is None


def test_generatePolar_2(function):
    ui = QWidget()
    axe, fig = function.generatePolar(widget=ui)
    assert axe is None
    assert fig is None


def test_generatePolar_3(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generatePolar(widget=widget)
    assert axe
    assert fig


def test_generatePolar_4(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generatePolar(widget=widget, title='test')
    assert axe
    assert fig


def test_generatePolar_5(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generatePolar(widget=widget, horizon=True)
    assert axe
    assert fig


def test_generatePolar_6(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generatePolar(widget=widget, showAxes=False)
    assert axe
    assert fig


def test_generatePolar_7(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generatePolar(widget=widget, showAxes=False,
                                      reverse=True)
    assert axe
    assert fig


def test_generateFlat_1(function):
    axe, fig = function.generateFlat()
    assert axe is None
    assert fig is None


def test_generateFlat_2(function):
    ui = QWidget()
    axe, fig = function.generateFlat(widget=ui)
    assert axe is None
    assert fig is None


def test_generateFlat_3(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generateFlat(widget=widget)
    assert axe
    assert fig


def test_generateFlat_4(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generateFlat(widget=widget, title='test')
    assert axe
    assert fig


def test_generateFlat_5(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generateFlat(widget=widget, title='test', showAxes=False)
    assert axe
    assert fig


def test_generateFlat_6(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    function.generateFlat(widget=widget, title='test')
    axe, fig = function.generateFlat(widget=widget, title='test')
    assert axe
    assert fig


def test_generateFlat_7(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generateFlat(widget=widget, title='test', horizon=True)
    assert axe
    assert fig


def test_generateColorbar_1(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generatePolar(widget=widget, title='test')
    scatter = axe.scatter([0, 1], [0, 1])
    suc = function.generateColorbar(figure=fig, scatter=scatter, label='test')
    assert suc


def test_generateColorbar_2(function):
    ui = QWidget()
    widget = function.embedMatplot(ui)
    axe, fig = function.generatePolar(widget=widget, title='test')
    scatter = axe.scatter([0, 1], [0, 1])
    function.generateColorbar(figure=fig, scatter=scatter, label='test')
    suc = function.generateColorbar(figure=fig, scatter=scatter, label='test')
    assert not suc


def test_getIndexPoint_0(function):
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = []
    epsilon = 0
    index = function.getIndexPoint(event=event,
                                   plane=plane,
                                   epsilon=epsilon,
                                   )
    assert not index


def test_getIndexPoint_1(function):
    event = None
    plane = None
    epsilon = 0
    index = function.getIndexPoint(event=event,
                                   plane=plane,
                                   epsilon=epsilon,
                                   )
    assert not index


def test_getIndexPoint_2(function):
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = None
    epsilon = 0
    index = function.getIndexPoint(event=event,
                                   plane=plane,
                                   epsilon=epsilon,
                                   )
    assert not index


def test_getIndexPoint_3(function):
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 0
    index = function.getIndexPoint(event=event,
                                   plane=plane,
                                   epsilon=epsilon,
                                   )
    assert not index


def test_getIndexPoint_4(function):
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 200
    index = function.getIndexPoint(event=event,
                                   plane=plane,
                                   epsilon=epsilon,
                                   )
    assert index == 0


def test_getIndexPoint_5(function):
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    epsilon = 200
    index = function.getIndexPoint(event=event,
                                   plane=plane,
                                   epsilon=epsilon,
                                   )
    assert index == 1


def test_getIndexPointX_1(function):
    x = None
    plane = None
    index = function.getIndexPointX(x=x,
                                    plane=plane,
                                    )
    assert not index


def test_getIndexPointX_2(function):
    plane = None
    index = function.getIndexPointX(x=182,
                                    plane=plane,
                                    )
    assert not index


def test_getIndexPointX_3(function):
    plane = [(45, 0), (45, 360)]
    index = function.getIndexPointX(x=180,
                                    plane=plane,
                                    )
    assert index == 1


def test_getIndexPointX_4(function):
    plane = [(45, 0), (45, 360)]
    index = function.getIndexPointX(x=182,
                                    plane=plane,
                                    )
    assert index == 1


def test_getIndexPointX_5(function):
    plane = [(45, 0), (45, 180), (45, 360)]
    index = function.getIndexPointX(x=182,
                                    plane=plane,
                                    )
    assert index == 2


def test_getIndexPointX_6(function):
    plane = [(45, 0)]
    index = function.getIndexPointX(x=182,
                                    plane=plane,
                                    )
    assert index == 1


def test_writeRetrofitData_1(function):
    val = function.writeRetrofitData({}, {})
    assert val == {}


def test_writeRetrofitData_2(function):
    model = Model()
    stars = list()
    a = ModelStar()
    a.obsSite = App().mount.obsSite
    a.coord = Star(ra_hours=0, dec_degrees=0)
    a.errorAngle = Angle(degrees=0)
    a.errorRMS = 1
    a.number = 1
    stars.append(a)
    model._starList = stars
    model.terms = 22
    model.errorRMS = 10
    model.orthoError = 10
    model.polarError = 10

    val = function.writeRetrofitData(model, [{}])
    assert val
