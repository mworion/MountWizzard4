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
import platform

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


def test_init_1():
    app.solverEnviron = {
        'astrometry-glob': {
            'programPath': '/usr/bin',
            'indexPath': '/usr/share/astrometry',
            'solver': app.solverNET,
        }
    }
