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
import traceback
import sys
import os
import glob
import unittest.mock as mock
import socket
import platform

# external packages
import pytest

# local import
from loader import except_hook, setupWorkDirs, writeSystemInfo, extractDataFiles


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    files = glob.glob('tests/config/*.cfg')
    for f in files:
        os.remove(f)
    yield


def test_except_hook(qtbot):
    with mock.patch.object(traceback,
                           'format_exception',
                           return_value=('1', '2', '3')):
        with mock.patch.object(sys,
                               '__excepthook__',
                               ):
            except_hook(1, 2, 3)


def test_setupWorkDirs_1(qtbot):
    with mock.patch.object(os,
                           'getcwd',
                           return_value='.'):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=True):
                val = setupWorkDirs(mwGlob={})
                assert val['modeldata'] == '4.0'


def test_setupWorkDirs_2(qtbot):
    with mock.patch.object(os,
                           'getcwd',
                           return_value='.'):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=False):
                val = setupWorkDirs(mwGlob={})
                assert val['modeldata'] == '4.0'


def test_writeSystemInfo_1(qtbot):
    mwGlob = dict()
    mwGlob['modeldata'] = ''
    mwGlob['workDir'] = ''
    suc = writeSystemInfo(mwGlob=mwGlob)
    assert suc


def test_writeSystemInfo_2(qtbot):
    mwGlob = dict()
    mwGlob['modeldata'] = ''
    mwGlob['workDir'] = ''
    with mock.patch.object(socket,
                           'gethostbyname_ex',
                           side_effect=Exception()):
        suc = writeSystemInfo(mwGlob=mwGlob)
        assert suc


def test_extractDataFiles_1(qtbot):
    suc = extractDataFiles()
    assert not suc


def test_extractDataFiles_2(qtbot):
    mwGlob = dict()
    mwGlob['dataDir'] = 'tests/data'
    suc = extractDataFiles(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_3(qtbot):
    class Splash:
        @staticmethod
        def showMessage(a):
            return

    mwGlob = dict()
    mwGlob['dataDir'] = 'tests/data'
    suc = extractDataFiles(mwGlob=mwGlob, splashW=Splash())
    assert suc


def test_extractDataFiles_4(qtbot):
    mwGlob = dict()
    mwGlob['dataDir'] = 'tests/data'
    suc = extractDataFiles(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_5(qtbot):
    if platform.system() == 'Windows':
        return

    mwGlob = {'dataDir': 'tests/data'}

    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = extractDataFiles(mwGlob=mwGlob)
        assert suc
    assert os.path.isfile('tests/data/de421_23.bsp')
    assert os.path.isfile('tests/data/active.txt')
    assert os.path.isfile('tests/data/finals2000A.all')
    assert os.path.isfile('tests/data/tai-utc.dat')
