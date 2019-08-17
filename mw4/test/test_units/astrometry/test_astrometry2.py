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
                           return_value='Windows'):
        app, spy, mwGlob, test = setupQt()
    yield


def test_init():

    assert app.astrometry.binPath == {}
    assert app.astrometry.indexPath == ''
    assert os.path.isfile(app.mwGlob['tempDir'] + '/astrometry.cfg')

