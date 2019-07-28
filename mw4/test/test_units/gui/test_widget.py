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
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import platform
# external packages
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore
# local import
from mw4.test.test_units.setupQt import setupQt
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test, a
    app, spy, mwGlob, test = setupQt()
    a = MWidget()
    yield


def test_wIcon_1():
    suc = a.wIcon()
    assert not suc


def test_wIcon_2():
    suc = a.wIcon(QPushButton())
    assert not suc


def test_wIcon_3():
    suc = a.wIcon(QPushButton(), QStyle.SP_ComputerIcon)
    assert suc


def test_getStyle_1():
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        val = a.getStyle()
        assert val


def test_getStyle_2():
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        val = a.getStyle()
        assert val


def test_getStyle_3():
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        val = a.getStyle()
        assert val


def test_initUI():
    suc = a.initUI()
    assert suc


def test_changeStyleDynamic_1():
    suc = a.changeStyleDynamic()
    assert not suc


def test_changeStyleDynamic_2():
    suc = a.changeStyleDynamic(QPushButton())
    assert not suc


def test_changeStyleDynamic_3():
    suc = a.changeStyleDynamic(QPushButton(), 'test')
    assert not suc


def test_changeStyleDynamic_4():
    suc = a.changeStyleDynamic(QPushButton(), 'test', 'true')
    assert suc


def test_clearPolar_1():
    fig, axe = a.clearPolar()

    assert fig is None
    assert axe is None


def test_clearPolar_2():
    fig, axe = a.clearPolar(QWidget())

    assert fig is None
    assert axe is None


def test_clearPolar_3():
    b = QWidget()
    c = a.embedMatplot(b)

    fig, axe = a.clearPolar(c)

    assert fig is not None
    assert axe is not None


def test_embedMatplot_1():
    b = QWidget()

    c = a.embedMatplot()

    assert c is None


def test_embedMatplot_2():
    b = QWidget()

    c = a.embedMatplot(b)

    assert c is not None


def test_extractNames_1():
    name, short, ext = a.extractNames()
    assert name == ''
    assert short == ''
    assert ext == ''


def test_extractNames_2():
    name, short, ext = a.extractNames('/User/mw/test.txt')
    assert name == ''
    assert short == ''
    assert ext == ''


def test_extractNames_3():
    name, short, ext = a.extractNames(['/User/mw/test.txt'])
    assert name == '/User/mw/test.txt'
    assert short == 'test'
    assert ext == '.txt'


def test_extractNames_4():
    name, short, ext = a.extractNames(['/User/mw/test.txt', '/User/mw/test.txt'])
    assert name == ['/User/mw/test.txt', '/User/mw/test.txt']
    assert short == ['test', 'test']
    assert ext == ['.txt', '.txt']


def test_prepareFileDialogue_1():
    dlg = a.prepareFileDialog()
    assert not dlg


def test_prepareFileDialogue_2():
    dlg = a.prepareFileDialog(QMainWindow(), False)
    assert dlg


def test_prepareFileDialogue_3():
    dlg = a.prepareFileDialog(QMainWindow(), True)
    assert dlg


def test_openFile_1():
    a.openFile()


def test_openFile_2():
    a.openFile(QMainWindow())


def test_openFile_3():
    a.openFile(QMainWindow(), 'test')


def test_openFile_4():
    a.openFile(QMainWindow(), 'test', 'test')


def test_saveFile_1():
    a.saveFile()


def test_openDir_1():
    a.openDir()


def test_clickable_1():
    a.clickable()
