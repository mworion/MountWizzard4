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
import sys
import unittest.mock as mock

# external packages
import pytest

# local import
from mw4 import loader
from mw4.loader import MyApp
from mw4 import mainApp


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    pass


def test_main_1(qtbot):
    with mock.patch.object(mainApp,
                           'MountWizzard4'):
        with mock.patch.object(MyApp,
                               'exec_',
                               return_value=True):
            with mock.patch.object(sys,
                                   'exit'):
                loader.main()
