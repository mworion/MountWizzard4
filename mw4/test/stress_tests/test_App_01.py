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


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():

    testArgv = ['run', 'test']

    with mock.patch.object(sys,
                           'argv',
                           testArgv):
        with mock.patch.object(sys,
                               'exit'):
            loader.main()

    yield


def test_image(qtbot):
    pass

