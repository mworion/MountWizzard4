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
from unittest import mock
import pytest
import platform

# external packages
# local import
from mw4.astrometry import astrometry
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        app, spy, mwGlob, test = setupQt()
        yield


def test_init_1():
    app.astrometry.solveApp = {
        'astrometry-glob': {
            'programPath': '/usr/bin',
            'indexPath': '/usr/share/astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
