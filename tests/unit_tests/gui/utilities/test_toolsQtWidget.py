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
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QWidget, QStyle, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.toolsQtWidget import FileSortProxyModel
from gui.utilities.toolsQtWidget import QMultiWait


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


def test_messageDialog_1(function):
    widget = QWidget()
    with mock.patch.object(QMessageBox,
                           'question',
                           return_value=QMessageBox.No):
        with mock.patch.object(QMessageBox,
                               'show'):
            with mock.patch.object(function,
                                   'runDialog'):
                suc = function.messageDialog(widget, 'test', 'test')
                assert not suc


def test_messageDialog_2(function):
    widget = QWidget()
    with mock.patch.object(QMessageBox,
                           'question',
                           return_value=QMessageBox.Yes):
        with mock.patch.object(QMessageBox,
                               'show'):
            with mock.patch.object(function,
                                   'runDialog'):
                suc = function.messageDialog(widget, 'test', 'test')
                assert not suc


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
