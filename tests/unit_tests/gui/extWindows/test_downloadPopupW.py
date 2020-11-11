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

# external packages
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget


# local import
from gui.extWindows.downloadPopupW import DownloadPopup


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    widget = QWidget()
    widget.threadPool = QThreadPool()
    with mock.patch.object(DownloadPopup,
                           'show'):
        window = DownloadPopup(parentWidget=widget,
                               url='',
                               dest='',
                               callBack=None,
                               )
    yield window


def test_setProgress(function):
    suc = function.setProgress(0)
    assert suc
    assert function.ui.progressBar.value() == 0


def test_downloadFile_1(function):
    with mock.patch.object(function.threadPool,
                           'start'):
        suc = function.downloadFile('', '')
        assert suc
