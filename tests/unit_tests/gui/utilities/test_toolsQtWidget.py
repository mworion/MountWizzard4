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
import unittest.mock as mock
import pytest
import os
import platform

# external packages
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QWidget, QTabWidget
from PyQt5.QtWidgets import QPushButton, QComboBox, QTableWidgetItem, QLineEdit
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QPainterPath
from PyQt5.QtTest import QTest
from skyfield.api import Angle, load
import numpy as np

# local import
from gui.utilities.toolsQtWidget import MWidget, sleepAndEvents
from gui.utilities.toolsQtWidget import FileSortProxyModel
from gui.utilities.toolsQtWidget import QMultiWait, QCustomTableWidgetItem
from gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    window = MWidget()
    window.app = App()
    window.ui = Ui_MainWindow()
    window.ui.setupUi(window)
    yield window


def test_FileSortProxyModel_1():
    f = FileSortProxyModel()
    f.sort()


def test_QMultiWait_1():
    class Test(QObject):
        a = pyqtSignal()
    w = QMultiWait()
    A = Test()
    w.addWaitableSignal(A.a)


def test_QMultiWait_2():
    class Test(QObject):
        a = pyqtSignal()
    w = QMultiWait()
    A = Test()
    w.addWaitableSignal(A.a)
    w.checkSignal()


def test_QMultiWait_3():
    w = QMultiWait()
    w.resetSignals()


def test_QMultiWait_4():
    class Test(QObject):
        a = pyqtSignal()
    w = QMultiWait()
    A = Test()
    w.addWaitableSignal(A.a)
    w.clear()


def test_QCustomTableWidgetItem_1():
    i1 = QCustomTableWidgetItem('')
    i2 = QCustomTableWidgetItem('')
    assert not (i1 < i2)


def test_QCustomTableWidgetItem_2():
    i1 = QCustomTableWidgetItem('-2.0')
    i2 = QCustomTableWidgetItem('')
    assert i1 < i2


def test_QCustomTableWidgetItem_3():
    i1 = QCustomTableWidgetItem('-2.0')
    i2 = QCustomTableWidgetItem('5')
    assert i1 < i2


def test_QCustomTableWidgetItem_4():
    i1 = QCustomTableWidgetItem('-2.0')
    i2 = QTableWidgetItem('5')
    assert i1 < i2


def test_FileSortProxyModel_1():
    w = QWidget()
    dialog = QFileDialog()
    dialog.setProxyModel(FileSortProxyModel(w))


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


def test_saveWindowAsPNG(function):
    class Save:
        @staticmethod
        def save(a):
            return

    with mock.patch.object(QWidget,
                           'grab',
                           return_value=Save()):
        suc = function.saveWindowAsPNG(QWidget())
        assert suc


def test_saveAllWindowsAsPNG_1(function):
    function.app.uiWindows = {'test1': {'classObj': None},
                              'test2': {'classObj': 1}}
    function.app.mainW = QWidget()
    with mock.patch.object(function,
                           'saveWindowAsPNG'):
        suc = function.saveAllWindowsAsPNG()
        assert suc


def test_keyPressEvent_1(function):
    class Key:
        @staticmethod
        def key():
            return 16777268

    with mock.patch.object(function,
                           'saveWindowAsPNG'):
        function.keyPressEvent(Key())


def test_keyPressEvent_2(function):
    class Key:
        @staticmethod
        def key():
            return 16777269

    with mock.patch.object(function,
                           'saveAllWindowsAsPNG'):
        function.keyPressEvent(Key())


def test_keyPressEvent_3(function):
    class Key:
        @staticmethod
        def key():
            return 1

    with mock.patch.object(QWidget,
                           'keyPressEvent'):
        function.keyPressEvent(Key())


def test_img2pixmap_1(function):
    img = function.img2pixmap(os.getcwd() + '/tests/testData/altitude.png')
    assert isinstance(img, QPixmap)


def test_img2pixmap_2(function):
    img = function.img2pixmap(os.getcwd() + '/tests/testData/altitude.png', '#202020', '#303030')
    assert isinstance(img, QPixmap)


def test_svg2pixmap(function):
    img = function.svg2pixmap(os.getcwd() + '/tests/testData/choose.svg')
    assert isinstance(img, QPixmap)


def test_svg2icon_1(function):
    val = function.svg2icon(os.getcwd() + '/tests/testData/choose.svg')
    assert isinstance(val, QIcon)


def test_wIcon_1(function):
    suc = function.wIcon()
    assert not suc


def test_wIcon_2(function):
    ui = QPushButton()
    suc = function.wIcon(gui=ui)
    assert not suc


def test_wIcon_3(function):
    ui = QPushButton()
    suc = function.wIcon(gui=ui, name='load')
    assert suc


def test_renderStyle_1(function):
    inp = '12345$M_BLUE$12345'
    function.colorSet = 0
    val = function.renderStyle(inp).strip(' ')
    assert val == '12345#2090C012345\n'


def test_renderStyle_2(function):
    inp = '12345$M_TEST$12345'
    function.colorSet = 0
    val = function.renderStyle(inp).strip(' ')
    assert val == '12345$M_TEST$12345\n'


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
    suc = function.changeStyleDynamic(ui, 'color', '')
    assert suc


def test_changeStyleDynamic_5(function):
    ui = QPushButton()
    ui.setProperty('color', 'red')
    suc = function.changeStyleDynamic(ui, 'color', 'red')
    assert suc


def test_changeStyleDynamic_6(function):
    ui = QPushButton()
    suc = function.changeStyleDynamic(ui, 'running', True)
    assert suc
    suc = function.changeStyleDynamic(ui, 'running', False)
    assert suc


def test_changeStyleDynamic_7(function):
    ui = QPushButton()
    suc = function.changeStyleDynamic(ui, 'running', True)
    suc = function.changeStyleDynamic(ui, 'running', False)
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
    suc = function.prepareFileDialog(window=window, enableDir=True, reverseOrder=True)
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
                                   'runDialog',
                                   return_value=QMessageBox.No):
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
                                   'runDialog',
                                   return_value=QMessageBox.Yes):
                suc = function.messageDialog(widget, 'test', 'test')
                assert suc


def test_messageDialog_3(function):
    widget = QWidget()
    with mock.patch.object(QMessageBox,
                           'question',
                           return_value=QMessageBox.Yes):
        with mock.patch.object(QMessageBox,
                               'show'):
            with mock.patch.object(function,
                                   'runDialog',
                                   return_value=QMessageBox.Yes):
                suc = function.messageDialog(widget, 'test', 'test', ['A', 'B'])
                assert suc


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
    function.clickable()


def test_clickable_2(function):
    widget = QLineEdit()
    function.clickable(widget=widget)


def test_clickable_3(function):
    widget = QLineEdit()
    function.clickable(widget=widget)
    QTest.mouseRelease(widget, Qt.LeftButton)


def test_clickable_4(function):
    widget = QLineEdit()
    function.clickable(widget=widget)
    QTest.mouseRelease(widget, Qt.LeftButton, pos=QPoint(0, 0))


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


def test_guiSetText_3b(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, '3.5f', [])
    assert suc


def test_guiSetText_3c(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, '3.5f', np.array([]))
    assert suc


def test_guiSetText_4(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, '3.0f', 100)
    assert suc
    assert pb.text() == '100'


def test_guiSetText_5(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 'HSTR', Angle(hours=10))
    assert suc
    assert pb.text() == '10:00:00'


def test_guiSetText_6(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 'DSTR', Angle(degrees=90))
    assert suc
    assert pb.text() == '+90:00:00'


def test_guiSetText_7(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 'H2.2f', Angle(hours=12))
    assert suc
    assert pb.text() == '12.00'


def test_guiSetText_8(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 'D+2.2f', Angle(degrees=90))
    assert suc
    assert pb.text() == '+90.00'


def test_guiSetText_9(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 's', 'E')
    assert suc
    assert pb.text() == 'EAST'


def test_guiSetText_10(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 's', 'W')
    assert suc
    assert pb.text() == 'WEST'


def test_guiSetText_11(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 's', True)
    assert suc
    assert pb.text() == 'ON'


def test_guiSetText_12(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 's', False)
    assert suc
    assert pb.text() == 'OFF'


def test_guiSetStyle_1(function):
    pb = QPushButton()
    suc = function.guiSetStyle(pb)
    assert not suc


def test_guiSetStyle_2(function):
    pb = QPushButton()
    suc = function.guiSetStyle(pb, pStyle='color', value=None)
    assert suc


def test_guiSetStyle_3(function):
    pb = QPushButton()
    suc = function.guiSetStyle(pb, pStyle='color', value=True)
    assert suc


def test_guiSetStyle_4(function):
    pb = QPushButton()
    suc = function.guiSetStyle(pb, pStyle='color', value=False)
    assert suc


def test_checkUpdaterOK_0(function):
    function.app.automation = None
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        suc = function.checkUpdaterOK()
        assert not suc


def test_checkUpdaterOK_1(function):
    function.app.automation = None
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        suc = function.checkUpdaterOK()
        assert not suc


def test_checkUpdaterOK_2(function):
    function.app.automation.installPath = None
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        suc = function.checkUpdaterOK()
        assert not suc


def test_checkUpdaterOK_3(function):
    function.app.automation.installPath = 'test'
    function.app.automation.updaterApp = 'test'
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        suc = function.checkUpdaterOK()
        assert suc


def test_sleepAndEvents(function):
    suc = sleepAndEvents(1)
    assert suc


def test_convertTime_1(function):
    ts = load.timescale()
    t = ts.tt(2000, 1, 1, 12, 0)
    function.ui.unitTimeUTC.setChecked(True)
    val = function.convertTime(t, '%H:%M')
    assert val


def test_convertTime_2(function):
    ts = load.timescale()
    t = ts.tt(2000, 1, 1, 12, 0)
    function.ui.unitTimeUTC.setChecked(False)
    val = function.convertTime(t, '%H:%M')
    assert val


def test_timeZoneString_1(function):
    function.ui.unitTimeUTC.setChecked(True)
    val = function.timeZoneString()
    assert val == '(time is UTC)'


def test_timeZoneString_2(function):
    function.ui.unitTimeUTC.setChecked(False)
    val = function.timeZoneString()
    assert val == '(time is local)'


def test_mwSuper_1(function):
    class Test1:
        @staticmethod
        def test1(a):
            pass

    class Test(MWidget, Test1):
        @staticmethod
        def test(a):
            pass

    suc = Test().mwSuper('test1')
    assert suc


def test_makePointer(function):
    val = function.makePointer()
    assert isinstance(val, QPainterPath)


def test_makeSat(function):
    val = function.makeSat()
    assert isinstance(val, QPainterPath)


def test_positionWindow_1(function):
    config = {'winPosX': 100,
              'winPosY': 100,
              'height': 400,
              'width': 600}
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    suc = function.positionWindow(config)
    assert suc


def test_positionWindow_2(function):
    config = {'winPosX': 900,
              'winPosY': 900,
              'height': 400,
              'width': 600}
    function.screenSizeX = 1000
    function.screenSizeY = 1000
    suc = function.positionWindow(config)
    assert suc


def test_getTabIndex(function):
    widget = QTabWidget()
    w = QWidget()
    w.setObjectName('test')
    widget.addTab(w, 'test')
    w = QWidget()
    w.setObjectName('test1')
    widget.addTab(w, 'test1')
    index = function.getTabIndex(widget, 'test1')
    assert index == 1


def test_setTabAndIndex_1(function):
    widget = QTabWidget()
    config = {'test': 0}
    suc = function.setTabAndIndex(widget, config, 'test')
    assert suc


def test_setTabAndIndex_2(function):
    widget = QTabWidget()
    widget.addTab(QWidget(), 'test')
    widget.addTab(QWidget(), 'tes1')
    config = {'test': {'00': 'test'}}
    suc = function.setTabAndIndex(widget, config, 'test')
    assert suc
