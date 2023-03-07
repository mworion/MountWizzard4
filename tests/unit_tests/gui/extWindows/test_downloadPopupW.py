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
import shutil
import builtins

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget
import requests

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import gui.extWindows.downloadPopupW
from gui.extWindows.downloadPopupW import DownloadPopup


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    widget = QWidget()
    widget.app = App()
    widget.threadPool = QThreadPool()
    with mock.patch.object(DownloadPopup,
                           'show'):
        window = DownloadPopup(parentWidget=widget,
                               url='',
                               dest='',
                               callBack=None,
                               )
    yield window


def set_setProgressBarColor(function):
    suc = function.setProgressBarColor('red')
    assert suc


def test_setProgressBarToValue(function):
    suc = function.setProgressBarToValue(0)
    assert suc
    assert function.ui.progressBar.value() == 0


def test_getFileFromUrl_1(function):
    class Response:
        headers = {}
        text = 'test'
        status_code = 200

        @staticmethod
        def iter_content(a):
            return [b's' * 512]
    function.cancel = False
    with mock.patch.object(requests,
                           'get',
                           return_value=Response()):
        with mock.patch.object(builtins,
                               'open'):
            suc = function.getFileFromUrl('http://local', 'tests/workDir/temp/test.txt')
            assert suc


def test_getFileFromUrl_2(function):
    class Response:
        headers = {}
        text = 'test'
        status_code = 200

        @staticmethod
        def iter_content(a):
            return [b's' * 512]
    with mock.patch.object(requests,
                           'get',
                           return_value=Response()):
        with mock.patch.object(builtins,
                               'open'):
            suc = function.getFileFromUrl('http://local', 'tests/workDir/temp/test.txt')
            assert suc


def test_getFileFromUrl_3(function):
    class Response:
        headers = {}
        text = 'test'
        status_code = 500

        @staticmethod
        def iter_content(a):
            return [b's' * 512]
    with mock.patch.object(requests,
                           'get',
                           return_value=Response()):
        with mock.patch.object(builtins,
                               'open'):
            suc = function.getFileFromUrl('http://local', 'tests/workDir/temp/test.txt')
            assert not suc


def test_unzipFile(function):
    shutil.copy('tests/testData/test.json.gz', 'tests/workDir/temp/test.json.gz')
    suc = function.unzipFile('tests/workDir/temp/test.json.gz')
    assert suc
    assert os.path.isfile('tests/workDir/temp/test.json')


def test_downloadFileWorker_1(function):
    suc = function.downloadFileWorker('', '')
    assert not suc


def test_downloadFileWorker_2(function):
    shutil.copy('tests/testData/visual.txt', 'tests/workDir/temp/test.txt')
    with mock.patch.object(function,
                           'getFileFromUrl',
                           return_value=True,
                           side_effect=TimeoutError):
        with mock.patch.object(gui.extWindows.downloadPopupW,
                               'sleepAndEvents'):
            suc = function.downloadFileWorker(url='', dest='tests/workDir/temp/test.txt')
            assert not suc


def test_downloadFileWorker_3(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           return_value=True,
                           side_effect=TimeoutError):
        with mock.patch.object(gui.extWindows.downloadPopupW,
                               'sleepAndEvents'):
            suc = function.downloadFileWorker(url='',
                                              dest='test/workDir/temp/test.txt')
            assert not suc


def test_downloadFileWorker_4(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           return_value=True,
                           side_effect=Exception):
        with mock.patch.object(gui.extWindows.downloadPopupW,
                               'sleepAndEvents'):
            suc = function.downloadFileWorker(url='',
                                              dest='test/workDir/temp/test.txt')
            assert not suc


def test_downloadFileWorker_5(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           return_value=True):
        with mock.patch.object(gui.extWindows.downloadPopupW,
                               'sleepAndEvents'):
            suc = function.downloadFileWorker(url='',
                                              dest='test/workDir/temp/test.txt')
            assert not suc


def test_downloadFileWorker_6(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           return_value=True,):
        with mock.patch.object(gui.extWindows.downloadPopupW,
                               'sleepAndEvents'):
            suc = function.downloadFileWorker(url='',
                                              dest='test/workDir/temp/test.txt',
                                              unzip=False)
            assert suc


def test_downloadFileWorker_7(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           return_value=True,):
        with mock.patch.object(gui.extWindows.downloadPopupW,
                               'sleepAndEvents'):
            with mock.patch.object(function,
                                   'unzipFile',
                                   side_effect=Exception):
                suc = function.downloadFileWorker(url='',
                                                  dest='test/workDir/temp/test.txt')
                assert not suc


def test_downloadFileWorker_8(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           return_value=True,):
        with mock.patch.object(function,
                               'unzipFile'):
            with mock.patch.object(gui.extWindows.downloadPopupW,
                                   'sleepAndEvents'):
                suc = function.downloadFileWorker(url='',
                                                  dest='test/workDir/temp/test.txt')
                assert suc


def test_downloadFileWorker_9(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           return_value=False,):
        with mock.patch.object(function,
                               'unzipFile'):
            with mock.patch.object(gui.extWindows.downloadPopupW,
                                   'sleepAndEvents'):
                suc = function.downloadFileWorker(url='',
                                                  dest='test/workDir/temp/test.txt')
                assert not suc


def test_processResult(function):
    def test():
        return

    function.callBack = test
    suc = function.processResult(True)
    assert suc


def test_downloadFile_1(function):
    function.callBack = 1
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.downloadFile('', '')
        assert suc


def test_downloadFile_2(function):
    function.callBack = None
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.downloadFile('', '')
        assert suc
