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
import os
import platform
import numpy as np
import subprocess
from astropy.io import fits

# external packages
# local import
from mw4.astrometry import astrometry
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app, spy, mwGlob, test
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        app, spy, mwGlob, test = setupQt()
    yield


def test_init():
    binSolve = '/usr/bin'
    index = '/usr/share/astrometry'
    assert app.astrometry.binPath['astrometry-glob'] == binSolve
    assert app.astrometry.indexPath == index
    assert os.path.isfile(app.mwGlob['tempDir'] + '/astrometry.cfg')


def test_checkAvailability():
    app.indexPath = '/usr/share/astrometry'
    app.binPath = {'astrometry-glob': '/usr/bin',
                   'astrometry-local': '/usr/local/astrometry/bin'}
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        suc = app.astrometry.checkAvailability()
        assert suc
        assert app.astrometry.available == {}
