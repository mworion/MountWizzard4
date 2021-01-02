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
#
# written in python3 , (c) 2019, 2020 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import unittest.mock as mock

from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal

# local import
from indibase.indiBase import Client


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    function = Client()
    yield function


def test_properties():
    pass
