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
import unittest.mock as mock
import pytest
import platform
import os
import math

# external packages
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QWidget, QStyle, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject, QEvent
from skyfield.api import Angle

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


def test_FileSortProxyModel_1():
    w = QWidget()
    dialog = QFileDialog()
    dialog.setProxyModel(FileSortProxyModel(w))


def test_wIcon_1(function):
    suc = function.wIcon()
    assert not suc


def test_wIcon_2(function):
    icon = QStyle.SP_DialogApplyButton
    suc = function.wIcon()
    assert not suc


def test_wIcon_3(function):
    ui = QPushButton()
    suc = function.wIcon(gui=ui)
    assert not suc


def test_wIcon_4(function):
    icon = QStyle.SP_DialogApplyButton
    ui = QPushButton()
    suc = function.wIcon(gui=ui, name='load')
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


def test_changeStyleDynamic_5(function):
    ui = QPushButton()
    ui.setProperty('color', 'red')
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
    event = QEvent(QEvent.MouseButtonRelease)
    widget = QPushButton()
    suc = function.clickable(widget=widget)
    assert suc
    suc = widget.eventFilter(widget, event)
    assert not suc


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


def test_guiSetText_5(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 'HSTR', Angle(hours=10))
    assert suc
    assert pb.text() == '10 00 00'


def test_guiSetText_6(function):
    pb = QPushButton()
    suc = function.guiSetText(pb, 'DSTR', Angle(degrees=90))
    assert suc
    assert pb.text() == '+90 00 00'


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


def test_formatLatLonToAngle_1(function):
    values = [
        ['+12.5', 'SN', 12.5],
        ['12.5', 'SN', 12.5],
        ['-12.5', 'SN', -12.5],
        ['+12.5', 'WE', 12.5],
        ['12.5', 'WE', 12.5],
        ['-12.5', 'WE', -12.5],
        ['12N 30 30.55', 'SN', 12.508333],
        ['12N 30 30.5', 'SN', 12.508333],
        ['12N 30 30,5', 'SN', 12.508333],
        ['12 30 30.5N', 'SN', None],
        ['12 30 30.5 N', 'SN', None],
        ['+12N 30 30.5', 'SN', None],
        ['12N 30 30', 'SN', 12.508333],
        ['12S 30 30', 'SN', -12.508333],
        ['12N 30', 'SN', 12.5],
        ['12NS 30', 'SN', None],
        ['12W ', 'SN', None],
        ['12E 30 30.55', 'WE', 12.508333],
        ['12E 30 30.5', 'WE', 12.508333],
        ['12 30 30.5E', 'WE', None],
        ['12 30 30.5 E', 'WE', None],
        ['+12E 30 30.5', 'WE', None],
        ['12E 30 30', 'WE', 12.508333],
        ['12W 30 30', 'WE', -12.508333],
        ['12E 30', 'WE', 12.5],
        ['12WE 30', 'WE', None],
        ['12N ', 'WE', None],
        ['99N ', 'SN', None],
        ['99S ', 'SN', None],
        ['190E ', 'WE', None],
        ['190W ', 'WE', None],
        ['12N 30  30.5 ', 'SN', 12.508333],
        ['12N  30 30.5', 'SN', 12.508333],
        ['12N  30  30.5', 'SN', 12.508333],
    ]
    for value in values:
        angle = function.formatLatLonToAngle(value[0], value[1])

        if angle is None:
            assert value[2] is None
        else:
            assert math.isclose(angle.degrees, value[2], abs_tol=0.000001)


def test_formatLatLonToAngle_2(function):
    val = function.formatLatLonToAngle(None, 'NS')
    assert val is None


def test_formatLat(function):
    with mock.patch.object(function,
                           'formatLatLonToAngle',
                           return_value=10):
        angle = function.convertLatToAngle('12345')
        assert angle == 10


def test_formatLon(function):
    with mock.patch.object(function,
                           'formatLatLonToAngle',
                           return_value=10):
        angle = function.convertLonToAngle('12345')
        assert angle == 10


def test_convertRaToAngle_1(function):
    values = [
        ['+12.5', 12.5],
        ['12,5', 12.5],
        ['-12.5', None],
        ['-190.5', None],
        ['190.5', None],
        ['12H 30 30', 187.624999],
        ['12D 30 30', None],
        ['12 30 30', 187.624999],
        ['12H 30 30.55', 187.624999],
        ['12H  30 30', 187.624999],
        ['12H 30  30', 187.624999],
        ['12H  30   30.50', 187.624999],
        ['12  30 30', 187.624999],
        ['12 30  30', 187.624999],
        ['12  30   30.50', 187.624999],
    ]
    for value in values:
        angle = function.convertRaToAngle(value[0])

        if angle is None:
            assert value[1] is None
        else:
            assert math.isclose(angle._degrees, value[1], abs_tol=0.000001)


def test_convertRaToAngle_2(function):
    val = function.convertRaToAngle(None)
    assert val is None


def test_convertDecToAngle_1(function):
    values = [
        ['+12.5', 12.5],
        ['12,5', 12.5],
        ['-12.5', -12.5],
        ['-90.5', None],
        ['90.5', None],
        ['12Deg 30 30', 12.508333],
        ['12Deg 30 30.55', 12.508333],
        ['12H 30 30.55', None],
        ['12 30 30.55', 12.508333],
        ['-12Deg 30 30.55', -12.508333],
        ['-12 30 30.55', -12.508333],
        ['12Deg 30  30.55', 12.508333],
        ['12Deg  30 30.55', 12.508333],
        ['12Deg  30  30.55', 12.508333],
        ['12 30  30.55', 12.508333],
        ['12  30 30.55', 12.508333],
        ['12  30  30.55', 12.508333],
    ]
    for value in values:
        angle = function.convertDecToAngle(value[0])

        if angle is None:
            assert value[1] is None
        else:
            assert math.isclose(angle._degrees, value[1], abs_tol=0.000001)


def test_convertDecToAngle_2(function):
    val = function.convertDecToAngle(None)
    assert val is None


def test_formatHstrToText(function):
    values = [
        [Angle(hours=12), '12 00 00'],
        [Angle(hours=12.000001), '12 00 00'],
        [Angle(hours=6), '06 00 00'],
    ]
    for value in values:
        text = function.formatHstrToText(value[0])
        assert text == value[1]


def test_formatDstrToText(function):
    values = [
        [Angle(degrees=12), '+12 00 00'],
        [Angle(degrees=12.000001), '+12 00 00'],
        [Angle(degrees=6), '+06 00 00'],
        [Angle(degrees=-6), '-06 00 00'],
    ]
    for value in values:
        text = function.formatDstrToText(value[0])
        assert text == value[1]


def test_formatLatToText(function):
    values = [
        [Angle(degrees=12), '12N 00 00'],
        [Angle(degrees=12.000001), '12N 00 00'],
        [Angle(degrees=6), '06N 00 00'],
        [Angle(degrees=-6), '06S 00 00'],
    ]
    for value in values:
        text = function.formatLatToText(value[0])
        assert text == value[1]


def test_formatLonToText(function):
    values = [
        [Angle(degrees=12), '012E 00 00'],
        [Angle(degrees=12.000001), '012E 00 00'],
        [Angle(degrees=6), '006E 00 00'],
        [Angle(degrees=-6), '006W 00 00'],
    ]
    for value in values:
        text = function.formatLonToText(value[0])
        assert text == value[1]
