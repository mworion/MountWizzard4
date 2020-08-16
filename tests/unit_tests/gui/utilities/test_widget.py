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
import PyQt5.QtWidgets
from PyQt5.QtWidgets import QComboBox
import PyQt5.QtTest
import PyQt5.QtCore

# local import
from gui.utilities.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app
    app = MWidget()
    qtbot.add_widget(app)

    yield


def test_wIcon_1():
    suc = app.wIcon()
    assert not suc


def test_wIcon_2():
    icon = PyQt5.QtWidgets.QStyle.SP_DialogApplyButton
    suc = app.wIcon(icon=icon)
    assert not suc


def test_wIcon_3():
    ui = PyQt5.QtWidgets.QPushButton()
    suc = app.wIcon(gui=ui)
    assert not suc


def test_wIcon_4():
    icon = PyQt5.QtWidgets.QStyle.SP_DialogApplyButton
    ui = PyQt5.QtWidgets.QPushButton()
    suc = app.wIcon(gui=ui, icon=icon)
    assert suc


def test_getStyle_1():
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        ret = app.getStyle()
        assert ret == app.MAC_STYLE + app.BASIC_STYLE


def test_getStyle_2():
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        ret = app.getStyle()
        assert ret == app.NON_MAC_STYLE + app.BASIC_STYLE


def test_initUI_1():
    suc = app.initUI()
    assert suc


def test_changeStyleDynamic_1():
    suc = app.changeStyleDynamic()
    assert not suc


def test_changeStyleDynamic_2():
    ui = PyQt5.QtWidgets.QPushButton()
    suc = app.changeStyleDynamic(ui)
    assert not suc


def test_changeStyleDynamic_3():
    ui = PyQt5.QtWidgets.QPushButton()
    suc = app.changeStyleDynamic(ui, 'color')
    assert not suc


def test_changeStyleDynamic_4():
    ui = PyQt5.QtWidgets.QPushButton()
    suc = app.changeStyleDynamic(ui, 'color', 'red')
    assert suc


def test_embedMatplot_1():
    ret = app.embedMatplot()
    assert ret is None


def test_embedMatplot_2():
    ui = PyQt5.QtWidgets.QPushButton()
    ret = app.embedMatplot(ui)
    assert ret


def test_extractNames_0():
    name = ''
    name, short, ext = app.extractNames(name)
    assert name == ''
    assert short == ''
    assert ext == ''


def test_extractNames_1():
    name = 1
    name, short, ext = app.extractNames(name)
    assert name == ''
    assert short == ''
    assert ext == ''


def test_extractNames_2():
    name = ['test']
    name, short, ext = app.extractNames(name)
    assert name == os.path.abspath(os.getcwd() +'/test')
    assert short == 'test'
    assert ext == ''


def test_extractNames_3():
    name = ['c:/test']
    name, short, ext = app.extractNames(name)
    assert name == os.path.abspath('c:/test')
    assert short == 'test'
    assert ext == ''


def test_extractNames_4():
    name = ['c:/test.cfg']
    name, short, ext = app.extractNames(name)
    assert name == os.path.abspath('c:/test.cfg')
    assert short == 'test'
    assert ext == '.cfg'


def test_extractNames_5():
    name = ['c:/test.cfg', 'c:/test.cfg']
    name, short, ext = app.extractNames(name)
    assert name == [os.path.abspath('c:/test.cfg'),
                    os.path.abspath('c:/test.cfg')]
    assert short == ['test', 'test']
    assert ext == ['.cfg', '.cfg']


def test_extractNames_6():
    name = ['', 'c:/test.cfg']
    name, short, ext = app.extractNames(name)
    assert name == [os.path.abspath(''),
                    os.path.abspath('c:/test.cfg')]
    assert short == ['', 'test']
    assert ext == ['', '.cfg']


def test_prepareFileDialog_1():
    suc = app.prepareFileDialog()
    assert not suc


def test_prepareFileDialog_2():
    window = PyQt5.QtWidgets.QWidget()
    suc = app.prepareFileDialog(window=window)
    assert suc


def test_prepareFileDialog_3():
    window = PyQt5.QtWidgets.QWidget()
    suc = app.prepareFileDialog(window=window, enableDir=True)
    assert suc


def test_runDialog_1():
    dialog = PyQt5.QtWidgets.QFileDialog()
    with mock.patch.object(app,
                           'runDialog',
                           return_value=0):
        app.runDialog(dialog)


def test_openFile_1():
    full, short, ext = app.openFile()
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openFile_2():
    window = PyQt5.QtWidgets.QWidget()
    full, short, ext = app.openFile(window=window)
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openFile_3():
    window = PyQt5.QtWidgets.QWidget()
    full, short, ext = app.openFile(window=window,
                                    title='title')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openFile_4():
    window = PyQt5.QtWidgets.QWidget()
    full, short, ext = app.openFile(window=window,
                                    title='title',
                                    folder='.')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openFile_5():
    window = PyQt5.QtWidgets.QWidget()
    with mock.patch.object(app,
                           'runDialog',
                           return_value=0):
        full, short, ext = app.openFile(window=window,
                                        title='title',
                                        folder='.',
                                        filterSet='*.*')
        assert full == ''
        assert short == ''
        assert ext == ''


def test_openFile_6():
    window = PyQt5.QtWidgets.QWidget()
    with mock.patch.object(app,
                           'runDialog',
                           return_value=1):
        with mock.patch.object(PyQt5.QtWidgets.QFileDialog,
                               'selectedFiles',
                               return_value=('test1', 'test2')):
            full, short, ext = app.openFile(window=window,
                                            title='title',
                                            folder='.',
                                            filterSet='*.*',
                                            multiple=True)
            assert full == ''
            assert short == ''
            assert ext == ''


def test_saveFile_1():
    full, short, ext = app.saveFile()
    assert full == ''
    assert short == ''
    assert ext == ''


def test_saveFile_2():
    window = PyQt5.QtWidgets.QWidget()
    full, short, ext = app.saveFile(window=window)
    assert full == ''
    assert short == ''
    assert ext == ''


def test_saveFile_3():
    window = PyQt5.QtWidgets.QWidget()
    full, short, ext = app.saveFile(window=window,
                                    title='title')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_saveFile_4():
    window = PyQt5.QtWidgets.QWidget()
    full, short, ext = app.saveFile(window=window,
                                    title='title',
                                    folder='.')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_saveFile_5():
    window = PyQt5.QtWidgets.QWidget()
    with mock.patch.object(app,
                           'runDialog',
                           return_value=0):
        full, short, ext = app.saveFile(window=window,
                                        title='title',
                                        folder='.',
                                        filterSet='*.*')
        assert full == ''
        assert short == ''
        assert ext == ''


def test_saveFile_6():
    window = PyQt5.QtWidgets.QWidget()
    with mock.patch.object(app,
                           'runDialog',
                           return_value=1):
        with mock.patch.object(PyQt5.QtWidgets.QFileDialog,
                               'selectedFiles',
                               return_value=(['mw4/test/test.txt'])):
            full, short, ext = app.saveFile(window=window,
                                            title='title',
                                            folder='.',
                                            filterSet='*.*')
        assert short == 'test'
        assert ext == '.txt'


def test_openDir_1():
    full, short, ext = app.openDir()
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openDir_2():
    window = PyQt5.QtWidgets.QWidget()
    full, short, ext = app.openDir(window=window)
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openDir_3():
    window = PyQt5.QtWidgets.QWidget()
    full, short, ext = app.openDir(window=window,
                                   title='title')
    assert full == ''
    assert short == ''
    assert ext == ''


def test_openDir_4():
    window = PyQt5.QtWidgets.QWidget()
    with mock.patch.object(app,
                           'runDialog',
                           return_value=1):
        full, short, ext = app.openDir(window=window,
                                       title='title',
                                       folder='.')
        assert full == os.getcwd()
        assert short == 'MountWizzard4'
        assert ext == ''


def test_clickable_1():
    suc = app.clickable()
    assert not suc


def test_clickable_2():
    widget = PyQt5.QtWidgets.QPushButton()
    suc = app.clickable(widget=widget)
    assert suc


def test_guiSetText_1():
    suc = app.guiSetText(None, None)
    assert not suc


def test_guiSetText_2():
    pb = PyQt5.QtWidgets.QPushButton()
    suc = app.guiSetText(pb, None)
    assert not suc


def test_guiSetText_3():
    pb = PyQt5.QtWidgets.QPushButton()
    suc = app.guiSetText(pb, '3.5f')
    assert suc
    assert pb.text() == '-'


def test_guiSetText_4():
    pb = PyQt5.QtWidgets.QPushButton()
    suc = app.guiSetText(pb, '3.0f', 100)
    assert suc
    assert pb.text() == '100'


def test_findIndexValue_1():
    ui = QComboBox()
    ui.addItem('dome')
    ui.addItem('test')
    val = app.findIndexValue(ui=ui,
                             searchString='dome')
    assert val == 0


def test_findIndexValue_2():
    ui = QComboBox()
    ui.addItem('dome')
    ui.addItem('indi')
    val = app.findIndexValue(ui=ui,
                             searchString='indi')
    assert val == 1


def test_findIndexValue_3():
    ui = QComboBox()
    ui.addItem('dome')
    ui.addItem('test')
    ui.addItem('indi - test')
    val = app.findIndexValue(ui=ui,
                             searchString='indi')
    assert val == 2


def test_generatePolar_1():
    axe, fig = app.generatePolar()
    assert axe is None
    assert fig is None


def test_generatePolar_2():
    ui = PyQt5.QtWidgets.QWidget()
    axe, fig = app.generatePolar(widget=ui)
    assert axe is None
    assert fig is None


def test_generatePolar_3():
    ui = PyQt5.QtWidgets.QWidget()
    widget = app.embedMatplot(ui)
    axe, fig = app.generatePolar(widget=widget)
    assert axe
    assert fig


def test_generatePolar_4():
    ui = PyQt5.QtWidgets.QWidget()
    widget = app.embedMatplot(ui)
    axe, fig = app.generatePolar(widget=widget, title='test')
    assert axe
    assert fig


def test_generateFlat_1():
    axe, fig = app.generateFlat()
    assert axe is None
    assert fig is None


def test_generateFlat_2():
    ui = PyQt5.QtWidgets.QWidget()
    axe, fig = app.generateFlat(widget=ui)
    assert axe is None
    assert fig is None


def test_generateFlat_3():
    ui = PyQt5.QtWidgets.QWidget()
    widget = app.embedMatplot(ui)
    axe, fig = app.generateFlat(widget=widget)
    assert axe
    assert fig


def test_generateFlat_4():
    ui = PyQt5.QtWidgets.QWidget()
    widget = app.embedMatplot(ui)
    axe, fig = app.generateFlat(widget=widget, title='test')
    assert axe
    assert fig