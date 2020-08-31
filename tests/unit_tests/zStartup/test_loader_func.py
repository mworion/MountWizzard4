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
from mw4 import loader


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
            loader.except_hook(1, 2, 3)


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
                val = loader.setupWorkDirs(mwGlob={})
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
                val = loader.setupWorkDirs(mwGlob={})
                assert val['modeldata'] == '4.0'


def test_writeSystemInfo_1(qtbot):
    mwGlob = dict()
    mwGlob['modeldata'] = ''
    mwGlob['workDir'] = ''
    suc = loader.writeSystemInfo(mwGlob=mwGlob)
    assert suc


def test_writeSystemInfo_2(qtbot):
    mwGlob = dict()
    mwGlob['modeldata'] = ''
    mwGlob['workDir'] = ''
    with mock.patch.object(socket,
                           'gethostbyname_ex',
                           side_effect=Exception()):
        suc = loader.writeSystemInfo(mwGlob=mwGlob)
        assert suc


def test_extractDataFiles_1(qtbot):
    suc = loader.extractDataFiles()
    assert not suc


def test_extractDataFiles_2(qtbot):
    mwGlob = dict()
    mwGlob['dataDir'] = 'tests/data'
    suc = loader.extractDataFiles(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_3(qtbot):
    mwGlob = dict()
    mwGlob['dataDir'] = 'tests/data'
    suc = loader.extractDataFiles(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_4(qtbot):
    if platform.system() == 'Windows':
        return

    mwGlob = {'dataDir': 'tests/data'}

    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        suc = loader.extractDataFiles(mwGlob=mwGlob)
        assert suc
    assert os.path.isfile('tests/data/Leap_Second.dat')
    assert os.path.isfile('tests/data/deltat.data')
    assert os.path.isfile('tests/data/deltat.preds')
    assert os.path.isfile('tests/data/de421_23.bsp')
    assert os.path.isfile('tests/data/active.txt')
