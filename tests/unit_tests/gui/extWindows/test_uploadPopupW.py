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
import unittest.mock as mock
import pytest
import builtins

# external packages
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QWidget
import requests

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import gui.extWindows.uploadPopupW
from gui.extWindows.uploadPopupW import UploadPopup


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    widget = QWidget()
    widget.app = App()
    widget.threadPool = QThreadPool()
    with mock.patch.object(UploadPopup,
                           'show'):
        window = UploadPopup(parentWidget=widget, url='',
                             dataTypes='', dataFilePath='')
    yield window


def set_setProgressBarColor(function):
    suc = function.setProgressBarColor('red')
    assert suc


def test_setProgressBarToValue(function):
    suc = function.setProgressBarToValue(0)
    assert suc
    assert function.ui.progressBar.value() == 0


def test_setStatusTextToValue(function):
    suc = function.setStatusTextToValue('test')
    assert suc
    assert function.ui.statusText.text() == 'test'


def test_uploadFileWorker_1(function):
    function.dataTypes = ['test']
    suc = function.uploadFileWorker()
    assert not suc


def test_uploadFileWorker_2(function):
    class Test:
        status_code = 202

    function.dataTypes = ['comet']
    with mock.patch.object(builtins,
                           'open'):
        with mock.patch.object(requests,
                               'delete',
                               return_value=Test()):
            suc = function.uploadFileWorker()
            assert not suc


def test_uploadFileWorker_3(function):
    class Test:
        status_code = 200

    class Test1:
        status_code = 404

    function.dataTypes = ['comet']
    with mock.patch.object(builtins,
                           'open'):
        with mock.patch.object(requests,
                               'delete',
                               return_value=Test()):
            with mock.patch.object(function.threadPool,
                                   'start'):
                with mock.patch.object(requests,
                                       'post',
                                       return_value=Test1()):
                    suc = function.uploadFileWorker()
                    assert not suc


def test_uploadFileWorker_4(function):
    class Test:
        status_code = 200

    class Test1:
        status_code = 202

    function.dataTypes = ['comet']
    with mock.patch.object(builtins,
                           'open'):
        with mock.patch.object(requests,
                               'delete',
                               return_value=Test()):
            with mock.patch.object(function.threadPool,
                                   'start'):
                with mock.patch.object(requests,
                                       'post',
                                       return_value=Test1()):
                    suc = function.uploadFileWorker()
                    assert suc


def test_sendProgressValue(function):
    suc = function.sendProgressValue('12')
    assert suc


def test_pollDispatcher_1(function):
    text = ['Uploading']
    suc = function.pollDispatcher(text)
    assert suc


def test_pollDispatcher_2(function):
    text = ['Processing']
    suc = function.pollDispatcher(text)
    assert suc


def test_pollDispatcher_3(function):
    text = ['Processing', 'elements file.']
    with mock.patch.object(function,
                           'sendProgressValue'):
        suc = function.pollDispatcher(text)
        assert suc
        assert not function.returnValues['successMount']


def test_pollDispatcher_4(function):
    text = ['Processing', 'file failed']
    with mock.patch.object(function,
                           'sendProgressValue'):
        suc = function.pollDispatcher(text)
        assert suc
        assert not function.returnValues['successMount']


def test_pollDispatcher_5(function):
    text = ['Processing', 'elements saved.']
    with mock.patch.object(function,
                           'sendProgressValue'):
        suc = function.pollDispatcher(text)
        assert suc
        assert function.returnValues['successMount']
        assert function.returnValues['success']
        assert not function.pollStatusRunState


def test_pollDispatcher_6(function):
    text = ['Processing', 'data updated.']
    with mock.patch.object(function,
                           'sendProgressValue'):
        suc = function.pollDispatcher(text)
        assert suc
        assert function.returnValues['successMount']
        assert function.returnValues['success']
        assert not function.pollStatusRunState


def test_pollDispatcher_7(function):
    text = ['Processing', '90']
    with mock.patch.object(function,
                           'sendProgressValue'):
        suc = function.pollDispatcher(text)
        assert suc


def test_pollDispatcher_8(function):
    text = ['wutwrut']
    suc = function.pollDispatcher(text)
    assert not suc


def test_pollStatus_1(function):
    function.pollStatusRunState = False
    suc = function.pollStatus()
    assert suc


def test_pollStatus_2(function):
    class Test:
        status_code = 202

    function.pollStatusRunState = True
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = function.pollStatus()
        assert not suc
        assert not function.pollStatusRunState
        assert not function.returnValues['successMount']


def test_pollStatus_3(function):
    class Test:
        status_code = 200
        text = 'test'

    def pollDispatcher(text):
        function.pollStatusRunState = False
        function.timeoutCounter = 0
        return False

    function.pollStatusRunState = True
    temp = function.pollDispatcher
    function.pollDispatcher = pollDispatcher
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        with mock.patch.object(gui.extWindows.uploadPopupW,
                               'sleepAndEvents'):
            suc = function.pollStatus()
            assert suc
            assert not function.pollStatusRunState
            assert not function.returnValues['successMount']
    function.pollDispatcher = temp


def test_closePopup_1(function):
    with mock.patch.object(function,
                           'close'):
        with mock.patch.object(gui.extWindows.uploadPopupW,
                               'sleepAndEvents'):
            suc = function.closePopup(False)
            assert suc


def test_closePopup_2(function):
    function.returnValues['successMount'] = True
    function.pollStatusRunState = False
    with mock.patch.object(function,
                           'close'):
        with mock.patch.object(gui.extWindows.uploadPopupW,
                               'sleepAndEvents'):
            suc = function.closePopup(True)
            assert suc


def test_closePopup_3(function):
    function.returnValues['successMount'] = False
    function.pollStatusRunState = False
    with mock.patch.object(function,
                           'close'):
        with mock.patch.object(gui.extWindows.uploadPopupW,
                               'sleepAndEvents'):
            suc = function.closePopup(True)
            assert suc


def test_uploadFile_1(function):
    function.callBack = 1
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.uploadFile()
        assert suc


def test_uploadFile_2(function):
    function.callBack = None
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.uploadFile()
        assert suc
