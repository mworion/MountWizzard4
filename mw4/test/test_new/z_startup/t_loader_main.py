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
import traceback
import sys
import os
import unittest.mock as mock
import socket

# external packages
import PyQt5
import pytest

# local import
from mw4 import loader
from mw4 import mainApp
from mw4.loader import MyApp


@pytest.fixture(autouse=True, scope="session")
def qapp():
    yield MyApp([])


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown(qapp):
    pass


def test_except_hook():
    with mock.patch.object(traceback,
                           'format_exception',
                           return_value=('1', '2', '3')):
        with mock.patch.object(sys,
                               '__excepthook__',
                               ):
            loader.except_hook(1, 2, 3)


def test_setupWorkDirs_1():
    with mock.patch.object(os,
                           'getcwd',
                           return_value='.'):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=True):
                val = loader.setupWorkDirs(mwGlob={})
                assert not val['frozen']


def test_setupWorkDirs_2():
    with mock.patch.object(os,
                           'getcwd',
                           return_value='.'):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=False):
                val = loader.setupWorkDirs(mwGlob={})
                assert not val['frozen']


def test_writeSystemInfo_1():
    mwGlob = dict()
    mwGlob['modeldata'] = ''
    mwGlob['frozen'] = ''
    mwGlob['bundleDir'] = ''
    mwGlob['workDir'] = ''
    suc = loader.writeSystemInfo(mwGlob=mwGlob)
    assert suc


def test_writeSystemInfo_2():
    mwGlob = dict()
    mwGlob['modeldata'] = ''
    mwGlob['frozen'] = ''
    mwGlob['bundleDir'] = ''
    mwGlob['workDir'] = ''
    with mock.patch.object(socket,
                           'gethostbyname_ex',
                           side_effect=Exception()):
        suc = loader.writeSystemInfo(mwGlob=mwGlob)
        assert suc


def test_extractDataFiles_1():
    suc = loader.extractDataFiles()
    assert not suc


def test_extractDataFiles_2():
    mwGlob = dict()
    mwGlob['dataDir'] = 'mw4/test/data'
    suc = loader.extractDataFiles(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_3():
    mwGlob = dict()
    mwGlob['dataDir'] = 'mw4/test/data'
    suc = loader.extractDataFiles(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_3():
    mwGlob = dict()
    mwGlob['dataDir'] = 'mw4/test/data'
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = loader.extractDataFiles(mwGlob=mwGlob)
        assert suc


def test_main_1():
    with mock.patch.object(PyQt5.QtWidgets.QApplication,
                           'exec_',
                           return_value=True):
        with mock.patch.object(mainApp,
                               'MountWizzard4'):
            with mock.patch.object(sys,
                                   'exit'):
                loader.main()
