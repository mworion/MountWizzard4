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
from unittest import mock
import pytest
import os
import subprocess

# external packages
from PyQt5.QtCore import QThreadPool

# local import
from mw4.astrometry.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test:
        threadPool = QThreadPool()

    global app
    app = Astrometry(app=Test(), tempDir='mw4/test/temp')
    yield
    del app


def test_runImage2xy_1():
    suc = app.solverNET.runImage2xy()
    assert not suc


def test_runImage2xy_2():
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

    class Test:
        returncode = '1'
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        suc = app.solverNET.runImage2xy()
    assert not suc


def test_runSolveField_1():
    suc = app.solverNET.runSolveField()
    assert not suc


def test_runSolveField_2():
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

    class Test:
        returncode = '1'
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        suc = app.solverNET.runSolveField()
    assert not suc


def test_solveNet_1():
    suc = app.solverNET.solve()
    assert not suc


def test_abortNet_1():
    app.process = None
    suc = app.solverNET.abort()
    assert not suc


def test_abortNet_2():
    class Test:
        @staticmethod
        def kill():
            return True
    app.solverNET.process = Test()
    suc = app.solverNET.abort()
    assert suc
