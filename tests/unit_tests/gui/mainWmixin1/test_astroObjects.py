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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import os
from unittest import mock

# external packages
from PySide6.QtWidgets import QWidget, QComboBox, QTableWidget, QGroupBox
from PySide6.QtCore import QThreadPool

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWmixin.astroObjects import AstroObjects
import gui
from gui.extWindows.downloadPopupW import DownloadPopup
from gui.extWindows.uploadPopupW import UploadPopup

satBaseUrl = 'http://www.celestrak.org/NORAD/elements/gp.php?'
satSourceURLs = {
    '100 brightest': {
        'url': satBaseUrl + 'GROUP=visual&FORMAT=tle',
        'file': 'visual.txt',
        'unzip': False,
        },
}


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    def test():
        pass

    with mock.patch.object(App().mount.obsSite.loader,
                           'days_old',
                           return_value=0):
        function = AstroObjects(
            window=QWidget(),
            app=App(),
            objectText='test',
            sourceUrls=satSourceURLs,
            uiObjectList=QTableWidget(),
            uiSourceList=QComboBox(),
            uiSourceGroup=QGroupBox(),
            processFunc=test,
        )
        function.window.app = App()
        function.window.threadPool = QThreadPool()
        yield function


def test_buildSourceListDropdown_1(function):
    with mock.patch.object(function,
                           'loadSourceUrl'):
        function.buildSourceListDropdown()
        assert function.uiSourceList.count() == 1


def test_setAge_1(function):
    function.setAge(0)
    assert function.uiSourceGroup.title() == 'test data - age: 0.0d'


def test_runDownloadPopup_1(function):
    with mock.patch.object(gui.extWindows.downloadPopupW.DownloadPopup,
                           'show'):
        with mock.patch.object(function.window.threadPool,
                               'start'):
            function.runDownloadPopup('', False)


def test_loadSourceUrl_1(function):
    function.uiSourceList.clear()

    function.loadSourceUrl()


def test_loadSourceUrl_2(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem('100 brightest')

    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(function,
                               'procSourceData'):
            function.loadSourceUrl()


def test_loadSourceUrl_3(function):
    function.uiSourceList.clear()
    function.uiSourceList.addItem('100 brightest')

    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(function,
                               'runDownloadPopup'):
            function.loadSourceUrl()


def test_runUploadPopup_1(function):
    with mock.patch.object(gui.extWindows.uploadPopupW.UploadPopup,
                           'show'):
        with mock.patch.object(function.window.threadPool,
                               'start'):
            function.runUploadPopup('')


def test_finishProgObjects_1(function):
    class Test:
        returnValues = {'success': False}

    function.uploadPopup = Test()
    function.finishProgObjects()


def test_finishProgObjects_2(function):
    class Test:
        returnValues = {'success': False}

    function.uploadPopup = Test()
    function.finishProgObjects()


def test_progObjects_1(function):
    function.progObjects([])
