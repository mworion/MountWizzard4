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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import platform
import os

# external packages
from PyQt5.QtWidgets import QComboBox, QFileDialog, QWidget, QStyle, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject
from skyfield.api import Star, Angle
from mountcontrol.modelStar import ModelStar
from mountcontrol.model import Model

# local import
from gui.utilities.widget import MWidget
from gui.utilities.widget import FileSortProxyModel
from gui.utilities.widget import QMultiWait
from tests.baseTestSetupExtWindows import App


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = MWidget()
    yield window


def test_QMultiWait_1():
    class Test(QObject):
        a = pyqtSignal()
    w = QMultiWait()
    A = Test()
    w.addWaitableSignal(A.a)


def test_QMultiWait_2():
    w = QMultiWait()
    w.checkSignal()


def test_QMultiWait_3():
    w = QMultiWait()
    w.resetSignals()


def test_QMultiWait_4():
    w = QMultiWait()
    w.clear()


def test_FileSortProxyModel_1():
    w = QWidget()
    dialog = QFileDialog()
    dialog.setProxyModel(FileSortProxyModel(w))


def test_wIcon_1(function):
    suc = function.wIcon()
    assert not suc


def test_wIcon_2(function):
    icon = QStyle.SP_DialogApplyButton
    suc = function.wIcon(icon=icon)
    assert not suc


def test_wIcon_3(function):
    ui = QPushButton()
    suc = function.wIcon(gui=ui)
    assert not suc


def test_wIcon_4(function):
    icon = QStyle.SP_DialogApplyButton
    ui = QPushButton()
    suc = function.wIcon(gui=ui, icon=icon)
    assert suc


def test_getStyle_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        ret = function.getStyle()
        assert ret == function.MAC_STYLE + function.BASIC_STYLE


def test_getStyle_2(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        ret = function.getStyle()
        assert ret == function.NON_MAC_STYLE + function.BASIC_STYLE


def test_initUI_1(function):
    suc = function.initUI()
    assert suc


def test_changeStyleDynamic_1(function):
    suc = function.changeStyleDynamic()
    assert not suc


def test_changeStyleDynamic_2(function):
    ui = QPushButton()
    suc = function.changeStyleDynamic(ui)
    assert not suc


def test_changeStyleDynamic_3(function):
    ui = QPushButton()
    suc = function.changeStyleDynamic(ui, 'color')
    assert not suc


def test_changeStyleDynamic_4(function):
    ui = QPushButton()
    suc = function.changeStyleDynamic(ui, 'color', 'red')
    assert suc


def test_embedMatplot_1(function):
    ret = function.embedMatplot()
    assert ret is None


def test_embedMatplot_2(function):
    ui = QPushButton()
    ret = function.embedMatplot(ui)
    assert ret


def test_extractNames_0(function):
    name = ''
    name, short, ext = function.extractNames(name)
    assert name == ''
    assert short == ''
    assert ext == ''


def test_extractNames_1(function):
    name = 1
    name, short, ext = function.extractNames(name)
    assert name == ''
    assert short == ''
    assert ext == ''


def test_extractNames_2(function):
    name = ['test']
    name, short, ext = function.extractNames(name)
    assert name == os.path.abspath(os.getcwd() + '/test')
    assert short == 'test'
    assert ext == ''


def test_extractNames_3(function):
    name = ['c:/test']
    name, short, ext = function.extractNames(name)
    assert name == os.path.abspath('c:/test')
    assert short == 'test'
    assert ext == ''


def test_extractNames_4(function):
    name = ['c:/test.cfg']
    name, short, ext = function.extractNames(name)
    assert name == os.path.abspath('c:/test.cfg')
    assert short == 'test'
    assert ext == '.cfg'


def test_extractNames_5(function):
    name = ['c:/test.cfg', 'c:/test.cfg']
    name, short, ext = function.extractNames(name)
    assert name == [os.path.abspath('c:/test.cfg'),
                    os.path.abspath('c:/test.cfg')]
    assert short == ['test', 'test']
    assert ext == ['.cfg', '.cfg']


def test_extractNames_6(function):
    name = ['', 'c:/test.cfg']
    name, short, ext = function.extractNames(name)
    assert name == [os.path.abspath(''),
                    os.path.abspath('c:/test.cfg')]
    assert short == ['', 'test']
    assert ext == ['', '.cfg']


def test_prepareFileDialog_1(function):
    suc = function.prepareFileDialog()
    assert not suc


def test_prepareFileDialog_2(function):
    window = QWidget()
    suc = function.prepareFileDialog(window=window)
    assert suc


def test_prepareFileDialog_3(function):
    window = QWidget()
    suc = function.prepareFileDialog(window=window, enableDir=True)
    assert suc


def test_runDialog_1(function):
    dialog = QFileDialog()
    with mock.patch.object(QFileDialog,
                           'exec_',
                           return_value=0):
        val = function.runDialog(dialog)
        assert val == 0


def test_openFile_1(function):
    full, short, ext = function.openFile()
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openFile_2(function):
    window = QWidget()
    full, short, ext = function.openFile(window=window)
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openFile_3(function):
    window = QWidget()
    full, short, ext = function.openFile(window=window,
                                         title='title')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openFile_4(function):
    window = QWidget()
    full, short, ext = function.openFile(window=window,
                                         title='title',
                                         folder='.')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openFile_5(function):
    window = QWidget()
    with mock.patch.object(function,
                           'runDialog',
                           return_value=0):
        full, short, ext = function.openFile(window=window,
                                             title='title',
                                             folder='.',
                                             filterSet='*.*')
        assert full == ''
        assert short == ''
        assert ext == ''


def test_openFile_6(function):
    window = QWidget()
    with mock.patch.object(function,
                           'runDialog',
                           return_value=1):
        with mock.patch.object(QFileDialog,
                               'selectedFiles',
                               return_value=('test1', 'test2')):
            full, short, ext = function.openFile(window=window,
                                                 title='title',
                                                 folder='.',
                                                 filterSet='*.*',
                                                 multiple=True)
            assert full == ''
            assert short == ''
            assert ext == ''


def test_saveFile_1(function):
    full, short, ext = function.saveFile()
    assert full == ''
    assert short == ''
    assert ext == ''


def test_saveFile_2(function):
    window = QWidget()
    full, short, ext = function.saveFile(window=window)
    assert full == ''
    assert short == ''
    assert ext == ''


def test_saveFile_3(function):
    window = QWidget()
    full, short, ext = function.saveFile(window=window,
                                         title='title')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_saveFile_4(function):
    window = QWidget()
    full, short, ext = function.saveFile(window=window,
                                         title='title',
                                         folder='.')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_saveFile_5(function):
    window = QWidget()
    with mock.patch.object(function,
                           'runDialog',
                           return_value=0):
        full, short, ext = function.saveFile(window=window,
                                             title='title',
                                             folder='.',
                                             filterSet='*.*')
        assert full == ''
        assert short == ''
        assert ext == ''


def test_saveFile_6(function):
    window = QWidget()
    with mock.patch.object(function,
                           'runDialog',
                           return_value=1):
        with mock.patch.object(QFileDialog,
                               'selectedFiles',
                               return_value=(['tests/test.txt'])):
            full, short, ext = function.saveFile(window=window,
                                                 title='title',
                                                 folder='.',
                                                 filterSet='*.*')
        assert short == 'test'
        assert ext == '.txt'


def test_openDir_1(function):
    full, short, ext = function.openDir()
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openDir_2(function):
    window = QWidget()
    full, short, ext = function.openDir(window=window)
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openDir_3(function):
    window = QWidget()
    full, short, ext = function.openDir(window=window,
                                        title='title')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openDir_4(function):
    window = QWidget()
    with mock.patch.object(function,
                           'runDialog',
                           return_value=1):
        full, short, ext = function.openDir(window=window,
                                            title='title',
                                            folder='.')
        assert full == os.getcwd()


def test_openDir_5(function):
    window = QWidget()
    with mock.patch.object(function,
                           'runDialog',
                           return_value=None):
        full, short, ext = function.openDir(window=window,
                                            title='title',
                                            folder='.')
        assert full == ''
        assert short == ''
        assert ext == ''


def test_clickable_1(function):
    suc = function.clickable()
    assert not suc


def test_clickable_2(function):
    widget = QWidget()
    suc = function.clickable(widget=widget)
    assert suc


def test_guiSetText_1(function):
    suc = function.guiSetText(None, None)
    assert not suc


def test_guiSetText_2(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, None)
    assert not suc


def test_guiSetText_3(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, '3.5f')
    assert suc
    assert pb.text() == '-'


def test_guiSetText_4(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, '3.0f', 100)
    assert suc
    assert pb.text() == '100'


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


def test_returnDriver_1(function):
    sender = QWidget()
    searchDict = {}
    driver = function.returnDriver(sender, searchDict)
    assert driver == ''


def test_returnDriver_2(function):
    sender = QWidget()
    searchDict = {}
    driver = function.returnDriver(sender, searchDict, addKey='test')
    assert driver == ''


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
    event = None
    plane = None
    index = function.getIndexPointX(event=event,
                                    plane=plane,
                                    )
    assert not index


def test_getIndexPointX_2(function):
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = None
    index = function.getIndexPointX(event=event,
                                    plane=plane,
                                    )
    assert not index


def test_getIndexPointX_3(function):
    class Test:
        pass
    event = Test()
    event.xdata = 180
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    index = function.getIndexPointX(event=event,
                                    plane=plane,
                                    )
    assert index == 1


def test_getIndexPointX_4(function):
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 360)]
    index = function.getIndexPointX(event=event,
                                    plane=plane,
                                    )
    assert index == 1


def test_getIndexPointX_5(function):
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0), (45, 180), (45, 360)]
    index = function.getIndexPointX(event=event,
                                    plane=plane,
                                    )
    assert index == 2


def test_getIndexPointX_6(function):
    class Test:
        pass
    event = Test()
    event.xdata = 182
    event.ydata = 45
    plane = [(45, 0)]
    index = function.getIndexPointX(event=event,
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
