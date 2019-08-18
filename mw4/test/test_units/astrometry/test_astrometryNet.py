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


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_solve_1():
    suc = app.astrometry.solveNET()
    assert not suc


def test_solve_2():
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=False):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=False):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                          timeout=5,
                                          )
        assert not suc


def test_solve_3():
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=False):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                          timeout=5,
                                          )
        assert not suc


def test_solve_4():
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=True):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                          timeout=5,
                                          )
        assert suc
