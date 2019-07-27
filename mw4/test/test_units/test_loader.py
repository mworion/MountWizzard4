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
# Python  v3.7.4
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
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import pytest
# local import
from mw4 import loader
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_MyApp():
    loader.MyApp(sys.argv)


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
                           return_value='test'):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=True):
                mwGlob = loader.setupWorkDirs()


def test_setupWorkDirs_2():
    with mock.patch.object(os,
                           'getcwd',
                           return_value='test'):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=False):
                mwGlob = loader.setupWorkDirs()


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
    suc = loader.writeSystemInfo(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_1():
    suc = loader.extractDataFiles()
    assert not suc


def test_extractDataFiles_2():
    suc = loader.extractDataFiles(mwGlob=mwGlob)
    assert suc

