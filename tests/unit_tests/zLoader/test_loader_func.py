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
import traceback
import sys
import os
import glob
import unittest.mock as mock
import socket
import platform
import json
import ctypes

# external packages
import pytest

# local import
import loader
from loader import except_hook, setupWorkDirs, writeSystemInfo, extractDataFiles
from loader import getWindowPos, checkIsAdmin, extractFile, minimizeStartTerminal


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)
    files = glob.glob('tests/workDir/config/profile')
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


def test_setupWorkDirs_3(qtbot):
    with mock.patch.object(os,
                           'getcwd',
                           return_value='.'):
        with mock.patch.object(os,
                               'makedirs',
                               return_value=True):
            with mock.patch.object(os.path,
                                   'isdir',
                                   return_value=False):
                with mock.patch.object(os,
                                       'access',
                                       return_value=False):
                    val = setupWorkDirs(mwGlob={})
                    assert val['modeldata'] == '4.0'


def test_checkIsAdmin_1(qtbot):
    @staticmethod
    def getiud():
        return 0

    os.getuid = getiud
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(os,
                               'getuid',
                               return_value=0,
                               side_effect=Exception):
            val = checkIsAdmin()
            assert val == 'unknown'


def test_checkIsAdmin_2(qtbot):
    @staticmethod
    def getiud():
        return 0

    os.getuid = getiud
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(os,
                               'getuid',
                               return_value=0):
            val = checkIsAdmin()
            assert val == 'yes'


def test_checkIsAdmin_3(qtbot):
    @staticmethod
    def getiud():
        return 0

    os.getuid = getiud
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(os,
                               'getuid',
                               return_value=1):
            val = checkIsAdmin()
            assert val == 'no'


@pytest.mark.skipif(platform.system() != 'Windows', reason="Windows needed")
def test_checkIsAdmin_4(qtbot):
    import ctypes
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(ctypes.windll.shell32,
                               'IsUserAnAdmin',
                               side_effect=Exception):
            val = checkIsAdmin()
            assert val == 'unknown'


@pytest.mark.skipif(platform.system() != 'Windows', reason="Windows needed")
def test_checkIsAdmin_5(qtbot):
    import ctypes
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(ctypes.windll.shell32,
                               'IsUserAnAdmin',
                               return_value=1):
            val = checkIsAdmin()
            assert val == 'yes'


@pytest.mark.skipif(platform.system() != 'Windows', reason="Windows needed")
def test_checkIsAdmin_6(qtbot):
    import ctypes
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(ctypes.windll.shell32,
                               'IsUserAnAdmin',
                               return_value=0):
            val = checkIsAdmin()
            assert val == 'no'


@pytest.mark.skipif(platform.system() != 'Windows', reason="need windows")
def test_checkIsAdmin_7(qtbot):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(ctypes.windll.shell32,
                               'IsUserAnAdmin',
                               return_value=0,
                               side_effect=Exception):
            val = checkIsAdmin()
            assert val == 'unknown'


@pytest.mark.skipif(platform.system() != 'Windows', reason="need windows")
def test_checkIsAdmin_8(qtbot):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(ctypes.windll.shell32,
                               'IsUserAnAdmin',
                               return_value=1):
            val = checkIsAdmin()
            assert val == 'yes'


@pytest.mark.skipif(platform.system() != 'Windows', reason="need windows")
def test_checkIsAdmin_9(qtbot):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(ctypes.windll.shell32,
                               'IsUserAnAdmin',
                               return_value=0):
            val = checkIsAdmin()
            assert val == 'no'


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


def test_extractFile_1():
    class MTime:
        st_mtime = 1000000000.0

    filePath = 'tests/workDir/data/de440_mw4.bsp'
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=False):
        with mock.patch.object(os,
                               'stat',
                               return_value=MTime()):
            suc = extractFile(filePath, 'de440_mw4.bsp', 0)
            assert suc


def test_extractFile_2():
    class MTime:
        st_mtime = 1000000000.0

    filePath = 'tests/workDir/data/de440_mw4.bsp'
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(os,
                               'stat',
                               return_value=MTime()):
            with mock.patch.object(os,
                                   'remove'):
                with mock.patch.object(os,
                                       'chmod'):
                    suc = extractFile(filePath, 'de440_mw4.bsp', 2000000000.0)
                    assert suc


def test_extractFile_3():
    class MTime:
        st_mtime = 1000000000.0

    filePath = 'tests/workDir/data/de440_mw4.bsp'
    with mock.patch.object(os.path,
                           'isfile',
                           return_value=True):
        with mock.patch.object(os,
                               'stat',
                               return_value=MTime()):
            with mock.patch.object(os,
                                   'chmod'):
                suc = extractFile(filePath, 'de440_mw4.bsp', 0)
                assert suc


def test_extractDataFiles_1():
    suc = extractDataFiles()
    assert not suc


def test_extractDataFiles_2():
    mwGlob = dict()
    mwGlob['dataDir'] = 'tests/workDir/data'
    suc = extractDataFiles(mwGlob=mwGlob)
    assert suc


def test_extractDataFiles_3():
    class Splash:
        @staticmethod
        def showMessage(a):
            return

    mwGlob = dict()
    mwGlob['dataDir'] = 'tests/workDir/data'
    with mock.patch.object(loader,
                           'extractFile'):
        suc = extractDataFiles(mwGlob=mwGlob, splashW=Splash())
        assert suc


def test_getWindowPos_1():
    test = 'tests'
    with mock.patch.object(os,
                           'getcwd',
                           return_value=test):
        x, y = getWindowPos()
        assert x == 0
        assert y == 0


def test_getWindowPos_2():
    test = 'tests/workDir'
    with open(test + '/config/profile', 'w+') as f:
        f.write('config')
    with mock.patch.object(os,
                           'getcwd',
                           return_value=test):
        x, y = getWindowPos()
        assert x == 0
        assert y == 0


def test_getWindowPos_3():
    test = 'tests/workDir'
    with open(test + '/config/profile', 'w+') as f:
        f.write('config')
    with open(test + '/config/config.cfg', 'w+') as f:
        f.write('this is a test')
    with mock.patch.object(os,
                           'getcwd',
                           return_value=test):
        x, y = getWindowPos()
        assert x == 0
        assert y == 0


def test_getWindowPos_4():
    test = 'tests/workDir'
    with open(test + '/config/profile', 'w+') as f:
        f.write('config')
    with open(test + '/config/config.cfg', 'w+') as f:
        data = {'mainW': {'winPosX': 200,
                          'winPosY': 100}}
        json.dump(data, f)
    with mock.patch.object(os,
                           'getcwd',
                           return_value=test):
        x, y = getWindowPos()
        assert x == 200
        assert y == 100


@pytest.mark.skipif(platform.system() != 'Windows', reason="Windows needed")
def test_minimizeStartTerminal():
    minimizeStartTerminal()
