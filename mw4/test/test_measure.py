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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
# external packages
import PyQt5.QtWidgets
# local import
from mw4.base import measuredata

test = PyQt5.QtWidgets.QApplication([])
host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    app = environ.Environment(host_ip)
    yield
    app = None

