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
import pytest
import os
# external packages
# local imports
from mountcontrol.mount import Mount


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global m
    m = Mount(host='127.0.0.1',
              pathToData=os.getcwd() + '/data',
              verbose=True)
    yield


def test_mount():
    pass


def test_resetData():
    m.resetData()
