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
import os
import shutil
import time
import builtins

# external packages
from PyQt5.QtCore import QThreadPool, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget
import requests


# local import
from gui.extWindows.downloadPopupW import DownloadPopup


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    class Test(QObject):
        message = pyqtSignal(str, int)

    widget = QWidget()
    widget.app = Test()
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
                           side_effect=TimeoutError):
        with mock.patch.object(time,
                               'sleep'):
            suc = function.downloadFileWorker(url='', dest='tests/workDir/temp/test.txt')
            assert not suc


def test_downloadFileWorker_3(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           side_effect=TimeoutError):
        with mock.patch.object(time,
                               'sleep'):
            suc = function.downloadFileWorker(url='',
                                              dest='test/workDir/temp/test.txt')
            assert not suc


def test_downloadFileWorker_4(function):
    with mock.patch.object(function,
                           'getFileFromUrl',
                           side_effect=Exception):
        with mock.patch.object(time,
                               'sleep'):
            suc = function.downloadFileWorker(url='',
                                              dest='test/workDir/temp/test.txt')
            assert not suc


def test_downloadFileWorker_5(function):
    with mock.patch.object(function,
                           'getFileFromUrl'):
        with mock.patch.object(time,
                               'sleep'):
            suc = function.downloadFileWorker(url='',
                                              dest='test/workDir/temp/test.txt')
            assert not suc


def test_downloadFileWorker_6(function):
    with mock.patch.object(function,
                           'getFileFromUrl'):
        with mock.patch.object(time,
                               'sleep'):
            suc = function.downloadFileWorker(url='',
                                              dest='test/workDir/temp/test.txt',
                                              unzip=False)
            assert suc


def test_downloadFileWorker_7(function):
    with mock.patch.object(function,
                           'getFileFromUrl'):
        with mock.patch.object(time,
                               'sleep'):
            with mock.patch.object(function,
                                   'unzipFile',
                                   side_effect=Exception):
                suc = function.downloadFileWorker(url='',
                                                  dest='test/workDir/temp/test.txt')
                assert not suc


def test_downloadFileWorker_8(function):
    with mock.patch.object(function,
                           'getFileFromUrl'):
        with mock.patch.object(function,
                               'unzipFile'):
            with mock.patch.object(time,
                                   'sleep'):
                suc = function.downloadFileWorker(url='',
                                                  dest='test/workDir/temp/test.txt')
                assert suc


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
