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
import glob
import copy
import unittest.mock as mock
# external packages
import pytest
# local import
from mw4 import loader
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test, testGlob, workDir
    app, spy, mwGlob, test = setupQt()
    testGlob = copy.copy(mwGlob)
    workDir = os.getcwd()


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
                           return_value=workDir):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=True):
                loader.setupWorkDirs(mwGlob=testGlob)


def test_setupWorkDirs_2():
    with mock.patch.object(os,
                           'getcwd',
                           return_value=workDir):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=False):
                loader.setupWorkDirs(mwGlob=testGlob)


def test_checkFrozen_1():
    mwGlob = loader.checkFrozen()
    assert not mwGlob['frozen']


def test_setup_logging():
    suc = loader.setupLogging()
    assert suc


def test_writeSystemInfo():
    mwGlob['modeldata'] = ''
    mwGlob['frozen'] = ''
    mwGlob['bundleDir'] = ''
    suc = loader.writeSystemInfo(mwGlob=testGlob)
    assert suc


def test_extractDataFiles_1():
    suc = loader.extractDataFiles()
    assert not suc


def test_extractDataFiles_2():
    suc = loader.extractDataFiles(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_3():
    files = glob.glob(mwGlob['dataDir'] + '/*')
    for f in files:
        os.remove(f)
    suc = loader.extractDataFiles(mwGlob=mwGlob)
    assert suc

