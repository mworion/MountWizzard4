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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import sys
import platform
import os

# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore

# local import
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = MWidget()
    yield
    del app


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


def test_clearPolar_1():
    fig, axes = app.clearPolar()
    assert fig is None
    assert axes is None


def test_clearPolar_2():
    widget = 'test'

    fig, axes = app.clearPolar(widget)
    assert fig is None
    assert axes is None


def test_clearPolar_3():
    ui = PyQt5.QtWidgets.QPushButton()
    widget = app.embedMatplot(ui)

    fig, axes = app.clearPolar(widget)
    assert fig
    assert axes


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
    assert name == 'test'
    assert short == 'test'
    assert ext == ''


def test_extractNames_3():
    name = ['c:/test']
    name, short, ext = app.extractNames(name)
    assert name == 'c:/test'
    assert short == 'test'
    assert ext == ''


def test_extractNames_4():
    name = ['c:/test.cfg']
    name, short, ext = app.extractNames(name)
    assert name == 'c:/test.cfg'
    assert short == 'test'
    assert ext == '.cfg'


def test_extractNames_5():
    name = ['c:/test.cfg', 'c:/test.cfg']
    name, short, ext = app.extractNames(name)
    assert name == ['c:/test.cfg', 'c:/test.cfg']
    assert short == ['test', 'test']
    assert ext == ['.cfg', '.cfg']


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
        assert full == os.getcwd()
        assert short == 'MountWizzard4'
        assert ext == ''


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
                           return_value=0):
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
