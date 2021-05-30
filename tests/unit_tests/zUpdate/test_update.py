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
import os
import sys
import unittest.mock as mock
import pytest
import subprocess
import builtins
import platform

# external packages
from PyQt5.QtWidgets import QApplication, QTextBrowser, QWidget
from PyQt5.QtTest import QTest

# local import
from mw4 import update
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def app(qapp):
    with mock.patch.object(QWidget,
                           'show'):
        yield


def test_writeText_1():
    tb = QTextBrowser()
    with mock.patch.object(QApplication,
                           'processEvents'):
        suc = update.writeText(tb, 'test', 0)
        assert suc


def test_formatPIP_1():
    line = update.formatPIP()
    assert line == ''


def test_formatPIP_2():
    line = update.formatPIP('   ')
    assert line == ''


def test_formatPIP_3():
    line = update.formatPIP('Requirement already satisfied: mountcontrol in /Users (0.157)')
    assert line == 'Requirement already satisfied : mountcontrol'


def test_formatPIP_4():
    line = update.formatPIP('Collecting mountcontrol==0.157')
    assert line == 'Collecting mountcontrol'


def test_formatPIP_5():
    line = update.formatPIP('Installing collected packages: mountcontrol')
    assert line == 'Installing collected packages'


def test_formatPIP_6():
    line = update.formatPIP('Successfully installed mountcontrol-0.156')
    assert line == 'Successfully installed mountcontrol-0.156'


def test_runInstall_1():

    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def readline():
            return ''

        @staticmethod
        def replace(a, b):
            return ''

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    tb = QTextBrowser()
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        with mock.patch.object(update,
                               'formatPIP',
                               return_value='test'):
            with mock.patch.object(builtins,
                                   'iter',
                                   return_value=['1', '2']):
                suc = update.runInstall(tb)
                assert suc


def test_runInstall_2():
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def readline():
            return

        @staticmethod
        def replace(a, b):
            return ''

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    tb = QTextBrowser()
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test(),
                           side_effect=Exception()):
        with mock.patch.object(update,
                               'formatPIP',
                               return_value=''):
            suc = update.runInstall(tb)
            assert not suc


def test_runInstall_3():
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

        @staticmethod
        def readline():
            return

        @staticmethod
        def replace(a, b):
            return ''

    class Test:
        returncode = 0
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    tb = QTextBrowser()
    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test(),
                           side_effect=subprocess.TimeoutExpired('res', 2)):
        with mock.patch.object(update,
                               'formatPIP',
                               return_value=''):
            suc = update.runInstall(tb)
            assert not suc


def test_runCancel():
    tb = QTextBrowser()
    with mock.patch.object(update,
                           'writeText'):
        with mock.patch.object(QTest,
                               'qWait'):
            with mock.patch.object(os,
                                   'execl'):
                update.runCancel(tb)


def test_runUpdate_1():
    tb = QTextBrowser()
    with mock.patch.object(update,
                           'writeText'):
        with mock.patch.object(update,
                               'runInstall',
                               return_value=False):
            with mock.patch.object(QTest,
                                   'qWait'):
                with mock.patch.object(os,
                                       'execl'):
                    update.runUpdate(tb, '1')


def test_runUpdate_2():
    tb = QTextBrowser()
    with mock.patch.object(update,
                           'writeText'):
        with mock.patch.object(update,
                               'runInstall',
                               return_value=True):
            with mock.patch.object(QTest,
                                   'qWait'):
                with mock.patch.object(os,
                                       'execl'):
                    update.runUpdate(tb, '1')


def test_main_1():
    class App:

        @staticmethod
        def installEventFilter(a):
            return

        @staticmethod
        def exec_():
            return 0

        @staticmethod
        def setWindowIcon(a):
            return 0

    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        with mock.patch.object(update,
                               'QApplication',
                               return_value=App()):
            with mock.patch.object(sys,
                                   'exit'):
                with mock.patch.object(sys,
                                       'argv',
                                       return_value=('', '1', '10', '10')):
                    update.main()


def test_main_2():
    class App:

        @staticmethod
        def installEventFilter(a):
            return

        @staticmethod
        def exec_():
            return 0

        @staticmethod
        def setWindowIcon(a):
            return 0

    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        with mock.patch.object(update,
                               'QApplication',
                               return_value=App()):
            with mock.patch.object(sys,
                                   'argv',
                                   return_value=('', '1', '10', '10')):
                with mock.patch.object(sys,
                                   'exit'):
                    update.main()
